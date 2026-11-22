'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
  LayoutGrid,
  Database,
  FileUp,
  ClipboardList,
  Activity,
  Award,
  BarChart3,
  Users,
  Wallet,
  FolderOpen,
  ChevronDown,
  LogOut,
  Menu,
  X,
  Home,
} from 'lucide-react';
import { AuthMeResponse, User } from '@/types';
import { apiFetch, restoreEphemeralIfNeeded } from '@/lib/api';

type ModuleKey = 'akip' | 'mitra' | 'pegawai' | 'keuangan';

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [checked, setChecked] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const initialOpen = (): ModuleKey => {
    if (pathname.startsWith('/mitra')) return 'mitra';
    if (pathname.startsWith('/pegawai')) return 'pegawai';
    if (pathname.startsWith('/keuangan')) return 'keuangan';
    return 'akip';
  };

  const [openModule, setOpenModule] = useState<ModuleKey | null>(initialOpen);

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
          if (pathname !== '/login') {
            router.replace('/login');
          }
        }
      })
      .catch(() => {
        setUser(null);
        if (pathname !== '/login') {
          router.replace('/login');
        }
      })
      .finally(() => setChecked(true));
  }, [pathname, router]);

  if (pathname === '/login') {
    return <>{children}</>;
  }

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
    return null;
  }

  const toggleModule = (mod: ModuleKey) => {
    setOpenModule((prev) => (prev === mod ? null : mod));
  };

  const handleLogout = async () => {
    try {
      await apiFetch('/auth/logout', { method: 'POST' });
    } catch {
      // ignore
    }
    setUser(null);
    router.replace('/login');
  };

  const navLinkClass = (path: string) => {
    const active = pathname === path;
    return `flex items-center gap-2.5 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
      active
        ? 'bg-gradient-to-r from-blue-600 to-sky-500 text-white shadow-md shadow-blue-950/30'
        : 'text-blue-100/80 hover:bg-white/10 hover:text-white'
    }`;
  };

  const sidebarContent = (
    <div className="flex flex-col h-full bg-[#0B1D39] text-white">
      <div className="p-4 border-b border-white/10 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-white p-1 shadow-md flex items-center justify-center shrink-0">
            <img src="/images/logo_lentera.jpg" alt="LENTERA" className="w-full h-full object-contain rounded-xl" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-sm tracking-tight text-white">LENTERA</span>
              <span className="px-1.5 py-0.5 rounded-md bg-blue-500/30 text-sky-200 text-[9px] font-bold">BPS</span>
            </div>
            <p className="text-[10px] text-blue-200/70">BPS Kabupaten Banyuwangi</p>
          </div>
        </Link>
        <button onClick={() => setMobileOpen(false)} className="lg:hidden text-blue-200 hover:text-white p-1">
          <X className="w-5 h-5" />
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto p-3 space-y-2">
        <Link href="/" onClick={() => setMobileOpen(false)} className={navLinkClass('/')}>
          <Home className="w-4 h-4 text-sky-300" />
          <span>Portal Utama (Hub)</span>
        </Link>

        {/* PRIMA AKIP */}
        <div className="rounded-2xl bg-white/5 border border-white/10 overflow-hidden">
          <button type="button" onClick={() => toggleModule('akip')} className="w-full flex items-center justify-between p-3 hover:bg-white/5 transition">
            <div className="flex items-center gap-2.5 text-left">
              <div className="w-8 h-8 rounded-xl bg-white p-1 flex items-center justify-center shrink-0">
                <img src="/images/logo_prima.png" alt="PRIMA" className="w-full h-full object-contain" />
              </div>
              <div>
                <div className="text-xs font-extrabold text-white">PRIMA</div>
                <div className="text-[10px] text-sky-200/75">Arsip &amp; Manajemen AKIP</div>
              </div>
            </div>
            <ChevronDown className={`w-4 h-4 text-sky-300 transition-transform ${openModule === 'akip' ? 'rotate-180' : ''}`} />
          </button>
          {openModule === 'akip' && (
            <div className="px-2.5 pb-2.5 space-y-1">
              <Link href="/akip" onClick={() => setMobileOpen(false)} className={navLinkClass('/akip')}>
                <FolderOpen className="w-4 h-4 text-sky-300" />
                <span>Dashboard &amp; Arsip AKIP</span>
              </Link>
            </div>
          )}
        </div>

        {/* MONITORING MITRA */}
        <div className="rounded-2xl bg-white/5 border border-blue-400/25 overflow-hidden">
          <button type="button" onClick={() => toggleModule('mitra')} className="w-full flex items-center justify-between p-3 hover:bg-white/5 transition">
            <div className="flex items-center gap-2.5 text-left">
              <div className="w-8 h-8 rounded-xl bg-white p-1 flex items-center justify-center shrink-0">
                <img src="/images/logo_mitra.svg" alt="Mitra" className="w-full h-full object-contain" />
              </div>
              <div>
                <div className="text-xs font-extrabold text-white">MONITORING MITRA</div>
                <div className="text-[10px] text-sky-200/75">Pengelolaan &amp; Evaluasi Mitra</div>
              </div>
            </div>
            <ChevronDown className={`w-4 h-4 text-sky-300 transition-transform ${openModule === 'mitra' ? 'rotate-180' : ''}`} />
          </button>
          {openModule === 'mitra' && (
            <div className="px-2.5 pb-3 space-y-1">
              <Link href="/mitra/dashboard" onClick={() => setMobileOpen(false)} className={navLinkClass('/mitra/dashboard')}>
                <LayoutGrid className="w-4 h-4 text-sky-300" />
                <span>Dashboard Mitra</span>
              </Link>
              <div className="pt-2 pb-1 px-3 text-[9px] font-bold uppercase tracking-wider text-blue-300/60">Data &amp; Upload</div>
              <Link href="/mitra/database" onClick={() => setMobileOpen(false)} className={navLinkClass('/mitra/database')}>
                <Database className="w-4 h-4 text-sky-300" />
                <span>Data Mitra</span>
              </Link>
              <Link href="/mitra/template" onClick={() => setMobileOpen(false)} className={navLinkClass('/mitra/template')}>
                <FileUp className="w-4 h-4 text-sky-300" />
                <span>Template &amp; Upload</span>
              </Link>
              <div className="pt-2 pb-1 px-3 text-[9px] font-bold uppercase tracking-wider text-blue-300/60">Kegiatan &amp; Laporan</div>
              <Link href="/mitra/penugasan" onClick={() => setMobileOpen(false)} className={navLinkClass('/mitra/penugasan')}>
                <ClipboardList className="w-4 h-4 text-sky-300" />
                <span>Penugasan Mitra</span>
              </Link>
              <Link href="/mitra/kegiatan" onClick={() => setMobileOpen(false)} className={navLinkClass('/mitra/kegiatan')}>
                <Activity className="w-4 h-4 text-sky-300" />
                <span>Daftar Kegiatan</span>
              </Link>
              <Link href="/mitra/evaluasi" onClick={() => setMobileOpen(false)} className={navLinkClass('/mitra/evaluasi')}>
                <Award className="w-4 h-4 text-sky-300" />
                <span>Penilaian Mitra</span>
              </Link>
              <Link href="/mitra/laporan" onClick={() => setMobileOpen(false)} className={navLinkClass('/mitra/laporan')}>
                <BarChart3 className="w-4 h-4 text-sky-300" />
                <span>Laporan &amp; Honor</span>
              </Link>
            </div>
          )}
        </div>

        {/* KINERJA PEGAWAI */}
        <div className="rounded-2xl bg-white/5 border border-white/10 overflow-hidden">
          <button type="button" onClick={() => toggleModule('pegawai')} className="w-full flex items-center justify-between p-3 hover:bg-white/5 transition">
            <div className="flex items-center gap-2.5 text-left">
              <div className="w-8 h-8 rounded-xl bg-white p-1 flex items-center justify-center shrink-0">
                <img src="/images/logo_pegawai.svg" alt="Pegawai" className="w-full h-full object-contain" />
              </div>
              <div>
                <div className="text-xs font-extrabold text-white">KINERJA PEGAWAI</div>
                <div className="text-[10px] text-sky-200/75">Monitoring Kinerja Pegawai</div>
              </div>
            </div>
            <ChevronDown className={`w-4 h-4 text-sky-300 transition-transform ${openModule === 'pegawai' ? 'rotate-180' : ''}`} />
          </button>
          {openModule === 'pegawai' && (
            <div className="px-2.5 pb-2.5 space-y-1">
              <Link href="/pegawai" onClick={() => setMobileOpen(false)} className={navLinkClass('/pegawai')}>
                <Users className="w-4 h-4 text-sky-300" />
                <span>Dashboard &amp; Data Pegawai</span>
              </Link>
            </div>
          )}
        </div>

        {/* TRACKING KEUANGAN */}
        <div className="rounded-2xl bg-white/5 border border-white/10 overflow-hidden">
          <button type="button" onClick={() => toggleModule('keuangan')} className="w-full flex items-center justify-between p-3 hover:bg-white/5 transition">
            <div className="flex items-center gap-2.5 text-left">
              <div className="w-8 h-8 rounded-xl bg-white p-1 flex items-center justify-center shrink-0">
                <img src="/images/logo_keuangan.svg" alt="Keuangan" className="w-full h-full object-contain" />
              </div>
              <div>
                <div className="text-xs font-extrabold text-white">TRACKING KEUANGAN</div>
                <div className="text-[10px] text-sky-200/75">Pengajuan &amp; Pencairan</div>
              </div>
            </div>
            <ChevronDown className={`w-4 h-4 text-sky-300 transition-transform ${openModule === 'keuangan' ? 'rotate-180' : ''}`} />
          </button>
          {openModule === 'keuangan' && (
            <div className="px-2.5 pb-2.5 space-y-1">
              <Link href="/keuangan" onClick={() => setMobileOpen(false)} className={navLinkClass('/keuangan')}>
                <Wallet className="w-4 h-4 text-sky-300" />
                <span>Pengajuan &amp; Realisasi</span>
              </Link>
            </div>
          )}
        </div>
      </nav>

      <div className="p-3 border-t border-white/10 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="w-9 h-9 rounded-xl bg-blue-600 text-white font-extrabold text-xs flex items-center justify-center shrink-0">
            {(user.full_name || 'U').slice(0, 2).toUpperCase()}
          </div>
          <div className="min-w-0">
            <p className="text-xs font-bold text-white truncate">{user.full_name}</p>
            <p className="text-[10px] text-blue-200/70 capitalize">{user.role}</p>
          </div>
        </div>
        <button onClick={handleLogout} title="Keluar" className="p-2 rounded-xl bg-white/10 hover:bg-white/20 text-blue-100 transition">
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen flex bg-slate-50">
      <aside className="hidden lg:block w-64 shrink-0 fixed inset-y-0 left-0 z-30 shadow-xl">{sidebarContent}</aside>

      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          <div className="w-64 max-w-[85vw] h-full shadow-2xl">{sidebarContent}</div>
          <div className="flex-1 bg-slate-900/50 backdrop-blur-sm" onClick={() => setMobileOpen(false)} />
        </div>
      )}

      <div className="flex-1 lg:pl-64 flex flex-col min-w-0">
        <header className="sticky top-0 z-20 h-16 bg-white/90 backdrop-blur-md border-b border-slate-200/80 px-4 sm:px-6 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <button type="button" onClick={() => setMobileOpen(true)} className="lg:hidden p-2 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50">
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full border border-slate-200 bg-white p-0.5 flex items-center justify-center">
                <img src="/images/logo_lentera.jpg" alt="LENTERA" className="w-full h-full object-contain rounded-full" />
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="text-xs sm:text-sm font-extrabold text-slate-900">LENTERA BPS</span>
                  <span className="px-1.5 py-0.5 rounded-md bg-blue-50 text-blue-700 border border-blue-200/70 text-[10px] font-bold">3510</span>
                </div>
                <p className="text-[10px] text-slate-400 hidden sm:block">Badan Pusat Statistik Kabupaten Banyuwangi</p>
              </div>
            </div>
          </div>

          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-200/80">
            <span className="text-xs font-bold text-slate-800">{user.full_name}</span>
            <span className="px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 text-[10px] font-bold capitalize">{user.role}</span>
          </div>
        </header>

        <main className="flex-1 p-4 sm:p-6 lg:p-8">{children}</main>

        <footer className="border-t border-slate-200/80 bg-white px-6 py-4 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-400">
          <div>
            <strong className="text-slate-700">LENTERA BPS</strong> &bull; Badan Pusat Statistik Kabupaten Banyuwangi
          </div>
          <div>&copy; 2025 - 2026 LENTERA BPS Banyuwangi. Portal Terpadu AKIP, Mitra, Kinerja &amp; Keuangan.</div>
        </footer>
      </div>
    </div>
  );
}
