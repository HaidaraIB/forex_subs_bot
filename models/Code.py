import sqlalchemy as sa
from models.DB import Base, connect_and_close, lock_and_release
from sqlalchemy.orm import Session, relationship
from sqlalchemy.exc import IntegrityError


class Code(Base):
    __tablename__ = "codes"
    code = sa.Column(sa.String, primary_key=True)
    user_id = sa.Column(sa.Integer, default=0)
    period = sa.Column(sa.String)
    creation_date = sa.Column(sa.TIMESTAMP, server_default=sa.func.current_timestamp())
    starts_at = sa.Column(sa.TIMESTAMP)
    ends_at = sa.Column(sa.TIMESTAMP)

    chats = relationship("Chat", secondary="code_chats", back_populates="codes")

    @classmethod
    @lock_and_release
    async def add(cls, codes , s: Session = None):
        s.add_all(codes)

    @classmethod
    @connect_and_close
    def get_by(
        cls,
        code: str = None,
        user_id: int = None,
        used: bool = None,
        unique_period: bool = None,
        s: Session = None,
    ):
        if code:
            res = s.execute(sa.select(cls).where(cls.code == code))
            try:
                return res.fetchone().t[0]
            except:
                pass

        elif user_id:
            res = s.execute(sa.select(cls).where(cls.user_id == user_id))
            try:
                return list(map(lambda x: x[0], res.tuples().all()))
            except:
                pass

        elif unique_period == True:
            res = s.execute(sa.select(cls.period).distinct())
            try:
                return list(map(lambda x: x[0], res.tuples().all()))
            except:
                pass

        elif used is not None:
            res = s.execute(
                sa.select(cls).where(cls.user_id == 0 if not used else cls.user_id != 0)
            )
            try:
                return list(map(lambda x: x[0], res.tuples().all()))
            except:
                pass

    @classmethod
    @lock_and_release
    async def use(
        cls,
        code: str,
        user_id: int,
        starts_at,
        ends_at,
        s: Session = None,
    ):
        s.query(cls).filter_by(code=code).update(
            {
                cls.user_id: user_id,
                cls.starts_at: starts_at,
                cls.ends_at: ends_at,
            }
        )

    @classmethod
    @lock_and_release
    async def delete(cls, codes: list[str], s: Session = None):
        s.execute(sa.delete(cls).where(cls.code.in_(codes)))
