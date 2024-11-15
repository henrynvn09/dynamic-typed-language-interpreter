from element import Element
from type_value_ import Value, Type
from copy import deepcopy


class Struct:
    def __init__(self, field_types: dict[str], get_default_value):
        self.fields = {}
        for field_name, field_type in field_types.items():
            self.fields[field_name] = get_default_value(field_type)

    def set_field(self, field_name: str, value: Value):
        if field_name not in self.fields:
            raise Exception(f"Field {field_name} does not exist in struct {self.name}")

        self.fields[field_name] = value

    def get_field(self, field_name: str):
        if field_name not in self.fields:
            raise Exception(f"Field {field_name} does not exist in struct {self.name}")

        return self.fields[field_name]
