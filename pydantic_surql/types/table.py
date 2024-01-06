from typing import Set
from pydantic import BaseModel, Field, field_validator
from .field import SurQLField

class SurQLIndex(BaseModel):
    """
        A pydantic SurQL index definition
        TODO: implement search indexes
    """
    name: str
    fields: list[str]
    unique: bool = False

    def SDL(self, table_name: str) -> str:
        """
            return a SDL index definition
        """
        _def = [
            "DEFINE INDEX",
            self.name,
            "ON TABLE",
            table_name,
            "UNIQUE" if self.unique else None,
            "FIELDS",
            f"{','.join(self.fields)}",
        ]
        return " ".join([e for e in _def if e is not None]) + ';'

    __hash__ = object.__hash__

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

    @field_validator("indexes")
    def indexes_validator(cls, v):
        """
            validate indexes
        """
        assert len(v) == len(set([index.name for index in v])), "indexes names must be unique"
        return v


class SurQLTable(BaseModel):
    """
        A pydantic SurQL table definition
    """
    name: str
    fields: list[SurQLField]
    config: SurQLTableConfig = SurQLTableConfig()

    def _table_def(self):
        """return a SDL schemafull table definition"""
        _def = [
            "DEFINE TABLE",
            self.name,
        ]
        if (self.config.asView is not None):
            _def += [self.config.asView.SDL()]
        else:
            _def += [
                "DROP" if self.config.drop else None,
                "SCHEMAFULL" if self.config.strict else "SCHEMALESS",
                f"CHANGEFEED {self.config.changeFeed}" if self.config.changeFeed is not None else None,
            ]
            _def = [e for e in _def if e is not None]
        return " ".join(_def) + ';'

    def SDL(self):
        """return a SDL table definition with all the fields SDL definitions"""
        res = [self._table_def()]
        if (self.config.asView is None):
            for field in self.fields:
                res.append(field.SDL(self.name))
            for index in self.config.indexes:
                res.append(index.SDL(self.name))
        return "\n".join(res)

class SurQLMapper(BaseModel):
    """
        A simple mapper to store all the SurQL tables definitions generated from pydantic models
    """
    tables: Set[SurQLTable]
    __hash__ = object.__hash__