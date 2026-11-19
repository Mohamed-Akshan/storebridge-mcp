from pwdlib import PasswordHash
from sqlalchemy import select

from core.config import settings
from database.auth_connection import SessionLocal, engine
from database.auth_models import AuthBase, User


def main():
    if not settings.owner_password or settings.owner_password.startswith("change-this"):
        raise RuntimeError("Set a strong OWNER_PASSWORD in .env first")

    AuthBase.metadata.create_all(bind=engine)

    with SessionLocal.begin() as db:
        existing = db.scalar(
            select(User).where(User.username == settings.owner_username)
        )

        if existing:
            print("Owner already exists; credentials were not changed.")
            return

        owner = User(
            username=settings.owner_username,
            full_name="Walk & Talk Owner",
            password_hash=PasswordHash.recommended().hash(settings.owner_password),
            role="admin",
            active=True,
        )

        db.add(owner)

    print("Owner account created.")


if __name__ == "__main__":
    main()
