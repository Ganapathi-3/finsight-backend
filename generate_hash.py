from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

print("Admin hash:")
print(pwd_context.hash("admin123"))

print("\nFinance hash:")
print(pwd_context.hash("finance123"))

print("\nHR hash:")
print(pwd_context.hash("hr123"))

print("\nExecutive hash:")
print(pwd_context.hash("executive123"))