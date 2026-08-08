from src.infrastructure.mongo import MongoDatabaseConnector


def load(model, content):
    if not content:
        return

    client = MongoDatabaseConnector()
    database = client["rag_database"]

    collection_name = model.Settings.name
    collection = database[collection_name]

    documents = []

    for data in content:
        instance = model(
            content=data,
            name=data["title"],
        )

        documents.append(instance.model_dump())

    if documents:
        collection.insert_many(documents)

    print(
        f"Loaded {len(documents)} documents "
        f"into '{collection_name}'"
    )