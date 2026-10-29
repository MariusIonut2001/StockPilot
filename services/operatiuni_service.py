
from datetime import datetime

from database.db import get_connection


def stoc_scriptic(material_id: int) -> float:
    with get_connection() as connection:
        material = connection.execute(
            "SELECT id FROM materiale WHERE id = ?",
            (material_id,),
        ).fetchone()

        if material is None:
            raise ValueError("Materialul selectat nu există.")

        rezultat = connection.execute(
            """
            SELECT COALESCE(SUM(cantitate * sens), 0) AS stoc
            FROM miscari_stoc
            WHERE material_id = ?
            """,
            (material_id,),
        ).fetchone()

        return float(rezultat["stoc"])


def _verifica_material(connection, material_id: int):
    material = connection.execute(
        """
        SELECT id
        FROM materiale
        WHERE id = ? AND activ = 1
        """,
        (material_id,),
    ).fetchone()

    if material is None:
        raise ValueError("Materialul nu există sau este inactiv.")


def _valideaza_cantitate(cantitate: float):
    if cantitate <= 0:
        raise ValueError("Cantitatea trebuie să fie mai mare decât zero.")


def _data_curenta():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def inregistreaza_intrare(
    material_id: int,
    cantitate: float,
    data_operatiunii: str | None = None,
    observatii: str | None = None,
) -> int:
    _valideaza_cantitate(cantitate)
    data_operatiunii = data_operatiunii or _data_curenta()

    with get_connection() as connection:
        connection.execute("BEGIN IMMEDIATE")

        _verifica_material(connection, material_id)

        cursor = connection.execute(
            """
            INSERT INTO miscari_stoc (
                material_id,
                tip,
                cantitate,
                sens,
                data_operatiunii,
                observatii
            )
            VALUES (?, 'INTRARE', ?, 1, ?, ?)
            """,
            (
                material_id,
                cantitate,
                data_operatiunii,
                observatii,
            ),
        )

        return cursor.lastrowid


def inregistreaza_iesire(
    material_id: int,
    cantitate: float,
    data_operatiunii: str | None = None,
    observatii: str | None = None,
    destinatar_id: int | None = None,
) -> int:
    _valideaza_cantitate(cantitate)
    data_operatiunii = data_operatiunii or _data_curenta()

    with get_connection() as connection:
        connection.execute("BEGIN IMMEDIATE")

        _verifica_material(connection, material_id)

        rezultat = connection.execute(
            """
            SELECT COALESCE(SUM(cantitate * sens), 0) AS stoc
            FROM miscari_stoc
            WHERE material_id = ?
            """,
            (material_id,),
        ).fetchone()

        stoc_disponibil = float(rezultat["stoc"])

        if cantitate > stoc_disponibil:
            raise ValueError(
                f"Stoc insuficient. Disponibil: {stoc_disponibil:g}, "
                f"solicitat: {cantitate:g}."
            )

        cod_atelier_snapshot = None
        sef_atelier_snapshot = None

        if destinatar_id is not None:
            destinatar = connection.execute(
                """
                SELECT cod_atelier, sef_atelier
                FROM destinatari
                WHERE id = ? AND activ = 1
                """,
                (destinatar_id,),
            ).fetchone()

            if destinatar is None:
                raise ValueError("Destinatarul nu există sau este inactiv.")

            cod_atelier_snapshot = destinatar["cod_atelier"]
            sef_atelier_snapshot = destinatar["sef_atelier"]

        cursor = connection.execute(
            """
            INSERT INTO miscari_stoc (
                material_id,
                tip,
                cantitate,
                sens,
                data_operatiunii,
                destinatar_id,
                cod_atelier_snapshot,
                sef_atelier_snapshot,
                observatii
            )
            VALUES (?, 'IESIRE', ?, -1, ?, ?, ?, ?, ?)
            """,
            (
                material_id,
                cantitate,
                data_operatiunii,
                destinatar_id,
                cod_atelier_snapshot,
                sef_atelier_snapshot,
                observatii,
            ),
        )

        return cursor.lastrowid


def istoric_material(material_id: int) -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                tip,
                cantitate,
                sens,
                data_operatiunii,
                cod_atelier_snapshot,
                sef_atelier_snapshot,
                observatii,
                motiv
            FROM miscari_stoc
            WHERE material_id = ?
            ORDER BY data_operatiunii DESC, id DESC
            """,
            (material_id,),
        ).fetchall()

        return [dict(row) for row in rows]
