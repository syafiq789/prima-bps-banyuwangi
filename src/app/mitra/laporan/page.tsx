'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Printer, Users, Wallet, Calendar, Search, FileSpreadsheet, Home, MapPin } from 'lucide-react';
import { apiFetch, formatRupiah } from '@/lib/api';
import { RekapKecamatanRow, RekapMitraRow, RekapTimRow } from '@/types';

export default function MitraLaporanPage() {
  const [kpi, setKpi] = useState({ total_mitra: 0, total_kegiatan: 0, total_penugasan: 0, total_honor_all: 0 });
  const [rekapKec, setRekapKec] = useState<RekapKecamatanRow[]>([]);
  const [rekapTim, setRekapTim] = useState<RekapTimRow[]>([]);
  const [rekapMitra, setRekapMitra] = useState<RekapMitraRow[]>([]);
  const [search, setSearch] = useState('');
  const [predFilter, setPredFilter] = useState('');

  useEffect(() => {
    apiFetch<{
      ok: boolean;
      kpi: typeof kpi;
      rekap_kecamatan: RekapKecamatanRow[];
      rekap_tim: RekapTimRow[];
      rekap_mitra: RekapMitraRow[];
    }>('/mitra/rekapitulasi')
      .then((res) => {
        setKpi(res.kpi || { total_mitra: 0, total_kegiatan: 0, total_penugasan: 0, total_honor_all: 0 });
        setRekapKec(res.rekap_kecamatan || []);
        setRekapTim(res.rekap_tim || []);
        setRekapMitra(res.rekap_mitra || []);
      })
      .catch(() => {});
  }, []);

  const q = search.toLowerCase().trim();
  const filteredMitra = rekapMitra.filter((r) => {
    const hay = `${r.mitra.nama} ${r.mitra.id_sobat} ${r.mitra.kecamatan} ${r.mitra.desa} ${r.tim_list.join(' ')} ${r.kegiatan_list.join(' ')}`.toLowerCase();
    const matchQ = !q || hay.includes(q);
    const matchPred = !predFilter || r.predikat.toLowerCase().includes(predFilter);
    return matchQ && matchPred;
  });

  return (
    <div className="space-y-6">
      <div className="executive-banner rounded-3xl p-5 sm:p-6 text-white shadow-xl">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-white/95 p-1.5 flex items-center justify-center shrink-0">
              <img src="/images/logo_mitra.svg" alt="Mitra" className="w-full h-full object-contain" />
            </div>
            <div>
              <div className="flex items-center gap-1.5 text-[11px] text-blue-200/80 mb-1">
                <Link href="/" className="hover:text-white inline-flex items-center gap-1"><Home className="w-3 h-3" /> LENTERA</Link>
                <span>/</span>
                <Link href="/mitra/dashboard" className="hover:text-white">Monitoring Mitra</Link>
                <span>/</span>
                <span className="text-white font-semibold">Laporan &amp; Honor</span>
              </div>
              <h1 className="text-xl sm:text-2xl font-extrabold">Laporan &amp; Honor Mitra</h1>
              <p className="text-xs text-blue-100/80 mt-1">Rekapitulasi otomatis seluruh data mitra, kegiatan, tim kerja, nilai evaluasi, dan honorarium.</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button onClick={() => window.print()} className="h-10 px-4 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 text-xs font-semibold inline-flex items-center gap-1.5">
              <Printer className="w-3.5 h-3.5" /> Cetak Laporan
            </button>
            <Link href="/mitra/database" className="h-10 px-4 rounded-xl bg-white hover:bg-blue-50 text-blue-700 text-xs font-bold inline-flex items-center gap-1.5 shadow-md">
              <Users className="w-3.5 h-3.5" /> Data Mitra
            </Link>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Total Mitra Terdaftar</p>
            <p className="text-2xl font-black text-slate-900 mt-1">{kpi.total_mitra} <span className="text-xs font-semibold text-slate-400">Orang</span></p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center"><Users className="w-5 h-5" /></div>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Total Honor Dialokasikan</p>
            <p className="text-2xl font-black font-mono text-blue-700 mt-1">{formatRupiah(kpi.total_honor_all)}</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center"><Wallet className="w-5 h-5" /></div>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Total Kegiatan &amp; Penugasan</p>
            <p className="text-2xl font-black text-slate-900 mt-1">{kpi.total_kegiatan} <span className="text-xs font-semibold text-slate-400">Kegiatan &bull; {kpi.total_penugasan} Tugas</span></p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center"><Calendar className="w-5 h-5" /></div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {rekapTim.map((t) => (
          <div key={t.nama} className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft">
            <h3 className="text-sm font-extrabold text-slate-900">{t.nama}</h3>
            <p className="text-[11px] text-slate-400 mt-0.5">{t.desc}</p>
            <div className="space-y-1.5 pt-3 mt-3 border-t border-slate-100 text-xs">
              <div className="flex justify-between"><span className="text-slate-500">Kegiatan</span><span className="font-bold text-slate-800">{t.total_kegiatan} Kegiatan</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Penugasan</span><span className="font-bold text-slate-800">{t.total_tugas} Tugas</span></div>
              <div className="flex justify-between pt-1"><span className="text-slate-500">Total Honor</span><span className="font-mono font-extrabold text-blue-700">{formatRupiah(t.total_honor)}</span></div>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-soft">
        <div className="flex items-center gap-2 mb-4">
          <MapPin className="w-4 h-4 text-blue-600" />
          <h2 className="text-base font-extrabold text-slate-900">Sebaran Mitra &amp; Beban Kerja di 25 Kecamatan</h2>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          {rekapKec.map((k, idx) => (
            <div key={k.kecamatan} className="p-3 rounded-2xl border border-slate-200/80 bg-slate-50/60 text-xs">
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-bold text-slate-800 truncate">{k.kecamatan}</span>
                <span className="text-[10px] font-mono text-slate-400">{idx + 1}</span>
              </div>
              <div className="text-[11px] text-slate-600 flex justify-between"><span>Mitra</span><strong>{k.total_mitra} Org</strong></div>
              <div className="text-[11px] text-slate-600 flex justify-between"><span>Tugas</span><strong>{k.total_tugas}</strong></div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-soft">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 pb-4 border-b border-slate-100 mb-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
              <FileSpreadsheet className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-extrabold text-slate-900">Laporan Rinci Kinerja, Kegiatan &amp; Honor per Mitra ({filteredMitra.length})</h2>
              <p className="text-xs text-slate-500">Rekap lengkap identitas, wilayah domisili, tim kerja, progres tugas, nilai evaluasi, dan honor.</p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-2">
            <select value={predFilter} onChange={(e) => setPredFilter(e.target.value)} className="px-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50/70">
              <option value="">Semua Kategori Kinerja</option>
              <option value="sangat baik">Sangat Baik (A)</option>
              <option value="baik (b)">Baik (B)</option>
              <option value="cukup">Cukup (C)</option>
              <option value="kurang">Kurang (D)</option>
              <option value="belum dinilai">Belum Dinilai</option>
            </select>
            <div className="relative w-full sm:w-60">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Cari nama, ID Sobat, kecamatan..."
                className="w-full pl-8 pr-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50/70 focus:bg-white focus:border-blue-500 outline-none"
              />
            </div>
          </div>
        </div>

        <div className="overflow-x-auto max-h-[520px] overflow-y-auto rounded-2xl border border-slate-200/80">
          <table className="w-full text-left text-xs">
            <thead className="sticky top-0 bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-bold text-[10px]">
              <tr>
                <th className="py-3 px-3 text-center">No</th>
                <th className="py-3 px-4">Identitas &amp; Kontak</th>
                <th className="py-3 px-4">Wilayah Domisili</th>
                <th className="py-3 px-4">Tim Kerja &amp; Kegiatan</th>
                <th className="py-3 px-4 text-center">Progres Tugas</th>
                <th className="py-3 px-4 text-center">Nilai Evaluasi</th>
                <th className="py-3 px-4 text-center">Kategori Kinerja</th>
                <th className="py-3 px-4 text-right">Total Honor</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredMitra.map((r, i) => (
                <tr key={r.mitra.id} className="hover:bg-blue-50/40">
                  <td className="py-3 px-3 text-center font-mono text-slate-400">{i + 1}</td>
                  <td className="py-3 px-4">
                    <div className="font-bold text-slate-900">{r.mitra.nama}</div>
                    <div className="text-[10px] text-slate-500 font-mono">ID Sobat: {r.mitra.id_sobat}</div>
                    <div className="text-[10px] text-slate-400">{r.mitra.nomor_hp || '-'}</div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="font-semibold text-slate-800">{r.mitra.kecamatan}</div>
                    <div className="text-[10px] text-slate-400">Desa {r.mitra.desa || '-'}</div>
                  </td>
                  <td className="py-3 px-4">
                    {r.tim_list.length > 0 ? (
                      <div>
                        <div className="flex flex-wrap gap-1 mb-1">
                          {r.tim_list.map((t) => (
                            <span key={t} className="px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 border border-blue-200/70 text-[10px] font-bold">{t}</span>
                          ))}
                        </div>
                        <div className="text-[10px] text-slate-500">{r.kegiatan_list.slice(0, 2).join(', ')}</div>
                      </div>
                    ) : (
                      <span className="text-[11px] text-slate-400 italic">Belum ada kegiatan ditugaskan</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className="px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 font-bold text-[10px]">{r.total_tugas} Tugas</span>
                    <div className="text-[10px] text-slate-400 mt-0.5">{r.tugas_selesai} Selesai &bull; {r.tugas_berjalan} Berjalan</div>
                  </td>
                  <td className="py-3 px-4 text-center font-mono font-bold text-slate-800">
                    {r.avg_score > 0 ? `${r.avg_score} / 100` : '-'}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">{r.predikat}</span>
                  </td>
                  <td className="py-3 px-4 text-right font-mono font-extrabold text-blue-700 whitespace-nowrap">
                    {formatRupiah(r.total_honor)}
                  </td>
                </tr>
              ))}
              {filteredMitra.length === 0 && (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400 text-xs">
                    <strong>Menunggu Laporan dari Fitur Monitoring Mitra</strong> — Data akan tampil otomatis setelah masuk dari fitur Monitoring Mitra lainnya.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
