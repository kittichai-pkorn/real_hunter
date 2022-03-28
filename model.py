from enum import Enum
from sqlalchemy import Column, Integer, Boolean, String
from sqlalchemy.ext.automap import automap_base

Base = automap_base()

class Result(Base):
    __tablename__ = "Result"

    id = Column(Integer, primary_key=True)
    category = Column(String)
    date = Column(String)
    six_top = Column(String)
    close_at = Column(String)
    three_top = Column(String)
    two_top = Column(String)
    two_under = Column(String)
    three_front = Column(String)
    three_back = Column(String)
    close_time = Column(String)
    is_cancel = Column(Boolean)

class Slug(Enum):
    TWO_TOP = "two_top"

class Stake:
    slug: Slug
    number: str
    price: int
    rate: int

    def __init__(self, slug: Slug, number: str, price: int, rate: int) -> None:
        self.slug = slug
        self.number = number
        self.price = price
        self.rate = rate
