from zenml import pipeline

from steps.etl.extract_data import process_chat_export




@pipeline(enable_cache=False)
def digital_data_etl(data: str) -> str:
    process_chat_export(data)

    




from configs.config import DATASET
path = DATASET
digital_data_etl(path )