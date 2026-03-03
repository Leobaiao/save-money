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
    """Página de gerenciamento de contas a pagar (Integrated with FinanceData)."""
    
    text_color = AppColors.DARK_TEXT if is_dark else AppColors.LIGHT_TEXT
    sub_color = AppColors.DARK_TEXT_SECONDARY if is_dark else AppColors.LIGHT_TEXT_SECONDARY
    bg_color = AppColors.DARK_BG if is_dark else AppColors.LIGHT_BG
    card_bg = AppColors.DARK_CARD if is_dark else AppColors.LIGHT_CARD
    border_color = AppColors.DARK_BORDER if is_dark else AppColors.LIGHT_BORDER

    bills = finance_data.get_bills()
    contas_list_view = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    async def toggle_pago(e, bill_id):
        is_pago = e.control.value
        finance_data.update_transaction(bill_id, is_paid=is_pago)
        await update_ui_callback()

    async def remover_conta(bill_id):
        finance_data.delete_transaction(bill_id)
        await update_ui_callback()

    for i, bill in enumerate(bills):
        contas_list_view.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Checkbox(value=bill.is_paid, on_change=lambda e, b_id=bill.id: toggle_pago(e, b_id)),
                    ft.Column([
                        ft.Text(bill.description, size=16, weight=ft.FontWeight.W_600, color=text_color),
                        ft.Text(f"R$ {bill.amount:,.2f}", size=14, color=sub_color),
                    ], expand=True, spacing=0),
                    ft.IconButton(
                        ft.Icons.DELETE_OUTLINE_ROUNDED, 
                        on_click=lambda e, b_id=bill.id: remover_conta(b_id), 
                        icon_color=AppColors.EXPENSE,
                        tooltip="Remover Conta"
                    )
                ], alignment=ft.MainAxisAlignment.CENTER),
                padding=10,
                bgcolor=card_bg,
                border_radius=AppStyle.BORDER_RADIUS_SM,
                border=ft.Border.all(1, border_color),
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

        finance_data.add_transaction(Transaction(
            description=nome_input.value,
            amount=valor,
            type="despesa",
            category_id="cat_bills",
            is_paid=False,
            is_fixed=True
        ))
        
        nome_input.value = ""
        valor_input.value = ""
        await update_ui_callback()

    return ft.Container(
        content=ft.Column([
            ft.Text("Contas a Pagar", size=28, weight=ft.FontWeight.BOLD, color=text_color),
            ft.Text("Gerencie suas contas fixas e variáveis", size=14, color=sub_color),
            ft.Container(height=10),
            ft.Row([nome_input, valor_input], spacing=10),
            ft.Button(
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
