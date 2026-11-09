import os
import uuid
import logging
from functools import wraps
from flask import abort, current_app, request
from flask_login import current_user
from werkzeug.utils import secure_filename
from app.models import db, Activity

logger = logging.getLogger(__name__)

def roles_required(*roles):
    """
    Decorator untuk membatasi akses endpoint berdasarkan satu atau lebih peran (RBAC).
    Contoh: @roles_required('admin', 'staf_umum', 'ppk')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            # Admin selalu memiliki hak akses bypass
            if current_user.role != 'admin' and current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """
    Decorator untuk membatasi akses endpoint khusus role 'admin'.
    Jika pengguna bukan admin atau belum login, akan menghasilkan abort HTTP 403 (Forbidden).
    """
    return roles_required('admin')(f)

def log_activity(action, description, user_id=None):
    """
    Mencatat rekam jejak (audit trail) aktivitas pengguna ke tabel `activities`.
    
    :param action: Jenis tindakan (misal: 'UPLOAD_DOCUMENT', 'DELETE_DOCUMENT', 'LOGIN')
    :param description: Rincian penjelasan aktivitas
    :param user_id: ID pengguna pelaksana (default: current_user.id jika terotentikasi)
    """
    try:
        uid = user_id or (current_user.id if current_user.is_authenticated else None)
        ip = request.remote_addr if request else '127.0.0.1'
        
        act = Activity(
            user_id=uid,
            action=action,
            description=description,
            ip_address=ip
        )
        db.session.add(act)
        db.session.commit()
    except Exception as e:
        logger.error(f"Gagal mencatat log aktivitas: {e}")
        db.session.rollback()

def allowed_file(filename):
    """
    Memeriksa apakah ekstensi file termasuk dalam daftar yang diperbolehkan.
    Format yang didukung: PDF, DOC, DOCX, XLS, XLSX, PPTX.
    """
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']

def get_document_file_path(filename):
    """
    Mengembalikan path fisik absolut dari file dokumen di penyimpanan server.
    Lokasi default: app/static/uploads/documents/<filename>
    """
    return os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

def save_document_file(file_storage):
    """
    Menyimpan file dokumen yang diunggah ke direktori server fisik dengan nama unik berbasis UUID.
    
    Tujuan nama unik berbasis UUID:
    Mencegah file saling bertumpuk (overwrite) jika ada nama file yang sama dari pengunggah berbeda.
    
    :param file_storage: Objek FileStorage dari request.files['file']
    :return: Tuple (unique_name, original_name, file_size, file_type)
    """
    original_name = secure_filename(file_storage.filename)
    if not original_name:
        original_name = "dokumen_tanpa_nama.pdf"

    ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'pdf'
    unique_name = f"{uuid.uuid4().hex}_{original_name}"
    
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    
    upload_path = os.path.join(upload_dir, unique_name)
    file_storage.save(upload_path)
    
    file_size = os.path.getsize(upload_path)
    return unique_name, original_name, file_size, ext

def delete_document_file(filename):
    """
    Menghapus file fisik dokumen dari server jika file tersebut ada di direktori upload.
    
    :param filename: Nama file unik di disk server
    :return: True jika berhasil atau tidak ditemukan, False jika terjadi kegagalan
    """
    if not filename:
        return False
        
    file_path = get_document_file_path(filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"File fisik dokumen {file_path} berhasil dihapus.")
            return True
        except Exception as e:
            logger.warning(f"Gagal menghapus file fisik {file_path}: {e}")
            return False
    return True
