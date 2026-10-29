
from services.unitati_service import adauga_unitate, lista_unitati


if __name__ == "__main__":
    unitati_initiale = [
        "bucată",
        "kilogram",
        "litru",
        "metru",
    ]

    for denumire in unitati_initiale:
        try:
            adauga_unitate(denumire)
            print(f"Unitate adăugată: {denumire}")
        except ValueError as eroare:
            print(f"{denumire}: {eroare}")

    print("\nUnități de măsură disponibile:")

    for unitate in lista_unitati():
        print(f"- ID {unitate['id']}: {unitate['denumire']}")
