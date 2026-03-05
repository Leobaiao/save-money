import flet as ft
from theme.app_theme import AppColors

def Header(title: str, subtitle: str = "", icon: str = None, actions: list = None):
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Row([
                    ft.Icon(icon, color=AppColors.PRIMARY, size=28) if icon else ft.Container(),
                    ft.Column([
                        ft.Text(title, size=22, weight="bold", color=AppColors.PRIMARY),
                        ft.Text(subtitle, size=12, color=ft.Colors.GREY_500) if subtitle else ft.Container(),
                    ], spacing=0)
                ], spacing=10),
                ft.Row(actions or [], spacing=5)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ]),
        margin=ft.Margin(20, 10, 20, 10)
    )
