from pydantic import BaseModel
from .parser import SurQLParser
from .types import SurQLTable, SurQLMetadata, SurQLTableConfig

Parser = SurQLParser()
Metadata = SurQLMetadata()

def surql_collection(name: str, config: SurQLTableConfig = SurQLTableConfig()):
    """
        A simple decorator to convert a pydantic model to a surQL SDL table definition
    """
    def inner(model: BaseModel):
        table = Parser.from_model(name, model, config)
        Metadata.tables += [table]
        for index in table.config.indexes:
            if hasattr(index, "analyzer") and index.analyzer is not None:
                exist = any([a.name == index.analyzer.name for a in Metadata.analyzers])
                if not exist:
                    Metadata.analyzers += [index.analyzer]
        return model
    return inner