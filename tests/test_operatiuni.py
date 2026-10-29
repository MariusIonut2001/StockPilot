
from services.gestiuni_service import lista_gestiuni
from services.materiale_service import adauga_material, lista_materiale
from services.unitati_service import lista_unitati
from services.operatiuni_service import (
    inregistreaza_intrare,
    inregistreaza_iesire,
    stoc_scriptic,
    istoric_material,
)


def main():
    gestiuni = lista_gestiuni()
    unitati = lista_unitati()

    if not gestiuni:
        print("Nu există gestiuni. Creează mai întâi una.")
        return

    if not unitati:
        print("Nu există unități de măsură.")
        return

    gestiune_id = gestiuni[0]["id"]
    unitate_id = unitati[0]["id"]

    try:
        material_id = adauga_material(
            gestiune_id=gestiune_id,
            denumire="MATERIAL TEST OPERATIUNI",
            unitate_id=unitate_id,
            cod="TEST-OPERATIUNI",
        )
        print(f"Material de test creat. ID: {material_id}")

    except ValueError as eroare:
        if "Există deja un material activ" not in str(eroare):
            print(f"Nu s-a putut crea materialul: {eroare}")
            return

        materiale = lista_materiale(gestiune_id)
        material = next(
            (
                m for m in materiale
                if m["cod"] == "TEST-OPERATIUNI"
            ),
            None,
        )

        if material is None:
            print("Materialul de test există, dar nu a putut fi găsit.")
            return

        material_id = material["id"]
        print(f"Folosim materialul de test existent. ID: {material_id}")

    print("\n1. Înregistrăm o intrare de 100...")
    inregistreaza_intrare(material_id, 100)
    print(f"Stoc după intrare: {stoc_scriptic(material_id):g}")

    print("\n2. Înregistrăm o ieșire de 30...")
    inregistreaza_iesire(material_id, 30)
    print(f"Stoc după ieșire: {stoc_scriptic(material_id):g}")

    print("\n3. Încercăm o ieșire de 1000...")
    try:
        inregistreaza_iesire(material_id, 1000)
        print("EROARE: ieșirea prea mare a fost acceptată!")
    except ValueError as eroare:
        print(f"Ieșire blocată corect: {eroare}")

    print(f"\nStoc final: {stoc_scriptic(material_id):g}")

    print("\nIstoric:")
    for miscare in istoric_material(material_id):
        print(
            f"ID {miscare['id']} | {miscare['tip']} | "
            f"{miscare['cantitate']:g} | {miscare['data_operatiunii']}"
        )


if __name__ == "__main__":
    main()
