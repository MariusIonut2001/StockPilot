
import flet as ft

from screens.gestiuni_screen import gestiuni_screen
from screens.materiale_screen import materiale_screen
from screens.operatiuni_screen import operatiuni_screen
from screens.stocuri_screen import stocuri_screen

def main(page: ft.Page):
    page.title = "StockPilot"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    continut = ft.Column(
        expand=True,
        spacing=12,
    )

    def afiseaza_gestiuni(e=None):
        continut.controls.clear()
        continut.controls.append(gestiuni_screen(page))
        page.update()

    def afiseaza_materiale(e=None):
        continut.controls.clear()
        continut.controls.append(materiale_screen(page))
        page.update()

    def afiseaza_operatiuni(e=None):
        continut.controls.clear()
        continut.controls.append(operatiuni_screen(page))
        page.update()

    def afiseaza_stocuri(e=None):
        continut.controls.clear()
        continut.controls.append(stocuri_screen(page))
        page.update()

    navigatie = ft.Row(
        controls=[
            ft.Button(
                "Gestiuni",
                icon=ft.Icons.WAREHOUSE,
                on_click=afiseaza_gestiuni,
            ),
            ft.Button(
                "Materiale",
                icon=ft.Icons.INVENTORY_2,
                on_click=afiseaza_materiale,
            ),
            ft.Button(
                "Operațiuni",
                icon=ft.Icons.SWAP_VERT,
                on_click=afiseaza_operatiuni,
            ),
            ft.Button(
                "Stocuri",
                icon=ft.Icons.INVENTORY,
                on_click=afiseaza_stocuri,
            ),
        ],
        wrap=True,
    )

    page.add(
        ft.Text(
            "StockPilot",
            size=30,
            weight=ft.FontWeight.BOLD,
        ),
        navigatie,
        ft.Divider(),
        continut,
    )

    afiseaza_gestiuni()


ft.run(main)
