from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from decimal import Decimal

from sqlalchemy import func, select

from database.connection import (
    BRANCH_NAMES,
    session_for,
)
from database.models import (
    Employee,
    Expense,
    Inventory,
    Product,
    PurchaseBatch,
    Sale,
    SaleItem,
    StockMovement,
)


BRANCH_ALIASES = {
    "liberty": "liberty",
    "liberty plaza": "liberty",
    "kollupitiya": "liberty",
    "colpetty": "liberty",
    "galle face": "galle_face",
    "one galle face": "galle_face",
    "ogf": "galle_face",
    "pettah": "pettah",
    "petta": "pettah",
    "main street": "pettah",
}


def branches_for(branch="all"):
    value = (branch or "all").strip().lower().replace("_", " ")

    if value in ("all", "all branches", "every", "every branch"):
        return list(BRANCH_NAMES)

    key = BRANCH_ALIASES.get(value)

    if key is None:
        raise ValueError(
            "Unknown branch. Choose Liberty Plaza, One Galle Face, Pettah or all."
        )

    return [key]


def period(start_date=None, end_date=None):
    today = datetime.now(ZoneInfo("Asia/Colombo")).date()

    if not start_date:
        start = today.replace(day=1)
    else:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()

    if not end_date:
        end = today
    else:
        end = datetime.strptime(end_date, "%Y-%m-%d").date()

    if start > end:
        raise ValueError("Start date must be on or before end date")

    if (end - start).days > 731:
        raise ValueError("Maximum reporting range is two years")

    return (
        datetime.combine(start, datetime.min.time()),
        datetime.combine(end + timedelta(days=1), datetime.min.time()),
    )


def money(value):
    return round(float(value or 0), 2)


def product_label(product):
    parts = [product.brand, product.model, product.storage, product.color]
    return " ".join(str(part) for part in parts if part).strip()


def inventory_search(query, branch="all", category="", limit=25):
    rows = []
    phrase = query.strip()

    if not phrase:
        raise ValueError("Please provide a product name or category")

    words = phrase.lower().split()

    for key in branches_for(branch):
        with session_for(key) as db:
            statement = (
                select(Product, Inventory)
                .join(Inventory, Product.id == Inventory.product_id)
            )

            for word in words:
                statement = statement.where(
                    func.lower(
                        Product.brand + " " + Product.model + " "
                        + Product.storage + " " + Product.color + " "
                        + Product.compatible_with + " " + Product.category
                    ).contains(word)
                )

            if category:
                statement = statement.where(
                    Product.category.ilike(f"%{category}%")
                )

            for product, stock in db.execute(statement.limit(limit)).all():
                rows.append({
                    "branch": BRANCH_NAMES[key],
                    "sku": product.sku,
                    "product": product_label(product),
                    "category": product.category,
                    "compatible_with": product.compatible_with,
                    "quantity": stock.quantity,
                    "selling_price_lkr": money(stock.selling_price),
                    "last_updated": stock.updated_at.isoformat(),
                })

    return rows[:75]


def price_comparison(query, branch="all"):
    rows = inventory_search(query, branch)

    for row in rows:
        key = next(
            key for key, title in BRANCH_NAMES.items()
            if title == row["branch"]
        )

        with session_for(key) as db:
            latest = db.execute(
                select(PurchaseBatch.unit_cost, PurchaseBatch.received_at)
                .join(Product, Product.id == PurchaseBatch.product_id)
                .where(Product.sku == row["sku"])
                .order_by(PurchaseBatch.received_at.desc())
                .limit(1)
            ).first()

            if latest:
                row["latest_batch_unit_cost_lkr"] = money(latest[0])
                row["latest_batch_received"] = latest[1].date().isoformat()
                row["indicative_spread_lkr"] = round(
                    row["selling_price_lkr"] - money(latest[0]), 2
                )
            else:
                row["latest_batch_unit_cost_lkr"] = None
                row["indicative_spread_lkr"] = None

    return rows


def stock_movements(query, branch="all", start_date=None, end_date=None):
    start, end = period(start_date, end_date)
    rows = []

    for key in branches_for(branch):
        with session_for(key) as db:
            statement = (
                select(StockMovement, Product)
                .join(Product, Product.id == StockMovement.product_id)
                .where(StockMovement.occurred_at >= start)
                .where(StockMovement.occurred_at < end)
            )

            if query:
                statement = statement.where(
                    (Product.brand + " " + Product.model).ilike(f"%{query}%")
                )

            for move, product in db.execute(
                statement.order_by(StockMovement.occurred_at.desc()).limit(60)
            ):
                rows.append({
                    "branch": BRANCH_NAMES[key],
                    "product": product_label(product),
                    "type": move.movement_type,
                    "change": move.quantity_change,
                    "date": move.occurred_at.isoformat(),
                })

    return sorted(rows, key=lambda r: r["date"], reverse=True)[:80]


def sales_summary(branch="all", start_date=None, end_date=None):
    start, end = period(start_date, end_date)
    rows = []

    for key in branches_for(branch):
        with session_for(key) as db:
            revenue = func.sum(
                SaleItem.quantity * SaleItem.unit_price - SaleItem.discount
            )
            cost = func.sum(SaleItem.quantity * SaleItem.unit_cost)

            result = db.execute(
                select(
                    revenue,
                    cost,
                    func.count(func.distinct(Sale.id)),
                    func.sum(SaleItem.quantity),
                )
                .join(SaleItem, Sale.id == SaleItem.sale_id)
                .where(Sale.sold_at >= start)
                .where(Sale.sold_at < end)
                .where(Sale.status == "completed")
            ).one()

            sales = money(result[0])
            cogs = money(result[1])

            expense = db.scalar(
                select(func.sum(Expense.amount))
                .where(Expense.expense_date >= start)
                .where(Expense.expense_date < end)
            )

            expenses = money(expense)
            gross = round(sales - cogs, 2)

            rows.append({
                "branch": BRANCH_NAMES[key],
                "revenue_lkr": sales,
                "cost_of_goods_sold_lkr": cogs,
                "gross_profit_lkr": gross,
                "gross_margin_pct": round(gross / sales * 100, 2) if sales else 0,
                "recorded_expenses_lkr": expenses,
                "estimated_operating_result_lkr": round(gross - expenses, 2),
                "invoices": result[2] or 0,
                "units_sold": result[3] or 0,
            })

    return {
        "period_start": start.date().isoformat(),
        "period_end": (end - timedelta(days=1)).date().isoformat(),
        "branches": rows,
        "totals": {
            "revenue_lkr": round(sum(r["revenue_lkr"] for r in rows), 2),
            "gross_profit_lkr": round(sum(r["gross_profit_lkr"] for r in rows), 2),
            "estimated_operating_result_lkr": round(
                sum(r["estimated_operating_result_lkr"] for r in rows), 2
            ),
            "invoices": sum(r["invoices"] for r in rows),
            "units_sold": sum(r["units_sold"] for r in rows),
        },
        "chart": {
            "title": "Revenue by branch (LKR)",
            "labels": [r["branch"] for r in rows],
            "values": [r["revenue_lkr"] for r in rows],
        },
        "note": (
            "Estimated operating result deducts recorded branch expenses only; "
            "it is not audited net profit."
        ),
    }


def employee_performance(branch="all", start_date=None, end_date=None):
    start, end = period(start_date, end_date)
    rows = []

    for key in branches_for(branch):
        with session_for(key) as db:
            result = db.execute(
                select(
                    Employee.name,
                    func.sum(
                        SaleItem.quantity * SaleItem.unit_price - SaleItem.discount
                    ),
                    func.sum(
                        SaleItem.quantity
                        * (SaleItem.unit_price - SaleItem.unit_cost)
                        - SaleItem.discount
                    ),
                    func.count(func.distinct(Sale.id)),
                    func.sum(SaleItem.quantity),
                )
                .join(Sale, Sale.employee_id == Employee.id)
                .join(SaleItem, SaleItem.sale_id == Sale.id)
                .where(Sale.sold_at >= start)
                .where(Sale.sold_at < end)
                .where(Sale.status == "completed")
                .group_by(Employee.id, Employee.name)
            ).all()

            for name, revenue, profit, invoices, units in result:
                rows.append({
                    "employee": name,
                    "branch": BRANCH_NAMES[key],
                    "revenue_lkr": money(revenue),
                    "gross_profit_lkr": money(profit),
                    "invoices": invoices,
                    "units_sold": units,
                })

    rows.sort(key=lambda r: r["revenue_lkr"], reverse=True)

    return {
        "start": start.date().isoformat(),
        "end": (end - timedelta(days=1)).date().isoformat(),
        "ranking": rows,
        "chart": {
            "title": "Top salespeople by revenue (LKR)",
            "labels": [r["employee"] for r in rows[:6]],
            "values": [r["revenue_lkr"] for r in rows[:6]],
        },
    }


def profit_analysis(branch="all", start_date=None, end_date=None, group_by="category"):
    if group_by not in ("category", "product"):
        raise ValueError("group_by must be category or product")

    start, end = period(start_date, end_date)
    combined = {}

    for key in branches_for(branch):
        with session_for(key) as db:
            name = Product.category if group_by == "category" else (
                Product.brand + " " + Product.model
            )

            rows = db.execute(
                select(
                    name,
                    func.sum(
                        SaleItem.quantity * SaleItem.unit_price - SaleItem.discount
                    ),
                    func.sum(SaleItem.quantity * SaleItem.unit_cost),
                    func.sum(SaleItem.quantity),
                )
                .join(SaleItem, SaleItem.product_id == Product.id)
                .join(Sale, Sale.id == SaleItem.sale_id)
                .where(Sale.sold_at >= start)
                .where(Sale.sold_at < end)
                .where(Sale.status == "completed")
                .group_by(name)
            ).all()

            for title, revenue, cost, units in rows:
                if title not in combined:
                    combined[title] = {"name": title, "revenue_lkr": 0, "cost_lkr": 0, "units": 0}

                combined[title]["revenue_lkr"] += money(revenue)
                combined[title]["cost_lkr"] += money(cost)
                combined[title]["units"] += units

    output = []

    for row in combined.values():
        gross = round(row["revenue_lkr"] - row["cost_lkr"], 2)
        row["gross_profit_lkr"] = gross
        row["gross_margin_pct"] = round(
            gross / row["revenue_lkr"] * 100, 2
        ) if row["revenue_lkr"] else 0
        output.append(row)

    output.sort(key=lambda r: r["gross_profit_lkr"], reverse=True)

    return {
        "group_by": group_by,
        "start": start.date().isoformat(),
        "end": (end - timedelta(days=1)).date().isoformat(),
        "rows": output[:30],
        "chart": {
            "title": "Gross profit by " + group_by + " (LKR)",
            "labels": [r["name"] for r in output[:8]],
            "values": [r["gross_profit_lkr"] for r in output[:8]],
        },
    }


def inventory_insights(branch="all", category="", limit=15):
    low = []
    high = []

    for key in branches_for(branch):
        with session_for(key) as db:
            statement = select(Product, Inventory).join(
                Inventory, Inventory.product_id == Product.id
            )

            if category:
                statement = statement.where(
                    Product.category.ilike(f"%{category}%")
                )

            for product, stock in db.execute(statement):
                item = {
                    "branch": BRANCH_NAMES[key],
                    "product": product_label(product),
                    "category": product.category,
                    "quantity": stock.quantity,
                    "reorder_level": stock.reorder_level,
                }

                if stock.quantity <= stock.reorder_level:
                    low.append(item)

                high.append(item)

    low.sort(key=lambda r: r["quantity"])
    high.sort(key=lambda r: r["quantity"], reverse=True)

    return {
        "low_stock": low[:limit],
        "largest_stock_positions": high[:limit],
        "note": "Reorder levels are illustrative thresholds, not automatic purchase instructions.",
    }
