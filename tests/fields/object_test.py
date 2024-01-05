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


        # recursive_check(field.types[0], truth)
    #recursive_check(field.types[0], truth)

    # assert field.to_surql("test_table") == "\n".join([
    #     "DEFINE FIELD test ON TABLE test_table TYPE object;",
    #     "DEFINE FIELD test.name ON TABLE test_table TYPE string;",
    #     "DEFINE FIELD test.age ON TABLE test_table TYPE number;",
    #     "DEFINE FIELD test.score ON TABLE test_table TYPE optional<number>;",
    #     "DEFINE FIELD test.is_active ON TABLE test_table TYPE boolean;",
    #     "DEFINE FIELD test.birthday ON TABLE test_table TYPE date;",
    #     "DEFINE FIELD test.nickname ON TABLE test_table TYPE optional<string>;",
    #     "DEFINE FIELD test.details ON TABLE test_table TYPE object;",
    #     "DEFINE FIELD test.details.address ON TABLE test_table TYPE string;",
    #     "DEFINE FIELD test.details.phone ON TABLE test_table TYPE string;",
    # ])