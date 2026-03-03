import flet as ft
from datetime import datetime
from theme.app_theme import AppColors, AppStyle
from models.data_model import FinanceData
from components.summary_card import create_summary_card
from components.transaction_card import create_transaction_card


# Tradução de meses para português
MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

DIAS_SEMANA_PT = {
    0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira",
    3: "Quinta-feira", 4: "Sexta-feira", 5: "Sábado", 6: "Domingo",
}


def build_dashboard(
    data: FinanceData,
    is_dark: bool,
    page: ft.Page = None,
    on_add_expense=None,
    on_pay_bill=None,
    on_refresh=None,
    on_edit_txn=None,
    on_delete_txn=None,
) -> ft.Container:
    """Dashboard Android-first com Hero Header, Burn Rate, Quick Actions e Alertas."""

    now = datetime.now()
    month, year = now.month, now.year

    # Cores
    text_color = AppColors.DARK_TEXT if is_dark else AppColors.LIGHT_TEXT
    sub_color = AppColors.DARK_TEXT_SECONDARY if is_dark else AppColors.LIGHT_TEXT_SECONDARY
    bg_color = AppColors.DARK_BG if is_dark else AppColors.LIGHT_BG
    card_bg = AppColors.DARK_CARD if is_dark else AppColors.LIGHT_CARD
    surface_bg = AppColors.DARK_SURFACE if is_dark else ft.Colors.WHITE
    border_color = AppColors.DARK_BORDER if is_dark else AppColors.LIGHT_BORDER

    # Dados
    balance = data.get_balance(month, year)
    income = data.get_total_income(month, year)
    expense = data.get_total_expense(month, year)
    burn = data.get_burn_rate_data()
    upcoming = data.get_upcoming_bills()
    user_name = data.settings.get("user_name", "")

    # ═══════════════════════════════════════════════════════════════════════
    # 1. HERO HEADER — Saudação Pessoal + Data
    # ═══════════════════════════════════════════════════════════════════════
    greeting = "Olá!"
    if user_name:
        greeting = f"Olá, {user_name}!"
    
    # Saudação por horário
    hora = now.hour
    if hora < 12:
        emoji = "☀️"
        periodo = "Bom dia"
    elif hora < 18:
        emoji = "🌤️"
        periodo = "Boa tarde"
    else:
        emoji = "🌙"
        periodo = "Boa noite"

    dia_semana = DIAS_SEMANA_PT.get(now.weekday(), "")
    data_formatada = f"{dia_semana}, {now.day} de {MESES_PT.get(month, '')} de {year}"

    hero_header = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text(f"{emoji} {periodo}", size=14, color=sub_color),
                    ft.Text(greeting, size=26, weight=ft.FontWeight.BOLD, color=text_color),
                    ft.Text(data_formatada, size=12, color=sub_color),
                ], spacing=2, expand=True),
                ft.Container(
                    content=ft.Icon(ft.Icons.ACCOUNT_CIRCLE_ROUNDED, size=48, color=AppColors.PRIMARY),
                    width=52, height=52,
                    border_radius=26,
                    bgcolor=ft.Colors.with_opacity(0.15, AppColors.PRIMARY),
                    alignment=ft.Alignment.CENTER,
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ]),
        padding=ft.Padding(20, 15, 20, 10),
    )

    # ═══════════════════════════════════════════════════════════════════════
    # 2. BURN RATE WIDGET — Elemento visual principal
    # ═══════════════════════════════════════════════════════════════════════
    saude = burn["saude_meta"]
    limite = burn["limite_diario"]
    dias_rest = burn["dias_restantes"]
    sobra = burn["sobra_prevista"]
    is_teto = burn["is_teto"]

    # Cor semafórica
    if saude >= 0.7:
        saude_color = AppColors.INCOME       # Verde
        saude_label = "Excelente"
        saude_emoji = "🟢"
    elif saude > 0.4:
        saude_color = "#FFC107"               # Amarelo
        saude_label = "Atenção"
        saude_emoji = "🟡"
    else:
        saude_color = AppColors.EXPENSE       # Vermelho
        saude_label = "Crítico"
        saude_emoji = "🔴"

    burn_rate_widget = ft.Container(
        content=ft.Column([
            # Label
            ft.Row([
                ft.Text("LIMITE DIÁRIO", size=11, weight="bold", color=sub_color),
                ft.Container(
                    content=ft.Text("TETO" if is_teto else "", size=9, color="black", weight="bold"),
                    bgcolor=ft.Colors.YELLOW_400 if is_teto else "transparent",
                    padding=ft.Padding(6, 2, 6, 2),
                    border_radius=4,
                    visible=is_teto,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),

            # Valor grande
            ft.Text(
                f"R$ {limite:,.2f}",
                size=44,
                weight=ft.FontWeight.BOLD,
                color=saude_color,
                text_align=ft.TextAlign.CENTER,
            ),

            # Barra de progresso
            ft.Container(
                content=ft.ProgressBar(
                    value=saude,
                    color=saude_color,
                    bgcolor=ft.Colors.with_opacity(0.12, saude_color),
                    bar_height=14,
                    border_radius=7,
                ),
                padding=ft.Padding(10, 0, 10, 0),
            ),

            # Info abaixo da barra
            ft.Row([
                ft.Text(f"{saude_emoji} {saude_label} ({saude*100:.0f}%)", size=12, color=saude_color, weight="bold"),
                ft.Text(f"{dias_rest} dias restantes", size=11, color=sub_color),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

            # Sobra prevista
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.SAVINGS_ROUNDED, size=16, color=AppColors.INCOME if sobra >= 0 else AppColors.EXPENSE),
                    ft.Text(
                        f"Sobra prevista: R$ {sobra:,.2f}",
                        size=12,
                        color=AppColors.INCOME if sobra >= 0 else AppColors.EXPENSE,
                        weight="bold",
                    ),
                ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                bgcolor=ft.Colors.with_opacity(0.08, AppColors.INCOME if sobra >= 0 else AppColors.EXPENSE),
                border_radius=8,
                padding=ft.Padding(12, 6, 12, 6),
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        padding=20,
        bgcolor=surface_bg,
        border_radius=20,
        border=ft.Border.all(1, border_color),
        shadow=ft.BoxShadow(
            spread_radius=0, blur_radius=12,
            color=ft.Colors.with_opacity(0.08 if is_dark else 0.04, "#000000"),
        ),
    )

    # ═══════════════════════════════════════════════════════════════════════
    # 3. QUICK ACTIONS — Botões circulares de ação rápida
    # ═══════════════════════════════════════════════════════════════════════
    def make_quick_action(icon, label, color, on_click_handler):
        return ft.Column([
            ft.Container(
                content=ft.Icon(icon, size=28, color="#FFFFFF"),
                width=58, height=58,
                border_radius=29,
                bgcolor=color,
                alignment=ft.Alignment.CENTER,
                on_click=on_click_handler,
                ink=True,
                shadow=ft.BoxShadow(
                    spread_radius=0, blur_radius=8,
                    color=ft.Colors.with_opacity(0.25, color),
                ),
            ),
            ft.Text(label, size=11, color=sub_color, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.W_500),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6)

    quick_actions = ft.Container(
        content=ft.Row([
            make_quick_action(
                ft.Icons.ADD_SHOPPING_CART_ROUNDED, "Novo\nGasto",
                AppColors.EXPENSE, on_add_expense,
            ),
            make_quick_action(
                ft.Icons.ATTACH_MONEY_ROUNDED, "Nova\nReceita",
                AppColors.INCOME, on_add_expense,
            ),
            make_quick_action(
                ft.Icons.RECEIPT_LONG_ROUNDED, "Pagar\nConta",
                "#FF9800", lambda _: on_pay_bill() if on_pay_bill else None,
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
        padding=ft.Padding(10, 12, 10, 12),
        bgcolor=surface_bg,
        border_radius=16,
        border=ft.Border.all(1, border_color),
    )

    # ═══════════════════════════════════════════════════════════════════════
    # 4. ALERTA DE CONTAS PRÓXIMAS (Urgency Widget)
    # ═══════════════════════════════════════════════════════════════════════
    urgency_widget = ft.Container(visible=False)  # Invisível se não houver contas

    if upcoming["count"] > 0:
        bill_items = []
        for bill in upcoming["bills"]:
            bill_items.append(
                ft.Row([
                    ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=14, color="#FF9800"),
                    ft.Text(bill.description, size=12, color=text_color, expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(f"R$ {bill.amount:,.2f}", size=12, color=AppColors.EXPENSE, weight="bold"),
                ], spacing=8)
            )

        urgency_widget = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE_ROUNDED, size=20, color="#FF9800"),
                    ft.Text(
                        f"{upcoming['count']} conta{'s' if upcoming['count'] > 1 else ''} pendente{'s' if upcoming['count'] > 1 else ''}!",
                        size=14, weight="bold", color="#FF9800", expand=True,
                    ),
                    ft.Text(f"R$ {upcoming['total']:,.2f}", size=14, weight="bold", color=AppColors.EXPENSE),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=4),
                ft.Column(bill_items, spacing=4),
                ft.Container(height=6),
                ft.Container(
                    content=ft.Text("Ver Contas →", size=12, color=AppColors.PRIMARY, weight="bold"),
                    on_click=lambda _: on_pay_bill() if on_pay_bill else None,
                    ink=True,
                    alignment=ft.Alignment.CENTER_RIGHT,
                ),
            ]),
            padding=16,
            bgcolor=ft.Colors.with_opacity(0.06, "#FF9800"),
            border_radius=16,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, "#FF9800")),
        )

    # ═══════════════════════════════════════════════════════════════════════
    # 5. RESUMO FINANCEIRO (Cards compactos)
    # ═══════════════════════════════════════════════════════════════════════
    balance_color = AppColors.INCOME if balance >= 0 else AppColors.EXPENSE
    summary_cards = ft.Column([
        create_summary_card("Saldo do Mês", f"R$ {balance:,.2f}", ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, balance_color, is_dark),
        ft.Row([
            ft.Container(
                create_summary_card("Receitas", f"R$ {income:,.2f}", ft.Icons.TRENDING_UP_ROUNDED, AppColors.INCOME, is_dark),
                expand=True,
            ),
            ft.Container(
                create_summary_card("Despesas", f"R$ {expense:,.2f}", ft.Icons.TRENDING_DOWN_ROUNDED, AppColors.EXPENSE, is_dark),
                expand=True,
            ),
        ], spacing=10),
    ], spacing=10)

    # ═══════════════════════════════════════════════════════════════════════
    # 6. ÚLTIMAS TRANSAÇÕES
    # ═══════════════════════════════════════════════════════════════════════
    recent_txns = data.get_transactions()[:5]
    txn_cards = []
    for txn in recent_txns:
        cat = data.get_category_by_id(txn.category_id)
        txn_cards.append(create_transaction_card(txn, cat, is_dark, on_edit_txn, on_delete_txn))

    if not txn_cards:
        txn_cards.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.RECEIPT_LONG_ROUNDED, size=36, color=sub_color),
                    ft.Text("Nenhuma transação registrada", size=13, color=sub_color),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                height=100, alignment=ft.Alignment.CENTER,
            )
        )

    transactions_section = ft.Container(
        content=ft.Column([
            ft.Text("Últimas Transações", size=16, weight=ft.FontWeight.W_600, color=text_color),
            ft.Column(txn_cards, spacing=8),
        ], spacing=10),
        padding=16,
        border_radius=16,
        bgcolor=card_bg,
        border=ft.Border.all(1, border_color),
    )

    # ═══════════════════════════════════════════════════════════════════════
    # LAYOUT FINAL
    # ═══════════════════════════════════════════════════════════════════════
    return ft.Container(
        content=ft.Column(
            [
                hero_header,
                ft.Container(
                    content=ft.Column([
                        burn_rate_widget,
                        ft.Container(height=6),
                        quick_actions,
                        ft.Container(height=6),
                        urgency_widget,
                        ft.Container(height=6),
                        summary_cards,
                        ft.Container(height=6),
                        transactions_section,
                    ], spacing=0),
                    padding=ft.Padding(16, 0, 16, 20),
                ),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        expand=True,
        bgcolor=bg_color,
    )
