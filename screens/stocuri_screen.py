
import flet as ft
from datetime import datetime

from services.gestiuni_service import lista_gestiuni
from services.materiale_service import lista_materiale
from services.operatiuni_service import (
    stoc_scriptic,
    inregistreaza_ajustare,
)
from services.inventariere_service import (
    lista_inventarieri,
    inregistreaza_inventariere,
)


def stocuri_screen(page: ft.Page):
    gestiuni = lista_gestiuni()

    material_selectat = None

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
            ft.dropdown.Option(key="TOATE", text="Toate materialele"),
            ft.dropdown.Option(key="CU_STOC", text="Doar materiale cu stoc pozitiv"),
            ft.dropdown.Option(key="FARA_STOC", text="Materiale fără stoc"),
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

    # FORMULAR INVENTARIERE

    titlu_inventariere = ft.Text(
        "Înregistrare inventariere",
        size=18,
        weight=ft.FontWeight.BOLD,
    )

    material_inventariere_text = ft.Text()

    cantitate_faptica = ft.TextField(
        label="Cantitate constatată fizic",
        hint_text="Introdu cantitatea găsită",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=250,
    )

    data_inventarierii = ft.TextField(
        label="Data inventarierii",
        hint_text="YYYY-MM-DD HH:MM:SS",
        width=250,
    )

    def completeaza_data_curenta(e=None):
        data_inventarierii.value = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        page.update()

    observatii = ft.TextField(
        label="Observații (opțional)",
        multiline=True,
        min_lines=2,
        max_lines=3,
    )

    mesaj_inventariere = ft.Text()

    def inchide_formular():
        nonlocal material_selectat

        material_selectat = None
        formular_inventariere.visible = False
        mesaj_inventariere.value = ""
        page.update()

    def deschide_formular(material):
        nonlocal material_selectat

        material_selectat = material

        material_inventariere_text.value = (
            f'{material["denumire"]} — {material["cod"]} '
            f'({material["unitate"]})'
        )

        cantitate_faptica.value = ""
        data_inventarierii.value = ""
        observatii.value = ""
        mesaj_inventariere.value = ""

        formular_inventariere.visible = True
        page.update()

    def salveaza_inventarierea(e=None):
        nonlocal material_selectat

        if material_selectat is None:
            return

        try:
            if not cantitate_faptica.value.strip():
                raise ValueError(
                    "Introdu cantitatea constatată fizic."
                )

            cantitate = float(
                cantitate_faptica.value.replace(",", ".")
            )

            data = data_inventarierii.value.strip() or None

            inregistreaza_inventariere(
                material_id=material_selectat["id"],
                cantitate_faptica=cantitate,
                data_inventarierii=data,
                observatii=observatii.value,
            )

            material_selectat = None
            formular_inventariere.visible = False

            mesaj_inventariere.value = (
                "Inventarierea a fost înregistrată."
            )
            mesaj_inventariere.color = ft.Colors.GREEN

            cauta_materiale()

        except (ValueError, TypeError) as eroare:
            mesaj_inventariere.value = str(eroare)
            mesaj_inventariere.color = ft.Colors.RED
            page.update()

        except Exception as eroare:
            mesaj_inventariere.value = f"Eroare: {eroare}"
            mesaj_inventariere.color = ft.Colors.RED
            page.update()

    formular_inventariere = ft.Container(
        visible=False,
        padding=15,
        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=10,
        content=ft.Column(
            controls=[
                titlu_inventariere,
                material_inventariere_text,
                cantitate_faptica,
                ft.Row(
                    controls=[
                        data_inventarierii,
                        ft.Button(
                            "Data de azi",
                            icon=ft.Icons.CALENDAR_TODAY,
                            on_click=completeaza_data_curenta,
                        ),
                    ],
                    wrap=True,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                observatii,
                ft.Row(
                    controls=[
                        ft.Button(
                            "Salvează inventarierea",
                            icon=ft.Icons.SAVE,
                            on_click=salveaza_inventarierea,
                        ),
                        ft.TextButton(
                            "Anulează",
                            on_click=lambda e: inchide_formular(),
                        ),
                    ],
                    wrap=True,
                ),
                mesaj_inventariere,
            ],
            spacing=10,
        ),
    )

    # CONSTRUIRE RÂND DIN ISTORICUL INVENTARIERILOR

    def construieste_rand_inventariere(inventariere):
        diferenta_initiala = float(inventariere["diferenta"])
        inventariere_id = inventariere["id"]
        ajustare_id = inventariere.get("ajustare_id")

        # După aplicarea ajustării, diferența afișată devine zero.
        diferenta = (
            0 if ajustare_id is not None else diferenta_initiala
        )

        motiv_ajustare = ft.TextField(
            label="Motivul ajustării",
            hint_text="Explică motivul diferenței",
            multiline=True,
            min_lines=2,
            max_lines=3,
        )

        mesaj_ajustare = ft.Text()

        formular_ajustare = ft.Container(
            visible=False,
            content=ft.Column(
                controls=[
                    motiv_ajustare,
                    ft.Button(
                        "Confirmă ajustarea",
                        icon=ft.Icons.CHECK,
                        on_click=lambda e, iid=inventariere_id:
                            aplica_ajustarea(iid),
                    ),
                    mesaj_ajustare,
                ],
                spacing=8,
            ),
        )

        def aplica_ajustarea(iid):
            try:
                motiv = (motiv_ajustare.value or "").strip()

                if not motiv:
                    raise ValueError(
                        "Motivul ajustării este obligatoriu."
                    )

                inregistreaza_ajustare(
                    inventariere_id=iid,
                    motiv=motiv,
                )

                cauta_materiale()

            except (ValueError, TypeError) as eroare:
                mesaj_ajustare.value = str(eroare)
                mesaj_ajustare.color = ft.Colors.RED
                page.update()

            except Exception as eroare:
                mesaj_ajustare.value = f"Eroare: {eroare}"
                mesaj_ajustare.color = ft.Colors.RED
                page.update()

        def arata_formular_ajustare(e=None):
            formular_ajustare.visible = not formular_ajustare.visible
            page.update()

        if diferenta > 0:
            diferenta_text = f"+{diferenta:g}"
            diferenta_color = ft.Colors.GREEN
        elif diferenta < 0:
            diferenta_text = f"{diferenta:g}"
            diferenta_color = ft.Colors.RED
        else:
            diferenta_text = "0"
            diferenta_color = ft.Colors.GREY

        controale_ajustare = []

        if ajustare_id is not None:
            controale_ajustare.append(
                ft.Text(
                    f"Ajustare aplicată (mișcare #{ajustare_id})",
                    color=ft.Colors.GREEN,
                    weight=ft.FontWeight.BOLD,
                    size=12,
                )
            )

        elif diferenta == 0:
            controale_ajustare.append(
                ft.Text(
                    "Fără diferențe – nu este necesară ajustarea.",
                    color=ft.Colors.GREY,
                    size=12,
                )
            )

        else:
            controale_ajustare.extend([
                ft.Button(
                    "Aplică ajustarea",
                    icon=ft.Icons.BALANCE,
                    on_click=arata_formular_ajustare,
                ),
                formular_ajustare,
            ])

        continut = [
            ft.Text(
                f'Data: {inventariere["data_inventarierii"]}',
                weight=ft.FontWeight.BOLD,
            ),
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text("Scriptic", size=11),
                            ft.Text(
                                f'{inventariere["cantitate_scriptica"]:g}',
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text("Faptic", size=11),
                            ft.Text(
                                f'{inventariere["cantitate_faptica"]:g}',
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text("Diferență", size=11),
                            ft.Text(
                                diferenta_text,
                                weight=ft.FontWeight.BOLD,
                                color=diferenta_color,
                            ),
                        ],
                        spacing=2,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        ]

        if inventariere.get("observatii"):
            continut.append(
                ft.Text(
                    f'Observații: {inventariere["observatii"]}',
                    size=12,
                )
            )

        continut.extend(controale_ajustare)

        return ft.Container(
            content=ft.Column(
                controls=continut,
                spacing=8,
            ),
            padding=10,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=8,
        )

    # CĂUTARE ȘI AFIȘARE MATERIALE

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

            inventarieri = lista_inventarieri()

            inventarieri_materiale = {}
            ultima_inventariere = {}

            for inventariere in inventarieri:
                material_id = inventariere["material_id"]

                if material_id not in inventarieri_materiale:
                    inventarieri_materiale[material_id] = []

                inventarieri_materiale[material_id].append(
                    inventariere
                )

                if material_id not in ultima_inventariere:
                    ultima_inventariere[material_id] = inventariere

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

                inventariere = ultima_inventariere.get(
                    material["id"]
                )

                if inventariere:
                    faptic = inventariere["cantitate_faptica"]
                    ajustare_id = inventariere.get("ajustare_id")

                    if ajustare_id is not None:
                        diferenta = 0
                    else:
                        diferenta = inventariere["diferenta"]

                    data = inventariere["data_inventarierii"]

                else:
                    faptic = None
                    diferenta = None
                    data = None
                    ajustare_id = None

                rezultate.append({
                    "id": material["id"],
                    "cod": material.get("cod") or "Fără cod",
                    "denumire": material["denumire"],
                    "unitate": material["unitate"],
                    "stoc": stoc,
                    "faptic": faptic,
                    "diferenta": diferenta,
                    "data": data,
                    "ajustare_id": ajustare_id,
                })

            total_text.value = f"Rezultate găsite: {len(rezultate)}"

            if not rezultate:
                mesaj.value = (
                    "Nu am găsit materiale pentru criteriile selectate."
                )
                mesaj.color = ft.Colors.SECONDARY

            for material in rezultate:
                if material["faptic"] is None:
                    faptic_text = "Neinventariat"
                    diferenta_text = "—"
                    diferenta_color = ft.Colors.GREY
                    data_text = "Nu există inventariere"

                else:
                    faptic_text = f'{material["faptic"]:g}'
                    diferenta_text = f'{material["diferenta"]:+g}'

                    if material["diferenta"] > 0:
                        diferenta_color = ft.Colors.GREEN
                    elif material["diferenta"] < 0:
                        diferenta_color = ft.Colors.RED
                    else:
                        diferenta_color = ft.Colors.GREY

                    data_text = (
                        f'Ultima inventariere: {material["data"]}'
                    )

                istoric_material = inventarieri_materiale.get(
                    material["id"],
                    [],
                )

                randuri_istoric = [
                    construieste_rand_inventariere(inv)
                    for inv in istoric_material
                ]

                continut_istoric = ft.Column(
                    controls=randuri_istoric or [
                        ft.Text("Nu există inventarieri înregistrate.")
                    ],
                    spacing=8,
                )

                container_istoric = ft.Container(
                    visible=False,
                    content=continut_istoric,
                )

                def comuta_istoric(e=None, container=container_istoric):
                    container.visible = not container.visible
                    page.update()

                lista.controls.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
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
                                        ft.Button(
                                            "Inventariază",
                                            icon=ft.Icons.FACT_CHECK,
                                            on_click=lambda e, m=material:
                                                deschide_formular(m),
                                        ),
                                    ],
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),

                                ft.Divider(height=1),

                                ft.Row(
                                    controls=[
                                        ft.Column(
                                            controls=[
                                                ft.Text("Scriptic", size=11),
                                                ft.Text(
                                                    f'{material["stoc"]:g}',
                                                    size=19,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                            ],
                                            spacing=2,
                                        ),
                                        ft.Column(
                                            controls=[
                                                ft.Text("Faptic", size=11),
                                                ft.Text(
                                                    faptic_text,
                                                    size=19,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                            ],
                                            spacing=2,
                                        ),
                                        ft.Column(
                                            controls=[
                                                ft.Text("Diferență", size=11),
                                                ft.Text(
                                                    diferenta_text,
                                                    size=19,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=diferenta_color,
                                                ),
                                            ],
                                            spacing=2,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),

                                ft.Text(
                                    data_text,
                                    size=11,
                                    color=ft.Colors.GREY_600,
                                ),

                                ft.Divider(height=1),

                                ft.TextButton(
                                    "Vezi istoricul inventarierilor",
                                    icon=ft.Icons.HISTORY,
                                    on_click=comuta_istoric,
                                ),

                                container_istoric,
                            ],
                            spacing=8,
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
                "Stoc scriptic, stoc faptic și diferențe pentru fiecare material."
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
            formular_inventariere,
            ft.Divider(),
            total_text,
            mesaj,
            lista,
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
