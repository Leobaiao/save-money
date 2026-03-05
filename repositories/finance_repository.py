from typing import List, Optional, Dict
from database import Database
from models.data_model import Transaction, Category
import json

class FinanceRepository:
    def __init__(self, db: Database):
        self.db = db

    # --- Transactions ---
    def add_transaction(self, txn: Transaction):
        query = """
            INSERT INTO transactions (id, description, amount, type, category_id, date, due_date, payment_date, notes, is_paid, is_fixed, is_recurring, recurrence_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            txn.id, txn.description, txn.amount, txn.type, txn.category_id, 
            txn.date, txn.due_date, txn.payment_date, txn.notes, 
            int(txn.is_paid), int(txn.is_fixed), int(txn.is_recurring),
            txn.recurrence_type
        )
        self.db.execute(query, params)

    def update_transaction(self, txn_id: str, **kwargs):
        if not kwargs:
            return
        fields = []
        params = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            if isinstance(value, bool):
                params.append(int(value))
            else:
                params.append(value)
        
        params.append(txn_id)
        query = f"UPDATE transactions SET {', '.join(fields)} WHERE id = ?"
        self.db.execute(query, tuple(params))

    def delete_transaction(self, txn_id: str):
        self.db.execute("DELETE FROM transactions WHERE id = ?", (txn_id,))

    def get_transaction_by_id(self, txn_id: str) -> Optional[Transaction]:
        row = self.db.fetch_one("SELECT * FROM transactions WHERE id = ?", (txn_id,))
        if row:
            return self._row_to_transaction(row)
        return None

    def get_transactions(self, type_filter: Optional[str] = None, category_id: Optional[str] = None) -> List[Transaction]:
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        if type_filter:
            query += " AND type = ?"
            params.append(type_filter)
        if category_id:
            query += " AND category_id = ?"
            params.append(category_id)
        
        query += " ORDER BY date DESC"
        rows = self.db.fetch_all(query, tuple(params))
        return [self._row_to_transaction(row) for row in rows]

    def _row_to_transaction(self, row) -> Transaction:
        return Transaction(
            id=row["id"],
            description=row["description"],
            amount=row["amount"],
            type=row["type"],
            category_id=row["category_id"],
            date=row["date"],
            due_date=row["due_date"],
            payment_date=row["payment_date"],
            notes=row["notes"],
            is_paid=bool(row["is_paid"]),
            is_fixed=bool(row["is_fixed"]),
            is_recurring=bool(row["is_recurring"]),
            recurrence_type=row["recurrence_type"] if "recurrence_type" in row.keys() else "none"
        )

    # --- Categories ---
    def add_category(self, cat: Category):
        query = "INSERT INTO categories (id, name, icon, color, type) VALUES (?, ?, ?, ?, ?)"
        params = (cat.id, cat.name, cat.icon, cat.color, cat.type)
        self.db.execute(query, params)

    def get_categories(self, type_filter: Optional[str] = None) -> List[Category]:
        query = "SELECT * FROM categories"
        params = []
        if type_filter:
            query += " WHERE type = ?"
            params.append(type_filter)
        
        rows = self.db.fetch_all(query, tuple(params))
        return [self._row_to_category(row) for row in rows]

    def _row_to_category(self, row) -> Category:
        return Category(
            id=row["id"],
            name=row["name"],
            icon=row["icon"],
            color=row["color"],
            type=row["type"]
        )

    # --- Settings ---
    def get_setting(self, key: str, default: any = None) -> any:
        row = self.db.fetch_one("SELECT value FROM settings WHERE key = ?", (key,))
        if row:
            try:
                return json.loads(row["value"])
            except:
                return row["value"]
        return default

    def set_setting(self, key: str, value: any):
        val_str = json.dumps(value)
        self.db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, val_str))

    def get_all_settings(self) -> Dict:
        rows = self.db.fetch_all("SELECT * FROM settings")
        settings = {}
        for row in rows:
            try:
                settings[row["key"]] = json.loads(row["value"])
            except:
                settings[row["key"]] = row["value"]
        return settings
