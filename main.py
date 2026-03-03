import flet as ft
from datetime import datetime, date
import json
import re

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

    # --- LEITOR DE QR CODE ---
    active_scan_target = None

    def on_scan_result(e):
        nonlocal active_scan_target
        if not e.data: return
        
        # Tentar extrair valor (ex: R$ 10,50 ou apenas 10.50)
        price_match = re.search(r"(\d+[,.]\d{2})", e.data)
        if price_match:
            val = price_match.group(1).replace(",", ".")
            if active_scan_target:
                active_scan_target.value = val
                page.update()
        else:
            # Se não achar preço, joga o texto bruto no campo
            if active_scan_target:
                active_scan_target.value = e.data
                page.update()
        
        page.overlay.append(ft.SnackBar(ft.Text(f"Código lido: {e.data[:30]}..."), open=True))
        page.update()

    barcode_scanner = None
    try:
        barcode_scanner = ft.BarcodeScanner(on_result=on_scan_result)
        page.overlay.append(barcode_scanner)
    except AttributeError:
        print("BarcodeScanner não suportado nesta versão do Flet. Ignore os botões de scan.")

    async def start_scan(target_field):
        nonlocal active_scan_target
        if barcode_scanner:
            active_scan_target = target_field
            await barcode_scanner.scan()
        else:
            page.overlay.append(ft.SnackBar(ft.Text("Leitor de QR não suportado. Atualize o Flet!"), open=True))
            page.update()

    # --- COMPONENTES PERSISTENTES DA HOME (BURN RATE) ---
    display_limite = ft.Text("R$ 0,00", size=42, weight="bold", color=AppColors.INCOME)
    badge_teto = ft.Container(
        content=ft.Text("TETO ATIVO", size=9, color="black", weight="bold"),
        bgcolor=ft.Colors.YELLOW_400, 
        padding=ft.Padding(6, 2, 6, 2),
        border_radius=4,
        visible=False
    )
    
    bar_saude = ft.ProgressBar(
        width=320,
        height=12,
        color=AppColors.INCOME,
        bgcolor=ft.Colors.with_opacity(0.1, AppColors.PRIMARY),
        border_radius=6
    )
    txt_saude_info = ft.Text("Saúde da Meta: 0% | Sobra: R$ 0,00", size=11, color=AppColors.DARK_TEXT_SECONDARY)
    
    input_valor = ft.TextField(
        label="Gasto Rápido",
        prefix=ft.Text("R$ "), 
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=12,
        focused_border_color=AppColors.PRIMARY,
        height=50,
        text_size=14,
        content_padding=10
    )

    async def btn_registrar(e):
        if not input_valor.value: return
        try:
            valor = float(input_valor.value.replace(",", "."))
            if valor <= 0: raise ValueError
        except ValueError: return
            
        finance_data.add_transaction(Transaction(
            description="Gasto Rápido (Home)",
            amount=valor,
            type="despesa",
            category_id="cat_other_out"
        ))
        
        input_valor.value = ""
        await atualizar_ui()
        
        page.overlay.append(ft.SnackBar(ft.Text("Gasto registrado!"), bgcolor=AppColors.INCOME, open=True))
        page.update()

    async def open_quick_expense(e):
        # Seleção de Tipo (Gasto vs Lucro)
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
                
                # Combinar loja e descrição se houver descrição
                final_desc = loja_input.value
                if desc_input.value:
                    final_desc += f" ({desc_input.value})"

                finance_data.add_transaction(Transaction(
                    description=final_desc,
                    amount=val,
                    type=tipo,
                    category_id="cat_other_in" if tipo == "receita" else "cat_other_out"
                ))
                
                page.bottom_sheet.open = False
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

        page.bottom_sheet = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.Row([
                            ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED, color=AppColors.PRIMARY),
                            ft.Text("NOVA TRANSAÇÃO RÁPIDA", size=16, weight="bold", color=AppColors.PRIMARY),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                        tipo_toggle,
                        loja_input,
                        ft.Row([
                            ft.Container(valor_input, expand=True),
                            ft.IconButton(
                                ft.Icons.QR_CODE_SCANNER_ROUNDED,
                                icon_color=AppColors.PRIMARY,
                                on_click=lambda _: start_scan(valor_input)
                            )
                        ], spacing=10),
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
        page.update()

    async def atualizar_ui():
        res = finance_data.get_burn_rate_data()

        display_limite.value = f"R$ {res['limite_diario']:,.2f}"
        badge_teto.visible = res['is_teto']
        
        saude = res['saude_meta']
        bar_saude.value = saude
        bar_saude.color = AppColors.INCOME if saude >= 0.8 else ft.Colors.YELLOW_400 if saude > 0.4 else AppColors.EXPENSE
        
        status_txt = "Excelente" if saude >= 0.8 else "Atenção" if saude > 0.4 else "Crítico"
        txt_saude_info.value = f"{status_txt} ({saude*100:.0f}%) | Sobra Prevista: R$ {res['sobra_prevista']:,.2f}"
        
        await render_view(page.navigation_bar.selected_index)

    def get_burn_rate_header():
        nonlocal is_dark
        return ft.Container(
            content=ft.Column([
                ft.Text("BURN RATE DIÁRIO", size=11, weight="bold", color=AppColors.DARK_TEXT_SECONDARY if is_dark else AppColors.LIGHT_TEXT_SECONDARY),
                ft.Row([
                    display_limite, 
                    badge_teto
                ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=5),
                ft.Column([
                    ft.Row([txt_saude_info], alignment=ft.MainAxisAlignment.CENTER),
                    bar_saude,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                ft.Divider(height=30, color=ft.Colors.with_opacity(0.1, ft.Colors.GREY)),
                ft.Row([
                    ft.Container(input_valor, expand=True),
                    ft.IconButton(
                        ft.Icons.ADD_CIRCLE_ROUNDED, 
                        icon_color=AppColors.PRIMARY, 
                        icon_size=40,
                        on_click=btn_registrar
                    )
                ], alignment=ft.MainAxisAlignment.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            padding=20,
            bgcolor=AppColors.DARK_SURFACE if is_dark else ft.Colors.WHITE,
            border_radius=20,
            border=ft.Border.all(1, AppColors.DARK_BORDER if is_dark else AppColors.LIGHT_BORDER),
            margin=ft.Margin(0, 0, 0, 15)
        )

    # Injetar o botão de Scan no header da Home
    def get_burn_rate_header_with_scan():
        header = get_burn_rate_header()
        # O header é um Container com uma Column
        # A última Row tem o input e o botão de add. Vamos mudar para incluir o scan.
        row_inputs = header.content.controls[-1] 
        row_inputs.controls.insert(1, ft.IconButton(
            ft.Icons.QR_CODE_SCANNER_ROUNDED,
            icon_color=AppColors.PRIMARY,
            on_click=lambda _: start_scan(input_valor),
            tooltip="Escanear Nota/Preço"
        ))
        return header

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

        # Helper para passar dados legados enquanto as páginas não são refatoradas
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
            page.add(build_dashboard(finance_data, is_dark, header_view=get_burn_rate_header_with_scan()))
        elif index == 1:
            page.add(build_transactions_page(finance_data, is_dark, page, on_refresh=atualizar_ui))
        elif index == 2:
            page.add(build_reports_page(finance_data, is_dark, page, on_refresh=atualizar_ui))
        elif index == 3:
            page.add(build_bills_page(legacy_data, finance_data, is_dark, page, save_state_legacy, atualizar_ui, render_view))
        elif index == 4:
            page.add(build_settings_page(legacy_data, finance_data, is_dark, page, save_state_legacy, atualizar_ui, toggle_theme))
            
        page.update()

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
