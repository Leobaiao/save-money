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
from pages.profile import build_profile_page
from pages.mentor import build_mentor_page

async def main(page: ft.Page):
    page.title = "Save Money"
    
    # --- CONFIGURAÇÃO ANDROID NATIVA ---
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    
    # Suporte ao botão voltar físico do Android
    async def on_back(e):
        if page.navigation_bar.selected_index != 0:
            page.navigation_bar.selected_index = 0
            await on_nav_change_direct(0)
        else:
            # Se já estiver na home, permite o comportamento padrão de fechar/minimizar
            # No Flet v0.20+, para NÃO fechar o app, você não chama nada.
            # Se quiser fechar, o Flet no Android costuma fechar se o evento não for 'cancelado'.
            # Mas não há 'e.prevent_default()' aqui.
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
    async def open_quick_expense(e, initial_type="despesa"):
        tipo_state = {"value": initial_type}
        
        is_income_init = initial_type == "receita"
        tipo_label = ft.Text(
            "RECEITA" if is_income_init else "GASTO", 
            size=14, weight="bold", 
            color=AppColors.INCOME if is_income_init else AppColors.EXPENSE
        )
        
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
            icon=ft.Icons.TRENDING_UP_ROUNDED if is_income_init else ft.Icons.TRENDING_DOWN_ROUNDED,
            icon_color=AppColors.INCOME if is_income_init else AppColors.EXPENSE,
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
                    description=loja_input.value or "Registro Rápido",
                    amount=val,
                    type=tipo,
                    category_id=category_dropdown.value,
                    notes=notes_input.value
                ))
                bs.open = False
                await atualizar_ui()
                page.update()
            except ValueError:
                pass

        # Categorias baseadas no tipo inicial
        categories = finance_data.get_categories_by_type(tipo_state["value"])
        category_dropdown = ft.Dropdown(
            label="Categoria",
            value=categories[0].id if categories else None,
            options=[ft.dropdown.Option(c.id, c.name) for c in categories],
            border_radius=12,
            focused_border_color=AppColors.PRIMARY,
            expand=True
        )

        def update_categories(ev=None):
            new_cats = finance_data.get_categories_by_type(tipo_state["value"])
            category_dropdown.options = [ft.dropdown.Option(c.id, c.name) for c in new_cats]
            category_dropdown.value = new_cats[0].id if new_cats else None
            page.update()

        # Sobrescrever toggle_tipo para atualizar categorias
        original_toggle = toggle_tipo
        def toggle_tipo_enhanced(ev):
            original_toggle(ev)
            update_categories()
        
        toggle_btn.on_click = toggle_tipo_enhanced

        notes_input = ft.TextField(
            label="Observações / Descrição Detalhada",
            prefix_icon=ft.Icons.DESCRIPTION_ROUNDED,
            border_radius=12,
            focused_border_color=AppColors.PRIMARY,
            multiline=True,
            min_lines=1,
            max_lines=3
        )

        bs = ft.BottomSheet(
            ft.Container(
                ft.Column([
                    ft.Container(
                        width=40, height=4, 
                        bgcolor=AppColors.DARK_BORDER if is_dark else AppColors.LIGHT_BORDER,
                        border_radius=2,
                        margin=ft.Margin.only(bottom=19)
                    ),
                    ft.Row([toggle_btn, tipo_label], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([category_dropdown], spacing=10),
                    ft.Row([loja_input, valor_input], spacing=10),
                    notes_input,
                    ft.Container(
                        content=ft.Button(
                            "Salvar Registro", 
                            on_click=save_quick, 
                            bgcolor=AppColors.PRIMARY, 
                            color="white",
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                            icon = ft.Icons.SAVE_ROUNDED,
                            icon_color="white",
                        ),
                        expand=True,
                    ),
                ],
                spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.ADAPTIVE),
                padding=ft.Padding(25, 20, 25, 20),
                bgcolor=AppColors.DARK_SURFACE if is_dark else ft.Colors.WHITE,
                border_radius=ft.BorderRadius(24, 24, 0, 0),
                expand=True,
            ),
            open=True,
            draggable=True,
        )
        page.overlay.append(bs)
        page.update()

    # --- ATUALIZAR UI ---
    async def atualizar_ui(e=None):
        await render_view(page.navigation_bar.selected_index)

    # --- NAVEGAÇÃO ---
    async def render_view(index):
        # Mostrar Loading
        from components.loading_spinner import LoadingSpinner
        page.controls.clear()
        page.add(ft.Container(height=AppStyle.SAFE_TOP_PADDING))
        page.add(LoadingSpinner("Preparando o Save Money..."))
        page.update()
        
        # Simular delay para UX (Opcional, mas bom para ver o spinner se for muito rápido)
        # import asyncio
        # await asyncio.sleep(0.3)
        
        page.controls.clear()
        # Safe Area Spacer
        page.add(ft.Container(height=AppStyle.SAFE_TOP_PADDING))
        
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

        async def handle_edit_txn(txn_id):
            # Simplificação: vai para a página de transações
            await on_nav_change_direct(1)

        async def handle_delete_txn(txn_id):
            async def confirm(e):
                finance_data.delete_transaction(txn_id)
                confirm_dialog.open = False
                page.update()
                await atualizar_ui()

            confirm_dialog = ft.AlertDialog(
                title=ft.Text("Confirmar Exclusão"),
                content=ft.Text("Tem certeza que deseja excluir esta transação?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: setattr(confirm_dialog, "open", False) or page.update()),
                    ft.Button("Excluir", bgcolor=AppColors.EXPENSE, color="white", on_click=confirm),
                ],
            )
            page.overlay.append(confirm_dialog)
            confirm_dialog.open = True
            page.update()

        async def go_bills(e=None):
            await on_nav_change_direct(3)

        async def go_profile(e=None):
            await on_nav_change_direct(5)

        if index == 0:
            page.add(build_dashboard(
                finance_data, is_dark, page,
                on_add_expense=lambda e, t="despesa": page.run_task(open_quick_expense, e, t),
                on_pay_bill=lambda e: page.run_task(go_bills, e),
                on_refresh=atualizar_ui,
                on_profile_click=lambda e: page.run_task(go_profile, e),
                on_edit_txn=handle_edit_txn,
                on_delete_txn=handle_delete_txn,
            ))
        elif index == 1:
            page.add(build_transactions_page(finance_data, is_dark, page, on_refresh=atualizar_ui))
        elif index == 2:
            page.add(build_reports_page(finance_data, is_dark, page, on_refresh=atualizar_ui))
        elif index == 3:
            page.add(build_bills_page(legacy_data, finance_data, is_dark, page, save_state_legacy, atualizar_ui, render_view))
        elif index == 4:
            page.add(build_settings_page(legacy_data, finance_data, is_dark, page, save_state_legacy, atualizar_ui, toggle_theme))
        elif index == 5:
            page.add(build_profile_page(finance_data, is_dark, page, on_refresh=atualizar_ui))
        elif index == 6:
            page.add(build_mentor_page(finance_data, is_dark, page))
            
        # Ocultar FAB na página do Mentor para não sobrepor o botão de enviar
        if page.floating_action_button:
            page.floating_action_button.visible = (index != 6)
            
        page.update()

    async def toggle_theme(e=None):
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
            ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE_ROUNDED, selected_icon=ft.Icons.PERSON_ROUNDED, label="Perfil"),
            ft.NavigationBarDestination(icon=ft.Icons.AUTO_AWESOME_OUTLINED, selected_icon=ft.Icons.AUTO_AWESOME_ROUNDED, label="Mentor"),
        ],
        on_change=lambda e: page.run_task(on_nav_change, e),
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
    ft.app(target=main, assets_dir="assets")
