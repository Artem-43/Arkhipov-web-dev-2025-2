import os

from flask import Flask, session, request
from flask_login import current_user
from .db_instance import db
from .repositories.visit_logs_repository import VisitLogRepository

def inject_current_user():
    return dict(current_user=current_user)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile('config.py', silent=False)

    if test_config:
        app.config.from_mapping(test_config)

    db.init_app(app)

    from .cli import init_db_command
    app.cli.add_command(init_db_command)

    from . import auth
    app.register_blueprint(auth.bp)
    auth.login_manager.init_app(app)

    from . import users
    app.register_blueprint(users.bp)
    app.route('/', endpoint='index')(users.index)

    from . import session_log
    app.register_blueprint(session_log.bp)

    repository_session_log = VisitLogRepository(db)

    @app.before_request
    def log_visit():
        if request.path != '/favicon.ico' and request.endpoint != 'static':
            user_id = current_user.id if current_user.is_authenticated else None
            repository_session_log.create(request.path, user_id)

    app.context_processor(inject_current_user)

    return app