from pydantic import BaseModel, Field, model_validator

class SurQLPermissions(BaseModel):
    """
        A pydantic SurQL table / field permissions definition
    """
    select: list[str] | None = Field(default=None, min_length=1, description="select statements")
    create: list[str] | None = Field(default=None, min_length=1, description="create statements")
    update: list[str] | None = Field(default=None, min_length=1, description="update statements")
    delete: list[str] | None = Field(default=None, min_length=1, description="delete statements")

    @staticmethod
    def __term_sdl__(term: str, definitions: list[str]) -> str:
        """
            return a SDL permission block
        """
        _def = '\n'.join([f"        {e}" for e in definitions])
        return f"FOR {term}\n{_def}"

    def SDL(self):
        _def = [
            "PERMISSIONS",
            self.__term_sdl__("SELECT", self.select) if self.select is not None else None,
            self.__term_sdl__("CREATE", self.create) if self.create is not None else None,
            self.__term_sdl__("UPDATE", self.update) if self.update is not None else None,
            self.__term_sdl__("DELETE", self.delete) if self.delete is not None else None,
        ]
        return "\n    ".join([e for e in _def if e is not None])

    @model_validator(mode="after")
    def validate_permissions(self) -> 'SurQLPermissions':
        """
            check if permissions are valid
        """
        assert any([self.select != None, self.create != None, self.update != None, self.delete != None]), "Permissions must have at least one permission set"
        return self