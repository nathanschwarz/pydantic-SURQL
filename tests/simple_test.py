from datetime import datetime
from typing import Any, Optional
from pydantic_surql.parser import SurQLParser
from pydantic_surql.types import SurQLNullable, SurQLAnyRecord, SurQLType, SurQLField


Parser = SurQLParser()
F_NAME = "test"
T_NAME = "test_table"

class TestSimpleFields:
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

    def common_check(self, _type: type, surql_type: SurQLType, optional: bool = False):
        """
            common test for type parsing
        """
        __type = Optional[_type] if optional else _type
        field = Parser.from_field(F_NAME, __type)
        self.simple_field_check(field, [surql_type], optional)
        assert field.SDL(T_NAME) == "\n".join([
            "DEFINE FIELD %s ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, f"optional<{surql_type.value}>" if optional else surql_type.value),
        ])

    def test_str(self):
        """
            test string type parsing
        """
        self.common_check(str, SurQLType.STRING)

    def test_float(self):
        """
            test float type parsing
        """
        self.common_check(float, SurQLType.NUMBER)

    def test_int(self):
        """
            test int type parsing
        """
        self.common_check(int, SurQLType.NUMBER)

    def test_bool(self):
        """
            test bool type parsing
        """
        self.common_check(bool, SurQLType.BOOLEAN)

    def test_date(self):
        """
            test date type parsing
        """
        self.common_check(datetime, SurQLType.DATE)

    def test_nullable(self):
        """
            test nullable type parsing
        """
        self.common_check(SurQLNullable, SurQLType.NULL)

    def test_optional(self):
        """
            test optional type parsing
        """
        self.common_check(str, SurQLType.STRING, True)

    def test_optional_nullable(self):
        """
            test optional nullable type parsing
        """
        self.common_check(SurQLNullable, SurQLType.NULL, True)

    def test_any(self):
        """
            test any type parsing
        """
        self.common_check(Any, SurQLType.ANY)

    def test_any_record(self):
        """
            test SurQLAnyRecord type parsing
        """
        self.common_check(SurQLAnyRecord, SurQLType.ANY_RECORD)

    def test_dict(self):
        """
            test dict type parsing
        """
        field = Parser.from_field(F_NAME, dict)
        self.simple_field_check(field, [SurQLType.DICT])
        assert field.SDL(T_NAME) == "\n".join([
            "DEFINE FIELD %s ON TABLE %s FLEXIBLE TYPE %s;" % (F_NAME, T_NAME, "object"),
        ])

    def test_multi(self):
        """
            test multi type parsing
        """
        field = Parser.from_field(F_NAME, str | int | float | bool | datetime | dict)
        common_types = [SurQLType.STRING, SurQLType.NUMBER, SurQLType.NUMBER, SurQLType.BOOLEAN, SurQLType.DATE, SurQLType.DICT]
        SDL_types = [SurQLType.STRING.value, SurQLType.NUMBER.value, SurQLType.NUMBER.value, SurQLType.BOOLEAN.value, SurQLType.DATE.value, SurQLType.OBJECT.value]
        self.simple_field_check(field, common_types)
        assert field.SDL(T_NAME) == "\n".join([
            "DEFINE FIELD %s ON TABLE %s FLEXIBLE TYPE %s;" % (F_NAME, T_NAME, "|".join(SDL_types)),
        ])