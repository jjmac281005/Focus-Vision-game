import sys
import os
from unittest.mock import Mock

# ✅ mock library berat
sys.modules['cv2'] = Mock()
sys.modules['mediapipe'] = Mock()

# ✅ fix path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app import create_app


@pytest.fixture
def client():
    mock_db = Mock()

    app = create_app({
        "TESTING": True,
        "DB": mock_db,
        "SECRET_KEY": "test"
    })

    with app.test_client() as client:
        yield client