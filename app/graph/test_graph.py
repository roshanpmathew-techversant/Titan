from app.graph.graph import build_titan_graph

def test_langgraph():
    graph = build_titan_graph()

    state = {
        "user_query": "load schema",
        "db_id": "tenant_analytics",
        "schema_name": "public"
        }



    result = graph.invoke(state)

    print("Final keys:", result.keys())
    print("Tables:", result["schema"].tables.keys())

if __name__ == "__main__":
    test_langgraph()
