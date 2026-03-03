import flet as ft
from theme.app_theme import AppColors, AppStyle
from models.data_model import Transaction, Category


def create_transaction_card(
    txn: Transaction,
    category: Category | None,
    is_dark: bool,
    on_edit=None,
    on_delete=None,
) -> ft.Container:
    """Card individual de transação."""

    bg_color = AppColors.DARK_CARD if is_dark else AppColors.LIGHT_CARD
    text_color = AppColors.DARK_TEXT if is_dark else AppColors.LIGHT_TEXT
    sub_color = AppColors.DARK_TEXT_SECONDARY if is_dark else AppColors.LIGHT_TEXT_SECONDARY
    border_color = AppColors.DARK_BORDER if is_dark else AppColors.LIGHT_BORDER

    is_income = txn.type == "receita"
    amount_color = AppColors.INCOME if is_income else AppColors.EXPENSE
    sign = "+" if is_income else "-"
    cat_name = category.name if category else "Sem Categoria"
    cat_color = category.color if category else "#9E9E9E"

    # Formatar a data
    parts = txn.date.split("-")
    formatted_date = f"{parts[2]}/{parts[1]}/{parts[0]}" if len(parts) == 3 else txn.date

    icon_name = ft.Icons.ARROW_UPWARD_ROUNDED if is_income else ft.Icons.ARROW_DOWNWARD_ROUNDED

    return ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Icon(icon_name, color="#FFFFFF", size=20),
                    width=40,
                    height=40,
                    border_radius=10,
                    bgcolor=amount_color,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column(
                    [
                        ft.Text(
                            txn.description,
                            size=14,
                            color=text_color,
                            weight=ft.FontWeight.W_600,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Row(
                            [
                                ft.Container(
                                    content=ft.Text(cat_name, size=11, color="#FFFFFF"),
                                    bgcolor=cat_color,
                                    border_radius=6,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                ),
                                ft.Text(formatted_date, size=11, color=sub_color),
                            ],
                            spacing=8,
                        ),
                    ],
                    spacing=4,
                    expand=True,
                ),
                ft.Text(
                    f"{sign} R$ {txn.amount:,.2f}",
                    size=16,
                    color=amount_color,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.PopupMenuButton(
                    icon=ft.Icons.MORE_VERT_ROUNDED,
                    icon_color=sub_color,
                    icon_size=20,
                    items=[
                        ft.PopupMenuItem(
                            text="Editar",
                            icon=ft.Icons.EDIT_ROUNDED,
                            on_click=lambda e, tid=txn.id: on_edit(tid) if on_edit else None,
                        ),
                        ft.PopupMenuItem(
                            text="Excluir",
                            icon=ft.Icons.DELETE_ROUNDED,
                            on_click=lambda e, tid=txn.id: on_delete(tid) if on_delete else None,
                        ),
                    ],
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        border_radius=AppStyle.BORDER_RADIUS_SM,
        bgcolor=bg_color,
        border=ft.border.all(1, border_color),
        animate=ft.Animation(AppStyle.ANIMATION_DURATION, ft.AnimationCurve.EASE_IN_OUT),
    )
