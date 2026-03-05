import flet as ft
from theme.app_theme import AppColors, AppStyle
from models.data_model import FinanceData

def build_profile_page(
    data: FinanceData,
    is_dark: bool,
    page: ft.Page,
    on_refresh=None,
) -> ft.Container:
    """Constrói a página de Perfil."""

    text_color = AppColors.DARK_TEXT if is_dark else AppColors.LIGHT_TEXT
    sub_color = AppColors.DARK_TEXT_SECONDARY if is_dark else AppColors.LIGHT_TEXT_SECONDARY
    bg_color = AppColors.DARK_BG if is_dark else AppColors.LIGHT_BG
    card_bg = AppColors.DARK_CARD if is_dark else AppColors.LIGHT_CARD
    input_bg = AppColors.DARK_SURFACE if is_dark else AppColors.LIGHT_BG
    border_color = AppColors.DARK_BORDER if is_dark else AppColors.LIGHT_BORDER

    # Campos de entrada
    name_field = ft.TextField(
        label="Nome do Usuário",
        value=data.settings.get("user_name", "Usuário"),
        border_radius=AppStyle.BORDER_RADIUS_SM,
        bgcolor=input_bg,
        border_color=border_color,
        label_style=ft.TextStyle(color=sub_color),
        color=text_color,
        focused_border_color=AppColors.PRIMARY,
    )

    photo_field = ft.TextField(
        label="URL da Foto de Perfil",
        value=data.settings.get("user_photo", ""),
        border_radius=AppStyle.BORDER_RADIUS_SM,
        bgcolor=input_bg,
        border_color=border_color,
        label_style=ft.TextStyle(color=sub_color),
        color=text_color,
        focused_border_color=AppColors.PRIMARY,
    )

    def update_preview(e):
        if photo_field.value:
            profile_img.src = photo_field.value
        else:
            profile_img.src = None
        page.update()

    photo_field.on_change = update_preview

    profile_img = ft.Image(
        src=data.settings.get("user_photo", ""),
        width=120,
        height=120,
        fit=ft.BoxFit.COVER,
        border_radius=60,
        error_content=ft.Icon(ft.Icons.PERSON_ROUNDED, size=80, color=sub_color),
    )

    async def save_profile(e):
        data.settings["user_name"] = name_field.value.strip() or "Usuário"
        data.settings["user_photo"] = photo_field.value.strip()
        data.save()
        
        page.snack_bar = ft.SnackBar(
            ft.Text("Perfil atualizado com sucesso!", color="white"),
            bgcolor=AppColors.INCOME
        )
        page.snack_bar.open = True
        page.update()
        if on_refresh:
            await on_refresh()

    async def clear_data_dialog(e):
        async def confirm_clear(ev):
            data.clear_all_data()
            dialog.open = False
            page.snack_bar = ft.SnackBar(
                ft.Text("Todos os dados foram apagados.", color="white"),
                bgcolor=AppColors.EXPENSE
            )
            page.snack_bar.open = True
            page.update()
            if on_refresh:
                await on_refresh()

        dialog = ft.AlertDialog(
            title=ft.Text("Apagar todos os dados?"),
            content=ft.Text("Esta ação não pode ser desfeita. Todas as transações serão excluídas."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: setattr(dialog, "open", False) or page.update()),
                ft.Button("Apagar Tudo", bgcolor=AppColors.EXPENSE, color="white", on_click=confirm_clear),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    from components.header import Header
    
    return ft.Container(
        content=ft.Column(
            [
                Header(
                    title="Perfil",
                    subtitle="Gerencie suas informações pessoais",
                    icon=ft.Icons.PERSON_ROUNDED
                ),
                ft.Container(height=20),
                
                # Foto Preview
                ft.Row(
                    [
                        ft.Container(
                            content=profile_img,
                            border=ft.Border.all(2, AppColors.PRIMARY),
                            border_radius=100,
                            padding=4,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(height=20),
                
                # Formulário
                ft.Container(
                    content=ft.Column(
                        [
                            name_field,
                            photo_field,
                            ft.Button(
                                "Salvar Alterações",
                                icon=ft.Icons.SAVE_ROUNDED,
                                bgcolor=AppColors.PRIMARY,
                                color="white",
                                on_click=save_profile,
                                height=50,
                            ),
                        ],
                        spacing=20,
                    ),
                    padding=20,
                    bgcolor=card_bg,
                    border_radius=AppStyle.BORDER_RADIUS,
                ),
                
                ft.Container(expand=True),
                
                # Zona de Perigo
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Zona de Perigo", color=AppColors.EXPENSE, weight="bold"),
                            ft.Divider(color=AppColors.EXPENSE, opacity=0.3),
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.DELETE_FOREVER_ROUNDED, color=AppColors.EXPENSE),
                                title=ft.Text("Apagar todos os dados", color=AppColors.EXPENSE),
                                subtitle=ft.Text("Exclui permanentemente todas as suas transações", size=12, color=sub_color),
                                on_click=clear_data_dialog,
                            ),
                        ]
                    ),
                    padding=20,
                    bgcolor=card_bg,
                    border_radius=AppStyle.BORDER_RADIUS,
                ),
            ],
            expand=True,
        ),
        padding=AppStyle.PAGE_PADDING,
        bgcolor=bg_color,
        expand=True,
    )
