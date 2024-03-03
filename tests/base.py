from typing import Type
from pydantic_surql.types.meta import BaseType, SchemaField
from pydantic_surql.types.utils import SurQLType

class Base:
    @staticmethod
    def check_record(name: str, field: SchemaField, model: Type[BaseType]):
        assert model.__surql_table_name__ == field.metas[0].recordLink, f"error record link mismatch expecting {model.__surql_table_name__} got {field.metas[0].recordLink} on {name}"

    def check_field(name: str, field: SchemaField, expectedTypes: list[SurQLType]):
        """
            common test for type parsing
        """
        assert field.name == name, f"error field name mismatch expecting {name} got {field.name} on {field.name}"
        assert len(field.metas) == len(expectedTypes), f"error field type count mismatch expecting {len(expectedTypes)} got {len(field.metas)} on {field.name}"
        for i, type in enumerate(field.types):
            assert type == expectedTypes[i], f"error type mismatch expecting {expectedTypes[i]} got {type} on {field.name}"

    def field(name: str, table: str, type: str, flexible: bool, optional: bool):
        """
            Generate a field definition
        """
        return "DEFINE FIELD %s ON TABLE %s %s %s%s%s;" % (
            name,
            table,
            "FLEXIBLE TYPE" if flexible else "TYPE",
            "option<" if optional else "",
            type,
            ">" if optional else "",
        )