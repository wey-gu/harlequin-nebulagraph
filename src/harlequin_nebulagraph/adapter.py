from __future__ import annotations

from typing import Any, Sequence

from harlequin import (
    HarlequinAdapter,
    HarlequinConnection,
    HarlequinCursor,
)
from harlequin.autocomplete.completion import HarlequinCompletion
from harlequin.catalog import Catalog, CatalogItem
from harlequin.exception import (
    HarlequinConnectionError,
    HarlequinQueryError,
)
from nebula3.Config import Config, SSL_config
from nebula3.data.ResultSet import ResultSet
from nebula3.gclient.net import ConnectionPool
from textual_fastdatatable.backend import AutoBackendType

from harlequin_nebulagraph.cli_options import NEBULAGRAPH_OPTIONS
from harlequin_nebulagraph.keywords import FUNCTIONS, RESERVED_WORDS

COLUMN_TYPE_MAPPING = {
    "empty": "",
    "null": "null",
    "bool": "t/f",
    "int": "#",
    "double": "#.#",
    "string": "s",
    "list": "[]",
    "set": "{}",
    "map": "{->}",
    "time": "t",
    "date": "d",
    "datetime": "dt",
    "vertex": "{}",
    "edge": "{}",
    "path": "{}",
    "geography": "geo",
    "duration": "|-|",
}


def as_primitive(result: ResultSet) -> list[dict[Any]]:
    """Convert result set to list of dict with primitive values per row

    :return: list<dict>
    """
    if result is None:
        return []

    if hasattr(result, "as_primitive"):
        return result.as_primitive()
    else:
        return [
            {
                col_key: result.row_values(row_index)[col_index].cast_primitive()
                for col_index, col_key in enumerate(result.keys())
            }
            for row_index in range(result.row_size())
        ]


class NebulaGraphCursor(HarlequinCursor):
    def __init__(self, result: ResultSet, *args: Any, **kwargs: Any) -> None:
        self.cur = result
        self.result_primitive: list[dict[Any]] | None = None
        # as_primitive(result)
        self._limit: int | None = None

    def columns(self) -> list[tuple[str, str]]:
        column_names = self.cur.keys()
        if self.cur.row_size() > 0:
            column_types = [
                COLUMN_TYPE_MAPPING[col._get_type_name()]
                for col in self.cur.row_values(0)
            ]
        else:
            column_types = [""] * len(column_names)
        return list(zip(column_names, column_types))

    def set_limit(self, limit: int) -> NebulaGraphCursor:
        self._limit = limit
        return self

    def fetchall(self) -> AutoBackendType:
        if self.result_primitive is None:
            self.result_primitive = as_primitive(self.cur)
        try:
            if self._limit is None or self._limit > len(self.result_primitive):
                return [
                    tuple(row[col] for col in self.cur.keys())
                    for row in self.result_primitive
                ]
            else:
                return [
                    tuple(row[col] for col in self.cur.keys())
                    for row in self.result_primitive[: self._limit]
                ]
        except Exception as e:
            raise HarlequinQueryError(
                msg=str(e),
                title="Harlequin encountered an error while executing your query.",
            ) from e


class NebulaGraphConnection(HarlequinConnection):
    def __init__(
        self,
        conn_str: Sequence[str],
        *_: Any,
        init_message: str = "",
        options: dict[str, Any],
    ) -> None:
        self.init_message = init_message
        try:
            # define a config
            config = Config()
            config.max_connection_pool_size = 10
            # init connection pool
            connection_pool = ConnectionPool()
            connection_pool.init([(options["host"], options["port"])], config)
            self.conn = connection_pool.get_session(
                options["user"], options["password"]
            )
            self.conn.execute("SHOW SPACES")
        except RuntimeError:
            ssl_config = SSL_config()
            try:
                connection_pool.init(
                    [(options["host"], options["port"])], config, ssl_config
                )
                self.conn = connection_pool.get_session(
                    options["user"], options["password"]
                )
                self.conn.execute("SHOW SPACES")
            except Exception as e:
                raise HarlequinConnectionError(
                    msg=str(e), title="Harlequin could not connect to NebulaGraph"
                ) from e
        except Exception as e:
            raise HarlequinConnectionError(
                msg=str(e), title="Harlequin could not connect to NebulaGraph."
            ) from e

    def execute(self, query: str) -> HarlequinCursor | None:
        try:
            cur: ResultSet | None = self.conn.execute(query)
        except Exception as e:
            raise HarlequinQueryError(
                msg=str(e),
                title="Harlequin encountered an error while executing query.",
            ) from e
        else:
            if cur is not None:
                if cur.is_succeeded():
                    return NebulaGraphCursor(result=cur)
                else:
                    raise HarlequinQueryError(
                        msg=f"{cur.error_code()}: {cur.error_msg()}",
                        title="Harlequin encountered an error while executing query.",
                    )
            else:
                return None

    def get_catalog(self) -> Catalog:
        databases = as_primitive(self.conn.execute("SHOW SPACES"))
        db_items: list[CatalogItem] = []
        for db in databases:
            db_name = db["Name"]
            tags_record = as_primitive(self.conn.execute(f"USE `{db_name}`; SHOW TAGS"))
            edges_record = as_primitive(
                self.conn.execute(f"USE `{db_name}`; SHOW EDGES")
            )
            tag_items: list[CatalogItem] = []
            for tag_schema in tags_record:
                tag_schema_name = tag_schema["Name"]
                tag_schema_desc = as_primitive(
                    self.conn.execute(f"USE `{db_name}`; DESC TAG `{tag_schema_name}`")
                )
                # ['Field', 'Type', 'Null', 'Default', 'Comment']
                col_items: list[CatalogItem] = []
                for col in tag_schema_desc:
                    col_items.append(
                        CatalogItem(
                            qualified_identifier=f'"{db_name}"."tags"."{tag_schema_name}"."{col["Field"]}"',
                            query_name=f'"{col["Field"]}"',
                            label=col["Field"],
                            type_label=col["Type"],
                        )
                    )
                tag_items.append(
                    CatalogItem(
                        qualified_identifier=f'"{db_name}"."tags"."{tag_schema_name}"',
                        query_name=f'"{tag_schema_name}"',
                        label=tag_schema_name,
                        type_label="tag",
                        children=col_items,
                    )
                )
            edge_items: list[CatalogItem] = []
            for edge_schema in edges_record:
                edge_schema_name = edge_schema["Name"]
                edge_schema_desc = as_primitive(
                    self.conn.execute(
                        f"USE `{db_name}`; DESC EDGE `{edge_schema_name}`"
                    )
                )
                # ['Field', 'Type', 'Null', 'Default', 'Comment']
                col_items: list[CatalogItem] = []
                for col in edge_schema_desc:
                    col_items.append(
                        CatalogItem(
                            qualified_identifier=f'"{db_name}"."edges"."{edge_schema_name}"."{col["Field"]}"',
                            query_name=f'"{col["Field"]}"',
                            label=col["Field"],
                            type_label=col["Type"],
                        )
                    )
                edge_items.append(
                    CatalogItem(
                        qualified_identifier=f'"{db_name}"."edges"."{edge_schema_name}"',
                        query_name=f'"{edge_schema_name}"',
                        label=edge_schema_name,
                        type_label="edge",
                        children=col_items,
                    )
                )
            children = tag_items + edge_items

            db_items.append(
                CatalogItem(
                    qualified_identifier=f"`{db_name}`",
                    query_name=f"`{db_name}`",
                    label=db_name,
                    type_label="space",
                    children=children,
                )
            )
        return Catalog(items=db_items)

    def get_completions(self) -> list[HarlequinCompletion]:
        keyword_completions = [
            HarlequinCompletion(
                label=keyword,
                type_label="kw",
                value=keyword,
                priority=100,
                context=None,
            )
            for keyword in RESERVED_WORDS
        ]

        function_completions = [
            HarlequinCompletion(
                label=function,
                type_label="fn",
                value=function,
                priority=1000,
                context=None,
            )
            for function in FUNCTIONS
        ]

        return [
            *keyword_completions,
            *function_completions,
        ]


class NebulaGraphAdapter(HarlequinAdapter):
    ADAPTER_OPTIONS = NEBULAGRAPH_OPTIONS

    def __init__(
        self,
        conn_str: Sequence[str],
        user: str = "root",
        password: str = "nebula",
        host: str = "127.0.0.1",
        port: int = 9669,
        **_: Any,
    ) -> None:
        self.conn_str = conn_str
        self.options = {
            "user": user,
            "password": password,
            "host": host,
            "port": port,
        }

    def connect(self) -> NebulaGraphConnection:
        conn = NebulaGraphConnection(self.conn_str, options=self.options)
        return conn
