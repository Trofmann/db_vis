import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor

from entities import (
    Table,
    Column,
    DbData,
    Relation,
)
from settings import settings


class DbDataExtractor:
    def __init__(self):
        self.db_data = DbData()

    def __call__(self):
        try:
            connection = psycopg2.connect(**settings.db_config)
            cursor = connection.cursor(cursor_factory=DictCursor)
            self.get_tables_info(cursor)
            self.get_foreign_keys_info(cursor)
        except Exception as e:
            print(f'Error: {e}')
        finally:
            # Закрытие соединения
            if connection:
                cursor.close()
                connection.close()
                print("Connection closed.")
                return self.db_data

    def get_tables_info(self, cursor) -> None:
        """Получение информации о таблицах"""

        # Получение списка всех таблиц
        cursor.execute("""
            SELECT table_name AS name
            FROM information_schema.tables
            WHERE table_schema = 'public';
        """)
        tables = cursor.fetchall()

        # Для каждой таблицы получаем информацию о столбцах
        for table in tables:
            parsed_table = Table(**dict(table))
            parsed_table.columns.extend(self.get_table_columns_data(cursor, parsed_table))
            self.db_data.add_table(parsed_table)

    def get_table_columns_data(self, cursor, table: Table) -> list[Column]:
        """Получение информации о столбцах таблицы"""
        cursor.execute(sql.SQL("""
            SELECT column_name as name, ordinal_position, is_nullable, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = %s;
        """), [table.name])
        columns = cursor.fetchall()

        return [
            Column(**dict(column))
            for column in columns
        ]

    def get_foreign_keys_info(self, cursor) -> None:
        """Получение информации о внешних ключах"""
        # Подключение к базе данных

        # Получение информации о внешних ключах
        cursor.execute("""
            SELECT
                tc.table_name AS source_table,
                kcu.column_name AS source_column,
                ccu.table_name AS target_table,
                ccu.column_name AS target_column,
                rc.constraint_name AS foreign_key_name
            FROM
                information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.referential_constraints AS rc
                  ON tc.constraint_name = rc.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON rc.unique_constraint_name = ccu.constraint_name
            WHERE
                tc.constraint_type = 'FOREIGN KEY';
        """)

        foreign_keys = cursor.fetchall()

        # Вывод информации о внешних ключах
        for fk in foreign_keys:
            fk_dict = dict(fk)
            source_table = self.db_data.tables[fk_dict['source_table']]

            source_column = source_table.get_column_by_name(fk_dict['source_column'])
            if source_column is None:
                raise Exception('Не найдена колонка')

            target_table = self.db_data.tables[fk_dict['target_table']]
            target_column = target_table.get_column_by_name(fk_dict['target_column'])
            if target_column is None:
                raise Exception('Не найдена колонка')

            self.db_data.relations.append(
                Relation(
                    source_table=source_table,
                    source_column=source_column,
                    target_table=target_table,
                    target_column=target_column
                )
            )
