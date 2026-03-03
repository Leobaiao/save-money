import flet as ft
from datetime import datetime, date

async def main(page: ft.Page):
    page.title = "Daily Burn Rate"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 400
    page.window.height = 700
    page.padding = 20

    # --- PERSISTÊNCIA (SharedPreferences) ---
    storage = ft.SharedPreferences()
    page.overlay.append(storage)

    async def get_state():
        state = await storage.get("user_data")
        if state:
            import json
            return json.loads(state)
        return {
            "dia_pag": 5, "saldo": 0.0, "meta": 0.0, "teto": 0.0, "contas": []
        }

    async def save_state(data):
        import json
        await storage.set("user_data", json.dumps(data))

    # --- LÓGICA ECONÔMICA ---
    async def calcular_limite():
        data = await get_state()
        hoje = date.today()
        
        # Próximo pagamento
        proximo_pag = date(hoje.year, hoje.month, data["dia_pag"])
        if hoje.day >= data["dia_pag"]:
            if hoje.month < 12:
                proximo_pag = date(hoje.year, hoje.month + 1, data["dia_pag"])
            else:
                proximo_pag = date(hoje.year + 1, 1, data["dia_pag"])
        
        dias_restantes = (proximo_pag - hoje).days
        dias_restantes = max(1, dias_restantes)

        contas_abertas = sum(float(c['valor']) for c in data["contas"] if not c['pago'])
        
        # Fórmula: Saldo - Contas - Meta
        disponivel = data["saldo"] - contas_abertas - data["meta"]
        limite_real = max(0, disponivel / dias_restantes)

        # Aplicação do Teto
        teto = data["teto"]
        exibido = min(limite_real, teto) if teto > 0 else limite_real
        is_teto = teto > 0 and limite_real > teto

        return round(exibido, 2), is_teto, round(contas_abertas, 2)

    # --- COMPONENTES DE INTERFACE ---
    display_limite = ft.Text("R$ 0,00", size=50, weight="bold", color=ft.Colors.GREEN_ACCENT)
    badge_teto = ft.Container(content=ft.Text("TETO ATIVO", size=10, color="black"), bgcolor=ft.Colors.YELLOW_400, padding=5, border_radius=5, visible=False)
    txt_saldo = ft.Text("Saldo: R$ 0,00", size=16)
    txt_contas = ft.Text("A Pagar: R$ 0,00", size=16, color=ft.Colors.RED_400)

    async def atualizar_ui():
        limite, teto_ativo, total_contas = await calcular_limite()
        data = await get_state()
        display_limite.value = f"R$ {limite:,.2f}"
        badge_teto.visible = teto_ativo
        txt_saldo.value = f"Banco: R$ {data['saldo']:,.2f}"
        txt_contas.value = f"A Pagar: R$ {total_contas:,.2f}"
        await page.update_async()

    # --- AÇÕES ---
    async def btn_registrar(e):
        if not input_valor.value: return
        data = await get_state()
        try:
            valor = float(input_valor.value.replace(",", "."))
        except ValueError:
            return
            
        data["saldo"] -= valor
        await save_state(data)
        input_valor.value = ""
        await atualizar_ui()
        
        snackbar = ft.SnackBar(ft.Text("Gasto registrado!"))
        page.overlay.append(snackbar)
        snackbar.open = True
        await page.update_async()

    input_valor = ft.TextField(label="Valor Gasto", prefix=ft.Text("R$ "), keyboard_type=ft.KeyboardType.NUMBER)

    # --- VIEWS ---
    def show_home():
        return ft.Column([
            ft.Container(height=40),
            ft.Text("LIMITE PARA HOJE", size=12, weight="bold", color="grey"),
            display_limite,
            badge_teto,
            ft.Divider(height=40, color="transparent"),
            ft.Row([txt_saldo, txt_contas], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=20),
            input_valor,
            ft.Button(
                "CONFIRMAR GASTO", 
                on_click=btn_registrar, 
                width=400, 
                height=50, 
                style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color="white")
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # --- NAVEGAÇÃO ---
    async def on_nav_change(e):
        index = e.control.selected_index
        page.controls.clear()
        if index == 0:
            page.add(show_home())
        # Adicionar outras telas conforme necessário
        await atualizar_ui()

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.LIST_ALT, label="Contas"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Ajustes"),
        ],
        on_change=on_nav_change
    )

    page.add(show_home())
    await atualizar_ui()

ft.run(main)
