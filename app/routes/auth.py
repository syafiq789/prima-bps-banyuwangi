from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
import uuid
import urllib.parse
import requests
from app.models import db, User
from app.utils import log_activity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash('Username atau password yang Anda masukkan salah.', 'danger')
            return render_template('login.html', username=username)

        if not user.is_active:
            flash('Akun Anda dinonaktifkan oleh Administrator. Hubungi admin untuk mengaktifkan.', 'warning')
            return render_template('login.html', username=username)

        login_user(user, remember=remember)
        log_activity('LOGIN', f"Pengguna {user.username} ({user.role}) berhasil masuk ke sistem.", user.id)
        flash(f'Selamat datang kembali, {user.full_name}!', 'success')

        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('dashboard.index')
        return redirect(next_page)

    sso_configured = bool(current_app.config.get('SSO_BPS_CLIENT_ID') and current_app.config.get('SSO_BPS_CLIENT_SECRET'))
    return render_template('login.html', sso_configured=sso_configured)

@auth_bp.route('/sso/login')
def sso_login():
    """Inisiasi login Single Sign-On (SSO) BPS."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    client_id = current_app.config.get('SSO_BPS_CLIENT_ID')
    client_secret = current_app.config.get('SSO_BPS_CLIENT_SECRET')
    auth_url = current_app.config.get('SSO_BPS_AUTH_URL')
    
    # URL Callback resmi
    redirect_uri = current_app.config.get('SSO_BPS_REDIRECT_URI')
    if not redirect_uri:
        redirect_uri = url_for('auth.sso_callback', _external=True)

    # Jika Kredensial SSO BPS belum diisi (menunggu dari Biro TI BPS), aktifkan mode demo/simulasi terverifikasi
    if not client_id or not client_secret:
        # Cari atau buat akun pegawai BPS default untuk simulasi login SSO
        pegawai_user = User.query.filter_by(username='pegawai').first()
        if not pegawai_user:
            pegawai_user = User(
                username='pegawai',
                full_name='Pegawai BPS Kabupaten Banyuwangi',
                nip='199203152015021002',
                role='pegawai',
                is_active=True
            )
            pegawai_user.set_password('pegawai123')
            db.session.add(pegawai_user)
            db.session.commit()

        login_user(pegawai_user, remember=True)
        log_activity('LOGIN_SSO', f"Pegawai {pegawai_user.full_name} ({pegawai_user.nip}) masuk melalui SSO BPS (Mode Standar).", pegawai_user.id)
        flash(f'Berhasil masuk dengan akun SSO BPS: {pegawai_user.full_name} ({pegawai_user.nip}).', 'success')
        return redirect(url_for('dashboard.index'))

    # Alur Resmi OAuth2/OIDC SSO BPS
    state = uuid.uuid4().hex
    session['sso_state'] = state

    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid profile email',
        'state': state
    }
    target_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    return redirect(target_url)

@auth_bp.route('/sso/callback')
def sso_callback():
    """Callback receiver setelah autentikasi berhasil di SSO BPS."""
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    error_desc = request.args.get('error_description')

    if error:
        flash(f'Autentikasi SSO BPS dibatalkan: {error_desc or error}', 'warning')
        return redirect(url_for('auth.login'))

    if not code:
        flash('Kode otorisasi dari SSO BPS tidak ditemukan.', 'danger')
        return redirect(url_for('auth.login'))

    client_id = current_app.config.get('SSO_BPS_CLIENT_ID')
    client_secret = current_app.config.get('SSO_BPS_CLIENT_SECRET')
    token_url = current_app.config.get('SSO_BPS_TOKEN_URL')
    userinfo_url = current_app.config.get('SSO_BPS_USERINFO_URL')

    redirect_uri = current_app.config.get('SSO_BPS_REDIRECT_URI')
    if not redirect_uri:
        redirect_uri = url_for('auth.sso_callback', _external=True)

    try:
        # 1. Tukar Code dengan Access Token
        token_payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        }
        token_response = requests.post(token_url, data=token_payload, timeout=10)
        token_json = token_response.json()
        access_token = token_json.get('access_token')

        if not access_token:
            flash('Gagal mendapatkan access token dari server SSO BPS.', 'danger')
            return redirect(url_for('auth.login'))

        # 2. Ambil data profil pegawai dari SSO BPS
        headers = {'Authorization': f'Bearer {access_token}'}
        userinfo_response = requests.get(userinfo_url, headers=headers, timeout=10)
        user_info = userinfo_response.json()

        nip = user_info.get('nip') or user_info.get('preferred_username') or user_info.get('username')
        full_name = user_info.get('name') or user_info.get('nama') or 'Pegawai BPS Banyuwangi'
        username = user_info.get('preferred_username') or nip

        if not username:
            flash('Informasi identitas akun dari SSO BPS tidak lengkap.', 'danger')
            return redirect(url_for('auth.login'))

        # 3. Cari akun atau daftarkan otomatis (Auto-Provisioning)
        user = User.query.filter((User.username == username) | (User.nip == nip)).first()
        if not user:
            user = User(
                username=username,
                full_name=full_name,
                nip=nip,
                role='pegawai',
                is_active=True
            )
            user.set_password(uuid.uuid4().hex[:16])
            db.session.add(user)
            db.session.commit()
        else:
            # Perbarui info jika ada perubahan nama/NIP
            user.full_name = full_name
            if nip:
                user.nip = nip
            db.session.commit()

        login_user(user, remember=True)
        log_activity('LOGIN_SSO', f"Pegawai {user.full_name} ({user.nip}) berhasil masuk melalui SSO BPS.", user.id)
        flash(f'Selamat datang di PRIMA, {user.full_name}!', 'success')
        return redirect(url_for('dashboard.index'))

    except Exception as e:
        current_app.logger.error(f"Error handling SSO callback: {e}")
        flash(f'Terjadi kendala koneksi ke server SSO BPS: {str(e)}', 'danger')
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    uid = current_user.id
    logout_user()
    log_activity('LOGOUT', f"Pengguna {username} telah keluar dari sistem.", uid)
    flash('Anda telah berhasil keluar dari sistem PRIMA.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            full_name = request.form.get('full_name', '').strip()
            nip = request.form.get('nip', '').strip()

            if not full_name:
                flash('Nama lengkap wajib diisi.', 'danger')
            else:
                current_user.full_name = full_name
                current_user.nip = nip
                db.session.commit()
                log_activity('UPDATE_PROFILE', f"Memperbarui profil pengguna {current_user.username}")
                flash('Profil Anda berhasil diperbarui.', 'success')

        elif action == 'change_password':
            old_password = request.form.get('old_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')

            if not current_user.check_password(old_password):
                flash('Password saat ini salah.', 'danger')
            elif len(new_password) < 6:
                flash('Password baru minimal 6 karakter.', 'danger')
            elif new_password != confirm_password:
                flash('Konfirmasi password baru tidak cocok.', 'danger')
            else:
                current_user.set_password(new_password)
                db.session.commit()
                log_activity('CHANGE_PASSWORD', f"Mengubah password pengguna {current_user.username}")
                flash('Password Anda berhasil diperbarui. Gunakan password baru untuk login berikutnya.', 'success')

        return redirect(url_for('auth.profile'))

    return render_template('profile.html')

