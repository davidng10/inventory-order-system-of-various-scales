from dataclasses import dataclass

import psycopg2
from psycopg2.extensions import connection as Connection

from psycopg2.extras import RealDictCursor


@dataclass
class ServiceBase:
    connection: Connection


def get_cursor(args: ServiceBase) -> RealDictCursor:
    connection = args.connection
    return connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # type: ignore
