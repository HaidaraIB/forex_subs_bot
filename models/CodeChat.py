import sqlalchemy as sa
from sqlalchemy.orm import Session
from models.DB import Base, connect_and_close, lock_and_release


class CodeChat(Base):
    __tablename__ = "code_chats"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    chat_id = sa.Column(sa.ForeignKey("chats.chat_id", ondelete="CASCADE"))
    code = sa.Column(sa.ForeignKey("codes.code", ondelete="CASCADE"))

    @classmethod
    @lock_and_release
    async def add(cls, code_chats: list[dict], s: Session = None):
        s.execute(sa.insert(cls).values(code_chats))

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
