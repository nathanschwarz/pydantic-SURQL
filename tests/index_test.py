from pydantic_surql import SurQLParser
from pydantic_surql.types import SurQLIndex, SurQLAnalyzer, SurQLTokenizers, SurQLUniqueIndex, SurQLSearchIndex

Parser = SurQLParser()

class TestIndexes:
    def test_simple_index(self):
        index = SurQLIndex(name="test_index", fields=["name", "age"])
        assert index.SDL("test_table") == "DEFINE INDEX test_index ON TABLE test_table FIELDS name,age;"

    def test_unique_index(self):
        index = SurQLUniqueIndex(name="test_index", fields=["name", "age"])
        assert index.SDL("test_table") == "DEFINE INDEX test_index ON TABLE test_table FIELDS name,age UNIQUE;"

    def test_good_analyzers_filters(self):
        try:
            analyzer = SurQLAnalyzer(name="test_analyzer", tokenizers=[SurQLTokenizers.BLANK], filters=["lowercase", "ascii", "uppercase", "edgengram(1,2)"])
        except Exception as e:
            assert False, e
        return True


    # def test_search_index():
    #     index = SurQLSearchIndex(name="test_index", fields=["name", "age"], analyzer=SurQLAnalyzer(name="test_analyzer", tokenizers=["unicode"], filters=["lowercase"]))
    #     assert index.SDL("test_table") == "DEFINE INDEX test_index FIELDS name,age ANALYZER test_analyzer;"