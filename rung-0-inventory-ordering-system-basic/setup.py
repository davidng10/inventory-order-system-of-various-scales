import psycopg2
import os

def migrations():
    project_dir = os.path.join(os.path.dirname(__file__))
    migrations_path  = os.path.join(project_dir, "sql", "migrations")

    conn = psycopg2.connect(
        host="localhost",
        dbname="inventory-order-sys",
        user="postgres",
        password="postgres",
        port=5432
        )
    
    with conn.cursor() as cur:
        for root, dirs, files in os.walk(migrations_path):
            for f in files:
                file_path = os.path.join(migrations_path, f)
                with open(file_path) as file:
                    cur.execute(file.read())

    conn.commit()
    print("done")
    conn.close()


if __name__ == "__main__":
    print("initializing table");
    migrations()
    print("table initialized")
