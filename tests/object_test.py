from datetime import datetime
from typing import Any, Optional
from pydantic_surql.parsers import parseFields
from pydantic_surql.types import SurQLNullable, SurQLAnyRecord, SurQLType, SurQLField
from pydantic import BaseModel

class ChildChildObject(BaseModel):
    country: str
    city: str

class ChildObject(BaseModel):
    address: str
    phone: str
    details: ChildChildObject

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
    assert len(fields) == len(truth)
    for (idx, field) in enumerate(fields):
        if (not field.name.startswith("details")):
            check_field(field, truth[idx])
        elif (field.name.endswith('arr')):
            check_fields(field.types[0][0].types, truth[idx].types[0][0].types)
        else:
            check_fields(field.types[0].types, truth[idx].types[0].types)

def test_object():
    fields = parseFields(ParentObject)
    details = SurQLField(name=None, types=[
            SurQLField(name="address", types=[SurQLType.STRING]),
            SurQLField(name="phone", types=[SurQLType.STRING]),
            SurQLField(name="details", types=[
                SurQLField(name=None, types=[
                    SurQLField(name="country", types=[SurQLType.STRING]),
                    SurQLField(name="city", types=[SurQLType.STRING]),
                ])
            ]),
        ])
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
    table = "test_table"
    detailsSDL = [
        "DEFINE FIELD %s.address ON TABLE %s TYPE string;",
        "DEFINE FIELD %s.phone ON TABLE %s TYPE string;",
        "DEFINE FIELD %s.details ON TABLE %s TYPE object;",
        "DEFINE FIELD %s.details.country ON TABLE %s TYPE string;",
        "DEFINE FIELD %s.details.city ON TABLE %s TYPE string;",
    ]
    assert [field.SDL(table) for field in fields[0:6]] == [
        "DEFINE FIELD name ON TABLE test_table TYPE string;",
        "DEFINE FIELD age ON TABLE test_table TYPE number;",
        "DEFINE FIELD score ON TABLE test_table TYPE number|null;",
        "DEFINE FIELD is_active ON TABLE test_table TYPE bool;",
        "DEFINE FIELD birthday ON TABLE test_table TYPE datetime;",
        "DEFINE FIELD nickname ON TABLE test_table TYPE optional<string>;",
    ]
    assert fields[6].SDL(table) == "\n".join(
        ["DEFINE FIELD %s ON TABLE %s TYPE %s;" % ("details", table, "object")] +
        [e % ("details", table) for e in detailsSDL]
    )
    assert fields[7].SDL(table) == "\n".join(
        ["DEFINE FIELD %s ON TABLE %s TYPE %s;" % ("details_opt", table, "optional<object>")] +
        [e % ("details_opt", table) for e in detailsSDL]
    )
    assert fields[8].SDL(table) == "\n".join(
        [
            "DEFINE FIELD %s ON TABLE %s TYPE %s;" % ("details_arr", table, "array"),
            "DEFINE FIELD %s.* ON TABLE %s TYPE %s;" % ("details_arr", table, "object"),
        ] +
        [e % ("details_arr.*", table) for e in detailsSDL]
    )