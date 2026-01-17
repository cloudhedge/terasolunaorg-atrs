/**
 * Main App component with routing
 */
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout';
import { useAuthStore } from './stores/authStore';

// Pages
import Home from './pages/Home';
import Login from './pages/Login';
import FlightSearch from './pages/FlightSearch';
import Reserve from './pages/Reserve';
import ReserveConfirm from './pages/ReserveConfirm';
import ReserveComplete from './pages/ReserveComplete';
import ReserveFail from './pages/ReserveFail';

// Protected route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <Layout>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/flights" element={<FlightSearch />} />
        
        {/* Reservation flow (no auth required for guest booking) */}
        <Route path="/reserve" element={<Reserve />} />
        <Route path="/reserve/confirm" element={<ReserveConfirm />} />
        <Route path="/reserve/complete" element={<ReserveComplete />} />
        <Route path="/reserve/fail" element={<ReserveFail />} />

        {/* Member routes (protected) */}
        <Route
          path="/member/update"
          element={
            <ProtectedRoute>
              <div>Member Update - Coming Soon</div>
            </ProtectedRoute>
          }
        />
        <Route
          path="/member/register"
          element={<div>Member Registration - Coming Soon</div>}
        />
        <Route
          path="/history/create"
          element={
            <ProtectedRoute>
              <div>History Report - Coming Soon</div>
            </ProtectedRoute>
          }
        />
        <Route
          path="/history/download"
          element={
            <ProtectedRoute>
              <div>History Download - Coming Soon</div>
            </ProtectedRoute>
          }
        />

        {/* 404 */}
        <Route
          path="*"
          element={
            <div className="row">
              <div className="col-md-12">
                <div className="alert alert-warning">
                  <h2>ページが見つかりません</h2>
                  <p>お探しのページは存在しません。</p>
                </div>
              </div>
            </div>
          }
        />
      </Routes>
    </Layout>
  );
}
