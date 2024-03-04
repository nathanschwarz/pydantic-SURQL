from typing import Type
from pydantic import BaseModel, field_validator, computed_field
from pydantic_surql.types.meta import BaseType
from .indexes import SurQLAnalyzer

class SurQLTable(BaseModel):
    """
        A pydantic SurQL table definition
        TODO: check name is not a reserved keyword
    """
    model: Type[BaseType]

    @computed_field
    def definition(self) -> str:
        """
            Get the table definition
        """
        _def = ["DEFINE TABLE", self.model.surql_table_name]
        if (self.model.surql_config.asView is not None):
            _def += [self.model.surql_config.asView.SDL()]
        else:
            _def += [
                "DROP" if self.model.surql_config.drop else None,
                "SCHEMAFULL" if self.model.surql_config.strict else "SCHEMALESS",
                f"CHANGEFEED {self.model.surql_config.changeFeed}" if self.model.surql_config.changeFeed is not None else None,
            ]
            _def = [e for e in _def if e is not None]
        if (self.model.surql_config.permissions is not None):
            _def.append(self.model.surql_config.permissions.SDL())
        return " ".join(_def) + ";"

    @computed_field
    def sdl(self) -> str:
        """
            Get the SDL representation of the model
        """
        sdl = [self.definition, self.model.surql_schema.sdl]
        for index in self.model.surql_config.indexes:
            sdl.append(index.SDL(self.model.surql_table_name))
        for event in self.model.surql_config.events:
            sdl.append(event.SDL(self.model.surql_table_name))
        return "\n".join(sdl)

    @computed_field
    def analyzers(self) -> list[SurQLAnalyzer]:
        """
            Get the analyzers of the model
        """
        return [index.analyzer for index in self.model.surql_config.indexes if index.analyzer is not None]

class SurQLMetadata(BaseModel):
    """
        A simple mapper to store all the SurQL tables definitions generated from pydantic models through the decorator @surql_collection
    """
    tables: list[SurQLTable] = []

    @computed_field
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
        assert len(v) == len(set([table.model.surql_table_name for table in v])), "tables names must be unique"
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