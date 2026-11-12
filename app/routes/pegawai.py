from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app.models import (
    db, Pegawai, AktivitasPegawai, Kegiatan, User
)

pegawai_bp = Blueprint('pegawai', __name__, url_prefix='/pegawai')

@pegawai_bp.route('/')
@pegawai_bp.route('/dashboard')
@login_required
def dashboard():
    total_pegawai = Pegawai.query.count()
    total_aktivitas = AktivitasPegawai.query.count()
    pekerjaan_selesai = AktivitasPegawai.query.filter_by(status='SELESAI').count()
    pekerjaan_proses = AktivitasPegawai.query.filter_by(status='PROSES').count()

    all_aktivitas = AktivitasPegawai.query.all()
    rata_rata_selesai = round(sum(a.persentase_selesai for a in all_aktivitas) / len(all_aktivitas), 1) if all_aktivitas else 0

    aktivitas_terbaru = AktivitasPegawai.query.order_by(AktivitasPegawai.created_at.desc()).limit(7).all()
    pegawai_list = Pegawai.query.limit(5).all()

    return render_template(
        'pegawai/dashboard.html',
        total_pegawai=total_pegawai,
        total_aktivitas=total_aktivitas,
        pekerjaan_selesai=pekerjaan_selesai,
        pekerjaan_proses=pekerjaan_proses,
        rata_rata_selesai=rata_rata_selesai,
        aktivitas_terbaru=aktivitas_terbaru,
        pegawai_list=pegawai_list
    )

@pegawai_bp.route('/database')
@login_required
def database():
    search = request.args.get('search', '').strip()
    query = Pegawai.query
    if search:
        query = query.filter((Pegawai.nama_lengkap.ilike(f'%{search}%')) | (Pegawai.nip.ilike(f'%{search}%')) | (Pegawai.tim_kerja.ilike(f'%{search}%')))
    pegawai_list = query.order_by(Pegawai.nama_lengkap.asc()).all()
    return render_template('pegawai/database.html', pegawai_list=pegawai_list, search=search)

@pegawai_bp.route('/database/create', methods=['POST'])
@login_required
def create_pegawai():
    nip = request.form.get('nip')
    nama_lengkap = request.form.get('nama_lengkap')
    jabatan = request.form.get('jabatan')
    tim_kerja = request.form.get('tim_kerja')
    email = request.form.get('email')

    if not nip or not nama_lengkap:
        flash('NIP dan Nama Lengkap wajib diisi.', 'danger')
        return redirect(url_for('pegawai.database'))

    if Pegawai.query.filter_by(nip=nip).first():
        flash(f'Pegawai dengan NIP {nip} sudah ada.', 'warning')
        return redirect(url_for('pegawai.database'))

    p = Pegawai(
        nip=nip,
        nama_lengkap=nama_lengkap,
        jabatan=jabatan,
        tim_kerja=tim_kerja,
        email=email
    )
    db.session.add(p)
    db.session.commit()
    flash(f'Pegawai {nama_lengkap} berhasil ditambahkan.', 'success')
    return redirect(url_for('pegawai.database'))

@pegawai_bp.route('/aktivitas')
@login_required
def aktivitas():
    aktivitas_list = AktivitasPegawai.query.order_by(AktivitasPegawai.created_at.desc()).all()
    pegawai_options = Pegawai.query.filter_by(status_aktif=True).order_by(Pegawai.nama_lengkap.asc()).all()
    kegiatan_options = Kegiatan.query.order_by(Kegiatan.nama_kegiatan.asc()).all()
    return render_template('pegawai/aktivitas.html', aktivitas_list=aktivitas_list, pegawai_options=pegawai_options, kegiatan_options=kegiatan_options)

@pegawai_bp.route('/aktivitas/create', methods=['POST'])
@login_required
def create_aktivitas():
    pegawai_id = request.form.get('pegawai_id', type=int)
    kegiatan_id = request.form.get('kegiatan_id', type=int)
    judul_aktivitas = request.form.get('judul_aktivitas')
    deskripsi = request.form.get('deskripsi', '')
    tgl_mulai_str = request.form.get('tanggal_mulai')
    tgl_selesai_str = request.form.get('tanggal_selesai')
    persentase_selesai = request.form.get('persentase_selesai', 0, type=int)

    try:
        tgl_mulai = datetime.strptime(tgl_mulai_str, '%Y-%m-%d').date() if tgl_mulai_str else datetime.utcnow().date()
        tgl_selesai = datetime.strptime(tgl_selesai_str, '%Y-%m-%d').date() if tgl_selesai_str else datetime.utcnow().date()
    except Exception:
        tgl_mulai = datetime.utcnow().date()
        tgl_selesai = datetime.utcnow().date()

    status = 'SELESAI' if persentase_selesai >= 100 else 'PROSES'

    act = AktivitasPegawai(
        pegawai_id=pegawai_id,
        kegiatan_id=kegiatan_id,
        judul_aktivitas=judul_aktivitas,
        deskripsi=deskripsi,
        tanggal_mulai=tgl_mulai,
        tanggal_selesai=tgl_selesai,
        persentase_selesai=persentase_selesai,
        status=status,
        created_by=current_user.id
    )
    db.session.add(act)
    db.session.commit()
    flash('Aktivitas pegawai berhasil dicatat.', 'success')
    return redirect(url_for('pegawai.aktivitas'))

@pegawai_bp.route('/monitoring')
@login_required
def monitoring():
    tim_list = db.session.query(Pegawai.tim_kerja).distinct().all()
    tim_names = [t[0] for t in tim_list if t[0]]
    pegawai_list = Pegawai.query.all()
    return render_template('pegawai/monitoring.html', tim_names=tim_names, pegawai_list=pegawai_list)

@pegawai_bp.route('/rekapitulasi')
@login_required
def rekapitulasi():
    pegawai_list = Pegawai.query.all()
    rekap = []
    for p in pegawai_list:
        acts = p.aktivitas.all()
        selesai = len([a for a in acts if a.status == 'SELESAI'])
        proses = len([a for a in acts if a.status == 'PROSES'])
        avg_pct = round(sum(a.persentase_selesai for a in acts) / len(acts), 1) if acts else 0
        rekap.append({
            'pegawai': p,
            'total_aktivitas': len(acts),
            'selesai': selesai,
            'proses': proses,
            'avg_pct': avg_pct
        })
    return render_template('pegawai/rekapitulasi.html', rekap=rekap)
