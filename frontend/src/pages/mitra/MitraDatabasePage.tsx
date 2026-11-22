import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, Power, Trash2, MapPin, Phone, FileUp, X, Home } from 'lucide-react';
import { apiFetch, syncEphemeralSnapshot } from '../../lib/api';
import { MitraItem } from '../../types';

export default function MitraDatabasePage() {
  const [items, setItems] = useState<MitraItem[]>([]);
  const [kecOptions, setKecOptions] = useState<string[]>([]);
  const [search, setSearch] = useState('');
  const [kecFilter, setKecFilter] = useState('');
  const [jkFilter, setJkFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({
    id_sobat: '',
    nama: '',
    email: '',
    alamat: '',
    nomor_hp: '',
    jenis_kelamin: 'Laki-laki',
    desa: '',
    kecamatan: 'Banyuwangi',
  });
  const [notice, setNotice] = useState('');

  const loadData = () => {
    const params = new URLSearchParams();
    if (search) params.set('search', search);
    if (kecFilter) params.set('kecamatan', kecFilter);
    if (jkFilter) params.set('jenis_kelamin', jkFilter);
    apiFetch<{ ok: boolean; items: MitraItem[]; kecamatan_options: string[] }>(`/mitra/list?${params.toString()}`)
      .then((res) => {
        setItems(res.items || []);
        setKecOptions(res.kecamatan_options || []);
      })
      .catch(() => {});
  };

  useEffect(() => {
    loadData();
  }, [kecFilter, jkFilter]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiFetch('/mitra/create', { method: 'POST', body: JSON.stringify(form) });
      setShowModal(false);
      setForm({ id_sobat: '', nama: '', email: '', alamat: '', nomor_hp: '', jenis_kelamin: 'Laki-laki', desa: '', kecamatan: 'Banyuwangi' });
      setNotice('Data mitra berhasil ditambahkan.');
      await syncEphemeralSnapshot();
      loadData();
    } catch (err: any) {
      setNotice(err.message);
    }
  };

  const handleToggle = async (id: number) => {
    await apiFetch(`/mitra/${id}/toggle`, { method: 'POST' });
    await syncEphemeralSnapshot();
    loadData();
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Hapus data mitra ini?')) return;
    await apiFetch(`/mitra/${id}`, { method: 'DELETE' });
    await syncEphemeralSnapshot();
    loadData();
  };

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
                <span className="text-white font-semibold">Data Mitra</span>
              </div>
              <h1 className="text-xl sm:text-2xl font-extrabold">Data Mitra Statistik ({items.length})</h1>
              <p className="text-xs text-blue-100/80 mt-1">Database resmi Sobat BPS Kabupaten Banyuwangi mencakup 8 isian standar.</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Link to="/mitra/template?tab=mitra" className="h-10 px-4 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 text-xs font-semibold inline-flex items-center gap-1.5">
              <FileUp className="w-3.5 h-3.5" /> Upload CSV
            </Link>
            <button onClick={() => setShowModal(true)} className="h-10 px-4 rounded-xl bg-white hover:bg-blue-50 text-blue-700 text-xs font-bold inline-flex items-center gap-1.5 shadow-md">
              <Plus className="w-3.5 h-3.5" /> Tambah Mitra
            </button>
          </div>
        </div>
      </div>

      {notice && (
        <div className="p-3.5 rounded-2xl bg-blue-50 border border-blue-200 text-xs font-semibold text-blue-800 flex items-center justify-between">
          <span>{notice}</span>
          <button onClick={() => setNotice('')}><X className="w-4 h-4" /></button>
        </div>
      )}

      <div className="bg-white rounded-3xl p-5 border border-slate-200/80 shadow-soft flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && loadData()}
            placeholder="Cari nama, ID Sobat, desa, nomor HP, atau email..."
            className="w-full pl-10 pr-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50/70 focus:bg-white focus:border-blue-500 outline-none"
          />
        </div>
        <select value={kecFilter} onChange={(e) => setKecFilter(e.target.value)} className="px-3 py-2 text-xs rounded-xl border border-slate-200 bg-white">
          <option value="">Semua Kecamatan (25)</option>
          {kecOptions.map((k) => <option key={k} value={k}>{k}</option>)}
        </select>
        <select value={jkFilter} onChange={(e) => setJkFilter(e.target.value)} className="px-3 py-2 text-xs rounded-xl border border-slate-200 bg-white">
          <option value="">Semua Jenis Kelamin</option>
          <option value="Laki-laki">Laki-laki</option>
          <option value="Perempuan">Perempuan</option>
        </select>
        <button onClick={loadData} className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold">Cari</button>
      </div>

      <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-soft overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-bold text-[10px]">
              <th className="py-3 px-3 text-center">No</th>
              <th className="py-3 px-3">ID Sobat</th>
              <th className="py-3 px-3">Nama &amp; Email</th>
              <th className="py-3 px-3">Nomor HP</th>
              <th className="py-3 px-3">Jenis Kelamin</th>
              <th className="py-3 px-3">Desa &amp; Alamat</th>
              <th className="py-3 px-3">Kecamatan</th>
              <th className="py-3 px-3 text-center">Status</th>
              <th className="py-3 px-3 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {items.map((m, idx) => (
              <tr key={m.id} className="hover:bg-blue-50/40">
                <td className="py-3 px-3 text-center font-mono text-slate-400">{idx + 1}</td>
                <td className="py-3 px-3 font-mono font-bold text-blue-700 whitespace-nowrap">{m.id_sobat}</td>
                <td className="py-3 px-3">
                  <div className="font-bold text-slate-900">{m.nama}</div>
                  <div className="text-[10px] text-slate-400">{m.email || '-'}</div>
                </td>
                <td className="py-3 px-3 font-mono whitespace-nowrap">
                  <span className="inline-flex items-center gap-1 text-slate-700"><Phone className="w-3 h-3 text-blue-500" /> {m.nomor_hp || '-'}</span>
                </td>
                <td className="py-3 px-3 whitespace-nowrap">
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200/70">{m.jenis_kelamin}</span>
                </td>
                <td className="py-3 px-3">
                  <div className="font-semibold text-slate-800">{m.desa || '-'}</div>
                  <div className="text-[10px] text-slate-400 max-w-[200px] truncate" title={m.alamat}>{m.alamat || '-'}</div>
                </td>
                <td className="py-3 px-3 whitespace-nowrap">
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg bg-slate-100 font-semibold text-slate-800">
                    <MapPin className="w-3 h-3 text-blue-600" /> {m.kecamatan}
                  </span>
                </td>
                <td className="py-3 px-3 text-center">
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${m.status_aktif ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'bg-slate-100 text-slate-500'}`}>
                    {m.status_aktif ? 'Aktif' : 'Nonaktif'}
                  </span>
                </td>
                <td className="py-3 px-3 text-right whitespace-nowrap">
                  <button onClick={() => handleToggle(m.id)} title="Ubah Status" className="p-1.5 rounded-lg hover:bg-blue-50 text-slate-500 hover:text-blue-600"><Power className="w-3.5 h-3.5" /></button>
                  <button onClick={() => handleDelete(m.id)} title="Hapus" className="p-1.5 rounded-lg hover:bg-blue-50 text-slate-500 hover:text-blue-700"><Trash2 className="w-3.5 h-3.5" /></button>
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr>
                <td colSpan={9} className="py-12 text-center text-slate-400 text-xs">
                  Belum ada data mitra. Tambahkan manual atau upload CSV melalui menu <strong>Template &amp; Upload</strong>.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <h3 className="text-sm font-extrabold text-slate-900">Tambah Mitra Baru</h3>
              <button onClick={() => setShowModal(false)}><X className="w-5 h-5 text-slate-400" /></button>
            </div>
            <form onSubmit={handleCreate} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <input required placeholder="ID Sobat *" value={form.id_sobat} onChange={(e) => setForm({ ...form, id_sobat: e.target.value })} className="px-3 py-2 rounded-xl border border-slate-200 text-xs" />
                <input required placeholder="Nama Lengkap *" value={form.nama} onChange={(e) => setForm({ ...form, nama: e.target.value })} className="px-3 py-2 rounded-xl border border-slate-200 text-xs" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <input placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="px-3 py-2 rounded-xl border border-slate-200 text-xs" />
                <input placeholder="Nomor HP" value={form.nomor_hp} onChange={(e) => setForm({ ...form, nomor_hp: e.target.value })} className="px-3 py-2 rounded-xl border border-slate-200 text-xs" />
              </div>
              <input placeholder="Alamat Lengkap" value={form.alamat} onChange={(e) => setForm({ ...form, alamat: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs" />
              <div className="grid grid-cols-3 gap-3">
                <select value={form.jenis_kelamin} onChange={(e) => setForm({ ...form, jenis_kelamin: e.target.value })} className="px-3 py-2 rounded-xl border border-slate-200 text-xs">
                  <option value="Laki-laki">Laki-laki</option>
                  <option value="Perempuan">Perempuan</option>
                </select>
                <input placeholder="Desa / Kelurahan" value={form.desa} onChange={(e) => setForm({ ...form, desa: e.target.value })} className="px-3 py-2 rounded-xl border border-slate-200 text-xs" />
                <select value={form.kecamatan} onChange={(e) => setForm({ ...form, kecamatan: e.target.value })} className="px-3 py-2 rounded-xl border border-slate-200 text-xs">
                  {kecOptions.map((k) => <option key={k} value={k}>{k}</option>)}
                </select>
              </div>
              <div className="pt-3 flex justify-end gap-2">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100">Batal</button>
                <button type="submit" className="px-5 py-2 rounded-xl bg-blue-600 text-white text-xs font-bold">Simpan Mitra</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
