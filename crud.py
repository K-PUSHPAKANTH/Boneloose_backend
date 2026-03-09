from sqlalchemy.orm import Session
from models import User

def create_user(db: Session, user):

    db_user = User(
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        password=user.password,   # store directly
        role=user.role,
        is_verified=True
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    # Direct comparison (NO bcrypt)
    if user.password != password:
        return None

    return user
