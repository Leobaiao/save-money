import flet as ft
from datetime import datetime, date
import json

from models.data_model import FinanceData, Transaction
from theme.app_theme import AppColors, AppStyle, get_dark_theme, get_light_theme

# Importações de Páginas Modulares
from pages.dashboard import build_dashboard
from pages.transactions import build_transactions_page
from pages.reports import build_reports_page
from pages.bills import build_bills_page
from pages.settings import build_settings_page

async def main(page: ft.Page):
    page.title = "SaveMoney"
    
    # --- CONFIGURAÇÃO ANDROID NATIVA ---
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    
    # Suporte ao botão voltar físico do Android
    async def on_back(e):
        if page.navigation_bar.selected_index != 0:
            page.navigation_bar.selected_index = 0
            await render_view(0)
        else:
            # Comportamento padrão: o sistema minimiza ou fecha o app se estiver na Home
            pass
    page.on_back_event = on_back

    # --- GERENCIADOR DE DADOS ---
    finance_data = FinanceData()
    is_dark = finance_data.settings.get("is_dark", True)

    def apply_theme():
        nonlocal is_dark
        page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        theme_factory = get_dark_theme if is_dark else get_light_theme
        page.theme = theme_factory()
        page.dark_theme = get_dark_theme()
        page.update()

    apply_theme()

    # --- REGISTRO RÁPIDO (BOTTOM SHEET) ---
    async def open_quick_expense(e):
        tipo_state = {"value": "despesa"}
        tipo_label = ft.Text("GASTO", size=14, weight="bold", color=AppColors.EXPENSE)
        
        def toggle_tipo(ev):
            if tipo_state["value"] == "despesa":
                tipo_state["value"] = "receita"
                tipo_label.value = "RECEITA"
                tipo_label.color = AppColors.INCOME
                toggle_btn.icon = ft.Icons.TRENDING_UP_ROUNDED
                toggle_btn.icon_color = AppColors.INCOME
            else:
                tipo_state["value"] = "despesa"
                tipo_label.value = "GASTO"
                tipo_label.color = AppColors.EXPENSE
                toggle_btn.icon = ft.Icons.TRENDING_DOWN_ROUNDED
                toggle_btn.icon_color = AppColors.EXPENSE
            page.update()

        toggle_btn = ft.IconButton(
            icon=ft.Icons.TRENDING_DOWN_ROUNDED,
            icon_color=AppColors.EXPENSE,
            icon_size=28,
            on_click=toggle_tipo,
        )
        
        loja_input = ft.TextField(
            label="Local/Loja", 
            prefix_icon=ft.Icons.STORE_ROUNDED, 
            border_radius=12,
            focused_border_color=AppColors.PRIMARY
        )
        
        valor_input = ft.TextField(
            label="Valor", 
            prefix=ft.Text("R$ "), 
            keyboard_type=ft.KeyboardType.NUMBER, 
            border_radius=12,
            focused_border_color=AppColors.PRIMARY,
            text_style=ft.TextStyle(weight="bold")
        )

        async def save_quick(ev):
            if not valor_input.value:
                return
            try:
                val = float(valor_input.value.replace(",", "."))
                tipo = tipo_state["value"]
                finance_data.add_transaction(Transaction(
                    description=loja_input.value or "Gasto Rápido",
                    amount=val,
                    type=tipo,
                    category_id="cat_other_in" if tipo == "receita" else "cat_other_out"
                ))
                bs.open = False
                await atualizar_ui()
                page.update()
            except ValueError:
                pass

        bs = ft.BottomSheet(
            ft.Container(
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED, color=AppColors.PRIMARY),
                        ft.Text("REGISTRO RÁPIDO", size=16, weight="bold", color=AppColors.PRIMARY),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                    ft.Row([toggle_btn, tipo_label], alignment=ft.MainAxisAlignment.CENTER),
                    loja_input,
                    valor_input,
                    ft.ElevatedButton(
                        "Salvar Agora", 
                        on_click=save_quick, 
                        bgcolor=AppColors.PRIMARY, 
                        color="white",
                        expand=True,
                        height=50,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
                    ),
                    ft.Container(height=10)
                ], tight=True, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=25,
                bgcolor=AppColors.DARK_SURFACE if is_dark else ft.Colors.WHITE,
                border_radius=ft.BorderRadius(24, 24, 0, 0),
            ),
            open=True,
        )
        page.overlay.append(bs)
        page.update()

    # --- ATUALIZAR UI ---
    async def atualizar_ui():
        await render_view(page.navigation_bar.selected_index)

    # --- NAVEGAÇÃO ---
    async def render_view(index):
        page.controls.clear()
        
        legacy_data = {
            "dia_pag": finance_data.settings.get("dia_pag", 5),
            "meta": finance_data.settings.get("meta", 0.0),
            "teto": finance_data.settings.get("teto", 0.0),
            "saldo": 0
        }

        async def save_state_legacy(new_data):
            finance_data.settings.update({
                "dia_pag": new_data["dia_pag"],
                "meta": new_data["meta"],
                "teto": new_data["teto"]
            })
            finance_data.save()

        if index == 0:
            page.add(build_dashboard(
                finance_data, is_dark, page,
                on_add_expense=open_quick_expense,
                on_pay_bill=lambda: on_nav_change_direct(3),
                on_refresh=atualizar_ui,
            ))
        elif index == 1:
            page.add(build_transactions_page(finance_data, is_dark, page, on_refresh=atualizar_ui))
        elif index == 2:
            page.add(build_reports_page(finance_data, is_dark, page, on_refresh=atualizar_ui))
        elif index == 3:
            page.add(build_bills_page(legacy_data, finance_data, is_dark, page, save_state_legacy, atualizar_ui, render_view))
        elif index == 4:
            page.add(build_settings_page(legacy_data, finance_data, is_dark, page, save_state_legacy, atualizar_ui, toggle_theme))
            
        page.update()

    async def toggle_theme():
        nonlocal is_dark
        is_dark = not is_dark
        finance_data.settings["is_dark"] = is_dark
        finance_data.save()
        apply_theme()
        await atualizar_ui()

    async def on_nav_change(e):
        await render_view(e.control.selected_index)

    async def on_nav_change_direct(idx):
        page.navigation_bar.selected_index = idx
        await render_view(idx)

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME_ROUNDED, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.LIST_ALT_ROUNDED, label="Extrato"),
            ft.NavigationBarDestination(icon=ft.Icons.INSERT_CHART_OUTLINED, selected_icon=ft.Icons.INSERT_CHART_ROUNDED, label="Análise"),
            ft.NavigationBarDestination(icon=ft.Icons.RECEIPT_LONG_OUTLINED, selected_icon=ft.Icons.RECEIPT_LONG_ROUNDED, label="Contas"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS_ROUNDED, label="Ajustes"),
        ],
        on_change=on_nav_change,
        selected_index=0,
        height=70
    )

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        bgcolor=AppColors.PRIMARY,
        on_click=open_quick_expense,
        tooltip="Registrar Gasto"
    )

    await atualizar_ui()

if __name__ == "__main__":
    ft.app(target=main)
