from harlequin.options import (
    FlagOption,  # noqa
    ListOption,  # noqa
    PathOption,  # noqa
    SelectOption,  # noqa
    TextOption,
)

host = TextOption(
    name="host",
    description=("The host name or IP address of the NebulaGraph Graphd service."),
    short_decls=["-h"],
    default="localhost",
)

port = TextOption(
    name="port",
    description=("The port of the NebulaGraph Graphd service."),
    short_decls=["-p"],
    default="9669",
)

user = TextOption(
    name="user",
    description=("The user to connect to the NebulaGraph Graphd service."),
    short_decls=["-u"],
    default="root",
)

password = TextOption(
    name="password",
    description=("The password to connect to the NebulaGraph Graphd service."),
    short_decls=["-pw"],
    default="nebula",
)

NEBULAGRAPH_OPTIONS = [host, port, user, password]
