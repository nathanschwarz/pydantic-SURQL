from datetime import datetime
from typing import Optional
from pydantic_surql import SurQLParser
from pydantic_surql.types import SurQLNullable, SurQLTableConfig, SurQLView
from pydantic import BaseModel, ConfigDict

from pydantic_surql.types.table import SurQLTable

Parser = SurQLParser()
class TableModel(BaseModel):
    name: str
    age: int
    score: float | SurQLNullable
    is_active: bool
    birthday: datetime
    nickname: Optional[str] = None

class SchemalessTable(TableModel):
    model_config = ConfigDict(extra="allow")

def test_strict_schemafull_table():
    """
        Test a schemafull table
    """
    name = "test_table"
    #mandatory to mark the child table object as a collection inÒternally
    model = Parser.from_model(name, TableModel, SurQLTableConfig(strict=True))
    table = SurQLTable(model=model)
    assert table.model.surql_table_name == name
    assert table.definition == "DEFINE TABLE %s SCHEMAFULL;" % name

def test_strict_schemaless_table():
    """
        Test a schemaless table
    """
    name = "test_table"
    #mandatory to mark the child table object as a collection internally
    model = Parser.from_model(name, TableModel, config=SurQLTableConfig(strict=False))
    table = SurQLTable(model=model)
    assert table.model.surql_table_name == name
    assert table.model.model_config.get('extra') == "allow"
    assert table.definition == "DEFINE TABLE %s SCHEMALESS;" % name

    # reset the value to avoid side effects on next tests
    TableModel.model_config['extra'] = None

def test_strict_schemaless_table_with_extra_allow():
    """
        Test a schemaless table with extra allow
    """
    name = "test_table"
    #mandatory to mark the child table object as a collection internally
    model = Parser.from_model(name, SchemalessTable)
    table = SurQLTable(model=model)
    assert table.model.surql_table_name == name
    assert SchemalessTable.model_config.get('extra') == "allow"
    assert table.model.surql_config.strict == False, "config.strict must be False"
    assert table.definition == "DEFINE TABLE %s SCHEMALESS;" % name

def test_table_view():
    """
        Test a table as a view
    """
    name = "test_table"
    view_name = "test_view"
    #mandatory to mark the child table object as a collection internally
    view = SurQLView(select=["name", "age"], from_t=[name], where=["age > 18"], group_by=["name"])
    model = Parser.from_model(view_name, TableModel, config=SurQLTableConfig(asView=view))
    table = SurQLTable(model=model)
    assert table.model.surql_table_name == view_name
    assert table.definition == "DEFINE TABLE %s AS SELECT name,age FROM %s WHERE age > 18 GROUP BY name;" % (view_name, name)

def test_table_drop():
    """
        Test a table with drop
    """
    name = "test_table"
    #mandatory to mark the child table object as a collection internally
    model = Parser.from_model(name, TableModel, config=SurQLTableConfig(drop=True))
    table = SurQLTable(model=model)
    assert table.model.surql_table_name == name
    assert table.definition == "DEFINE TABLE %s DROP SCHEMAFULL;" % name

def test_table_change_feed():
    """
        Test a table with change feed
    """
    name = "test_table"
    changeFeed = "1d"
    #mandatory to mark the child table object as a collection internally
    model = Parser.from_model(name, TableModel, config=SurQLTableConfig(changeFeed=changeFeed))
    table = SurQLTable(model=model)
    assert table.model.surql_table_name == name
    assert table.definition == "DEFINE TABLE %s SCHEMAFULL CHANGEFEED %s;" % (name, changeFeed)

