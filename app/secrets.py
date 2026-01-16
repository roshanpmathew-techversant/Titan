import os

def get_connection_string(db_id: str) -> str | None:
    """
    Maps db_id -> PostgreSQL connection string

    """
    print(db_id)
    print(os.getenv(f"DB_{db_id.upper()}")    )

    return os.getenv(f"DB_{db_id.upper()}")