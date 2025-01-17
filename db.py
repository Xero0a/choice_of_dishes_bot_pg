import os
from typing import List, Tuple

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql, errors

from exceptions import CantTableError

load_dotenv()


class PostgresClient:
    """Класс для работы с базой данных PostgresSQL."""

    def __init__(self, dbname, user, password, host):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.db_connect = psycopg2.connect(
            dbname=self.dbname, user=self.user, password=self.password, host=self.host
        )
        self.cursor = self.db_connect.cursor()

    def select_all_tables_name_from_db(self) -> List[Tuple[str, ...]]:
        """
        Выводит список кортежей, содержащий названия всех таблиц из базы данных.

        Или пустой список, если таблиц нет.
        """

        self.cursor.execute(
            """
                            SELECT table_name FROM information_schema.tables \
                            WHERE table_schema NOT IN ('information_schema','pg_catalog');
                        """
        )

        return self.cursor.fetchall()

    def select_columns_from_table(
        self, table_name: str, *args: str
    ) -> List[Tuple[str, ...]]:
        """Возвращает список с кортежами, содержащими данные переданных полей из *args из таблицы table_name."""

        query = sql.SQL("SELECT {} FROM {}").format(
            sql.SQL(",").join(map(sql.Identifier, args)), sql.Identifier(table_name)
        )
        self.cursor.execute(query)

        return self.cursor.fetchall()

    def select_all_from_table(self, table_name: str) -> List[Tuple[str, ...]]:
        """Возвращает все значения из переданной таблицы table_name."""
        try:
            self.cursor.execute("SELECT * FROM {}".format(table_name))
        except errors.SyntaxError:
            raise CantTableError("Вы ввели несуществующее название таблицы.")

        return self.cursor.fetchall()

    def create_table(self, table_name: str, values_pattern: str) -> None:
        """
        Создаёт новую таблицу table_name с переданными полями и параметрами полей из values_pattern.

        Поля и параметры values_pattern передаются по шаблону: "test TEXT, test1 VARCHAR(20), test2 INTEGER".
        """

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS {}({})".format(table_name, values_pattern)
        )
        self.db_connect.commit()

    def insert_in_table(self, table_name: str, **kwargs: str) -> None:
        """
        Добавляет данные переданные в **kwargs в таблицу table_name.

        Важно, что данные должны быть строками, иначе функция не сработает!
        """

        insert = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table_name),
            sql.SQL(", ").join(map(sql.Identifier, kwargs.keys())),
            sql.SQL(", ").join(map(sql.Literal, kwargs.values())),
        )
        self.cursor.execute(insert)
        self.db_connect.commit()

    def delete_table(self, table_name: str) -> None:
        """Удаляет таблицу table_name из базы данных."""

        query = """
                    DROP TABLE IF EXISTS {} CASCADE;
                """.format(
            table_name
        )
        self.cursor.execute(query)
        self.db_connect.commit()

    def update_table_where(
        self,
        table_name: str,
        set_column: str,
        set_column_value: str,
        where_pattern: str,
    ) -> None:
        """
        Обновляет колонку переданную в set_column данными, переданными в set_column_value,
        при условии переданном в where_pattern.

        where_pattern должен соответствовать sql синтаксису после WHERE:
        "firstname = 'Sasha'"
        "id = 25"
         и тп.
        """

        update = sql.SQL("UPDATE {} SET {}={} WHERE {}").format(
            sql.Identifier(table_name),
            sql.Identifier(set_column),
            sql.Literal(set_column_value),
            sql.SQL(where_pattern),
        )
        self.cursor.execute(update)
        self.db_connect.commit()

    def delete_value_in_table(self, table_name: str, where_pattern: str) -> None:
        """
        Удаляет запись из таблицы table_name которая соответствует введенному паттерну where_pattern.

        where_pattern должен соответствовать sql синтаксису после WHERE:
        "firstname = 'Sasha'"
        "id = 25"
        и тп.
        """

        query = """
            DELETE FROM {} WHERE {};
        """.format(
            table_name, where_pattern
        )
        self.cursor.execute(query)
        self.db_connect.commit()


if __name__ == "__main__":
    my_postgres_db = PostgresClient(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
    )
