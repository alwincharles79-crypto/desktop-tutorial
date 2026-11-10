import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from validation import validate_student

class StudentValidationTests(unittest.TestCase):
    def test_valid_student(self):
        self.assertEqual(validate_student("Aarav Sharma", "aarav@example.com", "9876543210", "BBA"), [])
    def test_blank_name(self):
        self.assertTrue(validate_student(" ", "aarav@example.com", "9876543210", "BBA"))
    def test_invalid_phone(self):
        self.assertTrue(validate_student("Aarav Sharma", "aarav@example.com", "5123456789", "BBA"))
    def test_invalid_email(self):
        self.assertTrue(validate_student("Aarav Sharma", "not-an-email", "9876543210", "BBA"))
    def test_missing_course(self):
        self.assertTrue(validate_student("Aarav Sharma", "aarav@example.com", "9876543210", " "))

if __name__ == "__main__":
    unittest.main()
