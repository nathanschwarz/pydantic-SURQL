from .parsers import parseFields
from .types import SchemaType, SurQLTable, SurQLMapper

Mapper = SurQLMapper(tables=[])

def toSurql(name: str):
    """
    Convert a pydantic model to a surQL query
    """
    def inner(model: SchemaType):
        table = SurQLTable(name=name, fields=parseFields(model))
        Mapper.tables.add(table)
    return inner