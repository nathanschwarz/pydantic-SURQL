from datetime import datetime
from typing import Any, Optional
from pydantic_surql import model_to_surql
from pydantic_surql.parsers import parseFields
from pydantic_surql.types import SurQLNullable, SurQLTableConfig, SurQLType, SurQLField, SurQLView
from pydantic import BaseModel

class TableModel(BaseModel):
    name: str
    age: int
    score: float | SurQLNullable
    is_active: bool
    birthday: datetime
    nickname: Optional[str] = None

def test_schemafull_table():
    """
        Test a schemafull table
    """
    name = "test_table"
    #mandatory to mark the child table object as a collection internally
    table = model_to_surql(name, TableModel, SurQLTableConfig(strict=True))
    assert table.name == name
    assert table._table_def() == "DEFINE TABLE %s SCHEMAFULL;" % name

def test_schemaless_table():
    """
        Test a schemaless table
    """
    name = "test_table"
    #mandatory to mark the child table object as a collection internally
    table = model_to_surql(name, TableModel, config=SurQLTableConfig(strict=False))
    assert table.name == name
    assert table._table_def() == "DEFINE TABLE %s SCHEMALESS;" % name

def test_table_view():
    """
        Test a table as a view
    """
    name = "test_table"
    view_name = "test_view"
    #mandatory to mark the child table object as a collection internally
    table = model_to_surql(view_name, TableModel, config=SurQLTableConfig(asView=SurQLView(select=["name", "age"], from_t=[name], where=["age > 18"], group_by=["name"])))
    assert table.name == view_name
    assert table._table_def() == "DEFINE TABLE %s AS SELECT name,age FROM %s WHERE age > 18 GROUP BY name;" % (view_name, name)

def test_table_drop():
    """
        Test a table with drop
    """
    name = "test_table"
    #mandatory to mark the child table object as a collection internally
    table = model_to_surql(name, TableModel, config=SurQLTableConfig(drop=True))
    assert table.name == name
    assert table._table_def() == "DEFINE TABLE %s DROP SCHEMAFULL;" % name