import flet as ft
from datetime import datetime
from theme.app_theme import AppColors, AppStyle
from models.data_model import FinanceData
from components.summary_card import create_summary_card
from components.transaction_card import create_transaction_card
from components.chart_widgets import create_bar_chart, create_pie_chart


def build_dashboard(
    data: FinanceData,
    is_dark: bool,
    on_edit_txn=None,
    on_delete_txn=None,
) -> ft.Container:
    """Constrói a página do Dashboard."""

    now = datetime.now()
    month, year = now.month, now.year

    # Dados financeiros
    balance = data.get_balance(month, year)
    income = data.get_total_income(month, year)
    expense = data.get_total_expense(month, year)

    text_color = AppColors.DARK_TEXT if is_dark else AppColors.LIGHT_TEXT
    sub_color = AppColors.DARK_TEXT_SECONDARY if is_dark else AppColors.LIGHT_TEXT_SECONDARY
    bg_color = AppColors.DARK_BG if is_dark else AppColors.LIGHT_BG

    # ─── Cards de Resumo ───────────────────────────────────────────────
    balance_color = AppColors.INCOME if balance >= 0 else AppColors.EXPENSE
    summary_cards = ft.Row(
        [
            create_summary_card(
                "Saldo do Mês",
                f"R$ {balance:,.2f}",
                ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED,
                balance_color,
                is_dark,
            ),
            create_summary_card(
                "Receitas",
                f"R$ {income:,.2f}",
                ft.Icons.TRENDING_UP_ROUNDED,
                AppColors.INCOME,
                is_dark,
            ),
            create_summary_card(
                "Despesas",
                f"R$ {expense:,.2f}",
                ft.Icons.TRENDING_DOWN_ROUNDED,
                AppColors.EXPENSE,
                is_dark,
            ),
        ],
        spacing=16,
    )

    # ─── Gráfico de Barras (últimos 6 meses) ──────────────────────────
    monthly_summary = data.get_monthly_summary(year)
    # Pegar os últimos 6 meses a partir do mês atual
    start_month = max(0, month - 6)
    recent_months = monthly_summary[start_month:month]

    bar_chart = create_bar_chart(recent_months, is_dark)

    # ─── Gráfico de Pizza ──────────────────────────────────────────────
    expenses_by_cat = data.get_expenses_by_category(month, year)
    pie_chart = create_pie_chart(expenses_by_cat, is_dark)

    # ─── Últimas Transações ────────────────────────────────────────────
    recent_txns = data.get_transactions()[:5]
    txn_cards = []
    for txn in recent_txns:
        cat = data.get_category_by_id(txn.category_id)
        txn_cards.append(
            create_transaction_card(txn, cat, is_dark, on_edit_txn, on_delete_txn)
        )

    if not txn_cards:
        txn_cards.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.RECEIPT_LONG_ROUNDED, size=40, color=sub_color),
                        ft.Text("Nenhuma transação registrada", size=14, color=sub_color),
                        ft.Text("Adicione sua primeira transação!", size=12, color=sub_color),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                ),
                height=120,
                alignment=ft.Alignment.CENTER,
            )
        )

    bg_card = AppColors.DARK_CARD if is_dark else AppColors.LIGHT_CARD
    border_color = AppColors.DARK_BORDER if is_dark else AppColors.LIGHT_BORDER

    return ft.Container(
        content=ft.Column(
            [
                # Header
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("Dashboard", size=28, weight=ft.FontWeight.BOLD, color=text_color),
                                ft.Text(
                                    f"Resumo de {now.strftime('%B %Y').title()}",
                                    size=14,
                                    color=sub_color,
                                ),
                            ],
                            spacing=4,
                        ),
                    ],
                ),
                ft.Container(height=10),

                # Cards de resumo
                summary_cards,
                ft.Container(height=10),

                # Gráficos
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Receitas vs Despesas", size=16, weight=ft.FontWeight.W_600, color=text_color),
                                    bar_chart,
                                ],
                                spacing=10,
                            ),
                            expand=3,
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Despesas por Categoria", size=16, weight=ft.FontWeight.W_600, color=text_color),
                                    pie_chart,
                                ],
                                spacing=10,
                            ),
                            expand=2,
                        ),
                    ],
                    spacing=16,
                ),
                ft.Container(height=10),

                # Últimas transações
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text("Últimas Transações", size=16, weight=ft.FontWeight.W_600, color=text_color),
                                ],
                            ),
                            ft.Column(txn_cards, spacing=8),
                        ],
                        spacing=12,
                    ),
                    padding=AppStyle.CARD_PADDING,
                    border_radius=AppStyle.BORDER_RADIUS,
                    bgcolor=bg_card,
                    border=ft.border.all(1, border_color),
                ),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        padding=AppStyle.PAGE_PADDING,
        expand=True,
        bgcolor=bg_color,
    )
