from flask import Blueprint, render_template
from flask_login import login_required

info_bp = Blueprint('info', __name__)

@info_bp.route('/about')
@login_required
def about():
    return render_template('info/about.html')

@info_bp.route('/guide')
@login_required
def guide():
    return render_template('info/guide.html')

