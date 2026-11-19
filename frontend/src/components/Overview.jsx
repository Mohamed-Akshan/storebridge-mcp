import { useEffect, useState } from 'react';
import { AlertTriangle, ArrowUpRight, Banknote, Boxes, ShoppingBag, TrendingUp } from 'lucide-react';

import { api } from '../api.js';
import SalesChart from './SalesChart.jsx';

function money(value) {
  return `Rs. ${Number(value || 0).toLocaleString('en-LK', { maximumFractionDigits: 0 })}`;
}

export default function Overview({ onChat }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api('/overview').then(setData).catch((reason) => setError(reason.message));
  }, []);

  if (error) return <div className="error-banner">{error}</div>;
  if (!data) return <div className="page-wrap"><p>Loading business overview...</p></div>;

  const metrics = [
    { label: 'Total revenue', value: money(data.totals.revenue_lkr), icon: Banknote },
    { label: 'Gross profit', value: money(data.totals.gross_profit_lkr), icon: TrendingUp },
    { label: 'Units sold', value: data.totals.units_sold, icon: ShoppingBag },
    { label: 'Low-stock alerts shown', value: data.low_stock_count_shown, icon: Boxes },
  ];

  return (
    <div className="page-wrap">
      <header className="page-header">
        <div className="eyebrow">OWNER OVERVIEW</div>
        <div className="header-flex">
          <div><h1>Business Overview</h1><p>Across all three branches · {data.period_start} to {data.period_end}</p></div>
          <button className="primary-button" onClick={onChat}>Ask the assistant <ArrowUpRight size={16} /></button>
        </div>
      </header>

      <div className="metric-grid">
        {metrics.map((metric) => (
          <div key={metric.label} className="metric-card">
            <metric.icon size={20} />
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
          </div>
        ))}
      </div>

      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-heading"><div><h2>Branch performance</h2><p>Revenue in Sri Lankan rupees</p></div></div>
          <SalesChart chart={data.chart} />
        </section>
        <section className="panel">
          <div className="panel-heading"><div><h2>Top salespeople</h2><p>Ranked by revenue this month</p></div></div>
          <div className="leader-list">
            {data.top_salespeople.map((person, index) => (
              <div className="leader-row" key={`${person.branch}-${person.employee}`}>
                <span className="rank">{index + 1}</span>
                <div><strong>{person.employee}</strong><small>{person.branch}</small></div>
                <b>{money(person.revenue_lkr)}</b>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="panel">
        <div className="panel-heading"><div><h2>Branch summary</h2><p>Combined view from independent PostgreSQL databases</p></div></div>
        <div className="table-scroll"><table className="data-table"><thead><tr><th>Branch</th><th>Revenue</th><th>Gross profit</th><th>Units sold</th><th>Gross margin</th></tr></thead><tbody>
          {data.branches.map((branch) => <tr key={branch.branch}>
            <td><strong>{branch.branch}</strong></td><td>{money(branch.revenue_lkr)}</td>
            <td>{money(branch.gross_profit_lkr)}</td><td>{branch.units_sold}</td>
            <td>{branch.gross_margin_pct}%</td>
          </tr>)}
        </tbody></table></div>
      </section>

      {data.low_stock_products.length > 0 && (
        <section className="panel low-panel">
          <h2><AlertTriangle size={18} /> Inventory to review</h2>
          <div className="low-list">{data.low_stock_products.slice(0, 5).map((item, index) => (
            <div key={index}><strong>{item.product}</strong><span>{item.branch} · {item.quantity} units left</span></div>
          ))}</div>
        </section>
      )}
      <p className="fineprint">Illustrative synthetic data. Gross profit excludes operating expenses. Low-stock alerts are capped on this overview; ask the assistant for complete analysis.</p>
    </div>
  );
}
