from pydantic import BaseModel, Field, model_validator

class SurQLEvent(BaseModel):
    """
        A pydantic SurQL event definition
        whenSDL accepts a list of strings (will be splitted by OR) or a single line string
        querySDL accepts a list of strings to allow multiline queries (can also be a single multiline string)
        TODO: check name is not a reserved keyword
    """
    name: str = Field(min_length=1)
    whenSDL: str | list[str] = Field(default="", description="event when definition, if list default to OR")
    querySDL: str | list[str] = Field(default="", description="event THEN definition")

    @model_validator(mode='after')
    def validate_event(self):
        assert len(self.querySDL) > 0, "event %s querySDL definition is required" % self.name
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
        if (type(self.whenSDL) == str):
            _def += [self.whenSDL, "THEN"]
        else:
            _def += [" OR ".join(self.whenSDL), "THEN"]
        if (type(self.querySDL) == str):
            _def += ["(" + self.querySDL + ")"]
        else:
            _def += ["\n".join(["{", *self.querySDL, "}"])]
        return " ".join(_def) + ';'