from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic_surql.parser import SurQLParser
from pydantic_surql.types.field import SurQLFieldConfig, SurQLNullable
from pydantic_surql.types.permissions import SurQLPermissions
from pydantic_surql.types.table import SurQLTableConfig


perms = SurQLPermissions.model_construct(
    select=["WHERE user = $auth.id"],
    create=["WHERE user = $auth.id"],
    update=["WHERE user = $auth.id"],
    delete=["WHERE user = $auth.id"]
)

Parser = SurQLParser()
class GrandChildObject(BaseModel):
    phone: str = SurQLFieldConfig(permissions=perms, min_length=8)

class ChildObject(BaseModel):
    address: str = SurQLFieldConfig(permissions=perms)
    obj: GrandChildObject

class TableModel(BaseModel):
    name: str
    age: int
    score: float | SurQLNullable
    is_active: bool
    birthday: datetime
    nickname: Optional[str] = None
    child: ChildObject =  SurQLFieldConfig(permissions=perms)
    arr_child: list[ChildObject] = SurQLFieldConfig(permissions=perms)


def test_table_permissions():
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
    assert table._table_def() == "DEFINE TABLE %s SCHEMAFULL %s;" % (name, perm_str)

def test_table_fields_perms():
    """
        Test a table with permissions
    """
    name = "test_table"
    #mandatory to mark the child table object as a collection internally
    table = Parser.from_model(name, TableModel)
    sdl = table.SDL()
    perms_sdl = perms.SDL()
    truth = "\n".join([
        "DEFINE TABLE %s SCHEMAFULL;" % name,
        "DEFINE FIELD name ON TABLE %s TYPE string;" % name,
        "DEFINE FIELD age ON TABLE %s TYPE number;" % name,
        "DEFINE FIELD score ON TABLE %s TYPE number|null;" % name,
        "DEFINE FIELD is_active ON TABLE %s TYPE bool;" % name,
        "DEFINE FIELD birthday ON TABLE %s TYPE datetime;" % name,
        "DEFINE FIELD nickname ON TABLE %s TYPE optional<string>;" % name,
        "DEFINE FIELD child ON TABLE %s TYPE object %s;" % (name, perms_sdl),
        "DEFINE FIELD child.address ON TABLE %s TYPE string %s;" % (name, perms_sdl),
        "DEFINE FIELD child.obj ON TABLE %s TYPE object;" % name,
        "DEFINE FIELD child.obj.phone ON TABLE %s TYPE string %s;" % (name, perms_sdl),
        "DEFINE FIELD arr_child ON TABLE %s TYPE array %s;" % (name, perms_sdl),
        "DEFINE FIELD arr_child.* ON TABLE %s TYPE object;" % name,
        "DEFINE FIELD arr_child.*.address ON TABLE %s TYPE string %s;" % (name, perms_sdl),
        "DEFINE FIELD arr_child.*.obj ON TABLE %s TYPE object;" % name,
        "DEFINE FIELD arr_child.*.obj.phone ON TABLE %s TYPE string %s;" % (name, perms_sdl),
    ])
    assert sdl == truth

    # check that the fields validation works
    try:
        GrandChildObject(phone="2")
    except BaseException as e:
        assert True