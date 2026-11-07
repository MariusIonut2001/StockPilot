
import shutil
import tempfile
from pathlib import Path
import os
import database.db as db


# 1. Pregătim o copie temporară a bazei de date.
if not db.DB_PATH.exists():
    raise FileNotFoundError("Baza de date StockPilot nu a fost găsită.")

fd, temp_path = tempfile.mkstemp(
    prefix="stockpilot_test_",
    suffix=".db",
)

# Închidem descriptorul creat de mkstemp.
os.close(fd)

temp_db = Path(temp_path)
temp_db.unlink(missing_ok=True)

try:
    shutil.copy2(db.DB_PATH, temp_db)

    # Toate serviciile vor lucra cu copia, nu cu baza reală.
    db.DB_PATH = temp_db

    db.init_db()

    from services.operatiuni_service import (
        inregistreaza_intrare,
        inregistreaza_iesire,
        inregistreaza_ajustare,
        stoc_scriptic,
    )
    from services.inventariere_service import (
        inregistreaza_inventariere,
    )

    print("\n=== TESTE AJUSTĂRI STOCKPILOT ===\n")

    # Luăm o gestiune și o unitate existente pentru
    # a crea materiale temporare de test.
    with db.get_connection() as connection:
        template = connection.execute("""
            SELECT gestiune_id, unitate_id
            FROM materiale
            WHERE activ = 1
            LIMIT 1
        """).fetchone()

    if template is None:
        raise RuntimeError(
            "Nu există materiale active. "
            "Adaugă cel puțin un material înainte de test."
        )

    def material_test(nume):
        with db.get_connection() as connection:
            cursor = connection.execute("""
                INSERT INTO materiale (
                    gestiune_id,
                    denumire,
                    unitate_id
                )
                VALUES (?, ?, ?)
            """, (
                template["gestiune_id"],
                nume,
                template["unitate_id"],
            ))
            return cursor.lastrowid

    def verifica_eroare(functie, mesaj):
        try:
            functie()
        except ValueError as eroare:
            print(f"OK - {eroare}")
            if mesaj.lower() not in str(eroare).lower():
                raise AssertionError(
                    f"Mesaj neașteptat: {eroare}"
                )
        else:
            raise AssertionError(
                f"Test eșuat: trebuia să apară eroarea '{mesaj}'."
            )

    # TEST 1: AJUSTARE POZITIVĂ
    print("TEST 1 - Ajustare pozitivă")

    m1 = material_test("TEST AJUSTARE POZITIVA")
    inregistreaza_intrare(m1, 100)

    inv1 = inregistreaza_inventariere(m1, 105)

    ajustare1 = inregistreaza_ajustare(
        inv1,
        "Test diferență pozitivă",
    )

    assert stoc_scriptic(m1) == 105
    print(f"OK - Stoc final: {stoc_scriptic(m1)}")
    print(f"OK - Mișcare creată: {ajustare1}")

    # TEST 2: ACEEAȘI INVENTARIERE NU POATE FI AJUSTATĂ DE DOUĂ ORI
    print("\nTEST 2 - Prevenire ajustare dublă")

    verifica_eroare(
        lambda: inregistreaza_ajustare(
            inv1,
            "A doua încercare",
        ),
        "deja ajustată",
    )

    assert stoc_scriptic(m1) == 105
    print("OK - Stocul nu a fost modificat a doua oară.")

    # TEST 3: AJUSTARE NEGATIVĂ
    print("\nTEST 3 - Ajustare negativă")

    m2 = material_test("TEST AJUSTARE NEGATIVA")
    inregistreaza_intrare(m2, 100)

    inv2 = inregistreaza_inventariere(m2, 95)

    inregistreaza_ajustare(
        inv2,
        "Test diferență negativă",
    )

    assert stoc_scriptic(m2) == 95
    print(f"OK - Stoc final: {stoc_scriptic(m2)}")

    # TEST 4: MOTIV OBLIGATORIU ȘI DIFERENȚĂ ZERO
    print("\nTEST 4 - Motiv obligatoriu și diferență zero")

    m3 = material_test("TEST AJUSTARE ZERO")
    inregistreaza_intrare(m3, 100)

    inv3 = inregistreaza_inventariere(m3, 100)

    verifica_eroare(
        lambda: inregistreaza_ajustare(inv3, ""),
        "obligatoriu",
    )

    verifica_eroare(
        lambda: inregistreaza_ajustare(
            inv3,
            "Test diferență zero",
        ),
        "nicio diferență",
    )

    assert stoc_scriptic(m3) == 100
    print("OK - Stocul a rămas 100.")

    # TEST 5: AJUSTAREA NU POATE DUCE STOCUL SUB ZERO
    print("\nTEST 5 - Prevenire stoc negativ")

    m4 = material_test("TEST AJUSTARE STOC NEGATIV")
    inregistreaza_intrare(m4, 100)

    inv4 = inregistreaza_inventariere(m4, 0)

    # După inventariere, mai înregistrăm o ieșire de 50.
    inregistreaza_iesire(m4, 50)

    verifica_eroare(
        lambda: inregistreaza_ajustare(
            inv4,
            "Test prevenire stoc negativ",
        ),
        "stocul sub zero",
    )

    assert stoc_scriptic(m4) == 50
    print("OK - Stocul a rămas 50.")

    print("\n================================")
    print("TOATE TESTELE AU TRECUT!")
    print("Baza de date reală nu a fost modificată.")
    print("================================")

finally:
    print("\nTestele s-au încheiat.")
    print(f"Copia temporară a bazei de date: {temp_db}")
    print("Fișierul temporar poate fi șters ulterior.")
