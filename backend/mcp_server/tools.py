from database import queries


def tool_search_inventory(query: str, branch: str = "all", category: str = ""):
    return {
        "matches": queries.inventory_search(query, branch, category),
        "note": "If no matching rows appear, check spelling, variant or database freshness.",
    }


def tool_compare_product_prices(query: str, branch: str = "all"):
    return {
        "products": queries.price_comparison(query, branch),
        "note": (
            "Latest batch cost is NOT necessarily the actual cost of remaining stock. "
            "Indicative spread excludes overheads."
        ),
    }


def tool_get_stock_movements(
    query: str = "",
    branch: str = "all",
    start_date: str = "",
    end_date: str = "",
):
    return {
        "movements": queries.stock_movements(
            query, branch, start_date or None, end_date or None
        )
    }


def tool_get_sales_summary(
    branch: str = "all",
    start_date: str = "",
    end_date: str = "",
):
    return queries.sales_summary(branch, start_date or None, end_date or None)


def tool_compare_branch_performance(
    start_date: str = "",
    end_date: str = "",
):
    return queries.sales_summary("all", start_date or None, end_date or None)


def tool_get_employee_performance(
    branch: str = "all",
    start_date: str = "",
    end_date: str = "",
):
    return queries.employee_performance(branch, start_date or None, end_date or None)


def tool_get_profit_analysis(
    branch: str = "all",
    start_date: str = "",
    end_date: str = "",
    group_by: str = "category",
):
    return queries.profit_analysis(
        branch, start_date or None, end_date or None, group_by
    )


def tool_get_inventory_insights(branch: str = "all", category: str = ""):
    return queries.inventory_insights(branch, category)
