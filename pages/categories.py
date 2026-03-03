import flet as ft
from theme.app_theme import AppColors, AppStyle
from models.data_model import FinanceData, Category


# Ícones disponíveis para categorias
AVAILABLE_ICONS = {
    "restaurant": ft.Icons.RESTAURANT_ROUNDED,
    "directions_car": ft.Icons.DIRECTIONS_CAR_ROUNDED,
    "home": ft.Icons.HOME_ROUNDED,
    "local_hospital": ft.Icons.LOCAL_HOSPITAL_ROUNDED,
    "school": ft.Icons.SCHOOL_ROUNDED,
    "sports_esports": ft.Icons.SPORTS_ESPORTS_ROUNDED,
    "shopping_cart": ft.Icons.SHOPPING_CART_ROUNDED,
    "receipt_long": ft.Icons.RECEIPT_LONG_ROUNDED,
    "work": ft.Icons.WORK_ROUNDED,
    "computer": ft.Icons.COMPUTER_ROUNDED,
    "trending_up": ft.Icons.TRENDING_UP_ROUNDED,
    "card_giftcard": ft.Icons.CARD_GIFTCARD_ROUNDED,
    "attach_money": ft.Icons.ATTACH_MONEY_ROUNDED,
    "money_off": ft.Icons.MONEY_OFF_ROUNDED,
    "category": ft.Icons.CATEGORY_ROUNDED,
    "flight": ft.Icons.FLIGHT_ROUNDED,
    "pets": ft.Icons.PETS_ROUNDED,
    "fitness_center": ft.Icons.FITNESS_CENTER_ROUNDED,
    "movie": ft.Icons.MOVIE_ROUNDED,
    "music_note": ft.Icons.MUSIC_NOTE_ROUNDED,
    "phone": ft.Icons.PHONE_ROUNDED,
    "wifi": ft.Icons.WIFI_ROUNDED,
    "local_cafe": ft.Icons.LOCAL_CAFE_ROUNDED,
    "local_gas_station": ft.Icons.LOCAL_GAS_STATION_ROUNDED,
}

AVAILABLE_COLORS = [
    "#FF5252", "#FF6B6B", "#FF9800", "#FFC107",
    "#4CAF50", "#00C853", "#2196F3", "#3F51B5",
    "#9C27B0", "#E91E63", "#00BCD4", "#607D8B",
    "#795548", "#F44336", "#FF5722", "#9E9E9E",
]


def build_categories_page(
    data: FinanceData,
    is_dark: bool,
    page: ft.Page,
    on_refresh=None,
) -> ft.Container:
    """Constrói a página de Categorias."""

    text_color = AppColors.DARK_TEXT if is_dark else AppColors.LIGHT_TEXT
    sub_color = AppColors.DARK_TEXT_SECONDARY if is_dark else AppColors.LIGHT_TEXT_SECONDARY
    bg_color = AppColors.DARK_BG if is_dark else AppColors.LIGHT_BG
    card_bg = AppColors.DARK_CARD if is_dark else AppColors.LIGHT_CARD
    border_color = AppColors.DARK_BORDER if is_dark else AppColors.LIGHT_BORDER
    input_bg = AppColors.DARK_SURFACE if is_dark else AppColors.LIGHT_BG

    def open_category_dialog(cat_id=None):
        editing = cat_id is not None
        cat = data.get_category_by_id(cat_id) if editing else None

        name_field = ft.TextField(
            label="Nome",
            value=cat.name if cat else "",
            border_radius=AppStyle.BORDER_RADIUS_SM,
            bgcolor=input_bg,
            border_color=border_color,
            label_style=ft.TextStyle(color=sub_color),
            color=text_color,
            focused_border_color=AppColors.PRIMARY,
        )

        type_dropdown = ft.Dropdown(
            label="Tipo",
            value=cat.type if cat else "despesa",
            options=[
                ft.dropdown.Option("receita", "Receita"),
                ft.dropdown.Option("despesa", "Despesa"),
            ],
            border_radius=AppStyle.BORDER_RADIUS_SM,
            bgcolor=input_bg,
            border_color=border_color,
            label_style=ft.TextStyle(color=sub_color),
            color=text_color,
            focused_border_color=AppColors.PRIMARY,
        )

        selected_icon = {"value": cat.icon if cat else "category"}
        selected_color = {"value": cat.color if cat else "#6C63FF"}

        # Grid de ícones
        icon_grid_items = []
        for icon_name, icon_ref in AVAILABLE_ICONS.items():
            is_sel = icon_name == selected_icon["value"]
            icon_grid_items.append(
                ft.Container(
                    content=ft.Icon(icon_ref, color="#FFFFFF" if is_sel else sub_color, size=20),
                    width=40,
                    height=40,
                    border_radius=8,
                    bgcolor=AppColors.PRIMARY if is_sel else "transparent",
                    border=ft.Border.all(1, AppColors.PRIMARY if is_sel else border_color),
                    alignment=ft.Alignment.CENTER,
                    on_click=lambda e, name=icon_name: select_icon(name),
                    data=icon_name,
                )
            )

        icon_grid = ft.Container(
            content=ft.Row(icon_grid_items, wrap=True, spacing=6, run_spacing=6),
            height=130,
            padding=5,
        )

        # Grid de cores
        color_grid_items = []
        for color in AVAILABLE_COLORS:
            is_sel = color == selected_color["value"]
            color_grid_items.append(
                ft.Container(
                    width=32,
                    height=32,
                    border_radius=8,
                    bgcolor=color,
                    border=ft.Border.all(3 if is_sel else 0, "#FFFFFF"),
                    on_click=lambda e, c=color: select_color(c),
                    shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.3, color)) if is_sel else None,
                )
            )

        color_grid = ft.Row(color_grid_items, wrap=True, spacing=6, run_spacing=6)

        def select_icon(name):
            selected_icon["value"] = name
            # Rebuild icon grid
            for item in icon_grid_items:
                is_s = item.data == name
                item.bgcolor = AppColors.PRIMARY if is_s else "transparent"
                item.border = ft.Border.all(1, AppColors.PRIMARY if is_s else border_color)
                item.content.color = "#FFFFFF" if is_s else sub_color
            page.update()

        def select_color(color):
            selected_color["value"] = color
            for i, c in enumerate(AVAILABLE_COLORS):
                is_s = c == color
                color_grid_items[i].border = ft.Border.all(3 if is_s else 0, "#FFFFFF")
                color_grid_items[i].shadow = (
                    ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.3, c)) if is_s else None
                )
            page.update()

        error_text = ft.Text("", color=AppColors.EXPENSE, size=12, visible=False)

        def save_category(e):
            if not name_field.value or not name_field.value.strip():
                error_text.value = "Preencha o nome da categoria."
                error_text.visible = True
                page.update()
                return

            if editing:
                data.update_category(
                    cat_id,
                    name=name_field.value.strip(),
                    type=type_dropdown.value,
                    icon=selected_icon["value"],
                    color=selected_color["value"],
                )
            else:
                new_cat = Category(
                    name=name_field.value.strip(),
                    type=type_dropdown.value,
                    icon=selected_icon["value"],
                    color=selected_color["value"],
                )
                data.add_category(new_cat)

            dialog.open = False
            page.update()
            if on_refresh:
                on_refresh()

        def close_dialog(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Editar Categoria" if editing else "Nova Categoria",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=text_color,
            ),
            bgcolor=card_bg,
            content=ft.Container(
                content=ft.Column(
                    [
                        name_field,
                        type_dropdown,
                        ft.Text("Ícone", size=13, color=sub_color, weight=ft.FontWeight.W_500),
                        icon_grid,
                        ft.Text("Cor", size=13, color=sub_color, weight=ft.FontWeight.W_500),
                        color_grid,
                        error_text,
                    ],
                    spacing=12,
                    tight=True,
                ),
                width=420,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.Button(
                    "Salvar",
                    on_click=save_category,
                    bgcolor=AppColors.PRIMARY,
                    color="#FFFFFF",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=AppStyle.BORDER_RADIUS_SM),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def on_delete_category(cat_id):
        def confirm_delete(e):
            data.delete_category(cat_id)
            confirm_dialog.open = False
            page.update()
            if on_refresh:
                on_refresh()

        def cancel_delete(e):
            confirm_dialog.open = False
            page.update()

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Exclusão", color=text_color),
            content=ft.Text(
                "Tem certeza que deseja excluir esta categoria?\nTransações associadas não serão excluídas.",
                color=sub_color,
            ),
            bgcolor=card_bg,
            actions=[
                ft.TextButton("Cancelar", on_click=cancel_delete),
                ft.Button(
                    "Excluir",
                    on_click=confirm_delete,
                    bgcolor=AppColors.EXPENSE,
                    color="#FFFFFF",
                ),
            ],
        )
        page.overlay.append(confirm_dialog)
        confirm_dialog.open = True
        page.update()

    # ─── Categorias de Receita ─────────────────────────────────────────

    def build_category_card(cat: Category) -> ft.Container:
        icon_ref = AVAILABLE_ICONS.get(cat.icon, ft.Icons.CATEGORY_ROUNDED)
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icon_ref, color="#FFFFFF", size=20),
                        width=40,
                        height=40,
                        border_radius=10,
                        bgcolor=cat.color,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Text(cat.name, size=14, color=text_color, weight=ft.FontWeight.W_500, expand=True),
                    ft.Container(
                        content=ft.Text(
                            "Receita" if cat.type == "receita" else "Despesa",
                            size=11,
                            color="#FFFFFF",
                        ),
                        bgcolor=AppColors.INCOME if cat.type == "receita" else AppColors.EXPENSE,
                        border_radius=6,
                        padding=ft.Padding(8, 3, 8, 3),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT_ROUNDED,
                        icon_color=sub_color,
                        icon_size=18,
                        on_click=lambda e, cid=cat.id: open_category_dialog(cid),
                        tooltip="Editar",
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                        icon_color=AppColors.EXPENSE,
                        icon_size=18,
                        on_click=lambda e, cid=cat.id: on_delete_category(cid),
                        tooltip="Excluir",
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
            padding=ft.Padding(16, 10, 16, 10),
            border_radius=AppStyle.BORDER_RADIUS_SM,
            bgcolor=card_bg,
            border=ft.Border.all(1, border_color),
        )

    income_cats = [build_category_card(c) for c in data.get_categories_by_type("receita")]
    expense_cats = [build_category_card(c) for c in data.get_categories_by_type("despesa")]

    fab = ft.FloatingActionButton(
        icon=ft.Icons.ADD_ROUNDED,
        bgcolor=AppColors.PRIMARY,
        foreground_color="#FFFFFF",
        on_click=lambda e: open_category_dialog(),
        tooltip="Nova Categoria",
    )

    return ft.Stack(
        [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Categorias", size=28, weight=ft.FontWeight.BOLD, color=text_color),
                        ft.Text(
                            f"{len(data.categories)} categorias",
                            size=14,
                            color=sub_color,
                        ),
                        ft.Container(height=10),

                        # Receitas
                        ft.Text("💰 Receitas", size=18, weight=ft.FontWeight.W_600, color=AppColors.INCOME),
                        ft.Column(income_cats if income_cats else [
                            ft.Text("Nenhuma categoria de receita", size=13, color=sub_color)
                        ], spacing=6),
                        ft.Container(height=16),

                        # Despesas
                        ft.Text("💸 Despesas", size=18, weight=ft.FontWeight.W_600, color=AppColors.EXPENSE),
                        ft.Column(expense_cats if expense_cats else [
                            ft.Text("Nenhuma categoria de despesa", size=13, color=sub_color)
                        ], spacing=6),
                    ],
                    spacing=6,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                padding=AppStyle.PAGE_PADDING,
                expand=True,
                bgcolor=bg_color,
            ),
            ft.Container(
                content=fab,
                alignment=ft.Alignment.BOTTOM_RIGHT,
                padding=30,
            ),
        ],
        expand=True,
    )
