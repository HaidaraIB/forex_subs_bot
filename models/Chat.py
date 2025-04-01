import sqlalchemy as sa
from sqlalchemy.orm import Session
from models.DB import Base, connect_and_close, lock_and_release


class Chat(Base):
    __tablename__ = "chats"
    chat_id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String)
    name = sa.Column(sa.String)

    @classmethod
    @lock_and_release
    async def add(cls, chat_id: int, username: str, name: str, s: Session = None):
        s.execute(sa.insert(cls).values(chat_id=chat_id, username=username, name=name))

    @classmethod
    @connect_and_close
    def get(cls, attr=None, val=None, all: bool = False, s: Session = None):
        if attr and val:
            res = s.execute(sa.select(cls).where(getattr(cls, attr) == val))
            try:
                if all:
                    return list(map(lambda x: x[0], res.tuples().all()))
                return res.fetchone().t[0]
            except:
                return
        res = s.execute(sa.select(cls))
        try:
            return list(map(lambda x: x[0], res.tuples().all()))
        except:
            pass

    @classmethod
    @lock_and_release
    async def delete(cls, chat_id: int, s: Session = None):
        s.execute(sa.delete(cls).where(cls.chat_id == chat_id))
