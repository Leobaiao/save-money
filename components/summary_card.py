import flet as ft
from theme.app_theme import AppColors, AppStyle


def create_summary_card(
    title: str,
    value: str,
    icon: str,
    color: str,
    is_dark: bool,
) -> ft.Container:
    """Card de resumo financeiro (Saldo, Receita, Despesa)."""

    bg_color = AppColors.DARK_CARD if is_dark else AppColors.LIGHT_CARD
    text_color = AppColors.DARK_TEXT if is_dark else AppColors.LIGHT_TEXT
    sub_color = AppColors.DARK_TEXT_SECONDARY if is_dark else AppColors.LIGHT_TEXT_SECONDARY
    border_color = AppColors.DARK_BORDER if is_dark else AppColors.LIGHT_BORDER

    return ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Icon(icon, color="#FFFFFF", size=24),
                    width=48,
                    height=48,
                    border_radius=12,
                    bgcolor=color,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column(
                    [
                        ft.Text(title, size=13, color=sub_color, weight=ft.FontWeight.W_500),
                        ft.Text(
                            value,
                            size=22,
                            color=text_color,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    spacing=2,
                    expand=True,
                ),
            ],
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=AppStyle.CARD_PADDING,
        border_radius=AppStyle.BORDER_RADIUS,
        bgcolor=bg_color,
        border=ft.Border.all(1, border_color),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=AppStyle.SHADOW_BLUR,
            color=ft.Colors.with_opacity(0.08 if is_dark else 0.04, "#000000"),
        ),
        expand=True,
        animate=ft.Animation(AppStyle.ANIMATION_DURATION, ft.AnimationCurve.EASE_IN_OUT),
    )
