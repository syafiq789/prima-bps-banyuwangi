'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { apiFetch, formatRupiah } from '@/lib/api';

export default function HubPage() {
  const [stats, setStats] = useState({
    total_docs: 0,
    total_mitra: 0,
    total_kegiatan: 0,
    total_pegawai: 0,
    total_pengajuan: 0,
    total_honor: 0,
  });

  useEffect(() => {
    apiFetch<{ ok: boolean; stats: typeof stats }>('/hub')
      .then((res) => {
        if (res.ok && res.stats) setStats(res.stats);
      })
      .catch(() => {});
  }, []);

  const modules = [
    {
      title: 'PRIMA — Arsip & AKIP',
      desc: 'Pusat arsip dokumen perencanaan, pengukuran, dan pelaporan kinerja instansi.',
      logo: '/images/logo_prima.png',
      href: '/akip',
      stat: `${stats.total_docs} Dokumen`,
    },
    {
      title: 'Monitoring Mitra',
      desc: 'Pengelolaan data mitra statistik, upload CSV, penugasan, penilaian, dan laporan honor.',
      logo: '/images/logo_mitra.svg',
      href: '/mitra/dashboard',
      stat: `${stats.total_mitra} Mitra • ${stats.total_kegiatan} Kegiatan`,
    },
    {
      title: 'Kinerja Pegawai',
      desc: 'Pemantauan data pegawai, catatan aktivitas harian, dan ringkasan kinerja per tim.',
      logo: '/images/logo_pegawai.svg',
      href: '/pegawai',
      stat: `${stats.total_pegawai} Pegawai`,
    },
    {
      title: 'Tracking Keuangan',
      desc: 'Alur pengajuan anggaran, persetujuan, pencairan, dan rekapitulasi realisasi.',
      logo: '/images/logo_keuangan.svg',
      href: '/keuangan',
      stat: `${stats.total_pengajuan} Pengajuan • ${formatRupiah(stats.total_honor)}`,
    },
  ];

  return (
    <div className="space-y-6">
      <div className="executive-banner rounded-3xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
        <div className="relative z-10 max-w-2xl">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/15 border border-white/20 text-[11px] font-bold text-sky-100 mb-3">
            LENTERA BPS Kabupaten Banyuwangi (3510)
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">Portal Sistem Informasi Terpadu</h1>
          <p className="text-xs sm:text-sm text-blue-100/85 mt-2 leading-relaxed">
            Satu platform Next.js + TypeScript modern untuk mengelola Arsip AKIP, Monitoring Mitra Statistik, Kinerja Pegawai, dan Tracking Keuangan BPS Kabupaten Banyuwangi.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {modules.map((mod) => (
          <Link
            key={mod.title}
            href={mod.href}
            className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-soft hover:shadow-lg hover:border-blue-300 hover:-translate-y-0.5 transition-all group flex flex-col justify-between"
          >
            <div className="flex items-start gap-4">
              <div className="w-14 h-14 rounded-2xl bg-blue-50 border border-blue-100 p-2 flex items-center justify-center shrink-0">
                <img src={mod.logo} alt={mod.title} className="w-full h-full object-contain" />
              </div>
              <div>
                <h2 className="text-base font-extrabold text-slate-900 group-hover:text-blue-700 transition-colors">{mod.title}</h2>
                <p className="text-xs text-slate-500 mt-1 leading-relaxed">{mod.desc}</p>
              </div>
            </div>
            <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between text-xs">
              <span className="px-3 py-1 rounded-full bg-blue-50 text-blue-700 font-bold text-[11px]">{mod.stat}</span>
              <span className="font-bold text-blue-600 inline-flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                Buka Modul <ArrowRight className="w-3.5 h-3.5" />
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
