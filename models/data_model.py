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
    notes: str = ""
    is_paid: bool = True  # Para transações agendadas/fixas
    is_fixed: bool = False # Para diferenciar gastos rápidos de contas fixas

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
    """Gerenciador central de dados financeiros com persistência em JSON."""

    def __init__(self):
        self.transactions: list[Transaction] = []
        self.categories: list[Category] = []
        self.settings: dict = {
            "dia_pag": 5,
            "meta": 0.0,
            "teto": 0.0,
            "is_dark": True,
            "user_name": ""
        }
        self._load()

    # ─── Persistência ──────────────────────────────────────────────────────

    def _load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.transactions = [Transaction.from_dict(t) for t in data.get("transactions", [])]
                self.categories = [Category.from_dict(c) for c in data.get("categories", [])]
                self.settings.update(data.get("settings", {}))
            except (json.JSONDecodeError, KeyError):
                self._init_defaults()
        else:
            self._init_defaults()

    def _init_defaults(self):
        self.categories = [Category.from_dict(c) for c in DEFAULT_CATEGORIES]
        self.transactions = []
        self.save()

    def save(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        data = {
            "transactions": [t.to_dict() for t in self.transactions],
            "categories": [c.to_dict() for c in self.categories],
            "settings": self.settings
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ─── CRUD de Transações ────────────────────────────────────────────────

    def add_transaction(self, txn: Transaction) -> Transaction:
        self.transactions.append(txn)
        self.save()
        return txn

    def update_transaction(self, txn_id: str, **kwargs) -> Optional[Transaction]:
        for txn in self.transactions:
            if txn.id == txn_id:
                for key, value in kwargs.items():
                    if hasattr(txn, key):
                        setattr(txn, key, value)
                self.save()
                return txn
        return None

    def delete_transaction(self, txn_id: str) -> bool:
        original_len = len(self.transactions)
        self.transactions = [t for t in self.transactions if t.id != txn_id]
        if len(self.transactions) < original_len:
            self.save()
            return True
        return False

    def get_transactions(
        self,
        type_filter: Optional[str] = None,
        category_id: Optional[str] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        only_paid: bool = True
    ) -> list[Transaction]:
        result = self.transactions
        if only_paid:
            result = [t for t in result if t.is_paid]
        if type_filter:
            result = [t for t in result if t.type == type_filter]
        if category_id:
            result = [t for t in result if t.category_id == category_id]

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

        return sorted(filtered, key=lambda t: t.date, reverse=True)

    def get_bills(self, is_paid: Optional[bool] = None) -> list[Transaction]:
        """Retorna transações marcadas como fixas (contas)."""
        result = [t for t in self.transactions if t.is_fixed]
        if is_paid is not None:
            result = [t for t in result if t.is_paid == is_paid]
        return sorted(result, key=lambda t: t.date, reverse=True)

    def get_upcoming_bills(self) -> dict:
        """Retorna info sobre contas pendentes (não pagas e fixas)."""
        pending = [t for t in self.transactions if t.is_fixed and not t.is_paid]
        total = sum(t.amount for t in pending)
        return {
            "count": len(pending),
            "total": round(total, 2),
            "bills": pending[:5]  # top 5 para exibir
        }

    # ─── Cálculos ──────────────────────────────────────────────────────────

    def get_total_balance(self) -> float:
        receitas = sum(t.amount for t in self.transactions if t.type == "receita" and t.is_paid)
        despesas = sum(t.amount for t in self.transactions if t.type == "despesa" and t.is_paid)
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
        for t in txns:
            cat = self.get_category_by_id(t.category_id)
            cat_name = cat.name if cat else "Sem Categoria"
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
        for cat in self.categories:
            if cat.id == cat_id:
                return cat
        return None

    def get_categories_by_type(self, txn_type: str) -> list[Category]:
        """Retorna categorias filtradas por tipo ('receita' ou 'despesa')."""
        return [c for c in self.categories if c.type == txn_type]

    # ─── Lógica de Burn Rate ───────────────────────────────────────────────

    def get_burn_rate_data(self):
        hoje = date.today()
        dia_pag = self.settings.get("dia_pag", 5)

        # Calcular próximo pagamento
        try:
            proximo_pag = date(hoje.year, hoje.month, dia_pag)
            if hoje.day >= dia_pag:
                if hoje.month < 12:
                    proximo_pag = date(hoje.year, hoje.month + 1, dia_pag)
                else:
                    proximo_pag = date(hoje.year + 1, 1, dia_pag)
        except ValueError:
            # Caso o dia_pag seja 31 e o mês tenha 30 dias
            proximo_pag = date(hoje.year, hoje.month + 1, 1) # Simplificação

        dias_restantes = max(1, (proximo_pag - hoje).days)

        saldo_real = self.get_total_balance()
        contas_abertas_list = self.get_bills(is_paid=False)
        contas_abertas = sum(t.amount for t in contas_abertas_list)

        disponivel_total = saldo_real - contas_abertas

        meta = self.settings.get("meta", 0.0)
        limite_com_meta = max(0.0, (disponivel_total - meta) / dias_restantes)

        # Multiplicadores
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
