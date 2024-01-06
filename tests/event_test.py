from pydantic_surql.types import SurQLEvent


T_NAME = "test_table"

class TestSurQLEvent:
    """
        Test SurQLEvent SDL generation and parsing
    """
    def test_event(self):
        event = SurQLEvent(name="test", whenSDL=["1==1"], querySDL="1==1")
        assert event.SDL(T_NAME) == "DEFINE EVENT test ON TABLE %s WHEN 1==1 THEN (1==1);" % T_NAME

    def test_event_with_multiple_when(self):
        event = SurQLEvent(name="test", whenSDL=["1==1", "2==2"], querySDL="1==1")
        assert event.SDL(T_NAME) == "DEFINE EVENT test ON TABLE %s WHEN 1==1 OR 2==2 THEN (1==1);" % T_NAME

    def test_event_with_multiple_query(self):
        event = SurQLEvent(name="test", whenSDL=["1==1"], querySDL=["1==1;", "2==2;"])
        assert event.SDL(T_NAME) == "DEFINE EVENT test ON TABLE %s WHEN 1==1 THEN {\n1==1;\n2==2;\n};" % T_NAME