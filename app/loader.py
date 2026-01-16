def load_schema(conn, schema_name: str = "public") -> dict:
    schema = {"tables": {}}
    cur = conn.cursor()

    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s
          AND table_type = 'BASE TABLE'
    """, (schema_name,))
    tables = [r[0] for r in cur.fetchall()]

    for table in tables:
        schema["tables"][table] = {
            "columns": {},
            "primary_key": [],
            "foreign_keys": []
        }

    cur.execute("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = %s
    """, (schema_name,))
    for t, c, d in cur.fetchall():
        schema["tables"][t]["columns"][c] = d

    cur.execute("""
        SELECT tc.table_name, kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema = %s
    """, (schema_name,))
    for t, c in cur.fetchall():
        schema["tables"][t]["primary_key"].append(c)

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
    """, (schema_name,))
    for t, c, ft, fc in cur.fetchall():
        schema["tables"][t]["foreign_keys"].append({
            "column": c,
            "references": {"table": ft, "column": fc}
        })

    return schema
