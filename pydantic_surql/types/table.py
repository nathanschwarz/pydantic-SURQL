from typing import Type
from pydantic import BaseModel, field_validator
from pydantic_surql.types.meta import BaseType
from .indexes import SurQLAnalyzer

class SurQLTable(BaseModel):
    """
        A pydantic SurQL table definition
        TODO: check name is not a reserved keyword
    """
    model: Type[BaseType]

    @property
    def sdl(self) -> str:
        """
            Get the SDL representation of the model
        """
        _def = ["DEFINE TABLE", self.model.__surql_table_name__]
        if (self.model.__surql_config__.asView is not None):
            _def += [self.model.__surql_config__.asView.SDL()]
        else:
            _def += [
                "DROP" if self.model.__surql_config__.drop else None,
                "SCHEMAFULL" if self.model.__surql_config__.strict else "SCHEMALESS",
                f"CHANGEFEED {self.model.__surql_config__.changeFeed}" if self.model.__surql_config__.changeFeed is not None else None,
            ]
            _def = [e for e in _def if e is not None]
        if (self.model.__surql_config__.permissions is not None):
            _def.append(self.model.__surql_config__.permissions.SDL())

        sdl = [" ".join(_def) + ';', self.model.__surql_schema__.sdl]
        for index in self.model.__surql_config__.indexes:
            sdl.append(index.SDL(self.model.__surql_table_name__))
        for event in self.model.__surql_config__.events:
            sdl.append(event.SDL(self.model.__surql_table_name__))
        return "\n".join(sdl)

    @property
    def analyzers(self) -> list[SurQLAnalyzer]:
        """
            Get the analyzers of the model
        """
        return [index.analyzer for index in self.model.__surql_config__.indexes if index.analyzer is not None]

class SurQLMetadata(BaseModel):
    """
        A simple mapper to store all the SurQL tables definitions generated from pydantic models through the decorator @surql_collection
    """
    tables: list[SurQLTable] = []

    @property
    def analyzers(self) -> list[SurQLAnalyzer]:
        """
            Get the analyzers of the model
        """
        return set([table.analyzers for table in self.tables])


    @field_validator("tables")
    @classmethod
    def tables_validator(cls, v: list[SurQLTable]):
        """
            validate tables
        """
        assert len(v) == len(set([table.model.__surql_table_name__ for table in v])), "tables names must be unique"
        return v

    def clear(self):
        """
            clear all the tables definitions
        """
        self.tables = []

    def collect(self):
        """
            return a SDL string with all the tables definitions
        """
        res = []
        for analyzer in self.analyzers:
            res.append(analyzer.SDL())
        for table in self.tables:
            res.append(table.sdl)
        return "\n\n".join(res)