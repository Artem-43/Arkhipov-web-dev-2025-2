import click
from flask import current_app
from flask.cli import with_appcontext
from .db_instance import db

@click.command('init-db')
@with_appcontext
def init_db_command():
    with current_app.open_resource('schema.sql') as f:
        connection = db.connect()
        with connection.cursor() as cursor:
            for _ in cursor.execute(f.read().decode('utf8'), multi=True):
                pass
            connection.commit()
        click.echo('Initialized database')
