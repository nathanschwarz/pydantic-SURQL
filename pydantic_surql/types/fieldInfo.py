from typing import Optional
from pydantic_surql.types.permissions import SurQLPermissions
from pydantic.fields import FieldInfo

class SurQLFieldInfo(FieldInfo):
    """
        A pydantic SurQL field info definition
    """
    perms: Optional[SurQLPermissions] = None

    def __init__(self, perms: Optional[SurQLPermissions], **kwargs):
        super().__init__(**kwargs)
        self.perms = perms

def SurQLFieldConfig(permissions: Optional[SurQLPermissions] = None, **kwargs) -> SurQLFieldInfo:
    """
        A pydantic SurQL field config definition
        TODO: find a way to map Field arguments for proper type hints (see: https://stackoverflow.com/questions/1409295/set-function-signature-in-python)
    """
    return SurQLFieldInfo(permissions, **kwargs)