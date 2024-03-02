from typing import overload
from pydantic import BaseModel
from .parser import SurQLParser
from .types import SurQLTableConfig
#SurQLMetadata

Parser = SurQLParser()
#Metadata = SurQLMetadata()

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
        print(schema.model_dump(mode="json"))
        # Metadata.tables += [table]
        # for index in table.config.indexes:
        #     if hasattr(index, "analyzer") and index.analyzer is not None:
        #         exist = any([a.name == index.analyzer.name for a in Metadata.analyzers])
        #         if not exist:
        #             Metadata.analyzers += [index.analyzer]
        return model
    return inner
