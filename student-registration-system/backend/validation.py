import re

EMAIL_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+$")


def validate_student(name: str, email: str, phone: str, course: str):
    errors = []
    if not name.strip() or len(name.strip()) < 2:
        errors.append("Student name must contain at least 2 characters.")
    if not EMAIL_RE.fullmatch(email.strip()):
        errors.append("Enter a valid email address.")
    if not phone.isdigit() or len(phone) != 10 or phone[0] not in "6789":
        errors.append("Enter a valid 10-digit Indian mobile number starting with 6, 7, 8 or 9.")
    if not course.strip():
        errors.append("Course is required.")
    return errors
