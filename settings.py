from typing import Any

__all__ = [
    'settings',
]


class Settings:
    @property
    def db_config(self) -> dict[str, Any]:
        """Параметры подключения к базе данных"""
        return {
            'dbname': 'german',
            'user': 'postgres',
            'password': 'postgres',
            'host': 'localhost',
            'port': 5432
        }


settings = Settings()
