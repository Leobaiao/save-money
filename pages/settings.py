import flet as ft
from models.data_model import FinanceData, Transaction
from theme.app_theme import AppColors, AppStyle

def build_settings_page(
    data_state: dict,
    finance_data: FinanceData,
    is_dark: bool,
    page: ft.Page,
    save_state_callback,
    update_ui_callback,
    toggle_theme_callback
) -> ft.Container:
    """Página de configurações do aplicativo."""
    
    text_color = AppColors.DARK_TEXT if is_dark else AppColors.LIGHT_TEXT
    sub_color = AppColors.DARK_TEXT_SECONDARY if is_dark else AppColors.LIGHT_TEXT_SECONDARY
    bg_color = AppColors.DARK_BG if is_dark else AppColors.LIGHT_BG
    card_bg = AppColors.DARK_CARD if is_dark else AppColors.LIGHT_CARD
    border_color = AppColors.DARK_BORDER if is_dark else AppColors.LIGHT_BORDER
    input_bg = AppColors.DARK_SURFACE if is_dark else "#FFFFFF"

    salario_input = ft.TextField(
        label="Saldo Atual no Banco", 
        hint_text="00,00", 
        value=str(round(finance_data.get_total_balance(), 2)), 
        prefix=ft.Text("R$ "), 
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=AppStyle.BORDER_RADIUS_SM,
        bgcolor=input_bg,
        border_color=border_color,
        color=text_color,
        label_style=ft.TextStyle(color=sub_color)
    )
    
    dia_pag_input = ft.TextField(
        label="Dia do Pagamento", 
        value=str(data_state["dia_pag"]), 
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=AppStyle.BORDER_RADIUS_SM,
        bgcolor=input_bg,
        border_color=border_color,
        color=text_color,
        label_style=ft.TextStyle(color=sub_color)
    )
    
    meta_input = ft.TextField(
        label="Meta de Sobra (Fim do Mês)", 
        value=str(data_state["meta"]), 
        prefix=ft.Text("R$ "), 
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=AppStyle.BORDER_RADIUS_SM,
        bgcolor=input_bg,
        border_color=border_color,
        color=text_color,
        label_style=ft.TextStyle(color=sub_color)
    )
    
    teto_input = ft.TextField(
        label="Teto de Gasto Diário (Opcional)", 
        value=str(data_state["teto"]), 
        prefix=ft.Text("R$ "), 
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=AppStyle.BORDER_RADIUS_SM,
        bgcolor=input_bg,
        border_color=border_color,
        color=text_color,
        label_style=ft.TextStyle(color=sub_color)
    )

    async def export_data(e):
        path = finance_data.export_data()
        if path:
            snackbar = ft.SnackBar(ft.Text(f"Banco exportado para Downloads", color="#FFFFFF"), bgcolor=AppColors.INCOME)
        else:
            snackbar = ft.SnackBar(ft.Text("Erro ao exportar banco de dados.", color="#FFFFFF"), bgcolor=AppColors.EXPENSE)
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()

    async def reset_data_confirm(e):
        def close_dlg(ev):
            dlg.open = False
            page.update()

        async def do_reset(ev):
            finance_data.reset_all_data()
            dlg.open = False
            await update_ui_callback()
            snackbar = ft.SnackBar(ft.Text("Banco de dados resetado (Zerado).", color="#FFFFFF"), bgcolor=AppColors.INCOME)
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Confirmar Reset"),
            content=ft.Text("Isso apagará TODOS os seus dados (transações e configurações) permanentemente. Deseja continuar?"),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dlg),
                ft.TextButton("Sim, Resetar", on_click=do_reset, color=AppColors.EXPENSE),
            ],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    async def save_settings(e):
        try:
            current_saldo = finance_data.get_total_balance()
            new_saldo = float(salario_input.value.replace(",", "."))
            diff = new_saldo - current_saldo
            
            if abs(diff) > 0.01:
                finance_data.add_transaction(Transaction(
                    description="Reconciliação de Saldo (Ajustes)",
                    amount=abs(diff),
                    type="receita" if diff > 0 else "despesa",
                    category_id="cat_other_in" if diff > 0 else "cat_other_out"
                ))
            
            # data_state["saldo"] não é mais usado para o valor atual, 
            # apenas mantemos para compatibilidade se necessário, mas zerado
            data_state["saldo"] = 0 
            data_state["dia_pag"] = int(dia_pag_input.value)
            data_state["meta"] = float(meta_input.value.replace(",", "."))
            data_state["teto"] = float(teto_input.value.replace(",", "."))
            
            await save_state_callback(data_state)
            await update_ui_callback()
            
            snackbar = ft.SnackBar(
                ft.Text("Configurações salvas com sucesso!", color="#FFFFFF"),
                bgcolor=AppColors.INCOME
            )
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()
        except ValueError:
            snackbar = ft.SnackBar(
                ft.Text("Erro: Verifique os valores digitados.", color="#FFFFFF"),
                bgcolor=AppColors.EXPENSE
            )
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()

    return ft.Container(
        content=ft.Column([
            ft.Text("Configurações", size=28, weight=ft.FontWeight.BOLD, color=text_color),
            ft.Text("Personalize sua experiência e metas", size=14, color=sub_color),
            ft.Container(height=20),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("Finanças Pessoais", size=18, weight=ft.FontWeight.W_600, color=text_color),
                    salario_input,
                    dia_pag_input,
                    meta_input,
                    teto_input,
                ], spacing=15),
                padding=20,
                bgcolor=card_bg,
                border_radius=AppStyle.BORDER_RADIUS,
                border=ft.Border.all(1, border_color),
            ),
            
            ft.Container(height=10),
            
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.PALETTE_ROUNDED, color=AppColors.PRIMARY),
                    ft.Text("Tema do Aplicativo", size=16, color=text_color, expand=True),
                    ft.Switch(
                        value=is_dark, 
                        on_change=toggle_theme_callback,
                        active_color=AppColors.PRIMARY
                    )
                ], alignment=ft.MainAxisAlignment.CENTER),
                padding=20,
                bgcolor=card_bg,
                border_radius=AppStyle.BORDER_RADIUS,
                border=ft.Border.all(1, border_color),
            ),
            
            ft.Container(height=10),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("Gerenciamento de Dados", size=18, weight=ft.FontWeight.W_600, color=text_color),
                    ft.Row([
                        ft.ElevatedButton(
                            "Exportar Banco", 
                            icon=ft.Icons.DOWNLOAD_ROUNDED, 
                            on_click=export_data,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=AppStyle.BORDER_RADIUS_SM)),
                            expand=True
                        ),
                        ft.ElevatedButton(
                            "Zerar App (Limpar tudo)", 
                            icon=ft.Icons.DELETE_FOREVER_ROUNDED, 
                            on_click=reset_data_confirm,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=AppStyle.BORDER_RADIUS_SM), color=AppColors.EXPENSE),
                            expand=True
                        ),
                    ], spacing=10),
                ], spacing=15),
                padding=20,
                bgcolor=card_bg,
                border_radius=AppStyle.BORDER_RADIUS,
                border=ft.Border.all(1, border_color),
            ),
            
            ft.Container(height=20),
            
            ft.Button(
                "Salvar Alterações", 
                icon=ft.Icons.SAVE_ROUNDED, 
                on_click=save_settings,
                bgcolor=AppColors.PRIMARY,
                color="#FFFFFF",
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=AppStyle.BORDER_RADIUS_SM),
                ),
                expand=True,
                height=55
            )
        ], spacing=10, scroll=ft.ScrollMode.ADAPTIVE),
        padding=AppStyle.PAGE_PADDING,
        expand=True,
        bgcolor=bg_color
    )
