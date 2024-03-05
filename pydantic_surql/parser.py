from typing import Type
from pydantic import BaseModel, create_model
from pydantic_surql.types.meta import BaseType, Schema, SchemaField, Input

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
        input = Input.from_schema(schema, name)
        class Parent(BaseType):
            is_surql_collection = True
            surql_table_name = name
            surql_schema = schema
            surql_config = config
            input = input

        cls = create_model(
            __model_name= model.__name__,
            __base__=(Parent, model),
            __doc__= model.__doc__,
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