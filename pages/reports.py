import flet as ft
from datetime import datetime
from theme.app_theme import AppColors, AppStyle
from models.data_model import FinanceData
from components.empty_state import EmptyState
from components.header import Header
from components.chart_widgets import create_bar_chart, create_pie_chart


MONTH_NAMES_FULL = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def build_reports_page(
    data: FinanceData,
    is_dark: bool,
    page: ft.Page,
    on_refresh=None,
) -> ft.Container:
    """Constrói a página de Relatórios."""

    now = datetime.now()
    text_color = AppColors.DARK_TEXT if is_dark else AppColors.LIGHT_TEXT
    sub_color = AppColors.DARK_TEXT_SECONDARY if is_dark else AppColors.LIGHT_TEXT_SECONDARY
    bg_color = AppColors.DARK_BG if is_dark else AppColors.LIGHT_BG
    card_bg = AppColors.DARK_CARD if is_dark else AppColors.LIGHT_CARD
    border_color = AppColors.DARK_BORDER if is_dark else AppColors.LIGHT_BORDER

    selected_year = {"value": now.year}
    selected_month = {"value": now.month}

    # Seletores
    year_dropdown = ft.Dropdown(
        label="Ano",
        value=str(selected_year["value"]),
        options=[ft.dropdown.Option(str(y), str(y)) for y in range(now.year - 5, now.year + 2)],
        border_radius=AppStyle.BORDER_RADIUS_SM,
        bgcolor=AppColors.DARK_SURFACE if is_dark else AppColors.LIGHT_BG,
        border_color=border_color,
        label_style=ft.TextStyle(color=sub_color),
        color=text_color,
        focused_border_color=AppColors.PRIMARY,
        expand=True,
    )

    month_dropdown = ft.Dropdown(
        label="Mês",
        value=str(selected_month["value"]),
        options=[ft.dropdown.Option(str(i + 1), MONTH_NAMES_FULL[i]) for i in range(12)],
        border_radius=AppStyle.BORDER_RADIUS_SM,
        bgcolor=AppColors.DARK_SURFACE if is_dark else AppColors.LIGHT_BG,
        border_color=border_color,
        label_style=ft.TextStyle(color=sub_color),
        color=text_color,
        focused_border_color=AppColors.PRIMARY,
        expand=True,
    )

    def on_period_change(e):
        selected_year["value"] = int(year_dropdown.value)
        selected_month["value"] = int(month_dropdown.value)
        if on_refresh:
            on_refresh()

    year_dropdown.on_change = on_period_change
    month_dropdown.on_change = on_period_change

    year = selected_year["value"]
    month = selected_month["value"]

    # Dados
    income = data.get_total_income(month, year)
    expense = data.get_total_expense(month, year)
    balance = income - expense

    monthly_summary = data.get_monthly_summary(year)
    expenses_by_cat = data.get_expenses_by_category(month, year)

    # Gráficos
    bar_chart = create_bar_chart(monthly_summary, is_dark, height=300)
    pie_chart = create_pie_chart(expenses_by_cat, is_dark, height=250)

    # Tabela Resumo
    balance_color = AppColors.INCOME if balance >= 0 else AppColors.EXPENSE

    summary_table = ft.Container(
        content=ft.Column(
            [
                ft.Text("Resumo do Período", size=16, weight=ft.FontWeight.W_600, color=text_color),
                ft.Container(height=8),
                _build_summary_row("Receitas", f"R$ {income:,.2f}", AppColors.INCOME, text_color, sub_color, is_dark),
                ft.Divider(height=1, color=border_color),
                _build_summary_row("Despesas", f"R$ {expense:,.2f}", AppColors.EXPENSE, text_color, sub_color, is_dark),
                ft.Divider(height=1, color=border_color),
                _build_summary_row("Saldo", f"R$ {balance:,.2f}", balance_color, text_color, sub_color, is_dark, bold=True),
            ],
            spacing=8,
        ),
        padding=AppStyle.CARD_PADDING,
        border_radius=AppStyle.BORDER_RADIUS,
        bgcolor=card_bg,
        border=ft.Border.all(1, border_color),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=AppStyle.SHADOW_BLUR,
            color=ft.Colors.with_opacity(0.08 if is_dark else 0.04, "#000000"),
        ),
    )

    # Top categorias de despesa
    top_categories = sorted(expenses_by_cat.items(), key=lambda x: x[1], reverse=True)[:5]
    top_cat_items = []
    total_expense = sum(expenses_by_cat.values()) if expenses_by_cat else 0

    for cat_name, amount in top_categories:
        pct = (amount / total_expense * 100) if total_expense > 0 else 0
        top_cat_items.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(cat_name, size=13, color=text_color, weight=ft.FontWeight.W_500, expand=True),
                                ft.Text(f"R$ {amount:,.2f}", size=13, color=sub_color),
                                ft.Text(f"{pct:.1f}%", size=12, color=AppColors.PRIMARY, weight=ft.FontWeight.BOLD),
                            ],
                        ),
                        ft.ProgressBar(
                            value=pct / 100,
                            color=AppColors.PRIMARY,
                            bgcolor=ft.Colors.with_opacity(0.1, AppColors.PRIMARY),
                            bar_height=6,
                            border_radius=3,
                        ),
                    ],
                    spacing=6,
                ),
            )
        )

    top_categories_card = ft.Container(
        content=ft.Column(
            [
                ft.Text("Top Categorias de Despesa", size=16, weight=ft.FontWeight.W_600, color=text_color),
                ft.Container(height=8),
                *(top_cat_items if top_cat_items else [
                    EmptyState(
                        icon=ft.Icons.CATEGORY_ROUNDED,
                        message="Sem despesas no período selecionado.",
                    )
                ]),
            ],
            spacing=10,
        ),
        padding=AppStyle.CARD_PADDING,
        border_radius=AppStyle.BORDER_RADIUS,
        bgcolor=card_bg,
        border=ft.Border.all(1, border_color),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=AppStyle.SHADOW_BLUR,
            color=ft.Colors.with_opacity(0.08 if is_dark else 0.04, "#000000"),
        ),
    )

    return ft.Container(
        content=ft.Column(
            [
                # Header
                Header(
                    title="Relatórios",
                    subtitle="Análise detalhada das suas finanças",
                    icon=ft.Icons.INSERT_CHART_ROUNDED
                ),
                ft.Row(
                    [
                        ft.Container(year_dropdown, expand=True),
                        ft.Container(month_dropdown, expand=True),
                    ],
                    spacing=12,
                ),
                ft.Container(height=16),

                # Resumo + Top Categorias
                ft.Column(
                    [
                        summary_table,
                        top_categories_card,
                    ],
                    spacing=16,
                ),
                ft.Container(height=16),

                # Gráficos
                ft.Text("Evolução Anual", size=18, weight=ft.FontWeight.W_600, color=text_color),
                bar_chart,
                ft.Container(height=16),

                ft.Text(
                    f"Despesas por Categoria — {MONTH_NAMES_FULL[month - 1]} {year}",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=text_color,
                ),
                pie_chart,
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        padding=AppStyle.PAGE_PADDING,
        expand=True,
        bgcolor=bg_color,
    )


def _build_summary_row(label, value, value_color, text_color, sub_color, is_dark, bold=False):
    return ft.Row(
        [
            ft.Text(label, size=14, color=sub_color, expand=True),
            ft.Text(
                value,
                size=16 if bold else 14,
                color=value_color,
                weight=ft.FontWeight.BOLD if bold else ft.FontWeight.W_500,
            ),
        ],
    )
