from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app.models import (
    db, Kegiatan, TemplateKegiatan, Mitra, PenugasanMitra, EvaluasiMitra, Activity
)

mitra_bp = Blueprint('mitra', __name__, url_prefix='/mitra')

@mitra_bp.route('/')
@mitra_bp.route('/dashboard')
@login_required
def dashboard():
    total_mitra = Mitra.query.count()
    total_penugasan = PenugasanMitra.query.count()
    total_kegiatan = Kegiatan.query.count()
    penugasan_selesai = PenugasanMitra.query.filter_by(status='SELESAI').count()
    penugasan_proses = PenugasanMitra.query.filter_by(status='PROSES').count()

    penugasan_terbaru = PenugasanMitra.query.order_by(PenugasanMitra.created_at.desc()).limit(7).all()
    kegiatan_aktif = Kegiatan.query.filter_by(status='BERJALAN').all()

    return render_template(
        'mitra/dashboard.html',
        total_mitra=total_mitra,
        total_penugasan=total_penugasan,
        total_kegiatan=total_kegiatan,
        penugasan_selesai=penugasan_selesai,
        penugasan_proses=penugasan_proses,
        penugasan_terbaru=penugasan_terbaru,
        kegiatan_aktif=kegiatan_aktif
    )

@mitra_bp.route('/database')
@login_required
def database():
    search = request.args.get('search', '').strip()
    query = Mitra.query
    if search:
        query = query.filter((Mitra.nama_lengkap.ilike(f'%{search}%')) | (Mitra.id_sobat.ilike(f'%{search}%')) | (Mitra.kecamatan.ilike(f'%{search}%')))
    mitra_list = query.order_by(Mitra.nama_lengkap.asc()).all()
    return render_template('mitra/database.html', mitra_list=mitra_list, search=search)

@mitra_bp.route('/database/create', methods=['POST'])
@login_required
def create_mitra():
    id_sobat = request.form.get('id_sobat')
    nama_lengkap = request.form.get('nama_lengkap')
    kecamatan = request.form.get('kecamatan')
    no_hp = request.form.get('no_hp')
    email = request.form.get('email')
    keahlian = request.form.get('keahlian', 'Pendataan Lapangan (CAPI)')

    if not id_sobat or not nama_lengkap:
        flash('ID Sobat dan Nama Lengkap wajib diisi.', 'danger')
        return redirect(url_for('mitra.database'))

    if Mitra.query.filter_by(id_sobat=id_sobat).first():
        flash(f'Mitra dengan ID Sobat {id_sobat} sudah terdaftar.', 'warning')
        return redirect(url_for('mitra.database'))

    mitra = Mitra(
        id_sobat=id_sobat,
        nama_lengkap=nama_lengkap,
        kecamatan=kecamatan,
        no_hp=no_hp,
        email=email,
        keahlian=keahlian
    )
    db.session.add(mitra)
    db.session.commit()
    flash(f'Mitra {nama_lengkap} berhasil ditambahkan.', 'success')
    return redirect(url_for('mitra.database'))

@mitra_bp.route('/penugasan')
@login_required
def penugasan():
    penugasan_list = PenugasanMitra.query.order_by(PenugasanMitra.created_at.desc()).all()
    mitra_options = Mitra.query.filter_by(status_aktif=True).order_by(Mitra.nama_lengkap.asc()).all()
    kegiatan_options = Kegiatan.query.order_by(Kegiatan.nama_kegiatan.asc()).all()
    return render_template('mitra/penugasan.html', penugasan_list=penugasan_list, mitra_options=mitra_options, kegiatan_options=kegiatan_options)

@mitra_bp.route('/penugasan/create', methods=['POST'])
@login_required
def create_penugasan():
    mitra_id = request.form.get('mitra_id', type=int)
    kegiatan_id = request.form.get('kegiatan_id', type=int)
    peran = request.form.get('peran', 'PPL')
    target_dokumen = request.form.get('target_dokumen', 10, type=int)
    honor_total = request.form.get('honor_total', 0, type=int)

    if not mitra_id or not kegiatan_id:
        flash('Mitra dan Kegiatan wajib dipilih.', 'danger')
        return redirect(url_for('mitra.penugasan'))

    penugasan_item = PenugasanMitra(
        mitra_id=mitra_id,
        kegiatan_id=kegiatan_id,
        peran=peran,
        target_dokumen=target_dokumen,
        honor_total=honor_total,
        created_by=current_user.id
    )
    db.session.add(penugasan_item)
    db.session.commit()
    flash('Penugasan mitra berhasil dibuat.', 'success')
    return redirect(url_for('mitra.penugasan'))

@mitra_bp.route('/monitoring')
@login_required
def monitoring():
    kegiatan_list = Kegiatan.query.order_by(Kegiatan.tanggal_mulai.desc()).all()
    return render_template('mitra/monitoring.html', kegiatan_list=kegiatan_list)

@mitra_bp.route('/evaluasi')
@login_required
def evaluasi():
    evaluasi_list = EvaluasiMitra.query.order_by(EvaluasiMitra.created_at.desc()).all()
    penugasan_belum_eval = PenugasanMitra.query.filter(~PenugasanMitra.evaluasi.has()).all()
    return render_template('mitra/evaluasi.html', evaluasi_list=evaluasi_list, penugasan_belum_eval=penugasan_belum_eval)

@mitra_bp.route('/evaluasi/create', methods=['POST'])
@login_required
def create_evaluasi():
    penugasan_id = request.form.get('penugasan_id', type=int)
    nilai_kualitas = request.form.get('nilai_kualitas', 85, type=int)
    nilai_ketepatan = request.form.get('nilai_ketepatan', 85, type=int)
    nilai_kerjasama = request.form.get('nilai_kerjasama', 85, type=int)
    catatan = request.form.get('catatan', '')

    penugasan = PenugasanMitra.query.get_or_404(penugasan_id)
    eval_item = EvaluasiMitra(
        penugasan_id=penugasan.id,
        mitra_id=penugasan.mitra_id,
        nilai_kualitas=nilai_kualitas,
        nilai_ketepatan=nilai_ketepatan,
        nilai_kerjasama=nilai_kerjasama,
        catatan=catatan,
        evaluator_id=current_user.id
    )
    penugasan.status = 'SELESAI'
    db.session.add(eval_item)
    db.session.commit()
    flash('Evaluasi mitra berhasil disimpan.', 'success')
    return redirect(url_for('mitra.evaluasi'))

@mitra_bp.route('/rekapitulasi')
@login_required
def rekapitulasi():
    mitra_list = Mitra.query.all()
    rekap_data = []
    for m in mitra_list:
        penugasan_all = m.penugasan.all()
        eval_all = m.evaluasi_list.all()
        avg_score = round(sum(e.rata_rata for e in eval_all) / len(eval_all), 1) if eval_all else 0
        total_honor = sum(p.honor_total for p in penugasan_all)
        rekap_data.append({
            'mitra': m,
            'total_tugas': len(penugasan_all),
            'avg_score': avg_score,
            'total_honor': total_honor
        })
    return render_template('mitra/rekapitulasi.html', rekap_data=rekap_data)

@mitra_bp.route('/template')
@login_required
def template():
    template_list = TemplateKegiatan.query.order_by(TemplateKegiatan.created_at.desc()).all()
    return render_template('mitra/template.html', template_list=template_list)

@mitra_bp.route('/template/create', methods=['POST'])
@login_required
def create_template():
    nama_template = request.form.get('nama_template')
    jenis_survei = request.form.get('jenis_survei')
    honor_standar = request.form.get('honor_standar', 0, type=int)
    deskripsi = request.form.get('deskripsi', '')

    item = TemplateKegiatan(
        nama_template=nama_template,
        jenis_survei=jenis_survei,
        honor_standar=honor_standar,
        deskripsi=deskripsi
    )
    db.session.add(item)
    db.session.commit()
    flash('Template kegiatan berhasil ditambahkan.', 'success')
    return redirect(url_for('mitra.template'))
