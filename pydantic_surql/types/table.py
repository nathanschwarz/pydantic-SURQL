from pydantic import BaseModel, Field, field_validator

from .field import SurQLField
from .indexes import SurQLAnalyzer
from pydantic_surql.types.config import SurQLTableConfig


class SurQLTable(BaseModel):
    """
        A pydantic SurQL table definition
        TODO: check name is not a reserved keyword
    """
    name: str = Field(min_length=1)
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
        if (self.config.permissions is not None):
            _def.append(self.config.permissions.SDL())
        return " ".join(_def) + ';'

    def SDL(self):
        """return a SDL table definition with all the fields SDL definitions"""
        res = [self._table_def()]
        if (self.config.asView is None):
            for field in self.fields:
                res.append(field.SDL(self.name))
            for index in self.config.indexes:
                res.append(index.SDL(self.name))
            for event in self.config.events:
                res.append(event.SDL(self.name))
        return "\n".join(res)

class SurQLMetadata(BaseModel):
    """
        A simple mapper to store all the SurQL tables definitions generated from pydantic models through the decorator @surql_collection
    """
    tables: list[SurQLTable] = []
    analyzers: list[SurQLAnalyzer] = []

    @field_validator("tables")
    @classmethod
    def tables_validator(cls, v):
        """
            validate tables
        """
        assert len(v) == len(set([table.name for table in v])), "tables names must be unique"
        return v

    def clear(self):
        """
            clear all the tables definitions
        """
        self.tables = []
        self.analyzers = []

    def collect(self):
        """
            return a SDL string with all the tables definitions
        """
        res = []
        for analyzer in self.analyzers:
            res.append(analyzer.SDL())
        for table in self.tables:
            res.append(table.SDL())
        return "\n\n".join(res)