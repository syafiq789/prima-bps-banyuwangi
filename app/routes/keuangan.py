from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import func
from app.models import (
    db, AkunAnggaran, KomponenAnggaran, PengajuanAnggaran, PersetujuanAnggaran, RealisasiAnggaran, Kegiatan
)

keuangan_bp = Blueprint('keuangan', __name__, url_prefix='/keuangan')

@keuangan_bp.route('/')
@keuangan_bp.route('/dashboard')
@login_required
def dashboard():
    total_pengajuan = PengajuanAnggaran.query.count()
    menunggu_persetujuan = PengajuanAnggaran.query.filter_by(status='MENUNGGU').count()
    
    all_pengajuan = PengajuanAnggaran.query.all()
    total_anggaran_diajukan = sum(p.jumlah_diajukan for p in all_pengajuan)
    
    pengajuan_disetujui = PengajuanAnggaran.query.filter_by(status='DISETUJUI').all()
    total_anggaran_disetujui = sum(p.jumlah_diajukan for p in pengajuan_disetujui)
    
    all_realisasi = RealisasiAnggaran.query.all()
    total_realisasi = sum(r.jumlah_realisasi for r in all_realisasi)
    
    total_pagu_akun = sum(a.pagu_awal for a in AkunAnggaran.query.all())
    sisa_anggaran = max(0, total_pagu_akun - total_realisasi)
    persentase_serapan = round((total_realisasi / total_pagu_akun * 100), 1) if total_pagu_akun > 0 else 0

    transaksi_terbaru = PengajuanAnggaran.query.order_by(PengajuanAnggaran.created_at.desc()).limit(7).all()
    realisasi_terbaru = RealisasiAnggaran.query.order_by(RealisasiAnggaran.created_at.desc()).limit(5).all()

    # Data Chart.js: Komposisi Pagu vs Realisasi per Kategori
    kategori_list = ['HONOR', 'PERJADIN', 'BAHAN']
    pagu_per_kat = []
    real_per_kat = []
    for k in kategori_list:
        pagu_k = db.session.query(func.sum(AkunAnggaran.pagu_awal)).filter(AkunAnggaran.kategori == k).scalar() or 0
        # hitung realisasi kategori k
        real_k = db.session.query(func.sum(RealisasiAnggaran.jumlah_realisasi))\
            .join(PengajuanAnggaran, RealisasiAnggaran.pengajuan_id == PengajuanAnggaran.id)\
            .join(AkunAnggaran, PengajuanAnggaran.akun_id == AkunAnggaran.id)\
            .filter(AkunAnggaran.kategori == k).scalar() or 0
        pagu_per_kat.append(pagu_k)
        real_per_kat.append(real_k)

    return render_template(
        'keuangan/dashboard.html',
        total_pengajuan=total_pengajuan,
        menunggu_persetujuan=menunggu_persetujuan,
        total_anggaran_diajukan=total_anggaran_diajukan,
        total_anggaran_disetujui=total_anggaran_disetujui,
        total_realisasi=total_realisasi,
        sisa_anggaran=sisa_anggaran,
        total_pagu_akun=total_pagu_akun,
        persentase_serapan=persentase_serapan,
        transaksi_terbaru=transaksi_terbaru,
        realisasi_terbaru=realisasi_terbaru,
        kategori_labels=kategori_list,
        pagu_per_kat=pagu_per_kat,
        real_per_kat=real_per_kat
    )

@keuangan_bp.route('/akun')
@login_required
def akun():
    akun_list = AkunAnggaran.query.order_by(AkunAnggaran.kode_akun.asc()).all()
    return render_template('keuangan/akun.html', akun_list=akun_list)

@keuangan_bp.route('/akun/create', methods=['POST'])
@login_required
def create_akun():
    kode_akun = request.form.get('kode_akun')
    nama_akun = request.form.get('nama_akun')
    kategori = request.form.get('kategori', 'HONOR')
    pagu_awal = request.form.get('pagu_awal', 0, type=int)

    if not kode_akun or not nama_akun:
        flash('Kode Akun dan Nama Akun wajib diisi.', 'danger')
        return redirect(url_for('keuangan.akun'))

    if AkunAnggaran.query.filter_by(kode_akun=kode_akun).first():
        flash(f'Akun {kode_akun} sudah ada.', 'warning')
        return redirect(url_for('keuangan.akun'))

    ak = AkunAnggaran(
        kode_akun=kode_akun,
        nama_akun=nama_akun,
        kategori=kategori,
        pagu_awal=pagu_awal
    )
    db.session.add(ak)
    db.session.commit()
    flash(f'Akun {kode_akun} berhasil ditambahkan.', 'success')
    return redirect(url_for('keuangan.akun'))

@keuangan_bp.route('/komponen')
@login_required
def komponen():
    komponen_list = KomponenAnggaran.query.order_by(KomponenAnggaran.kode_komponen.asc()).all()
    akun_options = AkunAnggaran.query.all()
    kegiatan_options = Kegiatan.query.all()
    return render_template('keuangan/komponen.html', komponen_list=komponen_list, akun_options=akun_options, kegiatan_options=kegiatan_options)

@keuangan_bp.route('/komponen/create', methods=['POST'])
@login_required
def create_komponen():
    kode_komponen = request.form.get('kode_komponen')
    nama_komponen = request.form.get('nama_komponen')
    akun_id = request.form.get('akun_id', type=int)
    kegiatan_id = request.form.get('kegiatan_id', type=int)
    pagu_komponen = request.form.get('pagu_komponen', 0, type=int)

    comp = KomponenAnggaran(
        kode_komponen=kode_komponen,
        nama_komponen=nama_komponen,
        akun_id=akun_id,
        kegiatan_id=kegiatan_id,
        pagu_komponen=pagu_komponen
    )
    db.session.add(comp)
    db.session.commit()
    flash(f'Komponen {nama_komponen} berhasil ditambahkan.', 'success')
    return redirect(url_for('keuangan.komponen'))

@keuangan_bp.route('/pengajuan')
@login_required
def pengajuan():
    status_filter = request.args.get('status', '').strip()
    query = PengajuanAnggaran.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    pengajuan_list = query.order_by(PengajuanAnggaran.created_at.desc()).all()
    akun_options = AkunAnggaran.query.all()
    komponen_options = KomponenAnggaran.query.all()
    kegiatan_options = Kegiatan.query.all()
    return render_template('keuangan/pengajuan.html', pengajuan_list=pengajuan_list, akun_options=akun_options, komponen_options=komponen_options, kegiatan_options=kegiatan_options, status_filter=status_filter)

@keuangan_bp.route('/pengajuan/create', methods=['POST'])
@login_required
def create_pengajuan():
    judul_pengajuan = request.form.get('judul_pengajuan')
    akun_id = request.form.get('akun_id', type=int)
    komponen_id = request.form.get('komponen_id', type=int)
    kegiatan_id = request.form.get('kegiatan_id', type=int)
    jumlah_diajukan = request.form.get('jumlah_diajukan', 0, type=int)
    keterangan = request.form.get('keterangan', '')

    nomor_pengajuan = f"AJU-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    item = PengajuanAnggaran(
        nomor_pengajuan=nomor_pengajuan,
        judul_pengajuan=judul_pengajuan,
        akun_id=akun_id,
        komponen_id=komponen_id,
        kegiatan_id=kegiatan_id,
        jumlah_diajukan=jumlah_diajukan,
        pengaju_id=current_user.id,
        keterangan=keterangan
    )
    db.session.add(item)
    db.session.commit()
    flash(f'Pengajuan {nomor_pengajuan} berhasil dibuat.', 'success')
    return redirect(url_for('keuangan.pengajuan'))

@keuangan_bp.route('/pengajuan/<int:id>/delete', methods=['POST'])
@login_required
def delete_pengajuan(id):
    p = PengajuanAnggaran.query.get_or_404(id)
    nomor = p.nomor_pengajuan
    db.session.delete(p)
    db.session.commit()
    flash(f'Pengajuan {nomor} berhasil dihapus.', 'info')
    return redirect(url_for('keuangan.pengajuan'))

@keuangan_bp.route('/persetujuan')
@login_required
def persetujuan():
    pengajuan_menunggu = PengajuanAnggaran.query.filter_by(status='MENUNGGU').order_by(PengajuanAnggaran.created_at.asc()).all()
    riwayat_persetujuan = PersetujuanAnggaran.query.order_by(PersetujuanAnggaran.tanggal_keputusan.desc()).all()
    return render_template('keuangan/persetujuan.html', pengajuan_menunggu=pengajuan_menunggu, riwayat_persetujuan=riwayat_persetujuan)

@keuangan_bp.route('/persetujuan/action', methods=['POST'])
@login_required
def action_persetujuan():
    pengajuan_id = request.form.get('pengajuan_id', type=int)
    status = request.form.get('status') # 'DISETUJUI' or 'DITOLAK'
    catatan = request.form.get('catatan', '')

    pengajuan = PengajuanAnggaran.query.get_or_404(pengajuan_id)
    pengajuan.status = status

    persetujuan_item = PersetujuanAnggaran(
        pengajuan_id=pengajuan.id,
        approver_id=current_user.id,
        status_keputusan=status,
        jumlah_disetujui=pengajuan.jumlah_diajukan if status == 'DISETUJUI' else 0,
        catatan_persetujuan=catatan
    )
    db.session.add(persetujuan_item)
    db.session.commit()
    flash(f'Pengajuan {pengajuan.nomor_pengajuan} berhasil diproses dengan status {status}.', 'success')
    return redirect(url_for('keuangan.persetujuan'))

@keuangan_bp.route('/realisasi')
@login_required
def realisasi():
    realisasi_list = RealisasiAnggaran.query.order_by(RealisasiAnggaran.created_at.desc()).all()
    pengajuan_disetujui = PengajuanAnggaran.query.filter_by(status='DISETUJUI').filter(~PengajuanAnggaran.realisasi_list.any()).all()
    return render_template('keuangan/realisasi.html', realisasi_list=realisasi_list, pengajuan_disetujui=pengajuan_disetujui)

@keuangan_bp.route('/realisasi/create', methods=['POST'])
@login_required
def create_realisasi():
    pengajuan_id = request.form.get('pengajuan_id', type=int)
    nomor_spm_sp2d = request.form.get('nomor_spm_sp2d')
    jumlah_realisasi = request.form.get('jumlah_realisasi', 0, type=int)
    keterangan = request.form.get('keterangan', '')

    pengajuan = PengajuanAnggaran.query.get_or_404(pengajuan_id)
    r = RealisasiAnggaran(
        pengajuan_id=pengajuan.id,
        nomor_sp2d=nomor_spm_sp2d,
        jumlah_realisasi=jumlah_realisasi,
        tanggal_realisasi=datetime.utcnow().date(),
        keterangan=keterangan,
        dicatat_oleh_id=current_user.id
    )
    db.session.add(r)
    db.session.commit()
    flash('Realisasi anggaran berhasil dicatat.', 'success')
    return redirect(url_for('keuangan.realisasi'))

@keuangan_bp.route('/rekapitulasi')
@login_required
def rekapitulasi():
    akun_list = AkunAnggaran.query.all()
    rekap = []
    total_pagu_all = 0
    total_realisasi_all = 0
    for a in akun_list:
        pagu = a.pagu_awal
        total_pagu_all += pagu
        pengajuan = a.pengajuan_list.all()
        diajukan = sum(p.jumlah_diajukan for p in pengajuan)
        disetujui = sum(p.jumlah_diajukan for p in pengajuan if p.status == 'DISETUJUI')
        realisasi_total = sum(p.realisasi.jumlah_realisasi for p in pengajuan if p.realisasi)
        total_realisasi_all += realisasi_total
        sisa = max(0, pagu - realisasi_total)
        serapan_persen = round((realisasi_total / pagu * 100), 1) if pagu > 0 else 0
        rekap.append({
            'akun': a,
            'pagu': pagu,
            'diajukan': diajukan,
            'disetujui': disetujui,
            'realisasi': realisasi_total,
            'sisa': sisa,
            'serapan_persen': serapan_persen
        })
    avg_serapan_all = round((total_realisasi_all / total_pagu_all * 100), 1) if total_pagu_all > 0 else 0
    return render_template('keuangan/rekapitulasi.html', rekap=rekap, total_pagu_all=total_pagu_all, total_realisasi_all=total_realisasi_all, avg_serapan_all=avg_serapan_all)
