from enum import Enum
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel
from pydantic_surql.parser import SurQLParser
from pydantic_surql.types import SurQLNullable, SurQLAnyRecord
from pydantic_surql.types.meta import Schema
from pydantic_surql.types.utils import SurQLType
from .base import Base

Parser = SurQLParser()

class EnumData(Enum):
    """
        Enum data
    """
    A = "a"
    B = "b"
    C = "c"
    D = 1
    E = 2
    F = 3

class BasePerson(BaseModel):
    """
        Base person
    """
    name: str
    age: int
    weight: float
    is_active: bool
    birthday: datetime
    nickname: Optional[str] = None
    tags: set[str] | None
    grades: list[float] | None
    links: list[str | SurQLNullable] | None

class SimpleTestObject(BasePerson):
    """
        Simple test object
    """
    classmates: list[BasePerson] | None

class TestSimpleFields(Base):
    def check_base_person(self, schema: Schema, path: str):
        # check fields

        # check name
        self.check_field(f"{path}.name", schema.fields[0], [SurQLType.STRING])

        # check age
        self.check_field(f"{path}.age", schema.fields[1], [SurQLType.NUMBER])

        # check weight
        self.check_field(f"{path}.weight", schema.fields[2], [SurQLType.NUMBER])

        # check is_active
        self.check_field(f"{path}.is_active", schema.fields[3], [SurQLType.BOOLEAN])

        # check birthday
        self.check_field(f"{path}.birthday", schema.fields[4], [SurQLType.DATE])

        # check nickname
        self.check_field(f"{path}.nickname", schema.fields[5], [SurQLType.STRING, SurQLType.OPTIONAL])

        # check tags
        self.check_field(f"{path}.tags", schema.fields[6], [SurQLType.SET, SurQLType.OPTIONAL])
        self.check_field(f"{path}.tags.*", schema.fields[6].definitions[0], [SurQLType.STRING])

        # check grades
        self.check_field(f"{path}.grades", schema.fields[7], [SurQLType.ARRAY, SurQLType.OPTIONAL])
        self.check_field(f"{path}.grades.*", schema.fields[7].definitions[0], [SurQLType.NUMBER])

        # check links
        self.check_field(f"{path}.links", schema.fields[8], [SurQLType.ARRAY, SurQLType.OPTIONAL])
        self.check_field(f"{path}.links.*", schema.fields[8].definitions[0], [SurQLType.STRING, SurQLType.NULL])

    def test_simple(self):
        """
            Test simple fields
        """
        TABLE = "test_table"
        model = Parser.from_model(TABLE, SimpleTestObject)
        schema = model.__surql_schema__
        assert model.__surql_table_name__ is TABLE, "table name mismatch expecting %s got %s" % (TABLE, model.__surql_table_name__)
        assert len(schema.fields) == 10, f"error field count mismatch expecting 10 got {len(schema.fields)}"

        # check base person
        self.check_base_person(schema, TABLE)

        # check classmates
        self.check_field(f"{TABLE}.classmates", schema.fields[9], [SurQLType.ARRAY, SurQLType.OPTIONAL])
        self.check_field(f"{TABLE}.classmates.*", schema.fields[9].definitions[0], [SurQLType.OBJECT])
        self.check_base_person(schema.fields[9].definitions[0].definitions[0], f"{TABLE}.classmates.*")