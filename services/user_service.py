class UserService:
    def __init__(self, db):
        self.db = db

    def get_user_by_email(self, email):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        return cursor.fetchone()

    def save_score(self, email, game_name, score):
        cursor = self.db.cursor(dictionary=True)

        cursor.execute("SELECT user_id FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if not user:
            return False

        cursor.execute("""
            INSERT INTO game_scores (user_id, game_name, score)
            VALUES (%s, %s, %s)
        """, (user["user_id"], game_name, score))

        self.db.commit()
        return True