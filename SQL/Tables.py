import datetime
from typing import List

from sqlalchemy import (
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship, sessionmaker,
)
from sqlalchemy.types import (
    Integer,
    BigInteger,
    String,
    Text,
)

from sqlalchemy import create_engine


class SQLiteBase(DeclarativeBase):
    pass


class Admins(SQLiteBase):
    __tablename__ = 'admins'

    id = mapped_column(BigInteger(), primary_key=True, index=True)


class Users(SQLiteBase):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    firstname: Mapped[str] = mapped_column(String(50), nullable=False)

    characters: Mapped['Characters'] = relationship(back_populates='users', primaryjoin='Users.id == Characters.user_id')
    gamestories: Mapped['GameStories'] = relationship(back_populates='users', primaryjoin='Users.id == GameStories.gm_id')
    selectedcharacters: Mapped['SelectedCharacters'] = relationship(back_populates='users', primaryjoin='Users.id == SelectedCharacters.player_id')
    playersstories: Mapped['PlayersStories'] = relationship(back_populates='users', primaryjoin='Users.id == PlayersStories.player_id')


class Verify(SQLiteBase):
    __tablename__ = 'verify'

    user_id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, index=True)
    gmail: Mapped[str] = mapped_column(String(100), nullable=False)

    # character: Mapped[List['Users']] = relationship(back_populates='Verify')


class Characters(SQLiteBase):
    __tablename__ = 'characters'

    id: Mapped[str] = mapped_column(String(250), primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger(), ForeignKey('users.id'), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    link: Mapped[str] = mapped_column(String(500), nullable=False)

    users: Mapped[List['Users']] = relationship(back_populates='characters')
    selectedcharacters: Mapped[List['SelectedCharacters']] = relationship(back_populates='characters')


class GameStories(SQLiteBase):
    __tablename__ = 'gamestories'
    # chat_id группы в телеграмме
    id: Mapped[str] = mapped_column(String(50), primary_key=True, nullable=False)
    gm_id: Mapped[int] = mapped_column(BigInteger(), ForeignKey('users.id'), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)

    users: Mapped[List['Users']] = relationship(back_populates='gamestories')
    selectedcharacters: Mapped[List['SelectedCharacters']] = relationship(back_populates='gamestories')
    playersstories: Mapped[List['PlayersStories']] = relationship(back_populates='gamestories')
    # activity: Mapped['Characters'] = relationship(back_populates='groups')


# TODO (autoincrement = -True- -> "auto")
class PlayersStories(SQLiteBase):
    __tablename__ = 'playersstories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement="auto")
    player_id: Mapped[int] = mapped_column(BigInteger(), ForeignKey('users.id'), nullable=False)
    story_id: Mapped[str] = mapped_column(String(50), ForeignKey('gamestories.id'), nullable=False)

    # characters: Mapped[List['SelectedCharacters']] = relationship(back_populates='playersstories')
    gamestories: Mapped[List['GameStories']] = relationship(back_populates='playersstories')
    users: Mapped[List['Users']] = relationship(back_populates='playersstories')


class SelectedCharacters(SQLiteBase):
    __tablename__ = 'selectedcharacters'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    story_id: Mapped[str] = mapped_column(String(50), ForeignKey('gamestories.id'), nullable=False)
    character_id: Mapped[str] = mapped_column(String(250), ForeignKey('characters.id'), nullable=False)
    player_id: Mapped[int] = mapped_column(BigInteger(), ForeignKey('users.id'), nullable=False)

    gamestories: Mapped[List['GameStories']] = relationship(back_populates='selectedcharacters')
    characters: Mapped[List['Characters']] = relationship(back_populates='selectedcharacters')
    users: Mapped[List['Users']] = relationship(back_populates='selectedcharacters')


# user = 'root'
# password = ''
# host = '127.0.0.1'
# port = 3306
# database = 'DndBase'


def new_engine():
    # return create_engine(url="mysql+mysqlconnector://{0}:{1}@{2}:{3}/{4}".format(
    #         user, password, host, port, database))
    return create_engine('sqlite:///file/db/dndbase.sqlite3')


def create_tables():
    engine = new_engine()
    SQLiteBase.metadata.create_all(bind=engine)


create_tables()


mysql_engine = new_engine()
MySQLSession = sessionmaker(bind=mysql_engine)
