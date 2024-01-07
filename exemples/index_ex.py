from pydantic_surql import surql_collection, Metadata
from pydantic import BaseModel, ConfigDict
from pydantic_surql.types import (
  SurQLTableConfig,
  SurQLIndex,
  SurQLUniqueIndex,
  SurQLSearchIndex,
  SurQLAnalyzer,
  SurQLTokenizers
)

index = SurQLIndex(name="index_name", fields=["field1", "field2"])
unique_index = SurQLUniqueIndex(name="unique_index_name", fields=["field1", "field2"])
analyzer = SurQLAnalyzer(name="analyzer_name", tokenizers=[SurQLTokenizers.BLANK])
search_index = SurQLSearchIndex(
  name="search_index_name",
  fields=["field3"],
  analyzer=analyzer,
  highlights=True
)

@surql_collection("indexed_collection", SurQLTableConfig(indexes=[index, unique_index, search_index]))
class IndexedCollection(BaseModel):
    field1: str
    field2: str
    field3: str

print(Metadata.collect())