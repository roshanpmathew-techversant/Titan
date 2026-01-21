def write_table_names(schema: dict, output_file: str = "schema.txt"):
    if not schema or "tables" not in schema:
        return

    tables = schema["tables"]

    with open(output_file, "w", encoding="utf-8") as f:
        for table_name in tables:
            f.write(f"{table_name}\n")
