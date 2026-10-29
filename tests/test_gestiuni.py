
from services.gestiuni_service import adauga_gestiune, lista_gestiuni


if __name__ == "__main__":
    try:
        gestiune_id = adauga_gestiune(
            "1201",
            "Materiale uz generale",
        )
        print(f"Gestiune adăugată cu ID-ul: {gestiune_id}")

    except Exception as eroare:
        print(f"Nu s-a putut adăuga gestiunea: {eroare}")

    print("\nLista gestiunilor:")
    for gestiune in lista_gestiuni():
        print(
            f"{gestiune['cod']} — {gestiune['denumire']}"
        )
