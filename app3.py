import json
import time # Just for demonstration or potential delays
from flask import Flask, render_template, request, Response, jsonify 
from src.logger import logging
from src.exception import CustomException 
from src.tutorengine.pipeline.master_pipeline import MasterPipeline 
# Assuming these utils are not directly used in this route anymore
from src.tutorengine.utils import FieldSelectionParser 
from src.tutorengine.daatabase.database_library import LibraryDatabase 
from werkzeug.utils import secure_filename
import uuid 
from flask import session
import mysql.connector
from flask_cors import CORS 
import sys
import  os 
from src.tutorengine.component.summary_bot import SummaryBot

app = Flask(__name__)
CORS(app)

chat_histories = {}

library_data = {
    "user_id":1,
    "subject":None,
    "chapter":None,
    "topic":None,
    "content":None
}



# Generate a unique ID for this piece of content
content_session_id = f"content_{uuid.uuid4().hex}"
# session[content_session_id] = "asdfgsdag"

DEFAULT_SESSION_ID = "default_user"
# ----------------------------------------------------

@app.route("/")
def index():
    # Ensure necessary history exists for the default session
    if DEFAULT_SESSION_ID not in chat_histories:
         chat_histories[DEFAULT_SESSION_ID] = [
             "UserMessage: my name is Shubhankar Samnata, age is 20, study in class 10", 
             "SystemMessage: hi! I am your classmate"
         ]
    return render_template("chatbot.html")

# Modified to handle GET request for EventSource and stream response
@app.route("/get", methods=["GET"]) 
def chat_stream():

    
    # Get prompt from URL query parameter 'msg'
    prompt = request.args.get("msg", "") 
    if not prompt:
        # Handle empty prompt if necessary, maybe return an error event?
        def empty_gen():
            err_obj = {"error": "Empty prompt received"}
            yield f"event: error\ndata: {json.dumps(err_obj)}\n\n"
        return Response(empty_gen(), mimetype='text/event-stream')

    # --- Get session-specific chat history ---
    # You would typically get session_id from request headers, cookies, or URL
    session_id = request.args.get("session_id", DEFAULT_SESSION_ID) 
    if session_id not in chat_histories:
        # Initialize history for new session if needed
         chat_histories[session_id] = [
             "UserMessage: my name is Shubhankar Samnata, age is 20, study in class 10", 
             "SystemMessage: hi! I am your classmate"
         ]
    current_chat_history = chat_histories[session_id]
    # -----------------------------------------

    inputs = {"messages": [prompt]} 
    
    # --- Generator function for streaming ---
    def generate_response():
        try:
            # Assuming MasterPipeline is correctly initialized
            workflow = MasterPipeline(current_chat_history).workflow()
            
            # print(f"Starting workflow stream for prompt: {prompt}") # Debug
            
            # Iterate through the stream from the workflow
            for output in workflow.stream(inputs):
                # print(f"Received output chunk: {output}") # Debug raw output

                # Process the output chunk - **ADJUST THIS LOGIC** based on actual output structure
                # This part is crucial and depends heavily on what workflow.stream yields.
                # The previous code assumed a specific dict structure. Let's make it slightly more robust.
                
                processed_chunk = None
                for key, value in output.items():
                    # --- Try to extract Answer and Content ---
                    try:
                        # Assuming the relevant data might be nested like before
                        if isinstance(value, dict) and 'messages' in value and isinstance(value['messages'], list) and len(value['messages']) > 0:
                            message_data = value['messages'][0]
                            # Check if message_data is an object with attributes or a dict
                            if hasattr(message_data, 'Answer') and hasattr(message_data, 'Content'):
                                answer_value = message_data.Answer
                                content_value = message_data.Content
                                user_query = getattr(message_data, 'Question_or_query', prompt) # Fallback query
                                # user_query = message_data.Question_or_query
                            elif isinstance(message_data, dict) and 'Answer' in message_data and 'Content' in message_data:
                                answer_value = message_data.get('Answer')
                                content_value = message_data.get('Content')
                                user_query = message_data.get('Question_or_query', prompt) # Fallback query
                            else:
                                print("#  continue # Skip if expected structure not found in this ")
                                continue
                            
                            # print("message_data",message_data)

                            if hasattr(message_data, 'Subject'): # and hasattr(message_data, 'Chapter'):
                                library_data["subject"] = message_data.Subject
                                library_data["chapter"] = message_data.Chapter
                                library_data["topic"] = message_data.Topic
                            elif isinstance(message_data, dict) and 'Subject' in message_data and 'Chapter' in message_data:
                                library_data["subject"] = message_data.get('Subject')
                                library_data["chapter"] = message_data.get('Chapter')
                                library_data["topic"] = message_data.get('Topic')
                            else:
                                logging.info("Subject or Chapter not found in message_data.") # Skip if expected structure not found in this value
                            
                            if hasattr(message_data, 'Content'):
                                library_data["content"] = message_data.Content
                            elif isinstance(message_data, dict) and 'Content' in message_data:
                                library_data["content"] = message_data.get('Content')
                            else:
                                 logging.info("Content not found in message_data.") # Skip if expected structure not found in this value

                            print("lilbrary",library_data)

                            # --- Update Chat History (per chunk) ---
                            # Be cautious with frequent updates if history gets very large
                            current_chat_history.extend([
                                f"UserMessage: {user_query}", 
                                f"SystemMessage: {answer_value}"
                            ])
                            chat_histories[session_id] = current_chat_history # Update stored history
                            # print("Updated chat_history:", current_chat_history) # Debug history

                            # --- Prepare the JSON chunk for the client ---
                            if content_value: # Check if content_value is truthy (not None, not empty)
                                response_chunk_dict = {"answer": answer_value, "content": content_value}
                            else:
                                response_chunk_dict = {"answer": answer_value, "content": None}

                            # --- Yield the processed chunk ---
                            print(f"Yielding processed chunk: {response_chunk_dict}") # Debug               
                            processed_chunk = response_chunk_dict
                            break # Found and processed the relevant part, exit inner loop

                    except Exception as e:
                        logging.error(f"Error processing stream value for key '{key}': {e}\nValue: {value}")
                        # Optionally yield an error event to the client
                        # yield f"event: processing_error\ndata: {json.dumps({'error': f'Problem processing part: {key}'})}\n\n"
                        continue # Continue to next key-value pair

                # --- Yield the processed chunk if found ---
                if processed_chunk:
                    json_output = json.dumps(processed_chunk)
                    sse_message = f"data: {json_output}\n\n"
                    print(f"Yielding SSE: {sse_message}") # Debug
                    yield sse_message
                    # time.sleep(0.1) # Optional small delay for demonstration

            # --- Signal stream end (Optional but recommended) ---
            yield f"event: end-stream\ndata: {json.dumps({'message': 'Stream finished'})}\n\n"
            print("Stream finished.")


            # library["subject"] = message_data.Subject
            
        except Exception as e:
            logging.error(f"Error during streaming workflow: {e}")
            # Yield a final error event to the client
            err_obj = {"error": "An internal error occurred during streaming."}
            yield f"event: error\ndata: {json.dumps(err_obj)}\n\n"
            # Ensure session history is saved even on error if needed
            chat_histories[session_id] = current_chat_history
        finally:
            pass

    # Return the Response object with the generator and correct mimetype
    return Response(generate_response(), mimetype='text/event-stream')
# ---------------------------------------------------------------

# Remove the old '/get' POST route if it's no longer needed
# Remove the commented out '/playboard' route unless you implement it

# Temporary file storage
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/upload", methods=['POST'])
def upload_document():
    try:
        logging.info("Received upload request")
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        else:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            logging.info("document ready to process")

            SummaryBot(filename).vector_store()

            logging.info("Document uploaded and processed successfully")
            
            return jsonify({"message": "Document uploaded successfully"})

    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        return {"error": str(e)}, 500




@app.route('/add_to_library', methods=['POST']) 
def add_to_library_route():
    # Initialize the LibraryDatabase with the configuration
    # db_config = DBConfig.db_config
    library_database = LibraryDatabase(1)
    # Add the content to the library
    success, message = library_database.add_learning_content(
        library_data["subject"],
        library_data["chapter"],
        library_data["topic"],
        library_data["content"]
    )
    # Render the playboard template
    # 4. Send Response
    
    return jsonify({"success": success, "message": message}) # Send back the message from the method

@app.route('/library')
def library():
    return render_template('library.html')


@app.route('/go-to-library')
def go_to_library():
    # Logic to determine the library URL (e.g., based on user, etc.)
    library_url = '/library'
    return jsonify({'redirect_url': library_url})

db = mysql.connector.connect(
        host='localhost',
        database='tutorengine',
        user='root',
        password='mYsql@2022'
        )


@app.route('/subjects/<int:user_id>')
def get_subjects(user_id):
    try:
        cursor = db.cursor(dictionary=True)
        # cursor = LibraryDatabase(1).connect()
        cursor.execute("SELECT * FROM subjects WHERE user_id = %s", (user_id,))
        subjects = cursor.fetchall()
        cursor.close()
        print(f"Subjects fetched for user {user_id}: {subjects}")
        return jsonify(subjects)
    except Exception as e:
        return logging.info(CustomException(e,sys))

@app.route('/chapters/<int:subject_id>')
def get_chapters(subject_id):
    cursor = db.cursor(dictionary=True)
    # cursor = LibraryDatabase.connect()
    cursor.execute("SELECT * FROM chapters WHERE subject_id = %s", (subject_id,))
    chapters = cursor.fetchall()
    cursor.close()
    return jsonify(chapters)

@app.route('/topics/<int:chapter_id>')
def get_topics(chapter_id):
    cursor = db.cursor(dictionary=True)
    # cursor = LibraryDatabase.connect()
    cursor.execute("SELECT * FROM topics WHERE chapter_id = %s", (chapter_id,))
    topics = cursor.fetchall()
    cursor.close()
    return jsonify(topics)

@app.route('/content/<int:topic_id>')
def get_content(topic_id):
    cursor = db.cursor(dictionary=True)
    # cursor = LibraryDatabase.connect()
    cursor.execute("SELECT * FROM contents WHERE topic_id = %s", (topic_id,))
    result = cursor.fetchone()
    cursor.close()
    return jsonify(result if result else {"content_text": "No content available"})


if __name__ == '__main__':
    # Use a suitable WSGI server for production (like gunicorn or uwsgi)
    # Flask's built-in server is for development. `threaded=True` helps with concurrent requests/streaming.
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)