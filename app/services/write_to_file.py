from app.models.schema import PrunedResponse


def write_table_names(schema: dict, output_file: str = "schema.txt"):
    if not schema or "tables" not in schema:
        return

    tables = schema["tables"]

    with open(output_file, "w", encoding="utf-8") as f:
        for table_name in tables:
            f.write(f"{table_name}\n")

def write_pruned_table_names(pruned: PrunedResponse, output_file: str):
    if not pruned or not pruned.tables:
        return

    with open(output_file, "w", encoding="utf-8") as f:
        for table_name in pruned.tables.keys():
            f.write(f"{table_name}\n")