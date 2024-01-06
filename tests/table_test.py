from datetime import datetime
from typing import Any, Optional
from pydantic_surql import SurQLParser
from pydantic_surql.types import SurQLIndex, SurQLNullable, SurQLTableConfig, SurQLType, SurQLField, SurQLView
from pydantic import BaseModel

Parser = SurQLParser()
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
    table = Parser.from_model(name, TableModel, SurQLTableConfig(strict=True))
    assert table.name == name
    assert table._table_def() == "DEFINE TABLE %s SCHEMAFULL;" % name

def test_schemaless_table():
    """
        Test a schemaless table
    """
    name = "test_table"
    #mandatory to mark the child table object as a collection internally
    table = Parser.from_model(name, TableModel, config=SurQLTableConfig(strict=False))
    assert table.name == name
    assert table._table_def() == "DEFINE TABLE %s SCHEMALESS;" % name

def test_table_view():
    """
        Test a table as a view
    """
    name = "test_table"
    view_name = "test_view"
    #mandatory to mark the child table object as a collection internally
    table = Parser.from_model(view_name, TableModel, config=SurQLTableConfig(asView=SurQLView(select=["name", "age"], from_t=[name], where=["age > 18"], group_by=["name"])))
    assert table.name == view_name
    assert table._table_def() == "DEFINE TABLE %s AS SELECT name,age FROM %s WHERE age > 18 GROUP BY name;" % (view_name, name)

def test_table_drop():
    """
        Test a table with drop
    """
    name = "test_table"
    #mandatory to mark the child table object as a collection internally
    table = Parser.from_model(name, TableModel, config=SurQLTableConfig(drop=True))
    assert table.name == name
    assert table._table_def() == "DEFINE TABLE %s DROP SCHEMAFULL;" % name

def test_table_change_feed():
    """
        Test a table with change feed
    """
    name = "test_table"
    changeFeed = "1d"
    #mandatory to mark the child table object as a collection internally
    table = Parser.from_model(name, TableModel, config=SurQLTableConfig(changeFeed=changeFeed))
    assert table.name == name
    assert table._table_def() == "DEFINE TABLE %s SCHEMAFULL CHANGEFEED %s;" % (name, changeFeed)

def test_table_indexes():
    """
        Test a table with indexes and unique indexes
        TODO: search indexes
    """
    name = "test_table"
    #mandatory to mark the child table object as a collection internally
    table = Parser.from_model(name, TableModel, config=SurQLTableConfig(indexes=[
        SurQLIndex(name="test_index", fields=["name", "age"]),
        SurQLIndex(name="test_index2", fields=["nickname"], unique=True),
    ]))
    assert table.name == name
    assert table.SDL() == "\n".join([
        "DEFINE TABLE %s SCHEMAFULL;" % name,
        "DEFINE FIELD name ON TABLE %s TYPE string;" % name,
        "DEFINE FIELD age ON TABLE %s TYPE number;" % name,
        "DEFINE FIELD score ON TABLE %s TYPE number|null;" % name,
        "DEFINE FIELD is_active ON TABLE %s TYPE bool;" % name,
        "DEFINE FIELD birthday ON TABLE %s TYPE datetime;" % name,
        "DEFINE FIELD nickname ON TABLE %s TYPE optional<string>;" % name,
        "DEFINE INDEX test_index ON TABLE %s FIELDS name,age;" % name,
        "DEFINE INDEX test_index2 ON TABLE %s UNIQUE FIELDS nickname;" % name,
    ])