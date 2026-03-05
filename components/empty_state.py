import flet as ft
from theme.app_theme import AppColors

def EmptyState(icon: str, message: str, cta_text: str = None, on_cta_click = None):
    controls = [
        ft.Icon(icon, size=64, color=ft.Colors.GREY_300),
        ft.Text(message, size=16, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER),
    ]
    if cta_text and on_cta_click:
        controls.append(
            ft.TextButton(
                cta_text, 
                on_click=on_cta_click,
                style=ft.ButtonStyle(color=AppColors.PRIMARY)
            )
        )
        
    return ft.Container(
        content=ft.Column(
            controls,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        padding=40,
        alignment=ft.Alignment.CENTER,
        expand=True
    )
