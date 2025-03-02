import pydantic

__all__ = [
    'Column',
    'Table',
    'Relation',
]


class Column(pydantic.BaseModel):
    name: str
    ordinal_position: int
    is_nullable: bool
    data_type: str
    character_maximum_length: int | None

    @pydantic.field_validator('is_nullable', mode='before')
    @classmethod
    def parse_bool(cls, v: str) -> bool:
        return v.lower() == 'yes'


class Table(pydantic.BaseModel):
    name: str
    columns: list[Column] = pydantic.Field(default_factory=list)


class Relation(pydantic.BaseModel):
    source_table: Table
    source_column: Column
    target_table: Table
    target_column: Column
