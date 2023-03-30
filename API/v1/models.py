from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, CheckConstraint, BigInteger
from config import Base
from datetime import datetime
import json
cardLevels = (0,1)
cardStatus = (0,1)



class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    uid = Column(Integer, autoincrement=True, unique=True)
    name = Column(String(length=100), nullable=False)
    email = Column(String(length=100), nullable=False, unique=True)
    phone = Column(Integer, nullable=False, unique=True)
    password = Column(String(length=255), nullable=False)
    dob = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self,uid:str, name: str, email: str, phone: str, password: str, dob: datetime):
        self.uid = uid
        self.name = name
        self.email = email
        self.phone = phone
        self.password = password
        self.dob = dob

    def __repr__(self):
        res = {
            'uid': self.uid,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'password': self.password,
            'dob': str(self.dob),
            'updated': str(self.updated),
            'created': str(self.created)
        }
        return json.dumps(res)


class Client(Base):
    __tablename__ = 'client'

    id = Column(Integer, primary_key=True)
    uid = Column(Integer, autoincrement=True, unique=True)
    name = Column(String(length=100), nullable=False)
    email = Column(String(length=100), nullable=False, unique=True)
    phone = Column(Integer, nullable=False, unique=True)
    password = Column(String(length=255), nullable=False)
    poc = Column(String(length=100), nullable=False)
    poc_contact = Column(Integer, nullable=False, unique=True)
    poc_email = Column(String(length=100), nullable=False, unique=True)
    updated = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self,uid:str, name: str, email: str, phone: int, password: str, poc: str,poc_contact: int, poc_email: str):
        self.uid = uid
        self.name = name
        self.email = email
        self.phone = phone
        self.password = password
        self.poc = poc
        self.poc_contact = poc_contact
        self.poc_email = poc_email

    def __repr__(self):
        res = {
            'uid': self.uid,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'password': self.password,
            'poc': self.poc,
            'poc_contact': self.poc_contact,
            'poc_email': self.poc_email,
            'updated': str(self.updated),
            'created': str(self.created)
        }
        return json.dumps(res)


class CardType(Base):
    __tablename__ = 'cardType'
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(length=50), nullable=False, index=True)
    clientID = Column(Integer, ForeignKey('client.uid'), nullable=False)
    discount = Column(Integer, nullable=False)
    minBill = Column(Integer, nullable=False)
    maxDiscount = Column(Integer, nullable=False)
    maxSwiped = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint(level.in_(cardLevels)),
    )

    def __init__(self, level, clientID, discount, minBill, maxDiscount, maxSwiped):
        self.level = level
        self.clientID = clientID
        self.discount = discount
        self.minBill = minBill
        self.maxDiscount = maxDiscount
        self.maxSwiped = maxSwiped

    def __repr__(self):
        res = {
            'level': self.level,
            'clientID': self.clientID,
            'discount': self.discount,
            'minBill': self.minBill,
            'maxDiscount': self.maxDiscount,
            'maxSwiped': self.maxSwiped,
        }
        return json.dumps(res)


class Cards(Base):
    __tablename__ = 'cards'
    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(BigInteger, nullable=False, unique=True)
    expiry = Column(DateTime, nullable=False)
    subscription = Column(DateTime, nullable=False, default=datetime.utcnow)
    userID = Column(Integer,ForeignKey('user.uid'),nullable=False)
    cardType = Column(String(length=50),ForeignKey('cardType.level'),nullable=False)
    status = Column(Integer, nullable=False, index=True)
    __table_args__ = (
        CheckConstraint(status.in_(cardStatus)),
    )

    def __init__(self,number,expiry,userID,cardType,status):
        self.number = number
        self.expiry = expiry
        self.userID = userID
        self.cardType = cardType
        self.status = status

    def __repr__(self):
        res = {
            'number':self.number,
            'expiry':self.expiry,
            'userID':self.userID,
            'cardType':self.cardType
        }
        return json.dumps(res)


class Transactions(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, nullable=False)
    tid = Column(Integer, nullable=False)
    cardID = Column(BigInteger,ForeignKey('cards.number'),nullable=False)
    clientID = Column(Integer,ForeignKey('client.uid'),nullable=False)
    discount = Column(Integer,nullable=False)
    billAmount = Column(Integer,nullable=False)
    timeStamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(length=50),nullable=False)

    def __init__(self,uid,tid,cardID,clientID,discount,billAmount,status):
        self.uid = uid
        self.tid = tid
        self.cardID = cardID
        self.clientID = clientID
        self.discount = discount
        self.billAmount = billAmount
        self.status = status

    def __repr__(self):
        res = {
            "tid":self.tid,
            "uid":self.uid,
            "cardID":self.cardID,
            "clientID":self.clientID,
            "discount":self.discount,
            "billAmount":self.billAmount,
            "timestamp":self.timeStamp,
            "status":self.status
        }
        return json.dumps(res)


