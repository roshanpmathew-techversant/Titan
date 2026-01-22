from app.services.Schema_pruning.initial_prune import initial_prune
mock_schema = {
    "tables": {
        # ❌ Dropped: system table (user)
        "UserActivity": {
            "columns": {
                "id": "integer",
                "user_id": "integer",
                "action": "text",
                "created_at": "timestamp without time zone"
            },
            "primary_key": ["id"],
            "foreign_keys": []
        },

        # ❌ Dropped: no numeric metric
        "ProductCatalog": {
            "columns": {
                "product_id": "integer",
                "name": "text",
                "category": "text",
                "created_at": "timestamp without time zone"
            },
            "primary_key": ["product_id"],
            "foreign_keys": []
        },

        # ✅ Kept
        "SalesMetrics": {
            "columns": {
                "sale_id": "integer",
                "order_amount": "decimal",
                "quantity": "integer",
                "sale_date": "date"
            },
            "primary_key": ["sale_id"],
            "foreign_keys": [
                {
                    "column": "sale_id",
                    "references": {
                        "table": "Orders",
                        "column": "id"
                    }
                }
            ]
        }
    }
}




initial_prune(mock_schema)

