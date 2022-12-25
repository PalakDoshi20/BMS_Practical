
from sqlalchemy import *
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from sqlalchemy_utils import EmailType
# import sqlalchemy_utils
from sqlalchemy import create_engine
PGUSER = 'authentication_user_user'
PGPASSWORD = 'tUOoDqqHrkr46yqASLN1YhIPSPmDUVNF'
PGHOST = 'dpg-cek2l9ta4991ihg50reg-a.oregon-postgres.render.com'
PGPORT = '5432'
PGDATABASE = 'authentication_user'
db_string = f"postgresql://{ PGUSER }:{ PGPASSWORD }@{ PGHOST }:{ PGPORT }/{ PGDATABASE }"


db = create_engine(db_string)

Base = declarative_base()

import sqlalchemy.types as types

class ChoiceType(types.TypeDecorator):

    impl = types.String

    def __init__(self, choices, **kw):
        self.choices = dict(choices)
        super(ChoiceType, self).__init__(**kw)

    def process_bind_param(self, value, dialect):
        return [k for k, v in self.choices.iteritems() if v == value][0]

    def process_result_value(self, value, dialect):
        return self.choices[value]


class User(Base):
    GENDER = {
        'Female': 'Female',
        'Male': 'Male',
        'Other': 'Other'
    }
    USERTYPES = {
        'Primary': 'Primary',
        'Secondary': 'Secondary'
    }

    __tablename__= 'users'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(80))
    last_name = Column(String(80))
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    date_of_birth = Column(Date)
    password = Column(String(16))
    confirm_password = Column(String(16))
    gender = Column(ChoiceType(GENDER))
    usertype = Column(ChoiceType(USERTYPES))
    is_authenticated = Column(Boolean, default=False)

Session = sessionmaker(db)
session = Session()

Base.metadata.create_all(db)
