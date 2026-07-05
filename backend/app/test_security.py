from security import *

password = "123456"

hashed = hash_password(password)

print("Password : ", password)

print("Hash : ", hashed)

print()

print(
    verify_password(
        "123456",
        hashed
    )
)

token = create_access_token(
    {
        "username": "Ahmed"
    }
)

print()

print(token)

print()

print(
    verify_token(token)
)