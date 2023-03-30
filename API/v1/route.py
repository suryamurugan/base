from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, extract
from main import generateCardNumber
from config import Base,user,password,host,database, SECRET_KEY
from models import User, Client, CardType, Cards, Transactions
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
import bcrypt, jwt, json

app = FastAPI()

engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}',echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(bind=engine)


@app.get("/api/v1/user")
def getAllUsers():
    results = session.query(User).all()
    return {"response": results}

@app.post("/api/v1/user/signup")
def userSignup(name:str,email:str,phone:int,password:str,dob:datetime):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    userid = "1" + "1" + str(len(session.query(User).all()) + 1)
    # <Version><userID : 1><Count>
    user = User(userid, name, email, phone, hashed_password.decode('utf-8'), dob)
    session.add(user)
    try:
        session.commit()
        return {"response": "success"}
    except Exception as e:
        return {"response": str(e)}

@app.post("/api/v1/user/login")
def userLogin(email: str, password: str):
    user = session.query(User).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = jwt.encode({'user_id': user.id}, SECRET_KEY, algorithm='HS256')
    return {'access_token': token}


@app.post("/api/v1/client/signup")
def clientSignup(name: str, email: str, phone: int, password: str, poc: str, poc_contact: int, poc_email: str):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    uid = "1" + "2" + str(len(session.query(Client).all()) + 1)
    client = Client(uid=uid, name=name, email=email, phone=phone, password=hashed_password, poc=poc, poc_contact=poc_contact,
                    poc_email=poc_email)
    # <Version><userID : 1><Count>
    try:
        session.add(client)
        session.commit()
    except Exception as e:
        session.rollback()
        return {"message": "Failed to add client to the database", "error": str(e)}
    return {"message": "Client signup successful"}

@app.get("/api/v1/client")
def getAllClients():
    results = session.query(Client).all()
    return {"response": results}

@app.get("/api/v1/card/levels")
def getCardLevels():
    results = session.query(CardType).all()
    return {"response": results}


@app.post("/api/v1/card/level/add")
def addCardLevel(level, clientID, discount, minBill, maxDiscount, maxSwiped):
    cardLevel = CardType(level, clientID, discount, minBill, maxDiscount, maxSwiped)
    session.add(cardLevel)
    try:
        session.commit()
        return {"response": "success"}
    except Exception as e:
        session.rollback()
        return {"response": str(e)}


@app.post("/api/v1/card/add")
def addCard(userID,cardType):
    number = generateCardNumber()
    expiry = datetime.today() + timedelta(days=365)
    status = 1
    card = Cards(number,expiry,userID,cardType,status)
    session.add(card)
    try:
        session.commit()
        return {"response": "success"}
    except Exception as e:
        session.rollback()
        return {"response": str(e)}


@app.post("/api/v1/client/login")
def clientLogin(email: str, password: str):
    client = session.query(Client).filter_by(email=email).first()

    if not client:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not bcrypt.checkpw(password.encode('utf-8'), client.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = jwt.encode({'user_id': client.id}, SECRET_KEY, algorithm='HS256')
    return {'access_token': token}

@app.post("/api/v1/authorize")
def authorizeTransaction(cardNumber, clientID, billAmount):
    uid = session.query(User.uid).join(Cards).filter(Cards.number == cardNumber).scalar()
    transactionID = str(datetime.now().strftime('%Y%m')) + str(session.query(func.count(Transactions.id)).scalar() + 1) + str(uid)
    temp = session.query(Cards, CardType).join(CardType, Cards.cardType == CardType.level).filter(
        Cards.number == cardNumber).filter(CardType.clientID==clientID).all()
    if not temp:
        return {"response": "Invalid Card"}
    maxSwipesAllowed = temp[0][1].maxSwiped
    minBilling = temp[0][1].minBill
    maxDiscount = temp[0][1].maxDiscount
    discountAvail = temp[0][1].discount
    results = session.query(Transactions).filter(Transactions.cardID==cardNumber).all()
    allMonths = [item.timeStamp for item in results]
    current_month_timestamps = [timestamp for timestamp in allMonths if timestamp.month == datetime.now().month and timestamp.year == datetime.now().year]
    currentSwipes = len(current_month_timestamps)

    if(currentSwipes>maxSwipesAllowed):
        return {"response":f'Only {maxSwipesAllowed} swipe/s allowed'}

    if(int(minBilling)<=int(billAmount)):
        discountAmount = min(int(discountAvail)*int(billAmount)/100,int(maxDiscount))
        transactions = Transactions(uid,transactionID,cardNumber,clientID,discountAmount,billAmount,"success")
        session.add(transactions)
        try:
            session.commit()
            return {"response": "Authorization success"}
        except Exception as e:
            session.rollback()
            return {"response": str(e)}
    else:
        return {"response":f'minimum billing should be {minBilling}'}


    return {"response":[transactionID,maxSwipesAllowed,currentSwipes,minBilling,maxDiscount,discountAvail]}

@app.get("/api/v1/transaction")
def transaction():
    results = session.query(Transactions, Client.name, User.name)\
              .join(Cards, Transactions.cardID == Cards.number)\
              .join(Client, Transactions.clientID == Client.uid)\
              .join(User, Cards.userID == User.uid).all()
    response = []
    for transaction, client_name, username in results:
        res = {
            "tid": transaction.tid,
            "uid": transaction.uid,
            "cardID": transaction.cardID,
            "clientID": transaction.clientID,
            "clientName": client_name,
            "discount": transaction.discount,
            "billAmount": transaction.billAmount,
            "timestamp": transaction.timeStamp,
            "status": transaction.status,
            "username": username
        }
        response.append(res)
    return {"response": response}




@app.get('/api/v1/cards')
def getAllCards():
    results = session.query(Cards,CardType).join(CardType,Cards.cardType == CardType.level).all()
    cards = []
    for result in results:
        card = {
            'user':(session.query(User).filter(User.uid==result[0].userID).all()[0]).name,
            'number': result[0].number,
            'subscription': result[0].subscription,
            'cardType':result[0].cardType,
            'expiry':result[0].expiry,
            'userID':result[0].userID,
            'status':result[0].status,
            # 'minBill':result[1].minBill,
            # 'clientID':result[1].clientID,
            # 'maxSwipes':result[1].maxSwiped,
            # 'discount':result[1].discount,
            # 'maxDiscount':result[1].maxDiscount
        }
        cards.append(card)
    return {"response":card}


# @app.post("/api/v1/authorize")
# def authorizeTransaction(cardNumber: str, clientID: int, billAmount: float):
#     uid = session.query(User.uid).join(Cards).filter(Cards.number == cardNumber).scalar()
#     transactionID = str(datetime.now().date()) + str(session.query(func.count(Transactions.id)).scalar() + 1) + str(uid)
#     temp = session.query(Cards, CardType).join(CardType, Cards.cardType == CardType.level).filter(
#         Cards.number == cardNumber).all()
#     maxSwipesAllowed = temp[0][1].maxSwiped
#     currentSwipes = session.query(func.count(Transactions.id)).filter(
#         Transactions.cardID == cardNumber,
#         extract('month', Transactions.timeStamp) == datetime.utcnow().month
#     ).scalar()
#     return {"response":[transactionID, maxSwipesAllowed, currentSwipes]}

