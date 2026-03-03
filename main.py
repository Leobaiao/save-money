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
    page.title = "SaveMoney - Burn Rate"
    
    # Configuração Inicial de Tema
    is_dark = True # Padrão
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = get_dark_theme()
    page.dark_theme = get_dark_theme()
    
    page.window.width = 450
    page.window.height = 800
    page.padding = 0 # Padding controlado pelas páginas
    
    # --- GERENCIADOR DE DADOS FINANCEIROS ---
    finance_data = FinanceData()

    # --- PERSISTÊNCIA (SharedPreferences) ---
    async def get_state():
        try:
            state = await page.shared_preferences.get("user_data")
            if state:
                return json.loads(state)
        except Exception:
            pass
        return {
            "dia_pag": 5, "saldo": 0.0, "meta": 0.0, "teto": 0.0, "contas": []
        }

    async def save_state(data):
        await page.shared_preferences.set("user_data", json.dumps(data))

    # --- LÓGICA ECONÔMICA (BURN RATE) ---
    async def calcular_limite():
        data = await get_state()
        hoje = date.today()
        
        proximo_pag = date(hoje.year, hoje.month, data["dia_pag"])
        if hoje.day >= data["dia_pag"]:
            if hoje.month < 12:
                proximo_pag = date(hoje.year, hoje.month + 1, data["dia_pag"])
            else:
                proximo_pag = date(hoje.year + 1, 1, data["dia_pag"])
        
        dias_restantes = max(1, (proximo_pag - hoje).days)
        
        if data.get("contas"):
            for c in data["contas"]:
                finance_data.add_transaction(Transaction(
                    description=c["nome"],
                    amount=float(c["valor"]),
                    type="despesa",
                    category_id="cat_bills",
                    is_paid=c["pago"],
                    is_fixed=True
                ))
            data["contas"] = []
            await save_state(data)

        # Migração de saldo legado (se houver saldo no SharedPreferences mas nenhuma transação)
        current_total = finance_data.get_total_balance()
        if data.get("saldo", 0) > 0 and len(finance_data.transactions) == 0:
            finance_data.add_transaction(Transaction(
                description="Saldo Inicial (Migração)",
                amount=data["saldo"],
                type="receita",
                category_id="cat_other_in"
            ))
            data["saldo"] = 0 # Zeramos para usar apenas o FinanceData daqui pra frente
            await save_state(data)

        # Buscar saldo real do FinanceData
        saldo_real = finance_data.get_total_balance()
        
        # Buscar contas não pagas do FinanceData
        contas_abertas_list = finance_data.get_bills(is_paid=False)
        contas_abertas = sum(t.amount for t in contas_abertas_list)
        
        disponivel_total = saldo_real - contas_abertas
        limite_com_meta = max(0, (disponivel_total - data["meta"]) / dias_restantes)

        teto = data["teto"]
        exibido = min(limite_com_meta, teto) if teto > 0 else limite_com_meta
        is_teto = teto > 0 and limite_com_meta > teto

        sobra_prevista = disponivel_total - (exibido * dias_restantes)
        meta = data["meta"]
        if meta > 0:
            saude = min(1.0, max(0.0, sobra_prevista / meta))
        else:
            saude = 1.0 if sobra_prevista >= 0 else 0.0

        return round(exibido, 2), is_teto, round(contas_abertas, 2), round(sobra_prevista, 2), saude

    # --- COMPONENTES PERSISTENTES DA HOME (BURN RATE) ---
    display_limite = ft.Text("R$ 0,00", size=48, weight="bold", color=AppColors.INCOME)
    badge_teto = ft.Container(
        content=ft.Text("TETO ATIVO", size=10, color="black", weight="bold"), 
        bgcolor=ft.Colors.YELLOW_400, 
        padding=ft.padding.symmetric(horizontal=8, vertical=4), 
        border_radius=5, 
        visible=False
    )
    
    bar_saude = ft.ProgressBar(width=300, height=8, color=AppColors.INCOME, bgcolor=ft.Colors.with_opacity(0.1, AppColors.PRIMARY))
    txt_saude_info = ft.Text("Saúde da Meta: 0% | Sobra: R$ 0,00", size=12, color=AppColors.DARK_TEXT_SECONDARY)
    
    input_valor = ft.TextField(
        label="Valor do Gasto", 
        prefix=ft.Text("R$ "), 
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=AppStyle.BORDER_RADIUS_SM,
        focused_border_color=AppColors.PRIMARY
    )

    async def btn_registrar(e):
        if not input_valor.value: return
        data = await get_state()
        try:
            valor = float(input_valor.value.replace(",", "."))
        except ValueError: return
            
        # Registrar transação no histórico JSON
        finance_data.add_transaction(Transaction(
            description="Gasto Rápido (Home)",
            amount=valor,
            type="despesa",
            category_id="cat_other_out"
        ))
        
        input_valor.value = ""
        await atualizar_ui()
        
        snackbar = ft.SnackBar(ft.Text("Gasto registrado!", color="white"), bgcolor=AppColors.INCOME)
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()

    # --- ATUALIZAÇÃO GLOBAL ---
    async def atualizar_ui():
        limite, teto_ativo, total_contas, sobra, saude = await calcular_limite()
        display_limite.value = f"R$ {limite:,.2f}"
        badge_teto.visible = teto_ativo
        
        bar_saude.value = saude
        bar_saude.color = AppColors.INCOME if saude >= 0.9 else ft.Colors.YELLOW_400 if saude > 0.4 else AppColors.EXPENSE
        txt_saude_info.value = f"Saúde da Meta: {saude*100:.0f}% | Sobra Prevista: R$ {sobra:,.2f}"
        
        await render_view(page.navigation_bar.selected_index)

    def get_burn_rate_header():
        return ft.Container(
            content=ft.Column([
                ft.Text("LIMITE PARA HOJE", size=12, weight="bold", color=AppColors.DARK_TEXT_SECONDARY),
                ft.Row([display_limite, badge_teto], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=5),
                txt_saude_info,
                bar_saude,
                ft.Container(height=15),
                ft.Row([
                    input_valor,
                    ft.IconButton(ft.Icons.CHECK_CIRCLE_ROUNDED, icon_color=AppColors.INCOME, icon_size=40, on_click=btn_registrar)
                ], alignment=ft.MainAxisAlignment.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            padding=20,
            bgcolor=AppColors.DARK_SURFACE if is_dark else AppColors.LIGHT_SURFACE,
            border_radius=AppStyle.BORDER_RADIUS,
            border=ft.border.all(1, AppColors.DARK_BORDER if is_dark else AppColors.LIGHT_BORDER),
        )

    # --- NAVEGAÇÃO ---
    async def toggle_theme():
        nonlocal is_dark
        is_dark = not is_dark
        page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        page.theme = get_dark_theme() if is_dark else get_light_theme()
        page.update()
        await atualizar_ui()

    async def render_view(index):
        page.controls.clear()
        data = await get_state()
        
        if index == 0: # Dashboard (Home)
            page.add(build_dashboard(
                finance_data, is_dark, 
                header_view=get_burn_rate_header()
            ))
        elif index == 1: # Histórico
            page.add(build_transactions_page(finance_data, is_dark, page, on_refresh=atualizar_ui))
        elif index == 2: # Relatórios
            page.add(build_reports_page(finance_data, is_dark, page, on_refresh=atualizar_ui))
        elif index == 3: # Contas
            page.add(build_bills_page(data, finance_data, is_dark, page, save_state, atualizar_ui, render_view))
        elif index == 4: # Ajustes
            page.add(build_settings_page(data, finance_data, is_dark, page, save_state, atualizar_ui, toggle_theme))
            
        page.update()

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD_ROUNDED, label="Resumo"),
            ft.NavigationBarDestination(icon=ft.Icons.HISTORY_ROUNDED, label="Histórico"),
            ft.NavigationBarDestination(icon=ft.Icons.INSERT_CHART_ROUNDED, label="Relatórios"),
            ft.NavigationBarDestination(icon=ft.Icons.RECEIPT_LONG_ROUNDED, label="Contas"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS_ROUNDED, label="Ajustes"),
        ],
        on_change=lambda e: render_view(e.control.selected_index),
        bgcolor=AppColors.DARK_SURFACE if is_dark else AppColors.LIGHT_SURFACE,
        selected_index=0
    )

    await atualizar_ui()

ft.run(main)
