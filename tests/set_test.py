from datetime import datetime
from typing import Any, Optional, Type

from pydantic_surql.parser import SurQLParser
from pydantic_surql.types import SurQLField, SurQLNullable, SurQLAnyRecord, SurQLType

Parser = SurQLParser()
F_NAME = "test"
T_NAME = "test_table"

class TestSimplesetFields:
    def simple_field_check(self, field: SurQLField, types: list[SurQLType], optional: bool = False):
        """
            common test for type parsing
        """
        if (optional):
            assert field.types == [*types, SurQLType.OPTIONAL]
        else:
            assert field.types == types
        assert field.name is F_NAME
        assert field.recordLink is None

    def common_check(self, _type: Type, surql_type: SurQLType, optional: bool = False):
        """
            common test for set<type> type parsing and SDL generation
        """
        __type = Optional[set[_type]] if optional else set[_type]
        field = Parser.from_field(F_NAME, __type)
        self.simple_field_check(field, [[SurQLType.SET, [surql_type]]], optional)
        assert field.SDL(T_NAME) == "\n".join([
            "DEFINE FIELD %s ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "optional<set>" if optional else "set"),
            "DEFINE FIELD %s.* ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, surql_type.value)
        ])

    def test_str(self):
        """
            test set<string> type parsing and SDL generation
        """
        self.common_check(str, SurQLType.STRING)

    def test_float(self):
        """
            test set<float> type parsing and SDL generation
        """
        self.common_check(float, SurQLType.NUMBER)

    def test_int(self):
        """
            test set<int> type parsing and SDL generation
        """
        self.common_check(int, SurQLType.NUMBER)

    def test_bool(self):
        """
            test set<bool> type parsing and SDL generation
        """
        self.common_check(bool, SurQLType.BOOLEAN)

    def test_date(self):
        """
            test set<date> type parsing and SDL generation
        """
        self.common_check(datetime, SurQLType.DATE)

    def test_nullable(self):
        """
            test set<nullable> type parsing and SDL generation
        """
        self.common_check(SurQLNullable, SurQLType.NULL)


    def test_any(self):
        """
            test set<any> type parsing and SDL generation
        """
        self.common_check(Any, SurQLType.ANY)

    def test_any_record(self):
        """
            test set<SurQLAnyRecord> type parsing and SDL generation
        """
        self.common_check(SurQLAnyRecord, SurQLType.ANY_RECORD)

    def test_optional(self):
        """
            test optional<set<str>> type parsing and SDL generation
        """
        self.common_check(str, SurQLType.STRING, True)

    def test_optional_nullable(self):
        """
            test optional<set<str | null>> nullable type parsing and SDL generation
        """
        field = Parser.from_field(F_NAME, Optional[set[str | SurQLNullable]])
        self.simple_field_check(field, [[SurQLType.SET, [SurQLType.STRING, SurQLType.NULL]]], True)
        assert field.SDL(T_NAME) == "\n".join([
            "DEFINE FIELD %s ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "optional<set>"),
            "DEFINE FIELD %s.* ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "string|null"),
        ])

    def test_multi(self):
        """
            test set<str | int | float | bool | datetime> type parsing and SDL generation
        """
        field = Parser.from_field(F_NAME, set[str | int | float | bool | datetime])
        common_types = [[SurQLType.SET, [SurQLType.STRING, SurQLType.NUMBER, SurQLType.NUMBER, SurQLType.BOOLEAN, SurQLType.DATE]]]
        SDL_types = [SurQLType.STRING.value, SurQLType.NUMBER.value, SurQLType.NUMBER.value, SurQLType.BOOLEAN.value, SurQLType.DATE.value]
        self.simple_field_check(field, common_types)
        assert field.SDL(T_NAME) == "\n".join([
            "DEFINE FIELD %s ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "set"),
            "DEFINE FIELD %s.* ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "|".join(SDL_types)),
        ])

    def test_nested(self):
        """
            test set<set<str>> type parsing
        """
        field = Parser.from_field(F_NAME, set[set[str]])
        self.simple_field_check(field, [[SurQLType.SET, [[SurQLType.SET, [SurQLType.STRING]]]]])
        assert field.SDL(T_NAME) == "\n".join([
            "DEFINE FIELD %s ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "set"),
            "DEFINE FIELD %s.* ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "set"),
            "DEFINE FIELD %s.*.* ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "string"),
        ])

    def test_nested_nested(self):
        """
            test set<set<set<str>>> type parsing
        """
        field = Parser.from_field(F_NAME, set[set[set[str]]])
        self.simple_field_check(field, [[SurQLType.SET, [[SurQLType.SET, [[SurQLType.SET, [SurQLType.STRING]]]]]]])
        assert field.SDL(T_NAME) == "\n".join([
            "DEFINE FIELD %s ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "set"),
            "DEFINE FIELD %s.* ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "set"),
            "DEFINE FIELD %s.*.* ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "set"),
            "DEFINE FIELD %s.*.*.* ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "string"),
        ])

