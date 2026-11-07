from datetime import datetime

from database.db import get_connection


def inregistreaza_inventariere(
    material_id: int,
    cantitate_faptica: float,
    data_inventarierii: str | None = None,
    observatii: str | None = None,
) -> int:
    """
    Înregistrează cantitatea constatată fizic.
    Nu modifică stocul scriptic.
    Calculează stocul scriptic la data inventarierii.
    Returnează ID-ul inventarierii.
    """

    try:
        cantitate_faptica = float(cantitate_faptica)
    except (TypeError, ValueError):
        raise ValueError(
            "Cantitatea constatată trebuie să fie un număr valid."
        )

    if cantitate_faptica < 0:
        raise ValueError(
            "Cantitatea constatată nu poate fi negativă."
        )

    if data_inventarierii is None:
        data_inventarierii = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    else:
        try:
            data_validata = datetime.fromisoformat(
                data_inventarierii
            )
            data_inventarierii = data_validata.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            raise ValueError(
                "Data trebuie să fie în formatul YYYY-MM-DD HH:MM:SS."
            )

    with get_connection() as connection:
        connection.execute("BEGIN IMMEDIATE")

        material = connection.execute(
            """
            SELECT id
            FROM materiale
            WHERE id = ? AND activ = 1
            """,
            (material_id,),
        ).fetchone()

        if material is None:
            raise ValueError(
                "Materialul nu există sau este arhivat."
            )

        # Calculăm stocul scriptic doar din mișcările
        # înregistrate până la data inventarierii.
        miscari = connection.execute(
            """
            SELECT COALESCE(SUM(cantitate * sens), 0) AS stoc
            FROM miscari_stoc
            WHERE material_id = ?
              AND data_operatiunii <= ?
            """,
            (material_id, data_inventarierii),
        ).fetchone()

        cantitate_scriptica = float(miscari["stoc"])

        diferenta = (
            cantitate_faptica - cantitate_scriptica
        )

        cursor = connection.execute(
            """
            INSERT INTO inventarieri (
                material_id,
                data_inventarierii,
                cantitate_scriptica,
                cantitate_faptica,
                diferenta,
                observatii
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                material_id,
                data_inventarierii,
                cantitate_scriptica,
                cantitate_faptica,
                diferenta,
                observatii.strip()
                if observatii and observatii.strip()
                else None,
            ),
        )

        return cursor.lastrowid


def lista_inventarieri(
    material_id: int | None = None
) -> list[dict]:
    """
    Returnează inventarierile, de la cea mai recentă
    la cea mai veche.

    Dacă este transmis un material_id,
    filtrează după material.

    Returnează și ID-ul ajustării asociate,
    dacă aceasta a fost deja aplicată.
    """

    interogare = """
        SELECT
            i.id,
            i.material_id,
            m.cod AS cod_material,
            m.denumire AS denumire_material,
            g.cod AS cod_gestiune,
            g.denumire AS denumire_gestiune,
            u.denumire AS unitate,
            i.data_inventarierii,
            i.cantitate_scriptica,
            i.cantitate_faptica,
            i.diferenta,
            i.observatii,

            (
                SELECT ms.id
                FROM miscari_stoc ms
                WHERE ms.inventariere_id = i.id
                LIMIT 1
            ) AS ajustare_id

        FROM inventarieri i
        JOIN materiale m ON m.id = i.material_id
        JOIN gestiuni g ON g.id = m.gestiune_id
        JOIN unitati_masura u ON u.id = m.unitate_id
    """

    parametri = []

    if material_id is not None:
        interogare += " WHERE i.material_id = ?"
        parametri.append(material_id)

    interogare += """
        ORDER BY i.data_inventarierii DESC, i.id DESC
    """

    with get_connection() as connection:
        randuri = connection.execute(
            interogare,
            parametri,
        ).fetchall()

        return [dict(rand) for rand in randuri]