from datetime import datetime
from typing import Any, Optional
from pydantic_surql import SurQLParser
from pydantic_surql.types import SurQLIndex, SurQLNullable, SurQLTableConfig, SurQLType, SurQLField, SurQLView, SurQLPermissions
from pydantic import BaseModel, ConfigDict, ValidationError

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
    table = Parser.from_model(name, TableModel, SurQLTableConfig(strict=True))
    assert table.name == name
    assert table._table_def() == "DEFINE TABLE %s SCHEMAFULL;" % name

def test_strict_schemaless_table():
    """
        Test a schemaless table
    """
    name = "test_table"
    #mandatory to mark the child table object as a collection internally
    table = Parser.from_model(name, TableModel, config=SurQLTableConfig(strict=False))
    assert table.name == name
    assert TableModel.model_config.get('extra') == "allow"
    assert table._table_def() == "DEFINE TABLE %s SCHEMALESS;" % name

    # reset the value to avoid side effects on next tests
    TableModel.model_config['extra'] = None

def test_strict_schemaless_table_with_extra_allow():
    """
        Test a schemaless table with extra allow
    """
    name = "test_table"
    #mandatory to mark the child table object as a collection internally
    table = Parser.from_model(name, SchemalessTable)
    assert table.name == name
    assert SchemalessTable.model_config.get('extra') == "allow"
    assert table.config.strict == False, "config.strict must be False"
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

def test_table_good_permissions():
    """
        Test a table with permissions
    """
    name = "test_table"
    permissions = SurQLPermissions(
        select=["WHERE published = true", "OR user = $auth.id"],
        create=["WHERE user = $auth.id"],
        update=["WHERE user = $auth.id"],
        delete=["WHERE user = $auth.id", "OR $auth.admin = true"]
    )
    perm_str = permissions.SDL()
    config = SurQLTableConfig(permissions=permissions)
    #mandatory to mark the child table object as a collection internally
    table = Parser.from_model(name, TableModel, config=config)
    assert table.name == name
    assert table._table_def() == "DEFINE TABLE %s SCHEMAFULL %s;" % (name, perm_str)