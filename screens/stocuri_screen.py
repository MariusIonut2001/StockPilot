
import flet as ft

from services.gestiuni_service import lista_gestiuni
from services.materiale_service import lista_materiale
from services.operatiuni_service import stoc_scriptic


def stocuri_screen(page: ft.Page):
    gestiuni = lista_gestiuni()

    gestiune_selectata = ft.Dropdown(
        label="Selectează gestiunea",
        hint_text="Alege gestiunea",
        options=[
            ft.dropdown.Option(
                key=str(g["id"]),
                text=f'{g["cod"]} — {g["denumire"]}',
            )
            for g in gestiuni
        ],
        width=400,
    )

    tip_materiale = ft.Dropdown(
        label="Tip de materiale",
        value="TOATE",
        options=[
            ft.dropdown.Option(
                key="TOATE",
                text="Toate materialele",
            ),
            ft.dropdown.Option(
                key="CU_STOC",
                text="Doar materiale cu stoc pozitiv",
            ),
            ft.dropdown.Option(
                key="FARA_STOC",
                text="Materiale fără stoc",
            ),
        ],
        width=400,
    )

    cautare = ft.TextField(
        label="Cod sau denumire (opțional)",
        hint_text="Ex. MAT-001 sau Șurub",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
    )

    lista = ft.Column(spacing=8)
    mesaj = ft.Text()
    total_text = ft.Text()

    def cauta_materiale(e=None):
        lista.controls.clear()
        mesaj.value = ""
        total_text.value = ""

        if not gestiune_selectata.value:
            mesaj.value = "Selectează mai întâi o gestiune."
            mesaj.color = ft.Colors.RED
            page.update()
            return

        try:
            materiale = lista_materiale(
                int(gestiune_selectata.value)
            )

            rezultate = []
            termen = (cautare.value or "").strip().casefold()

            for material in materiale:
                text_material = (
                    f'{material.get("cod") or ""} '
                    f'{material["denumire"]}'
                ).casefold()

                if termen and termen not in text_material:
                    continue

                stoc = stoc_scriptic(material["id"])

                if tip_materiale.value == "CU_STOC" and stoc <= 0:
                    continue

                if tip_materiale.value == "FARA_STOC" and stoc > 0:
                    continue

                rezultate.append({
                    "cod": material.get("cod") or "Fără cod",
                    "denumire": material["denumire"],
                    "unitate": material["unitate"],
                    "stoc": stoc,
                })

            total_text.value = (
                f"Rezultate găsite: {len(rezultate)}"
            )

            if not rezultate:
                mesaj.value = (
                    "Nu am găsit materiale pentru criteriile selectate."
                )
                mesaj.color = ft.Colors.SECONDARY
            else:
                for material in rezultate:
                    lista.controls.append(
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                material["denumire"],
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            ft.Text(
                                                f'{material["cod"]} · '
                                                f'{material["unitate"]}',
                                                size=12,
                                                color=ft.Colors.GREY_600,
                                            ),
                                        ],
                                        expand=True,
                                        spacing=4,
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                "Stoc scriptic",
                                                size=11,
                                            ),
                                            ft.Text(
                                                f'{material["stoc"]:g}',
                                                size=22,
                                                weight=ft.FontWeight.BOLD,
                                                color=(
                                                    ft.Colors.ORANGE
                                                    if material["stoc"] <= 0
                                                    else ft.Colors.GREEN
                                                ),
                                            ),
                                        ],
                                        spacing=3,
                                        horizontal_alignment=(
                                            ft.CrossAxisAlignment.END
                                        ),
                                    ),
                                ],
                                vertical_alignment=(
                                    ft.CrossAxisAlignment.CENTER
                                ),
                            ),
                            padding=12,
                            border=ft.Border.all(
                                1,
                                ft.Colors.OUTLINE_VARIANT,
                            ),
                            border_radius=10,
                        )
                    )

        except Exception as eroare:
            mesaj.value = f"Eroare la căutare: {eroare}"
            mesaj.color = ft.Colors.RED

        page.update()

    return ft.Column(
        controls=[
            ft.Text(
                "Stocuri",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text(
                "Selectează criteriile și caută materialele din gestiune."
            ),
            ft.Divider(),
            gestiune_selectata,
            tip_materiale,
            cautare,
            ft.Button(
                "Caută materiale",
                icon=ft.Icons.SEARCH,
                on_click=cauta_materiale,
            ),
            ft.Divider(),
            total_text,
            mesaj,
            lista,
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
