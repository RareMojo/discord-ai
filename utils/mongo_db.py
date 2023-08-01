from pymongo import MongoClient
import os



class MongoDBHandler:
    """
    Handles data for a MongoDB database.
    """

    def __init__(self, database_name: str):
        """
        Initializes the MongoDBHandler class.
        Args:
          database_name (str): The name of the MongoDB database.
        """
        self.client = MongoClient(os.environ.get("MONGO_URI"))
        self.db = self.client[database_name]

    def handle_data(
        self, user_id, user_name, db_name, db_id, ingest_url, ingested_time
    ):
        """
        Handles data for a user.
        Args:
          user_id (str): The ID of the user.
          user_name (str): The name of the user.
          db_name (str): The name of the document.
          db_id (str): The ID of the document.
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
            "db": {
                "db_name": db_name,
                "db_id": db_id,
                "ingested_url": ingest_url,
                "ingested_time": ingested_time,
            }
        }
        user_collection.update_one({"user_id": user_id}, {"$push": {"data": data}})

    def list_db(self, user_id: str):
        """
        Lists all documents for a user.
        Args:
          user_id (str): The ID of the user.
        Returns:
          list: A list of documents for the user.
        Examples:
          >>> list_db('123')
          [{'db_name': 'doc1', 'db_id': '456', 'ingested_url': 'www.example.com', 'ingested_time': '2020-01-01'}, {'db_name': 'doc2', 'db_id': '789', 'ingested_url': 'www.example.com', 'ingested_time': '2020-01-02'}]
        """
        user_collection = self.db["users"]
        user = user_collection.find_one({"user_id": user_id})

        if user:
            db = []
            for entry in user["data"]:
                db_data = {
                    "db_name": entry["db"]["db_name"],
                    "db_id": entry["db"]["db_id"],
                    "ingested_url": entry["db"]["ingested_url"],
                    "ingested_time": entry["db"]["ingested_time"],
                }
                db.append(db_data)

            if db:
                return db
            else:
                return "You have no db"
        else:
            return "User not found"
          
    def list_all_db(self):
      """
      Lists all documents for all users.
      Returns:
        list: A list of all documents.
      Examples:
        >>> list_all_db()
        [{'db_name': 'doc1', 'db_id': '456', 'ingested_url': 'www.example.com', 'ingested_time': '2020-01-01', 'user_id': '123'}, {'db_name': 'doc2', 'db_id': '789', 'ingested_url': 'www.example.com', 'ingested_time': '2020-01-02', 'user_id': '123'}, ...]
      """
      user_collection = self.db["users"]
      all_db = []
      for user in user_collection.find():
          for entry in user["data"]:
              db_data = {
                  "db_name": entry["db"]["db_name"],
                  "db_id": entry["db"]["db_id"],
                  "ingested_url": entry["db"]["ingested_url"],
                  "ingested_time": entry["db"]["ingested_time"],
                  "user_id": user["user_id"],  # include the user_id in the returned data
              }
              all_db.append(db_data)

      if all_db:
          return all_db
      else:
          return "No DB found"

    def delete_db(self, user_id: str, db_id: str):
        """
        Deletes a document for a user.
        Args:
          user_id (str): The ID of the user.
          db_id (str): The ID of the document.
        Returns:
          bool: True if the document was deleted, False otherwise.
        Examples:
          >>> delete_db('123', '456')
          True
        """
        user_collection = self.db["users"]
        result = user_collection.update_one(
            {"user_id": user_id, "data.db.db_id": db_id},
            {"$pull": {"data": {"db.db_id": db_id}}},
        )

        if result.modified_count > 0:
            return True
        else:
            return False


    def get_db_name(self, user_id: str, db_id: str):
        """
        Gets the name of a document for a user.
        Args:
          user_id (str): The ID of the user.
          db_id (str): The ID of the document.
        Returns:
          str: The name of the document.
        Raises:
          ValueError: If the document with the given ID is not found.
        Examples:
          >>> get_db_name('123', '456')
          'doc1'
        """
        user_collection = self.db["users"]
        user = user_collection.find_one(
            {"user_id": user_id, "data.db.db_id": db_id}
        )

        if user:
            for entry in user["data"]:
                if entry["db"]["db_id"] == db_id:
                    return entry["db"]["db_name"]

            raise ValueError(f"db with ID {db_id} not found.")
        else:
            raise ValueError("No user found with the provided db ID.")

    def check_exists(self, db_id: str):
        """
        Checks if a db exists for any user.
        Args:
          db_id (str): The ID of the document.
        Returns:
          bool: True if the document exists, False otherwise.
        Examples:
          >>> check_exists('456')
          True
        """
        user_collection = self.db["users"]
        user = user_collection.find_one({"data": { "$elemMatch": { "db.db_id": db_id } } })

        return user is not None
