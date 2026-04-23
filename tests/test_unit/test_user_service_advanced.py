import unittest
from unittest.mock import Mock, call
from services.user_service import UserService


class TestUserServiceAdvanced(unittest.TestCase):

    def setUp(self):
        self.mock_db = Mock()
        self.mock_cursor = Mock()
        self.mock_db.cursor.return_value = self.mock_cursor
        self.service = UserService(self.mock_db)

    # =========================
    # EDGE CASE: USER NOT FOUND
    # =========================
    def test_save_score_user_not_found_no_insert(self):
        self.mock_cursor.fetchone.return_value = None

        result = self.service.save_score("x@mail.com", "game", 10)

        self.assertFalse(result)

        # pastikan INSERT tidak pernah dipanggil
        insert_calls = [
            call for call in self.mock_cursor.execute.call_args_list
            if "INSERT INTO game_scores" in call[0][0]
        ]
        self.assertEqual(len(insert_calls), 0)

    # =========================
    # VERIFY QUERY ORDER
    # =========================
    def test_query_execution_order(self):
        self.mock_cursor.fetchone.return_value = {"user_id": 1}

        self.service.save_score("a@mail.com", "game", 10)

        calls = self.mock_cursor.execute.call_args_list

        self.assertIn("SELECT user_id FROM users", calls[0][0][0])
        self.assertIn("INSERT INTO game_scores", calls[1][0][0])

    # =========================
    # MULTIPLE CALL SAFETY
    # =========================
    def test_multiple_calls_commit_called_multiple_times(self):
        self.mock_cursor.fetchone.return_value = {"user_id": 1}

        self.service.save_score("a@mail.com", "game", 10)
        self.service.save_score("a@mail.com", "game", 20)

        self.assertEqual(self.mock_db.commit.call_count, 2)

    # =========================
    # INVALID SCORE (EDGE CASE)
    # =========================
    def test_negative_score(self):
        self.mock_cursor.fetchone.return_value = {"user_id": 1}

        result = self.service.save_score("a@mail.com", "game", -10)

        # tetap boleh, tapi kita cek value masuk
        args = self.mock_cursor.execute.call_args_list[-1][0][1]
        self.assertEqual(args[2], -10)

    # =========================
    # EMPTY GAME NAME
    # =========================
    def test_empty_game_name(self):
        self.mock_cursor.fetchone.return_value = {"user_id": 1}

        result = self.service.save_score("a@mail.com", "", 10)

        args = self.mock_cursor.execute.call_args_list[-1][0][1]
        self.assertEqual(args[1], "")

    # =========================
    # DB FAILURE (EXCEPTION)
    # =========================
    def test_db_exception_handling(self):
        self.mock_cursor.execute.side_effect = Exception("DB Error")

        with self.assertRaises(Exception):
            self.service.save_score("a@mail.com", "game", 10)

    # =========================
    # VERIFY EXACT INSERT DATA
    # =========================
    def test_insert_exact_values(self):
        self.mock_cursor.fetchone.return_value = {"user_id": 99}

        self.service.save_score("user@mail.com", "pencil", 50)

        insert_call = self.mock_cursor.execute.call_args_list[-1]

        query = insert_call[0][0]
        params = insert_call[0][1]

        self.assertEqual(params, (99, "pencil", 50))

    # =========================
    # CURSOR USED ONLY ONCE
    # =========================
    def test_cursor_reuse(self):
        self.mock_cursor.fetchone.return_value = {"user_id": 1}

        self.service.save_score("a@mail.com", "game", 10)

        self.mock_db.cursor.assert_called_once()

    # =========================
    # NO COMMIT IF USER NOT FOUND
    # =========================
    def test_no_commit_if_user_not_found(self):
        self.mock_cursor.fetchone.return_value = None

        self.service.save_score("a@mail.com", "game", 10)

        self.mock_db.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()