from typing import Union
from urllib.parse import urlsplit
from urllib.parse import urlunsplit

from pydantic import validate_arguments

_proto_map = {
    "postgres": "postgresql",
    "postgresql": "postgresql",
}


@validate_arguments
def with_driver(dsn: Union[str, bytes], driver: str) -> str:
    dsn_1: str = dsn.decode() if isinstance(dsn, bytes) else dsn
    components_1 = urlsplit(dsn_1)
    protocol_1 = components_1.scheme.split("+")[0]
    protocol_2 = _proto_map[protocol_1]
    scheme_2 = f"{protocol_2}+{driver}"
    components_2 = (scheme_2, *(components_1[1:]))
    dsn_2 = urlunsplit(components_2)

    return dsn_2
