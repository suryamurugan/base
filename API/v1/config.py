from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SECRET_KEY = "jdhfybfhyhdbvdsb"
host = "bd8ih6ugkiburcgucmhm-mysql.services.clever-cloud.com"
user = "usub4dgq5i9lkeox"
password = "k00QldxXzeMuvFU4YHWg"
database = "bd8ih6ugkiburcgucmhm"
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}", echo=True)

Session = sessionmaker(bind=engine)

Base = declarative_base()


