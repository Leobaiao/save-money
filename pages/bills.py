import flet as ft
from datetime import datetime, date
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
        p_date = datetime.today().strftime("%Y-%m-%d") if is_pago else ""
        finance_data.update_transaction(bill_id, is_paid=is_pago, payment_date=p_date)
        await update_ui_callback()

    async def remover_conta(e, bill_id):
        finance_data.delete_transaction(bill_id)
        await update_ui_callback()

    def make_toggle_handler(bill_id):
        async def handler(e):
            await toggle_pago(e, bill_id)
        return handler

    def make_remove_handler(bill_id):
        async def handler(e):
            await remover_conta(e, bill_id)
        return handler

    if not bills:
        from components.empty_state import EmptyState
        contas_list_view.controls.append(
            EmptyState(
                icon=ft.Icons.RECEIPT_LONG_ROUNDED,
                message="Você não tem contas registradas.",
                cta_text="Adicionar Gasto Rápido",
                on_cta_click=lambda e: page.run_task(render_view_callback, 0) # Volta pro dashboard
            )
        )
    else:
        for i, bill in enumerate(bills):
            contas_list_view.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Checkbox(value=bill.is_paid, on_change=make_toggle_handler(bill.id)),
                        ft.Column([
                            ft.Text(bill.description, size=16, weight=ft.FontWeight.W_600, color=text_color),
                            ft.Row([
                                ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=14, color=sub_color),
                                ft.Text(f"Vence: {bill.due_date}" if bill.due_date else "Sem vencimento", size=12, color=sub_color),
                                ft.Container(width=10),
                                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, size=14, color=AppColors.INCOME if bill.is_paid else sub_color),
                                ft.Text(f"Pago: {bill.payment_date}" if bill.is_paid and bill.payment_date else ("Pendente" if not bill.is_paid else "Pago"), size=12, color=AppColors.INCOME if bill.is_paid else sub_color),
                                ft.Container(width=10),
                                ft.Icon(
                                    ft.Icons.REPLAY_CIRCLE_FILLED_ROUNDED if bill.recurrence_type != "none" else ft.Icons.RADIO_BUTTON_UNCHECKED_ROUNDED, 
                                    size=14, 
                                    color=AppColors.PRIMARY if bill.recurrence_type != "none" else sub_color
                                ),
                                ft.Text(
                                    "Mensal" if bill.recurrence_type == "monthly" else 
                                    "Anual" if bill.recurrence_type == "yearly" else "Única", 
                                    size=12, 
                                    color=AppColors.PRIMARY if bill.recurrence_type != "none" else sub_color
                                ),
                            ], spacing=4),
                            ft.Text(f"R$ {bill.amount:,.2f}", size=14, color=text_color, weight="bold"),
                            ft.Text(bill.notes, size=12, color=sub_color, italic=True) if bill.notes else ft.Container(),
                        ], expand=True, spacing=4),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE_ROUNDED, 
                            on_click=make_remove_handler(bill.id), 
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

    vencimento_input = ft.TextField(
        label="Vencimento (DD/MM)", 
        expand=True,
        border_radius=AppStyle.BORDER_RADIUS_SM,
        bgcolor=AppColors.DARK_SURFACE if is_dark else "#FFFFFF",
        border_color=border_color,
        color=text_color,
        label_style=ft.TextStyle(color=sub_color),
        hint_text="Ex: 15/03"
    )

    obs_input = ft.TextField(
        label="Observações / Descrição", 
        multiline=True,
        min_lines=1,
        max_lines=3,
        border_radius=AppStyle.BORDER_RADIUS_SM,
        bgcolor=AppColors.DARK_SURFACE if is_dark else "#FFFFFF",
        border_color=border_color,
        color=text_color,
        label_style=ft.TextStyle(color=sub_color)
    )

    # DatePicker Configuration
    async def on_date_change(e):
        vencimento_btn.text = date_picker.value.strftime("%d/%m/%Y")
        vencimento_btn.update()

    date_picker = ft.DatePicker(
        on_change=on_date_change,
        first_date=datetime.now(),
    )
    page.overlay.append(date_picker)

    vencimento_btn = ft.OutlinedButton(
        "Selecionar Vencimento",
        icon=ft.Icons.CALENDAR_MONTH_ROUNDED,
        on_click=lambda _: setattr(date_picker, "open", True) or page.update(),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=AppStyle.BORDER_RADIUS_SM),
            color=sub_color,
        ),
        expand=True,
        height=50,
    )

    recurrence_dropdown = ft.Dropdown(
        label="Recorrência / Frequência",
        options=[
            ft.dropdown.Option("none", "Única (Não repete)"),
            ft.dropdown.Option("monthly", "Mensal (Todo mês)"),
            ft.dropdown.Option("yearly", "Anual (Todo ano)"),
        ],
        value="none",
        border_radius=AppStyle.BORDER_RADIUS_SM,
        bgcolor=AppColors.DARK_SURFACE if is_dark else "#FFFFFF",
        border_color=border_color,
        color=text_color,
        label_style=ft.TextStyle(color=sub_color),
        expand=True,
    )

    async def add_conta(e):
        if not nome_input.value or not valor_input.value or not date_picker.value: 
            return
        
        try:
            valor = float(valor_input.value.replace(",", "."))
        except ValueError:
            return

        is_recurring = recurrence_dropdown.value != "none"

        finance_data.add_transaction(Transaction(
            description=nome_input.value,
            amount=valor,
            type="despesa",
            category_id="cat_bills",
            is_paid=False,
            is_fixed=True,
            is_recurring=is_recurring,
            recurrence_type=recurrence_dropdown.value,
            due_date=date_picker.value.strftime("%Y-%m-%d"),
            notes=obs_input.value
        ))
        
        nome_input.value = ""
        valor_input.value = ""
        vencimento_btn.text = "Selecionar Vencimento"
        recurrence_dropdown.value = "none"
        obs_input.value = ""
        await update_ui_callback()

    from components.header import Header
    
    return ft.Container(
        content=ft.Column([
            Header(
                title="Contas a Pagar",
                subtitle="Gerencie suas contas fixas e variáveis",
                icon=ft.Icons.RECEIPT_LONG_ROUNDED
            ),
            ft.Container(height=10),
            ft.Row([nome_input, valor_input], spacing=10),
            ft.Row([vencimento_btn], spacing=10),
            recurrence_dropdown,
            obs_input,
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
