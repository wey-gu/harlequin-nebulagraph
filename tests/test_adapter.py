import sys

import pytest
from harlequin.adapter import HarlequinAdapter, HarlequinConnection, HarlequinCursor
from harlequin.catalog import Catalog, CatalogItem
from harlequin.exception import HarlequinConnectionError, HarlequinQueryError
from harlequin_nebulagraph.adapter import NebulaGraphAdapter, NebulaGraphConnection
from textual_fastdatatable.backend import create_backend

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points


def test_plugin_discovery() -> None:
    PLUGIN_NAME = "nebulagraph"
    eps = entry_points(group="harlequin.adapter")
    assert eps[PLUGIN_NAME]
    adapter_cls = eps[PLUGIN_NAME].load()
    assert issubclass(adapter_cls, HarlequinAdapter)
    assert adapter_cls == NebulaGraphAdapter


def test_connect() -> None:
    conn = NebulaGraphAdapter(conn_str=tuple()).connect()
    assert isinstance(conn, HarlequinConnection)


def test_connect_raises_connection_error() -> None:
    with pytest.raises(HarlequinConnectionError):
        _ = NebulaGraphAdapter(conn_str=tuple(), port=12345).connect()


@pytest.fixture
def connection() -> NebulaGraphConnection:
    return NebulaGraphAdapter(conn_str=tuple()).connect()


def test_get_catalog(connection: NebulaGraphConnection) -> None:
    catalog = connection.get_catalog()
    assert isinstance(catalog, Catalog)
    assert catalog.items
    assert isinstance(catalog.items[0], CatalogItem)


def test_execute_select(connection: NebulaGraphConnection) -> None:
    cur = connection.execute("YIELD 1 AS a")
    assert isinstance(cur, HarlequinCursor)
    assert cur.columns() == [("a", "#")]
    data = cur.fetchall()
    backend = create_backend(data)
    assert backend.column_count == 1
    assert backend.row_count == 1


def test_set_limit(connection: NebulaGraphConnection) -> None:
    cur = connection.execute(
        "YIELD 1 AS a UNION ALL YIELD 2 AS a UNION ALL YIELD 3 AS a"
    )
    assert isinstance(cur, HarlequinCursor)
    cur = cur.set_limit(2)
    assert isinstance(cur, HarlequinCursor)
    data = cur.fetchall()
    backend = create_backend(data)
    assert backend.column_count == 1
    assert backend.row_count == 2


def test_execute_raises_query_error(connection: NebulaGraphConnection) -> None:
    with pytest.raises(HarlequinQueryError):
        _ = connection.execute("YIELD;")
