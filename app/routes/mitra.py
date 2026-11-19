import io
import csv
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from app.models import (
    db, Kegiatan, TemplateKegiatan, Mitra, PenugasanMitra, EvaluasiMitra, Activity
)

mitra_bp = Blueprint('mitra', __name__, url_prefix='/mitra')

# 25 Kecamatan Resmi di Kabupaten Banyuwangi (Wilayah Kerja BPS 3510)
KECAMATAN_BANYUWANGI = [
    'Bangorejo', 'Banyuwangi', 'Blimbingsari', 'Cluring', 'Gambiran',
    'Genteng', 'Giri', 'Glagah', 'Glenmore', 'Kabat',
    'Kalibaru', 'Kalipuro', 'Licin', 'Muncar', 'Pesanggaran',
    'Purwoharjo', 'Rogojampi', 'Sempu', 'Siliragung', 'Singojuruh',
    'Songgon', 'Srono', 'Tegaldlimo', 'Tegalsari', 'Wongsorejo'
]

@mitra_bp.route('/')
@mitra_bp.route('/dashboard')
@login_required
def dashboard():
    total_mitra = Mitra.query.count()
    total_penugasan = PenugasanMitra.query.count()
    total_kegiatan = Kegiatan.query.count()
    penugasan_selesai = PenugasanMitra.query.filter_by(status='SELESAI').count()
    penugasan_proses = PenugasanMitra.query.filter_by(status='PROSES').count()

    penugasan_terbaru = PenugasanMitra.query.order_by(PenugasanMitra.created_at.desc()).limit(8).all()
    kegiatan_aktif = Kegiatan.query.filter_by(status='BERJALAN').all()

    # Data untuk Chart.js & Matriks: Sebaran Mitra per 25 Kecamatan Banyuwangi
    kec_data = db.session.query(Mitra.kecamatan, func.count(Mitra.id)).group_by(Mitra.kecamatan).all()
    kec_counts = dict(kec_data) if kec_data else {}
    
    sebaran_25_kecamatan = []
    for kec in KECAMATAN_BANYUWANGI:
        sebaran_25_kecamatan.append({
            'kecamatan': kec,
            'count': kec_counts.get(kec, 0)
        })

    active_kec = [(k, c) for k, c in kec_counts.items() if c > 0]
    if active_kec:
        chart_kec_labels = [k[0] for k in active_kec]
        chart_kec_values = [k[1] for k in active_kec]
    else:
        chart_kec_labels = ['Rogojampi', 'Genteng', 'Banyuwangi', 'Muncar', 'Giri', 'Kabat']
        chart_kec_values = [0, 0, 0, 0, 0, 0]

    # Data Performa & Skor Rata-rata
    eval_list = EvaluasiMitra.query.all()
    avg_score = round(sum(e.rata_rata for e in eval_list) / len(eval_list), 1) if eval_list else 0

    # Top Mitra
    top_eval = EvaluasiMitra.query.order_by(EvaluasiMitra.nilai_kualitas.desc()).limit(4).all()

    # Statistik per Tim Kerja BPS (Distribusi, Neraca, Produksi, PLS)
    all_kegiatans = Kegiatan.query.all()
    count_keg_distribusi = len([k for k in all_kegiatans if k.tim_kerja == 'Tim Distribusi'])
    count_keg_neraca = len([k for k in all_kegiatans if k.tim_kerja == 'Tim Neraca'])
    count_keg_produksi = len([k for k in all_kegiatans if k.tim_kerja == 'Tim Produksi'])
    count_keg_pls = len([k for k in all_kegiatans if k.tim_kerja == 'Tim PLS'])

    all_penugasan = PenugasanMitra.query.all()
    total_honor_all = sum(p.honor_total for p in all_penugasan)
    rasio_selesai = round((penugasan_selesai / total_penugasan * 100), 1) if total_penugasan > 0 else 0

    return render_template(
        'mitra/dashboard.html',
        total_mitra=total_mitra,
        total_penugasan=total_penugasan,
        total_kegiatan=total_kegiatan,
        penugasan_selesai=penugasan_selesai,
        penugasan_proses=penugasan_proses,
        penugasan_terbaru=penugasan_terbaru,
        kegiatan_aktif=kegiatan_aktif,
        chart_kec_labels=chart_kec_labels,
        chart_kec_values=chart_kec_values,
        avg_score=avg_score,
        top_eval=top_eval,
        count_keg_distribusi=count_keg_distribusi,
        count_keg_neraca=count_keg_neraca,
        count_keg_produksi=count_keg_produksi,
        count_keg_pls=count_keg_pls,
        total_honor_all=total_honor_all,
        rasio_selesai=rasio_selesai,
        kecamatan_options=KECAMATAN_BANYUWANGI,
        sebaran_25_kecamatan=sebaran_25_kecamatan
    )

@mitra_bp.route('/database')
@login_required
def database():
    search = request.args.get('search', '').strip()
    tahun_filter = request.args.get('tahun', '').strip()
    bulan_filter = request.args.get('bulan', '').strip()
    kegiatan_filter = request.args.get('kegiatan', '').strip()
    kec_filter = request.args.get('kecamatan', '').strip()
    jk_filter = request.args.get('jenis_kelamin', '').strip()

    query = Mitra.query

    # 1. Pencarian teks nama, ID Sobat, kontak, alamat, atau domisili
    if search:
        query = query.filter(
            (Mitra.nama_lengkap.ilike(f'%{search}%')) | 
            (Mitra.id_sobat.ilike(f'%{search}%')) | 
            (Mitra.kecamatan.ilike(f'%{search}%')) |
            (Mitra.desa.ilike(f'%{search}%')) |
            (Mitra.alamat.ilike(f'%{search}%')) |
            (Mitra.no_hp.ilike(f'%{search}%')) |
            (Mitra.email.ilike(f'%{search}%'))
        )

    # 2. Filter 3 Parameter Kegiatan: Tahun, Bulan, dan Kegiatan Sensus/Survei
    has_keg_filter = False
    keg_filters = []

    if tahun_filter and tahun_filter != 'Semua':
        try:
            keg_filters.append(Kegiatan.tahun == int(tahun_filter))
            has_keg_filter = True
        except ValueError:
            pass

    if bulan_filter and bulan_filter != 'Semua':
        keg_filters.append(
            (Kegiatan.bulan == bulan_filter) |
            (Kegiatan.tanggal_mulai.cast(db.String).ilike(f'%-{bulan_filter.zfill(2)}-%'))
        )
        has_keg_filter = True

    if kegiatan_filter and kegiatan_filter != 'Semua':
        keg_filters.append(
            (Kegiatan.nama_kegiatan.ilike(f'%{kegiatan_filter}%')) |
            (Kegiatan.kode_kegiatan.ilike(f'%{kegiatan_filter}%'))
        )
        has_keg_filter = True

    if has_keg_filter:
        query = query.join(Mitra.penugasan).join(PenugasanMitra.kegiatan).filter(*keg_filters).distinct()

    # 3. Filter Demografi (Opsional)
    if kec_filter:
        query = query.filter(Mitra.kecamatan == kec_filter)
    if jk_filter:
        query = query.filter(Mitra.jenis_kelamin == jk_filter)

    mitra_list = query.order_by(Mitra.nama_lengkap.asc()).all()

    # Data pendukung filter
    all_kegiatans = Kegiatan.query.all()
    years = sorted(list(set([k.tahun for k in all_kegiatans if k.tahun] + [2024, 2025, 2026])), reverse=True)
    kegiatan_options = Kegiatan.query.order_by(Kegiatan.nama_kegiatan.asc()).all()
    kecamatans = [k[0] for k in db.session.query(Mitra.kecamatan).distinct().all() if k[0]]

    months = [
        ('01', 'Januari'), ('02', 'Februari'), ('03', 'Maret'), ('04', 'April'),
        ('05', 'Mei'), ('06', 'Juni'), ('07', 'Juli'), ('08', 'Agustus'),
        ('09', 'September'), ('10', 'Oktober'), ('11', 'November'), ('12', 'Desember')
    ]

    return render_template(
        'mitra/database.html', 
        mitra_list=mitra_list, 
        search=search, 
        tahun_filter=tahun_filter,
        bulan_filter=bulan_filter,
        kegiatan_filter=kegiatan_filter,
        kec_filter=kec_filter, 
        jk_filter=jk_filter,
        years=years,
        months=months,
        kegiatan_options=kegiatan_options,
        kecamatans=kecamatans,
        kecamatan_options=KECAMATAN_BANYUWANGI
    )

@mitra_bp.route('/database/create', methods=['POST'])
@login_required
def create_mitra():
    id_sobat = request.form.get('id_sobat', '').strip()
    nama_lengkap = request.form.get('nama_lengkap', '').strip()
    email = request.form.get('email', '').strip()
    alamat = request.form.get('alamat', '').strip()
    no_hp = request.form.get('no_hp', '').strip()
    jenis_kelamin = request.form.get('jenis_kelamin', 'Laki-laki').strip()
    desa = request.form.get('desa', '').strip()
    kecamatan = request.form.get('kecamatan', '').strip()
    keahlian = request.form.get('keahlian', 'Pendataan Lapangan (CAPI)').strip()

    if not id_sobat or not nama_lengkap or not kecamatan:
        flash('ID Sobat, Nama Lengkap, dan Kecamatan wajib diisi.', 'danger')
        return redirect(url_for('mitra.database'))

    if Mitra.query.filter_by(id_sobat=id_sobat).first():
        flash(f'Mitra dengan ID Sobat {id_sobat} sudah terdaftar.', 'warning')
        return redirect(url_for('mitra.database'))

    mitra = Mitra(
        id_sobat=id_sobat,
        nama_lengkap=nama_lengkap,
        email=email or None,
        alamat=alamat or None,
        no_hp=no_hp or None,
        jenis_kelamin=jenis_kelamin,
        desa=desa or None,
        kecamatan=kecamatan,
        keahlian=keahlian
    )
    db.session.add(mitra)
    db.session.commit()
    flash(f'Mitra {nama_lengkap} (ID Sobat: {id_sobat}) berhasil ditambahkan.', 'success')
    return redirect(url_for('mitra.database'))

@mitra_bp.route('/database/template-download')
@login_required
def download_template_mitra():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id_sobat', 'nama', 'email', 'alamat', 'nomor_hp', 'jenis_kelamin', 'desa', 'kecamatan'])
    # Contoh data acuan BPS Banyuwangi
    writer.writerow(['35102025001', 'Ahmad Subandi', 'ahmad.subandi@gmail.com', 'Jl. Ahmad Yani No. 15 RT 01 RW 02', '081234567890', 'Laki-laki', 'Rogojampi', 'Rogojampi'])
    writer.writerow(['35102025002', 'Siti Rahmawati', 'siti.rahma@gmail.com', 'Jl. Diponegoro No. 44 RT 02 RW 03', '081298765432', 'Perempuan', 'Genteng Wetan', 'Genteng'])
    writer.writerow(['35102025003', 'Budi Santoso', 'budi.santoso@gmail.com', 'Jl. Hayam Wuruk No. 8', '085712345678', 'Laki-laki', 'Mojopanggung', 'Giri'])
    
    response = Response(output.getvalue().encode('utf-8-sig'), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=Template_Data_Master_Mitra_BPS.csv'
    return response

@mitra_bp.route('/database/import', methods=['POST'])
@login_required
def import_mitra():
    file = request.files.get('file')
    if not file or not file.filename:
        flash('Silakan pilih berkas CSV template yang akan diunggah.', 'warning')
        return redirect(url_for('mitra.database'))

    if not file.filename.lower().endswith('.csv'):
        flash('Format berkas harus berupa CSV.', 'danger')
        return redirect(url_for('mitra.database'))

    try:
        content = file.stream.read().decode('utf-8-sig')
        stream = io.StringIO(content, newline=None)
        reader = csv.DictReader(stream)
        success_count = 0
        updated_count = 0

        for row in reader:
            clean_row = {k.strip().lower(): (v.strip() if v else '') for k, v in row.items() if k}
            id_sobat = clean_row.get('id_sobat') or clean_row.get('id sobat')
            nama_lengkap = clean_row.get('nama') or clean_row.get('nama_lengkap') or clean_row.get('nama lengkap')
            nomor_hp = clean_row.get('nomor_hp') or clean_row.get('nomor hp') or clean_row.get('no_hp')
            jenis_kelamin = clean_row.get('jenis_kelamin') or clean_row.get('jenis kelamin')
            if not id_sobat or not nama_lengkap:
                continue

            existing = Mitra.query.filter_by(id_sobat=id_sobat).first()
            if existing:
                existing.nama_lengkap = nama_lengkap
                if clean_row.get('email'): existing.email = clean_row.get('email')
                if clean_row.get('alamat'): existing.alamat = clean_row.get('alamat')
                if nomor_hp: existing.no_hp = nomor_hp
                if jenis_kelamin: existing.jenis_kelamin = jenis_kelamin
                if clean_row.get('desa'): existing.desa = clean_row.get('desa')
                if clean_row.get('kecamatan'): existing.kecamatan = clean_row.get('kecamatan')
                if clean_row.get('keahlian'): existing.keahlian = clean_row.get('keahlian')
                updated_count += 1
            else:
                new_mitra = Mitra(
                    id_sobat=id_sobat,
                    nama_lengkap=nama_lengkap,
                    email=clean_row.get('email') or None,
                    alamat=clean_row.get('alamat') or None,
                    no_hp=nomor_hp or None,
                    jenis_kelamin=jenis_kelamin or 'Laki-laki',
                    desa=clean_row.get('desa') or None,
                    kecamatan=clean_row.get('kecamatan') or 'Banyuwangi',
                    keahlian=clean_row.get('keahlian') or 'Pendataan Lapangan (CAPI)'
                )
                db.session.add(new_mitra)
                success_count += 1

        db.session.commit()
        flash(f'Impor templat selesai: {success_count} data mitra baru ditambahkan, {updated_count} diperbarui.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal memproses berkas CSV: {str(e)}', 'danger')

    return redirect(url_for('mitra.database'))

@mitra_bp.route('/database/<int:id>/delete', methods=['POST'])
@login_required
def delete_mitra(id):
    mitra = Mitra.query.get_or_404(id)
    nama = mitra.nama_lengkap
    db.session.delete(mitra)
    db.session.commit()
    flash(f'Data mitra {nama} berhasil dihapus.', 'info')
    return redirect(url_for('mitra.database'))

@mitra_bp.route('/database/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_mitra_status(id):
    mitra = Mitra.query.get_or_404(id)
    mitra.status_aktif = not mitra.status_aktif
    db.session.commit()
    status_str = 'Aktif' if mitra.status_aktif else 'Nonaktif'
    flash(f'Status mitra {mitra.nama_lengkap} diubah menjadi {status_str}.', 'success')
    return redirect(url_for('mitra.database'))

@mitra_bp.route('/penugasan')
@login_required
def penugasan():
    status_filter = request.args.get('status', '').strip()
    search_nama = request.args.get('nama', '').strip()
    kec_filter = request.args.get('kecamatan', '').strip()
    tahun_filter = request.args.get('tahun', '').strip()
    bulan_filter = request.args.get('bulan', '').strip()
    kegiatan_filter = request.args.get('kegiatan', '').strip()
    tim_filter = request.args.get('tim', '').strip()

    query = PenugasanMitra.query
    if status_filter:
        query = query.filter(PenugasanMitra.status == status_filter)
    if search_nama or kec_filter:
        query = query.join(PenugasanMitra.mitra)
        if search_nama:
            query = query.filter(Mitra.nama_lengkap.ilike(f'%{search_nama}%'))
        if kec_filter:
            query = query.filter(Mitra.kecamatan == kec_filter)
    
    # Filter kegiatan properties
    if tahun_filter or bulan_filter or kegiatan_filter or tim_filter:
        query = query.join(PenugasanMitra.kegiatan)
        if tahun_filter and tahun_filter != 'Semua':
            try:
                query = query.filter(Kegiatan.tahun == int(tahun_filter))
            except ValueError:
                pass
        if bulan_filter and bulan_filter != 'Semua':
            query = query.filter(
                (Kegiatan.bulan == bulan_filter) |
                (Kegiatan.tanggal_mulai.cast(db.String).ilike(f'%-{bulan_filter.zfill(2)}-%'))
            )
        if kegiatan_filter:
            query = query.filter(
                (Kegiatan.nama_kegiatan.ilike(f'%{kegiatan_filter}%')) |
                (Kegiatan.kode_kegiatan.ilike(f'%{kegiatan_filter}%'))
            )
        if tim_filter and tim_filter != 'Semua':
            query = query.filter(Kegiatan.tim_kerja == tim_filter)

    penugasan_list = query.order_by(PenugasanMitra.created_at.desc()).all()
    mitra_options = Mitra.query.filter_by(status_aktif=True).order_by(Mitra.nama_lengkap.asc()).all()
    kegiatan_options = Kegiatan.query.order_by(Kegiatan.nama_kegiatan.asc()).all()
    
    all_kegiatans = Kegiatan.query.all()
    years = sorted(list(set([k.tahun for k in all_kegiatans if k.tahun] + [2024, 2025, 2026])), reverse=True)

    return render_template(
        'mitra/penugasan.html', 
        penugasan_list=penugasan_list, 
        mitra_options=mitra_options, 
        kegiatan_options=kegiatan_options, 
        status_filter=status_filter,
        search_nama=search_nama,
        kec_filter=kec_filter,
        tahun_filter=tahun_filter,
        bulan_filter=bulan_filter,
        kegiatan_filter=kegiatan_filter,
        tim_filter=tim_filter,
        years=years,
        kecamatan_options=KECAMATAN_BANYUWANGI
    )

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

@mitra_bp.route('/penugasan/<int:id>/update-progress', methods=['POST'])
@login_required
def update_penugasan_progress(id):
    p = PenugasanMitra.query.get_or_404(id)
    realisasi = request.form.get('realisasi_dokumen', type=int)
    if realisasi is not None:
        p.realisasi_dokumen = max(0, realisasi)
        if p.realisasi_dokumen >= p.target_dokumen:
            p.status = 'SELESAI'
        else:
            p.status = 'PROSES'
        db.session.commit()
        flash(f'Progres penugasan {p.mitra.nama_lengkap} diperbarui ({p.realisasi_dokumen}/{p.target_dokumen} dokumen).', 'success')
    return redirect(request.referrer or url_for('mitra.penugasan'))

@mitra_bp.route('/penugasan/<int:id>/delete', methods=['POST'])
@login_required
def delete_penugasan(id):
    p = PenugasanMitra.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash('Penugasan mitra berhasil dihapus.', 'info')
    return redirect(url_for('mitra.penugasan'))

@mitra_bp.route('/monitoring')
@login_required
def monitoring():
    tim_filter = request.args.get('tim', '').strip()
    tahun_filter = request.args.get('tahun', '').strip()
    bulan_filter = request.args.get('bulan', '').strip()
    kegiatan_filter = request.args.get('kegiatan', '').strip()

    query = Kegiatan.query

    # Filter Tim Kerja: Distribusi, Neraca, Produksi, PLS
    if tim_filter and tim_filter != 'Semua':
        query = query.filter(Kegiatan.tim_kerja == tim_filter)

    # 3 Tab / Filter Search Utama:
    # 1. Tahun
    if tahun_filter and tahun_filter != 'Semua':
        try:
            query = query.filter(Kegiatan.tahun == int(tahun_filter))
        except ValueError:
            pass

    # 2. Bulan
    if bulan_filter and bulan_filter != 'Semua':
        query = query.filter(
            (Kegiatan.bulan == bulan_filter) |
            (Kegiatan.tanggal_mulai.cast(db.String).ilike(f'%-{bulan_filter.zfill(2)}-%'))
        )

    # 3. Kegiatan (Nama Kegiatan atau Kode Kegiatan)
    if kegiatan_filter:
        query = query.filter(
            (Kegiatan.nama_kegiatan.ilike(f'%{kegiatan_filter}%')) |
            (Kegiatan.kode_kegiatan.ilike(f'%{kegiatan_filter}%'))
        )

    kegiatan_list = query.order_by(Kegiatan.tanggal_mulai.desc()).all()

    # Hitungan per Tim untuk Badge Tabs
    all_kegiatans = Kegiatan.query.all()
    count_all = len(all_kegiatans)
    count_distribusi = len([k for k in all_kegiatans if k.tim_kerja == 'Tim Distribusi'])
    count_neraca = len([k for k in all_kegiatans if k.tim_kerja == 'Tim Neraca'])
    count_produksi = len([k for k in all_kegiatans if k.tim_kerja == 'Tim Produksi'])
    count_pls = len([k for k in all_kegiatans if k.tim_kerja == 'Tim PLS'])

    # Daftar tahun yang tersedia
    years = sorted(list(set([k.tahun for k in all_kegiatans if k.tahun] + [2024, 2025, 2026])), reverse=True)

    return render_template(
        'mitra/monitoring.html',
        kegiatan_list=kegiatan_list,
        tim_filter=tim_filter or 'Semua',
        tahun_filter=tahun_filter,
        bulan_filter=bulan_filter,
        kegiatan_filter=kegiatan_filter,
        count_all=count_all,
        count_distribusi=count_distribusi,
        count_neraca=count_neraca,
        count_produksi=count_produksi,
        count_pls=count_pls,
        years=years
    )

@mitra_bp.route('/monitoring/create', methods=['POST'])
@login_required
def create_kegiatan():
    kode_kegiatan = request.form.get('kode_kegiatan', '').strip()
    nama_kegiatan = request.form.get('nama_kegiatan', '').strip()
    tim_kerja = request.form.get('tim_kerja', 'Tim Distribusi').strip()
    tahun = request.form.get('tahun', type=int) or datetime.utcnow().year
    bulan = request.form.get('bulan', '').strip()
    tanggal_mulai_raw = request.form.get('tanggal_mulai', '').strip()
    tanggal_selesai_raw = request.form.get('tanggal_selesai', '').strip()

    if not kode_kegiatan or not nama_kegiatan or not tanggal_mulai_raw or not tanggal_selesai_raw:
        flash('Kode, Nama Kegiatan, Tanggal Mulai dan Selesai wajib diisi.', 'danger')
        return redirect(url_for('mitra.monitoring'))

    try:
        tanggal_mulai = datetime.strptime(tanggal_mulai_raw, '%Y-%m-%d').date()
        tanggal_selesai = datetime.strptime(tanggal_selesai_raw, '%Y-%m-%d').date()
    except Exception:
        flash('Format tanggal tidak valid (gunakan format YYYY-MM-DD).', 'danger')
        return redirect(url_for('mitra.monitoring'))

    if Kegiatan.query.filter_by(kode_kegiatan=kode_kegiatan).first():
        flash(f'Kegiatan dengan kode {kode_kegiatan} sudah terdaftar.', 'warning')
        return redirect(url_for('mitra.monitoring'))

    keg = Kegiatan(
        kode_kegiatan=kode_kegiatan,
        nama_kegiatan=nama_kegiatan,
        tim_kerja=tim_kerja,
        tahun=tahun,
        bulan=bulan or None,
        tanggal_mulai=tanggal_mulai,
        tanggal_selesai=tanggal_selesai,
        penanggung_jawab_id=current_user.id
    )
    db.session.add(keg)
    db.session.commit()
    flash(f'Kegiatan {nama_kegiatan} ({tim_kerja}) berhasil ditambahkan.', 'success')
    return redirect(url_for('mitra.monitoring'))

@mitra_bp.route('/monitoring/<int:kegiatan_id>')
@login_required
def monitoring_detail(kegiatan_id):
    kegiatan = Kegiatan.query.get_or_404(kegiatan_id)
    penugasans = kegiatan.penugasan_mitra.order_by(PenugasanMitra.created_at.desc()).all()
    aktivitass = kegiatan.aktivitas_pegawai or []
    pengajuans = kegiatan.pengajuan_anggaran or []
    komponens = kegiatan.komponen_anggaran or []

    # Ringkasan 360
    total_target_dok = sum(p.target_dokumen for p in penugasans)
    total_real_dok = sum(p.realisasi_dokumen for p in penugasans)
    progres_dokumen = round((total_real_dok / total_target_dok * 100), 1) if total_target_dok > 0 else 0

    total_honor_mitra = sum(p.honor_total for p in penugasans)
    pegawai_terlibat = len(set(a.pegawai_id for a in aktivitass if a.pegawai_id))
    progres_aktivitas = round(sum(a.persentase_selesai for a in aktivitass) / len(aktivitass), 1) if aktivitass else 0

    total_anggaran_diajukan = sum(p.jumlah_diajukan for p in pengajuans)
    total_anggaran_cair = sum(p.realisasi.jumlah_realisasi for p in pengajuans if p.realisasi)

    return render_template(
        'mitra/monitoring_detail.html',
        kegiatan=kegiatan,
        penugasans=penugasans,
        aktivitass=aktivitass,
        pengajuans=pengajuans,
        komponens=komponens,
        total_target_dok=total_target_dok,
        total_real_dok=total_real_dok,
        progres_dokumen=progres_dokumen,
        total_honor_mitra=total_honor_mitra,
        pegawai_terlibat=pegawai_terlibat,
        progres_aktivitas=progres_aktivitas,
        total_anggaran_diajukan=total_anggaran_diajukan,
        total_anggaran_cair=total_anggaran_cair
    )

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
    total_honor_all = 0
    for m in mitra_list:
        penugasan_all = m.penugasan.all()
        eval_all = m.evaluasi_list.all()
        avg_score = round(sum(e.rata_rata for e in eval_all) / len(eval_all), 1) if eval_all else 0
        total_honor = sum(p.honor_total for p in penugasan_all)
        total_honor_all += total_honor

        tugas_selesai = sum(1 for p in penugasan_all if (p.status or '').upper() == 'SELESAI')
        tugas_berjalan = len(penugasan_all) - tugas_selesai
        tim_list = sorted({p.kegiatan.tim_kerja for p in penugasan_all if p.kegiatan and p.kegiatan.tim_kerja})
        kegiatan_list_mitra = []
        seen_keg = set()
        for p in penugasan_all:
            if p.kegiatan and p.kegiatan.nama_kegiatan and p.kegiatan.nama_kegiatan not in seen_keg:
                seen_keg.add(p.kegiatan.nama_kegiatan)
                kegiatan_list_mitra.append(p.kegiatan.nama_kegiatan)

        # Predikat
        if avg_score >= 90:
            predikat = "Sangat Baik (A)"
        elif avg_score >= 80:
            predikat = "Baik (B)"
        elif avg_score >= 70:
            predikat = "Cukup (C)"
        elif avg_score > 0:
            predikat = "Kurang (D)"
        else:
            predikat = "Belum Dinilai"

        rekap_data.append({
            'mitra': m,
            'total_tugas': len(penugasan_all),
            'tugas_selesai': tugas_selesai,
            'tugas_berjalan': tugas_berjalan,
            'tim_list': tim_list,
            'kegiatan_list': kegiatan_list_mitra,
            'jumlah_eval': len(eval_all),
            'avg_score': avg_score,
            'predikat': predikat,
            'total_honor': total_honor
        })

    # Rekapitulasi Sebaran per 25 Kecamatan Kabupaten Banyuwangi
    rekap_25_kecamatan = []
    for kec in KECAMATAN_BANYUWANGI:
        mitras_kec = Mitra.query.filter_by(kecamatan=kec).all()
        tot_mitra_kec = len(mitras_kec)
        mitra_ids = [m.id for m in mitras_kec]
        if mitra_ids:
            tot_tugas_kec = PenugasanMitra.query.filter(PenugasanMitra.mitra_id.in_(mitra_ids)).count()
            tot_honor_kec = sum(p.honor_total for p in PenugasanMitra.query.filter(PenugasanMitra.mitra_id.in_(mitra_ids)).all())
        else:
            tot_tugas_kec = 0
            tot_honor_kec = 0
        rekap_25_kecamatan.append({
            'kecamatan': kec,
            'total_mitra': tot_mitra_kec,
            'total_tugas': tot_tugas_kec,
            'total_honor': tot_honor_kec
        })

    # Rekapitulasi per 4 Tim Kerja Teknis BPS (selaras dengan Daftar Kegiatan & Penugasan Mitra)
    tim_meta = [
        ('Tim Distribusi', 'SHPB, VHTS, Transportasi & Jasa', 'truck'),
        ('Tim Neraca', 'PDRB, SKLNP, SKPS & Analisis Makro', 'scale'),
        ('Tim Produksi', 'KSA Padi/Jagung, Ubinan & Pertanian', 'sprout'),
        ('Tim PLS', 'Pengolahan Data, TI & Wilkerstat', 'database'),
    ]
    rekap_tim_kerja = []
    for tim_nama, tim_desc, tim_icon in tim_meta:
        keg_tim = Kegiatan.query.filter_by(tim_kerja=tim_nama).all()
        keg_ids = [k.id for k in keg_tim]
        if keg_ids:
            tugas_tim = PenugasanMitra.query.filter(PenugasanMitra.kegiatan_id.in_(keg_ids)).all()
            tot_tugas_tim = len(tugas_tim)
            tot_honor_tim = sum(p.honor_total for p in tugas_tim)
        else:
            tot_tugas_tim = 0
            tot_honor_tim = 0
        rekap_tim_kerja.append({
            'nama': tim_nama,
            'desc': tim_desc,
            'icon': tim_icon,
            'total_kegiatan': len(keg_tim),
            'total_tugas': tot_tugas_tim,
            'total_honor': tot_honor_tim
        })

    total_kegiatan = Kegiatan.query.count()
    total_penugasan = PenugasanMitra.query.count()

    return render_template(
        'mitra/rekapitulasi.html', 
        rekap_data=rekap_data, 
        total_honor_all=total_honor_all,
        rekap_tim_kerja=rekap_tim_kerja,
        total_kegiatan=total_kegiatan,
        total_penugasan=total_penugasan,
        rekap_25_kecamatan=rekap_25_kecamatan,
        kecamatan_options=KECAMATAN_BANYUWANGI
    )

@mitra_bp.route('/template')
@login_required
def template():
    tim_filter = request.args.get('tim', '').strip()
    active_tab = request.args.get('tab', 'kegiatan').strip()

    # Query Template Kegiatan (SBU)
    query_tpl = TemplateKegiatan.query
    if tim_filter and tim_filter != 'Semua':
        query_tpl = query_tpl.filter(TemplateKegiatan.tim_kerja == tim_filter)
    template_list = query_tpl.order_by(TemplateKegiatan.created_at.desc()).all()
    
    all_tpls = TemplateKegiatan.query.all()
    count_all = len(all_tpls)
    count_distribusi = len([t for t in all_tpls if t.tim_kerja == 'Tim Distribusi'])
    count_neraca = len([t for t in all_tpls if t.tim_kerja == 'Tim Neraca'])
    count_produksi = len([t for t in all_tpls if t.tim_kerja == 'Tim Produksi'])
    count_pls = len([t for t in all_tpls if t.tim_kerja == 'Tim PLS'])

    # Query Kegiatan untuk Tampilan Hasil Unggahan Otomatis
    query_keg = Kegiatan.query
    if tim_filter and tim_filter != 'Semua':
        query_keg = query_keg.filter(Kegiatan.tim_kerja == tim_filter)
    kegiatan_list = query_keg.order_by(Kegiatan.created_at.desc()).all()
    total_kegiatan = Kegiatan.query.count()

    # Query Mitra untuk Tab Mitra (tampilkan hingga 500 agar semua hasil upload terlihat & bisa dicari)
    mitra_list = Mitra.query.order_by(Mitra.id.asc()).limit(500).all()
    total_mitra = Mitra.query.count()

    return render_template(
        'mitra/template.html', 
        template_list=template_list,
        kegiatan_list=kegiatan_list,
        mitra_list=mitra_list,
        total_kegiatan=total_kegiatan,
        total_mitra=total_mitra,
        active_tab=active_tab,
        tim_filter=tim_filter or 'Semua',
        count_all=count_all,
        count_distribusi=count_distribusi,
        count_neraca=count_neraca,
        count_produksi=count_produksi,
        count_pls=count_pls
    )

@mitra_bp.route('/template/download-kegiatan')
@login_required
def download_template_kegiatan():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['nama_kegiatan', 'tim_kerja', 'tahun', 'bulan', 'tanggal_mulai', 'tanggal_selesai'])
    writer.writerow(['Survei Harga Perdagangan Besar (SHPB)', 'Tim Distribusi', '2025', 'Januari', '2025-01-05', '2025-01-31'])
    writer.writerow(['Survei Khusus Lembaga Non-Profit (SKLNP)', 'Tim Neraca', '2025', 'Januari', '2025-01-10', '2025-02-15'])
    writer.writerow(['Kerangka Sampel Area (KSA) Padi Subround 1', 'Tim Produksi', '2025', 'Februari', '2025-02-01', '2025-02-28'])
    writer.writerow(['Pemutakhiran Wilkerstat & Geotagging SLS', 'Tim PLS', '2025', 'Februari', '2025-02-10', '2025-03-15'])
    
    response = Response(output.getvalue().encode('utf-8-sig'), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=Template_Kegiatan_Sensus_Survei_BPS.csv'
    return response

@mitra_bp.route('/template/upload-kegiatan', methods=['POST'])
@login_required
def upload_kegiatan():
    file = request.files.get('file')
    if not file or not file.filename:
        flash('Silakan pilih berkas CSV kegiatan yang ingin diunggah.', 'warning')
        return redirect(url_for('mitra.template', tab='kegiatan'))

    if not (file.filename.lower().endswith('.csv') or file.filename.lower().endswith('.txt')):
        flash('Format berkas harus berupa CSV.', 'danger')
        return redirect(url_for('mitra.template', tab='kegiatan'))

    try:
        raw_bytes = file.stream.read()
        for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
            try:
                content = raw_bytes.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            content = raw_bytes.decode('utf-8', errors='ignore')

        first_line = content.splitlines()[0] if content.splitlines() else ''
        delimiter = ';' if ';' in first_line and ',' not in first_line else ','

        stream = io.StringIO(content, newline=None)
        reader = csv.DictReader(stream, delimiter=delimiter)
        
        success_count = 0
        updated_count = 0

        for row in reader:
            clean_row = {k.strip().lower(): (v.strip() if v else '') for k, v in row.items() if k}
            
            kode_kegiatan = clean_row.get('kode_kegiatan') or clean_row.get('kode') or clean_row.get('id')
            nama_kegiatan = clean_row.get('nama_kegiatan') or clean_row.get('nama kegiatan') or clean_row.get('nama') or clean_row.get('kegiatan')
            
            if not nama_kegiatan:
                continue

            # Normalisasi Tim Kerja
            tim_input = clean_row.get('tim_kerja') or clean_row.get('tim kerja') or clean_row.get('tim') or 'Tim Distribusi'
            tim_upper = tim_input.upper()
            if 'NERACA' in tim_upper:
                tim_kerja = 'Tim Neraca'
            elif 'PRODUKSI' in tim_upper or 'PERTANIAN' in tim_upper:
                tim_kerja = 'Tim Produksi'
            elif 'PLS' in tim_upper or 'PENGOLAHAN' in tim_upper or 'TI' in tim_upper:
                tim_kerja = 'Tim PLS'
            else:
                tim_kerja = 'Tim Distribusi'

            tahun_str = clean_row.get('tahun')
            try:
                tahun = int(tahun_str) if tahun_str else datetime.utcnow().year
            except ValueError:
                tahun = datetime.utcnow().year

            bulan = clean_row.get('bulan') or '01'

            def parse_date(date_str, fallback):
                if not date_str:
                    return fallback
                for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d'):
                    try:
                        return datetime.strptime(date_str, fmt).date()
                    except ValueError:
                        pass
                return fallback

            today = datetime.utcnow().date()
            tanggal_mulai = parse_date(clean_row.get('tanggal_mulai') or clean_row.get('tanggal mulai'), today)
            tanggal_selesai = parse_date(clean_row.get('tanggal_selesai') or clean_row.get('tanggal selesai'), today + timedelta(days=30))

            if kode_kegiatan:
                existing = Kegiatan.query.filter_by(kode_kegiatan=kode_kegiatan).first()
            else:
                existing = Kegiatan.query.filter_by(nama_kegiatan=nama_kegiatan, tahun=tahun).first()
                if not existing:
                    prefix_map = {
                        'Tim Distribusi': 'DIS',
                        'Tim Neraca': 'NER',
                        'Tim Produksi': 'PRD',
                        'Tim PLS': 'PLS'
                    }
                    pfx = prefix_map.get(tim_kerja, 'KEG')
                    seq = Kegiatan.query.count() + success_count + 1
                    kode_kegiatan = f"KEG-{pfx}-{tahun}-{seq:03d}"
                    while Kegiatan.query.filter_by(kode_kegiatan=kode_kegiatan).first():
                        seq += 1
                        kode_kegiatan = f"KEG-{pfx}-{tahun}-{seq:03d}"

            if existing:
                existing.nama_kegiatan = nama_kegiatan
                existing.tim_kerja = tim_kerja
                existing.tahun = tahun
                existing.bulan = bulan
                existing.tanggal_mulai = tanggal_mulai
                existing.tanggal_selesai = tanggal_selesai
                updated_count += 1
            else:
                new_keg = Kegiatan(
                    kode_kegiatan=kode_kegiatan,
                    nama_kegiatan=nama_kegiatan,
                    tim_kerja=tim_kerja,
                    tahun=tahun,
                    bulan=bulan,
                    tanggal_mulai=tanggal_mulai,
                    tanggal_selesai=tanggal_selesai,
                    penanggung_jawab_id=current_user.id
                )
                db.session.add(new_keg)
                success_count += 1

        db.session.commit()
        flash(f'Unggah template berhasil! {success_count} kegiatan baru otomatis ditambahkan, {updated_count} diperbarui.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal mengimpor berkas template: {str(e)}', 'danger')

    return redirect(url_for('mitra.template', tab='kegiatan'))

@mitra_bp.route('/template/upload-mitra', methods=['POST'])
@login_required
def upload_mitra_from_template():
    file = request.files.get('file')
    if not file or not file.filename:
        flash('Silakan pilih berkas CSV template mitra yang akan diunggah.', 'warning')
        return redirect(url_for('mitra.template', tab='mitra'))

    if not file.filename.lower().endswith('.csv'):
        flash('Format berkas harus berupa CSV.', 'danger')
        return redirect(url_for('mitra.template', tab='mitra'))

    try:
        content = file.stream.read().decode('utf-8-sig')
        stream = io.StringIO(content, newline=None)
        reader = csv.DictReader(stream)
        success_count = 0
        updated_count = 0

        for row in reader:
            clean_row = {k.strip().lower(): (v.strip() if v else '') for k, v in row.items() if k}
            id_sobat = clean_row.get('id_sobat') or clean_row.get('id sobat')
            nama_lengkap = clean_row.get('nama') or clean_row.get('nama_lengkap') or clean_row.get('nama lengkap')
            nomor_hp = clean_row.get('nomor_hp') or clean_row.get('nomor hp') or clean_row.get('no_hp')
            jenis_kelamin = clean_row.get('jenis_kelamin') or clean_row.get('jenis kelamin')
            if not id_sobat or not nama_lengkap:
                continue

            existing = Mitra.query.filter_by(id_sobat=id_sobat).first()
            if existing:
                existing.nama_lengkap = nama_lengkap
                if clean_row.get('email'): existing.email = clean_row.get('email')
                if clean_row.get('alamat'): existing.alamat = clean_row.get('alamat')
                if nomor_hp: existing.no_hp = nomor_hp
                if jenis_kelamin: existing.jenis_kelamin = jenis_kelamin
                if clean_row.get('desa'): existing.desa = clean_row.get('desa')
                if clean_row.get('kecamatan'): existing.kecamatan = clean_row.get('kecamatan')
                if clean_row.get('keahlian'): existing.keahlian = clean_row.get('keahlian')
                updated_count += 1
            else:
                new_mitra = Mitra(
                    id_sobat=id_sobat,
                    nama_lengkap=nama_lengkap,
                    email=clean_row.get('email') or None,
                    alamat=clean_row.get('alamat') or None,
                    no_hp=nomor_hp or None,
                    jenis_kelamin=jenis_kelamin or 'Laki-laki',
                    desa=clean_row.get('desa') or None,
                    kecamatan=clean_row.get('kecamatan') or 'Banyuwangi',
                    keahlian=clean_row.get('keahlian') or 'Pendataan Lapangan (CAPI)'
                )
                db.session.add(new_mitra)
                success_count += 1

        db.session.commit()
        flash(f'Unggah template mitra selesai: {success_count} data mitra baru otomatis ditambahkan, {updated_count} diperbarui.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal mengimpor berkas template mitra: {str(e)}', 'danger')

    return redirect(url_for('mitra.template', tab='mitra'))

@mitra_bp.route('/template/create', methods=['POST'])
@login_required
def create_template():
    nama_template = request.form.get('nama_template')
    jenis_survei = request.form.get('jenis_survei')
    tim_kerja = request.form.get('tim_kerja', 'Tim Distribusi')
    honor_standar = request.form.get('honor_standar', 0, type=int)
    deskripsi = request.form.get('deskripsi', '')

    item = TemplateKegiatan(
        nama_template=nama_template,
        jenis_survei=jenis_survei,
        tim_kerja=tim_kerja,
        honor_standar=honor_standar,
        deskripsi=deskripsi
    )
    db.session.add(item)
    db.session.commit()
    flash(f'Template kegiatan {nama_template} ({tim_kerja}) berhasil ditambahkan.', 'success')
    return redirect(url_for('mitra.template'))


@mitra_bp.route('/api/ephemeral-sync', methods=['GET', 'POST'])
@login_required
def ephemeral_sync():
    """Snapshot & auto-restore data Monitoring Mitra agar tidak hilang saat refresh/pindah fitur di Vercel tanpa DB permanen."""
    if request.method == 'GET':
        mitras = [
            {
                'id_sobat': m.id_sobat,
                'nama_lengkap': m.nama_lengkap,
                'email': m.email or '',
                'alamat': m.alamat or '',
                'no_hp': m.no_hp or '',
                'jenis_kelamin': m.jenis_kelamin or 'Laki-laki',
                'desa': m.desa or '',
                'kecamatan': m.kecamatan or 'Banyuwangi',
                'keahlian': m.keahlian or 'Pendataan Lapangan (CAPI)',
                'status_aktif': bool(m.status_aktif),
            }
            for m in Mitra.query.order_by(Mitra.id.asc()).all()
        ]
        kegiatans = [
            {
                'kode_kegiatan': k.kode_kegiatan,
                'nama_kegiatan': k.nama_kegiatan,
                'tim_kerja': k.tim_kerja or 'Tim Distribusi',
                'tahun': k.tahun or 2025,
                'bulan': k.bulan or 'Januari',
                'tanggal_mulai': k.tanggal_mulai.isoformat() if k.tanggal_mulai else '',
                'tanggal_selesai': k.tanggal_selesai.isoformat() if k.tanggal_selesai else '',
                'status': k.status or 'BERJALAN',
            }
            for k in Kegiatan.query.order_by(Kegiatan.id.asc()).all()
        ]
        penugasans = [
            {
                'id_sobat': p.mitra.id_sobat,
                'kode_kegiatan': p.kegiatan.kode_kegiatan,
                'peran': p.peran or 'PPL',
                'target_unit': p.target_unit or 0,
                'realisasi_unit': p.realisasi_unit or 0,
                'honor_satuan': p.honor_satuan or 0,
                'honor_total': p.honor_total or 0,
                'status': p.status or 'DITUGASKAN',
            }
            for p in PenugasanMitra.query.all() if p.mitra and p.kegiatan
        ]
        return jsonify({
            'ok': True,
            'mitra': mitras,
            'kegiatan': kegiatans,
            'penugasan': penugasans,
        })

    # POST: Restore snapshot idempotently
    payload = request.get_json(silent=True) or {}
    restored_mitra = 0
    restored_kegiatan = 0
    restored_penugasan = 0

    try:
        for item in payload.get('mitra', []):
            id_sobat = (item.get('id_sobat') or '').strip()
            nama = (item.get('nama_lengkap') or '').strip()
            if not id_sobat or not nama:
                continue
            if not Mitra.query.filter_by(id_sobat=id_sobat).first():
                db.session.add(Mitra(
                    id_sobat=id_sobat,
                    nama_lengkap=nama,
                    email=item.get('email') or None,
                    alamat=item.get('alamat') or None,
                    no_hp=item.get('no_hp') or None,
                    jenis_kelamin=item.get('jenis_kelamin') or 'Laki-laki',
                    desa=item.get('desa') or None,
                    kecamatan=item.get('kecamatan') or 'Banyuwangi',
                    keahlian=item.get('keahlian') or 'Pendataan Lapangan (CAPI)',
                    status_aktif=item.get('status_aktif', True),
                ))
                restored_mitra += 1

        today = datetime.utcnow().date()
        for item in payload.get('kegiatan', []):
            kode = (item.get('kode_kegiatan') or '').strip()
            nama = (item.get('nama_kegiatan') or '').strip()
            if not kode or not nama:
                continue
            if not Kegiatan.query.filter_by(kode_kegiatan=kode).first():
                try:
                    t_mulai = datetime.strptime(item.get('tanggal_mulai', ''), '%Y-%m-%d').date() if item.get('tanggal_mulai') else today
                except ValueError:
                    t_mulai = today
                try:
                    t_selesai = datetime.strptime(item.get('tanggal_selesai', ''), '%Y-%m-%d').date() if item.get('tanggal_selesai') else today + timedelta(days=30)
                except ValueError:
                    t_selesai = today + timedelta(days=30)
                db.session.add(Kegiatan(
                    kode_kegiatan=kode,
                    nama_kegiatan=nama,
                    tim_kerja=item.get('tim_kerja') or 'Tim Distribusi',
                    tahun=int(item.get('tahun') or today.year),
                    bulan=item.get('bulan') or 'Januari',
                    tanggal_mulai=t_mulai,
                    tanggal_selesai=t_selesai,
                    status=item.get('status') or 'BERJALAN',
                    penanggung_jawab_id=current_user.id,
                ))
                restored_kegiatan += 1

        db.session.flush()

        for item in payload.get('penugasan', []):
            m = Mitra.query.filter_by(id_sobat=item.get('id_sobat')).first()
            k = Kegiatan.query.filter_by(kode_kegiatan=item.get('kode_kegiatan')).first()
            if m and k and not PenugasanMitra.query.filter_by(mitra_id=m.id, kegiatan_id=k.id).first():
                db.session.add(PenugasanMitra(
                    mitra_id=m.id,
                    kegiatan_id=k.id,
                    peran=item.get('peran') or 'PPL',
                    target_unit=int(item.get('target_unit') or 0),
                    realisasi_unit=int(item.get('realisasi_unit') or 0),
                    honor_satuan=int(item.get('honor_satuan') or 0),
                    honor_total=int(item.get('honor_total') or 0),
                    status=item.get('status') or 'DITUGASKAN',
                ))
                restored_penugasan += 1

        db.session.commit()
        return jsonify({
            'ok': True,
            'restored_mitra': restored_mitra,
            'restored_kegiatan': restored_kegiatan,
            'restored_penugasan': restored_penugasan,
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'ok': False, 'error': str(e)}), 500
