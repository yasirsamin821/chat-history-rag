from zenml import pipeline

from etl.crawl_links import crawl_links
from database.get_or_create_user import get_or_create_user

@pipeline
def digital_data_etl(user_full_name: str, links: list[str]) -> str:
    user = get_or_create_user(user_full_name)
    last_step = crawl_links(user=user, links=links)

    return last_step.invocation_id
