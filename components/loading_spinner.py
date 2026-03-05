import flet as ft
from theme.app_theme import AppColors

def LoadingSpinner(message: str = "Carregando..."):
    return ft.Container(
        content=ft.Column([
            ft.ProgressRing(color=AppColors.PRIMARY),
            ft.Text(message, size=14, color=AppColors.PRIMARY)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
        alignment=ft.Alignment.CENTER,
        expand=True
    )
