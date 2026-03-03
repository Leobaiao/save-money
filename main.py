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
    
    # Configuração para Android Layout
    page.window.width = 450
    page.window.height = 800
    page.padding = 0
    
    # --- GERENCIADOR DE DADOS FINANCEIROS ---
    finance_data = FinanceData()

    # Estado reativo simples para o tema
    is_dark = finance_data.settings.get("is_dark", True)

    def apply_theme():
        nonlocal is_dark
        page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        theme_factory = get_dark_theme if is_dark else get_light_theme
        page.theme = theme_factory()
        page.dark_theme = get_dark_theme()
        page.update()

    apply_theme()

    # --- QUICK EXPENSE FAB ---
    async def open_quick_expense(e):
        tipo_toggle = ft.SegmentedButton(
            segments=[
                ft.Segment(value="despesa", label=ft.Text("Gasto"), icon=ft.Icon(ft.Icons.TRENDING_DOWN_ROUNDED)),
                ft.Segment(value="receita", label=ft.Text("Lucro"), icon=ft.Icon(ft.Icons.TRENDING_UP_ROUNDED)),
            ],
            selected={"despesa"},
            allow_multiple_selection=False,
            selected_icon=ft.Icon(ft.Icons.CHECK),
        )

        loja_input = ft.TextField(
            label="Onde / De quem?",
            prefix_icon=ft.Icons.STORE_ROUNDED,
            border_radius=12,
            focused_border_color=AppColors.PRIMARY,
            text_size=14,
        )

        valor_input = ft.TextField(
            label="Valor",
            prefix=ft.Text("R$ "),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=12,
            focused_border_color=AppColors.PRIMARY,
            text_size=16,
            text_style=ft.TextStyle(weight="bold"),
        )

        desc_input = ft.TextField(
            label="Descrição (Opcional)",
            prefix_icon=ft.Icons.NOTES_ROUNDED,
            border_radius=12,
            focused_border_color=AppColors.PRIMARY,
            multiline=True,
            min_lines=1,
            max_lines=3,
            text_size=13,
        )
        
        async def save_quick(e):
            if not valor_input.value or not loja_input.value:
                page.overlay.append(ft.SnackBar(ft.Text("Preencha Loja e Valor!", color="white"), bgcolor=AppColors.EXPENSE, open=True))
                page.update()
                return

            try:
                val = float(valor_input.value.replace(",", "."))
                tipo = list(tipo_toggle.selected)[0]
                
                final_desc = loja_input.value
                if desc_input.value:
                    final_desc += f" ({desc_input.value})"

                finance_data.add_transaction(Transaction(
                    description=final_desc,
                    amount=val,
                    type=tipo,
                    category_id="cat_other_in" if tipo == "receita" else "cat_other_out"
                ))
                
                # Fechar bottom sheet
                for ctrl in page.overlay:
                    if isinstance(ctrl, ft.BottomSheet):
                        ctrl.open = False
                await atualizar_ui()
                page.overlay.append(ft.SnackBar(
                    ft.Text(f"{'Receita' if tipo == 'receita' else 'Gasto'} registrado!"), 
                    bgcolor=AppColors.INCOME if tipo == "receita" else AppColors.PRIMARY, 
                    open=True
                ))
                page.update()
            except ValueError:
                page.overlay.append(ft.SnackBar(ft.Text("Valor inválido!", color="white"), bgcolor=AppColors.EXPENSE, open=True))
                page.update()

        bs = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.Row([
                            ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED, color=AppColors.PRIMARY),
                            ft.Text("NOVA TRANSAÇÃO RÁPIDA", size=16, weight="bold", color=AppColors.PRIMARY),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                        tipo_toggle,
                        loja_input,
                        valor_input,
                        desc_input,
                        ft.Button(
                            "Registrar Agora",
                            icon=ft.Icons.SAVE_ROUNDED,
                            on_click=save_quick,
                            expand=True,
                            style=ft.ButtonStyle(
                                bgcolor=AppColors.PRIMARY,
                                color="white",
                                padding=15,
                                shape=ft.RoundedRectangleBorder(radius=12),
                            ),
                        ),
                        ft.Container(height=10),
                    ],
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                ),
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
    async def toggle_theme():
        nonlocal is_dark
        is_dark = not is_dark
        finance_data.settings["is_dark"] = is_dark
        finance_data.save()
        apply_theme()
        await atualizar_ui()

    async def on_nav_change(e):
        await render_view(e.control.selected_index)

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

    async def on_nav_change_direct(idx):
        page.navigation_bar.selected_index = idx
        await render_view(idx)

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD_ROUNDED, label="Home"),
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

ft.run(main)
