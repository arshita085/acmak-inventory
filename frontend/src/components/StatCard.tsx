type StatCardProps = {
  title: string;
  value: number;
  icon: string;
  change?: string;
};

function StatCard({ title, value, icon, change }: StatCardProps) {
  return (
    <div className="stat-card">
      <div className="stat-card-top">
        <span className="stat-icon">{icon}</span>
        {change && <span className="stat-change">{change}</span>}
      </div>

      <p>{title}</p>
      <h2>{value.toLocaleString()}</h2>
    </div>
  );
}

export default StatCard;