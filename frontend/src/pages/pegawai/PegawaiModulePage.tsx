import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, Plus, X, Home, Activity } from 'lucide-react';
import { apiFetch } from '../../lib/api';

interface PegawaiRow {
  id: number;
  nip: string;
  nama: string;
  jabatan: string;
  tim_kerja: string;
  status_aktif: boolean;
  total_aktivitas: number;
}

interface AktivitasRow {
  id: number;
  pegawai_nama: string;
  tim_kerja: string;
  judul: string;
  deskripsi: string;
  tanggal_mulai: string;
  tanggal_selesai: string;
  status: string;
}

export default function PegawaiModulePage() {
  const [pegawai, setPegawai] = useState<PegawaiRow[]>([]);
  const [aktivitas, setAktivitas] = useState<AktivitasRow[]>([]);
  const [tab, setTab] = useState<'pegawai' | 'aktivitas'>('pegawai');
  const [showAddPegawai, setShowAddPegawai] = useState(false);
  const [showAddAct, setShowAddAct] = useState(false);

  const [pegForm, setPegForm] = useState({ nip: '', nama: '', jabatan: 'Statistisi', tim_kerja: 'Tim Distribusi' });
  const [actForm, setActForm] = useState({ pegawai_id: '', judul: '', deskripsi: '', status: 'PROSES' });

  const loadData = () => {
    apiFetch<{ ok: boolean; pegawai: PegawaiRow[]; aktivitas: AktivitasRow[] }>('/pegawai/overview')
      .then((res) => {
        setPegawai(res.pegawai || []);
        setAktivitas(res.aktivitas || []);
        if (res.pegawai?.length && !actForm.pegawai_id) {
          setActForm((prev) => ({ ...prev, pegawai_id: String(res.pegawai[0].id) }));
        }
      })
      .catch(() => {});
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreatePegawai = async (e: React.FormEvent) => {
    e.preventDefault();
    await apiFetch('/pegawai/create', { method: 'POST', body: JSON.stringify(pegForm) });
    setShowAddPegawai(false);
    setPegForm({ nip: '', nama: '', jabatan: 'Statistisi', tim_kerja: 'Tim Distribusi' });
    loadData();
  };

  const handleCreateAct = async (e: React.FormEvent) => {
    e.preventDefault();
    await apiFetch('/pegawai/aktivitas/create', { method: 'POST', body: JSON.stringify(actForm) });
    setShowAddAct(false);
    setActForm((prev) => ({ ...prev, judul: '', deskripsi: '' }));
    loadData();
  };

  return (
    <div className="space-y-6">
      <div className="executive-banner rounded-3xl p-5 sm:p-6 text-white shadow-xl">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-white/95 p-1.5 flex items-center justify-center shrink-0">
              <img src="/images/logo_pegawai.svg" alt="Pegawai" className="w-full h-full object-contain" />
            </div>
            <div>
              <div className="flex items-center gap-1.5 text-[11px] text-blue-200/80 mb-1">
                <Link to="/" className="hover:text-white inline-flex items-center gap-1"><Home className="w-3 h-3" /> LENTERA</Link>
                <span>/</span>
                <span className="text-white font-semibold">Kinerja Pegawai</span>
              </div>
              <h1 className="text-xl sm:text-2xl font-extrabold">Kinerja Pegawai BPS Banyuwangi</h1>
              <p className="text-xs text-blue-100/80 mt-1">Kelola data pegawai dan pantau catatan aktivitas harian per tim kerja.</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <button onClick={() => setShowAddAct(true)} className="h-10 px-4 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 text-xs font-semibold inline-flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5" /> Catat Aktivitas
            </button>
            <button onClick={() => setShowAddPegawai(true)} className="h-10 px-4 rounded-xl bg-white hover:bg-blue-50 text-blue-700 text-xs font-bold inline-flex items-center gap-1.5 shadow-md">
              <Plus className="w-3.5 h-3.5" /> Tambah Pegawai
            </button>
          </div>
        </div>
      </div>

      <div className="flex gap-2">
        <button onClick={() => setTab('pegawai')} className={`px-4 py-2 rounded-xl text-xs font-bold transition ${tab === 'pegawai' ? 'bg-blue-600 text-white shadow-sm' : 'bg-white text-slate-600 border border-slate-200'}`}>
          Data Pegawai ({pegawai.length})
        </button>
        <button onClick={() => setTab('aktivitas')} className={`px-4 py-2 rounded-xl text-xs font-bold transition ${tab === 'aktivitas' ? 'bg-blue-600 text-white shadow-sm' : 'bg-white text-slate-600 border border-slate-200'}`}>
          Aktivitas Pegawai ({aktivitas.length})
        </button>
      </div>

      <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-soft overflow-x-auto">
        {tab === 'pegawai' ? (
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-bold text-[10px]">
                <th className="py-3 px-4">NIP</th>
                <th className="py-3 px-4">Nama Pegawai</th>
                <th className="py-3 px-4">Jabatan</th>
                <th className="py-3 px-4">Tim Kerja</th>
                <th className="py-3 px-4 text-center">Aktivitas</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {pegawai.map((p) => (
                <tr key={p.id} className="hover:bg-blue-50/40">
                  <td className="py-3 px-4 font-mono text-blue-700 font-bold">{p.nip}</td>
                  <td className="py-3 px-4 font-bold text-slate-900">{p.nama}</td>
                  <td className="py-3 px-4 text-slate-600">{p.jabatan}</td>
                  <td className="py-3 px-4"><span className="px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 text-[10px] font-bold">{p.tim_kerja}</span></td>
                  <td className="py-3 px-4 text-center font-bold text-slate-800">{p.total_aktivitas} Tugas</td>
                </tr>
              ))}
              {pegawai.length === 0 && (
                <tr><td colSpan={5} className="py-10 text-center text-slate-400">Belum ada data pegawai.</td></tr>
              )}
            </tbody>
          </table>
        ) : (
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-bold text-[10px]">
                <th className="py-3 px-4">Pegawai</th>
                <th className="py-3 px-4">Judul Aktivitas</th>
                <th className="py-3 px-4">Periode</th>
                <th className="py-3 px-4 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {aktivitas.map((a) => (
                <tr key={a.id} className="hover:bg-blue-50/40">
                  <td className="py-3 px-4">
                    <div className="font-bold text-slate-900">{a.pegawai_nama}</div>
                    <div className="text-[10px] text-slate-400">{a.tim_kerja}</div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="font-semibold text-slate-800">{a.judul}</div>
                    <div className="text-[10px] text-slate-400">{a.deskripsi || '-'}</div>
                  </td>
                  <td className="py-3 px-4 font-mono text-[11px] text-slate-600">{a.tanggal_mulai} s.d {a.tanggal_selesai}</td>
                  <td className="py-3 px-4 text-center">
                    <span className="px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 text-[10px] font-bold">{a.status}</span>
                  </td>
                </tr>
              ))}
              {aktivitas.length === 0 && (
                <tr><td colSpan={4} className="py-10 text-center text-slate-400">Belum ada catatan aktivitas pegawai.</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      {showAddPegawai && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <h3 className="text-sm font-extrabold text-slate-900">Tambah Data Pegawai</h3>
              <button onClick={() => setShowAddPegawai(false)}><X className="w-5 h-5 text-slate-400" /></button>
            </div>
            <form onSubmit={handleCreatePegawai} className="space-y-3">
              <input required placeholder="NIP *" value={pegForm.nip} onChange={(e) => setPegForm({ ...pegForm, nip: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs" />
              <input required placeholder="Nama Lengkap *" value={pegForm.nama} onChange={(e) => setPegForm({ ...pegForm, nama: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs" />
              <input placeholder="Jabatan" value={pegForm.jabatan} onChange={(e) => setPegForm({ ...pegForm, jabatan: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs" />
              <select value={pegForm.tim_kerja} onChange={(e) => setPegForm({ ...pegForm, tim_kerja: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs">
                <option value="Tim Distribusi">Tim Distribusi</option>
                <option value="Tim Neraca">Tim Neraca</option>
                <option value="Tim Produksi">Tim Produksi</option>
                <option value="Tim PLS">Tim PLS</option>
                <option value="Subbagian Umum">Subbagian Umum</option>
              </select>
              <div className="pt-2 flex justify-end gap-2">
                <button type="button" onClick={() => setShowAddPegawai(false)} className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100">Batal</button>
                <button type="submit" className="px-5 py-2 rounded-xl bg-blue-600 text-white text-xs font-bold">Simpan</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showAddAct && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <h3 className="text-sm font-extrabold text-slate-900">Catat Aktivitas Pegawai</h3>
              <button onClick={() => setShowAddAct(false)}><X className="w-5 h-5 text-slate-400" /></button>
            </div>
            <form onSubmit={handleCreateAct} className="space-y-3">
              <select required value={actForm.pegawai_id} onChange={(e) => setActForm({ ...actForm, pegawai_id: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs">
                <option value="">-- Pilih Pegawai --</option>
                {pegawai.map((p) => <option key={p.id} value={p.id}>{p.nama} ({p.tim_kerja})</option>)}
              </select>
              <input required placeholder="Judul Aktivitas *" value={actForm.judul} onChange={(e) => setActForm({ ...actForm, judul: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs" />
              <textarea rows={2} placeholder="Deskripsi singkat" value={actForm.deskripsi} onChange={(e) => setActForm({ ...actForm, deskripsi: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs" />
              <div className="pt-2 flex justify-end gap-2">
                <button type="button" onClick={() => setShowAddAct(false)} className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100">Batal</button>
                <button type="submit" className="px-5 py-2 rounded-xl bg-blue-600 text-white text-xs font-bold">Simpan</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
