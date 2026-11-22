from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from backend.models import (
    db, Kegiatan, Mitra, PenugasanMitra, EvaluasiMitra,
    Pegawai, AktivitasPegawai, AkunAnggaran, KomponenAnggaran,
    PengajuanAnggaran, RealisasiAnggaran
)

hub_bp = Blueprint('hub', __name__)

@hub_bp.route('/launcher')
@hub_bp.route('/simpatik')
@hub_bp.route('/simpatik/hub')
@login_required
def index():
    # 1. Metrik Terpadu Lintas Modul
    total_mitra = Mitra.query.count()
    total_mitra_aktif = Mitra.query.filter_by(status_aktif=True).count()
    total_penugasan = PenugasanMitra.query.count()
    penugasan_selesai = PenugasanMitra.query.filter_by(status='SELESAI').count()

    total_pegawai = Pegawai.query.count()
    total_aktivitas = AktivitasPegawai.query.count()
    aktivitas_selesai = AktivitasPegawai.query.filter_by(status='SELESAI').count()

    total_pagu = sum(a.pagu_awal for a in AkunAnggaran.query.all())
    total_realisasi = sum(r.jumlah_realisasi for r in RealisasiAnggaran.query.all())
    serapan_persen = round((total_realisasi / total_pagu * 100), 1) if total_pagu > 0 else 0

    # 2. Matriks Kegiatan Terpadu (Menghubungkan Mitra + Pegawai + Keuangan)
    kegiatan_list = Kegiatan.query.order_by(Kegiatan.tanggal_mulai.desc()).all()
    matrix_kegiatan = []
    for k in kegiatan_list:
        penugasans = k.penugasan_mitra.all()
        target_dok = sum(p.target_dokumen for p in penugasans)
        real_dok = sum(p.realisasi_dokumen for p in penugasans)
        progres_dok = round((real_dok / target_dok * 100), 1) if target_dok > 0 else 0
        total_honor_mitra = sum(p.honor_total for p in penugasans)

        aktivitass = k.aktivitas_pegawai or []
        pegawai_terlibat = len(set(a.pegawai_id for a in aktivitass if a.pegawai_id))
        progres_pegawai = round(sum(a.persentase_selesai for a in aktivitass) / len(aktivitass), 1) if aktivitass else 0

        pengajuans = k.pengajuan_anggaran or []
        anggaran_diajukan = sum(p.jumlah_diajukan for p in pengajuans)
        anggaran_cair = sum(p.realisasi.jumlah_realisasi for p in pengajuans if p.realisasi)

        matrix_kegiatan.append({
            'kegiatan': k,
            'mitra_count': len(penugasans),
            'target_dok': target_dok,
            'real_dok': real_dok,
            'progres_dok': progres_dok,
            'total_honor_mitra': total_honor_mitra,
            'pegawai_count': pegawai_terlibat,
            'progres_pegawai': progres_pegawai,
            'anggaran_diajukan': anggaran_diajukan,
            'anggaran_cair': anggaran_cair
        })

    return render_template(
        'hub/index.html',
        total_mitra=total_mitra,
        total_mitra_aktif=total_mitra_aktif,
        total_penugasan=total_penugasan,
        penugasan_selesai=penugasan_selesai,
        total_pegawai=total_pegawai,
        total_aktivitas=total_aktivitas,
        aktivitas_selesai=aktivitas_selesai,
        total_pagu=total_pagu,
        total_realisasi=total_realisasi,
        serapan_persen=serapan_persen,
        matrix_kegiatan=matrix_kegiatan
    )

