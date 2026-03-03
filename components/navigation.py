import flet as ft
from theme.app_theme import AppColors, AppStyle


def create_navigation_rail(
    selected_index: int,
    on_change,
    on_theme_toggle,
    is_dark: bool,
) -> ft.Container:
    """Cria a barra de navegação lateral."""

    nav_items = [
        {"icon": ft.Icons.DASHBOARD_ROUNDED, "label": "Dashboard"},
        {"icon": ft.Icons.SWAP_HORIZ_ROUNDED, "label": "Transações"},
        {"icon": ft.Icons.CATEGORY_ROUNDED, "label": "Categorias"},
        {"icon": ft.Icons.BAR_CHART_ROUNDED, "label": "Relatórios"},
    ]

    def build_nav_button(index: int, icon, label: str):
        is_selected = index == selected_index
        bg = AppColors.PRIMARY if is_selected else "transparent"
        icon_color = "#FFFFFF" if is_selected else (AppColors.DARK_TEXT_SECONDARY if is_dark else AppColors.LIGHT_TEXT_SECONDARY)

        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, color=icon_color, size=24),
                    ft.Text(label, size=10, color=icon_color, weight=ft.FontWeight.W_500),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            ),
            width=64,
            height=64,
            border_radius=AppStyle.BORDER_RADIUS_SM,
            bgcolor=bg,
            alignment=ft.Alignment.CENTER,
            on_click=lambda e, idx=index: on_change(idx),
            animate=ft.Animation(AppStyle.ANIMATION_DURATION, ft.AnimationCurve.EASE_IN_OUT),
            ink=True,
        )

    nav_buttons = [build_nav_button(i, item["icon"], item["label"]) for i, item in enumerate(nav_items)]

    theme_icon = ft.Icons.LIGHT_MODE_ROUNDED if is_dark else ft.Icons.DARK_MODE_ROUNDED
    theme_color = AppColors.DARK_TEXT_SECONDARY if is_dark else AppColors.LIGHT_TEXT_SECONDARY

    theme_button = ft.IconButton(
        icon=theme_icon,
        icon_color=theme_color,
        icon_size=22,
        on_click=on_theme_toggle,
        tooltip="Alternar tema",
    )

    bg_color = AppColors.DARK_SURFACE if is_dark else AppColors.LIGHT_SURFACE
    border_color = AppColors.DARK_BORDER if is_dark else AppColors.LIGHT_BORDER

    return ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Text(
                        "₿",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=AppColors.PRIMARY,
                    ),
                    alignment=ft.Alignment.CENTER,
                    height=60,
                ),
                ft.Divider(height=1, color=border_color),
                ft.Column(
                    nav_buttons,
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                ),
                ft.Divider(height=1, color=border_color),
                ft.Container(
                    content=theme_button,
                    alignment=ft.Alignment.CENTER,
                    height=50,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        width=AppStyle.NAV_WIDTH,
        bgcolor=bg_color,
        border=ft.border.only(right=ft.BorderSide(1, border_color)),
        padding=ft.padding.symmetric(vertical=10, horizontal=8),
        animate=ft.Animation(AppStyle.ANIMATION_DURATION, ft.AnimationCurve.EASE_IN_OUT),
    )
