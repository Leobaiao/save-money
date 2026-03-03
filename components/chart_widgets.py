import flet as ft
from theme.app_theme import AppColors, AppStyle

MONTH_NAMES = [
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez",
]


def create_bar_chart(
    monthly_data: list[dict],
    is_dark: bool,
    height: int = 280,
) -> ft.Container:
    """Gráfico de barras comparativo receita vs despesa por mês (nativo Flet)."""

    bg_color = AppColors.DARK_CARD if is_dark else AppColors.LIGHT_CARD
    text_color = AppColors.DARK_TEXT if is_dark else AppColors.LIGHT_TEXT
    sub_color = AppColors.DARK_TEXT_SECONDARY if is_dark else AppColors.LIGHT_TEXT_SECONDARY
    border_color = AppColors.DARK_BORDER if is_dark else AppColors.LIGHT_BORDER

    if not monthly_data:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.BAR_CHART_ROUNDED, size=48, color=sub_color),
                    ft.Text("Sem dados para exibir", size=14, color=sub_color),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=AppStyle.CARD_PADDING,
            border_radius=AppStyle.BORDER_RADIUS,
            bgcolor=bg_color,
            border=ft.border.all(1, border_color),
            height=height + 80,
            alignment=ft.Alignment.CENTER,
        )

    max_val = max(
        (max(d.get("income", 0), d.get("expense", 0)) for d in monthly_data),
        default=100,
    )
    max_val = max(max_val, 1)
    bar_height = height - 40  # reserva espaço para label

    def make_bar(color: str, h: int) -> ft.Container:
        """Retorna uma barra vertical com altura proporcional."""
        return ft.Container(
            width=13,
            height=max(h, 2),
            bgcolor=color,
            border_radius=ft.border_radius.only(top_left=3, top_right=3),
        )

    def make_bar_group(d: dict) -> ft.Column:
        income = d.get("income", 0)
        expense = d.get("expense", 0)
        month_idx = d.get("month", 1) - 1
        label = MONTH_NAMES[month_idx]

        income_h = int((income / max_val) * bar_height)
        expense_h = int((expense / max_val) * bar_height)

        return ft.Column(
            [
                ft.Row(
                    [
                        make_bar(AppColors.INCOME, income_h),
                        make_bar(AppColors.EXPENSE, expense_h),
                    ],
                    spacing=3,
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    height=bar_height,
                ),
                ft.Text(label, size=9, color=sub_color, text_align=ft.TextAlign.CENTER),
            ],
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    bar_groups = [make_bar_group(d) for d in monthly_data]

    legend = ft.Row(
        [
            ft.Row(
                [
                    ft.Container(width=12, height=12, border_radius=3, bgcolor=AppColors.INCOME),
                    ft.Text("Receita", size=12, color=sub_color),
                ],
                spacing=6,
            ),
            ft.Row(
                [
                    ft.Container(width=12, height=12, border_radius=3, bgcolor=AppColors.EXPENSE),
                    ft.Text("Despesa", size=12, color=sub_color),
                ],
                spacing=6,
            ),
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    bar_groups,
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    expand=True,
                ),
                legend,
            ],
            spacing=10,
            expand=True,
        ),
        padding=AppStyle.CARD_PADDING,
        border_radius=AppStyle.BORDER_RADIUS,
        bgcolor=bg_color,
        border=ft.border.all(1, border_color),
        height=height + 60,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=AppStyle.SHADOW_BLUR,
            color=ft.Colors.with_opacity(0.08 if is_dark else 0.04, "#000000"),
        ),
    )


def create_pie_chart(
    data: dict[str, float],
    is_dark: bool,
    height: int = 280,
) -> ft.Container:
    """Gráfico de categorias com barras horizontais de proporção."""

    bg_color = AppColors.DARK_CARD if is_dark else AppColors.LIGHT_CARD
    text_color = AppColors.DARK_TEXT if is_dark else AppColors.LIGHT_TEXT
    sub_color = AppColors.DARK_TEXT_SECONDARY if is_dark else AppColors.LIGHT_TEXT_SECONDARY
    border_color = AppColors.DARK_BORDER if is_dark else AppColors.LIGHT_BORDER

    if not data:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.PIE_CHART_OUTLINE_ROUNDED, size=48, color=sub_color),
                    ft.Text("Sem dados para exibir", size=14, color=sub_color),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=AppStyle.CARD_PADDING,
            border_radius=AppStyle.BORDER_RADIUS,
            bgcolor=bg_color,
            border=ft.border.all(1, border_color),
            height=height + 80,
            alignment=ft.Alignment.CENTER,
        )

    total = sum(data.values())
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)

    items = []
    for i, (cat_name, amount) in enumerate(sorted_data):
        color = AppColors.CHART_COLORS[i % len(AppColors.CHART_COLORS)]
        pct = (amount / total * 100) if total > 0 else 0
        filled = max(int(pct * 10), 1)
        empty = max(1000 - filled, 1)

        items.append(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                width=10, height=10,
                                border_radius=3,
                                bgcolor=color,
                            ),
                            ft.Text(
                                cat_name,
                                size=12,
                                color=text_color,
                                expand=True,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                f"{pct:.1f}%",
                                size=12,
                                color=color,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(f"R$ {amount:,.2f}", size=11, color=sub_color),
                        ],
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        [
                            ft.Container(
                                expand=filled,
                                height=7,
                                bgcolor=color,
                                border_radius=ft.border_radius.only(
                                    top_left=4, bottom_left=4,
                                    top_right=4 if pct >= 99 else 0,
                                    bottom_right=4 if pct >= 99 else 0,
                                ),
                            ),
                            ft.Container(
                                expand=empty,
                                height=7,
                                bgcolor=ft.Colors.with_opacity(0.08 if is_dark else 0.06, color),
                                border_radius=ft.border_radius.only(
                                    top_right=4, bottom_right=4,
                                ),
                            ),
                        ],
                        spacing=0,
                    ),
                ],
                spacing=4,
            )
        )

    return ft.Container(
        content=ft.Column(
            items,
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=AppStyle.CARD_PADDING,
        border_radius=AppStyle.BORDER_RADIUS,
        bgcolor=bg_color,
        border=ft.border.all(1, border_color),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=AppStyle.SHADOW_BLUR,
            color=ft.Colors.with_opacity(0.08 if is_dark else 0.04, "#000000"),
        ),
    )
