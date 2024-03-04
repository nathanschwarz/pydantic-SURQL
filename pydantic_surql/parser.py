from typing import Type, Union
from pydantic import BaseModel, create_model
from pydantic_surql.types.meta import BaseType, Schema, SchemaField

from .cache import Cache
from .types import SurQLTableConfig

class SurQLParser:
    """
        A pydantic SurQL parser
    """
    def __init__(self):
        self.cache = Cache[Schema | SchemaField]()

    def __rewriteClass(self, model: Type, name: str, config: SurQLTableConfig) -> Type[BaseType]:
        """
            Rewrite the class to add the new attributes
        """
        schema = Schema.from_pydantic_model(model, name)
        cls = create_model(
            __model_name= model.__name__,
            __base__=(BaseType, model),
            __name__ = model.__name__,
            __is_surql_collection__ = True,
            __surql_table_name__ = name,
            __surql_schema__ = schema,
            __surql_config__ = config,
        )
        return cls

    def from_model(self, name: str, model: BaseModel, config: SurQLTableConfig = SurQLTableConfig()):
        """
            Convert a pydantic model to a SurQLTable
            can be used at runtime
        """
        extra = model.model_config.get('extra')
        if extra == 'allow':
            config.strict = False
        elif config.strict == False:
            model.model_config['extra'] = 'allow'
        return self.__rewriteClass(model, name, config)