from datetime import datetime
from typing import Any, Optional, Type, get_args

from pydantic_surql.parser import SurQLParser
from pydantic_surql.types import SchemaField
from pydantic_surql.types import SurQLNullable, SurQLAnyRecord, SurQLType
from pydantic_surql.types.utils import is_union

Parser = SurQLParser()
F_NAME = "test"
T_NAME = "test_table"

class TestSimpleArrayFields:
    def tree_check(self, field: SchemaField, types: list[SurQLType], inherantType: SurQLType, optional: bool = False):
        """
            common test for type parsing
        """
        assert field.name is F_NAME
        if (optional):
            assert field.isOptional, f"error optional mismatch expecting {optional} got {field.isOptional}"
            assert len(field.metas) == 2, f"error optional field should have only one type got {len(field.metas)}"
            for t in [meta.type for meta in field.metas]:
                assert t in [SurQLType.ARRAY, SurQLType.OPTIONAL], f"error expecting array or optional got {t}"
        else:
            assert len(field.metas) == 1, f"error field should have only one type got {len(field.metas)}"
            assert not field.isOptional, f"error optional mismatch expecting {optional} got {field.isOptional}"
            assert field.metas[0].type == SurQLType.ARRAY, f"error expecting array got {field.metas[0].type}"
        for i, meta in enumerate(field.metas):
            assert meta.type == types[i], f"error type mismatch expecting {types[i]} got {meta.type}"
            if (meta.hasDefinition):
                definition = field.definitions[i]
                assert definition.name == f"{F_NAME}.*", f"error definition name mismatch expecting {F_NAME}.* got {definition.name}"
                assert definition.metas[0].type == inherantType, f"error definition type mismatch expecting {inherantType} got {definition.metas[0].type}"
            else:
                assert field.definitions[i] == None, f"error definition should be None got {field.definitions[i]}"


    def common_check(self, _type: Type, surql_type: SurQLType, optional: bool = False):
        """
            common test for array<type> type parsing and SDL generation
        """
        __type = Optional[list[_type]] if optional else list[_type]
        field = SchemaField.from_type(F_NAME, __type, Parser.cache)
        self.tree_check(field, [[surql_type]], surql_type, optional)
        assert field.sdl == "\n".join([
            "DEFINE FIELD %s ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "option<array>" if optional else "array"),
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
            test option<array<str>> type parsing and SDL generation
        """
        self.common_check(str, SurQLType.STRING, True)

    def test_optional_nullable(self):
        """
            test option<array<str | null>> nullable type parsing and SDL generation
        """
        field = Parser.from_field(F_NAME, Optional[list[str | SurQLNullable]])
        self.simple_field_check(field, [[SurQLType.STRING, SurQLType.NULL]], True)
        assert field.SDL(T_NAME) == "\n".join([
            "DEFINE FIELD %s ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "option<array>"),
            "DEFINE FIELD %s.* ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "string|null"),
        ])

    def test_multi(self):
        """
            test array<str | int | float | bool | datetime> type parsing and SDL generation
        """
        field = Parser.from_field(F_NAME, list[str | int | float | bool | datetime])
        common_types = [[SurQLType.STRING, SurQLType.NUMBER, SurQLType.NUMBER, SurQLType.BOOLEAN, SurQLType.DATE]]
        SDL_types = [SurQLType.STRING.value, SurQLType.NUMBER.value, SurQLType.NUMBER.value, SurQLType.BOOLEAN.value, SurQLType.DATE.value]
        self.simple_field_check(field, common_types)
        assert field.SDL(T_NAME) == "\n".join([
            "DEFINE FIELD %s ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "array"),
            "DEFINE FIELD %s.* ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "|".join(SDL_types)),
        ])

    def test_nested(self):
        """
            test array<array<str>> type parsing
        """
        field = Parser.from_field(F_NAME, list[list[str]])
        self.simple_field_check(field, [[[SurQLType.STRING]]])
        assert field.SDL(T_NAME) == "\n".join([
            "DEFINE FIELD %s ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "array"),
            "DEFINE FIELD %s.* ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "array"),
            "DEFINE FIELD %s.*.* ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "string"),
        ])

    def test_nested_nested(self):
        """
            test array<array<array<str>>> type parsing
        """
        field = Parser.from_field(F_NAME, list[list[list[str]]])
        self.simple_field_check(field, [[[[SurQLType.STRING]]]])
        assert field.SDL(T_NAME) == "\n".join([
            "DEFINE FIELD %s ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "array"),
            "DEFINE FIELD %s.* ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "array"),
            "DEFINE FIELD %s.*.* ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "array"),
            "DEFINE FIELD %s.*.*.* ON TABLE %s TYPE %s;" % (F_NAME, T_NAME, "string"),
        ])

