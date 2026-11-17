import io
import csv
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import func
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

    penugasan_terbaru = PenugasanMitra.query.order_by(PenugasanMitra.created_at.desc()).limit(8).all()
    kegiatan_aktif = Kegiatan.query.filter_by(status='BERJALAN').all()

    # Data untuk Chart.js: Distribusi Mitra per Kecamatan
    kec_data = db.session.query(Mitra.kecamatan, func.count(Mitra.id)).group_by(Mitra.kecamatan).all()
    chart_kec_labels = [k[0] for k in kec_data] if kec_data else ['Banyuwangi', 'Genteng', 'Rogojampi']
    chart_kec_values = [k[1] for k in kec_data] if kec_data else [1, 1, 1]

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
        rasio_selesai=rasio_selesai
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
        kecamatans=kecamatans
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
    writer.writerow(['id_sobat', 'nama_lengkap', 'email', 'alamat', 'no_hp', 'jenis_kelamin', 'desa', 'kecamatan', 'keahlian'])
    # Contoh data acuan BPS Banyuwangi
    writer.writerow(['35102025001', 'Ahmad Subandi', 'ahmad.subandi@gmail.com', 'Jl. Ahmad Yani No. 15 RT 01 RW 02', '081234567890', 'Laki-laki', 'Rogojampi', 'Rogojampi', 'Pendataan Lapangan (CAPI)'])
    writer.writerow(['35102025002', 'Siti Rahmawati', 'siti.rahma@gmail.com', 'Jl. Diponegoro No. 44 RT 02 RW 03', '081298765432', 'Perempuan', 'Genteng Wetan', 'Genteng', 'PML & Pengawasan'])
    writer.writerow(['35102025003', 'Budi Santoso', 'budi.santoso@gmail.com', 'Jl. Hayam Wuruk No. 8', '085712345678', 'Laki-laki', 'Mojopanggung', 'Giri', 'Pengolahan Data & Entri'])
    
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
            clean_row = {k.strip(): (v.strip() if v else '') for k, v in row.items() if k}
            id_sobat = clean_row.get('id_sobat')
            nama_lengkap = clean_row.get('nama_lengkap')
            if not id_sobat or not nama_lengkap:
                continue

            existing = Mitra.query.filter_by(id_sobat=id_sobat).first()
            if existing:
                existing.nama_lengkap = nama_lengkap
                if clean_row.get('email'): existing.email = clean_row.get('email')
                if clean_row.get('alamat'): existing.alamat = clean_row.get('alamat')
                if clean_row.get('no_hp'): existing.no_hp = clean_row.get('no_hp')
                if clean_row.get('jenis_kelamin'): existing.jenis_kelamin = clean_row.get('jenis_kelamin')
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
                    no_hp=clean_row.get('no_hp') or None,
                    jenis_kelamin=clean_row.get('jenis_kelamin') or 'Laki-laki',
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
    tahun_filter = request.args.get('tahun', '').strip()
    bulan_filter = request.args.get('bulan', '').strip()
    kegiatan_filter = request.args.get('kegiatan', '').strip()
    tim_filter = request.args.get('tim', '').strip()

    query = PenugasanMitra.query
    if status_filter:
        query = query.filter(PenugasanMitra.status == status_filter)
    if search_nama:
        query = query.join(PenugasanMitra.mitra).filter(Mitra.nama_lengkap.ilike(f'%{search_nama}%'))
    
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
        tahun_filter=tahun_filter,
        bulan_filter=bulan_filter,
        kegiatan_filter=kegiatan_filter,
        tim_filter=tim_filter,
        years=years
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
            'avg_score': avg_score,
            'predikat': predikat,
            'total_honor': total_honor
        })
    return render_template('mitra/rekapitulasi.html', rekap_data=rekap_data, total_honor_all=total_honor_all)

@mitra_bp.route('/template')
@login_required
def template():
    tim_filter = request.args.get('tim', '').strip()
    query = TemplateKegiatan.query
    if tim_filter and tim_filter != 'Semua':
        query = query.filter(TemplateKegiatan.tim_kerja == tim_filter)
    template_list = query.order_by(TemplateKegiatan.created_at.desc()).all()
    
    all_tpls = TemplateKegiatan.query.all()
    count_all = len(all_tpls)
    count_distribusi = len([t for t in all_tpls if t.tim_kerja == 'Tim Distribusi'])
    count_neraca = len([t for t in all_tpls if t.tim_kerja == 'Tim Neraca'])
    count_produksi = len([t for t in all_tpls if t.tim_kerja == 'Tim Produksi'])
    count_pls = len([t for t in all_tpls if t.tim_kerja == 'Tim PLS'])

    return render_template(
        'mitra/template.html', 
        template_list=template_list,
        tim_filter=tim_filter or 'Semua',
        count_all=count_all,
        count_distribusi=count_distribusi,
        count_neraca=count_neraca,
        count_produksi=count_produksi,
        count_pls=count_pls
    )

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
