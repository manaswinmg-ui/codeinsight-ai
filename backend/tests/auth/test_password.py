from app.auth.password import password_service


def test_password_hashing() -> None:
    password = "SuperSecurePassword123!"
    hashed = password_service.hash_password(password)

    assert hashed != password
    assert len(hashed) > 20
    assert password_service.verify_password(password, hashed)
    assert not password_service.verify_password("wrong_password", hashed)
