from typing import overload
from pydantic import BaseModel

from .parser import SurQLParser
from .types import SurQLTableConfig, SurQLMetadata, SurQLTable

Parser = SurQLParser()
Metadata = SurQLMetadata()

@overload
def surql_collection(name: str, config: dict = {}):
    _config = SurQLTableConfig.model_validate(config)
    return surql_collection(name, _config)

def surql_collection(name: str, config: SurQLTableConfig = SurQLTableConfig()):
    """
        A simple decorator to convert a pydantic model to a surQL SDL table definition
    """
    def inner(model: BaseModel):
        schema = Parser.from_model(name, model, config)
        table = SurQLTable(model=schema)
        Metadata.tables.append(table)
        return schema
    return inner
