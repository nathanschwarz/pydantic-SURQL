from enum import Enum
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

class SurQLAnalyzer(BaseModel):
    """
        A pydantic SurQL analyzer definition
    """
    name: str
    tokenizers: list[SurQLTokenizers] = Field(min_length=1)
    filters: list[str] = []
    SNOWBALL_LANG = "|".join([
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
    SNOWBALL_RE = f"snowball\(({SNOWBALL_LANG})\)"
    RE = f"^({SNOWBALL_RE}|ascii|lowercase|uppercase|edgengram\(\d+,\d+\))$"

    @field_validator("filters")
    @classmethod
    def filters_validator(cls, v):
        """
            validate filters
        """
        assert len(v) == len(set(v)), "filters must be unique"
        for t in v:
            assert re.match(cls.RE, t), "invalid filter, must be one of ascii, lowercase, uppercase, edgengram(<min>,<max>), snowball(<lang>)"
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
    name: str
    fields: list[str]

    def baseSDL(self) -> list[str]:
        """
            return a SDL index definition list of terms
        """
        return [
            "DEFINE INDEX",
            self.name,
            "FIELDS",
            f"{','.join(self.fields)}",
        ]

    def SDL(self, table_name: str) -> str:
        """
            return a SDL index definition
        """
        return " ".join([e for e in self.baseSDL() if e is not None]) + ';'

class SurQLUniqueIndex(SurQLIndex):
    """
        A pydantic SurQL unique index definition
    """
    def baseSDL(self) -> list[str]:
        """
            return a SDL unique index definition list of terms
        """
        return super().baseSDL() + ["UNIQUE"]

class SurQLSearchIndex(SurQLIndex):
    """
        A pydantic SurQL search index definition
    """
    analyzer: SurQLAnalyzer
    bm25: bool = False
    highlights: bool = False

    def baseSDL(self) -> list[str]:
        """
            return a SDL search index definition list of terms
        """
        return super().baseSDL() + [
            "SEARCH ANALYZER",
            self.analyzer.name,
            "BM25" if self.bm25 else None,
            "HIGHLIGHTS" if self.highlights else None,
        ]