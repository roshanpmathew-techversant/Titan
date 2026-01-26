from collections import defaultdict

def table_signature(table_def: dict) -> tuple:
    """
    Creates a hashable signature for a table based on columns.
    """
    cols = table_def["columns"]
    return tuple(sorted(
        (col.lower(), dtype.lower())
        for col, dtype in cols.items()
    ))

def collapse_similar_tables(schema: dict) -> dict:
    """
    Collapse tables with identical column structures into logical tables.
    Returns a dictionary with 'tables' and 'logical_to_physical'.
    """
    tables = schema["tables"]
    groups = defaultdict(list)

    for table_name, table_def in tables.items():
        sig = table_signature(table_def)
        groups[sig].append(table_name)

    collapsed_tables = {}
    logical_to_physical = {}

    for sig, table_names in groups.items():
        if len(table_names) == 1:
            # Single table → keep as-is
            t = table_names[0]
            collapsed_tables[t] = tables[t]
        else:
            # Multiple tables → collapse into logical table
            logical_name = table_names[0].rsplit("_", 1)[0]  # e.g., store_txn_XAH → store_txn
            base_table = tables[table_names[0]]

            collapsed_tables[logical_name] = {
                "columns": {
                    "source_table": "text",  # virtual column to track origin
                    **base_table["columns"]
                },
                "primary_key": base_table["primary_key"],
                "foreign_keys": base_table["foreign_keys"],
                "source_tables": table_names
            }

            logical_to_physical[logical_name] = table_names

    return {
        "tables": collapsed_tables,
        "logical_to_physical": logical_to_physical
    }

def load_schema(conn, schema_name: str = "public") -> dict:
    """
    Load the database schema and collapse similar tables into logical tables.
    Returns a dictionary with 'tables' and 'logical_to_physical'.
    """
    schema = {"tables": {}}

    with conn.cursor() as cur:
        # Tables
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """, (schema_name,))
        tables = [r[0] for r in cur.fetchall()]

        for table in tables:
            schema["tables"][table] = {
                "columns": {},
                "primary_key": [],
                "foreign_keys": []
            }

        # Columns
        cur.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = %s
            ORDER BY table_name, ordinal_position
        """, (schema_name,))
        for t, c, d in cur.fetchall():
            if t in schema["tables"]:
                schema["tables"][t]["columns"][c] = d

        # Primary keys
        cur.execute("""
            SELECT tc.table_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_schema = %s
            ORDER BY tc.table_name, kcu.ordinal_position
        """, (schema_name,))
        for t, c in cur.fetchall():
            if t in schema["tables"]:
                schema["tables"][t]["primary_key"].append(c)

        # Foreign keys
        cur.execute("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name,
                ccu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
              ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = %s
            ORDER BY tc.table_name
        """, (schema_name,))
        for t, c, ft, fc in cur.fetchall():
            if t in schema["tables"]:
                schema["tables"][t]["foreign_keys"].append({
                    "column": c,
                    "references": {
                        "table": ft,
                        "column": fc
                    }
                })

    # Collapse similar tables before returning
    return collapse_similar_tables(schema)
