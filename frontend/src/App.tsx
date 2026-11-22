import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthMeResponse, User } from './types';
import { apiFetch, restoreEphemeralIfNeeded } from './lib/api';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import HubPage from './pages/HubPage';
import MitraDashboardPage from './pages/mitra/MitraDashboardPage';
import MitraDatabasePage from './pages/mitra/MitraDatabasePage';
import MitraTemplatePage from './pages/mitra/MitraTemplatePage';
import MitraPenugasanPage from './pages/mitra/MitraPenugasanPage';
import MitraKegiatanPage from './pages/mitra/MitraKegiatanPage';
import MitraEvaluasiPage from './pages/mitra/MitraEvaluasiPage';
import MitraLaporanPage from './pages/mitra/MitraLaporanPage';
import PegawaiModulePage from './pages/pegawai/PegawaiModulePage';
import KeuanganModulePage from './pages/keuangan/KeuanganModulePage';
import AkipModulePage from './pages/akip/AkipModulePage';

export default function App() {
  const location = useLocation();
  const [user, setUser] = useState<User | null>(null);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    apiFetch<AuthMeResponse>('/auth/me')
      .then(async (res) => {
        if (res.authenticated && res.user) {
          if (res.is_ephemeral_db) {
            await restoreEphemeralIfNeeded(res.counts);
          }
          setUser(res.user);
        } else {
          setUser(null);
        }
      })
      .catch(() => setUser(null))
      .finally(() => setChecked(true));
  }, [location.pathname]);

  if (!checked) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center space-y-2">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs font-bold text-slate-600">Memuat LENTERA BPS Banyuwangi...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage onLoginSuccess={(u) => setUser(u)} />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <Layout user={user} onLogout={() => setUser(null)}>
      <Routes>
        <Route path="/" element={<HubPage />} />
        <Route path="/mitra" element={<Navigate to="/mitra/dashboard" replace />} />
        <Route path="/mitra/dashboard" element={<MitraDashboardPage />} />
        <Route path="/mitra/database" element={<MitraDatabasePage />} />
        <Route path="/mitra/template" element={<MitraTemplatePage />} />
        <Route path="/mitra/penugasan" element={<MitraPenugasanPage />} />
        <Route path="/mitra/kegiatan" element={<MitraKegiatanPage />} />
        <Route path="/mitra/evaluasi" element={<MitraEvaluasiPage />} />
        <Route path="/mitra/laporan" element={<MitraLaporanPage />} />
        <Route path="/pegawai/*" element={<PegawaiModulePage />} />
        <Route path="/keuangan/*" element={<KeuanganModulePage />} />
        <Route path="/akip/*" element={<AkipModulePage />} />
        <Route path="*" element={<Navigate to="/mitra/dashboard" replace />} />
      </Routes>
    </Layout>
  );
}
