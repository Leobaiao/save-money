import json
import os
import uuid
from datetime import datetime, date
from dataclasses import dataclass, field, asdict
from typing import Optional


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DATA_FILE = os.path.join(DATA_DIR, "financas.json")


# ─── Categorias Padrão ─────────────────────────────────────────────────────────
DEFAULT_CATEGORIES = [
    {"id": "cat_salary", "name": "Salário", "icon": "work", "color": "#4CAF50", "type": "receita"},
    {"id": "cat_freelance", "name": "Freelance", "icon": "computer", "color": "#2196F3", "type": "receita"},
    {"id": "cat_investments", "name": "Investimentos", "icon": "trending_up", "color": "#9C27B0", "type": "receita"},
    {"id": "cat_gifts_in", "name": "Presentes", "icon": "card_giftcard", "color": "#E91E63", "type": "receita"},
    {"id": "cat_other_in", "name": "Outros (Receita)", "icon": "attach_money", "color": "#00BCD4", "type": "receita"},
    {"id": "cat_food", "name": "Alimentação", "icon": "restaurant", "color": "#FF9800", "type": "despesa"},
    {"id": "cat_transport", "name": "Transporte", "icon": "directions_car", "color": "#607D8B", "type": "despesa"},
    {"id": "cat_housing", "name": "Moradia", "icon": "home", "color": "#795548", "type": "despesa"},
    {"id": "cat_health", "name": "Saúde", "icon": "local_hospital", "color": "#F44336", "type": "despesa"},
    {"id": "cat_education", "name": "Educação", "icon": "school", "color": "#3F51B5", "type": "despesa"},
    {"id": "cat_leisure", "name": "Lazer", "icon": "sports_esports", "color": "#FF5722", "type": "despesa"},
    {"id": "cat_shopping", "name": "Compras", "icon": "shopping_cart", "color": "#E91E63", "type": "despesa"},
    {"id": "cat_bills", "name": "Contas", "icon": "receipt_long", "color": "#FFC107", "type": "despesa"},
    {"id": "cat_other_out", "name": "Outros (Despesa)", "icon": "money_off", "color": "#9E9E9E", "type": "despesa"},
]


@dataclass
class Transaction:
    id: str = ""
    description: str = ""
    amount: float = 0.0
    type: str = "despesa"  # "receita" ou "despesa"
    category_id: str = ""
    date: str = ""  # ISO format YYYY-MM-DD
    due_date: str = "" # Data de vencimento
    payment_date: str = "" # Data de pagamento
    notes: str = ""
    is_paid: bool = True  # Para transações agendadas/fixas
    is_fixed: bool = False # Para diferenciar gastos rápidos de contas fixas
    is_recurring: bool = False # Para contas mensais
    recurrence_type: str = "none" # "none", "monthly", "yearly"

    def __post_init__(self):
        if not self.id:
            self.id = f"txn_{uuid.uuid4().hex[:12]}"
        if not self.date:
            self.date = date.today().isoformat()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Category:
    id: str = ""
    name: str = ""
    icon: str = "category"
    color: str = "#6C63FF"
    type: str = "despesa"  # "receita" ou "despesa"

    def __post_init__(self):
        if not self.id:
            self.id = f"cat_{uuid.uuid4().hex[:8]}"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Category":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class FinanceData:
    """Gerenciador central de dados financeiros agora utilizando SQLite via FinanceRepository."""

    def __init__(self):
        from database import Database
        from repositories.finance_repository import FinanceRepository
        
        self.db = Database()
        self.repo = FinanceRepository(self.db)
        
        self.filter_type: str | None = None  # Para persistir filtro na UI
        
        # Carregar ou inicializar configurações padrão
        self.settings = {
            "dia_pag": 5,
            "meta": 0.0,
            "teto": 0.0,
            "is_dark": True,
            "user_name": "Usuário",
            "user_photo": ""
        }
        
        # Tentar carregar do banco
        db_settings = self.repo.get_all_settings()
        if db_settings:
            self.settings.update(db_settings)
        else:
            # Se não houver settings no banco, talvez seja a primeira vez ou migração
            self._handle_migration_or_init()

    def _handle_migration_or_init(self):
        """Verifica se há dados no JSON legado e migra para o SQLite."""
        if os.path.exists(DATA_FILE):
            print("Migrando dados do JSON para SQLite...")
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Migrar Categorias
                legacy_cats = data.get("categories", [])
                if legacy_cats:
                    for cat_dict in legacy_cats:
                        self.repo.add_category(Category.from_dict(cat_dict))
                else:
                    self._init_default_categories()
                
                # Migrar Transações
                legacy_txns = data.get("transactions", [])
                for txn_dict in legacy_txns:
                    self.repo.add_transaction(Transaction.from_dict(txn_dict))
                
                # Migrar Configurações
                legacy_settings = data.get("settings", {})
                if legacy_settings:
                    self.settings.update(legacy_settings)
                    for k, v in legacy_settings.items():
                        self.repo.set_setting(k, v)
                
                # Renomear arquivo para evitar nova migração
                os.rename(DATA_FILE, DATA_FILE + ".bak")
                print("Migração concluída com sucesso.")
            except Exception as e:
                print(f"Erro na migração: {e}")
                self._init_default_categories()
        else:
            self._init_default_categories()
            # Salvar settings padrão no banco
            for k, v in self.settings.items():
                self.repo.set_setting(k, v)

    def _init_default_categories(self):
        existing = self.repo.get_categories()
        if not existing:
            for cat_dict in DEFAULT_CATEGORIES:
                self.repo.add_category(Category.from_dict(cat_dict))

    def save(self):
        """Salva as configurações atuais no banco (Transações e categorias são salvas via repo)."""
        for k, v in self.settings.items():
            self.repo.set_setting(k, v)

    # ─── CRUD de Transações (Delegado ao Repo) ───────────────────────────

    def add_transaction(self, txn: Transaction) -> Transaction:
        self.repo.add_transaction(txn)
        return txn

    def update_transaction(self, txn_id: str, **kwargs) -> Optional[Transaction]:
        # Buscar transação original para checar recorrência
        original = self.repo.get_transaction_by_id(txn_id)
        
        self.repo.update_transaction(txn_id, **kwargs)
        
        # Lógica de Recorrência
        if original and kwargs.get("is_paid") is True and original.is_fixed and original.recurrence_type in ["monthly", "yearly"]:
            # Se era uma conta pendente que foi paga, e é recorrente
            if not original.is_paid:
                self._create_next_recurring_instance(original)
        
        # Buscar a transação atualizada
        return self.repo.get_transaction_by_id(txn_id)

    def _create_next_recurring_instance(self, original_txn: Transaction):
        """Cria a próxima instância de uma conta recorrente."""
        try:
            curr_date = datetime.fromisoformat(original_txn.date)
            # due_date também pode ser ISO
            due_date_obj = None
            if original_txn.due_date:
                due_date_obj = datetime.fromisoformat(original_txn.due_date)
            
            if original_txn.recurrence_type == "monthly":
                import calendar
                # Avançar um mês
                month = curr_date.month + 1
                year = curr_date.year
                if month > 12:
                    month = 1
                    year += 1
                
                # Garantir que o dia existe no próximo mês (ex: 31 de Jan -> 28 de Fev)
                last_day = calendar.monthrange(year, month)[1]
                new_day = min(curr_date.day, last_day)
                new_date = datetime(year, month, new_day)
                
                if due_date_obj:
                    # Mesma lógica para due_date
                    d_month = due_date_obj.month + 1
                    d_year = due_date_obj.year
                    if d_month > 12:
                        d_month = 1
                        d_year += 1
                    d_last_day = calendar.monthrange(d_year, d_month)[1]
                    d_new_day = min(due_date_obj.day, d_last_day)
                    new_due_date = datetime(d_year, d_month, d_new_day)
                else:
                    new_due_date = None
            
            elif original_txn.recurrence_type == "yearly":
                new_date = datetime(curr_date.year + 1, curr_date.month, curr_date.day)
                if due_date_obj:
                    new_due_date = datetime(due_date_obj.year + 1, due_date_obj.month, due_date_obj.day)
                else:
                    new_due_date = None
            else:
                return

            new_txn = Transaction(
                description=original_txn.description,
                amount=original_txn.amount,
                type=original_txn.type,
                category_id=original_txn.category_id,
                date=new_date.date().isoformat(),
                due_date=new_due_date.date().isoformat() if new_due_date else "",
                notes=original_txn.notes,
                is_paid=False, # A nova sempre começa pendente
                is_fixed=True,
                is_recurring=True,
                recurrence_type=original_txn.recurrence_type
            )
            self.add_transaction(new_txn)
        except Exception as e:
            print(f"Erro ao criar próxima instância recorrente: {e}")

    def delete_transaction(self, txn_id: str) -> bool:
        self.repo.delete_transaction(txn_id)
        return True

    def clear_all_data(self):
        """Apaga todas as transações."""
        self.db.execute("DELETE FROM transactions")

    def reset_all_data(self):
        """Apaga o banco de dados e reinicia do zero (Limpeza total)."""
        self.db.reset_database()
        self._init_default_categories()
        # Recarregar settings padrão
        self.settings = {
            "dia_pag": 5,
            "meta": 0.0,
            "teto": 0.0,
            "is_dark": True,
            "user_name": "Usuário",
            "user_photo": ""
        }
        for k, v in self.settings.items():
            self.repo.set_setting(k, v)

    def export_data(self) -> Optional[str]:
        """Exporta o banco de dados para a pasta Downloads."""
        return self.db.export_database()

    def get_transactions(
        self,
        type_filter: Optional[str] = None,
        category_id: Optional[str] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        only_paid: bool = True
    ) -> list[Transaction]:
        # O repo já faz o filtro básico e o sort
        result = self.repo.get_transactions(type_filter=type_filter, category_id=category_id)
        
        if only_paid:
            result = [t for t in result if t.is_paid]

        filtered = []
        for t in result:
            t_date = datetime.fromisoformat(t.date)
            if month and year:
                if t_date.month == month and t_date.year == year:
                    filtered.append(t)
            elif year:
                if t_date.year == year:
                    filtered.append(t)
            else:
                filtered.append(t)

        return filtered # Já vêm ordenados pelo repo

    def get_bills(self, is_paid: Optional[bool] = None) -> list[Transaction]:
        """Retorna transações marcadas como fixas (contas)."""
        query = "SELECT * FROM transactions WHERE is_fixed = 1"
        params = []
        if is_paid is not None:
            query += " AND is_paid = ?"
            params.append(int(is_paid))
        
        query += " ORDER BY date DESC"
        rows = self.db.fetch_all(query, tuple(params))
        result = [self.repo._row_to_transaction(row) for row in rows]
        return result

    def get_upcoming_bills(self) -> dict:
        """Retorna info sobre contas pendentes (não pagas e fixas)."""
        pending = self.get_bills(is_paid=False)
        total = sum(t.amount for t in pending)
        return {
            "count": len(pending),
            "total": round(total, 2),
            "bills": pending[:5]
        }

    # ─── Cálculos ──────────────────────────────────────────────────────────

    def get_total_balance(self) -> float:
        receitas = sum(t.amount for t in self.repo.get_transactions(type_filter="receita") if t.is_paid)
        despesas = sum(t.amount for t in self.repo.get_transactions(type_filter="despesa") if t.is_paid)
        return receitas - despesas

    def get_balance(self, month: Optional[int] = None, year: Optional[int] = None) -> float:
        income = self.get_total_income(month, year)
        expense = self.get_total_expense(month, year)
        return income - expense

    def get_total_income(self, month: Optional[int] = None, year: Optional[int] = None) -> float:
        txns = self.get_transactions(type_filter="receita", month=month, year=year, only_paid=True)
        return sum(t.amount for t in txns)

    def get_total_expense(self, month: Optional[int] = None, year: Optional[int] = None) -> float:
        txns = self.get_transactions(type_filter="despesa", month=month, year=year, only_paid=True)
        return sum(t.amount for t in txns)

    def get_expenses_by_category(
        self, month: Optional[int] = None, year: Optional[int] = None
    ) -> dict[str, float]:
        txns = self.get_transactions(type_filter="despesa", month=month, year=year)
        result: dict[str, float] = {}
        # Cache de categorias para evitar múltiplas queries
        cats = {c.id: c.name for c in self.repo.get_categories()}
        for t in txns:
            cat_name = cats.get(t.category_id, "Sem Categoria")
            result[cat_name] = result.get(cat_name, 0) + t.amount
        return result

    def get_monthly_summary(self, year: int) -> list[dict]:
        summary = []
        for month in range(1, 13):
            income = self.get_total_income(month=month, year=year)
            expense = self.get_total_expense(month=month, year=year)
            summary.append({
                "month": month,
                "income": income,
                "expense": expense,
                "balance": income - expense,
            })
        return summary

    def get_category_by_id(self, cat_id: str) -> Optional[Category]:
        row = self.db.fetch_one("SELECT * FROM categories WHERE id = ?", (cat_id,))
        if row:
            return self.repo._row_to_category(row)
        return None

    def get_categories_by_type(self, txn_type: str) -> list[Category]:
        return self.repo.get_categories(type_filter=txn_type)

    # ─── Lógica de Burn Rate (Idêntica, apenas usa métodos delegados) ──────

    def get_burn_rate_data(self):
        hoje = date.today()
        dia_pag = self.settings.get("dia_pag", 5)

        try:
            proximo_pag = date(hoje.year, hoje.month, dia_pag)
            if hoje.day >= dia_pag:
                if hoje.month < 12:
                    proximo_pag = date(hoje.year, hoje.month + 1, dia_pag)
                else:
                    proximo_pag = date(hoje.year + 1, 1, dia_pag)
        except ValueError:
            proximo_pag = date(hoje.year, hoje.month + 1, 1)

        dias_restantes = max(1, (proximo_pag - hoje).days)

        saldo_real = self.get_total_balance()
        contas_abertas_list = self.get_bills(is_paid=False)
        contas_abertas = sum(t.amount for t in contas_abertas_list)

        disponivel_total = saldo_real - contas_abertas

        meta = self.settings.get("meta", 0.0)
        limite_com_meta = max(0.0, (disponivel_total - meta) / dias_restantes)

        multiplicadores = {0: 0.8, 4: 1.2, 5: 1.1}
        multiplicador = multiplicadores.get(hoje.weekday(), 1.0)

        teto = self.settings.get("teto", 0.0)
        base_limite = min(limite_com_meta, teto) if teto > 0 else limite_com_meta
        exibido = base_limite * multiplicador
        is_teto = teto > 0 and limite_com_meta > teto

        sobra_prevista = disponivel_total - (exibido * dias_restantes)

        if meta > 0:
            saude = min(1.0, max(0.0, sobra_prevista / meta))
        else:
            saude = 1.0 if sobra_prevista >= 0 else 0.0

        return {
            "limite_diario": round(exibido, 2),
            "is_teto": is_teto,
            "contas_abertas": round(contas_abertas, 2),
            "sobra_prevista": round(sobra_prevista, 2),
            "saude_meta": saude,
            "dias_restantes": dias_restantes
        }
