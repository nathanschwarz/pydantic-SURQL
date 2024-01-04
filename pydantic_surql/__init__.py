from pydantic import BaseModel
from .parsers import parseFields
from .types import SurQLTable, SurQLMapper

Mapper = SurQLMapper(tables=[])

def toSurql(name: str):
    """
        A simple decorator to onvert a pydantic model to a surQL SDL table definition
    """
    def inner(model: BaseModel):
        model.__is_surql_collection__ = True
        model.__surql_table_name__ = name
        table = SurQLTable(name=name, fields=parseFields(model))
        Mapper.tables.add(table)
        return model
    return inner