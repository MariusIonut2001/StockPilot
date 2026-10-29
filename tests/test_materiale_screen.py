
import flet as ft

from screens.materiale_screen import materiale_screen


def main(page: ft.Page):
    page.title = "StockPilot - Test materiale"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.add(materiale_screen(page))


ft.run(main)
