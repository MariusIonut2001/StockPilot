
import flet as ft

from screens.gestiuni_screen import gestiuni_screen


def main(page: ft.Page):
    page.title = "StockPilot"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    page.add(
        gestiuni_screen(page)
    )


ft.run(main)
