"""Generate fictional but internally consistent Walk & Talk retail records."""

import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from decimal import Decimal

from sqlalchemy import delete

from database.connection import Base, BRANCH_NAMES, engines, session_for
from database.models import (
    Product,
    Inventory,
    PurchaseBatch,
    Employee,
    Sale,
    SaleItem,
    StockMovement,
    Expense,
)


PEOPLE = {
    "liberty": ["Ahamed Rizwan", "Fathima Nazeera", "Kevin Fernando", "Ayesha Rauf"],
    "galle_face": ["Mohamed Irfan", "Nethmi Perera", "Tharindu Silva", "Shanika Deen"],
    "pettah": ["Imran Hameed", "Sachini Jayawardena", "Rameez Farook", "Dilshan Peris"],
}

SUPPLIERS = [
    "Island Mobile Imports",
    "Ceylon Tech Distribution",
    "Metro Devices Trading",
    "Global Accessory Wholesale",
]


def catalog():
    items = []

    phones = {
        "Samsung": [
            ("Galaxy S26 Ultra", 380000),
            ("Galaxy S26", 235000),
            ("Galaxy S25 Ultra", 310000),
            ("Galaxy A56", 103000),
            ("Galaxy A36", 82000),
        ],
        "Apple": [
            ("iPhone 17 Pro Max", 440000),
            ("iPhone 17", 290000),
            ("iPhone 16 Pro Max", 365000),
            ("iPhone 16", 235000),
        ],
        "Xiaomi": [("Redmi Note 15", 78000), ("POCO X7 Pro", 113000)],
        "Oppo": [("Reno 14", 135000), ("A5 Pro", 70000)],
        "Vivo": [("V60", 142000), ("Y29", 72000)],
        "Honor": [("X9c", 105000)],
        "Google": [("Pixel 10", 265000)],
    }

    for brand, models in phones.items():
        for model, base in models:
            for storage, multiplier in [("256GB", 1), ("512GB", 1.23)]:
                for color in ["Black", "Silver"]:
                    items.append(("Smartphones", brand, model, storage, color, "", int(base * multiplier), 12))

    accessories = [
        ("Earbuds & Headphones", "Apple", "AirPods Pro 3", 74000, "iPhone"),
        ("Earbuds & Headphones", "Samsung", "Galaxy Buds3 Pro", 46000, "Galaxy"),
        ("Earbuds & Headphones", "Anker", "Soundcore R50i", 6500, "Android iPhone"),
        ("Earbuds & Headphones", "JBL", "Tune 520BT", 14500, "Android iPhone"),
        ("Earbuds & Headphones", "Sony", "WH-CH520", 18000, "Android iPhone"),
        ("Earbuds & Headphones", "Baseus", "Wired USB-C Earphones", 3500, "USB-C"),
        ("Chargers & Cables", "Apple", "20W USB-C Adapter", 8500, "iPhone USB-C"),
        ("Chargers & Cables", "Samsung", "45W Fast Charger", 10500, "Galaxy S26 Ultra S25 Ultra"),
        ("Chargers & Cables", "Anker", "30W Nano Charger", 8500, "Android iPhone"),
        ("Chargers & Cables", "UGREEN", "100W USB-C Cable", 3600, "USB-C"),
        ("Chargers & Cables", "Baseus", "Lightning Cable", 2500, "iPhone"),
        ("Power Banks", "Anker", "10000mAh Power Bank", 14500, "Android iPhone"),
        ("Power Banks", "Baseus", "20000mAh Power Bank", 17500, "Android iPhone"),
        ("Cases & Protection", "Spigen", "Rugged Armor Case", 8500, "Galaxy S26 Ultra"),
        ("Cases & Protection", "ESR", "MagSafe Clear Case", 6000, "iPhone 17 Pro Max"),
        ("Cases & Protection", "Generic", "Clear TPU Case", 1900, "Galaxy S26 Ultra"),
        ("Cases & Protection", "Generic", "Privacy Tempered Glass", 2500, "Galaxy S26 Ultra"),
        ("Cases & Protection", "Generic", "Camera Lens Protector", 1500, "iPhone 17 Pro Max"),
        ("Smartwatches", "Apple", "Watch Series 11", 128000, "iPhone"),
        ("Smartwatches", "Samsung", "Galaxy Watch8", 81000, "Galaxy"),
        ("Smartwatches", "Xiaomi", "Smart Band 10", 17500, "Android iPhone"),
        ("Gaming", "GameSir", "Mobile Game Controller", 18000, "Android iPhone"),
        ("Gaming", "Black Shark", "Phone Cooling Fan", 9000, "Android iPhone"),
        ("Photography", "DJI", "Osmo Mobile Gimbal", 62000, "Android iPhone"),
        ("Photography", "BOYA", "Wireless Clip Microphone", 27000, "Android iPhone"),
        ("Photography", "Ulanzi", "Mini Tripod", 6500, "Android iPhone"),
        ("Tablets", "Apple", "iPad Air 11-inch", 245000, "Apple Pencil"),
        ("Tablets", "Samsung", "Galaxy Tab S10 FE", 145000, "S Pen"),
        ("Tablet Accessories", "ESR", "iPad Keyboard Case", 18500, "iPad Air"),
        ("Adapters & Storage", "SanDisk", "128GB microSD Card", 7000, "Android"),
        ("Adapters & Storage", "UGREEN", "USB-C OTG Adapter", 2200, "USB-C"),
        ("Car Accessories", "Baseus", "Magnetic Car Mount", 5500, "Android iPhone"),
        ("Car Accessories", "Anker", "Dual Port Car Charger", 9500, "Android iPhone"),
    ]

    for category, brand, model, base, compatibility in accessories:
        colors = ["Black", "White"] if category in (
            "Earbuds & Headphones", "Cases & Protection"
        ) else ["Black"]

        for color in colors:
            items.append((category, brand, model, "", color, compatibility, base, 6))

    return items


def seed_branch(branch, items):
    rng = random.Random(911 + list(BRANCH_NAMES).index(branch) * 100)
    today = datetime.now(ZoneInfo("Asia/Colombo")).replace(
        hour=15, minute=0, second=0, microsecond=0, tzinfo=None
    )
    start = today - timedelta(days=365)

    with session_for(branch, writable=True) as db:
        for model in (
            StockMovement, SaleItem, Sale, PurchaseBatch,
            Inventory, Expense, Employee, Product,
        ):
            db.execute(delete(model))

        db.flush()

        employees = [Employee(name=name) for name in PEOPLE[branch]]
        db.add_all(employees)
        db.flush()

        products = []
        quantities = {}
        unit_costs = {}
        prices = {}
        movements = []
        batches = []

        for index, item in enumerate(items):
            category, brand, model, storage, color, compatibility, base, warranty = item
            sku = f"WT-{index + 1:04d}"

            product = Product(
                sku=sku,
                category=category,
                brand=brand,
                model=model,
                storage=storage,
                color=color,
                compatible_with=compatibility,
                warranty_months=warranty,
            )
            db.add(product)
            products.append(product)

        db.flush()

        for product, item in zip(products, items):
            base = item[6]
            selling = int(base * rng.uniform(0.98, 1.05) / 100) * 100
            cost = int(selling * rng.uniform(0.78, 0.91) / 100) * 100
            opening = rng.randint(16, 45) if item[0] != "Smartphones" else rng.randint(8, 20)

            if "S26 Ultra" in item[2] and branch == "liberty":
                opening = 3

            prices[product.id] = selling
            unit_costs[product.id] = cost
            quantities[product.id] = opening

            batches.append(PurchaseBatch(
                product_id=product.id,
                supplier=rng.choice(SUPPLIERS),
                received_at=start,
                units_received=opening,
                unit_cost=cost,
            ))
            movements.append(StockMovement(
                product_id=product.id,
                occurred_at=start,
                movement_type="opening_receipt",
                quantity_change=opening,
                reference="OPENING",
            ))

        sales = []
        sale_items = []
        sales_count = 0

        # Sales and periodic receipts are processed in chronological order.
        for day_index in range(366):
            date = start + timedelta(days=day_index)

            if date.date() > today.date():
                break

            if day_index and day_index % 24 == 0:
                for product in rng.sample(products, k=24):
                    add = rng.randint(10, 28)
                    new_cost = int(
                        unit_costs[product.id] * rng.uniform(0.94, 1.07) / 100
                    ) * 100
                    unit_costs[product.id] = new_cost
                    quantities[product.id] += add

                    batches.append(PurchaseBatch(
                        product_id=product.id,
                        supplier=rng.choice(SUPPLIERS),
                        received_at=date,
                        units_received=add,
                        unit_cost=new_cost,
                    ))
                    movements.append(StockMovement(
                        product_id=product.id,
                        occurred_at=date,
                        movement_type="receipt",
                        quantity_change=add,
                        reference=f"BATCH-{day_index}",
                    ))

            daily_sales = rng.randint(3, 8)

            for _ in range(daily_sales):
                product = rng.choice(products)

                if quantities[product.id] <= 0:
                    continue

                units = min(quantities[product.id], rng.choices([1, 2], [9, 1])[0])
                sold_at = date.replace(
                    hour=rng.randint(10, 20),
                    minute=rng.randint(0, 59),
                )

                if sold_at > today:
                    continue

                quantities[product.id] -= units
                sales_count += 1
                invoice = f"WT-{branch.upper()}-{sales_count:06d}"
                sale = Sale(
                    invoice_no=invoice,
                    sold_at=sold_at,
                    employee_id=rng.choice(employees).id,
                )
                sales.append(sale)
                db.add(sale)
                db.flush()

                discount = rng.choice([0, 0, 0, 0, 500, 1000])
                discount = min(discount, prices[product.id] * 0.04)

                sale_items.append(SaleItem(
                    sale_id=sale.id,
                    product_id=product.id,
                    quantity=units,
                    unit_price=prices[product.id],
                    unit_cost=unit_costs[product.id],
                    discount=discount,
                ))
                movements.append(StockMovement(
                    product_id=product.id,
                    occurred_at=sold_at,
                    movement_type="sale",
                    quantity_change=-units,
                    reference=invoice,
                ))

        # Ensure one reliable cross-branch stock example for demonstrations.
        # Liberty is out of stock, while the other branches can supply it.
        for product in products:
            if not (
                product.brand == "Samsung"
                and product.model == "Galaxy S26 Ultra"
                and product.storage == "256GB"
                and product.color == "Black"
            ):
                continue

            current = quantities[product.id]
            desired = {
                "liberty": 0,
                "galle_face": 5,
                "pettah": 8,
            }[branch]

            difference = desired - current

            if difference:
                quantities[product.id] = desired

                movements.append(StockMovement(
                    product_id=product.id,
                    occurred_at=today,
                    movement_type="demo_stock_adjustment",
                    quantity_change=difference,
                    reference="DEMO-RECONCILE",
                ))

        db.add_all(sale_items)
        db.add_all(batches)
        db.add_all(movements)

        for product in products:
            qty = quantities[product.id]
            db.add(Inventory(
                product_id=product.id,
                quantity=qty,
                selling_price=prices[product.id],
                reorder_level=5 if product.category == "Smartphones" else 8,
                updated_at=today,
            ))

        for i in range(13):
            month_index = today.year * 12 + today.month - 1 - i
            month = datetime(
                month_index // 12,
                month_index % 12 + 1,
                1,
            )

            for category, amount in [
                ("Rent", rng.randint(280000, 580000)),
                ("Salaries", rng.randint(250000, 430000)),
                ("Utilities", rng.randint(30000, 80000)),
            ]:
                db.add(Expense(
                    expense_date=month,
                    category=category,
                    amount=amount,
                    description="Synthetic monthly operating expense",
                ))

        db.commit()
        print(f"{BRANCH_NAMES[branch]}: {len(products)} SKUs, {sales_count} sales")


def main():
    items = catalog()

    for branch, engine in engines.items():
        Base.metadata.create_all(engine)
        seed_branch(branch, items)

    print("All three branch databases seeded successfully.")


if __name__ == "__main__":
    main()
