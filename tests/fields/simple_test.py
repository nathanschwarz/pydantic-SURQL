from datetime import datetime
from typing import Any, Optional
from pydantic_surql.parsers import parseField
from pydantic_surql.types import SurQLNullable, SurQLAnyRecord, SurQLType

class TestSimpleFields:
    def test_str(self):
        """
            test string type parsing
        """
        field = parseField("test", str)
        assert field.types == [SurQLType.STRING]
        assert field.name is "test"
        assert field.recordLink is None

    def test_float(self):
        """
            test float type parsing
        """
        field = parseField("test", float)
        assert field.types == [SurQLType.NUMBER]
        assert field.name is "test"
        assert field.recordLink is None

    def test_int(self):
        """
            test int type parsing
        """
        field = parseField("test", int)
        assert field.types == [SurQLType.NUMBER]
        assert field.name is "test"
        assert field.recordLink is None

    def test_bool(self):
        """
            test bool type parsing
        """
        field = parseField("test", bool)
        assert field.types == [SurQLType.BOOLEAN]
        assert field.name is "test"
        assert field.recordLink is None

    def test_date(self):
        """
            test date type parsing
        """
        field = parseField("test", datetime)
        assert field.types == [SurQLType.DATE]
        assert field.name is "test"
        assert field.recordLink is None

    def test_nullable(self):
        """
            test nullable type parsing
        """
        field = parseField("test", SurQLNullable)
        assert field.types == [SurQLType.NULL]
        assert field.name is "test"
        assert field.recordLink is None

    def test_optional(self):
        """
            test optional type parsing
        """
        field = parseField("test", Optional[str])
        assert field.types == [SurQLType.STRING, SurQLType.OPTIONAL]
        assert field.name is "test"
        assert field.recordLink is None

    def test_optional_nullable(self):
        """
            test optional nullable type parsing
        """
        field = parseField("test", Optional[str | SurQLNullable])
        assert field.types == [SurQLType.STRING, SurQLType.NULL, SurQLType.OPTIONAL]
        assert field.name is "test"
        assert field.recordLink is None

    def test_any(self):
        """
            test any type parsing
        """
        field = parseField("test", Any)
        assert field.types == [SurQLType.ANY]
        assert field.name is "test"
        assert field.recordLink is None

    def test_dict(self):
        """
            test dict type parsing
        """
        field = parseField("test", dict)
        assert field.types == [SurQLType.DICT]
        assert field.name is "test"
        assert field.recordLink is None

    def test_multi(self):
        """
            test multi type parsing
        """
        field = parseField("test", str | int | float | bool | datetime | dict)
        assert field.types == [SurQLType.STRING, SurQLType.NUMBER, SurQLType.NUMBER, SurQLType.BOOLEAN, SurQLType.DATE, SurQLType.DICT]
        assert field.name is "test"
        assert field.recordLink is None

    def test_any_record(self):
        """
            test SurQLAnyRecord type parsing
        """
        field = parseField("test", SurQLAnyRecord)
        assert field.types == [SurQLType.ANY_RECORD]
        assert field.name is "test"
        assert field.recordLink is None

    def test_nested(self):
        """
            test nested type parsing
        """
        field = parseField("test", list[list[str]])
        assert field.types == [[[SurQLType.STRING]]]
        assert field.name is "test"
        assert field.recordLink is None

    def test_nested_nested(self):
        """
            test nested nested type parsing
        """
        field = parseField("test", list[list[list[str]]])
        assert field.types == [[[[SurQLType.STRING]]]]
        assert field.name is "test"
        assert field.recordLink is None