import os
import json
import mlflow
import datetime
import argparse
import importlib
import pandas as pd
from pathlib import Path
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine, Column, String, DateTime, Numeric, Integer

POSTGRES_HOST = "192.168.1.2"
POSTGRES_PORT = 32102
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "super_dooper_secret"
POSTGRES_DB = "postgres"

parser = argparse.ArgumentParser(description="Saving data!")

parser.add_argument('-n', '--name', type=str, help='Name of the model.')
parser.add_argument('-a', '--architecture', type=str, help='The architecture of the model.')

args = parser.parse_args()
model_name = args.name
architecture = args.architecture

MLFLOW_TRACKING_URI = "http://62.72.21.79:5000"

os.environ['MLFLOW_TRACKING_USERNAME'] = "admin"
os.environ['MLFLOW_TRACKING_PASSWORD'] = "password"
os.environ['AWS_ACCESS_KEY_ID'] = "super"
os.environ['AWS_SECRET_ACCESS_KEY'] = "doopersecret"
os.environ['MLFLOW_S3_ENDPOINT_URL'] = "https://minio1.sedimark.work"
os.environ['MLFLOW_TRACKING_INSECURE_TLS'] = "true"
os.environ['MLFLOW_HTTP_REQUEST_TIMEOUT'] = "1000"

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

model, tokenizer, metrics, params = None, None, None, None

try:
    module = importlib.import_module("transformers")
    function = getattr(module, str(architecture))
    checkpoint_list = []
    for path in Path("./finetuned_model").glob("*"):
        if "checkpoint" in str(path):
            checkpoint_list.append(str(path).split("/")[-1].split("-")[-1])

    last_checkpoint = max(checkpoint_list)
    model = function.from_pretrained(f"./finetuned_model/checkpoint-{last_checkpoint}")
    if "Image" in str(architecture):
        tokenizer_function = getattr(module, "AutoImageProcessor")
        tokenizer = function.from_pretrained(f"./finetuned_model/checkpoint-{last_checkpoint}")
    else:
        tokenizer_function = getattr(module, "AutoTokenizer")
        tokenizer = function.from_pretrained(f"./finetuned_model/checkpoint-{last_checkpoint}")
except (Exception, FileNotFoundError) as exception:
    print(exception)

try:
    with open("metrics.json", "r") as json_file:
        metrics = json.load(json_file)
except (Exception, FileNotFoundError) as exception:
    print(exception)

try:
    with open("params.json", "r") as json_file:
        params = json.load(json_file)
except (Exception, FileNotFoundError) as exception:
    print(exception)

if metrics is not None and params is not None and model is not None and tokenizer is not None:
    components = {
        "model": model,
        "tokenizer": tokenizer,
    }
    with mlflow.start_run(experiment_id=mlflow.get_experiment_by_name("default").experiment_id) as run:
        mlflow.transformers.log_model(
            transformers_model=components,
            artifact_path="model",
        )
        mlflow.log_metrics(metrics)
        mlflow.log_params(params)
        mlflow.log_artifact('temp_file.csv')

    run_id = run.info.run_id

    # Define the model
    Base = declarative_base()


    class MyTable(Base):
        __tablename__ = 'models'
        model_id = Column(String, primary_key=True)
        created_at = Column(DateTime)
        user_id = Column(String)
        dataset_user = Column(String)
        description = Column(String)
        score = Column(Numeric)
        model_name = Column(String)
        score_count = Column(Integer)
        notebook_type = Column(String)


    df = pd.read_csv("./temp_file.csv")

    csv_data = {
        "column_dtypes": {},
        "column_ranges": {},
        "column_categories": {},
        "column_unique_values": {}
    }

    for column in df.columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            csv_data["column_dtypes"][column] = "numeric"
            csv_data["column_ranges"][column] = (min(df[column]), max(df[column]))
            csv_data["column_categories"][column] = None
            csv_data["column_unique_values"][column] = None
        else:
            if len(df[column].unique()) == len(df):
                csv_data["column_dtypes"][column] = "unique_identifier"
                csv_data["column_ranges"][column] = None
                csv_data["column_categories"][column] = None
                csv_data["column_unique_values"][column] = len(df[column].unique())
            else:
                csv_data["column_dtypes"][column] = "categorical"
                csv_data["column_ranges"][column] = None
                csv_data["column_categories"][column] = df[column].unique()
                csv_data["column_unique_values"][column] = None

    engine = create_engine(f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/'
                           f'{POSTGRES_DB}')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    new_row = MyTable(model_id=run_id, created_at=datetime.datetime.now(), user_id=os.getenv("USER_ID"),
                      description=json.dumps(csv_data), score=0.0, model_name=model_name, score_count=0, dataset_user=os.getenv("DATASET_USER"), notebook_type="transformers")

    session.add(new_row)

    session.commit()
    session.close()
else:
    print("Something happened!")
