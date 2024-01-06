from pydantic import BaseModel
from .parser import SurQLParser
from .types import SurQLTable, SurQLMapper, SurQLTableConfig

Parser = SurQLParser()
Mapper = SurQLMapper(tables=[])

def surql_collection(name: str, config: SurQLTableConfig = SurQLTableConfig()):
    """
        A simple decorator to convert a pydantic model to a surQL SDL table definition
    """
    def inner(model: BaseModel):
        table = Parser.from_model(name, model, config)
        Mapper.tables.add(table)
        return model
    return inner