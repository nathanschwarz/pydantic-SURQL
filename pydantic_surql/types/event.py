from enum import Enum
from pydantic import BaseModel, Field, model_validator

class SurQLEvent(BaseModel):
    """
        A pydantic SurQL event definition
    """
    name: str = Field(min_length=1)
    whenSDL: list[str] = Field(default=[], description="event when definition, if list default to OR", min_length=1)
    querySDL: list[str] = Field(default=[], min_length=1, description="event THEN definition, each item will be a single line in the query SDL")

    @model_validator('after')
    def validate_event(self):
        assert len(self.SDL) > 0, "event %s SDL definition is required" % self.name
        assert len(self.whenSDL) > 0, "event %s WHEN close required" % self.name
        return self

    def SDL(self, table_name: str):
        """
            return a SDL event definition
        """
        _def = [
            "DEFINE EVENT",
            self.name,
            "ON TABLE",
            table_name,
            "WHEN",
        ]
        + "OR ".join(self.whenSDL)
        + ["THEN"]
        if (len(self.querySDL) > 1):
            _def += ["{\n%s\n};" % "\n".join(self.querySDL)]
        else:
            _def += ["(\n%s\n);" % self.querySDL[0]]
        return " ".join(_def) + ';'