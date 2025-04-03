import logging
import os
from datetime import datetime
from src.exception import CustomException
import sys

# 3. after exceptin.py
LOG_FILE=f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
logs_path=os.path.join(os.getcwd(),"logs",LOG_FILE) #cwd  - current working directory >ckd prediction> "logs" directory/folder  > log_file.log directory 
os.makedirs(logs_path,exist_ok=True) # if there exist already "logs" directory/folder keep on appending  logs directory to it else create a new one directory

LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE) #logfile.log file is created  in logs folder/directory

# 4.
logging.basicConfig( # function to print  the log messages on console and also write it into a .log file
    filename=LOG_FILE_PATH, 
    format= "[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s", ##structure how log message is printed
    level = logging.INFO #to print the exception tracebacks and other important information, like logging.INFO(Exception) or logging.INFO("executed")

)

# 5. before EDA
if __name__=="__main__":
    try:
        a =1/0
    except Exception as e:
        # logging.info("logging has started")
        raise logging.info(CustomException(e,sys))