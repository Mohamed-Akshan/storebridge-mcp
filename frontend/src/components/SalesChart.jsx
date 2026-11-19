import { ResponsiveContainer, BarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts';

export default function SalesChart({ chart }) {
  if (!chart?.labels?.length || !chart?.values?.length) {
    return null;
  }

  const items = chart.labels.map((name, index) => ({
    name,
    value: Number(chart.values[index] || 0),
  }));

  return (
    <div className="chart-box">
      <div className="chart-heading">{chart.title || 'Business comparison'}</div>
      <div className="chart-area">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={items} margin={{ top: 12, right: 10, left: 4, bottom: 15 }}>
            <CartesianGrid vertical={false} stroke="#e7ebed" strokeDasharray="3 4" />
            <XAxis dataKey="name" tick={{ fontSize: 10 }} interval={0} angle={items.length > 4 ? -20 : 0} textAnchor={items.length > 4 ? 'end' : 'middle'} />
            <YAxis tick={{ fontSize: 10 }} tickFormatter={(number) => number >= 1000000 ? `${(number / 1000000).toFixed(1)}M` : number >= 1000 ? `${Math.round(number / 1000)}K` : number} />
            <Tooltip formatter={(value) => [`Rs. ${Number(value).toLocaleString('en-LK')}`, 'Value']} />
            <Bar dataKey="value" fill="#158b70" radius={[6, 6, 0, 0]} maxBarSize={56} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
