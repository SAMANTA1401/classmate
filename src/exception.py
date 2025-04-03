import sys

# 1.before logger.py
def error_message_details(error, error_details:sys):
    _,_,exc_tb = error_details.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    error_message = f"Error occured in python script name [{file_name}] line number [{exc_tb.tb_lineno}] error message [{str(error)}]"

    return error_message
# 2.
class CustomException(Exception):
    # 2.1
    def __init__(self,error_message,error_details:sys):
        super().__init__(error_message) ## inheritance from  base class Exception
        self.error_message=error_message_details(error_message,error_details=error_details) #return from error_message_details() function
    
    # 2.2
    def __str__(self):
        return self.error_message # return from error_message_details() function whenever  object of this class is called 