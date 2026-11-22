'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { ClipboardList, Clock, CheckCircle2, Wallet, Plus, X, Home, BarChart3 } from 'lucide-react';
import { apiFetch, formatRupiah, syncEphemeralSnapshot } from '@/lib/api';
import { KegiatanItem, MitraItem, PenugasanItem } from '@/types';

export default function MitraPenugasanPage() {
  const [items, setItems] = useState<PenugasanItem[]>([]);
  const [kpi, setKpi] = useState({ total: 0, proses: 0, selesai: 0, total_honor: 0 });
  const [mitraOpts, setMitraOpts] = useState<MitraItem[]>([]);
  const [kegOpts, setKegOpts] = useState<KegiatanItem[]>([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');

  const [showCreate, setShowCreate] = useState(false);
  const [createForm, setCreateForm] = useState({
    mitra_id: '',
    kegiatan_id: '',
    peran: 'PPL',
    target_dokumen: '25',
    honor_total: '3200000',
  });

  const [editProg, setEditProg] = useState<PenugasanItem | null>(null);
  const [realisasiInput, setRealisasiInput] = useState('0');

  const loadData = () => {
    apiFetch<{
      ok: boolean;
      kpi: typeof kpi;
      items: PenugasanItem[];
      mitra_options: MitraItem[];
      kegiatan_options: KegiatanItem[];
    }>('/mitra/penugasan')
      .then((res) => {
        setItems(res.items || []);
        setKpi(res.kpi || { total: 0, proses: 0, selesai: 0, total_honor: 0 });
        setMitraOpts(res.mitra_options || []);
        setKegOpts(res.kegiatan_options || []);
        if (res.mitra_options?.length && !createForm.mitra_id) {
          setCreateForm((prev) => ({
            ...prev,
            mitra_id: String(res.mitra_options[0].id),
            kegiatan_id: res.kegiatan_options?.[0] ? String(res.kegiatan_options[0].id) : '',
          }));
        }
      })
      .catch(() => {});
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await apiFetch('/mitra/penugasan/create', { method: 'POST', body: JSON.stringify(createForm) });
    setShowCreate(false);
    await syncEphemeralSnapshot();
    loadData();
  };

  const handleUpdateProgress = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editProg) return;
    await apiFetch(`/mitra/penugasan/${editProg.id}/progress`, {
      method: 'POST',
      body: JSON.stringify({ realisasi_dokumen: Number(realisasiInput) }),
    });
    setEditProg(null);
    await syncEphemeralSnapshot();
    loadData();
  };

  const q = search.toLowerCase().trim();
  const filtered = items.filter((p) => {
    const matchStatus = !statusFilter || p.status === statusFilter;
    const matchSearch = !q || `${p.mitra_nama} ${p.kegiatan_nama} ${p.kegiatan_tim} ${p.peran}`.toLowerCase().includes(q);
    return matchStatus && matchSearch;
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
                <span className="text-white font-semibold">Penugasan Mitra</span>
              </div>
              <h1 className="text-xl sm:text-2xl font-extrabold">Penugasan Mitra</h1>
              <p className="text-xs text-blue-100/80 mt-1">
                Atur pembagian tugas mitra ke kegiatan, pantau dokumen lapangan, dan kelola honorarium.
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Link href="/mitra/laporan" className="h-10 px-4 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 text-xs font-semibold inline-flex items-center gap-1.5">
              <BarChart3 className="w-3.5 h-3.5" /> Laporan &amp; Honor
            </Link>
            <button onClick={() => setShowCreate(true)} className="h-10 px-4 rounded-xl bg-white hover:bg-blue-50 text-blue-700 text-xs font-bold inline-flex items-center gap-1.5 shadow-md">
              <Plus className="w-3.5 h-3.5" /> Tugaskan Mitra Baru
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft flex items-center justify-between">
          <div>
            <p className="text-[11px] font-semibold text-slate-500">Total Penugasan</p>
            <p className="text-2xl font-extrabold text-slate-900 mt-1">{kpi.total} <span className="text-xs font-semibold text-slate-400">Tugas</span></p>
          </div>
          <div className="w-11 h-11 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center"><ClipboardList className="w-5 h-5" /></div>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft flex items-center justify-between">
          <div>
            <p className="text-[11px] font-semibold text-slate-500">Sedang Berjalan</p>
            <p className="text-2xl font-extrabold text-sky-600 mt-1">{kpi.proses} <span className="text-xs font-semibold text-slate-400">Aktif</span></p>
          </div>
          <div className="w-11 h-11 rounded-2xl bg-sky-50 text-sky-600 flex items-center justify-center"><Clock className="w-5 h-5" /></div>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft flex items-center justify-between">
          <div>
            <p className="text-[11px] font-semibold text-slate-500">Tugas Selesai</p>
            <p className="text-2xl font-extrabold text-blue-700 mt-1">{kpi.selesai} <span className="text-xs font-semibold text-slate-400">Selesai</span></p>
          </div>
          <div className="w-11 h-11 rounded-2xl bg-blue-50 text-blue-700 flex items-center justify-center"><CheckCircle2 className="w-5 h-5" /></div>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft flex items-center justify-between">
          <div>
            <p className="text-[11px] font-semibold text-slate-500">Total Honorarium</p>
            <p className="text-xl font-extrabold font-mono text-blue-700 mt-1">{formatRupiah(kpi.total_honor)}</p>
          </div>
          <div className="w-11 h-11 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center"><Wallet className="w-5 h-5" /></div>
        </div>
      </div>

      <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-soft space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
          <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl self-start">
            {[
              { val: '', label: 'Semua' },
              { val: 'PROSES', label: 'Sedang Berjalan' },
              { val: 'SELESAI', label: 'Selesai' },
            ].map((s) => (
              <button
                key={s.label}
                onClick={() => setStatusFilter(s.val)}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition ${statusFilter === s.val ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'}`}
              >
                {s.label}
              </button>
            ))}
          </div>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Cari nama mitra, kegiatan, atau tim..."
            className="w-full sm:w-64 px-3.5 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50/70 focus:bg-white focus:border-blue-500 outline-none"
          />
        </div>

        <div className="overflow-x-auto rounded-2xl border border-slate-200/80">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-bold text-[10px]">
                <th className="py-3 px-3 text-center">No</th>
                <th className="py-3 px-4">Nama Mitra</th>
                <th className="py-3 px-4">Kegiatan &amp; Tim Kerja</th>
                <th className="py-3 px-4 text-center">Peran</th>
                <th className="py-3 px-4">Dokumen</th>
                <th className="py-3 px-4 text-right">Honor</th>
                <th className="py-3 px-4 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((p, i) => (
                <tr key={p.id} className="hover:bg-blue-50/40">
                  <td className="py-3.5 px-3 text-center font-mono text-slate-400">{i + 1}</td>
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-slate-900">{p.mitra_nama}</div>
                    <div className="text-[10px] text-slate-400 font-mono">{p.mitra_id_sobat} &bull; {p.mitra_kecamatan}</div>
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-slate-800">{p.kegiatan_nama}</div>
                    <div className="text-[10px] text-blue-700 font-semibold">{p.kegiatan_tim} &bull; {p.kegiatan_bulan} {p.kegiatan_tahun}</div>
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className="px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 font-bold text-[10px] border border-blue-200">{p.peran}</span>
                  </td>
                  <td className="py-3.5 px-4">
                    <button onClick={() => { setEditProg(p); setRealisasiInput(String(p.realisasi_dokumen)); }} className="text-left group">
                      <div className="text-[11px] font-bold text-slate-800 group-hover:text-blue-600">
                        {p.realisasi_dokumen} / {p.target_dokumen} Dok <span className="text-blue-600 text-[10px] ml-1">(Update)</span>
                      </div>
                    </button>
                  </td>
                  <td className="py-3.5 px-4 text-right font-mono font-extrabold text-blue-700 whitespace-nowrap">
                    {formatRupiah(p.honor_total)}
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${p.status === 'SELESAI' ? 'bg-blue-50 text-blue-700 border-blue-200' : 'bg-sky-50 text-sky-700 border-sky-200'}`}>
                      {p.status === 'SELESAI' ? 'Selesai' : 'Proses'}
                    </span>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400 text-xs">
                    Belum ada penugasan mitra. Tersedia <strong>{mitraOpts.length} Mitra</strong> dan <strong>{kegOpts.length} Kegiatan</strong> siap ditugaskan.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showCreate && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <h3 className="text-sm font-extrabold text-slate-900">Tugaskan Mitra Baru</h3>
              <button onClick={() => setShowCreate(false)}><X className="w-5 h-5 text-slate-400" /></button>
            </div>
            <form onSubmit={handleCreate} className="space-y-3.5">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Pilih Mitra *</label>
                <select required value={createForm.mitra_id} onChange={(e) => setCreateForm({ ...createForm, mitra_id: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs">
                  <option value="">-- Pilih Mitra --</option>
                  {mitraOpts.map((m) => (
                    <option key={m.id} value={m.id}>{m.nama} ({m.id_sobat} &bull; {m.kecamatan})</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Pilih Kegiatan *</label>
                <select required value={createForm.kegiatan_id} onChange={(e) => setCreateForm({ ...createForm, kegiatan_id: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs">
                  <option value="">-- Pilih Kegiatan --</option>
                  {kegOpts.map((k) => (
                    <option key={k.id} value={k.id}>{k.nama_kegiatan} — {k.tim_kerja} ({k.bulan} {k.tahun})</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Peran</label>
                  <select value={createForm.peran} onChange={(e) => setCreateForm({ ...createForm, peran: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs">
                    <option value="PPL">Pencacah (PPL)</option>
                    <option value="PML">Pengawas (PML)</option>
                    <option value="PENGOLAH">Pengolah Data</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Target Dokumen</label>
                  <input type="number" min={1} value={createForm.target_dokumen} onChange={(e) => setCreateForm({ ...createForm, target_dokumen: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-bold" />
                </div>
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Total Honorarium (Rp)</label>
                <input type="number" min={0} value={createForm.honor_total} onChange={(e) => setCreateForm({ ...createForm, honor_total: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-mono font-bold" />
              </div>
              <div className="pt-3 flex justify-end gap-2">
                <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100">Batal</button>
                <button type="submit" className="px-5 py-2 rounded-xl bg-blue-600 text-white text-xs font-bold">Simpan Penugasan</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {editProg && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-sm w-full p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <h3 className="text-sm font-extrabold text-slate-900">Perbarui Dokumen Selesai</h3>
              <button onClick={() => setEditProg(null)}><X className="w-5 h-5 text-slate-400" /></button>
            </div>
            <form onSubmit={handleUpdateProgress} className="space-y-4">
              <div className="p-3 rounded-2xl bg-blue-50 border border-blue-100">
                <p className="text-[10px] font-bold text-blue-600 uppercase">Nama Mitra</p>
                <p className="text-sm font-extrabold text-slate-900">{editProg.mitra_nama}</p>
              </div>
              <div className="flex items-center gap-2">
                <input type="number" min={0} value={realisasiInput} onChange={(e) => setRealisasiInput(e.target.value)} className="flex-1 px-3 py-2 rounded-xl border border-slate-200 text-sm font-bold" />
                <span className="text-xs text-slate-500 font-semibold">/ {editProg.target_dokumen} Dok</span>
              </div>
              <div className="flex justify-end gap-2">
                <button type="button" onClick={() => setEditProg(null)} className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100">Batal</button>
                <button type="submit" className="px-4 py-2 rounded-xl bg-blue-600 text-white text-xs font-bold">Simpan</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
