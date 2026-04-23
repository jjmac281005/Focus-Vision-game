import unittest
from unittest.mock import Mock
from services.user_service import UserService


class TestUserService(unittest.TestCase):

    def setUp(self):
        self.mock_db = Mock()
        self.service = UserService(self.mock_db)

    def test_user_not_found(self):
        cursor = self.mock_db.cursor.return_value
        cursor.fetchone.return_value = None

        result = self.service.save_score("a@mail.com", "game", 10)
        self.assertFalse(result)

    def test_user_found_success_insert(self):
        cursor = self.mock_db.cursor.return_value
        cursor.fetchone.return_value = {"user_id": 1}

        result = self.service.save_score("a@mail.com", "game", 10)

        self.assertTrue(result)
        self.mock_db.commit.assert_called_once()

    def test_cursor_called(self):
        cursor = self.mock_db.cursor.return_value
        cursor.fetchone.return_value = {"user_id": 1}  # 🔥 WAJIB

        self.service.save_score("a@mail.com", "game", 10)

        self.mock_db.cursor.assert_called_once()

    def test_insert_query_called(self):
        cursor = self.mock_db.cursor.return_value
        cursor.fetchone.return_value = {"user_id": 1}

        self.service.save_score("a@mail.com", "game", 10)

        cursor.execute.assert_called()

    def test_email_parameter_passed(self):
        cursor = self.mock_db.cursor.return_value
        cursor.fetchone.return_value = {"user_id": 1}

        self.service.save_score("test@mail.com", "game", 10)

        cursor.execute.assert_any_call(
            "SELECT user_id FROM users WHERE email=%s",
            ("test@mail.com",)
        )

    def test_score_value(self):
        cursor = self.mock_db.cursor.return_value
        cursor.fetchone.return_value = {"user_id": 1}

        self.service.save_score("a@mail.com", "game", 99)

        args = cursor.execute.call_args_list[-1][0][1]
        assert args[2] == 99

    def test_game_name_value(self):
        cursor = self.mock_db.cursor.return_value
        cursor.fetchone.return_value = {"user_id": 1}

        self.service.save_score("a@mail.com", "barrel", 10)

        args = cursor.execute.call_args_list[-1][0][1]
        assert args[1] == "barrel"

    def test_commit_called_once(self):
        cursor = self.mock_db.cursor.return_value
        cursor.fetchone.return_value = {"user_id": 1}

        self.service.save_score("a@mail.com", "game", 10)

        self.mock_db.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()