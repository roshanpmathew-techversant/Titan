import json

import re
from app.graph.state import TitanState
from app.services.Schema_pruning.initial_prune import initial_prune
from app.services.write_to_file import write_pruned_table_names
from app.llm.gemini import gemini_llm_call
from app.core.secrets import get_gemini_api_key
from app.models.schema import TableSchema, PrunedResponse
from langfuse import observe
from app.services.Schema_pruning.secondary_prune import serialize_schema_for_llm, validate_llm_output


@observe()
def schema_pruner_node(state: TitanState) -> TitanState:
    raw_schema = state["schema"]
    # combined_tables = state["schema"]["logical_to_physical"]
    # print(combined_tables)
    intent = state.get("intent")
    user_question = state.get("user_query")

    # print("Schema Pruner Called")

    
    pruned_schema = initial_prune(raw_schema, intent)
    write_pruned_table_names(pruned_schema, "pruned_schema.txt")

    
    # print("Schema Pruner: initial pruning successful.")

    # print("Schema Pruner: schema serialization to be done.")
    safe_schema = serialize_schema_for_llm(pruned_schema)
    # print("Schema Pruner: schema serialization successful.")


    if isinstance(pruned_schema, PrunedResponse):
        final_tables = pruned_schema.tables
    else:
        final_tables = pruned_schema.get("tables", {})
    # print("Final tables: Done", )
   

    try:
        api_key = get_gemini_api_key()
        # print("Schema Pruner: API key fetched.")
        if not api_key:
            raise RuntimeError("Gemini API key is not configured.")

        system_prompt = """
        You are a database schema pruning engine.

        Rules:
        - You may ONLY remove tables or columns.
        - You must NOT add, rename, or invent tables or columns.
        - You must NOT infer new relationships.
        - You must consider the Combined Tables List when deciding which tables are relevant.
        - If multiple physical tables are combined into a logical table, treat them as a single unit.
        - Do NOT select individual physical tables if a combined (logical) table is available.
        - If unsure about a table, KEEP it.
        - Output MUST be valid JSON mapping table_name -> list[column_name].
        - If a logical table exists in Combined Tables List, selecting any of its physical tables is INVALID.

        """


        user_prompt = f"""
            User question:
            {user_question}

            Parsed intent:
            {intent}

            Database schema:
            {safe_schema}

            Task:
            Return ONLY the minimal set of tables and columns required to answer the question.

            Important:
            - If a table appears in the Combined Tables List, prefer the combined (logical) table.
            - Do NOT include individual physical tables that belong to a combined table.
            - Prune columns only after selecting the correct table (logical or standalone).
            """

        # print("Schema Pruner: LLM call to be done")

        raw_llm_output = gemini_llm_call(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            api_key=api_key,
            metadata={"node": "schema_pruner_node"},
        )
        # print("Schema Pruner: LLM call successful.",raw_llm_output)

        raw_llm_output = re.sub(
            r"^```(?:json)?\s*|\s*```$", "",
            raw_llm_output,
            flags=re.IGNORECASE,
        ).strip()

        llm_output = json.loads(raw_llm_output)
        if not isinstance(llm_output, dict):
            raise ValueError("LLM did not return JSON dict")
        # print("Schema Pruner: Gonna Validate OP.")    
        final_tables = validate_llm_output(
            llm_output=llm_output,
            original_schema=pruned_schema
        )
        # print("Schema Pruner: LLM output validated.")

        # print("Schema Pruner LLM wise pruning successful.")

    except Exception as e:
        print(f"[SchemaPruner] LLM pruning failed, using fallback: {e}")

   
    assert isinstance(final_tables, dict)

    return {
        **state,
        "pruned_schema": PrunedResponse(
            version="v2",
            tables=final_tables
        )
    }
