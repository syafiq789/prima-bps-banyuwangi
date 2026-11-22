import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Award, Users, Clock, Star, X, Home } from 'lucide-react';
import { apiFetch, syncEphemeralSnapshot } from '../../lib/api';
import { EvaluasiItem, KegiatanItem, MitraItem, PenugasanItem } from '../../types';

export default function MitraEvaluasiPage() {
  const [items, setItems] = useState<EvaluasiItem[]>([]);
  const [kpi, setKpi] = useState({ avg_score: 0, total_dinilai: 0, menunggu: 0, total_mitra: 0, total_kegiatan: 0 });
  const [belumEval, setBelumEval] = useState<PenugasanItem[]>([]);
  const [mitraOpts, setMitraOpts] = useState<MitraItem[]>([]);
  const [kegOpts, setKegOpts] = useState<KegiatanItem[]>([]);
  const [showModal, setShowModal] = useState(false);

  const [form, setForm] = useState({
    penugasan_id: '',
    mitra_id: '',
    kegiatan_id: '',
    nilai_kualitas: '90',
    nilai_ketepatan: '90',
    nilai_kerjasama: '88',
    catatan: '',
  });

  const loadData = () => {
    apiFetch<{
      ok: boolean;
      kpi: typeof kpi;
      items: EvaluasiItem[];
      penugasan_belum_eval: PenugasanItem[];
      mitra_options: MitraItem[];
      kegiatan_options: KegiatanItem[];
    }>('/mitra/evaluasi')
      .then((res) => {
        setItems(res.items || []);
        setKpi(res.kpi || { avg_score: 0, total_dinilai: 0, menunggu: 0, total_mitra: 0, total_kegiatan: 0 });
        setBelumEval(res.penugasan_belum_eval || []);
        setMitraOpts(res.mitra_options || []);
        setKegOpts(res.kegiatan_options || []);
        setForm((prev) => ({
          ...prev,
          penugasan_id: res.penugasan_belum_eval?.[0] ? String(res.penugasan_belum_eval[0].id) : '',
          mitra_id: res.mitra_options?.[0] ? String(res.mitra_options[0].id) : '',
          kegiatan_id: res.kegiatan_options?.[0] ? String(res.kegiatan_options[0].id) : '',
        }));
      })
      .catch(() => {});
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload =
      belumEval.length > 0
        ? {
            penugasan_id: Number(form.penugasan_id),
            nilai_kualitas: Number(form.nilai_kualitas),
            nilai_ketepatan: Number(form.nilai_ketepatan),
            nilai_kerjasama: Number(form.nilai_kerjasama),
            catatan: form.catatan,
          }
        : {
            mitra_id: Number(form.mitra_id),
            kegiatan_id: Number(form.kegiatan_id),
            nilai_kualitas: Number(form.nilai_kualitas),
            nilai_ketepatan: Number(form.nilai_ketepatan),
            nilai_kerjasama: Number(form.nilai_kerjasama),
            catatan: form.catatan,
          };

    await apiFetch('/mitra/evaluasi/create', { method: 'POST', body: JSON.stringify(payload) });
    setShowModal(false);
    await syncEphemeralSnapshot();
    loadData();
  };

  const canEvaluate = belumEval.length > 0 || (mitraOpts.length > 0 && kegOpts.length > 0);

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
                <Link to="/" className="hover:text-white inline-flex items-center gap-1"><Home className="w-3 h-3" /> LENTERA</Link>
                <span>/</span>
                <Link to="/mitra/dashboard" className="hover:text-white">Monitoring Mitra</Link>
                <span>/</span>
                <span className="text-white font-semibold">Penilaian Mitra</span>
              </div>
              <h1 className="text-xl sm:text-2xl font-extrabold">Penilaian Kinerja Mitra</h1>
              <p className="text-xs text-blue-100/80 mt-1">Berikan penilaian kualitas, ketepatan waktu, dan kerjasama untuk mitra statistik.</p>
            </div>
          </div>

          {canEvaluate && (
            <button onClick={() => setShowModal(true)} className="h-10 px-4 rounded-xl bg-white hover:bg-blue-50 text-blue-700 text-xs font-bold inline-flex items-center gap-1.5 shadow-md">
              <Star className="w-3.5 h-3.5" /> Beri Penilaian Mitra
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Nilai Rata-Rata</p>
            <p className="text-2xl font-extrabold text-blue-700 mt-1">{kpi.avg_score} <span className="text-xs text-slate-400">/ 100</span></p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center"><Award className="w-5 h-5" /></div>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Mitra Selesai Dinilai</p>
            <p className="text-2xl font-extrabold text-slate-900 mt-1">{kpi.total_dinilai} <span className="text-xs text-slate-400">Penilaian</span></p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center"><Users className="w-5 h-5" /></div>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Siap Dinilai</p>
            <p className="text-xl font-extrabold text-sky-600 mt-1">{kpi.total_mitra} Mitra &bull; {kpi.total_kegiatan} Kegiatan</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center"><Clock className="w-5 h-5" /></div>
        </div>
      </div>

      <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-soft overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-bold text-[10px]">
              <th className="py-3 px-4">Nama Mitra</th>
              <th className="py-3 px-4">Kegiatan &amp; Tim Kerja</th>
              <th className="py-3 px-4 text-center">Kualitas</th>
              <th className="py-3 px-4 text-center">Ketepatan</th>
              <th className="py-3 px-4 text-center">Kerjasama</th>
              <th className="py-3 px-4 text-center">Rata-Rata</th>
              <th className="py-3 px-4">Catatan</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {items.map((ev) => (
              <tr key={ev.id} className="hover:bg-blue-50/40">
                <td className="py-3.5 px-4">
                  <div className="font-bold text-slate-900">{ev.mitra_nama}</div>
                  <div className="text-[10px] text-slate-400 font-mono">{ev.mitra_id_sobat} &bull; {ev.mitra_kecamatan}</div>
                </td>
                <td className="py-3.5 px-4">
                  <div className="font-semibold text-slate-800">{ev.kegiatan_nama}</div>
                  <div className="text-[10px] text-slate-400">{ev.kegiatan_tim} &bull; Tahun {ev.kegiatan_tahun}</div>
                </td>
                <td className="py-3.5 px-4 text-center font-mono font-bold">{ev.nilai_kualitas}</td>
                <td className="py-3.5 px-4 text-center font-mono font-bold">{ev.nilai_ketepatan}</td>
                <td className="py-3.5 px-4 text-center font-mono font-bold">{ev.nilai_kerjasama}</td>
                <td className="py-3.5 px-4 text-center">
                  <span className="px-3 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200 font-mono font-black">{ev.rata_rata}</span>
                </td>
                <td className="py-3.5 px-4 text-slate-500">{ev.catatan || '-'}</td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr>
                <td colSpan={7} className="py-12 text-center text-slate-400 text-xs">
                  Belum ada penilaian masuk. Klik tombol <strong>Beri Penilaian Mitra</strong> di atas untuk mulai menilai.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <h3 className="text-sm font-extrabold text-slate-900">Beri Penilaian Mitra</h3>
              <button onClick={() => setShowModal(false)}><X className="w-5 h-5 text-slate-400" /></button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4">
              {belumEval.length > 0 ? (
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Pilih Penugasan Mitra *</label>
                  <select required value={form.penugasan_id} onChange={(e) => setForm({ ...form, penugasan_id: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs">
                    {belumEval.map((p) => (
                      <option key={p.id} value={p.id}>{p.mitra_nama} ({p.mitra_kecamatan}) — {p.kegiatan_nama}</option>
                    ))}
                  </select>
                </div>
              ) : (
                <div className="space-y-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Pilih Mitra *</label>
                    <select required value={form.mitra_id} onChange={(e) => setForm({ ...form, mitra_id: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs">
                      {mitraOpts.map((m) => <option key={m.id} value={m.id}>{m.nama} ({m.id_sobat} &bull; {m.kecamatan})</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Pilih Kegiatan *</label>
                    <select required value={form.kegiatan_id} onChange={(e) => setForm({ ...form, kegiatan_id: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs">
                      {kegOpts.map((k) => <option key={k.id} value={k.id}>{k.nama_kegiatan} ({k.tim_kerja})</option>)}
                    </select>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-[11px] font-bold text-slate-700 mb-1">Kualitas</label>
                  <input type="number" min={0} max={100} value={form.nilai_kualitas} onChange={(e) => setForm({ ...form, nilai_kualitas: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-mono font-bold" />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-slate-700 mb-1">Ketepatan</label>
                  <input type="number" min={0} max={100} value={form.nilai_ketepatan} onChange={(e) => setForm({ ...form, nilai_ketepatan: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-mono font-bold" />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-slate-700 mb-1">Kerjasama</label>
                  <input type="number" min={0} max={100} value={form.nilai_kerjasama} onChange={(e) => setForm({ ...form, nilai_kerjasama: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-mono font-bold" />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Catatan Pengawas</label>
                <textarea rows={2} value={form.catatan} onChange={(e) => setForm({ ...form, catatan: e.target.value })} placeholder="Catatan hasil kinerja..." className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs" />
              </div>

              <div className="flex justify-end gap-2">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100">Batal</button>
                <button type="submit" className="px-5 py-2 rounded-xl bg-blue-600 text-white text-xs font-bold">Simpan Nilai</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
