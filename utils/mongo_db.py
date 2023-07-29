from pymongo import MongoClient
import os


class MongoDBHandler:
    """
    Handles data for a MongoDB database.
    """

    def __init__(self, database_name):
        """
        Initializes the MongoDBHandler class.
        Args:
          database_name (str): The name of the MongoDB database.
        """
        self.client = MongoClient(os.environ.get("MONGO_URI"))
        self.db = self.client[database_name]

    def handle_data(
        self, user_id, user_name, docs_name, docs_id, ingest_url, ingested_time
    ):
        """
        Handles data for a user.
        Args:
          user_id (str): The ID of the user.
          user_name (str): The name of the user.
          docs_name (str): The name of the document.
          docs_id (str): The ID of the document.
          ingest_url (str): The URL of the document.
          ingested_time (str): The time the document was ingested.
        Side Effects:
          Inserts or updates a user in the MongoDB database.
        """
        user_collection = self.db["users"]
        user = user_collection.find_one({"user_id": user_id})

        if not user:
            user_collection.insert_one(
                {"user_id": user_id, "user_name": user_name, "data": []}
            )

        data = {
            "docs": {
                "docs_name": docs_name,
                "docs_id": docs_id,
                "ingested_url": ingest_url,
                "ingested_time": ingested_time,
            }
        }
        user_collection.update_one({"user_id": user_id}, {"$push": {"data": data}})

    def list_docs(self, user_id):
        """
        Lists all documents for a user.
        Args:
          user_id (str): The ID of the user.
        Returns:
          list: A list of documents for the user.
        Examples:
          >>> list_docs('123')
          [{'docs_name': 'doc1', 'docs_id': '456', 'ingested_url': 'www.example.com', 'ingested_time': '2020-01-01'}, {'docs_name': 'doc2', 'docs_id': '789', 'ingested_url': 'www.example.com', 'ingested_time': '2020-01-02'}]
        """
        user_collection = self.db["users"]
        user = user_collection.find_one({"user_id": user_id})

        if user:
            docs = []
            for entry in user["data"]:
                docs_data = {
                    "docs_name": entry["docs"]["docs_name"],
                    "docs_id": entry["docs"]["docs_id"],
                    "ingested_url": entry["docs"]["ingested_url"],
                    "ingested_time": entry["docs"]["ingested_time"],
                }
                docs.append(docs_data)

            if docs:
                return docs
            else:
                return "You have no docs"
        else:
            return "User not found"

    def delete_docs(self, user_id, docs_id):
        """
        Deletes a document for a user.
        Args:
          user_id (str): The ID of the user.
          docs_id (str): The ID of the document.
        Returns:
          bool: True if the document was deleted, False otherwise.
        Raises:
          ValueError: If the document with the given ID is not found.
        Examples:
          >>> delete_docs('123', '456')
          True
        """
        user_collection = self.db["users"]
        result = user_collection.update_one(
            {"user_id": user_id, "data.docs.docs_id": docs_id},
            {"$pull": {"data": {"docs.docs_id": docs_id}}},
        )

        if result.modified_count > 0:
            return True
        else:
            raise ValueError(f"Docs with ID {docs_id} not found.")

    def get_docs_name(self, user_id, docs_id):
        """
        Gets the name of a document for a user.
        Args:
          user_id (str): The ID of the user.
          docs_id (str): The ID of the document.
        Returns:
          str: The name of the document.
        Raises:
          ValueError: If the document with the given ID is not found.
        Examples:
          >>> get_docs_name('123', '456')
          'doc1'
        """
        user_collection = self.db["users"]
        user = user_collection.find_one(
            {"user_id": user_id, "data.docs.docs_id": docs_id}
        )

        if user:
            for entry in user["data"]:
                if entry["docs"]["docs_id"] == docs_id:
                    return entry["docs"]["docs_name"]

            raise ValueError(f"Docs with ID {docs_id} not found.")
        else:
            raise ValueError("No user found with the provided docs ID.")

    def check_ownership(self, user_id, docs_id):
        """
        Checks if a user owns a document.
        Args:
          user_id (str): The ID of the user.
          docs_id (str): The ID of the document.
        Returns:
          bool: True if the user owns the document, False otherwise.
        Examples:
          >>> check_ownership('123', '456')
          True
        """
        user_collection = self.db["users"]
        user = user_collection.find_one(
            {"user_id": user_id, "data.docs.docs_id": docs_id}
        )

        if user:
            for entry in user["data"]:
                if entry["docs"]["docs_id"] == docs_id:
                    return True
            return False
        else:
            return False
