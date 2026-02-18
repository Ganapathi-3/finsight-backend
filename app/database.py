import duckdb

# Persistent database file
con = duckdb.connect(database="finsight.db")

def init_db():
    con.execute("""
        CREATE TABLE IF NOT EXISTS department_data (
            id INTEGER,
            department VARCHAR,
            revenue DOUBLE
        )
    """)

    # Insert sample data (only if empty)
    existing = con.execute("SELECT COUNT(*) FROM department_data").fetchone()[0]

    if existing == 0:
        con.execute("INSERT INTO department_data VALUES (1, 'finance', 100000)")
        con.execute("INSERT INTO department_data VALUES (2, 'hr', 20000)")
        con.execute("INSERT INTO department_data VALUES (3, 'executive', 500000)")

init_db()

def run_sql(query: str):
    return con.execute(query).fetchall()
