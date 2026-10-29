
import flet as ft

from screens.operatiuni_screen import operatiuni_screen


def main(page: ft.Page):
    page.title = "StockPilot - Test operațiuni"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.add(operatiuni_screen(page))


ft.run(main)
