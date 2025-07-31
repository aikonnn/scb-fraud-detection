from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import joblib
import pandas as pd
import xgboost as xgb

app = FastAPI()

model = xgb.XGBClassifier()
model.load_model("model/fraud_detection.model")

# SQLite setup
engine = create_engine("sqlite:///db/frauds.db")
Session = sessionmaker(bind=engine)
Base = declarative_base()

class FraudRecord(Base):
    __tablename__ = "frauds"
    id = Column(Integer, primary_key=True)
    src_acc = Column(String)
    dst_acc = Column(String)
    amount = Column(Float)
    is_fraud = Column(Boolean)

Base.metadata.create_all(engine)

class Transaction(BaseModel):
    time_ind: int
    transac_type: str
    amount: float
    src_acc: str
    src_bal: float
    src_new_bal: float
    dst_acc: str
    dst_bal: float = 0
    dst_new_bal: float = 0
    is_flagged_fraud: int

transac_type_encode = {
   'CASH_OUT': 0,
   'TRANSFER': 1
}

@app.post("/predict")
def predict(t: Transaction):
    if t.transac_type not in ["CASH_OUT", "TRANSFER"]:
      return {"is_fraud": False}

    #process input
    X = pd.DataFrame([t.dict()])
    X['transac_type']=X['transac_type'].map(transac_type_encode)
    X.drop(columns=["src_acc", "dst_acc", "is_flagged_fraud"], axis=1, inplace=True)
    X.loc[:, 'hour_of_day'] = X['time_ind']%24

    prediction = model.predict(X)[0]
    
    if prediction == 1:
        session = Session()
        record = FraudRecord(
            src_acc=t.src_acc,
            dst_acc=t.dst_acc,
            amount=t.amount,
            is_fraud=True
        )
        session.add(record)
        session.commit()
        session.close()

    return {"is_fraud": bool(prediction)}

@app.get("/frauds")
def get_frauds():
    session = Session()
    results = session.query(FraudRecord).all()
    return [{"src_acc": r.src_acc, "dst_acc": r.dst_acc, "amount": r.amount} for r in results]
