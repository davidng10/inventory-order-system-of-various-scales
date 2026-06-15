import psycopg2

def seed():
    conn = psycopg2.connect(
        host="localhost",
        dbname="inventory-order-sys",
        user="postgres",
        password="postgres",
        port=5432
        )
    
    with conn.cursor() as cur:
        # Read and execute the SQL file
        with open("./sql/seed.sql", "r") as file:
            cur.execute(file.read())

    conn.commit()
    print("done")
    conn.close()


if __name__ == "__main__":
    print("seeding data");
    seed()
    print("seeding complete")
