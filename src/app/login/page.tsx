'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Shield, Lock, Mail, ArrowRight } from 'lucide-react';
import { apiFetch } from '@/lib/api';

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('tfdewanto@bps.go.id');
  const [password, setPassword] = useState('12345678');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await apiFetch<{ ok: boolean }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });
      if (res.ok) {
        router.replace('/mitra/dashboard');
      }
    } catch (err: any) {
      setError(err.message || 'Gagal masuk. Periksa kembali kredensial Anda.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen executive-banner flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute -right-24 -top-24 w-96 h-96 bg-sky-400/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -left-24 -bottom-24 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 w-full max-w-md bg-white rounded-3xl p-8 shadow-2xl border border-blue-100">
        <div className="text-center mb-6">
          <div className="w-16 h-16 rounded-2xl bg-blue-50 border border-blue-100 p-2 mx-auto flex items-center justify-center shadow-sm mb-3">
            <img src="/images/logo_lentera.jpg" alt="LENTERA BPS" className="w-full h-full object-contain rounded-xl" />
          </div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200/70 text-[11px] font-bold mb-2">
            <Shield className="w-3.5 h-3.5" />
            <span>SSO LENTERA BPS</span>
          </div>
          <h1 className="text-xl font-extrabold text-slate-900">Portal Terpadu BPS Banyuwangi</h1>
          <p className="text-xs text-slate-500 mt-1">Masuk menggunakan akun resmi BPS Kabupaten Banyuwangi</p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-blue-50 border border-blue-200 text-xs font-semibold text-blue-800">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5">Email / Username BPS</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-xs font-medium focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none"
                placeholder="nama@bps.go.id"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5">Kata Sandi</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-xs font-medium focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-600 to-sky-500 hover:opacity-95 text-white text-xs font-bold shadow-lg shadow-blue-600/25 flex items-center justify-center gap-2 transition disabled:opacity-60"
          >
            <span>{loading ? 'Memproses...' : 'Masuk ke LENTERA BPS'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
