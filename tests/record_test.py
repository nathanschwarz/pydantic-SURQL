from datetime import datetime
from typing import Any, Optional
from pydantic_surql import model_to_surql
from pydantic_surql.parsers import parseFields
from pydantic_surql.types import SurQLNullable, SurQLType, SurQLField
from pydantic import BaseModel


class ChildObject(BaseModel):
    address: str
    phone: str

class ParentObject(BaseModel):
    name: str
    age: int
    score: float | SurQLNullable
    is_active: bool
    birthday: datetime
    nickname: Optional[str] = None
    details: ChildObject
    details_opt: Optional[ChildObject]
    details_arr: list[ChildObject]

def check_field(field: SurQLField, truth: SurQLField):
    assert field.name == truth.name
    assert field.recordLink == truth.recordLink
    assert len(field.types) == len(truth.types)
    assert set(field.types) == set(truth.types)

def check_fields(fields: list[SurQLField], truth: list[SurQLField]):
    for (idx, field) in enumerate(fields):
        if (not field.name.startswith("details")):
            check_field(field, truth[idx])
        elif (field.name.endswith('arr')):
            check_field(field.types[0][0], truth[idx].types[0][0])
        else:
            check_field(field.types[0], truth[idx].types[0])

def test_record():
    """
        Test the record type
    """
    #mandatory to mark the child table object as a collection internally
    childTable = model_to_surql("child_table", ChildObject)
    table = model_to_surql("parent_table", ParentObject)
    fields = parseFields(ParentObject)
    details = SurQLField(name=None, types=[SurQLType.RECORD], recordLink="child_table")
    truth = [
        SurQLField(name="name", types=[SurQLType.STRING]),
        SurQLField(name="age", types=[SurQLType.NUMBER]),
        SurQLField(name="score", types=[SurQLType.NUMBER, SurQLType.NULL]),
        SurQLField(name="is_active", types=[SurQLType.BOOLEAN]),
        SurQLField(name="birthday", types=[SurQLType.DATE]),
        SurQLField(name="nickname", types=[SurQLType.STRING, SurQLType.OPTIONAL]),
        SurQLField(name="details", types=[details]),
        SurQLField(name="details_opt", types=[details, SurQLType.OPTIONAL]),
        SurQLField(name="details_arr", types=[[details]]),
    ]
    check_fields(fields, truth)
    assert table.SDL() == "\n".join([
        "DEFINE TABLE %s SCHEMAFULL;" % table.name,
        "DEFINE FIELD name ON TABLE %s TYPE string;" % table.name,
        "DEFINE FIELD age ON TABLE %s TYPE number;" % table.name,
        "DEFINE FIELD score ON TABLE %s TYPE number|null;" % table.name,
        "DEFINE FIELD is_active ON TABLE %s TYPE bool;" % table.name,
        "DEFINE FIELD birthday ON TABLE %s TYPE datetime;" % table.name,
        "DEFINE FIELD nickname ON TABLE %s TYPE optional<string>;" % table.name,
        "DEFINE FIELD details ON TABLE %s TYPE record<child_table>;" % table.name,
        "DEFINE FIELD details_opt ON TABLE %s TYPE optional<record<child_table>>;" % table.name,
        "DEFINE FIELD details_arr ON TABLE %s TYPE array;" % table.name,
        "DEFINE FIELD details_arr.* ON TABLE %s TYPE record<child_table>;" % table.name,
    ])