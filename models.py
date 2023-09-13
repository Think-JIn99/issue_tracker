from sqlalchemy import Column, String, TIMESTAMP, BigInteger, ForeignKey, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Newses(Base):
    __tablename__ = "newses"
    id = Column(BigInteger, primary_key=True)
    category = Column(String(10), nullable=False)
    title = Column(String(100), nullable=False)
    summary = Column(String(200), nullable=False)
    office_name = Column(String(20), nullable=False)
    service_time = Column(BigInteger, nullable=False)  # unix 타임
    created_at = Column(TIMESTAMP, default=func.now())
    url = Column(String(400), nullable=False)
