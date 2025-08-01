# SCB Fraud Detection System
## Project Structure
```
.
├── app.py                   # FastAPI model server (Part 3)
├── model/
│   └── fraud_detection.model  # Trained XGBoost model
├── db/
│   └── frauds.db             # SQLite DB used by the API
├── data/
│   └── fraud_mock.csv        # Dataset (download manually)
├── eda/
│   └── SCB_EDA.ipynb         # Exploratory data analysis (Part 1)
├── model_dev/
│   └── SCB_Model.ipynb       # Model training notebook (Part 2)
├── requirements.txt
├── README.md
└── architecture.drawio       # System architecture diagram (Part 4)

```
Download the dataset from the link below and place it in the data/ directory as fraud_mock.csv:

https://scbpocseasta001stdsbx.z23.web.core.windows.net/
## Setup Instructions
### Install Dependencies
pip: 
```bash
pip install -r requirements.txt
```

conda:
```bash
conda install --file requirements.txt
```
### Train and save model
See [Part 2](#p2).
### Start API locally
See [Part 3](#p3).

<a id="p1"></a>
## Run EDA (Part 1)
Open and run all cells in eda/SCB_EDA.ipynb.

<a id="p2"></a>
## Train Model (Part 2)
Run all cells in model_dev/SCB_Model.ipynb.

<a id="p3"></a>
## API Endpoints (Part 3)
### Start API
```bash
uvicorn app:app --reload
```
The API will be run on http://localhost:8000.
### POST /predict
Make a fraud prediction on a new transaction.

Example: 
```json
{
  "time_ind": 1,
  "transac_type": "TRANSFER",
  "amount": 181.0,
  "src_acc": "dummyacc1",
  "src_bal": 181.0,
  "src_new_bal": 0.0,
  "dst_acc": "dummyacc2",
  "dst_bal": 0.0,
  "dst_new_bal": 0.0,
  "is_flagged_fraud": 0
}
```

Returns: 
```json
{"is_fraud": true}
```
If predicted as fraud, the transaction is saved in the frauds database.

### GET /frauds
Returns all predicted fraud transactions (full record from DB).

``` json
[
  {
    "id": 1,
    "time_ind": 1,
    "transac_type": "TRANSFER",
    "amount": 181.0,
    "src_acc": "dummyacc1",
    "src_bal": 181.0,
    "src_new_bal": 0.0,
    "dst_acc": "adummyacc2",
    "dst_bal": 0.0,
    "dst_new_bal": 0.0,
    "is_flagged_fraud": 0,
    "is_fraud": true
  },
  ...
]
```
<a id="p4"></a>
## System Architecture (Part 4)
See architecture.drawio for the full architecture diagram.
### Design Considerations
- Scalability: Kafka + horizontally scalable model servers
- Security: Access control managed by API gateway and database backup on cloud platform
- Fault Tolerance: Kafka replay, Multiple servers in parallel

### Business Considerations
- Precision is balanced with recall to minimize false positives while ensuring real frauds are not missed.
- The system is designed to flag suspicious transactions for auditor review, not auto-blocking.