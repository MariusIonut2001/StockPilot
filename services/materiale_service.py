
from database.db import get_connection


def adauga_material(
    gestiune_id: int,
    denumire: str,
    unitate_id: int,
    cod: str | None = None,
) -> int:
    denumire = denumire.strip()
    cod = cod.strip() if cod else None

    if not denumire:
        raise ValueError("Denumirea materialului este obligatorie.")

    if gestiune_id <= 0:
        raise ValueError("Selectează o gestiune validă.")

    if unitate_id <= 0:
        raise ValueError("Selectează o unitate de măsură validă.")

    with get_connection() as connection:
        gestiune = connection.execute(
            "SELECT id FROM gestiuni WHERE id = ? AND activa = 1",
            (gestiune_id,),
        ).fetchone()

        if gestiune is None:
            raise ValueError("Gestiunea selectată nu există sau este inactivă.")

        unitate = connection.execute(
            "SELECT id FROM unitati_masura WHERE id = ? AND activa = 1",
            (unitate_id,),
        ).fetchone()

        if unitate is None:
            raise ValueError("Unitatea de măsură nu există sau este inactivă.")

        if cod:
            existent = connection.execute(
                """
                SELECT id
                FROM materiale
                WHERE gestiune_id = ?
                  AND cod = ?
                  AND activ = 1
                """,
                (gestiune_id, cod),
            ).fetchone()

            if existent:
                raise ValueError(
                    "Există deja un material activ cu acest cod în gestiunea selectată."
                )

        cursor = connection.execute(
            """
            INSERT INTO materiale (gestiune_id, cod, denumire, unitate_id)
            VALUES (?, ?, ?, ?)
            """,
            (gestiune_id, cod, denumire, unitate_id),
        )

        return cursor.lastrowid


def lista_materiale(
    gestiune_id: int | None = None,
    doar_active: bool = True,
) -> list[dict]:
    conditii = []
    parametri = []

    if gestiune_id is not None:
        conditii.append("m.gestiune_id = ?")
        parametri.append(gestiune_id)

    if doar_active:
        conditii.append("m.activ = 1")

    where_sql = ""
    if conditii:
        where_sql = "WHERE " + " AND ".join(conditii)

    interogare = f"""
        SELECT
            m.id,
            m.gestiune_id,
            g.cod AS cod_gestiune,
            g.denumire AS denumire_gestiune,
            m.cod,
            m.denumire,
            m.unitate_id,
            u.denumire AS unitate,
            m.activ
        FROM materiale m
        JOIN gestiuni g ON g.id = m.gestiune_id
        JOIN unitati_masura u ON u.id = m.unitate_id
        {where_sql}
        ORDER BY g.cod, m.denumire
    """

    with get_connection() as connection:
        rows = connection.execute(
            interogare,
            parametri,
        ).fetchall()

        return [dict(row) for row in rows]
