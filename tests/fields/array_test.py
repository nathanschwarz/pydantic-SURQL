from datetime import datetime
from typing import Any, Optional, Type
from pydantic_surql.parsers import parseField
from pydantic_surql.types import SurQLNullable, SurQLAnyRecord, SurQLType

F_NAME = "test"
T_NAME = "test_table"

class TestSimpleArrayFields:
    def common_check(self, _type: Type, surql_type: SurQLType, optional: bool = False):
        """
            common test for array<type> type parsing and SDL generation
        """
        __type = Optional[list[_type]] if optional else list[_type]
        field = parseField(F_NAME, __type)
        if (optional):
            assert field.types == [[surql_type], SurQLType.OPTIONAL]
        else:
            assert field.types == [[surql_type]]
        assert field.name is F_NAME
        assert field.recordLink is None
        assert field.to_surql(T_NAME) == "\n".join([
            "DEFINE FIELD %s ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "optional<array>" if optional else "array"),
            "DEFINE FIELD %s.* ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, surql_type.value)
        ])

    def test_str(self):
        """
            test array<string> type parsing and SDL generation
        """
        self.common_check(str, SurQLType.STRING)

    def test_float(self):
        """
            test array<float> type parsing and SDL generation
        """
        self.common_check(float, SurQLType.NUMBER)

    def test_int(self):
        """
            test array<int> type parsing and SDL generation
        """
        self.common_check(int, SurQLType.NUMBER)

    def test_bool(self):
        """
            test array<bool> type parsing and SDL generation
        """
        self.common_check(bool, SurQLType.BOOLEAN)

    def test_date(self):
        """
            test array<date> type parsing and SDL generation
        """
        self.common_check(datetime, SurQLType.DATE)

    def test_nullable(self):
        """
            test array<nullable> type parsing and SDL generation
        """
        self.common_check(SurQLNullable, SurQLType.NULL)


    def test_any(self):
        """
            test array<any> type parsing and SDL generation
        """
        self.common_check(Any, SurQLType.ANY)

    def test_any_record(self):
        """
            test array<SurQLAnyRecord> type parsing and SDL generation
        """
        self.common_check(SurQLAnyRecord, SurQLType.ANY_RECORD)

    def test_optional(self):
        """
            test optional<array<str>> type parsing and SDL generation
        """
        self.common_check(str, SurQLType.STRING, True)

    def test_optional_nullable(self):
        """
            test optional<array<str | null>> nullable type parsing and SDL generation
        """
        field = parseField(F_NAME, Optional[list[str | SurQLNullable]])
        assert field.types == [[SurQLType.STRING, SurQLType.NULL], SurQLType.OPTIONAL]
        assert field.name is F_NAME
        assert field.recordLink is None

    def test_dict(self):
        """
            test array<dict> type parsing and SDL generation
        """
        field = parseField(F_NAME, list[dict])
        assert field.types == [[SurQLType.DICT]]
        assert field.name is F_NAME
        assert field.recordLink is None

    def test_multi(self):
        """
            test array<str | int | float | bool | datetime | dict> type parsing and SDL generation
        """
        field = parseField(F_NAME, list[str | int | float | bool | datetime | dict])
        assert field.types == [[SurQLType.STRING, SurQLType.NUMBER,  SurQLType.NUMBER, SurQLType.BOOLEAN, SurQLType.DATE, SurQLType.DICT]]
        assert field.name is F_NAME
        assert field.recordLink is None

    def test_nested(self):
        """
            test array<array<str>> type parsing
        """
        field = parseField("test", list[list[str]])
        assert field.types == [[[SurQLType.STRING]]]
        assert field.name is "test"
        assert field.recordLink is None

    def test_nested_nested(self):
        """
            test array<array<array<str>>> type parsing
        """
        field = parseField("test", list[list[list[str]]])
        assert field.types == [[[[SurQLType.STRING]]]]
        assert field.name is "test"
        assert field.recordLink is None
