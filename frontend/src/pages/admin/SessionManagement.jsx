import { useState, useEffect } from "react";
import { getSessions, terminateSession, terminateAllOtherSessions } from "../../api/endpoints";
import { useAuth } from "../../context/AuthContext";

export default function SessionManagement() {
  const { user, sessionId } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [terminatingId, setTerminatingId] = useState(null);

  useEffect(() => {
    fetchSessions();
  }, []);

  async function fetchSessions() {
    try {
      setLoading(true);
      const response = await getSessions();
      setSessions(response.data);
      setError("");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to fetch sessions");
    } finally {
      setLoading(false);
    }
  }

  async function handleTerminateSession(sessionIdToTerminate) {
    if (
      !window.confirm(
        "Are you sure you want to terminate this session? The device will be logged out."
      )
    ) {
      return;
    }

    try {
      setTerminatingId(sessionIdToTerminate);
      await terminateSession(sessionIdToTerminate, "User terminated via dashboard");
      setSessions(sessions.filter((s) => s.id !== sessionIdToTerminate));
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to terminate session");
    } finally {
      setTerminatingId(null);
    }
  }

  async function handleTerminateAllOthers() {
    if (
      !window.confirm(
        "This will log out all other sessions. Only your current session will remain active."
      )
    ) {
      return;
    }

    try {
      setLoading(true);
      await terminateAllOtherSessions(sessionId);
      await fetchSessions();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to terminate sessions");
    } finally {
      setLoading(false);
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const getStatusBadgeColor = (status) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800";
      case "revoked":
        return "bg-red-100 text-red-800";
      case "expired":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (loading) {
    return <div className="p-4">Loading sessions...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-6">Active Sessions</h2>

      {error && (
        <div className="bg-red-50 text-red-700 p-3 rounded mb-4">{error}</div>
      )}

      <p className="text-gray-600 mb-4">
        Manage your active login sessions across different devices. You can
        terminate sessions to force logout from specific devices.
      </p>

      {sessions.length > 0 && (
        <button
          onClick={handleTerminateAllOthers}
          className="mb-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Log out All Other Devices
        </button>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-4 py-2 text-left">Device</th>
              <th className="px-4 py-2 text-left">IP Address</th>
              <th className="px-4 py-2 text-left">Login Time</th>
              <th className="px-4 py-2 text-left">Last Activity</th>
              <th className="px-4 py-2 text-left">Status</th>
              <th className="px-4 py-2 text-left">Action</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((session) => (
              <tr key={session.id} className="border-b hover:bg-gray-50">
                <td className="px-4 py-3">
                  <div>
                    <p className="font-medium">{session.device_name}</p>
                    <p className="text-xs text-gray-500">
                      ID: {session.id.substring(0, 8)}...
                    </p>
                  </div>
                </td>
                <td className="px-4 py-3">{session.ip_address || "Unknown"}</td>
                <td className="px-4 py-3">{formatDate(session.created_at)}</td>
                <td className="px-4 py-3">{formatDate(session.last_activity)}</td>
                <td className="px-4 py-3">
                  <span
                    className={`px-3 py-1 rounded text-xs font-medium ${getStatusBadgeColor(
                      session.status
                    )}`}
                  >
                    {session.status.charAt(0).toUpperCase() +
                      session.status.slice(1)}
                  </span>
                  {session.id === sessionId && (
                    <p className="text-xs text-blue-600 mt-1">Current Session</p>
                  )}
                </td>
                <td className="px-4 py-3">
                  {session.id !== sessionId && session.status === "active" && (
                    <button
                      onClick={() => handleTerminateSession(session.id)}
                      disabled={terminatingId === session.id}
                      className="px-3 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600 disabled:opacity-50"
                    >
                      {terminatingId === session.id ? "Terminating..." : "Terminate"}
                    </button>
                  )}
                  {session.id === sessionId && (
                    <span className="text-xs text-gray-500">Current</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {sessions.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No active sessions found.
        </div>
      )}
    </div>
  );
}
