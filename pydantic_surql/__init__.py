from .parsers import parseFields
from .types import SchemaType, SurQLTable, SurQLMapper

Mapper = SurQLMapper(tables=[])

def toSurql(name: str):
    """
    Convert a pydantic model to a surQL query
    """
    def inner(model: SchemaType):
        table = SurQLTable(name=name, fields=[])
        fields = parseFields(model)
        print(fields)

            #print(types, subDef)
                #table.fields.append(field)
            # if field_type == str:
            #     field_type = SurQLType.STRING
            # elif field_type == int or field_type == float:
            #     field_type = SurQLType.NUMBER
            # elif field_type == bool:
            #     field_type = SurQLType.BOOLEAN
            # elif field_type == list:
            #     field_type = SurQLType.ARRAY
            # elif field_type == dict:
            #     field_type = SurQLType.OBJECT
            # else:
            #     field_type = SurQLType.RECORD
            # field = SurQLField(name=field_name, types=[field_type], subDef=None, optional=field.required)
            # table.fields.append(field)
        #print(model.model_fields)
    return inner