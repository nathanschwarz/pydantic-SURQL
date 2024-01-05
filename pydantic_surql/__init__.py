from pydantic import BaseModel
from .parsers import parseFields
from .types import SurQLTable, SurQLMapper, SurQLTableConfig

Mapper = SurQLMapper(tables=[])

def model_to_surql(name: str, config: SurQLTableConfig, model: BaseModel) -> SurQLTable:
    """
        Convert a pydantic model to a SurQLTable
    """
    model.__is_surql_collection__ = True
    model.__surql_table_name__ = name
    return SurQLTable(name=name, fields=parseFields(model), config=config)

def to_surql(name: str, config: SurQLTableConfig = SurQLTableConfig()):
    """
        A simple decorator to onvert a pydantic model to a surQL SDL table definition
    """
    def inner(model: BaseModel):
        table = model_to_surql(name, config, model)
        Mapper.tables.add(table)
        return model
    return inner