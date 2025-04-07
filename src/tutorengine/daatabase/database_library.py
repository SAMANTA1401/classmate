import mysql.connector
from mysql.connector import Error



class LibraryDatabase:
    def __init__(self, user_id):
        self.db_config = {
        'host': 'localhost',
        'database': 'tutorengine',
        'user': 'root',
        'password': 'mYsql@2022'
    }
        self.cnx = None
        self.cursor = None
        self.user_id = user_id

    def connect(self):
        try:
            self.cnx = mysql.connector.connect(**self.db_config)
            self.cursor = self.cnx.cursor()
            print("Connected to the database.")
            return self.cursor
        except Error as e:
            print(f"Error connecting to the database: {e}")

    def disconnect(self):
        if self.cnx:
            self.cursor.close()
            self.cnx.close()
            print("Disconnected from the database.")

    def execute_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.cnx.commit()
            print("Query executed successfully.")
        except Error as e:
            print(f"Error executing query: {e}")

    def fetch_results(self):
        return self.cursor.fetchall()

    def add_learning_content(self,subject_name, chapter_name, topic_name, content_text):
        """

        """
        
        subject_id = None
        chapter_id = None
        topic_id = None

        try:
            self.connect()

            # --- Step 1 & 2: Handle Subject ---
            query_subject = "SELECT subject_id FROM Subjects WHERE subject_name = %s AND user_id = %s"
            self.cursor.execute(query_subject, (subject_name, self.user_id))
            result = self.cursor.fetchone()

            if result:
                subject_id = result[0]
                print(f"Subject '{subject_name}' found for user {self.user_id}. ID: {subject_id}")
            else:
                insert_subject = "INSERT INTO Subjects (user_id, subject_name) VALUES (%s, %s)"
                self.cursor.execute(insert_subject, (self.user_id, subject_name))
                subject_id = self.cursor.lastrowid  # Get the ID of the newly inserted row
                print(f"Inserted Subject '{subject_name}' for user {self.user_id}. New ID: {subject_id}")
                if not subject_id: # Handle cases where lastrowid might not be reliable (depends on config/engine)
                    self.cursor.execute(query_subject, (subject_name, self.user_id))
                    result = self.cursor.fetchone()
                    if result:
                        subject_id = result[0]
                    else:
                        raise Exception("Failed to retrieve subject_id after insert.")


            # --- Step 3 & 4: Handle Chapter ---
            query_chapter = "SELECT chapter_id FROM Chapters WHERE chapter_name = %s AND subject_id = %s"
            self.cursor.execute(query_chapter, (chapter_name, subject_id))
            result = self.cursor.fetchone()

            if result:
                chapter_id = result[0]
                print(f"Chapter '{chapter_name}' found for subject ID {subject_id}. ID: {chapter_id}")
            else:
                insert_chapter = "INSERT INTO Chapters (subject_id, chapter_name) VALUES (%s, %s)"
                self.cursor.execute(insert_chapter, (subject_id, chapter_name))
                chapter_id = self.cursor.lastrowid
                print(f"Inserted Chapter '{chapter_name}' for subject ID {subject_id}. New ID: {chapter_id}")
                if not chapter_id:
                    self.cursor.execute(query_chapter, (chapter_name, subject_id))
                    result = self.cursor.fetchone()
                    if result:
                        chapter_id = result[0]
                    else:
                        raise Exception("Failed to retrieve chapter_id after insert.")

            # --- Step 5: Handle Topic ---
            query_topic = "SELECT topic_id FROM Topics WHERE topic_name = %s AND chapter_id = %s"
            self.cursor.execute(query_topic, (topic_name, chapter_id))
            result = self.cursor.fetchone()

            if result:
                topic_id = result[0]
                print(f"Topic '{topic_name}' found for chapter ID {chapter_id}. ID: {topic_id}")
            else:
                insert_topic = "INSERT INTO Topics (chapter_id, topic_name) VALUES (%s, %s)"
                self.cursor.execute(insert_topic, (chapter_id, topic_name))
                topic_id = self.cursor.lastrowid
                print(f"Inserted Topic '{topic_name}' for chapter ID {chapter_id}. New ID: {topic_id}")
                if not topic_id:
                    self.cursor.execute(query_topic, (topic_name, chapter_id))
                    result = self.cursor.fetchone()
                    if result:
                        topic_id = result[0]
                    else:
                        raise Exception("Failed to retrieve topic_id after insert.")


            # --- Step 6: Handle Content ---
           
            insert_content = "INSERT INTO Contents (topic_id, content_text) VALUES (%s, %s)"
            self.cursor.execute(insert_content, (topic_id, content_text))
            content_id = self.cursor.lastrowid
            print(f"Inserted Content for topic ID {topic_id}. New Content ID: {content_id}")

            # Commit the transaction if all steps were successful
            self.cnx.commit()
            print("Transaction committed successfully.")
            return True, f"Content added/found successfully. Topic ID: {topic_id}"

        except Error as err:
            print(f"Database Error: {err}")
            if self.cnx and self.cnx.is_connected():
                print("Rolling back transaction.")
                self.cnx.rollback() # Roll back changes on error
            return False, f"Database Error: {err}"
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            if self.cnx and self.cnx.is_connected():
                print("Rolling back transaction due to unexpected error.")
                self.cnx.rollback()
            return False, f"An unexpected error occurred: {e}"

        finally:
            # Close self.self.cursor and connection
            if self.cursor:
                self.cursor.close()
                print("self.self.cursor closed.")
            if self.cnx and self.cnx.is_connected():
                self.cnx.close()
                print("MySQL connection closed.")

# --- How to use the function ---







if __name__ == "__main__":
    # Example usage
    db_config = {
        'host': 'localhost',
        'database': 'tutorengine',
        'user': 'root',
        'password': 'mYsql@2022'
    }

    library = LibraryDatabase(db_config, 1)

    # Example call
    success, message =library.add_learning_content(
        "Physics",
        "Mechanics",
        "Newton's Laws",
        "Newton's laws describe the relationship between motion and forces."
    )
    print(f"Operation Result: Success={success}, Message={message}")
