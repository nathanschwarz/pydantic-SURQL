from pydantic import BaseModel, model_validator

class SurQLPermissions(BaseModel):
    """
        A pydantic SurQL table / field permissions definition
    """
    select: list[str] | None = None
    create: list[str] | None = None
    update: list[str] | None = None
    delete: list[str] | None = None

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
    @classmethod
    def check_permissions(cls, v):
        """
            check if permissions are valid
        """
        assert v.select is None or len(v.select) > 0, "SELECT permissions must have at least one permission set"
        assert v.create is None or len(v.create) > 0, "CREATE permissions must have at least one permission set"
        assert v.update is None or len(v.update) > 0, "UPDATE permissions must have at least one permission set"
        assert v.delete is None or len(v.delete) > 0, "DELETE permissions must have at least one permission set"
        assert any([v.select != None, v.create != None, v.update != None, v.delete != None]), "Permissions must have at least one permission set"
        return v