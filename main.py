import flet as ft
from datetime import datetime, date

async def main(page: ft.Page):
    page.title = "Daily Burn Rate"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 400
    page.window.height = 700
    page.padding = 20

    # --- PERSISTÊNCIA (Native SharedPreferences) ---
    async def get_state():
        try:
            state = await page.shared_preferences.get("user_data")
            if state:
                import json 
                return json.loads(state)
        except Exception:
            pass
        return {
            "dia_pag": 5, "saldo": 0.0, "meta": 0.0, "teto": 0.0, "contas": []
        }

    async def save_state(data):
        import json
        await page.shared_preferences.set("user_data", json.dumps(data))

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
        page.update()

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
        page.update()

    input_valor = ft.TextField(label="Valor Gasto", prefix=ft.Text("R$ "), keyboard_type=ft.KeyboardType.NUMBER)

    # --- VIEWS ---
    def show_home():
        input_valor.value = ""
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

    async def show_contas():
        data = await get_state()
        contas_list = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)

        async def toggle_pago(e, index):
            data["contas"][index]["pago"] = e.control.value
            await save_state(data)
            await atualizar_ui()

        async def remover_conta(index):
            data["contas"].pop(index)
            await save_state(data)
            await render_view(1)
            await atualizar_ui()

        for i, conta in enumerate(data["contas"]):
            contas_list.controls.append(
                ft.ListTile(
                    title=ft.Text(conta["nome"]),
                    subtitle=ft.Text(f"R$ {float(conta['valor']):,.2f}"),
                    leading=ft.Checkbox(value=conta["pago"], on_change=lambda e, idx=i: toggle_pago(e, idx)),
                    trailing=ft.IconButton(ft.Icons.DELETE_OUTLINE, on_click=lambda e, idx=i: remover_conta(idx), icon_color=ft.Colors.RED_400)
                )
            )

        nome_input = ft.TextField(label="Nome da Conta", expand=True)
        valor_input = ft.TextField(label="Valor", prefix=ft.Text("R$ "), expand=True, keyboard_type=ft.KeyboardType.NUMBER)

        async def add_conta(e):
            if not nome_input.value or not valor_input.value: return
            data["contas"].append({
                "nome": nome_input.value,
                "valor": float(valor_input.value.replace(",", ".")),
                "pago": False
            })
            await save_state(data)
            await render_view(1)
            await atualizar_ui()

        return ft.Column([
            ft.Text("MINHAS CONTAS", size=20, weight="bold"),
            ft.Row([nome_input, valor_input]),
            ft.Button("Adicionar Conta", icon=ft.Icons.ADD, on_click=add_conta),
            ft.Divider(),
            contas_list
        ], expand=True)

    async def show_settings():
        data = await get_state()
        
        salario_input = ft.TextField(label="Saldo Atual no Banco", placeholder="00,00", value=str(data["saldo"]), prefix=ft.Text("R$ "), keyboard_type=ft.KeyboardType.NUMBER)
        dia_pag_input = ft.TextField(label="Dia do Pagamento", value=str(data["dia_pag"]), keyboard_type=ft.KeyboardType.NUMBER)
        meta_input = ft.TextField(label="Meta de Sobra (Fim do Mês)", value=str(data["meta"]), prefix=ft.Text("R$ "), keyboard_type=ft.KeyboardType.NUMBER)
        teto_input = ft.TextField(label="Teto de Gasto Diário (Opcional)", value=str(data["teto"]), prefix=ft.Text("R$ "), keyboard_type=ft.KeyboardType.NUMBER)

        async def save_settings(e):
            data["saldo"] = float(salario_input.value.replace(",", "."))
            data["dia_pag"] = int(dia_pag_input.value)
            data["meta"] = float(meta_input.value.replace(",", "."))
            data["teto"] = float(teto_input.value.replace(",", "."))
            await save_state(data)
            await atualizar_ui()
            snackbar = ft.SnackBar(ft.Text("Configurações salvas!"))
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()

        return ft.Column([
            ft.Text("CONFIGURAÇÕES", size=20, weight="bold"),
            salario_input,
            dia_pag_input,
            meta_input,
            teto_input,
            ft.Container(height=20),
            ft.Button("Salvar Ajustes", icon=ft.Icons.SAVE, on_click=save_settings, width=400, height=50)
        ], scroll=ft.ScrollMode.ADAPTIVE)

    # --- NAVEGAÇÃO ---
    async def render_view(index):
        page.controls.clear()
        if index == 0:
            page.add(show_home())
        elif index == 1:
            page.add(await show_contas())
        elif index == 2:
            page.add(await show_settings())
        page.update()

    async def on_nav_change(e):
        await render_view(e.control.selected_index)

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.LIST_ALT, label="Contas"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Ajustes"),
        ],
        on_change=on_nav_change
    )

    await render_view(0)
    await atualizar_ui()

ft.run(main)

