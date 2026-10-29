
import flet as ft

from services.gestiuni_service import lista_gestiuni
from services.materiale_service import adauga_material, lista_materiale
from services.unitati_service import lista_unitati


def materiale_screen(page: ft.Page):
    gestiuni = lista_gestiuni()
    unitati = lista_unitati()

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
        width=350,
    )

    cod_input = ft.TextField(
        label="Cod material (opțional)",
        hint_text="Ex. MAT-001",
        expand=True,
    )

    denumire_input = ft.TextField(
        label="Denumire material",
        hint_text="Ex. Șurub M8",
        expand=True,
    )

    unitate_selectata = ft.Dropdown(
        label="Unitate de măsură",
        hint_text="Selectează unitatea",
        options=[
            ft.dropdown.Option(
                key=str(u["id"]),
                text=u["denumire"],
            )
            for u in unitati
        ],
        width=250,
    )

    lista = ft.Column(spacing=8)
    mesaj = ft.Text()

    def incarca_materiale():
        lista.controls.clear()

        if not gestiuni:
            lista.controls.append(
                ft.Text(
                    "Nu există gestiuni active. "
                    "Adaugă mai întâi o gestiune în secțiunea Gestiuni."
                )
            )
            return

        if not gestiune_selectata.value:
            lista.controls.append(
                ft.Text("Selectează o gestiune pentru a vedea materialele.")
            )
            return

        materiale = lista_materiale(
            int(gestiune_selectata.value)
        )

        if not materiale:
            lista.controls.append(
                ft.Text("Nu există materiale în această gestiune.")
            )
            return

        for material in materiale:
            lista.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                material["cod"] or "Fără cod",
                                width=110,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                material["denumire"],
                                expand=True,
                            ),
                            ft.Text(
                                material["unitate"],
                                width=100,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=12,
                    border=ft.Border.all(
                        1,
                        ft.Colors.OUTLINE_VARIANT,
                    ),
                    border_radius=10,
                )
            )

    def la_schimbarea_gestiunii(e):
        mesaj.value = ""
        incarca_materiale()
        page.update()

    def salveaza_material(e):
        if not gestiune_selectata.value:
            mesaj.value = "Selectează mai întâi o gestiune."
            mesaj.color = ft.Colors.RED
            page.update()
            return

        if not denumire_input.value or not denumire_input.value.strip():
            mesaj.value = "Introdu denumirea materialului."
            mesaj.color = ft.Colors.RED
            page.update()
            return

        if not unitate_selectata.value:
            mesaj.value = "Selectează unitatea de măsură."
            mesaj.color = ft.Colors.RED
            page.update()
            return

        try:
            adauga_material(
                gestiune_id=int(gestiune_selectata.value),
                denumire=denumire_input.value,
                unitate_id=int(unitate_selectata.value),
                cod=cod_input.value or "",
            )

            mesaj.value = "Materialul a fost adăugat."
            mesaj.color = ft.Colors.GREEN

            cod_input.value = ""
            denumire_input.value = ""

            incarca_materiale()

        except ValueError as eroare:
            mesaj.value = str(eroare)
            mesaj.color = ft.Colors.RED

        except Exception as eroare:
            mesaj.value = f"Nu s-a putut salva materialul: {eroare}"
            mesaj.color = ft.Colors.RED

        page.update()

    gestiune_selectata.on_change = la_schimbarea_gestiunii

    # Încarcă lista imediat, folosind prima gestiune activă.
    incarca_materiale()

    return ft.Column(
        controls=[
            ft.Text(
                "Materiale",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text(
                "Adaugă și consultă materialele din fiecare gestiune."
            ),
            ft.Divider(),
            gestiune_selectata,
            ft.Divider(),
            ft.Text(
                "Material nou",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
            cod_input,
            denumire_input,
            unitate_selectata,
            ft.Button(
                "Adaugă material",
                icon=ft.Icons.ADD,
                on_click=salveaza_material,
            ),
            mesaj,
            ft.Divider(),
            ft.Text(
                "Materiale existente",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
            lista,
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
