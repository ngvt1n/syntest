import api from "./api";

export const dashboardService = {
  async getParticipantDashboard() {
    const response = await api.get("/participant/dashboard");
    return response.data;
  },

  async getResearcherDashboard() {
    // Fetch both summary and recent data
    const [summary, recent] = await Promise.all([
      api.get("/researcher/dashboard/summary"),
      api.get("/researcher/dashboard/recent"),
    ]);

    return {
      summary: summary.data,
      recent: recent.data,
    };
  },
};
