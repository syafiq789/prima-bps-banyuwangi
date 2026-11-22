'use client';

import React, { Suspense, useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { Download, Upload, Search, Calendar, Users, ArrowUpRight, MapPin, Home, CheckCircle2 } from 'lucide-react';
import { apiFetch, syncEphemeralSnapshot } from '@/lib/api';
import { KegiatanItem, MitraItem } from '@/types';

function MitraTemplateInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const activeTab = searchParams.get('tab') === 'mitra' ? 'mitra' : 'kegiatan';

  const [kegiatans, setKegiatans] = useState<KegiatanItem[]>([]);
  const [mitras, setMitras] = useState<MitraItem[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [search, setSearch] = useState('');

  const loadAll = () => {
    apiFetch<{ ok: boolean; items: KegiatanItem[] }>('/mitra/kegiatan')
      .then((res) => setKegiatans(res.items || []))
      .catch(() => {});
    apiFetch<{ ok: boolean; items: MitraItem[] }>('/mitra/list')
      .then((res) => setMitras(res.items || []))
      .catch(() => {});
  };

  useEffect(() => {
    loadAll();
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;
    setUploading(true);
    setMessage('');
    try {
      const fd = new FormData();
      fd.append('file', selectedFile);
      const endpoint = activeTab === 'mitra' ? '/mitra/upload-mitra' : '/mitra/upload-kegiatan';
      const res = await apiFetch<{ ok: boolean; message: string }>(endpoint, { method: 'POST', body: fd });
      setMessage(res.message || 'Upload berhasil!');
      setSelectedFile(null);
      await syncEphemeralSnapshot();
      loadAll();
    } catch (err: any) {
      setMessage(err.message || 'Gagal upload CSV.');
    } finally {
      setUploading(false);
    }
  };

  const q = search.toLowerCase().trim();
  const filteredKeg = kegiatans.filter(
    (k) => !q || `${k.nama_kegiatan} ${k.tim_kerja} ${k.bulan} ${k.tahun}`.toLowerCase().includes(q)
  );
  const filteredMitra = mitras.filter(
    (m) => !q || `${m.id_sobat} ${m.nama} ${m.email} ${m.desa} ${m.kecamatan}`.toLowerCase().includes(q)
  );

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
                <span className="text-white font-semibold">Template &amp; Upload</span>
              </div>
              <h1 className="text-xl sm:text-2xl font-extrabold">Template &amp; Upload Data (.CSV)</h1>
              <p className="text-xs text-blue-100/80 mt-1">Unduh template, isi data, lalu upload agar langsung tersimpan dan terhubung ke seluruh fitur.</p>
            </div>
          </div>

          <div className="inline-flex p-1 rounded-2xl bg-blue-950/45 border border-white/15 self-start lg:self-auto">
            <button
              onClick={() => { router.push('/mitra/template?tab=kegiatan'); setSelectedFile(null); setSearch(''); }}
              className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition ${activeTab === 'kegiatan' ? 'bg-white text-blue-700 shadow-md' : 'text-blue-100 hover:text-white'}`}
            >
              <Calendar className="w-3.5 h-3.5" />
              <span>Upload Kegiatan ({kegiatans.length})</span>
            </button>
            <button
              onClick={() => { router.push('/mitra/template?tab=mitra'); setSelectedFile(null); setSearch(''); }}
              className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition ${activeTab === 'mitra' ? 'bg-white text-blue-700 shadow-md' : 'text-blue-100 hover:text-white'}`}
            >
              <Users className="w-3.5 h-3.5" />
              <span>Upload Data Mitra ({mitras.length})</span>
            </button>
          </div>
        </div>
      </div>

      {message && (
        <div className="p-4 rounded-2xl bg-blue-50 border border-blue-200 text-xs font-bold text-blue-800 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
          <span>{message}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <div className="lg:col-span-6 bg-white rounded-3xl p-6 border border-slate-200/80 shadow-soft flex flex-col justify-between gap-4">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <span className="w-8 h-8 rounded-xl bg-blue-600 text-white font-black text-xs flex items-center justify-center">1</span>
              <div>
                <h2 className="text-sm font-extrabold text-slate-900">
                  {activeTab === 'kegiatan' ? 'Template Kegiatan' : 'Template Data Mitra'}
                </h2>
                <p className="text-[11px] text-slate-500">Format isian resmi sebelum upload CSV</p>
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-blue-50/60 border border-blue-100">
              <p className="text-[10px] font-bold uppercase tracking-wider text-blue-700 mb-2">Isian yang Dibutuhkan</p>
              <div className="flex flex-wrap gap-1.5 text-[11px]">
                {(activeTab === 'kegiatan'
                  ? ['Nama Kegiatan', 'Tim Kerja', 'Tahun', 'Bulan', 'Tanggal Mulai', 'Tanggal Selesai']
                  : ['ID Sobat', 'Nama', 'Email', 'Alamat', 'Nomor HP', 'Jenis Kelamin', 'Desa', 'Kecamatan']
                ).map((field) => (
                  <span key={field} className="px-2.5 py-1 rounded-lg bg-white border border-blue-200/80 text-slate-800 font-semibold">
                    {field}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <a
            href={activeTab === 'kegiatan' ? '/api/v1/mitra/download-template-kegiatan' : '/api/v1/mitra/download-template-mitra'}
            className="w-full py-2.5 px-4 rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 font-bold text-xs flex items-center justify-center gap-2 transition"
          >
            <Download className="w-4 h-4" />
            <span>Unduh Template {activeTab === 'kegiatan' ? 'Kegiatan' : 'Mitra'} (.CSV)</span>
          </a>
        </div>

        <div className="lg:col-span-6 bg-white rounded-3xl p-6 border border-blue-200/80 shadow-soft flex flex-col justify-between">
          <div className="flex items-center gap-3 mb-4">
            <span className="w-8 h-8 rounded-xl bg-blue-600 text-white font-black text-xs flex items-center justify-center">2</span>
            <div>
              <h2 className="text-sm font-extrabold text-slate-900">
                Upload {activeTab === 'kegiatan' ? 'Kegiatan' : 'Data Mitra'}
              </h2>
              <p className="text-[11px] text-slate-500">Pilih file CSV yang sudah diisi, data langsung tersimpan otomatis</p>
            </div>
          </div>

          <form onSubmit={handleUpload} className="flex-1 flex flex-col justify-between gap-4">
            <label className="relative flex-1 min-h-[130px] border-2 border-dashed border-blue-300 hover:border-blue-500 rounded-2xl p-6 text-center bg-blue-50/40 hover:bg-blue-50/70 transition cursor-pointer flex flex-col items-center justify-center">
              <input
                type="file"
                accept=".csv,.txt"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                className="hidden"
              />
              <Upload className="w-6 h-6 text-blue-600 mb-2" />
              <p className="text-xs font-bold text-slate-800">
                {selectedFile ? `File siap: ${selectedFile.name}` : `Klik untuk memilih file CSV ${activeTab === 'kegiatan' ? 'Kegiatan' : 'Data Mitra'}`}
              </p>
              <p className="text-[11px] text-slate-400 mt-1">Mendukung format .csv (UTF-8)</p>
            </label>

            <button
              type="submit"
              disabled={!selectedFile || uploading}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-600 to-sky-500 hover:opacity-95 text-white text-xs font-bold shadow-md disabled:opacity-50 flex items-center justify-center gap-2 transition"
            >
              <Upload className="w-4 h-4" />
              <span>{uploading ? 'Mengunggah...' : 'Upload & Simpan Otomatis'}</span>
            </button>
          </form>
        </div>
      </div>

      <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-soft">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 pb-4 border-b border-slate-100 mb-4">
          <div>
            <h2 className="text-base font-extrabold text-slate-900">
              {activeTab === 'kegiatan' ? `Daftar Kegiatan Tersimpan (${filteredKeg.length})` : `Daftar Mitra Tersimpan (${filteredMitra.length})`}
            </h2>
            <p className="text-xs text-slate-500">Data otomatis terhubung ke seluruh menu Monitoring Mitra.</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative w-full sm:w-60">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Cari di tabel hasil upload..."
                className="w-full pl-8 pr-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50/70 focus:bg-white focus:border-blue-500 outline-none"
              />
            </div>
            <Link
              href={activeTab === 'kegiatan' ? '/mitra/kegiatan' : '/mitra/database'}
              className="px-3 py-2 rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 text-xs font-bold inline-flex items-center gap-1"
            >
              <span>{activeTab === 'kegiatan' ? 'Daftar Kegiatan' : 'Data Mitra'}</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
            <Link href="/mitra/laporan" className="px-3 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold inline-flex items-center gap-1">
              <span>Laporan &amp; Honor</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        <div className="overflow-x-auto max-h-[500px] overflow-y-auto rounded-2xl border border-slate-200/80">
          {activeTab === 'kegiatan' ? (
            <table className="w-full text-left text-xs">
              <thead className="sticky top-0 bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-bold text-[10px]">
                <tr>
                  <th className="py-3 px-3 text-center">No</th>
                  <th className="py-3 px-4">Nama Kegiatan</th>
                  <th className="py-3 px-4">Tim Kerja</th>
                  <th className="py-3 px-4">Jadwal</th>
                  <th className="py-3 px-4 text-center">Mitra</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredKeg.map((k, i) => (
                  <tr key={k.id} className="hover:bg-blue-50/40">
                    <td className="py-3 px-3 text-center font-mono text-slate-400">{i + 1}</td>
                    <td className="py-3 px-4">
                      <div className="font-bold text-slate-900">{k.nama_kegiatan}</div>
                      <div className="text-[10px] text-slate-400">Tahun {k.tahun} &bull; {k.bulan}</div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200/70">{k.tim_kerja}</span>
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-600 whitespace-nowrap">
                      {k.tanggal_mulai} s.d {k.tanggal_selesai}
                    </td>
                    <td className="py-3 px-4 text-center font-bold text-slate-700">{k.total_mitra} Orang</td>
                  </tr>
                ))}
                {filteredKeg.length === 0 && (
                  <tr><td colSpan={5} className="py-10 text-center text-slate-400">Belum ada data kegiatan.</td></tr>
                )}
              </tbody>
            </table>
          ) : (
            <table className="w-full text-left text-xs">
              <thead className="sticky top-0 bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-bold text-[10px]">
                <tr>
                  <th className="py-3 px-3 text-center">No</th>
                  <th className="py-3 px-4">ID Sobat</th>
                  <th className="py-3 px-4">Nama &amp; Email</th>
                  <th className="py-3 px-4">Nomor HP</th>
                  <th className="py-3 px-4 text-center">Jenis Kelamin</th>
                  <th className="py-3 px-4">Desa &amp; Alamat</th>
                  <th className="py-3 px-4">Kecamatan</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredMitra.map((m, i) => (
                  <tr key={m.id} className="hover:bg-blue-50/40">
                    <td className="py-3 px-3 text-center font-mono text-slate-400">{i + 1}</td>
                    <td className="py-3 px-4 font-mono font-bold text-blue-700 whitespace-nowrap">{m.id_sobat}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2.5">
                        <div className="w-7 h-7 rounded-full bg-blue-100 text-blue-700 font-extrabold text-[10px] flex items-center justify-center shrink-0">
                          {(m.nama || 'M').slice(0, 1).toUpperCase()}
                        </div>
                        <div>
                          <div className="font-bold text-slate-900">{m.nama}</div>
                          <div className="text-[10px] text-slate-400">{m.email || '-'}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] whitespace-nowrap">{m.nomor_hp || '-'}</td>
                    <td className="py-3 px-4 text-center">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200/70">{m.jenis_kelamin}</span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-800">Desa {m.desa || '-'}</div>
                      <div className="text-[10px] text-slate-400 max-w-[220px] truncate">{m.alamat || '-'}</div>
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg bg-slate-100 font-bold text-slate-800">
                        <MapPin className="w-3 h-3 text-blue-600" /> {m.kecamatan}
                      </span>
                    </td>
                  </tr>
                ))}
                {filteredMitra.length === 0 && (
                  <tr><td colSpan={7} className="py-10 text-center text-slate-400">Belum ada data mitra.</td></tr>
                )}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}

export default function MitraTemplatePage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-xs text-slate-500">Memuat halaman Template &amp; Upload...</div>}>
      <MitraTemplateInner />
    </Suspense>
  );
}
