import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Navbar } from './components/common/Navbar';
import { Footer } from './components/common/Footer';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { Home } from './pages/Home';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Profile } from './pages/Profile';
import { AdminDashboard } from './pages/AdminDashboard';
import { ReportItem } from './pages/ReportItem';
import { MyReports } from './pages/MyReports';
import { ItemDetails } from './pages/ItemDetails';
import { EditItem } from './pages/EditItem';
import { SearchItems } from './pages/SearchItems';
import { MyClaims } from './pages/MyClaims';
import { AdminClaims } from './pages/AdminClaims';
import { Dashboard } from './pages/Dashboard';
import { NotificationsPage } from './pages/NotificationsPage';
import { NotFound } from './pages/NotFound';

export const App: React.FC = () => {
  return (
    <>
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/notifications"
            element={
              <ProtectedRoute>
                <NotificationsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <ProtectedRoute requireAdmin={true}>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/search"
            element={
              <ProtectedRoute>
                <SearchItems />
              </ProtectedRoute>
            }
          />
          {/* Phase 4: Lost & Found Core Module Routes */}
          <Route
            path="/report-lost"
            element={
              <ProtectedRoute>
                <ReportItem initialType="LOST" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/report-found"
            element={
              <ProtectedRoute>
                <ReportItem initialType="FOUND" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/my-reports"
            element={
              <ProtectedRoute>
                <MyReports />
              </ProtectedRoute>
            }
          />
          <Route
            path="/my-claims"
            element={
              <ProtectedRoute>
                <MyClaims />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/claims"
            element={
              <ProtectedRoute requireAdmin={true}>
                <AdminClaims />
              </ProtectedRoute>
            }
          />
          <Route
            path="/items/:id"
            element={
              <ProtectedRoute>
                <ItemDetails />
              </ProtectedRoute>
            }
          />
          <Route
            path="/items/:id/edit"
            element={
              <ProtectedRoute>
                <EditItem />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
    </>
  );
};

export default App;
