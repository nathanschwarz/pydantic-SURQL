from datetime import datetime
from typing import Optional
from ..pydantic_surql import toSurql
from ..pydantic_surql.types import SurQLNullable
from pydantic import BaseModel

@toSurql("basic_types")
class BasicTypesTest(BaseModel):
    """
        test all basic types parsing :
        string, number, datetime, bool, nullable, optional
    """
    t_str: str
    t_float: float
    t_int: int
    t_bool: bool
    t_date: datetime
    t_nullable: str | SurQLNullable
    t_optional: Optional[str]

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
    print("testing parsing")