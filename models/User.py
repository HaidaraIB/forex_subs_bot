from sqlalchemy import PrimaryKeyConstraint, Column, Boolean, String, select, insert
from models.DB import connect_and_close, lock_and_release
from sqlalchemy.orm import Session
from models.BaseUser import BaseUser


class User(BaseUser):
    is_banned = Column(Boolean, default=0)
    cur_sub = Column(String)
    __tablename__ = "users"
    __table_args__ = (
        PrimaryKeyConstraint(
            "id",
            name="_id_user",
        ),
    )

    @staticmethod
    @lock_and_release
    async def add_new_user(user_id: int, username: str, name: str, s: Session = None):
        s.execute(
            insert(User)
            .values(id=user_id, username=username if username else "", name=name)
            .prefix_with("OR IGNORE")
        )

    @classmethod
    @connect_and_close
    def get_users(
        cls,
        user_id: int = None,
        subsicribers: bool = None,
        s: Session = None,
    ):
        if user_id:
            res = s.execute(select(cls).where(cls.id == user_id))
            try:
                return res.fetchone().t[0]
            except:
                pass
        elif subsicribers is not None:
            res = s.execute(
                select(cls).where(
                    (cls.cur_sub != None) if subsicribers else (cls.cur_sub == None)
                )
            )
            try:
                return list(map(lambda x: x[0], res.tuples().all()))
            except:
                pass

        res = s.execute(select(cls))
        try:
            return list(map(lambda x: x[0], res.tuples().all()))
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

    @classmethod
    @lock_and_release
    async def add_sub(cls, user_id: int, sub: str, s: Session = None):
        s.query(cls).filter_by(id=user_id).update({cls.cur_sub: sub})
