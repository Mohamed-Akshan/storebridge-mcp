from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from database.connection import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    sku = Column(String(90), unique=True, nullable=False)
    category = Column(String(70), nullable=False)
    brand = Column(String(70), nullable=False)
    model = Column(String(130), nullable=False)
    storage = Column(String(30), default="")
    color = Column(String(50), default="")
    compatible_with = Column(String(200), default="")
    warranty_months = Column(Integer, default=6)


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)
    quantity = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, default=5)
    selling_price = Column(Numeric(12, 2), nullable=False)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class PurchaseBatch(Base):
    __tablename__ = "purchase_batches"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    supplier = Column(String(100), nullable=False)
    received_at = Column(DateTime, nullable=False)
    units_received = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(12, 2), nullable=False)


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50), default="Sales Associate")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    invoice_no = Column(String(60), unique=True, nullable=False)
    sold_at = Column(DateTime, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    status = Column(String(20), nullable=False, default="completed")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    unit_cost = Column(Numeric(12, 2), nullable=False)
    discount = Column(Numeric(12, 2), nullable=False, default=0)


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    occurred_at = Column(DateTime, nullable=False)
    movement_type = Column(String(30), nullable=False)
    quantity_change = Column(Integer, nullable=False)
    reference = Column(String(100), default="")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    expense_date = Column(DateTime, nullable=False)
    category = Column(String(70), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(String(200), default="")
