from flask import render_template, request, send_file, Blueprint, make_response
from flask_login import login_required, current_user
from .repositories.visit_logs_repository import VisitLogRepository
from .db_instance import db
from .auth import check_rights
import csv
from io import StringIO

def export_to_csv(rows, header, filename):
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)

    output = make_response(si.getvalue())
    output.headers['Content-Disposition'] = f'attachment; filename={filename}'
    output.headers['Content-type'] = 'text/csv'
    return output

repository = VisitLogRepository(db)

bp = Blueprint('session_log', __name__, url_prefix='/session_log')


@bp.route('/')
@login_required
def main():
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page

    if current_user.role == 'admin':
        logs = repository.all(limit=per_page, offset=offset)
        total = repository.count()
    else:
        logs = repository.all(user_id=current_user.id, limit=per_page, offset=offset)
        total = repository.count(user_id=current_user.id)

    return render_template('session_log/main.html', logs=logs, page=page, total=total, per_page=per_page)


@bp.route('/report/pages')
@login_required
@check_rights('view_logs')
def report_pages():
    stats = repository.stats_by_page()
    return render_template('session_log/report_pages.html', stats=stats)


@bp.route('/report/users')
@login_required
@check_rights('view_logs')
def report_users():
    stats = repository.stats_by_user()
    return render_template('session_log/report_users.html', stats=stats)


@bp.route('/report/pages/export')
@login_required
@check_rights('view_logs')
def export_pages_csv():
    rows = repository.stats_by_page()
    rows = [(i + 1, row['path'], row['visits']) for i, row in enumerate(rows)]
    header = ['№', 'Страница', 'Количество посещений']
    return export_to_csv(rows, header, 'report_pages.csv')


@bp.route('/report/users/export')
@login_required
@check_rights('view_logs')
def export_users_csv():
    rows = repository.stats_by_user()
    rows = [(i + 1, row['username'], row['visits']) for i, row in enumerate(rows)]
    header = ['№', 'Пользователь', 'Количество посещений']
    return export_to_csv(rows, header, 'report_users.csv')