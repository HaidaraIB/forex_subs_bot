from sqlalchemy import Column, Integer, String, TIMESTAMP, func, select, insert
from models.DB import Base, connect_and_close, lock_and_release
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


class Code(Base):
    __tablename__ = "codes"
    code = Column(String, primary_key=True)
    user_id = Column(Integer, default=0)
    period = Column(String)
    creation_date = Column(TIMESTAMP, server_default=func.current_timestamp())
    starts_at = Column(TIMESTAMP)
    ends_at = Column(TIMESTAMP)

    @classmethod
    @lock_and_release
    async def add(cls, code: str, user_id: int, period: str, s: Session = None):
        try:
            s.execute(
                insert(cls).values(
                    code=code,
                    user_id=user_id,
                    period=period,
                )
            )
            return True
        except IntegrityError:
            return False

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
            res = s.execute(select(cls).where(cls.code == code))
            try:
                return res.fetchone().t[0]
            except:
                pass

        elif user_id:
            res = s.execute(select(cls).where(cls.user_id == user_id))
            try:
                return list(map(lambda x: x[0], res.tuples().all()))
            except:
                pass
            
        elif unique_period == True:
            res = s.execute(select(cls.period).distinct())
            try:
                return list(map(lambda x: x[0], res.tuples().all()))
            except:
                pass

        elif used is not None:
            res = s.execute(
                select(cls).where(cls.user_id == 0 if not used else cls.user_id != 0)
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
