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
        self._load()

    # ─── Persistência ──────────────────────────────────────────────────────

    def _load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.transactions = [Transaction.from_dict(t) for t in data.get("transactions", [])]
                self.categories = [Category.from_dict(c) for c in data.get("categories", [])]
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
    ) -> list[Transaction]:
        result = self.transactions
        if type_filter:
            result = [t for t in result if t.type == type_filter]
        if category_id:
            result = [t for t in result if t.category_id == category_id]
        if month and year:
            result = [
                t for t in result
                if datetime.fromisoformat(t.date).month == month
                and datetime.fromisoformat(t.date).year == year
            ]
        elif year:
            result = [t for t in result if datetime.fromisoformat(t.date).year == year]
        return sorted(result, key=lambda t: t.date, reverse=True)

    # ─── CRUD de Categorias ────────────────────────────────────────────────

    def add_category(self, cat: Category) -> Category:
        self.categories.append(cat)
        self.save()
        return cat

    def update_category(self, cat_id: str, **kwargs) -> Optional[Category]:
        for cat in self.categories:
            if cat.id == cat_id:
                for key, value in kwargs.items():
                    if hasattr(cat, key):
                        setattr(cat, key, value)
                self.save()
                return cat
        return None

    def delete_category(self, cat_id: str) -> bool:
        original_len = len(self.categories)
        self.categories = [c for c in self.categories if c.id != cat_id]
        if len(self.categories) < original_len:
            self.save()
            return True
        return False

    def get_category_by_id(self, cat_id: str) -> Optional[Category]:
        for cat in self.categories:
            if cat.id == cat_id:
                return cat
        return None

    def get_categories_by_type(self, type_filter: str) -> list[Category]:
        return [c for c in self.categories if c.type == type_filter]

    # ─── Cálculos ──────────────────────────────────────────────────────────

    def get_balance(self, month: Optional[int] = None, year: Optional[int] = None) -> float:
        income = self.get_total_income(month, year)
        expense = self.get_total_expense(month, year)
        return income - expense

    def get_total_income(self, month: Optional[int] = None, year: Optional[int] = None) -> float:
        txns = self.get_transactions(type_filter="receita", month=month, year=year)
        return sum(t.amount for t in txns)

    def get_total_expense(self, month: Optional[int] = None, year: Optional[int] = None) -> float:
        txns = self.get_transactions(type_filter="despesa", month=month, year=year)
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
        """Retorna resumo mensal (receitas, despesas) para cada mês do ano."""
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
