# Order Tracker

Flask API for orders. Will grow into an async pipeline:
Flask -> SQS -> Lambda -> DynamoDB (with DLQ and CloudWatch).

## Run locally
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py

## Run tests
pytest -v
