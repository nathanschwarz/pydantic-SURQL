from enum import Enum
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel
from pydantic_surql import surql_collection
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

@surql_collection("address")
class Address(BaseModel):
    """
    a simple record exemple
    """
    street: str
    city: str
    zip: int

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
    group: EnumData
    known_addresses: list[Address] | None


class SimpleTestObject(BasePerson):
    """
        Simple test object
    """
    classmates: list[BasePerson] | None

TABLE = "test_table"
model = Parser.from_model(TABLE, SimpleTestObject)

class TestSDL(Base):
    """
        Test fields types and sdl generation.
    """
    def test_str(self, schema: Schema = model.__surql_schema__, path: str = TABLE):
        """
            Test string field
        """
        Base.check_field(f"{path}.name", schema.fields[0], [SurQLType.STRING])

    def test_int(self, schema: Schema = model.__surql_schema__, path: str = TABLE):
        """
            Test int field
        """
        Base.check_field(f"{path}.age", schema.fields[1], [SurQLType.NUMBER])

    def test_float(self, schema: Schema = model.__surql_schema__, path: str = TABLE):
        """
            Test float field
        """
        Base.check_field(f"{path}.weight", schema.fields[2], [SurQLType.NUMBER])

    def test_bool(self, schema: Schema = model.__surql_schema__, path: str = TABLE):
        """
            Test bool field
        """
        Base.check_field(f"{path}.is_active", schema.fields[3], [SurQLType.BOOLEAN])

    def test_date(self, schema: Schema = model.__surql_schema__, path: str = TABLE):
        """
            Test date field
        """
        Base.check_field(f"{path}.birthday", schema.fields[4], [SurQLType.DATE])

    def test_optional(self, schema: Schema = model.__surql_schema__, path: str = TABLE):
        """
            Test optional field
        """
        Base.check_field(f"{path}.nickname", schema.fields[5], [SurQLType.STRING, SurQLType.OPTIONAL])

    def test_set(self, schema: Schema = model.__surql_schema__, path: str = TABLE):
        """
            Test set field
        """
        Base.check_field(f"{path}.tags", schema.fields[6], [SurQLType.SET, SurQLType.OPTIONAL])
        Base.check_field(f"{path}.tags.*", schema.fields[6].definitions[0], [SurQLType.STRING])

    def test_array(self, schema: Schema = model.__surql_schema__, path: str = TABLE):
        """
            Test array field
        """
        Base.check_field(f"{path}.grades", schema.fields[7], [SurQLType.ARRAY, SurQLType.OPTIONAL])
        Base.check_field(f"{path}.grades.*", schema.fields[7].definitions[0], [SurQLType.NUMBER])

    def test_array_nullable(self, schema: Schema = model.__surql_schema__, path: str = TABLE):
        """
            Test array nullable field
        """
        Base.check_field(f"{path}.links", schema.fields[8], [SurQLType.ARRAY, SurQLType.OPTIONAL])
        Base.check_field(f"{path}.links.*", schema.fields[8].definitions[0], [SurQLType.STRING, SurQLType.NULL])

    def test_enum(self, schema: Schema = model.__surql_schema__, path: str = TABLE):
        """
            Test enum field
        """
        Base.check_field(f"{path}.group", schema.fields[9], [SurQLType.ENUM])

    def test_record(self, schema: Schema = model.__surql_schema__, path: str = TABLE):
        """
            Test record field
        """
        Base.check_field(f"{path}.known_addresses", schema.fields[10], [SurQLType.ARRAY, SurQLType.OPTIONAL])
        Base.check_field(f"{path}.known_addresses.*", schema.fields[10].definitions[0], [SurQLType.RECORD])
        Base.check_record(f"{path}.known_addresses.*", schema.fields[10].definitions[0], Address)

    def check_base_person(self, schema: Schema, path: str):
        """
            Check base person fields
        """
        self.test_str(schema, path)
        self.test_int(schema, path)
        self.test_float(schema, path)
        self.test_bool(schema, path)
        self.test_date(schema, path)
        self.test_optional(schema, path)
        self.test_set(schema, path)
        self.test_array(schema, path)
        self.test_array_nullable(schema, path)
        self.test_enum(schema, path)
        self.test_record(schema, path)

    def test_schema(self):
        """
            Test simple fields
        """
        schema = model.__surql_schema__
        assert model.__surql_table_name__ is TABLE, "table name mismatch expecting %s got %s" % (TABLE, model.__surql_table_name__)
        assert len(schema.fields) == 12, f"error field count mismatch expecting 12 got {len(schema.fields)}"

        # check classmates
        Base.check_field(f"{TABLE}.classmates", schema.fields[11], [SurQLType.ARRAY, SurQLType.OPTIONAL])
        Base.check_field(f"{TABLE}.classmates.*", schema.fields[11].definitions[0], [SurQLType.OBJECT])
        self.check_base_person(schema.fields[11].definitions[0].definitions[0], f"{TABLE}.classmates.*")