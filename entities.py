import pydantic

__all__ = [
    'Column',
    'Table',
    'Relation',
    'DbData',
]


class Column(pydantic.BaseModel):
    table_name: str
    name: str
    ordinal_position: int
    is_nullable: bool
    data_type: str
    character_maximum_length: int | None

    def __str__(self) -> str:
        return f'{self.table_name}.{self.name}'

    @pydantic.field_validator('is_nullable', mode='before')
    @classmethod
    def parse_bool(cls, v: str) -> bool:
        return v.lower() == 'yes'


class Table(pydantic.BaseModel):
    name: str
    columns: list[Column] = pydantic.Field(default_factory=list)

    def get_column_by_name(self, name: str) -> Column | None:
        for column in self.columns:
            if column.name == name:
                return column
        return None


class Relation(pydantic.BaseModel):
    source_table: Table
    source_column: Column
    target_table: Table
    target_column: Column


class DbData(pydantic.BaseModel):
    tables: dict[str, Table] = pydantic.Field(default_factory=dict)
    relations: list[Relation] = pydantic.Field(default_factory=list)

    def add_table(self, table: Table):
        self.tables[table.name] = table
