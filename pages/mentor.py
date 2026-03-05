import flet as ft
from models.data_model import FinanceData
from theme.app_theme import AppColors, AppStyle
from services.ai_service import AIService
import asyncio

class ChatMessage(ft.Row):
    def __init__(self, text: str, is_user: bool, is_dark: bool):
        super().__init__()
        self.text = text
        self.is_user = is_user
        self.is_dark = is_dark
        
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.alignment = ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
        
        # Cores das bolhas
        user_bg = AppColors.PRIMARY
        ai_bg = AppColors.DARK_SURFACE if is_dark else "#F0F2F5"
        text_color = "#FFFFFF" if is_user else (AppColors.DARK_TEXT if is_dark else AppColors.LIGHT_TEXT)
        
        avatar = ft.CircleAvatar(
            content=ft.Icon(ft.Icons.PERSON_ROUNDED if is_user else ft.Icons.AUTO_AWESOME_ROUNDED),
            bgcolor=AppColors.PRIMARY if is_user else AppColors.PRIMARY_LIGHT,
            color="#FFFFFF",
            radius=16
        )
        
        bubble = ft.Container(
            content=ft.Text(text, color=text_color, size=15),
            bgcolor=user_bg if is_user else ai_bg,
            padding=ft.padding.all(12),
            border_radius=ft.border_radius.only(
                top_left=15, 
                top_right=15, 
                bottom_left=15 if is_user else 5, 
                bottom_right=5 if is_user else 15
            ),
            width=280,
        )
        
        if is_user:
            self.controls = [bubble, avatar]
        else:
            self.controls = [avatar, bubble]

def build_mentor_page(
    finance_data: FinanceData,
    is_dark: bool,
    page: ft.Page
) -> ft.Container:
    
    ai_service = AIService()
    chat_history = ft.Column(spacing=15, scroll=ft.ScrollMode.ALWAYS, expand=True)

    # Definir send_message ANTES de usá-lo nos controles
    async def send_message(e):
        user_text = text_input.value.strip()
        if not user_text:
            return
        
        # Limpar input e adicionar mensagem do usuário
        text_input.value = ""
        chat_history.controls.append(ChatMessage(user_text, True, is_dark))
        
        # Indicador de "digitando"
        typing_indicator = ft.Row([
            ft.Text("Conway está pensando...", size=12, italic=True, color=AppColors.PRIMARY)
        ], alignment=ft.MainAxisAlignment.START)
        chat_history.controls.append(typing_indicator)
        page.update()
        
        # Obter contexto real
        context = ai_service.build_context_string(finance_data)
        
        # Chamar IA
        response = await ai_service.get_response(user_text, context)
        
        # Remover indicador e adicionar resposta
        chat_history.controls.remove(typing_indicator)
        chat_history.controls.append(ChatMessage(response, False, is_dark))
        page.update()

    # Mensagem de boas vindas do Conway
    chat_history.controls.append(
        ChatMessage("Olá! Eu sou o Conway, seu mentor financeiro. Como posso te ajudar a organizar seu dinheiro hoje?", False, is_dark)
    )

    text_input = ft.TextField(
        hint_text="Pergunte algo ao Conway...",
        border_radius=25,
        expand=True,
        bgcolor=AppColors.DARK_SURFACE if is_dark else "#F0F2F5",
        border_color=ft.Colors.TRANSPARENT,
        content_padding=ft.padding.symmetric(horizontal=20),
        on_submit=lambda e: page.run_task(send_message, e)
    )

    input_row = ft.Row([
        text_input,
        ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED,
            icon_color=AppColors.PRIMARY,
            on_click=lambda e: page.run_task(send_message, e)
        )
    ], spacing=10)

    return ft.Container(
        content=ft.Column([
            # Header estilizado
            ft.Row([
                ft.Image(src="icon.png", width=40, height=40),
                ft.Column([
                    ft.Text("Conway AI", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Seu Mentor Financeiro", size=12, color=AppColors.PRIMARY),
                ], spacing=0)
            ], alignment=ft.MainAxisAlignment.START),
            
            ft.Divider(height=1, color=AppColors.DARK_BORDER if is_dark else AppColors.LIGHT_BORDER),
            
            # Área de Chat
            ft.Container(
                content=chat_history,
                expand=True,
                padding=ft.padding.symmetric(vertical=10)
            ),
            
            # Input Area
            ft.Container(
                content=input_row,
                padding=ft.padding.all(10),
                border_radius=30,
            )
        ], spacing=10, expand=True),
        padding=AppStyle.PAGE_PADDING,
        expand=True,
        bgcolor=AppColors.DARK_BG if is_dark else AppColors.LIGHT_BG
    )
