
import flet as ft

from services.gestiuni_service import adauga_gestiune, lista_gestiuni


def gestiuni_screen(page: ft.Page):
    cod_input = ft.TextField(
        label="Cod gestiune",
        hint_text="Ex. 1201",
        width=220,
    )

    denumire_input = ft.TextField(
        label="Denumire gestiune",
        hint_text="Ex. Materiale uz generale",
        expand=True,
    )

    lista = ft.Column(spacing=8)
    mesaj = ft.Text()

    def incarca_gestiuni():
        lista.controls.clear()

        gestiuni = lista_gestiuni()

        if not gestiuni:
            lista.controls.append(
                ft.Text("Nu există gestiuni înregistrate.")
            )
        else:
            for gestiune in gestiuni:
                lista.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(
                                    gestiune["cod"],
                                    weight=ft.FontWeight.BOLD,
                                    width=90,
                                ),
                                ft.Text(
                                    gestiune["denumire"],
                                    expand=True,
                                ),
                            ],
                        ),
                        padding=12,
                        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                        border_radius=10,
                    )
                )

        page.update()

    def salveaza_gestiune(e):
        cod = cod_input.value or ""
        denumire = denumire_input.value or ""

        try:
            adauga_gestiune(cod, denumire)
            mesaj.value = "Gestiunea a fost adăugată."
            mesaj.color = ft.Colors.GREEN

            cod_input.value = ""
            denumire_input.value = ""

            incarca_gestiuni()

        except ValueError as eroare:
            mesaj.value = str(eroare)
            mesaj.color = ft.Colors.RED

        except Exception as eroare:
            if "UNIQUE constraint failed" in str(eroare):
                mesaj.value = "Există deja o gestiune cu acest cod."
            else:
                mesaj.value = f"Nu s-a putut salva gestiunea: {eroare}"

            mesaj.color = ft.Colors.RED

        page.update()

    incarca_gestiuni()
    return ft.Column(
        controls=[
            ft.Text("Gestiuni", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Adaugă și consultă gestiunile tale."),
            ft.Divider(),
            ft.Text("Gestiune nouă", size=18, weight=ft.FontWeight.BOLD),
            ft.Row(
                controls=[
                    cod_input,
                    denumire_input,
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            ft.Button(
                "Adaugă gestiune",
                icon=ft.Icons.ADD,
                on_click=salveaza_gestiune,
            ),
            mesaj,
            ft.Divider(),
            ft.Text("Gestiuni existente", size=18, weight=ft.FontWeight.BOLD),
            lista,
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
