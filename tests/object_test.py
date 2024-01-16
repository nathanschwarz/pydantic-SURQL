from datetime import datetime
from typing import Any, Optional
from pydantic_surql.parser import SurQLParser
from pydantic_surql.types import SurQLNullable, SurQLType, SurQLField, RecursiveType
from pydantic import BaseModel, ConfigDict

Parser = SurQLParser()

class ChildChildObject(BaseModel):
    model_config = ConfigDict(extra="allow")
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

def check_fields(fields: RecursiveType, truth: RecursiveType):
    assert len(fields) == len(truth), "fields and truth must have the same length"
    for (idx, field) in enumerate(fields):
        if (isinstance(field, list)):
            check_fields(field, truth[idx])
        elif (isinstance(field, SurQLField)):
            assert field.name == truth[idx].name, "field name must be the same"
            assert field.recordLink == truth[idx].recordLink, "field recordLink must be the same"
            assert len(field.types) == len(truth[idx].types), "field %s types must have the same length %s\n%s" % (
                field.name,
                field.model_dump_json(indent=2),
                truth[idx].model_dump_json(indent=2)
            )
            check_fields(field.types, truth[idx].types)
        else:
            assert field == truth[idx], f"field type is incorrect, got {field} vs {truth[idx]}"

def test_object():
    """
        test the object type SDL generation
    """
    fields = Parser.from_fields(ParentObject)
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
        "DEFINE FIELD %s.details ON TABLE %s FLEXIBLE TYPE object;",
        "DEFINE FIELD %s.details.country ON TABLE %s TYPE string;",
        "DEFINE FIELD %s.details.city ON TABLE %s TYPE string;",
    ]
    assert [field.SDL(table) for field in fields[0:6]] == [
        "DEFINE FIELD name ON TABLE test_table TYPE string;",
        "DEFINE FIELD age ON TABLE test_table TYPE number;",
        "DEFINE FIELD score ON TABLE test_table TYPE number|null;",
        "DEFINE FIELD is_active ON TABLE test_table TYPE bool;",
        "DEFINE FIELD birthday ON TABLE test_table TYPE datetime;",
        "DEFINE FIELD nickname ON TABLE test_table TYPE option<string>;",
    ]
    assert fields[6].SDL(table) == "\n".join(
        ["DEFINE FIELD %s ON TABLE %s TYPE %s;" % ("details", table, "object")] +
        [e % ("details", table) for e in detailsSDL]
    )
    assert fields[7].SDL(table) == "\n".join(
        ["DEFINE FIELD %s ON TABLE %s TYPE %s;" % ("details_opt", table, "option<object>")] +
        [e % ("details_opt", table) for e in detailsSDL]
    )
    assert fields[8].SDL(table) == "\n".join(
        [
            "DEFINE FIELD %s ON TABLE %s TYPE %s;" % ("details_arr", table, "array"),
            "DEFINE FIELD %s.* ON TABLE %s TYPE %s;" % ("details_arr", table, "object"),
        ] +
        [e % ("details_arr.*", table) for e in detailsSDL]
    )