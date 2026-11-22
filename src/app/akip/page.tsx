'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { FileText, Link2, ArrowUpRight, Home } from 'lucide-react';
import { apiFetch } from '@/lib/api';

interface AkipData {
  kpi: { total_docs: number; lengkap: number; belum_lengkap: number; total_categories: number };
  categories: { id: number; name: string; group: string; drive_url: string }[];
  documents: { id: number; title: string; category: string; year: number; status: string; drive_url: string }[];
  links: { id: number; title: string; url: string; description: string }[];
}

export default function AkipPage() {
  const [data, setData] = useState<AkipData | null>(null);

  useEffect(() => {
    apiFetch<{ ok: boolean } & AkipData>('/akip/overview')
      .then((res) => setData(res))
      .catch(() => {});
  }, []);

  const kpi = data?.kpi || { total_docs: 0, lengkap: 0, belum_lengkap: 0, total_categories: 0 };

  return (
    <div className="space-y-6">
      <div className="executive-banner rounded-3xl p-5 sm:p-6 text-white shadow-xl">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-white/95 p-1.5 flex items-center justify-center shrink-0">
            <img src="/images/logo_prima.png" alt="PRIMA" className="w-full h-full object-contain" />
          </div>
          <div>
            <div className="flex items-center gap-1.5 text-[11px] text-blue-200/80 mb-1">
              <Link href="/" className="hover:text-white inline-flex items-center gap-1"><Home className="w-3 h-3" /> LENTERA</Link>
              <span>/</span>
              <span className="text-white font-semibold">PRIMA — Arsip &amp; AKIP</span>
            </div>
            <h1 className="text-xl sm:text-2xl font-extrabold">Pusat Arsip &amp; Manajemen AKIP</h1>
            <p className="text-xs text-blue-100/80 mt-1">Arsip tertata, akuntabilitas terjaga, kinerja prima BPS Kabupaten Banyuwangi.</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft">
          <p className="text-xs text-slate-500 font-medium">Total Dokumen Arsip</p>
          <p className="text-2xl font-black text-slate-900 mt-1">{kpi.total_docs} <span className="text-xs text-slate-400">Berkas</span></p>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft">
          <p className="text-xs text-slate-500 font-medium">Dokumen Lengkap</p>
          <p className="text-2xl font-black text-blue-700 mt-1">{kpi.lengkap} <span className="text-xs text-slate-400">Berkas</span></p>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-soft">
          <p className="text-xs text-slate-500 font-medium">Kategori AKIP</p>
          <p className="text-2xl font-black text-slate-900 mt-1">{kpi.total_categories} <span className="text-xs text-slate-400">Kategori</span></p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8 bg-white rounded-3xl p-6 border border-slate-200/80 shadow-soft">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="w-4 h-4 text-blue-600" />
            <h2 className="text-base font-extrabold text-slate-900">Daftar Dokumen AKIP</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-bold text-[10px]">
                  <th className="py-3 px-4">Judul Dokumen</th>
                  <th className="py-3 px-4">Kategori</th>
                  <th className="py-3 px-4 text-center">Tahun</th>
                  <th className="py-3 px-4 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {(data?.documents || []).map((d) => (
                  <tr key={d.id} className="hover:bg-blue-50/40">
                    <td className="py-3 px-4 font-bold text-slate-900">{d.title}</td>
                    <td className="py-3 px-4 text-slate-600">{d.category}</td>
                    <td className="py-3 px-4 text-center font-mono">{d.year}</td>
                    <td className="py-3 px-4 text-center">
                      <span className="px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 text-[10px] font-bold">{d.status}</span>
                    </td>
                  </tr>
                ))}
                {(!data?.documents || data.documents.length === 0) && (
                  <tr><td colSpan={4} className="py-10 text-center text-slate-400">Belum ada dokumen AKIP diunggah.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="lg:col-span-4 bg-white rounded-3xl p-6 border border-slate-200/80 shadow-soft space-y-3">
          <div className="flex items-center gap-2">
            <Link2 className="w-4 h-4 text-blue-600" />
            <h2 className="text-base font-extrabold text-slate-900">Tautan Penting</h2>
          </div>
          {(data?.links || []).map((l) => (
            <a
              key={l.id}
              href={l.url}
              target="_blank"
              rel="noreferrer"
              className="block p-3.5 rounded-2xl bg-slate-50 hover:bg-blue-50 border border-slate-200/70 transition"
            >
              <div className="flex items-center justify-between text-xs font-bold text-slate-900">
                <span>{l.title}</span>
                <ArrowUpRight className="w-3.5 h-3.5 text-blue-600" />
              </div>
              {l.description && <p className="text-[11px] text-slate-500 mt-1">{l.description}</p>}
            </a>
          ))}
          {(!data?.links || data.links.length === 0) && (
            <p className="text-xs text-slate-400 py-4 text-center">Belum ada tautan aktif.</p>
          )}
        </div>
      </div>
    </div>
  );
}
