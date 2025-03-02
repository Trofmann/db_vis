import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from entities import Table, Column

# Параметры подключения к базе данных
db_config = {
    'dbname': 'german',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': 5432
}


# Функция для получения информации о таблицах
def get_tables_info() -> dict[str, Table] | None:
    """Получение информации о таблицах"""
    try:
        # Подключение к базе данных
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor(cursor_factory=DictCursor)

        # Получение списка всех таблиц
        cursor.execute("""
            SELECT table_name AS name
            FROM information_schema.tables
            WHERE table_schema = 'public';
        """)
        tables = cursor.fetchall()

        parsed_tables: dict[str, Table] = dict()

        # Для каждой таблицы получаем информацию о столбцах
        for table in tables:
            parsed_table = Table(**dict(table))
            parsed_tables[parsed_table.name] = parsed_table

            parsed_table.columns.extend(get_table_columns_data(cursor, parsed_table))


    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Закрытие соединения
        if connection:
            cursor.close()
            connection.close()
            print("Connection closed.")
            return parsed_tables


def get_table_columns_data(cursor, table: Table) -> list[Column]:
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


def get_foreign_keys_info():
    try:
        # Подключение к базе данных
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()

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
            source_table, source_column, target_table, target_column, fk_name = fk
            print(
                f"Foreign Key: {fk_name}\n"
                f"  Source Table: {source_table}, Column: {source_column}\n"
                f"  Target Table: {target_table}, Column: {target_column}\n"
            )

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Закрытие соединения
        if connection:
            cursor.close()
            connection.close()
            print("Connection closed.")


# Вызов функции
get_tables_info()
