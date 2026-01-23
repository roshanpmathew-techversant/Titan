from app.models.schema import TableSchema, PrunedResponse




def serialize_schema_for_llm(schema):
    """
    Convert schema to LLM-friendly format.
    Accepts:
        - dict with TableSchema values
        - or PrunedResponse object
    """
    if isinstance(schema, PrunedResponse):
        tables_dict = schema.tables
    elif isinstance(schema, dict):
        tables_dict = schema.get("tables", {})
    else:
        raise TypeError("Unsupported schema type")

    tables = []
    for table_name, table in tables_dict.items():
        # table.columns is a dict: iterate via .items()
        columns = [{"name": col_name, "type": col_type} for col_name, col_type in table.columns.items()]
        foreign_keys = [
            {"column": fk.column, "references": {"table": fk.references.table, "column": fk.references.column}}
            for fk in getattr(table, "foreign_keys", [])
        ]
        tables.append({"table": table_name, "columns": columns, "foreign_keys": foreign_keys})
    return tables



def validate_llm_output(llm_output, original_schema):
    if isinstance(original_schema, PrunedResponse):
        original_tables = original_schema.tables
    else:
        original_tables = original_schema.get("tables", {})

    valid_tables = {}
    for table_name, cols in llm_output.items():
        if table_name not in original_tables:
            continue
        table = original_tables[table_name]
        valid_columns = [col_name for col_name in table.columns if col_name in cols]
        if not valid_columns:
            continue
        valid_tables[table_name] = TableSchema(
            columns={k: table.columns[k] for k in valid_columns},
            primary_key=table.primary_key,
            foreign_keys=table.foreign_keys
        )
    return valid_tables

