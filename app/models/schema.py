from pydantic import BaseModel, Field
from typing import Dict, List

class ForeignKeyRef(BaseModel):
    table: str
    column: str

class ForeignKey(BaseModel):
    column: str
    references: ForeignKeyRef

class TableSchema(BaseModel):
    columns: Dict[str, str]
    primary_key: List[str]
    foreign_keys: List[ForeignKey]

class SchemaResponse(BaseModel):
    version: str = "v1"
    tables: Dict[str, TableSchema]

class SchemaRequest(BaseModel):
    db_id: str = Field(..., example="tenant_analytics")
    schema_name: str = Field(default="public", example="public")


class PrunedResponse(BaseModel):
    version: str = 'v2'
    tables: Dict[str, TableSchema]