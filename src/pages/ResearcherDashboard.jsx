import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import DashboardStatCard from "../components/dashboard/DashboardStatCard";
import RecentTable from "../components/dashboard/RecentTable";
import { dashboardService } from "../services/dashboard";

export default function ResearcherDashboard() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [recent, setRecent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!authLoading && (!user || user.role !== "researcher")) {
      navigate("/login");
      return;
    }

    if (user && user.role === "researcher") {
      loadData();
    }
  }, [user, authLoading, navigate]);

  async function loadData() {
    try {
      setLoading(true);
      setError(null);
      
      const data = await dashboardService.getResearcherDashboard();
      
      setSummary(data.summary);
      setRecent(data.recent);
    } catch (e) {
      console.error("Failed to load dashboard", e);
      setError(e.response?.data?.error || "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  }

  if (authLoading || loading) {
    return (
      <div className="dashboard-loading">
        <div className="dashboard-spinner"></div>
        <p className="dashboard-loading-text">Loading dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <h2 className="dashboard-error-title">Error Loading Dashboard</h2>
        <p className="dashboard-error-text">{error}</p>
        <button onClick={loadData} className="dashboard-error-button">
          Try Again
        </button>
      </div>
    );
  }

  if (!summary || !recent) {
    return <p>No data available</p>;
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Researcher Dashboard</h1>
        <p className="dashboard-welcome">Welcome back, {user?.name}</p>
      </div>

      {/* Summary Stats */}
      <div className="dashboard-stats-grid">
        <DashboardStatCard
          label="Total Participants"
          value={summary.total_participants}
        />
        <DashboardStatCard
          label="Active Participants"
          value={summary.active_participants}
        />
        <DashboardStatCard
          label="Total Stimuli"
          value={summary.total_stimuli}
        />
        <DashboardStatCard
          label="Tests Completed"
          value={summary.tests_completed}
        />
      </div>

      {/* Recent Activity */}
      <RecentTable
        title="Recent Participants"
        columns={["name", "email", "created_at"]}
        rows={recent.participants}
      />

      <RecentTable
        title="Recent Stimuli"
        columns={["description", "family", "created_at"]}
        rows={recent.stimuli}
      />
    </div>
  );
}