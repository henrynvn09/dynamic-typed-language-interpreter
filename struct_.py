from element import Element
from type_value_ import Value, create_default_value_obj
from copy import deepcopy


class Struct:
    def __init__(self, struct_def: Element):
        if isinstance(struct_def, Element):
            self.name = struct_def.get("name")
            self.fields = {}
            for field in struct_def.get("fields"):
                self.fields[field.get("name")] = create_default_value_obj(
                    field.get("var_type")
                )
                # TODO: do I need to support default values for fields?
        elif isinstance(struct_def, Struct):
            self.name = struct_def.name
            self.fields = deepcopy(struct_def.fields)
        else:
            raise Exception("Invalid argument type for Struct constructor")

    def set_field(self, field_name: str, value: Value):
        if field_name not in self.fields:
            raise Exception(f"Field {field_name} does not exist in struct {self.name}")

        self.fields[field_name] = value

    def get_field(self, field_name: str):
        if field_name not in self.fields:
            raise Exception(f"Field {field_name} does not exist in struct {self.name}")

        return self.fields[field_name]
