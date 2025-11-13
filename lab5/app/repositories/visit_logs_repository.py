class VisitLogRepository:
    def __init__(self, db_connector):
        self.db_connector = db_connector

    def create(self, path, user_id=None):
        connection = self.db_connector.connect()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                "INSERT INTO visit_logs (path, user_id) VALUES (%s, %s);", (path, user_id)
            )
        connection.commit()

    def all(self, user_id=None, limit=20, offset=0):
        with self.db_connector.connect().cursor(dictionary=True) as cursor:
            if user_id:
                cursor.execute(
                    """
                    SELECT visit_logs.*, users.first_name, users.last_name, users.middle_name
                    FROM visit_logs
                    LEFT JOIN users ON users.id = visit_logs.user_id
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """, (user_id, limit, offset)
                )
            else:
                cursor.execute(
                    """
                    SELECT visit_logs.*, users.first_name, users.last_name, users.middle_name FROM visit_logs
                    LEFT JOIN users ON users.id = visit_logs.user_id
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """, (limit, offset)
                )
            return cursor.fetchall()

    def count(self, user_id=None):
        with self.db_connector.connect().cursor(dictionary=True) as cursor:
            if user_id:
                cursor.execute("SELECT COUNT(*) AS total FROM visit_logs WHERE user_id = %s;", (user_id,))
            else:
                cursor.execute("SELECT COUNT(*) AS total FROM visit_logs;")
            row = cursor.fetchone()
            return row['total']

    def stats_by_page(self):
        with self.db_connector.connect().cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT path, COUNT(*) AS visits
                FROM visit_logs
                GROUP BY path
                ORDER BY visits DESC
            """)
            return cursor.fetchall()

    def stats_by_user(self):
        with self.db_connector.connect().cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT COALESCE(CONCAT(users.last_name, ' ', users.first_name, ' ', users.middle_name), 'Неаутентифицированный пользователь') AS username,
                       COUNT(*) AS visits FROM visit_logs
                LEFT JOIN users ON users.id = visit_logs.user_id
                GROUP BY username
                ORDER BY visits DESC
            """)
            return cursor.fetchall()

    def clear_all(self):
        connection = self.db_connector.connect()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM visit_logs;")
        connection.commit()