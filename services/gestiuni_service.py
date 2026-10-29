
from database.db import get_connection


def adauga_gestiune(cod: str, denumire: str) -> int:

    cod = cod.strip()
    denumire = denumire.strip()

    if not cod:
        raise ValueError("Codul gestiunii este obligatoriu.")

    if not denumire:
        raise ValueError("Denumirea gestiunii este obligatorie.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO gestiuni (cod, denumire)
            VALUES (?, ?)
            """,
            (cod, denumire),
        )
        return cursor.lastrowid


def lista_gestiuni(doar_active: bool = True) -> list[dict]:

    with get_connection() as connection:
        if doar_active:
            rows = connection.execute(
                """
                SELECT id, cod, denumire, activa
                FROM gestiuni
                WHERE activa = 1
                ORDER BY cod
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT id, cod, denumire, activa
                FROM gestiuni
                ORDER BY cod
                """
            ).fetchall()

        return [dict(row) for row in rows]
