from datetime import datetime
from typing import Any, Optional
from pydantic_surql.parsers import parseField
from pydantic_surql.types import SurQLNullable, SurQLAnyRecord, SurQLType

class TestSimpleArrayField:
    def test_str(self):
        """
            test string type parsing
        """
        field = parseField("test", str)
        assert set(field.types) == set([SurQLType.STRING])
        assert field.name is "test"
        assert field.recordLink is None

    def test_float(self):
        """
            test float type parsing
        """
        field = parseField("test", float)
        assert set(field.types) == set([SurQLType.NUMBER])
        assert field.name is "test"
        assert field.recordLink is None

    def test_int(self):
        """
            test int type parsing
        """
        field = parseField("test", int)
        assert set(field.types) == set([SurQLType.NUMBER])
        assert field.name is "test"
        assert field.recordLink is None

    def test_bool(self):
        """
            test bool type parsing
        """
        field = parseField("test", bool)
        assert set(field.types) == set([SurQLType.BOOLEAN])
        assert field.name is "test"
        assert field.recordLink is None

    def test_date(self):
        """
            test date type parsing
        """
        field = parseField("test", datetime)
        assert set(field.types) == set([SurQLType.DATE])
        assert field.name is "test"
        assert field.recordLink is None

    def test_nullable(self):
        """
            test nullable type parsing
        """
        field = parseField("test", SurQLNullable)
        assert set(field.types) == set([SurQLType.NULL])
        assert field.name is "test"
        assert field.recordLink is None

    def test_optional(self):
        """
            test optional type parsing
        """
        field = parseField("test", Optional[str])
        assert set(field.types) == set([SurQLType.OPTIONAL, SurQLType.STRING])
        assert field.name is "test"
        assert field.recordLink is None

    def test_optional_nullable(self):
        """
            test optional nullable type parsing
        """
        field = parseField("test", Optional[str | SurQLNullable])
        assert set(field.types) == set([SurQLType.OPTIONAL, SurQLType.NULL, SurQLType.STRING])
        assert field.name is "test"
        assert field.recordLink is None

    def test_any(self):
        """
            test any type parsing
        """
        field = parseField("test", Any)
        assert set(field.types) == set([SurQLType.ANY])
        assert field.name is "test"
        assert field.recordLink is None

    def test_dict(self):
        """
            test dict type parsing
        """
        field = parseField("test", dict)
        assert set(field.types) == set([SurQLType.DICT])
        assert field.name is "test"
        assert field.recordLink is None

    def test_multi(self):
        """
            test multi type parsing
        """
        field = parseField("test", str | int | float | bool | datetime | dict)
        assert set(field.types) == set([SurQLType.STRING, SurQLType.NUMBER, SurQLType.BOOLEAN, SurQLType.DATE, SurQLType.DICT])
        assert field.name is "test"
        assert field.recordLink is None

    def test_any_record(self):
        """
            test SurQLAnyRecord type parsing
        """
        field = parseField("test", SurQLAnyRecord)
        assert set(field.types) == set([SurQLType.ANY_RECORD])
        assert field.name is "test"
        assert field.recordLink is None