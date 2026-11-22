import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Calendar, Plus, FileUp, Search, X, Home } from 'lucide-react';
import { apiFetch, formatRupiah, syncEphemeralSnapshot } from '../../lib/api';
import { KegiatanItem } from '../../types';

export default function MitraKegiatanPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const timFilter = searchParams.get('tim') || 'Semua';

  const [items, setItems] = useState<KegiatanItem[]>([]);
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({
    nama_kegiatan: '',
    tim_kerja: 'Tim Distribusi',
    tahun: '2025',
    bulan: 'Januari',
    tanggal_mulai: '2025-01-05',
    tanggal_selesai: '2025-01-31',
  });

  const loadData = () => {
    const params = new URLSearchParams();
    if (timFilter && timFilter !== 'Semua') params.set('tim', timFilter);
    if (search) params.set('search', search);
    apiFetch<{ ok: boolean; items: KegiatanItem[]; counts: Record<string, number> }>(`/mitra/kegiatan?${params.toString()}`)
      .then((res) => {
        setItems(res.items || []);
        setCounts(res.counts || {});
      })
      .catch(() => {});
  };

  useEffect(() => {
    loadData();
  }, [timFilter]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await apiFetch('/mitra/kegiatan/create', { method: 'POST', body: JSON.stringify(form) });
    setShowModal(false);
    setForm({ nama_kegiatan: '', tim_kerja: 'Tim Distribusi', tahun: '2025', bulan: 'Januari', tanggal_mulai: '2025-01-05', tanggal_selesai: '2025-01-31' });
    await syncEphemeralSnapshot();
    loadData();
  };

  const tabs = ['Semua', 'Tim Distribusi', 'Tim Neraca', 'Tim Produksi', 'Tim PLS'];

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
                <span className="text-white font-semibold">Daftar Kegiatan</span>
              </div>
              <h1 className="text-xl sm:text-2xl font-extrabold">Daftar Kegiatan ({counts['Semua'] || 0})</h1>
              <p className="text-xs text-blue-100/80 mt-1">Lihat dan kelola seluruh kegiatan per tim kerja beserta jadwal, mitra, dan honor.</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Link to="/mitra/template?tab=kegiatan" className="h-10 px-4 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 text-xs font-semibold inline-flex items-center gap-1.5">
              <FileUp className="w-3.5 h-3.5" /> Template &amp; Upload
            </Link>
            <button onClick={() => setShowModal(true)} className="h-10 px-4 rounded-xl bg-white hover:bg-blue-50 text-blue-700 text-xs font-bold inline-flex items-center gap-1.5 shadow-md">
              <Plus className="w-3.5 h-3.5" /> Tambah Kegiatan
            </button>
          </div>
        </div>
      </div>

      {/* Tabs + Search */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {tabs.map((t) => (
            <button
              key={t}
              onClick={() => setSearchParams(t === 'Semua' ? {} : { tim: t })}
              className={`h-9 px-4 rounded-full text-xs font-bold whitespace-nowrap border transition ${timFilter === t ? 'bg-slate-900 text-white border-slate-900' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'}`}
            >
              {t === 'Semua' ? 'Semua Tim' : t} ({counts[t] || 0})
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && loadData()}
              placeholder="Cari nama kegiatan..."
              className="pl-8 pr-3 py-2 text-xs rounded-xl border border-slate-200 bg-white outline-none focus:border-blue-500"
            />
          </div>
          <button onClick={loadData} className="px-4 py-2 rounded-xl bg-blue-600 text-white text-xs font-bold">Cari</button>
        </div>
      </div>

      {/* Grid Kartu Kegiatan (Tanpa Kode Kegiatan & Tanpa Persen) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {items.map((k) => (
          <div key={k.id} className="bg-white rounded-3xl p-5 border border-slate-200/80 shadow-soft hover:shadow-md transition flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between gap-2 mb-3">
                <div className="flex items-center gap-1.5">
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200/70">{k.tim_kerja}</span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 text-slate-600">{k.bulan} {k.tahun}</span>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-600 border border-blue-200">{k.status}</span>
              </div>

              <h3 className="text-base font-bold text-slate-900 mb-1.5">{k.nama_kegiatan}</h3>
              <p className="text-xs text-slate-500 mb-4 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                <span>{k.tanggal_mulai} s.d. {k.tanggal_selesai}</span>
              </p>

              <div className="grid grid-cols-3 gap-2 my-4 text-center">
                <div className="p-2.5 rounded-2xl bg-blue-50/60 border border-blue-100">
                  <div className="text-[10px] text-blue-600 font-semibold uppercase">Mitra</div>
                  <div className="text-sm font-bold text-slate-800 mt-0.5">{k.total_mitra} Org</div>
                </div>
                <div className="p-2.5 rounded-2xl bg-blue-50/60 border border-blue-100">
                  <div className="text-[10px] text-blue-600 font-semibold uppercase">Dokumen</div>
                  <div className="text-xs font-bold text-slate-800 mt-1">{k.total_dokumen_realisasi}/{k.total_dokumen_target}</div>
                </div>
                <div className="p-2.5 rounded-2xl bg-blue-50/60 border border-blue-100">
                  <div className="text-[10px] text-blue-600 font-semibold uppercase">Honor</div>
                  <div className="text-[11px] font-bold font-mono text-blue-700 mt-1 truncate">{formatRupiah(k.total_honor_mitra)}</div>
                </div>
              </div>
            </div>

            <Link
              to="/mitra/penugasan"
              className="mt-2 w-full py-2.5 rounded-xl bg-blue-50 hover:bg-blue-600 text-blue-700 hover:text-white font-bold text-xs text-center transition border border-blue-200/80"
            >
              Atur Penugasan Mitra
            </Link>
          </div>
        ))}
        {items.length === 0 && (
          <div className="col-span-full py-12 text-center bg-white rounded-3xl border border-dashed border-slate-200 text-slate-400 text-xs">
            Belum ada kegiatan. Upload CSV melalui <strong>Template &amp; Upload</strong> atau klik <strong>Tambah Kegiatan</strong>.
          </div>
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <h3 className="text-sm font-extrabold text-slate-900">Tambah Kegiatan Baru</h3>
              <button onClick={() => setShowModal(false)}><X className="w-5 h-5 text-slate-400" /></button>
            </div>
            <form onSubmit={handleCreate} className="space-y-3">
              <input required placeholder="Nama Kegiatan *" value={form.nama_kegiatan} onChange={(e) => setForm({ ...form, nama_kegiatan: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs" />
              <select value={form.tim_kerja} onChange={(e) => setForm({ ...form, tim_kerja: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs">
                <option value="Tim Distribusi">Tim Distribusi</option>
                <option value="Tim Neraca">Tim Neraca</option>
                <option value="Tim Produksi">Tim Produksi</option>
                <option value="Tim PLS">Tim PLS</option>
              </select>
              <div className="grid grid-cols-2 gap-3">
                <input type="number" value={form.tahun} onChange={(e) => setForm({ ...form, tahun: e.target.value })} className="px-3 py-2 rounded-xl border border-slate-200 text-xs" />
                <select value={form.bulan} onChange={(e) => setForm({ ...form, bulan: e.target.value })} className="px-3 py-2 rounded-xl border border-slate-200 text-xs">
                  {['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember'].map((b) => <option key={b} value={b}>{b}</option>)}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <input type="date" value={form.tanggal_mulai} onChange={(e) => setForm({ ...form, tanggal_mulai: e.target.value })} className="px-3 py-2 rounded-xl border border-slate-200 text-xs" />
                <input type="date" value={form.tanggal_selesai} onChange={(e) => setForm({ ...form, tanggal_selesai: e.target.value })} className="px-3 py-2 rounded-xl border border-slate-200 text-xs" />
              </div>
              <div className="pt-3 flex justify-end gap-2">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100">Batal</button>
                <button type="submit" className="px-5 py-2 rounded-xl bg-blue-600 text-white text-xs font-bold">Simpan Kegiatan</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
