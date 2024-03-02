from pydantic import BaseModel, Field, field_validator
from pydantic_surql.types.event import SurQLEvent
from pydantic_surql.types.indexes import SurQLIndex
from pydantic_surql.types.permissions import SurQLPermissions


class SurQLView(BaseModel):
    """
        A pydantic SurQL view query definition
    """
    select: list[str] = Field(default=["*"], min_length=1)
    from_t: list[str] = Field(min_length=1)
    where: list[str]
    group_by: list[str]

    def SDL(self) -> str:
        """
            return a SDL view definition
        """
        _def = [
            "AS SELECT",
            ','.join(self.select),
            "FROM",
            ','.join(self.from_t),
        ]
        if (len(self.where) > 0):
            _def += ["WHERE", ','.join(self.where)]
        if (len(self.group_by) > 0):
            _def += ["GROUP BY", ','.join(self.group_by)]
        return " ".join(_def)

class SurQLTableConfig(BaseModel):
    """
        A pydantic SurQL table configuration definition
        TODO: add validation for changefeed
        TODO: implement table permissions
        TODO: implement table events
    """
    asView: SurQLView | None = Field(default=None, description="view definition")
    strict: bool = Field(default=True, description="schemafull|schemaless")
    changeFeed: str | None = Field(default=None, description="changefeed definition")
    drop: bool = Field(default=False, description="set table in DROP mode")
    indexes: list[SurQLIndex] = Field(default=[], description="table indexes definitions")
    events: list[SurQLEvent] = Field(default=[], description="table events definitions")
    permissions: SurQLPermissions | None = Field(default=None, description="table permissions definitions")

    @field_validator("indexes")
    @classmethod
    def indexes_validator(cls, v: list[SurQLIndex]) -> list[SurQLIndex]:
        """
            validate indexes
        """
        assert len(v) == len(set([index.name for index in v])), "indexes names must be unique"
        return v
