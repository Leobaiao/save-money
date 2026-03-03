import flet as ft

# ─── Paleta de Cores ───────────────────────────────────────────────────────────
class AppColors:
    # Cores principais
    PRIMARY = "#6C63FF"
    PRIMARY_LIGHT = "#8B83FF"
    PRIMARY_DARK = "#4A42D4"

    # Cores de status
    INCOME = "#00C853"
    INCOME_LIGHT = "#69F0AE"
    EXPENSE = "#FF5252"
    EXPENSE_LIGHT = "#FF8A80"

    # Cores de fundo (Dark)
    DARK_BG = "#0F0F1A"
    DARK_SURFACE = "#1A1A2E"
    DARK_CARD = "#222240"
    DARK_BORDER = "#2A2A4A"
    DARK_TEXT = "#E8E8F0"
    DARK_TEXT_SECONDARY = "#9E9EB8"

    # Cores de fundo (Light)
    LIGHT_BG = "#F5F5FA"
    LIGHT_SURFACE = "#FFFFFF"
    LIGHT_CARD = "#FFFFFF"
    LIGHT_BORDER = "#E0E0EA"
    LIGHT_TEXT = "#1A1A2E"
    LIGHT_TEXT_SECONDARY = "#6B6B80"

    # Categorias (cores para gráficos)
    CHART_COLORS = [
        "#6C63FF", "#FF6B6B", "#4ECDC4", "#FFE66D",
        "#A8E6CF", "#FF8B94", "#DDA0DD", "#98D8C8",
        "#F7DC6F", "#BB8FCE", "#85C1E9", "#F0B27A",
    ]


# ─── Constantes de Estilo ──────────────────────────────────────────────────────
class AppStyle:
    BORDER_RADIUS = 16
    BORDER_RADIUS_SM = 10
    BORDER_RADIUS_LG = 20
    CARD_PADDING = 20
    PAGE_PADDING = 30
    NAV_WIDTH = 80
    NAV_WIDTH_EXPANDED = 220
    ANIMATION_DURATION = 300
    SHADOW_BLUR = 20
    SHADOW_SPREAD = 2


def get_dark_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=AppColors.PRIMARY,
        color_scheme=ft.ColorScheme(
            primary=AppColors.PRIMARY,
            on_primary="#FFFFFF",
            surface=AppColors.DARK_SURFACE,
            on_surface=AppColors.DARK_TEXT,
            surface_container_lowest=AppColors.DARK_BG,
        ),
        text_theme=ft.TextTheme(
            body_large=ft.TextStyle(color=AppColors.DARK_TEXT),
            body_medium=ft.TextStyle(color=AppColors.DARK_TEXT),
            body_small=ft.TextStyle(color=AppColors.DARK_TEXT_SECONDARY),
            title_large=ft.TextStyle(color=AppColors.DARK_TEXT, weight=ft.FontWeight.BOLD),
            title_medium=ft.TextStyle(color=AppColors.DARK_TEXT, weight=ft.FontWeight.W_600),
        ),
    )


def get_light_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=AppColors.PRIMARY,
        color_scheme=ft.ColorScheme(
            primary=AppColors.PRIMARY,
            on_primary="#FFFFFF",
            surface=AppColors.LIGHT_SURFACE,
            on_surface=AppColors.LIGHT_TEXT,
            surface_container_lowest=AppColors.LIGHT_BG,
        ),
        text_theme=ft.TextTheme(
            body_large=ft.TextStyle(color=AppColors.LIGHT_TEXT),
            body_medium=ft.TextStyle(color=AppColors.LIGHT_TEXT),
            body_small=ft.TextStyle(color=AppColors.LIGHT_TEXT_SECONDARY),
            title_large=ft.TextStyle(color=AppColors.LIGHT_TEXT, weight=ft.FontWeight.BOLD),
            title_medium=ft.TextStyle(color=AppColors.LIGHT_TEXT, weight=ft.FontWeight.W_600),
        ),
    )
