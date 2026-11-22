import io
import csv
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, Response, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
from app.models import (
    db, User, Category, ImportantLink, Document,
    Kegiatan, Mitra, PenugasanMitra, EvaluasiMitra,
    Pegawai, AktivitasPegawai, AkunAnggaran, KomponenAnggaran,
    PengajuanAnggaran, PersetujuanAnggaran, RealisasiAnggaran
)
from app.routes.mitra import KECAMATAN_BANYUWANGI, ephemeral_sync as _mitra_ephemeral_sync

api_v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')


@api_v1_bp.route('/mitra/ephemeral-sync', methods=['GET', 'POST'])
@login_required
def api_mitra_ephemeral_sync():
    return _mitra_ephemeral_sync()


def _is_ephemeral_db():
    return bool(current_app.config.get('IS_VERCEL')) and 'sqlite' in str(current_app.config.get('SQLALCHEMY_DATABASE_URI', ''))


def _user_dict(u):
    return {
        'id': u.id,
        'username': u.username,
        'email': u.email or '',
        'full_name': u.full_name,
        'role': u.role,
        'nip': u.nip or '',
    }


def _mitra_dict(m):
    return {
        'id': m.id,
        'id_sobat': m.id_sobat,
        'nama': m.nama_lengkap,
        'email': m.email or '',
        'alamat': m.alamat or '',
        'nomor_hp': m.no_hp or '',
        'jenis_kelamin': m.jenis_kelamin or 'Laki-laki',
        'desa': m.desa or '',
        'kecamatan': m.kecamatan or 'Banyuwangi',
        'status_aktif': bool(m.status_aktif),
    }


def _kegiatan_dict(k):
    return {
        'id': k.id,
        'kode_kegiatan': k.kode_kegiatan,
        'nama_kegiatan': k.nama_kegiatan,
        'tim_kerja': k.tim_kerja or 'Tim Distribusi',
        'tahun': k.tahun or 2025,
        'bulan': k.bulan or '',
        'tanggal_mulai': k.tanggal_mulai.isoformat() if k.tanggal_mulai else '',
        'tanggal_selesai': k.tanggal_selesai.isoformat() if k.tanggal_selesai else '',
        'status': k.status or 'BERJALAN',
        'total_mitra': k.penugasan_mitra.count(),
        'total_dokumen_target': k.total_dokumen_target,
        'total_dokumen_realisasi': k.total_dokumen_realisasi,
        'total_honor_mitra': k.total_honor_mitra,
    }


def _penugasan_dict(p):
    return {
        'id': p.id,
        'mitra_id': p.mitra_id,
        'mitra_nama': p.mitra.nama_lengkap if p.mitra else '-',
        'mitra_id_sobat': p.mitra.id_sobat if p.mitra else '-',
        'mitra_kecamatan': p.mitra.kecamatan if p.mitra else '-',
        'kegiatan_id': p.kegiatan_id,
        'kegiatan_nama': p.kegiatan.nama_kegiatan if p.kegiatan else '-',
        'kegiatan_tim': p.kegiatan.tim_kerja if p.kegiatan else '-',
        'kegiatan_bulan': p.kegiatan.bulan if p.kegiatan else '',
        'kegiatan_tahun': p.kegiatan.tahun if p.kegiatan else 2025,
        'peran': p.peran or 'PPL',
        'target_dokumen': p.target_dokumen or 0,
        'realisasi_dokumen': p.realisasi_dokumen or 0,
        'honor_total': p.honor_total or 0,
        'status': p.status or 'PROSES',
        'sudah_dinilai': bool(p.evaluasi),
    }


# ==============================================================================
# AUTH ENDPOINTS
# ==============================================================================

@api_v1_bp.route('/auth/me', methods=['GET'])
def auth_me():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': _user_dict(current_user),
            'is_ephemeral_db': _is_ephemeral_db(),
            'counts': {
                'mitra': Mitra.query.count(),
                'kegiatan': Kegiatan.query.count(),
                'penugasan': PenugasanMitra.query.count(),
                'evaluasi': EvaluasiMitra.query.count(),
            }
        })
    return jsonify({'authenticated': False, 'user': None, 'is_ephemeral_db': _is_ephemeral_db()})


@api_v1_bp.route('/auth/login', methods=['POST'])
def auth_login():
    data = request.get_json(silent=True) or {}
    identifier = (data.get('username') or data.get('email') or '').strip()
    password = data.get('password') or ''
    if not identifier or not password:
        return jsonify({'ok': False, 'message': 'Username/email dan password wajib diisi.'}), 400

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()
    if not user or not user.check_password(password):
        return jsonify({'ok': False, 'message': 'Username/email atau password salah.'}), 401

    login_user(user, remember=bool(data.get('remember', True)))
    return jsonify({'ok': True, 'user': _user_dict(user), 'is_ephemeral_db': _is_ephemeral_db()})


@api_v1_bp.route('/auth/logout', methods=['POST'])
@login_required
def auth_logout():
    logout_user()
    return jsonify({'ok': True})


# ==============================================================================
# HUB OVERVIEW
# ==============================================================================

@api_v1_bp.route('/hub', methods=['GET'])
@login_required
def hub_overview():
    total_docs = Document.query.count()
    total_mitra = Mitra.query.count()
    total_kegiatan = Kegiatan.query.count()
    total_pegawai = Pegawai.query.count()
    total_pengajuan = PengajuanAnggaran.query.count()
    total_honor = sum(p.honor_total for p in PenugasanMitra.query.all())
    return jsonify({
        'ok': True,
        'stats': {
            'total_docs': total_docs,
            'total_mitra': total_mitra,
            'total_kegiatan': total_kegiatan,
            'total_pegawai': total_pegawai,
            'total_pengajuan': total_pengajuan,
            'total_honor': total_honor,
        }
    })


# ==============================================================================
# MONITORING MITRA ENDPOINTS
# ==============================================================================

@api_v1_bp.route('/mitra/dashboard', methods=['GET'])
@login_required
def mitra_dashboard():
    total_mitra = Mitra.query.count()
    total_kegiatan = Kegiatan.query.count()
    all_penugasan = PenugasanMitra.query.order_by(PenugasanMitra.created_at.desc()).all()
    total_penugasan = len(all_penugasan)
    penugasan_selesai = sum(1 for p in all_penugasan if p.status == 'SELESAI')
    penugasan_proses = total_penugasan - penugasan_selesai
    total_honor_all = sum(p.honor_total for p in all_penugasan)

    eval_list = EvaluasiMitra.query.all()
    avg_score = round(sum(e.rata_rata for e in eval_list) / len(eval_list), 1) if eval_list else 0

    kec_data = db.session.query(Mitra.kecamatan, func.count(Mitra.id)).group_by(Mitra.kecamatan).all()
    kec_counts = dict(kec_data) if kec_data else {}
    sebaran_kecamatan = [{'kecamatan': k, 'count': kec_counts.get(k, 0)} for k in KECAMATAN_BANYUWANGI]

    all_keg = Kegiatan.query.order_by(Kegiatan.created_at.desc()).all()
    tim_counts = {
        'Tim Distribusi': sum(1 for k in all_keg if k.tim_kerja == 'Tim Distribusi'),
        'Tim Neraca': sum(1 for k in all_keg if k.tim_kerja == 'Tim Neraca'),
        'Tim Produksi': sum(1 for k in all_keg if k.tim_kerja == 'Tim Produksi'),
        'Tim PLS': sum(1 for k in all_keg if k.tim_kerja == 'Tim PLS'),
    }

    return jsonify({
        'ok': True,
        'kpi': {
            'total_mitra': total_mitra,
            'total_kegiatan': total_kegiatan,
            'total_penugasan': total_penugasan,
            'penugasan_selesai': penugasan_selesai,
            'penugasan_proses': penugasan_proses,
            'total_honor_all': total_honor_all,
            'avg_score': avg_score,
        },
        'tim_counts': tim_counts,
        'sebaran_kecamatan': sebaran_kecamatan,
        'penugasan_terbaru': [_penugasan_dict(p) for p in all_penugasan[:8]],
        'kegiatan_aktif': [_kegiatan_dict(k) for k in all_keg[:6]],
    })


@api_v1_bp.route('/mitra/list', methods=['GET'])
@login_required
def mitra_list():
    search = request.args.get('search', '').strip()
    kec = request.args.get('kecamatan', '').strip()
    jk = request.args.get('jenis_kelamin', '').strip()

    q = Mitra.query
    if search:
        q = q.filter(
            (Mitra.nama_lengkap.ilike(f'%{search}%')) |
            (Mitra.id_sobat.ilike(f'%{search}%')) |
            (Mitra.kecamatan.ilike(f'%{search}%')) |
            (Mitra.desa.ilike(f'%{search}%')) |
            (Mitra.no_hp.ilike(f'%{search}%')) |
            (Mitra.email.ilike(f'%{search}%'))
        )
    if kec:
        q = q.filter(Mitra.kecamatan == kec)
    if jk:
        q = q.filter(Mitra.jenis_kelamin == jk)

    items = q.order_by(Mitra.id.asc()).all()
    return jsonify({
        'ok': True,
        'total': len(items),
        'items': [_mitra_dict(m) for m in items],
        'kecamatan_options': KECAMATAN_BANYUWANGI,
    })


@api_v1_bp.route('/mitra/create', methods=['POST'])
@login_required
def mitra_create():
    data = request.get_json(silent=True) or {}
    id_sobat = (data.get('id_sobat') or '').strip()
    nama = (data.get('nama') or data.get('nama_lengkap') or '').strip()
    kecamatan = (data.get('kecamatan') or '').strip()
    if not id_sobat or not nama or not kecamatan:
        return jsonify({'ok': False, 'message': 'ID Sobat, Nama, dan Kecamatan wajib diisi.'}), 400
    if Mitra.query.filter_by(id_sobat=id_sobat).first():
        return jsonify({'ok': False, 'message': f'ID Sobat {id_sobat} sudah terdaftar.'}), 409

    m = Mitra(
        id_sobat=id_sobat,
        nama_lengkap=nama,
        email=(data.get('email') or '').strip() or None,
        alamat=(data.get('alamat') or '').strip() or None,
        no_hp=(data.get('nomor_hp') or data.get('no_hp') or '').strip() or None,
        jenis_kelamin=(data.get('jenis_kelamin') or 'Laki-laki').strip(),
        desa=(data.get('desa') or '').strip() or None,
        kecamatan=kecamatan,
    )
    db.session.add(m)
    db.session.commit()
    return jsonify({'ok': True, 'item': _mitra_dict(m)}), 201


@api_v1_bp.route('/mitra/<int:mitra_id>/toggle', methods=['POST'])
@login_required
def mitra_toggle(mitra_id):
    m = Mitra.query.get_or_404(mitra_id)
    m.status_aktif = not m.status_aktif
    db.session.commit()
    return jsonify({'ok': True, 'item': _mitra_dict(m)})


@api_v1_bp.route('/mitra/<int:mitra_id>', methods=['DELETE'])
@login_required
def mitra_delete(mitra_id):
    m = Mitra.query.get_or_404(mitra_id)
    db.session.delete(m)
    db.session.commit()
    return jsonify({'ok': True})


@api_v1_bp.route('/mitra/upload-mitra', methods=['POST'])
@login_required
def mitra_upload_csv():
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({'ok': False, 'message': 'Silakan pilih file CSV Data Mitra.'}), 400
    try:
        raw = file.stream.read()
        content = raw.decode('utf-8-sig', errors='ignore')
        first_line = content.splitlines()[0] if content.splitlines() else ''
        delimiter = ';' if ';' in first_line and ',' not in first_line else ','
        reader = csv.DictReader(io.StringIO(content, newline=None), delimiter=delimiter)
        added = 0
        updated = 0
        for row in reader:
            clean = {k.strip().lower(): (v.strip() if v else '') for k, v in row.items() if k}
            id_sobat = clean.get('id_sobat') or clean.get('id sobat')
            nama = clean.get('nama') or clean.get('nama_lengkap') or clean.get('nama lengkap')
            nomor_hp = clean.get('nomor_hp') or clean.get('nomor hp') or clean.get('no_hp')
            jk = clean.get('jenis_kelamin') or clean.get('jenis kelamin')
            if not id_sobat or not nama:
                continue
            existing = Mitra.query.filter_by(id_sobat=id_sobat).first()
            if existing:
                existing.nama_lengkap = nama
                if clean.get('email'): existing.email = clean.get('email')
                if clean.get('alamat'): existing.alamat = clean.get('alamat')
                if nomor_hp: existing.no_hp = nomor_hp
                if jk: existing.jenis_kelamin = jk
                if clean.get('desa'): existing.desa = clean.get('desa')
                if clean.get('kecamatan'): existing.kecamatan = clean.get('kecamatan')
                updated += 1
            else:
                db.session.add(Mitra(
                    id_sobat=id_sobat,
                    nama_lengkap=nama,
                    email=clean.get('email') or None,
                    alamat=clean.get('alamat') or None,
                    no_hp=nomor_hp or None,
                    jenis_kelamin=jk or 'Laki-laki',
                    desa=clean.get('desa') or None,
                    kecamatan=clean.get('kecamatan') or 'Banyuwangi',
                ))
                added += 1
        db.session.commit()
        return jsonify({
            'ok': True,
            'added': added,
            'updated': updated,
            'message': f'Upload berhasil: {added} mitra baru ditambahkan, {updated} diperbarui.',
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'ok': False, 'message': f'Gagal mengimpor CSV: {str(e)}'}), 400


@api_v1_bp.route('/mitra/download-template-mitra', methods=['GET'])
@login_required
def mitra_download_template():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id_sobat', 'nama', 'email', 'alamat', 'nomor_hp', 'jenis_kelamin', 'desa', 'kecamatan'])
    writer.writerow(['35102025001', 'Ahmad Subandi', 'ahmad.subandi@gmail.com', 'Jl. Ahmad Yani No. 15', '081234567890', 'Laki-laki', 'Rogojampi', 'Rogojampi'])
    writer.writerow(['35102025002', 'Siti Rahmawati', 'siti.rahma@gmail.com', 'Jl. Diponegoro No. 44', '081298765432', 'Perempuan', 'Genteng Wetan', 'Genteng'])
    resp = Response(output.getvalue().encode('utf-8-sig'), mimetype='text/csv')
    resp.headers['Content-Disposition'] = 'attachment; filename=Template_Data_Mitra_BPS.csv'
    return resp


@api_v1_bp.route('/mitra/kegiatan', methods=['GET'])
@login_required
def mitra_kegiatan_list():
    tim = request.args.get('tim', '').strip()
    tahun = request.args.get('tahun', '').strip()
    bulan = request.args.get('bulan', '').strip()
    search = request.args.get('search', '').strip()

    q = Kegiatan.query
    if tim and tim != 'Semua':
        q = q.filter(Kegiatan.tim_kerja == tim)
    if tahun:
        try:
            q = q.filter(Kegiatan.tahun == int(tahun))
        except ValueError:
            pass
    if bulan:
        q = q.filter(Kegiatan.bulan.ilike(f'%{bulan}%'))
    if search:
        q = q.filter(Kegiatan.nama_kegiatan.ilike(f'%{search}%'))

    items = q.order_by(Kegiatan.id.desc()).all()
    all_keg = Kegiatan.query.all()
    counts = {
        'Semua': len(all_keg),
        'Tim Distribusi': sum(1 for k in all_keg if k.tim_kerja == 'Tim Distribusi'),
        'Tim Neraca': sum(1 for k in all_keg if k.tim_kerja == 'Tim Neraca'),
        'Tim Produksi': sum(1 for k in all_keg if k.tim_kerja == 'Tim Produksi'),
        'Tim PLS': sum(1 for k in all_keg if k.tim_kerja == 'Tim PLS'),
    }
    return jsonify({
        'ok': True,
        'items': [_kegiatan_dict(k) for k in items],
        'counts': counts,
    })


@api_v1_bp.route('/mitra/kegiatan/create', methods=['POST'])
@login_required
def mitra_kegiatan_create():
    data = request.get_json(silent=True) or {}
    nama = (data.get('nama_kegiatan') or '').strip()
    tim = (data.get('tim_kerja') or 'Tim Distribusi').strip()
    tahun = int(data.get('tahun') or datetime.utcnow().year)
    bulan = (data.get('bulan') or 'Januari').strip()
    today = datetime.utcnow().date()
    try:
        t_mulai = datetime.strptime(data.get('tanggal_mulai', ''), '%Y-%m-%d').date() if data.get('tanggal_mulai') else today
        t_selesai = datetime.strptime(data.get('tanggal_selesai', ''), '%Y-%m-%d').date() if data.get('tanggal_selesai') else today + timedelta(days=30)
    except ValueError:
        return jsonify({'ok': False, 'message': 'Format tanggal tidak valid (YYYY-MM-DD).'}), 400
    if not nama:
        return jsonify({'ok': False, 'message': 'Nama kegiatan wajib diisi.'}), 400

    pfx = {'Tim Distribusi': 'DIS', 'Tim Neraca': 'NER', 'Tim Produksi': 'PRD', 'Tim PLS': 'PLS'}.get(tim, 'KEG')
    seq = Kegiatan.query.count() + 1
    kode = f"KEG-{pfx}-{tahun}-{seq:03d}"
    while Kegiatan.query.filter_by(kode_kegiatan=kode).first():
        seq += 1
        kode = f"KEG-{pfx}-{tahun}-{seq:03d}"

    k = Kegiatan(
        kode_kegiatan=kode,
        nama_kegiatan=nama,
        tim_kerja=tim,
        tahun=tahun,
        bulan=bulan,
        tanggal_mulai=t_mulai,
        tanggal_selesai=t_selesai,
        penanggung_jawab_id=current_user.id,
    )
    db.session.add(k)
    db.session.commit()
    return jsonify({'ok': True, 'item': _kegiatan_dict(k)}), 201


@api_v1_bp.route('/mitra/upload-kegiatan', methods=['POST'])
@login_required
def mitra_upload_kegiatan():
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({'ok': False, 'message': 'Silakan pilih file CSV Kegiatan.'}), 400
    try:
        raw = file.stream.read()
        content = raw.decode('utf-8-sig', errors='ignore')
        first_line = content.splitlines()[0] if content.splitlines() else ''
        delimiter = ';' if ';' in first_line and ',' not in first_line else ','
        reader = csv.DictReader(io.StringIO(content, newline=None), delimiter=delimiter)
        added = 0
        updated = 0
        today = datetime.utcnow().date()

        def parse_date(s, fb):
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
                try:
                    return datetime.strptime(s, fmt).date()
                except ValueError:
                    pass
            return fb

        for row in reader:
            clean = {k.strip().lower(): (v.strip() if v else '') for k, v in row.items() if k}
            nama = clean.get('nama_kegiatan') or clean.get('nama kegiatan') or clean.get('nama')
            if not nama:
                continue
            tim_raw = (clean.get('tim_kerja') or clean.get('tim kerja') or 'Tim Distribusi').upper()
            if 'NERACA' in tim_raw:
                tim = 'Tim Neraca'
            elif 'PRODUKSI' in tim_raw:
                tim = 'Tim Produksi'
            elif 'PLS' in tim_raw or 'PENGOLAHAN' in tim_raw:
                tim = 'Tim PLS'
            else:
                tim = 'Tim Distribusi'
            try:
                tahun = int(clean.get('tahun') or today.year)
            except ValueError:
                tahun = today.year
            bulan = clean.get('bulan') or 'Januari'
            t_mulai = parse_date(clean.get('tanggal_mulai') or clean.get('tanggal mulai') or '', today)
            t_selesai = parse_date(clean.get('tanggal_selesai') or clean.get('tanggal selesai') or '', today + timedelta(days=30))

            existing = Kegiatan.query.filter_by(nama_kegiatan=nama, tahun=tahun).first()
            if existing:
                existing.tim_kerja = tim
                existing.bulan = bulan
                existing.tanggal_mulai = t_mulai
                existing.tanggal_selesai = t_selesai
                updated += 1
            else:
                pfx = {'Tim Distribusi': 'DIS', 'Tim Neraca': 'NER', 'Tim Produksi': 'PRD', 'Tim PLS': 'PLS'}.get(tim, 'KEG')
                seq = Kegiatan.query.count() + added + 1
                kode = f"KEG-{pfx}-{tahun}-{seq:03d}"
                while Kegiatan.query.filter_by(kode_kegiatan=kode).first():
                    seq += 1
                    kode = f"KEG-{pfx}-{tahun}-{seq:03d}"
                db.session.add(Kegiatan(
                    kode_kegiatan=kode,
                    nama_kegiatan=nama,
                    tim_kerja=tim,
                    tahun=tahun,
                    bulan=bulan,
                    tanggal_mulai=t_mulai,
                    tanggal_selesai=t_selesai,
                    penanggung_jawab_id=current_user.id,
                ))
                added += 1
        db.session.commit()
        return jsonify({
            'ok': True,
            'added': added,
            'updated': updated,
            'message': f'Upload berhasil: {added} kegiatan baru ditambahkan, {updated} diperbarui.',
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'ok': False, 'message': f'Gagal mengimpor CSV: {str(e)}'}), 400


@api_v1_bp.route('/mitra/download-template-kegiatan', methods=['GET'])
@login_required
def mitra_download_template_kegiatan():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['nama_kegiatan', 'tim_kerja', 'tahun', 'bulan', 'tanggal_mulai', 'tanggal_selesai'])
    writer.writerow(['Survei Harga Perdagangan Besar (SHPB)', 'Tim Distribusi', '2025', 'Januari', '2025-01-05', '2025-01-31'])
    writer.writerow(['Survei Khusus Lembaga Non-Profit (SKLNP)', 'Tim Neraca', '2025', 'Januari', '2025-01-10', '2025-02-15'])
    resp = Response(output.getvalue().encode('utf-8-sig'), mimetype='text/csv')
    resp.headers['Content-Disposition'] = 'attachment; filename=Template_Kegiatan_BPS.csv'
    return resp


@api_v1_bp.route('/mitra/penugasan', methods=['GET'])
@login_required
def mitra_penugasan_list():
    all_p = PenugasanMitra.query.order_by(PenugasanMitra.created_at.desc()).all()
    mitra_opts = Mitra.query.filter_by(status_aktif=True).order_by(Mitra.nama_lengkap.asc()).all()
    keg_opts = Kegiatan.query.order_by(Kegiatan.nama_kegiatan.asc()).all()
    return jsonify({
        'ok': True,
        'kpi': {
            'total': len(all_p),
            'proses': sum(1 for p in all_p if p.status != 'SELESAI'),
            'selesai': sum(1 for p in all_p if p.status == 'SELESAI'),
            'total_honor': sum(p.honor_total for p in all_p),
        },
        'items': [_penugasan_dict(p) for p in all_p],
        'mitra_options': [_mitra_dict(m) for m in mitra_opts],
        'kegiatan_options': [_kegiatan_dict(k) for k in keg_opts],
    })


@api_v1_bp.route('/mitra/penugasan/create', methods=['POST'])
@login_required
def mitra_penugasan_create():
    data = request.get_json(silent=True) or {}
    mitra_id = data.get('mitra_id')
    kegiatan_id = data.get('kegiatan_id')
    if not mitra_id or not kegiatan_id:
        return jsonify({'ok': False, 'message': 'Mitra dan Kegiatan wajib dipilih.'}), 400
    p = PenugasanMitra(
        mitra_id=int(mitra_id),
        kegiatan_id=int(kegiatan_id),
        peran=data.get('peran') or 'PPL',
        target_dokumen=int(data.get('target_dokumen') or 25),
        honor_total=int(data.get('honor_total') or 0),
        created_by=current_user.id,
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({'ok': True, 'item': _penugasan_dict(p)}), 201


@api_v1_bp.route('/mitra/penugasan/<int:penugasan_id>/progress', methods=['POST'])
@login_required
def mitra_penugasan_progress(penugasan_id):
    p = PenugasanMitra.query.get_or_404(penugasan_id)
    data = request.get_json(silent=True) or {}
    realisasi = max(0, int(data.get('realisasi_dokumen', 0)))
    p.realisasi_dokumen = realisasi
    p.status = 'SELESAI' if realisasi >= (p.target_dokumen or 1) else 'PROSES'
    db.session.commit()
    return jsonify({'ok': True, 'item': _penugasan_dict(p)})


@api_v1_bp.route('/mitra/evaluasi', methods=['GET'])
@login_required
def mitra_evaluasi_list():
    evals = EvaluasiMitra.query.order_by(EvaluasiMitra.created_at.desc()).all()
    belum = PenugasanMitra.query.filter(~PenugasanMitra.evaluasi.has()).all()
    mitra_opts = Mitra.query.filter_by(status_aktif=True).order_by(Mitra.nama_lengkap.asc()).all()
    keg_opts = Kegiatan.query.order_by(Kegiatan.nama_kegiatan.asc()).all()
    avg_score = round(sum(e.rata_rata for e in evals) / len(evals), 1) if evals else 0
    return jsonify({
        'ok': True,
        'kpi': {
            'avg_score': avg_score,
            'total_dinilai': len(evals),
            'menunggu': len(belum),
            'total_mitra': len(mitra_opts),
            'total_kegiatan': len(keg_opts),
        },
        'items': [
            {
                'id': e.id,
                'mitra_nama': e.mitra.nama_lengkap if e.mitra else '-',
                'mitra_id_sobat': e.mitra.id_sobat if e.mitra else '-',
                'mitra_kecamatan': e.mitra.kecamatan if e.mitra else '-',
                'kegiatan_nama': e.penugasan.kegiatan.nama_kegiatan if (e.penugasan and e.penugasan.kegiatan) else '-',
                'kegiatan_tim': e.penugasan.kegiatan.tim_kerja if (e.penugasan and e.penugasan.kegiatan) else '-',
                'kegiatan_tahun': e.penugasan.kegiatan.tahun if (e.penugasan and e.penugasan.kegiatan) else 2025,
                'nilai_kualitas': e.nilai_kualitas,
                'nilai_ketepatan': e.nilai_ketepatan,
                'nilai_kerjasama': e.nilai_kerjasama,
                'rata_rata': e.rata_rata,
                'catatan': e.catatan or '',
            }
            for e in evals
        ],
        'penugasan_belum_eval': [_penugasan_dict(p) for p in belum],
        'mitra_options': [_mitra_dict(m) for m in mitra_opts],
        'kegiatan_options': [_kegiatan_dict(k) for k in keg_opts],
    })


@api_v1_bp.route('/mitra/evaluasi/create', methods=['POST'])
@login_required
def mitra_evaluasi_create():
    data = request.get_json(silent=True) or {}
    penugasan_id = data.get('penugasan_id')
    mitra_id = data.get('mitra_id')
    kegiatan_id = data.get('kegiatan_id')
    nk = int(data.get('nilai_kualitas', 85))
    nt = int(data.get('nilai_ketepatan', 85))
    nj = int(data.get('nilai_kerjasama', 85))
    catatan = (data.get('catatan') or '').strip()

    if penugasan_id:
        p = PenugasanMitra.query.get_or_404(int(penugasan_id))
    elif mitra_id and kegiatan_id:
        p = PenugasanMitra.query.filter_by(mitra_id=int(mitra_id), kegiatan_id=int(kegiatan_id)).first()
        if not p:
            p = PenugasanMitra(
                mitra_id=int(mitra_id),
                kegiatan_id=int(kegiatan_id),
                peran='PPL',
                target_dokumen=10,
                realisasi_dokumen=10,
                honor_total=0,
                status='SELESAI',
                created_by=current_user.id,
            )
            db.session.add(p)
            db.session.flush()
    else:
        return jsonify({'ok': False, 'message': 'Pilih penugasan atau Mitra & Kegiatan.'}), 400

    if p.evaluasi:
        p.evaluasi.nilai_kualitas = nk
        p.evaluasi.nilai_ketepatan = nt
        p.evaluasi.nilai_kerjasama = nj
        p.evaluasi.catatan = catatan
        p.evaluasi.evaluator_id = current_user.id
    else:
        db.session.add(EvaluasiMitra(
            penugasan_id=p.id,
            mitra_id=p.mitra_id,
            nilai_kualitas=nk,
            nilai_ketepatan=nt,
            nilai_kerjasama=nj,
            catatan=catatan,
            evaluator_id=current_user.id,
        ))
    p.status = 'SELESAI'
    db.session.commit()
    return jsonify({'ok': True}), 201


@api_v1_bp.route('/mitra/rekapitulasi', methods=['GET'])
@login_required
def mitra_rekapitulasi():
    mitra_all = Mitra.query.order_by(Mitra.id.asc()).all()
    rekap_data = []
    total_honor_all = 0
    for m in mitra_all:
        p_all = m.penugasan.all()
        e_all = m.evaluasi_list.all()
        avg = round(sum(e.rata_rata for e in e_all) / len(e_all), 1) if e_all else 0
        honor = sum(p.honor_total for p in p_all)
        total_honor_all += honor
        selesai = sum(1 for p in p_all if (p.status or '').upper() == 'SELESAI')
        tim_list = sorted({p.kegiatan.tim_kerja for p in p_all if p.kegiatan and p.kegiatan.tim_kerja})
        keg_names = list(dict.fromkeys([p.kegiatan.nama_kegiatan for p in p_all if p.kegiatan]))
        if avg >= 90:
            pred = 'Sangat Baik (A)'
        elif avg >= 80:
            pred = 'Baik (B)'
        elif avg >= 70:
            pred = 'Cukup (C)'
        elif avg > 0:
            pred = 'Kurang (D)'
        else:
            pred = 'Belum Dinilai'
        rekap_data.append({
            'mitra': _mitra_dict(m),
            'total_tugas': len(p_all),
            'tugas_selesai': selesai,
            'tugas_berjalan': len(p_all) - selesai,
            'tim_list': tim_list,
            'kegiatan_list': keg_names,
            'jumlah_eval': len(e_all),
            'avg_score': avg,
            'predikat': pred,
            'total_honor': honor,
        })

    rekap_kec = []
    for kec in KECAMATAN_BANYUWANGI:
        ms = [m for m in mitra_all if m.kecamatan == kec]
        m_ids = [m.id for m in ms]
        if m_ids:
            ps = PenugasanMitra.query.filter(PenugasanMitra.mitra_id.in_(m_ids)).all()
            t_tugas = len(ps)
            t_honor = sum(p.honor_total for p in ps)
        else:
            t_tugas = 0
            t_honor = 0
        rekap_kec.append({
            'kecamatan': kec,
            'total_mitra': len(ms),
            'total_tugas': t_tugas,
            'total_honor': t_honor,
        })

    tim_meta = [
        ('Tim Distribusi', 'SHPB, VHTS, Transportasi & Jasa'),
        ('Tim Neraca', 'PDRB, SKLNP, SKPS & Analisis Makro'),
        ('Tim Produksi', 'KSA Padi/Jagung, Ubinan & Pertanian'),
        ('Tim PLS', 'Pengolahan Data, TI & Wilkerstat'),
    ]
    rekap_tim = []
    for t_nama, t_desc in tim_meta:
        ks = Kegiatan.query.filter_by(tim_kerja=t_nama).all()
        k_ids = [k.id for k in ks]
        if k_ids:
            ps = PenugasanMitra.query.filter(PenugasanMitra.kegiatan_id.in_(k_ids)).all()
            t_tugas = len(ps)
            t_honor = sum(p.honor_total for p in ps)
        else:
            t_tugas = 0
            t_honor = 0
        rekap_tim.append({
            'nama': t_nama,
            'desc': t_desc,
            'total_kegiatan': len(ks),
            'total_tugas': t_tugas,
            'total_honor': t_honor,
        })

    return jsonify({
        'ok': True,
        'kpi': {
            'total_mitra': len(mitra_all),
            'total_kegiatan': Kegiatan.query.count(),
            'total_penugasan': PenugasanMitra.query.count(),
            'total_honor_all': total_honor_all,
        },
        'rekap_kecamatan': rekap_kec,
        'rekap_tim': rekap_tim,
        'rekap_mitra': rekap_data,
    })


# ==============================================================================
# KINERJA PEGAWAI ENDPOINTS
# ==============================================================================

@api_v1_bp.route('/pegawai/overview', methods=['GET'])
@login_required
def pegawai_overview():
    pegawais = Pegawai.query.order_by(Pegawai.nama_lengkap.asc()).all()
    aktivitas = AktivitasPegawai.query.order_by(AktivitasPegawai.created_at.desc()).all()
    return jsonify({
        'ok': True,
        'pegawai': [
            {
                'id': p.id,
                'nip': p.nip or '-',
                'nama': p.nama_lengkap,
                'jabatan': p.jabatan or '-',
                'tim_kerja': p.tim_kerja or 'Umum',
                'status_aktif': bool(p.status_aktif),
                'total_aktivitas': p.aktivitas.count(),
            }
            for p in pegawais
        ],
        'aktivitas': [
            {
                'id': a.id,
                'pegawai_nama': a.pegawai.nama_lengkap if a.pegawai else '-',
                'tim_kerja': a.pegawai.tim_kerja if a.pegawai else '-',
                'judul': a.judul_aktivitas,
                'deskripsi': a.deskripsi or '',
                'tanggal_mulai': a.tanggal_mulai.isoformat() if a.tanggal_mulai else '',
                'tanggal_selesai': a.tanggal_selesai.isoformat() if a.tanggal_selesai else '',
                'status': a.status or 'PROSES',
            }
            for a in aktivitas
        ],
    })


@api_v1_bp.route('/pegawai/create', methods=['POST'])
@login_required
def pegawai_create():
    data = request.get_json(silent=True) or {}
    nama = (data.get('nama') or '').strip()
    nip = (data.get('nip') or '').strip()
    if not nama or not nip:
        return jsonify({'ok': False, 'message': 'NIP dan Nama Pegawai wajib diisi.'}), 400
    if Pegawai.query.filter_by(nip=nip).first():
        return jsonify({'ok': False, 'message': f'NIP {nip} sudah terdaftar.'}), 409
    p = Pegawai(
        nip=nip,
        nama_lengkap=nama,
        jabatan=(data.get('jabatan') or 'Statistisi').strip(),
        tim_kerja=(data.get('tim_kerja') or 'Tim Distribusi').strip(),
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({'ok': True}), 201


@api_v1_bp.route('/pegawai/aktivitas/create', methods=['POST'])
@login_required
def pegawai_aktivitas_create():
    data = request.get_json(silent=True) or {}
    pegawai_id = data.get('pegawai_id')
    judul = (data.get('judul') or '').strip()
    if not pegawai_id or not judul:
        return jsonify({'ok': False, 'message': 'Pegawai dan judul aktivitas wajib diisi.'}), 400
    today = datetime.utcnow().date()
    a = AktivitasPegawai(
        pegawai_id=int(pegawai_id),
        judul_aktivitas=judul,
        deskripsi=(data.get('deskripsi') or '').strip(),
        tanggal_mulai=today,
        tanggal_selesai=today + timedelta(days=7),
        status=data.get('status') or 'PROSES',
    )
    db.session.add(a)
    db.session.commit()
    return jsonify({'ok': True}), 201


# ==============================================================================
# TRACKING KEUANGAN ENDPOINTS
# ==============================================================================

@api_v1_bp.route('/keuangan/overview', methods=['GET'])
@login_required
def keuangan_overview():
    akuns = AkunAnggaran.query.all()
    komponens = KomponenAnggaran.query.all()
    pengajuans = PengajuanAnggaran.query.order_by(PengajuanAnggaran.created_at.desc()).all()
    total_pagu = sum(k.pagu_anggaran for k in komponens)
    total_diajukan = sum(p.jumlah_diajukan for p in pengajuans)
    total_cair = sum(p.realisasi.jumlah_realisasi for p in pengajuans if p.realisasi)
    return jsonify({
        'ok': True,
        'kpi': {
            'total_pagu': total_pagu,
            'total_diajukan': total_diajukan,
            'total_cair': total_cair,
            'total_pengajuan': len(pengajuans),
        },
        'akun': [{'id': a.id, 'kode': a.kode_akun, 'nama': a.nama_akun} for a in akuns],
        'komponen': [
            {
                'id': k.id,
                'kode': k.kode_komponen,
                'nama': k.nama_komponen,
                'pagu': k.pagu_anggaran,
            }
            for k in komponens
        ],
        'pengajuan': [
            {
                'id': p.id,
                'nomor': p.nomor_pengajuan,
                'uraian': p.uraian,
                'jumlah': p.jumlah_diajukan,
                'status': p.status,
                'tanggal': p.tanggal_pengajuan.isoformat() if p.tanggal_pengajuan else '',
                'cair': p.realisasi.jumlah_realisasi if p.realisasi else 0,
            }
            for p in pengajuans
        ],
    })


@api_v1_bp.route('/keuangan/pengajuan/create', methods=['POST'])
@login_required
def keuangan_pengajuan_create():
    data = request.get_json(silent=True) or {}
    uraian = (data.get('uraian') or '').strip()
    jumlah = int(data.get('jumlah') or 0)
    if not uraian or jumlah <= 0:
        return jsonify({'ok': False, 'message': 'Uraian dan jumlah pengajuan wajib diisi.'}), 400
    nomor = f"AJU-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    p = PengajuanAnggaran(
        nomor_pengajuan=nomor,
        uraian=uraian,
        jumlah_diajukan=jumlah,
        tanggal_pengajuan=datetime.utcnow().date(),
        status='DIAJUKAN',
        pengaju_id=current_user.id,
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({'ok': True}), 201


@api_v1_bp.route('/keuangan/pengajuan/<int:pid>/approve', methods=['POST'])
@login_required
def keuangan_pengajuan_approve(pid):
    p = PengajuanAnggaran.query.get_or_404(pid)
    p.status = 'DISETUJUI'
    if not p.persetujuan:
        db.session.add(PersetujuanAnggaran(
            pengajuan_id=p.id,
            approver_id=current_user.id,
            status_keputusan='DISETUJUI',
            catatan='Disetujui melalui LENTERA',
        ))
    db.session.commit()
    return jsonify({'ok': True})


@api_v1_bp.route('/keuangan/pengajuan/<int:pid>/cairkan', methods=['POST'])
@login_required
def keuangan_pengajuan_cairkan(pid):
    p = PengajuanAnggaran.query.get_or_404(pid)
    p.status = 'CAIR'
    if not p.realisasi:
        db.session.add(RealisasiAnggaran(
            pengajuan_id=p.id,
            nomor_sp2d=f"CAIR-{datetime.utcnow().strftime('%Y%m%d%H%M')}",
            jumlah_realisasi=p.jumlah_diajukan,
            tanggal_realisasi=datetime.utcnow().date(),
            created_by=current_user.id,
        ))
    db.session.commit()
    return jsonify({'ok': True})


# ==============================================================================
# PRIMA (ARSIP & AKIP) ENDPOINTS
# ==============================================================================

@api_v1_bp.route('/akip/overview', methods=['GET'])
@login_required
def akip_overview():
    cats = Category.query.all()
    docs = Document.query.order_by(Document.created_at.desc()).limit(100).all()
    links = ImportantLink.query.filter_by(is_active=True).all()
    return jsonify({
        'ok': True,
        'kpi': {
            'total_docs': Document.query.count(),
            'lengkap': Document.query.filter_by(status='lengkap').count(),
            'belum_lengkap': Document.query.filter_by(status='belum_lengkap').count(),
            'total_categories': len(cats),
        },
        'categories': [
            {
                'id': c.id,
                'name': c.name,
                'group': c.group,
                'drive_url': c.drive_url or '',
            }
            for c in cats
        ],
        'documents': [
            {
                'id': d.id,
                'title': d.title,
                'category': d.category.name if d.category else '-',
                'year': d.year,
                'status': d.status,
                'drive_url': d.drive_url or '',
            }
            for d in docs
        ],
        'links': [
            {'id': l.id, 'title': l.title, 'url': l.url, 'description': l.description or ''}
            for l in links
        ],
    })
