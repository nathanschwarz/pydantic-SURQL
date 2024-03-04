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
    metadata: SurQLAnyRecord | None
    extra: Any | None

class SimpleTestObject(BasePerson):
    """
        Simple test object
    """
    classmates: list[BasePerson] | None

TABLE = "test_table"
model = Parser.from_model(TABLE, SimpleTestObject)

class TestSDL(Base):
    """
        test unit for :
            - fields types
            - schema tree generation
            - field sdl generation
    """
    def test_str(self, schema: Schema = model.surql_schema, path: str = TABLE):
        """
            Test string field
        """
        field = schema.fields[0]
        Base.check_field(f"{path}.name", field, [SurQLType.STRING])
        Base.check_field_sdl(field, f"DEFINE FIELD {field.field_path} ON TABLE {field.table} TYPE string;")

    def test_int(self, schema: Schema = model.surql_schema, path: str = TABLE):
        """
            Test int field
        """
        field = schema.fields[1]
        Base.check_field(f"{path}.age", field, [SurQLType.NUMBER])
        Base.check_field_sdl(field, f"DEFINE FIELD {field.field_path} ON TABLE {field.table} TYPE number;")

    def test_float(self, schema: Schema = model.surql_schema, path: str = TABLE):
        """
            Test float field
        """
        field = schema.fields[2]
        Base.check_field(f"{path}.weight", field, [SurQLType.NUMBER])
        Base.check_field_sdl(field, f"DEFINE FIELD {field.field_path} ON TABLE {field.table} TYPE number;")

    def test_bool(self, schema: Schema = model.surql_schema, path: str = TABLE):
        """
            Test bool field
        """
        field = schema.fields[3]
        Base.check_field(f"{path}.is_active", field, [SurQLType.BOOLEAN])
        Base.check_field_sdl(field, f"DEFINE FIELD {field.field_path} ON TABLE {field.table} TYPE bool;")

    def test_date(self, schema: Schema = model.surql_schema, path: str = TABLE):
        """
            Test date field
        """
        field = schema.fields[4]
        Base.check_field(f"{path}.birthday", field, [SurQLType.DATE])
        Base.check_field_sdl(field, f"DEFINE FIELD {field.field_path} ON TABLE {field.table} TYPE datetime;")

    def test_optional(self, schema: Schema = model.surql_schema, path: str = TABLE):
        """
            Test optional field
        """
        field = schema.fields[5]
        Base.check_field(f"{path}.nickname", field, [SurQLType.STRING, SurQLType.OPTIONAL])
        Base.check_field_sdl(field, f"DEFINE FIELD {field.field_path} ON TABLE {field.table} TYPE option<string>;")

    def test_set(self, schema: Schema = model.surql_schema, path: str = TABLE):
        """
            Test set field
        """
        field = schema.fields[6]
        Base.check_field(f"{path}.tags", field, [SurQLType.SET, SurQLType.OPTIONAL])
        Base.check_field(f"{path}.tags.*", field.definitions[0], [SurQLType.STRING])
        Base.check_field_sdl(field, f"DEFINE FIELD {field.field_path} ON TABLE {field.table} TYPE option<set<string>>;")

    def test_array(self, schema: Schema = model.surql_schema, path: str = TABLE):
        """
            Test array field
        """
        field = schema.fields[7]
        Base.check_field(f"{path}.grades", field, [SurQLType.ARRAY, SurQLType.OPTIONAL])
        Base.check_field(f"{path}.grades.*", field.definitions[0], [SurQLType.NUMBER])
        Base.check_field_sdl(field, f"DEFINE FIELD {field.field_path} ON TABLE {field.table} TYPE option<array<number>>;")

    def test_array_nullable(self, schema: Schema = model.surql_schema, path: str = TABLE):
        """
            Test array nullable field
        """
        field = schema.fields[8]
        Base.check_field(f"{path}.links", field, [SurQLType.ARRAY, SurQLType.OPTIONAL])
        Base.check_field(f"{path}.links.*", field.definitions[0], [SurQLType.STRING, SurQLType.NULL])
        Base.check_field_sdl(field, f"DEFINE FIELD {field.field_path} ON TABLE {field.table} TYPE option<array<string|null>>;")

    def test_enum(self, schema: Schema = model.surql_schema, path: str = TABLE):
        """
            Test enum field
            TODO: check assertions when re-implemented
        """
        field = schema.fields[9]
        Base.check_field(f"{path}.group", field, [SurQLType.ENUM])
        Base.check_field_sdl(field, f"DEFINE FIELD {field.field_path} ON TABLE {field.table} TYPE string|number;")

    def test_record(self, schema: Schema = model.surql_schema, path: str = TABLE):
        """
            Test record field
        """
        field = schema.fields[10]
        Base.check_field(f"{path}.known_addresses", field, [SurQLType.ARRAY, SurQLType.OPTIONAL])
        Base.check_field(f"{path}.known_addresses.*", field.definitions[0], [SurQLType.RECORD])
        Base.check_record(f"{path}.known_addresses.*", field.definitions[0], Address)
        Base.check_field_sdl(field, f"DEFINE FIELD {field.field_path} ON TABLE {field.table} TYPE option<array<record<address>>>;")

    def test_any_record(self, schema: Schema = model.surql_schema, path: str = TABLE):
        """
            Test any record field
        """
        field = schema.fields[11]
        Base.check_field(f"{path}.metadata", field, [SurQLType.ANY_RECORD, SurQLType.OPTIONAL])
        Base.check_field_sdl(field, f"DEFINE FIELD {field.field_path} ON TABLE {field.table} TYPE option<record()>;")

    def test_any(self, schema: Schema = model.surql_schema, path: str = TABLE):
        """
            Test any field
        """
        field = schema.fields[12]
        Base.check_field(f"{path}.extra", field, [SurQLType.ANY, SurQLType.OPTIONAL])
        Base.check_field_sdl(field, f"DEFINE FIELD {field.field_path} ON TABLE {field.table} TYPE option<any>;")

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

    def test_object(self, schema: Schema = model.surql_schema, path: str = TABLE):
        """
            Test object field
        """
        field = schema.fields[13]
        Base.check_field(f"{path}.classmates", field, [SurQLType.ARRAY, SurQLType.OPTIONAL])
        Base.check_field(f"{path}.classmates.*", field.definitions[0], [SurQLType.OBJECT])
        self.check_base_person(field.definitions[0].definitions[0], f"{path}.classmates.*")

    def test_schema(self):
        """
            Test simple fields
        """
        schema = model.surql_schema
        assert model.surql_table_name is TABLE, "table name mismatch expecting %s got %s" % (TABLE, model.surql_table_name)
        assert len(schema.fields) == 14, f"error field count mismatch expecting 14 got {len(schema.fields)}"