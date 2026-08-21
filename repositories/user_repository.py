from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.users import User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, password: str) -> User:
    db_user = User(
        email=email,
        password=password,
    )

    db.add(db_user)

    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise
