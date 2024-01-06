from enum import Enum
from typing import LiteralString
from pydantic import BaseModel, Field, field_validator
import re

class SurQLTokenizers(Enum):
    """
        SurQL tokenizers enumeration
    """
    BLANK = "blank"
    CAMEL = "camel"
    CLASS = "class"
    PUNCT = "punct"

SNOWBALL_LANG: LiteralString = "|".join([
    "arabic",
    "danish",
    "dutch",
    "english",
    "french",
    "german",
    "greek",
    "hungarian",
    "italian",
    "norwegian",
    "portuguese",
    "romanian",
    "russian",
    "spanish",
    "swedish",
    "tamil",
    "turkish",
])
RE = re.compile(fr"^snowball\(({SNOWBALL_LANG})\)|ascii|lowercase|uppercase|edgengram\(\d+,\d+\)$")

class SurQLAnalyzer(BaseModel):
    """
        A pydantic SurQL analyzer definition
    """
    name: str = Field(min_length=1)
    tokenizers: list[SurQLTokenizers] = Field(min_length=1)
    filters: list[str] = []

    @field_validator("filters")
    @classmethod
    def filters_validator(cls, v):
        """
            validate filters
        """
        assert len(v) == len(set(v)), "filters must be unique"
        for t in v:
            assert re.match(RE, t), "invalid filter, must be one of ascii, lowercase, uppercase, edgengram(<min>,<max>), snowball(<lang>)"
        return v

    def SDL(self) -> str:
        """
            return a SDL analyzer definition
        """
        _def = [
            "DEFINE ANALYZER",
            self.name,
            "TOKENIZERS",
            ','.join([t.value for t in self.tokenizers]),
        ]
        if (len(self.filters) > 0):
            _def += ["FILTERS", ','.join(self.filters)]
        return " ".join(_def) + ';'

class SurQLIndex(BaseModel):
    """
        A pydantic SurQL index definition
        TODO: implement search indexes
    """
    name: str = Field(min_length=1)
    fields: list[str]

    def baseSDL(self, table_name: str) -> list[str]:
        """
            return a SDL index definition list of terms
        """
        return [
            "DEFINE INDEX",
            self.name,
            "ON TABLE",
            table_name,
            "FIELDS",
            f"{','.join(self.fields)}",
        ]

    def SDL(self, table_name: str) -> str:
        """
            return a SDL index definition
        """
        return " ".join([e for e in self.baseSDL(table_name) if e is not None]) + ';'

class SurQLUniqueIndex(SurQLIndex):
    """
        A pydantic SurQL unique index definition
    """
    def baseSDL(self, table_name: str) -> list[str]:
        """
            return a SDL unique index definition list of terms
        """
        return super().baseSDL(table_name) + ["UNIQUE"]

class SurQLSearchIndex(SurQLIndex):
    """
        A pydantic SurQL search index definition
    """
    analyzer: SurQLAnalyzer
    bm25: tuple[float, float] | None = None
    highlights: bool = False

    def baseSDL(self, table_name: str) -> list[str]:
        """
            return a SDL search index definition list of terms
        """
        return super().baseSDL(table_name) + [
            "SEARCH ANALYZER",
            self.analyzer.name,
            f"BM25({self.bm25[0]},{self.bm25[1]})" if self.bm25 else None,
            "HIGHLIGHTS" if self.highlights else None,
        ]