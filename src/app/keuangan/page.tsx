'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Plus, CheckCircle2, X, Home } from 'lucide-react';
import { apiFetch, formatRupiah } from '@/lib/api';

interface PengajuanRow {
  id: number;
  nomor: string;
  uraian: string;
  jumlah: number;
  status: string;
  tanggal: string;
  cair: number;
}

export default function KeuanganPage() {
  const [kpi, setKpi] = useState({ total_pagu: 0, total_diajukan: 0, total_cair: 0, total_pengajuan: 0 });
  const [pengajuan, setPengajuan] = useState<PengajuanRow[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ uraian: '', jumlah: '5000000' });

  const loadData = () => {
    apiFetch<{ ok: boolean; kpi: typeof kpi; pengajuan: PengajuanRow[] }>('/keuangan/overview')
      .then((res) => {
        setKpi(res.kpi || { total_pagu: 0, total_diajukan: 0, total_cair: 0, total_pengajuan: 0 });
        setPengajuan(res.pengajuan || []);
      })
      .catch(() => {});
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await apiFetch('/keuangan/pengajuan/create', {
      method: 'POST',
      body: JSON.stringify({ uraian: form.uraian, jumlah: Number(form.jumlah) }),
    });
    setShowModal(false);
    setForm({ uraian: '', jumlah: '5000000' });
    loadData();
  };

  const handleApprove = async (id: number) => {
    await apiFetch(`/keuangan/pengajuan/${id}/approve`, { method: 'POST' });
    loadData();
  };

  const handleCairkan = async (id: number) => {
    await apiFetch(`/keuangan/pengajuan/${id}/cairkan`, { method: 'POST' });
    loadData();
  };

  return (
    <div className="space-y-6">
      <div className="executive-banner rounded-3xl p-5 sm:p-6 text-white shadow-xl">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-white/95 p-1.5 flex items-center justify-center shrink-0">
              <img src="/images/logo_keuangan.svg" alt="Keuangan" className="w-full h-full object-contain" />
            </div>
            <div>
              <div className="flex items-center gap-1.5 text-[11px] text-blue-200/80 mb-1">
                <Link href="/" className="hover:text-white inline-flex items-center gap-1"><Home className="w-3 h-3" /> LENTERA</Link>
                <span>/</span>
                <span className="text-white font-semibold">Tracking Keuangan</span>
              </div>
              <h1 className="text-xl sm:text-2xl font-extrabold">Tracking Keuangan</h1>
              <p className="text-xs text-blue-100/80 mt-1">Alur Pengajuan Anggaran &rarr; Persetujuan &rarr; Pencairan Realisasi secara transparan.</p>
            </div>
          </div>

          <button onClick={() => setShowModal(true)} className="h-10 px-4 rounded-xl bg-white hover:bg-blue-50 text-blue-700 text-xs font-bold inline-flex items-center gap-1.5 shadow-md">
            <Plus className="w-3.5 h-3.5" /> Buat Pengajuan Anggaran
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft">
          <p className="text-xs text-slate-500 font-medium">Total Pengajuan</p>
          <p className="text-2xl font-black font-mono text-slate-900 mt-1">{formatRupiah(kpi.total_diajukan)}</p>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft">
          <p className="text-xs text-slate-500 font-medium">Total Realisasi Cair</p>
          <p className="text-2xl font-black font-mono text-blue-700 mt-1">{formatRupiah(kpi.total_cair)}</p>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft">
          <p className="text-xs text-slate-500 font-medium">Jumlah Dokumen Pengajuan</p>
          <p className="text-2xl font-black text-slate-900 mt-1">{kpi.total_pengajuan} <span className="text-xs text-slate-400">Berkas</span></p>
        </div>
      </div>

      <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-soft overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-bold text-[10px]">
              <th className="py-3 px-4">Nomor</th>
              <th className="py-3 px-4">Uraian Pengajuan</th>
              <th className="py-3 px-4 text-right">Jumlah</th>
              <th className="py-3 px-4 text-center">Status</th>
              <th className="py-3 px-4 text-right">Tindak Lanjut</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {pengajuan.map((p) => (
              <tr key={p.id} className="hover:bg-blue-50/40">
                <td className="py-3.5 px-4 font-mono font-bold text-blue-700 whitespace-nowrap">{p.nomor}</td>
                <td className="py-3.5 px-4 font-semibold text-slate-800">{p.uraian}</td>
                <td className="py-3.5 px-4 text-right font-mono font-bold text-slate-900 whitespace-nowrap">{formatRupiah(p.jumlah)}</td>
                <td className="py-3.5 px-4 text-center">
                  <span className="px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 text-[10px] font-bold">{p.status}</span>
                </td>
                <td className="py-3.5 px-4 text-right whitespace-nowrap space-x-1.5">
                  {p.status === 'DIAJUKAN' && (
                    <button onClick={() => handleApprove(p.id)} className="px-3 py-1 rounded-lg bg-blue-600 text-white text-[11px] font-bold hover:bg-blue-700">Setujui</button>
                  )}
                  {p.status === 'DISETUJUI' && (
                    <button onClick={() => handleCairkan(p.id)} className="px-3 py-1 rounded-lg bg-sky-600 text-white text-[11px] font-bold hover:bg-sky-700">Cairkan</button>
                  )}
                  {p.status === 'CAIR' && (
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-blue-700"><CheckCircle2 className="w-3.5 h-3.5" /> Selesai</span>
                  )}
                </td>
              </tr>
            ))}
            {pengajuan.length === 0 && (
              <tr><td colSpan={5} className="py-10 text-center text-slate-400">Belum ada pengajuan anggaran.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <h3 className="text-sm font-extrabold text-slate-900">Pengajuan Anggaran Baru</h3>
              <button onClick={() => setShowModal(false)}><X className="w-5 h-5 text-slate-400" /></button>
            </div>
            <form onSubmit={handleCreate} className="space-y-3">
              <input required placeholder="Uraian Kebutuhan Anggaran *" value={form.uraian} onChange={(e) => setForm({ ...form, uraian: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs" />
              <input required type="number" min={1} placeholder="Jumlah (Rp)" value={form.jumlah} onChange={(e) => setForm({ ...form, jumlah: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-mono font-bold" />
              <div className="pt-2 flex justify-end gap-2">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100">Batal</button>
                <button type="submit" className="px-5 py-2 rounded-xl bg-blue-600 text-white text-xs font-bold">Ajukan</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
