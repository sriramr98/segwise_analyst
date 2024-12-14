from collections import defaultdict
from sqlalchemy import BigInteger, Date, create_engine, Column, Integer, String, Float, Boolean, Text
from sqlalchemy.dialects.postgresql import ARRAY, Any
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Any as AnyType
import os

# Database Connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres:testpwd@localhost/gamedb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class GameData(Base):
    __tablename__ = "game_data"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(BigInteger)
    name = Column(String)
    release_date = Column(Date)
    required_age = Column(Integer)
    price = Column(Float)
    dlc_count = Column(Integer)
    about_the_game = Column(Text)
    supported_languages = Column(ARRAY(String))
    windows = Column(Boolean)
    mac = Column(Boolean)
    linux = Column(Boolean)
    positive_reviews = Column(Integer)
    negative_reviews = Column(Integer)
    score_rank = Column(Float)
    developers = Column(String)
    publishers = Column(String)
    categories = Column(ARRAY(String))
    genres = Column(ARRAY(String))
    tags = Column(ARRAY(String))


column_name_map: dict[str, Column[AnyType]] = defaultdict(None)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

    column_name_map['AppId'] = GameData.app_id
    column_name_map['Name'] = GameData.name
    column_name_map['Release date'] = GameData.release_date
    column_name_map['Required age'] = GameData.required_age
    column_name_map['Price'] = GameData.price
    column_name_map['DLC count'] = GameData.dlc_count
    column_name_map['About the game'] = GameData.about_the_game
    column_name_map['Supported languages'] = GameData.supported_languages
    column_name_map['Windows'] = GameData.windows
    column_name_map['Mac'] = GameData.mac
    column_name_map['Linux'] = GameData.linux
    column_name_map['Positive'] = GameData.positive_reviews
    column_name_map['Negative'] = GameData.negative_reviews
    column_name_map['Score rank'] = GameData.score_rank
    column_name_map['Developers'] = GameData.developers
    column_name_map['Publishers'] = GameData.publishers
    column_name_map['Categories'] = GameData.categories
    column_name_map['Genres'] = GameData.genres
    column_name_map['Tags'] = GameData.tags

def getNameToColumnMap():
    return column_name_map
