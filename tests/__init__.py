from datetime import datetime
from typing import Any, Optional
from pydantic_surql import toSurql, Mapper
from pydantic_surql.types import SurQLNullable
from pydantic import BaseModel

@toSurql("basic_types")
class BasicTypesTest(BaseModel):
    """
        test all basic types parsing :
        string, number, datetime, bool, nullable, optional, any
    """
    t_str: str
    t_float: float
    t_int: int
    t_bool: bool
    t_date: datetime
    t_nullable: str | SurQLNullable
    t_optional: Optional[str]
    t_optional_nullable: Optional[str | SurQLNullable]
    t_any: Any

@toSurql("basic_array_types")
class BasicArrayTypesTest(BaseModel):
    """
        test all basic array types parsing :
        string, number, datetime, bool
    """
    t_str: list[str]
    t_float: list[float]
    t_int: list[int]
    t_bool: list[bool]
    t_date: list[datetime]

def main():
    for table in Mapper.tables:
        print(table.model_dump_json(indent=4))