import flet as ft
from models.data_model import FinanceData, Transaction
from theme.app_theme import AppColors, AppStyle

def build_bills_page(
    data_state: dict,
    finance_data: FinanceData,
    is_dark: bool,
    page: ft.Page,
    save_state_callback,
    update_ui_callback,
    render_view_callback
) -> ft.Container:
    """Página de gerenciamento de contas a pagar."""
    
    text_color = AppColors.DARK_TEXT if is_dark else AppColors.LIGHT_TEXT
    sub_color = AppColors.DARK_TEXT_SECONDARY if is_dark else AppColors.LIGHT_TEXT_SECONDARY
    bg_color = AppColors.DARK_BG if is_dark else AppColors.LIGHT_BG
    card_bg = AppColors.DARK_CARD if is_dark else AppColors.LIGHT_CARD
    border_color = AppColors.DARK_BORDER if is_dark else AppColors.LIGHT_BORDER

    contas_list_view = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    async def toggle_pago(e, index):
        is_pago = e.control.value
        conta = data_state["contas"][index]
        valor = float(conta["valor"])
        
        if is_pago:
            data_state["saldo"] -= valor
            finance_data.add_transaction(Transaction(
                description=f"Pagamento: {conta['nome']}",
                amount=valor,
                type="despesa",
                category_id="cat_bills"
            ))
        else:
            data_state["saldo"] += valor
            
        data_state["contas"][index]["pago"] = is_pago
        await save_state_callback(data_state)
        await update_ui_callback()

    async def remover_conta(index):
        data_state["contas"].pop(index)
        await save_state_callback(data_state)
        await render_view_callback(3) # Index da aba de contas
        await update_ui_callback()

    for i, conta in enumerate(data_state["contas"]):
        contas_list_view.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Checkbox(value=conta["pago"], on_change=lambda e, idx=i: toggle_pago(e, idx)),
                    ft.Column([
                        ft.Text(conta["nome"], size=16, weight=ft.FontWeight.W_600, color=text_color),
                        ft.Text(f"R$ {float(conta['valor']):,.2f}", size=14, color=sub_color),
                    ], expand=True, spacing=0),
                    ft.IconButton(
                        ft.Icons.DELETE_OUTLINE_ROUNDED, 
                        on_click=lambda e, idx=i: remover_conta(idx), 
                        icon_color=AppColors.EXPENSE,
                        tooltip="Remover Conta"
                    )
                ], alignment=ft.MainAxisAlignment.CENTER),
                padding=10,
                bgcolor=card_bg,
                border_radius=AppStyle.BORDER_RADIUS_SM,
                border=ft.border.all(1, border_color),
            )
        )

    nome_input = ft.TextField(
        label="Nome da Conta", 
        expand=True,
        border_radius=AppStyle.BORDER_RADIUS_SM,
        bgcolor=AppColors.DARK_SURFACE if is_dark else "#FFFFFF",
        border_color=border_color,
        color=text_color,
        label_style=ft.TextStyle(color=sub_color)
    )
    
    valor_input = ft.TextField(
        label="Valor", 
        prefix=ft.Text("R$ "), 
        expand=True, 
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=AppStyle.BORDER_RADIUS_SM,
        bgcolor=AppColors.DARK_SURFACE if is_dark else "#FFFFFF",
        border_color=border_color,
        color=text_color,
        label_style=ft.TextStyle(color=sub_color)
    )

    async def add_conta(e):
        if not nome_input.value or not valor_input.value: return
        try:
            valor = float(valor_input.value.replace(",", "."))
        except ValueError:
            return

        data_state["contas"].append({
            "nome": nome_input.value,
            "valor": valor,
            "pago": False
        })
        await save_state_callback(data_state)
        await render_view_callback(3)
        await update_ui_callback()

    return ft.Container(
        content=ft.Column([
            ft.Text("Contas a Pagar", size=28, weight=ft.FontWeight.BOLD, color=text_color),
            ft.Text("Gerencie suas contas fixas e variáveis", size=14, color=sub_color),
            ft.Container(height=10),
            ft.Row([nome_input, valor_input], spacing=10),
            ft.ElevatedButton(
                "Adicionar Conta", 
                icon=ft.Icons.ADD_ROUNDED, 
                on_click=add_conta,
                bgcolor=AppColors.PRIMARY,
                color="#FFFFFF",
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=AppStyle.BORDER_RADIUS_SM)),
                height=50
            ),
            ft.Divider(height=30, color=border_color),
            ft.Text("Suas Contas", size=18, weight=ft.FontWeight.W_600, color=text_color),
            ft.Column([contas_list_view], expand=True, spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
        ], spacing=10, expand=True),
        padding=AppStyle.PAGE_PADDING,
        expand=True,
        bgcolor=bg_color
    )
