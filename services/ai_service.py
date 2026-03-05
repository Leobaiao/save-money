import os
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import date

load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        self.chat_session = None
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self._setup_model()

    def _setup_model(self):
        system_instruction = """
        Você é o "Conway", um conselheiro financeiro pessoal representado por uma coruja sábia.
        Sua personalidade é encorajadora, inteligente e prática. 
        Você nunca é julgador, mas é realista sobre metas financeiras.

        CONTEXTO DO APP (SaveMoney):
        O usuário utiliza o app "SaveMoney" para gerenciar finanças.
        Você receberá dados reais do usuário (saldo, contas, transações) para dar conselhos precisos.

        REGRAS DE RESPOSTA:
        1. Seja conciso e direto.
        2. Use analogias simples.
        3. Se os gastos estiverem altos, sugira cortes práticos.
        4. Encoraje a reserva de emergência.
        5. Responda sempre em Português do Brasil.
        """
        
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }

        # Usando o modelo estável que funcionou nos testes
        self.model = genai.GenerativeModel(
            model_name="models/gemini-flash-latest",
            generation_config=generation_config,
            system_instruction=system_instruction,
        )
        self.chat_session = self.model.start_chat(history=[])

    async def get_response(self, user_message: str, context_data: str = "") -> str:
        if not self.model:
            return "Erro: API Key não configurada. Verifique as configurações."
        
        try:
            full_prompt = f"{user_message}\n\n[DADOS ATUAIS DO USUÁRIO]:\n{context_data}"
            response = self.chat_session.send_message(full_prompt)
            return response.text
        except Exception as e:
            if "429" in str(e):
                return "Estou um pouco sobrecarregado agora. Por favor, aguarde um minuto antes de perguntar novamente."
            return f"Erro ao processar sua pergunta: {str(e)}"

    def build_context_string(self, finance_data):
        """Transforma os dados reais do app em uma string para a IA entender o todo."""
        balance = finance_data.get_total_balance()
        bills_data = finance_data.get_upcoming_bills()
        bills = bills_data.get("bills", [])
        
        # 1. Resumo por Categoria (Visão estratégica de todos os gastos)
        cat_expenses = finance_data.get_expenses_by_category()
        
        # 2. Resumo Mensal do Ano (Tendência)
        hoje = date.today()
        monthly_data = finance_data.get_monthly_summary(hoje.year)
        
        context = f"--- VISÃO GERAL DO PERFIL ---\n"
        context += f"Saldo Atual: R$ {balance:.2f}\n"
        context += f"Contas Pendentes: {len(bills)}\n"
        
        if bills:
            context += "\nPróximas Contas Críticas:\n"
            for b in bills[:3]:
                context += f"- {b.description}: R$ {b.amount}\n"
        
        if cat_expenses:
            context += "\nDistribuição Histórica de Gastos por Categoria:\n"
            # Ordenar por valor para o Conway focar no que importa
            sorted_cats = sorted(cat_expenses.items(), key=lambda x: x[1], reverse=True)
            for cat, total in sorted_cats[:5]:
                context += f"- {cat}: R$ {total:.2f}\n"
        
        if monthly_data:
            # Pegar apenas os últimos 3 meses para ver a tendência
            current_month = hoje.month
            recent_months = [m for m in monthly_data if m['month'] <= current_month][-3:]
            context += "\nTendência dos Últimos Meses (Receita vs Despesa):\n"
            for m in recent_months:
                context += f"Mês {m['month']}: Ganhou R$ {m['income']:.2f} | Gastou R$ {m['expense']:.2f}\n"
        
        return context
