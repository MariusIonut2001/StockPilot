
from database.db import get_connection


def adauga_unitate(denumire: str) -> int:
    denumire = denumire.strip()

    if not denumire:
        raise ValueError("Denumirea unității de măsură este obligatorie.")

    with get_connection() as connection:
        existenta = connection.execute(
            """
            SELECT id, activa
            FROM unitati_masura
            WHERE denumire = ? COLLATE NOCASE
            """,
            (denumire,),
        ).fetchone()

        if existenta:
            if existenta["activa"]:
                raise ValueError("Această unitate de măsură există deja.")

            connection.execute(
                """
                UPDATE unitati_masura
                SET activa = 1
                WHERE id = ?
                """,
                (existenta["id"],),
            )
            return existenta["id"]

        cursor = connection.execute(
            "INSERT INTO unitati_masura (denumire) VALUES (?)",
            (denumire,),
        )

        return cursor.lastrowid


def lista_unitati(doar_active: bool = True) -> list[dict]:
    with get_connection() as connection:
        if doar_active:
            rows = connection.execute(
                """
                SELECT id, denumire, activa
                FROM unitati_masura
                WHERE activa = 1
                ORDER BY denumire
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT id, denumire, activa
                FROM unitati_masura
                ORDER BY denumire
                """
            ).fetchall()

        return [dict(row) for row in rows]
