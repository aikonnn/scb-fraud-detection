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
    time_ind = Column(Integer)
    transac_type = Column(String)
    amount = Column(Float)
    src_acc = Column(String)
    src_bal = Column(Float)
    src_new_bal = Column(Float)
    dst_acc = Column(String)
    dst_bal = Column(Float)
    dst_new_bal = Column(Float)
    is_flagged_fraud = Column(Integer)
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
            time_ind=t.time_ind,
            transac_type=t.transac_type,
            amount=t.amount,
            src_acc=t.src_acc,
            src_bal=t.src_bal,
            src_new_bal=t.src_new_bal,
            dst_acc=t.dst_acc,
            dst_bal=t.dst_bal,
            dst_new_bal=t.dst_new_bal,
            is_flagged_fraud=t.is_flagged_fraud,
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
    return [
        {
            "id": r.id,
            "time_ind": r.time_ind,
            "transac_type": r.transac_type,
            "amount": r.amount,
            "src_acc": r.src_acc,
            "src_bal": r.src_bal,
            "src_new_bal": r.src_new_bal,
            "dst_acc": r.dst_acc,
            "dst_bal": r.dst_bal,
            "dst_new_bal": r.dst_new_bal,
            "is_flagged_fraud": r.is_flagged_fraud,
            "is_fraud": r.is_fraud
        }
        for r in results
    ]
