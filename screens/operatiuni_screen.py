
import flet as ft
from datetime import datetime

from services.gestiuni_service import lista_gestiuni
from services.materiale_service import lista_materiale
from services.operatiuni_service import (
    inregistreaza_intrare,
    inregistreaza_iesire,
    stoc_scriptic,
    istoric_material,
)


def operatiuni_screen(page: ft.Page):
    gestiuni = lista_gestiuni()

    gestiune_selectata = ft.Dropdown(
        label="Gestiune",
        hint_text="Selectează gestiunea",
        value=str(gestiuni[0]["id"]) if gestiuni else None,
        options=[
            ft.dropdown.Option(
                key=str(g["id"]),
                text=f'{g["cod"]} — {g["denumire"]}',
            )
            for g in gestiuni
        ],
        width=400,
    )

    material_selectat = ft.Dropdown(
        label="Material",
        hint_text="Selectează un material",
        options=[],
        width=400,
    )

    tip_operatiune = ft.Dropdown(
        label="Tip operațiune",
        value="INTRARE",
        options=[
            ft.dropdown.Option(key="INTRARE", text="Intrare"),
            ft.dropdown.Option(key="IESIRE", text="Ieșire"),
        ],
        width=200,
    )

    cantitate_input = ft.TextField(
        label="Cantitate",
        hint_text="Ex. 10",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=200,
    )

    data_input = ft.TextField(
        label="Data și ora",
        value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        hint_text="AAAA-LL-ZZ HH:MM:SS",
        width=260,
    )

    observatii_input = ft.TextField(
        label="Observații (opțional)",
        multiline=True,
        min_lines=2,
        max_lines=3,
    )

    stoc_text = ft.Text(
        "Stoc scriptic curent: —",
        size=18,
        weight=ft.FontWeight.BOLD,
    )

    mesaj = ft.Text()
    lista_istoric = ft.Column(spacing=6)

    def incarca_istoric():
        lista_istoric.controls.clear()

        if not material_selectat.value:
            lista_istoric.controls.append(
                ft.Text("Selectează un material pentru a vedea istoricul.")
            )
            return

        miscari = istoric_material(int(material_selectat.value))

        if not miscari:
            lista_istoric.controls.append(
                ft.Text("Nu există operațiuni înregistrate.")
            )
            return

        for miscare in miscari:
            semn = "+" if miscare["sens"] == 1 else "-"
            detalii = (
                f'{miscare["data_operatiunii"]} | '
                f'{miscare["tip"]} | '
                f'{semn}{miscare["cantitate"]:g}'
            )

            if miscare["observatii"]:
                detalii += f' | {miscare["observatii"]}'

            lista_istoric.controls.append(
                ft.Container(
                    content=ft.Text(detalii),
                    padding=10,
                    border=ft.Border.all(
                        1,
                        ft.Colors.OUTLINE_VARIANT,
                    ),
                    border_radius=8,
                )
            )

    def actualizeaza_stoc():
        if not material_selectat.value:
            stoc_text.value = "Stoc scriptic curent: —"
            return

        stoc = stoc_scriptic(int(material_selectat.value))
        stoc_text.value = f"Stoc scriptic curent: {stoc:g}"

    def incarca_materiale(e=None):
        material_selectat.options = []
        material_selectat.value = None
        mesaj.value = ""

        if not gestiune_selectata.value:
            material_selectat.hint_text = "Selectează mai întâi gestiunea"
            material_selectat.options = [
                ft.dropdown.Option(
                    key="",
                    text="Nu există o gestiune selectată",
                )
            ]
        else:
            materiale = lista_materiale(
                int(gestiune_selectata.value)
            )

            if materiale:
                material_selectat.options = [
                    ft.dropdown.Option(
                        key=str(m["id"]),
                        text=f'{m["cod"] or "Fără cod"} — {m["denumire"]}',
                    )
                    for m in materiale
                ]
                material_selectat.hint_text = "Selectează un material"
            else:
                material_selectat.hint_text = (
                    "Nu există materiale în această gestiune"
                )

        actualizeaza_stoc()
        incarca_istoric()
        page.update()

    def la_schimbarea_materialului(e):
        actualizeaza_stoc()
        incarca_istoric()
        mesaj.value = ""
        page.update()

    def salveaza_operatiune(e):
        if not material_selectat.value:
            mesaj.value = "Selectează un material."
            mesaj.color = ft.Colors.RED
            page.update()
            return

        try:
            cantitate = float(
                (cantitate_input.value or "").replace(",", ".")
            )

            if not data_input.value:
                raise ValueError("Data și ora sunt obligatorii.")

            datetime.strptime(
                data_input.value,
                "%Y-%m-%d %H:%M:%S",
            )

            if tip_operatiune.value == "INTRARE":
                inregistreaza_intrare(
                    material_id=int(material_selectat.value),
                    cantitate=cantitate,
                    data_operatiunii=data_input.value,
                    observatii=observatii_input.value or None,
                )
            else:
                inregistreaza_iesire(
                    material_id=int(material_selectat.value),
                    cantitate=cantitate,
                    data_operatiunii=data_input.value,
                    observatii=observatii_input.value or None,
                )

            mesaj.value = "Operațiunea a fost înregistrată."
            mesaj.color = ft.Colors.GREEN

            cantitate_input.value = ""
            observatii_input.value = ""

            actualizeaza_stoc()
            incarca_istoric()

        except ValueError as eroare:
            mesaj.value = str(eroare)
            mesaj.color = ft.Colors.RED

        except Exception as eroare:
            mesaj.value = (
                f"Nu s-a putut înregistra operațiunea: {eroare}"
            )
            mesaj.color = ft.Colors.RED

        page.update()

    gestiune_selectata.on_change = incarca_materiale
    material_selectat.on_change = la_schimbarea_materialului

    # Încarcă materialele imediat la deschiderea ecranului.
    if gestiuni:
        materiale_initiale = lista_materiale(
            int(gestiune_selectata.value)
        )

        material_selectat.options = [
            ft.dropdown.Option(
                key=str(m["id"]),
                text=f'{m["cod"] or "Fără cod"} — {m["denumire"]}',
            )
            for m in materiale_initiale
        ]

        if not materiale_initiale:
            material_selectat.hint_text = (
                "Nu există materiale în această gestiune"
            )
    else:
        material_selectat.hint_text = "Adaugă mai întâi o gestiune"

    incarca_istoric()

    return ft.Column(
        controls=[
            ft.Text(
                "Operațiuni de stoc",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text(
                "Înregistrează intrări și ieșiri și consultă istoricul."
            ),
            ft.Divider(),
            gestiune_selectata,
            material_selectat,
            stoc_text,
            ft.Divider(),
            ft.Text(
                "Operațiune nouă",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
            tip_operatiune,
            cantitate_input,
            data_input,
            observatii_input,
            ft.Button(
                "Înregistrează operațiunea",
                icon=ft.Icons.SAVE,
                on_click=salveaza_operatiune,
            ),
            mesaj,
            ft.Divider(),
            ft.Text(
                "Istoric",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
            lista_istoric,
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
