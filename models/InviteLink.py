from sqlalchemy import Column, Boolean, String, TIMESTAMP, Integer, select, insert
from models.DB import Base, connect_and_close, lock_and_release
from sqlalchemy.orm import Session
from datetime import datetime
from common.constants import *
class InviteLink(Base):
    __tablename__ = "invite_links"
    link = Column(String, primary_key=True)
    used = Column(Boolean, default=False)
    code = Column(String)
    user_id = Column(Integer)
    use_date = Column(TIMESTAMP)

    @classmethod
    @lock_and_release
    async def add(cls, link: str, code: str, user_id: int, s: Session = None):
        s.execute(
            insert(cls).values(
                link=link,
                code=code,
                user_id=user_id,
            )
        )

    @classmethod
    @connect_and_close
    def get_by(
        cls,
        code: str = None,
        link: str = None,
        used: bool = None,
        s: Session = None,
    ):
        if code:
            res = s.execute(select(cls).where(cls.code == code))
            try:
                return res.fetchone().t[0]
            except:
                pass

        elif link:
            res = s.execute(select(cls).where(cls.link == link))
            try:
                return res.fetchone().t[0]
            except:
                pass

        elif used is not None:
            res = s.execute(select(cls).where(cls.used == used))
            try:
                return list(map(lambda x: x[0], res.tuples().all()))
            except:
                pass

    @classmethod
    @lock_and_release
    async def use(
        cls,
        invite_link: str,
        s: Session = None,
    ):
        s.query(cls).filter_by(link=invite_link).update(
            {cls.used: True, cls.use_date: datetime.now(TIMEZONE)}
        )
