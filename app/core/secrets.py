import os

def get_connection_string(db_id: str) -> str | None:
    """
    Maps db_id -> PostgreSQL connection string

    """

    return os.getenv(f"DB_{db_id.upper()}")


