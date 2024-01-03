from datetime import datetime
from typing import Any, Optional
from pydantic_surql import toSurql, Mapper
from pydantic_surql.types import SurQLNullable
from pydantic import BaseModel, Field

@toSurql("basic_types")
class BasicTypesTest(BaseModel):
    """
        test all basic types parsing
    """
    t_str: str = Field(description="should be a string")
    t_float: float = Field(description="should be a number")
    t_int: int = Field(description="should be a number")
    t_bool: bool = Field(description="should be a boolean")
    t_date: datetime = Field(description="should be a datetime")
    t_nullable: str | SurQLNullable = Field(description="should be a nullable string")
    t_optional: Optional[str] = Field(description="should be an optional string")
    t_optional_nullable: Optional[str | SurQLNullable] = Field(description="should be an optional nullable string")
    t_any: Any = Field(description="should be an any type")
    t_dict: dict = Field(description="should be an object")
    t_multi: str | int | float | bool | datetime | dict = Field(description="should be a multi type")

@toSurql("array_types")
class BasicArrayTypesTest(BaseModel):
    """
        test all basic array types parsing :
        - string
        - number
        - datetime
        - bool
        - dict
        - nested arrays
    """
    arr_str: list[str]
    arr_float: list[float]
    arr_int: list[int]
    arr_bool: list[bool]
    arr_date: list[datetime]
    arr_dict: list[dict]
    arr_nullable: list[str | SurQLNullable]
    arr_optional: Optional[list[str]]
    arr_optional_nullable: Optional[list[str | SurQLNullable]]
    arr_any: list[Any]
    arr_multi: list[str | int | float | bool | datetime | dict]
    arr_nested: list[list[str]]
    arr_nested_nested: list[list[list[str]]]


@toSurql("record_types")
class complexRecordTest(BaseModel):
    """
        test all records types parsing :
            - record
            - array<records>
            - optional<record>
            - optional<array<records>>
            - nullable<record>
            - nullable<array<records>>
    """
    complex_record: BasicTypesTest
    nullable_record: SurQLNullable | BasicTypesTest
    optional_record: Optional[BasicTypesTest]
    complex_record_arr: list[BasicTypesTest]
    nullable_record_arr: list[SurQLNullable | BasicTypesTest]
    optional_record_arr: Optional[list[BasicTypesTest]]

def main():
    for table in Mapper.tables:
        print(table.model_dump_json(indent=2))
        #print(table.to_surql())