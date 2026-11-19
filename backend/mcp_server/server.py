import os

from mcp.server.fastmcp import FastMCP

from mcp_server import tools

role = os.environ.get("STOREBRIDGE_MCP_ROLE", "manager")
if role not in {"admin", "demo", "manager"}:
    raise RuntimeError("Invalid MCP role")

mcp = FastMCP("StoreBridge MCP")


@mcp.tool()
def search_inventory(query: str, branch: str = "all", category: str = "") -> dict:
    """Search mobile phones and accessories across all branches and return stocks and selling prices."""
    return tools.tool_search_inventory(query, branch, category)


@mcp.tool()
def compare_product_prices(query: str, branch: str = "all") -> dict:
    """Compare phone or accessory quantities, selling prices and latest purchase-batch cost per branch."""
    return tools.tool_compare_product_prices(query, branch)


@mcp.tool()
def get_inventory_insights(branch: str = "all", category: str = "") -> dict:
    """Show low-stock products and largest inventory positions across branches."""
    return tools.tool_get_inventory_insights(branch, category)


if role in {"admin", "demo"}:

    @mcp.tool()
    def get_stock_movements(
        query: str = "",
        branch: str = "all",
        start_date: str = "",
        end_date: str = "",
    ) -> dict:
        """Read historic receipts, sales and transfers; YYYY-MM-DD dates."""
        return tools.tool_get_stock_movements(query, branch, start_date, end_date)


    @mcp.tool()
    def get_sales_summary(
        branch: str = "all",
        start_date: str = "",
        end_date: str = "",
    ) -> dict:
        """Get revenue, gross profit, units sold and recorded expenses."""
        return tools.tool_get_sales_summary(branch, start_date, end_date)


    @mcp.tool()
    def compare_branch_performance(
        start_date: str = "",
        end_date: str = "",
    ) -> dict:
        """Compare monthly revenue and gross profit across three branches."""
        return tools.tool_compare_branch_performance(start_date, end_date)


    @mcp.tool()
    def get_employee_performance(
        branch: str = "all",
        start_date: str = "",
        end_date: str = "",
    ) -> dict:
        """Rank salespeople by revenue, units sold and gross profit."""
        return tools.tool_get_employee_performance(branch, start_date, end_date)


    @mcp.tool()
    def get_profit_analysis(
        branch: str = "all",
        start_date: str = "",
        end_date: str = "",
        group_by: str = "category",
    ) -> dict:
        """Compare category or product gross profitability, based on historical item costs."""
        return tools.tool_get_profit_analysis(branch, start_date, end_date, group_by)


if __name__ == "__main__":
    mcp.run(transport="stdio")
