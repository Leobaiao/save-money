import flet as ft
from datetime import datetime, date
from theme.app_theme import AppColors, AppStyle
from models.data_model import FinanceData, Transaction
from components.transaction_card import create_transaction_card


def build_transactions_page(
    data: FinanceData,
    is_dark: bool,
    page: ft.Page,
    on_refresh=None,
) -> ft.Container:
    """Constrói a página de Transações com CRUD."""

    text_color = AppColors.DARK_TEXT if is_dark else AppColors.LIGHT_TEXT
    sub_color = AppColors.DARK_TEXT_SECONDARY if is_dark else AppColors.LIGHT_TEXT_SECONDARY
    bg_color = AppColors.DARK_BG if is_dark else AppColors.LIGHT_BG
    card_bg = AppColors.DARK_CARD if is_dark else AppColors.LIGHT_CARD
    border_color = AppColors.DARK_BORDER if is_dark else AppColors.LIGHT_BORDER
    input_bg = AppColors.DARK_SURFACE if is_dark else AppColors.LIGHT_BG

    # Estado dos filtros
    filter_type = {"value": None}  # None = todos

    def get_filtered_transactions():
        if filter_type["value"] == "agendadas":
            return data.get_bills(is_paid=False)
        return data.get_transactions(type_filter=filter_type["value"])

    # ─── Dialog de Transação ───────────────────────────────────────────

    def open_transaction_dialog(txn_id=None):
        editing = txn_id is not None
        txn = None
        if editing:
            for t in data.transactions:
                if t.id == txn_id:
                    txn = t
                    break

        desc_field = ft.TextField(
            label="Descrição",
            value=txn.description if txn else "",
            border_radius=AppStyle.BORDER_RADIUS_SM,
            bgcolor=input_bg,
            border_color=border_color,
            label_style=ft.TextStyle(color=sub_color),
            color=text_color,
            focused_border_color=AppColors.PRIMARY,
        )

        amount_field = ft.TextField(
            label="Valor (R$)",
            value=str(txn.amount) if txn else "",
            border_radius=AppStyle.BORDER_RADIUS_SM,
            bgcolor=input_bg,
            border_color=border_color,
            label_style=ft.TextStyle(color=sub_color),
            color=text_color,
            keyboard_type=ft.KeyboardType.NUMBER,
            focused_border_color=AppColors.PRIMARY,
        )

        type_dropdown = ft.Dropdown(
            label="Tipo",
            value=txn.type if txn else "despesa",
            options=[
                ft.dropdown.Option("receita", "Receita"),
                ft.dropdown.Option("despesa", "Despesa"),
            ],
            border_radius=AppStyle.BORDER_RADIUS_SM,
            bgcolor=input_bg,
            border_color=border_color,
            label_style=ft.TextStyle(color=sub_color),
            color=text_color,
            focused_border_color=AppColors.PRIMARY,
            width=200,
        )

        # Categorias baseadas no tipo selecionado
        def get_category_options(txn_type):
            cats = data.get_categories_by_type(txn_type)
            return [ft.dropdown.Option(c.id, c.name) for c in cats]

        cat_dropdown = ft.Dropdown(
            label="Categoria",
            value=txn.category_id if txn else "",
            options=get_category_options(txn.type if txn else "despesa"),
            border_radius=AppStyle.BORDER_RADIUS_SM,
            bgcolor=input_bg,
            border_color=border_color,
            label_style=ft.TextStyle(color=sub_color),
            color=text_color,
            focused_border_color=AppColors.PRIMARY,
            expand=True,
        )

        def on_type_change(e):
            cat_dropdown.options = get_category_options(type_dropdown.value)
            cat_dropdown.value = ""
            page.update()

        type_dropdown.on_change = on_type_change

        date_field = ft.TextField(
            label="Data (AAAA-MM-DD)",
            value=txn.date if txn else date.today().isoformat(),
            border_radius=AppStyle.BORDER_RADIUS_SM,
            bgcolor=input_bg,
            border_color=border_color,
            label_style=ft.TextStyle(color=sub_color),
            color=text_color,
            focused_border_color=AppColors.PRIMARY,
        )

        notes_field = ft.TextField(
            label="Observações",
            value=txn.notes if txn else "",
            border_radius=AppStyle.BORDER_RADIUS_SM,
            bgcolor=input_bg,
            border_color=border_color,
            label_style=ft.TextStyle(color=sub_color),
            color=text_color,
            multiline=True,
            min_lines=2,
            max_lines=4,
            focused_border_color=AppColors.PRIMARY,
        )

        error_text = ft.Text("", color=AppColors.EXPENSE, size=12, visible=False)

        def save_transaction(e):
            # Validação
            if not desc_field.value or not desc_field.value.strip():
                error_text.value = "Preencha a descrição."
                error_text.visible = True
                page.update()
                return

            try:
                amount = float(amount_field.value.replace(",", "."))
                if amount <= 0:
                    raise ValueError()
            except (ValueError, TypeError):
                error_text.value = "Valor inválido. Use um número positivo."
                error_text.visible = True
                page.update()
                return

            if not cat_dropdown.value:
                error_text.value = "Selecione uma categoria."
                error_text.visible = True
                page.update()
                return

            # Validar data
            try:
                datetime.fromisoformat(date_field.value)
            except (ValueError, TypeError):
                error_text.value = "Data inválida. Use o formato AAAA-MM-DD."
                error_text.visible = True
                page.update()
                return

            if editing:
                data.update_transaction(
                    txn_id,
                    description=desc_field.value.strip(),
                    amount=amount,
                    type=type_dropdown.value,
                    category_id=cat_dropdown.value,
                    date=date_field.value,
                    notes=notes_field.value.strip(),
                )
            else:
                new_txn = Transaction(
                    description=desc_field.value.strip(),
                    amount=amount,
                    type=type_dropdown.value,
                    category_id=cat_dropdown.value,
                    date=date_field.value,
                    notes=notes_field.value.strip(),
                )
                data.add_transaction(new_txn)

            dialog.open = False
            page.update()
            if on_refresh:
                on_refresh()

        def close_dialog(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Editar Transação" if editing else "Nova Transação",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=text_color,
            ),
            bgcolor=card_bg,
            content=ft.Container(
                content=ft.Column(
                    [
                        desc_field,
                        ft.Row([amount_field, type_dropdown], spacing=12),
                        ft.Row([cat_dropdown], spacing=12),
                        date_field,
                        notes_field,
                        error_text,
                    ],
                    spacing=14,
                    tight=True,
                ),
                width=450,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton(
                    "Salvar",
                    on_click=save_transaction,
                    bgcolor=AppColors.PRIMARY,
                    color="#FFFFFF",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=AppStyle.BORDER_RADIUS_SM),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # ─── Handlers ──────────────────────────────────────────────────────

    def on_edit(txn_id):
        open_transaction_dialog(txn_id)

    def on_delete(txn_id):
        def confirm_delete(e):
            data.delete_transaction(txn_id)
            confirm_dialog.open = False
            page.update()
            if on_refresh:
                on_refresh()

        def cancel_delete(e):
            confirm_dialog.open = False
            page.update()

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Exclusão", color=text_color),
            content=ft.Text("Tem certeza que deseja excluir esta transação?", color=sub_color),
            bgcolor=card_bg,
            actions=[
                ft.TextButton("Cancelar", on_click=cancel_delete),
                ft.ElevatedButton(
                    "Excluir",
                    on_click=confirm_delete,
                    bgcolor=AppColors.EXPENSE,
                    color="#FFFFFF",
                ),
            ],
        )
        page.overlay.append(confirm_dialog)
        confirm_dialog.open = True
        page.update()

    # ─── Filtros ───────────────────────────────────────────────────────

    def on_filter_change(e):
        value = e.control.data
        filter_type["value"] = value
        if on_refresh:
            on_refresh()

    filter_buttons = ft.Row(
        [
            ft.Container(
                content=ft.Text("Todos", size=13, color="#FFFFFF" if filter_type["value"] is None else sub_color),
                bgcolor=AppColors.PRIMARY if filter_type["value"] is None else "transparent",
                border=ft.border.all(1, AppColors.PRIMARY if filter_type["value"] is None else border_color),
                border_radius=20,
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                on_click=on_filter_change,
                data=None,
                ink=True,
            ),
            ft.Container(
                content=ft.Text("Receitas", size=13, color="#FFFFFF" if filter_type["value"] == "receita" else sub_color),
                bgcolor=AppColors.INCOME if filter_type["value"] == "receita" else "transparent",
                border=ft.border.all(1, AppColors.INCOME if filter_type["value"] == "receita" else border_color),
                border_radius=20,
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                on_click=on_filter_change,
                data="receita",
                ink=True,
            ),
            ft.Container(
                content=ft.Text("Despesas", size=13, color="#FFFFFF" if filter_type["value"] == "despesa" else sub_color),
                bgcolor=AppColors.EXPENSE if filter_type["value"] == "despesa" else "transparent",
                border=ft.border.all(1, AppColors.EXPENSE if filter_type["value"] == "despesa" else border_color),
                border_radius=20,
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                on_click=on_filter_change,
                data="despesa",
                ink=True,
            ),
            ft.Container(
                content=ft.Text("Agendadas", size=13, color="#FFFFFF" if filter_type["value"] == "agendadas" else sub_color),
                bgcolor=ft.Colors.YELLOW_700 if filter_type["value"] == "agendadas" else "transparent",
                border=ft.border.all(1, ft.Colors.YELLOW_700 if filter_type["value"] == "agendadas" else border_color),
                border_radius=20,
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                on_click=on_filter_change,
                data="agendadas",
                ink=True,
            ),
        ],
        spacing=8,
    )

    # ─── Lista de Transações ───────────────────────────────────────────

    transactions = get_filtered_transactions()
    txn_list = []
    for txn in transactions:
        cat = data.get_category_by_id(txn.category_id)
        txn_list.append(create_transaction_card(txn, cat, is_dark, on_edit, on_delete))

    if not txn_list:
        txn_list.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.RECEIPT_LONG_ROUNDED, size=48, color=sub_color),
                        ft.Text("Nenhuma transação encontrada", size=14, color=sub_color),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                ),
                height=200,
                alignment=ft.Alignment.CENTER,
            )
        )

    # ─── FAB ───────────────────────────────────────────────────────────

    fab = ft.FloatingActionButton(
        icon=ft.Icons.ADD_ROUNDED,
        bgcolor=AppColors.PRIMARY,
        foreground_color="#FFFFFF",
        on_click=lambda e: open_transaction_dialog(),
        tooltip="Nova Transação",
    )

    return ft.Stack(
        [
            ft.Container(
                content=ft.Column(
                    [
                        # Header
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text("Transações", size=28, weight=ft.FontWeight.BOLD, color=text_color),
                                        ft.Text(
                                            f"{len(transactions)} transações",
                                            size=14,
                                            color=sub_color,
                                        ),
                                    ],
                                    spacing=4,
                                    expand=True,
                                ),
                            ],
                        ),
                        ft.Container(height=6),

                        # Filtros
                        filter_buttons,
                        ft.Container(height=10),

                        # Lista
                        ft.Column(txn_list, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True),
                    ],
                    spacing=0,
                    expand=True,
                ),
                padding=AppStyle.PAGE_PADDING,
                expand=True,
                bgcolor=bg_color,
            ),
            ft.Container(
                content=fab,
                alignment=ft.Alignment.BOTTOM_RIGHT,
                padding=30,
            ),
        ],
        expand=True,
    )
