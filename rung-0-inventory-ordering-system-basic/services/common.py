from dataclasses import dataclass

import psycopg2
from psycopg2.extensions import connection as Connection

@dataclass
class ServiceBase:
    connection: Connection

def get_cursor(args: ServiceBase):
    connection = args.connection
    return connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
