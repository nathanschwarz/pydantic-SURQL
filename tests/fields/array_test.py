from datetime import datetime
from typing import Any, Optional
from pydantic_surql.parsers import parseField
from pydantic_surql.types import SurQLNullable, SurQLAnyRecord, SurQLType

class TestSimpleArrayFields:
    def test_str(self):
        """
            test array<string> type parsing
        """
        field = parseField("test", list[str])
        assert field.types == [[SurQLType.STRING]]
        assert field.name is "test"
        assert field.recordLink is None

    def test_float(self):
        """
            test array<float> type parsing
        """
        field = parseField("test", list[float])
        assert field.types == [[SurQLType.NUMBER]]
        assert field.name is "test"
        assert field.recordLink is None

    def test_int(self):
        """
            test array<int> type parsing
        """
        field = parseField("test", list[int])
        assert field.types == [[SurQLType.NUMBER]]
        assert field.name is "test"
        assert field.recordLink is None

    def test_bool(self):
        """
            test array<bool> type parsing
        """
        field = parseField("test", list[bool])
        assert field.types == [[SurQLType.BOOLEAN]]
        assert field.name is "test"
        assert field.recordLink is None

    def test_date(self):
        """
            test array<date> type parsing
        """
        field = parseField("test", list[datetime])
        assert field.types == [[SurQLType.DATE]]
        assert field.name is "test"
        assert field.recordLink is None

    def test_nullable(self):
        """
            test array<nullable> type parsing
        """
        field = parseField("test", list[SurQLNullable])
        assert field.types == [[SurQLType.NULL]]
        assert field.name is "test"
        assert field.recordLink is None

    def test_optional(self):
        """
            test array<optional> type parsing
        """
        field = parseField("test", Optional[list[str]])
        assert field.types == [[SurQLType.STRING], SurQLType.OPTIONAL]
        assert field.name is "test"
        assert field.recordLink is None

    def test_optional_nullable(self):
        """
            test array<optional> nullable type parsing
        """
        field = parseField("test", Optional[list[str | SurQLNullable]])
        assert field.types == [[SurQLType.STRING, SurQLType.NULL], SurQLType.OPTIONAL]
        assert field.name is "test"
        assert field.recordLink is None

    def test_any(self):
        """
            test array<any> type parsing
        """
        field = parseField("test", list[Any])
        assert field.types == [[SurQLType.ANY]]
        assert field.name is "test"
        assert field.recordLink is None

    def test_dict(self):
        """
            test array<dict> type parsing
        """
        field = parseField("test", list[dict])
        assert field.types == [[SurQLType.DICT]]
        assert field.name is "test"
        assert field.recordLink is None

    def test_multi(self):
        """
            test array<str | int | float | bool | datetime | dict> type parsing
        """
        field = parseField("test", list[str | int | float | bool | datetime | dict])
        assert field.types == [[SurQLType.STRING, SurQLType.NUMBER,  SurQLType.NUMBER, SurQLType.BOOLEAN, SurQLType.DATE, SurQLType.DICT]]
        assert field.name is "test"
        assert field.recordLink is None

    def test_any_record(self):
        """
            test array<SurQLAnyRecord> type parsing
        """
        field = parseField("test", list[SurQLAnyRecord])
        assert field.types == [[SurQLType.ANY_RECORD]]
        assert field.name is "test"
        assert field.recordLink is None