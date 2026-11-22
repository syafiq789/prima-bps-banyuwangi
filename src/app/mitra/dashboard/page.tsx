'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Users,
  Calendar,
  ClipboardList,
  Wallet,
  Database,
  FileUp,
  Plus,
  BarChart3,
  ArrowRight,
  Award,
  FileSpreadsheet,
  Home,
} from 'lucide-react';
import { apiFetch, formatRupiah } from '@/lib/api';
import { KegiatanItem, PenugasanItem } from '@/types';

interface DashboardData {
  kpi: {
    total_mitra: number;
    total_kegiatan: number;
    total_penugasan: number;
    penugasan_selesai: number;
    penugasan_proses: number;
    total_honor_all: number;
    avg_score: number;
  };
  tim_counts: Record<string, number>;
  sebaran_kecamatan: { kecamatan: string; count: number }[];
  penugasan_terbaru: PenugasanItem[];
  kegiatan_aktif: KegiatanItem[];
}

export default function MitraDashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    apiFetch<{ ok: boolean } & DashboardData>('/mitra/dashboard')
      .then((res) => setData(res))
      .catch(() => {});
  }, []);

  const kpi = data?.kpi || {
    total_mitra: 0,
    total_kegiatan: 0,
    total_penugasan: 0,
    penugasan_selesai: 0,
    penugasan_proses: 0,
    total_honor_all: 0,
    avg_score: 0,
  };

  const sebaran = data?.sebaran_kecamatan || [];
  const activeSebaran = sebaran.filter((s) => s.count > 0);
  const chartItems = activeSebaran.length > 0 ? activeSebaran : sebaran.slice(0, 12);
  const maxVal = Math.max(1, ...chartItems.map((c) => c.count));

  const timCards = [
    { key: 'Tim Distribusi', desc: 'Harga, Perdagangan & Jasa' },
    { key: 'Tim Neraca', desc: 'Neraca & Ekonomi Wilayah' },
    { key: 'Tim Produksi', desc: 'Pertanian & Industri' },
    { key: 'Tim PLS', desc: 'Pengolahan Data & TI' },
  ];

  return (
    <div className="space-y-6">
      <div className="executive-banner rounded-3xl p-5 sm:p-6 text-white shadow-xl border border-blue-400/20 relative overflow-hidden">
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-5">
          <div className="flex items-start sm:items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-white/95 p-1.5 shadow-lg flex items-center justify-center shrink-0">
              <img src="/images/logo_mitra.svg" alt="Mitra" className="w-full h-full object-contain" />
            </div>
            <div>
              <div className="flex items-center gap-1.5 text-[11px] text-blue-200/80 mb-1">
                <Link href="/" className="hover:text-white inline-flex items-center gap-1">
                  <Home className="w-3 h-3" /> LENTERA
                </Link>
                <span>/</span>
                <span className="text-white font-semibold">Dashboard Mitra</span>
              </div>
              <div className="flex flex-wrap items-center gap-2.5">
                <h1 className="text-xl sm:text-2xl font-extrabold tracking-tight">Dashboard Mitra</h1>
                <span className="px-3 py-0.5 rounded-full text-[11px] font-semibold bg-white/15 text-sky-100 border border-white/20">
                  BPS Banyuwangi (3510)
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-blue-950/40 text-blue-100 border border-white/15">
                  {kpi.total_mitra} Mitra &bull; {kpi.total_kegiatan} Kegiatan
                </span>
              </div>
              <p className="text-xs text-blue-100/80 mt-1.5">
                Ringkasan data mitra statistik, sebaran 25 kecamatan, kegiatan per tim kerja, dan progres penugasan lapangan.
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Link href="/mitra/database" className="h-10 px-4 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 font-semibold text-xs flex items-center gap-1.5 transition">
              <Database className="w-3.5 h-3.5 text-sky-200" />
              <span>Data Mitra</span>
            </Link>
            <Link href="/mitra/template" className="h-10 px-4 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 font-semibold text-xs flex items-center gap-1.5 transition">
              <FileUp className="w-3.5 h-3.5 text-sky-200" />
              <span>Template &amp; Upload</span>
            </Link>
            <Link href="/mitra/penugasan" className="h-10 px-4 rounded-xl bg-white hover:bg-blue-50 text-blue-700 font-bold text-xs shadow-lg flex items-center gap-1.5 transition">
              <Plus className="w-3.5 h-3.5" />
              <span>Tugaskan Mitra</span>
            </Link>
          </div>
        </div>
      </div>

      {/* 4 Kartu Statistik (Tanpa Persen) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link href="/mitra/database" className="bg-white rounded-3xl p-5 border border-slate-200/80 shadow-soft hover:shadow-lg hover:border-blue-300 transition relative overflow-hidden group">
          <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-blue-600 to-sky-400" />
          <div className="flex items-start justify-between">
            <div>
              <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Total Mitra</p>
              <p className="text-3xl font-black text-slate-900 mt-1.5">
                {kpi.total_mitra} <span className="text-xs font-semibold text-slate-400">Orang</span>
              </p>
            </div>
            <div className="w-11 h-11 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center group-hover:bg-blue-600 group-hover:text-white transition">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px]">
            <span className="text-slate-500">Cakupan Wilayah</span>
            <span className="font-bold text-blue-700">25 Kecamatan</span>
          </div>
        </Link>

        <Link href="/mitra/kegiatan" className="bg-white rounded-3xl p-5 border border-slate-200/80 shadow-soft hover:shadow-lg hover:border-blue-300 transition relative overflow-hidden group">
          <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-blue-600 to-sky-400" />
          <div className="flex items-start justify-between">
            <div>
              <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Total Kegiatan</p>
              <p className="text-3xl font-black text-slate-900 mt-1.5">
                {kpi.total_kegiatan} <span className="text-xs font-semibold text-slate-400">Kegiatan</span>
              </p>
            </div>
            <div className="w-11 h-11 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center group-hover:bg-blue-600 group-hover:text-white transition">
              <Calendar className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px]">
            <span className="text-slate-500">Distribusi Tim</span>
            <span className="font-bold text-blue-700">4 Tim Kerja BPS</span>
          </div>
        </Link>

        <Link href="/mitra/penugasan" className="bg-white rounded-3xl p-5 border border-slate-200/80 shadow-soft hover:shadow-lg hover:border-blue-300 transition relative overflow-hidden group">
          <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-blue-600 to-sky-400" />
          <div className="flex items-start justify-between">
            <div>
              <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Penugasan Mitra</p>
              <p className="text-3xl font-black text-blue-700 mt-1.5">
                {kpi.total_penugasan} <span className="text-xs font-semibold text-slate-400">Tugas</span>
              </p>
            </div>
            <div className="w-11 h-11 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center group-hover:bg-blue-600 group-hover:text-white transition">
              <ClipboardList className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px]">
            <span className="text-slate-500">{kpi.penugasan_selesai} Selesai</span>
            <span className="font-bold text-sky-600">{kpi.penugasan_proses} Berjalan</span>
          </div>
        </Link>

        <Link href="/mitra/laporan" className="bg-white rounded-3xl p-5 border border-slate-200/80 shadow-soft hover:shadow-lg hover:border-blue-300 transition relative overflow-hidden group">
          <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-sky-500 to-blue-600" />
          <div className="flex items-start justify-between">
            <div className="min-w-0">
              <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Total Honorarium</p>
              <p className="text-xl sm:text-2xl font-black font-mono text-blue-700 mt-2 truncate">{formatRupiah(kpi.total_honor_all)}</p>
            </div>
            <div className="w-11 h-11 rounded-2xl bg-sky-50 text-sky-600 flex items-center justify-center shrink-0 group-hover:bg-blue-600 group-hover:text-white transition">
              <Wallet className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px]">
            <span className="text-slate-500">Nilai Rata-Rata</span>
            <span className="font-bold text-slate-800">{kpi.avg_score > 0 ? `${kpi.avg_score} / 100` : 'Belum Dinilai'}</span>
          </div>
        </Link>
      </div>

      {/* Grafik Sebaran Kecamatan + 4 Tim Kerja */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        <div className="lg:col-span-7 bg-white rounded-3xl p-6 border border-slate-200/80 shadow-soft flex flex-col justify-between">
          <div className="flex items-center justify-between gap-3 pb-4 border-b border-slate-100 mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                <BarChart3 className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-sm sm:text-base font-extrabold text-slate-900">Sebaran Mitra per Kecamatan</h2>
                <p className="text-xs text-slate-500">Distribusi mitra statistik di wilayah Kabupaten Banyuwangi</p>
              </div>
            </div>
            <Link href="/mitra/database" className="text-xs font-bold text-blue-600 hover:underline inline-flex items-center gap-1">
              Lihat Data <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="h-56 flex items-end gap-1.5 overflow-x-auto pt-4 pb-2">
            {chartItems.map((item) => {
              const heightPx = Math.max(8, Math.round((item.count / maxVal) * 165));
              return (
                <div key={item.kecamatan} className="flex-1 min-w-[24px] flex flex-col items-center justify-end gap-1 group">
                  <span className="text-[10px] font-bold text-blue-700 font-mono">{item.count}</span>
                  <div
                    className="w-full max-w-[26px] rounded-t-lg bg-gradient-to-t from-blue-600 to-sky-400 group-hover:from-blue-700 group-hover:to-blue-500 transition-all"
                    style={{ height: `${heightPx}px` }}
                    title={`${item.kecamatan}: ${item.count} Mitra`}
                  />
                  <span className="text-[9px] text-slate-500 truncate max-w-[42px] text-center" title={item.kecamatan}>
                    {item.kecamatan.slice(0, 5)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="lg:col-span-5 bg-white rounded-3xl p-6 border border-slate-200/80 shadow-soft flex flex-col justify-between">
          <div className="flex items-center justify-between gap-2 pb-4 border-b border-slate-100 mb-4">
            <div>
              <h2 className="text-sm sm:text-base font-extrabold text-slate-900">Kegiatan per Tim Kerja</h2>
              <p className="text-xs text-slate-500">Klik kartu tim untuk membuka daftar kegiatannya</p>
            </div>
            <Link href="/mitra/kegiatan" className="text-xs font-bold text-blue-600 hover:underline">
              Semua &rarr;
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 flex-1">
            {timCards.map((t) => (
              <Link
                key={t.key}
                href={`/mitra/kegiatan?tim=${encodeURIComponent(t.key)}`}
                className="p-4 rounded-2xl bg-slate-50/80 hover:bg-blue-50/70 border border-slate-200/80 hover:border-blue-300 transition flex flex-col justify-between group"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-extrabold text-slate-900 group-hover:text-blue-700">{t.key}</span>
                  <span className="text-lg font-black text-blue-700 font-mono">{data?.tim_counts?.[t.key] || 0}</span>
                </div>
                <p className="text-[10px] text-slate-500 mt-2">{t.desc}</p>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Penugasan Terbaru + Kegiatan Aktif */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        <div className="lg:col-span-7 bg-white rounded-3xl p-6 border border-slate-200/80 shadow-soft">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
            <div>
              <h2 className="text-base font-extrabold text-slate-900">Penugasan Mitra Terbaru</h2>
              <p className="text-xs text-slate-500">Daftar penugasan terbaru beserta jumlah dokumen</p>
            </div>
            <Link href="/mitra/penugasan" className="text-xs font-bold text-blue-600 hover:underline inline-flex items-center gap-1">
              Kelola <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="overflow-x-auto rounded-2xl border border-slate-200/80">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-slate-50/90 border-b border-slate-200/80 text-slate-600 uppercase font-bold text-[10px]">
                  <th className="py-3 px-4">Nama Mitra</th>
                  <th className="py-3 px-4">Kegiatan</th>
                  <th className="py-3 px-4 text-center">Dokumen</th>
                  <th className="py-3 px-4 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {(data?.penugasan_terbaru || []).map((item) => (
                  <tr key={item.id} className="hover:bg-blue-50/40">
                    <td className="py-3 px-4 font-bold text-slate-900">
                      <div>{item.mitra_nama}</div>
                      <div className="text-[10px] text-slate-400 font-normal">{item.mitra_kecamatan}</div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-800">{item.kegiatan_nama}</div>
                      <div className="text-[10px] text-slate-400">{item.kegiatan_tim} &bull; {item.peran}</div>
                    </td>
                    <td className="py-3 px-4 text-center font-mono font-bold text-slate-700 whitespace-nowrap">
                      {item.realisasi_dokumen} / {item.target_dokumen} Dok
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${item.status === 'SELESAI' ? 'bg-blue-50 text-blue-700 border-blue-200' : 'bg-sky-50 text-sky-700 border-sky-200'}`}>
                        {item.status === 'SELESAI' ? 'Selesai' : 'Proses'}
                      </span>
                    </td>
                  </tr>
                ))}
                {(!data?.penugasan_terbaru || data.penugasan_terbaru.length === 0) && (
                  <tr>
                    <td colSpan={4} className="py-10 text-center text-slate-400 text-xs">
                      Belum ada penugasan mitra. Klik tombol <strong>Tugaskan Mitra</strong> di atas.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="lg:col-span-5 bg-white rounded-3xl p-6 border border-slate-200/80 shadow-soft flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
              <div>
                <h2 className="text-base font-extrabold text-slate-900">Kegiatan Aktif Terbaru</h2>
                <p className="text-xs text-slate-500">Daftar kegiatan yang sedang berjalan</p>
              </div>
              <Link href="/mitra/kegiatan" className="text-xs font-bold text-blue-600 hover:underline">
                Lihat Semua &rarr;
              </Link>
            </div>

            <div className="space-y-2.5">
              {(data?.kegiatan_aktif || []).map((keg) => (
                <div key={keg.id} className="p-3.5 rounded-2xl bg-slate-50/80 border border-slate-200/70 flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <h3 className="text-xs font-bold text-slate-900 truncate">{keg.nama_kegiatan}</h3>
                    <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-500">
                      <span className="px-2 py-0.5 rounded-md bg-white border border-blue-200/70 text-blue-700 font-bold">{keg.tim_kerja}</span>
                      <span>{keg.bulan} {keg.tahun}</span>
                    </div>
                  </div>
                  <span className="px-2.5 py-1 rounded-full bg-white border border-slate-200 text-slate-700 font-bold text-[10px] whitespace-nowrap">
                    {keg.total_mitra} Mitra
                  </span>
                </div>
              ))}
              {(!data?.kegiatan_aktif || data.kegiatan_aktif.length === 0) && (
                <div className="py-10 text-center text-slate-400 text-xs">
                  Belum ada kegiatan aktif. Upload melalui <strong>Template &amp; Upload</strong>.
                </div>
              )}
            </div>
          </div>

          <div className="mt-5 pt-4 border-t border-slate-100 grid grid-cols-2 gap-2.5">
            <Link href="/mitra/evaluasi" className="py-2.5 px-3 rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200/80 text-xs font-bold text-center inline-flex items-center justify-center gap-1.5">
              <Award className="w-3.5 h-3.5" />
              <span>Penilaian Mitra</span>
            </Link>
            <Link href="/mitra/laporan" className="py-2.5 px-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold text-center inline-flex items-center justify-center gap-1.5">
              <FileSpreadsheet className="w-3.5 h-3.5" />
              <span>Laporan &amp; Honor</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
