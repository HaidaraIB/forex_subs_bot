from sqlalchemy import (
    PrimaryKeyConstraint,
    Column,
    Boolean,
    select,
    insert,
)
from models.DB import (
    connect_and_close,
    lock_and_release,
)
from sqlalchemy.orm import Session
from models.BaseUser import BaseUser


class User(BaseUser):
    is_banned = Column(Boolean, default=0)
    __tablename__ = "users"
    __table_args__ = (PrimaryKeyConstraint("id", name="_id_user"),)

    @staticmethod
    @lock_and_release
    async def add_new_user(user_id: int, username: str, name: str, s: Session = None):
        s.execute(
            insert(User)
            .values(id=user_id, username=username if username else "", name=name)
            .prefix_with("OR IGNORE")
        )

    @staticmethod
    @connect_and_close
    def get_all_users(s: Session = None):
        res = s.execute(select(User))
        try:
            return list(map(lambda x: x[0], res.tuples().all()))
        except:
            pass

    @staticmethod
    @connect_and_close
    def get_user(user_id: int, s: Session = None):
        res = s.execute(select(User).where(User.id == user_id))
        try:
            return res.fetchone().t[0]
        except:
            pass

    @staticmethod
    @lock_and_release
    async def set_banned(user_id: int, banned: bool, s: Session = None):
        s.query(User).filter_by(id=user_id).update(
            {
                User.is_banned: banned,
            },
        )
