# SCB Fraud Detection System
## Project Structure
```
.
├── app.py                   # FastAPI model server 
│                            (Part 3)
├── model/
│   └── fraud_detection.model  # XGBoost saved model
├── db/
│   └── frauds.db             # SQLite DB for demo
├── data/
│   └── fraud_mock.csv        # dataset
├── eda/
│   └── SCB_EDA.ipynb      # EDA on dataset (Part 1)
├── model_dev/
│   └── SCB_Model.ipynb   # Script to train and 
│                            evaluate model (Part 2)
├── requirements.txt
├── README.md
└── architecture.png      # System design diagram 
                            ( Part 4)
```
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
Run the entirety of SCB_Model.ipynb.
### Start API locally
```bash
uvicorn app:app --reload
```