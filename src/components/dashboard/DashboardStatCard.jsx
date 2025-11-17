export default function DashboardStatCard({ label, value }) {
    return (
      <div className="p-6 bg-white shadow-md rounded-lg border border-gray-200">
        <h3 className="text-gray-500 text-sm">{label}</h3>
        <p className="text-3xl font-semibold">{value}</p>
      </div>
    );
  }
  