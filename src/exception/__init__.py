import sys
import logging

def error_message_detail(error: Exception, error_detail: sys) -> str:
    """
    Extracts detailed error information including file name, line number, and the error message.

    :param error: The exception that occurred.
    :param error_detail: The sys module to access traceback details.
    :return: A formatted error message string.
    """
    # Extract traceback details (exception information)
    _, _, exc_tb = error_detail.exc_info()

    # Get the file name where the exception occurred
    file_name = exc_tb.tb_frame.f_code.co_filename

    # Create a formatted error message string with file name, line number, and the actual error
    line_number = exc_tb.tb_lineno
    error_message = f"Error occurred in python script: [{file_name}] at line number [{line_number}]: {str(error)}"
    
    # Log the error for better tracking
    logging.error(error_message)
    
    return error_message

class MyException(Exception):
    """
    Custom exception class for handling errors in the US visa application.
    """
    def __init__(self, error_message: str, error_detail: sys):
        """
        Initializes the Exception with a detailed error message.

        :param error_message: A string describing the error.
        :param error_detail: The sys module to access traceback details.
        """
        # Call the base class constructor with the error message
        super().__init__(error_message)

        # Format the detailed error message using the error_message_detail function
        self.error_message = error_message_detail(error_message, error_detail)

    def __str__(self) -> str:
        """
        Returns the string representation of the error message.
        """
        return self.error_message
    




# 🔴 Purpose of This Module (Before Code)

# This module exists to:

# Capture where an error happened

# Capture what exactly went wrong

# Log it properly

# Raise a clean, informative exception

# Instead of vague errors like:

# ValueError: something went wrong


# You get:

# Error occurred in python script: [data_ingestion.py] at line number [42]: File not found


# This is professional-grade debugging.

# 1️⃣ Imports
# import sys


# sys gives access to system-level details

# Here, it’s used to extract traceback information
# (file name, line number, call stack)

# import logging


# Used to log errors

# Ensures errors are recorded in log files

# Integrates with your logging module

# 2️⃣ error_message_detail Function
# def error_message_detail(error: Exception, error_detail: sys) -> str:

# What this function does

# It extracts detailed information from an exception:

# Which file crashed

# Which line crashed

# What the error message was

# Parameters
# error: Exception


# The actual exception that occurred

# Example: FileNotFoundError, ValueError

# error_detail: sys


# The sys module

# Used to access Python’s internal traceback info

# 2.1 Extract traceback details
# _, _, exc_tb = error_detail.exc_info()

# What exc_info() returns

# It returns a tuple:

# (type, value, traceback)


# We only care about:

# traceback → stored in exc_tb

# The _ means:

# “I don’t need the first two values”

# 2.2 Get file name where error occurred
# file_name = exc_tb.tb_frame.f_code.co_filename


# Breakdown:

# exc_tb → traceback object

# tb_frame → frame where error happened

# f_code → compiled code info

# co_filename → file name

# Result:

# /src/components/data_ingestion.py

# 2.3 Get line number
# line_number = exc_tb.tb_lineno


# This tells:

# Exactly which line number caused the crash

# 2.4 Create readable error message
# error_message = f"Error occurred in python script: [{file_name}] at line number [{line_number}]: {str(error)}"


# This builds a human-readable error like:

# Error occurred in python script: [data_ingestion.py] at line number [45]: File not found


# Much better than default Python errors.

# 2.5 Log the error
# logging.error(error_message)


# Writes error into:

# log file

# console (depending on config)

# This ensures:
# ✔ error is saved
# ✔ error is traceable later

# 2.6 Return error message
# return error_message


# Returns the formatted message

# Used later by the custom exception class

# 3️⃣ MyException Class (Custom Exception)
# class MyException(Exception):

# What this does

# Creates your own exception type

# Allows you to raise meaningful, consistent errors across the project

# 3.1 Constructor (__init__)
# def __init__(self, error_message: str, error_detail: sys):

# Parameters

# error_message: short description

# error_detail: sys module for traceback info

# super().__init__(error_message)


# Calls Python’s base Exception class

# Ensures this behaves like a normal exception

# 3.2 Attach detailed error message
# self.error_message = error_message_detail(error_message, error_detail)


# What happens here:

# Calls error_message_detail

# Extracts file name, line number, actual error

# Stores the formatted message

# This is the core logic.

# 3.3 String representation
# def __str__(self) -> str:


# This method controls:

# print(exception)

# return self.error_message


# So when the exception is printed, you see the full detailed message, not just a generic one.

# 4️⃣ How This Is Used in Your Project (IMPORTANT)

# Example usage:

# try:
#     df = pd.read_csv("missing_file.csv")
# except Exception as e:
#     raise MyException(e, sys)


# Instead of:

# FileNotFoundError


# You get:

# Error occurred in python script: [data_ingestion.py] at line number [23]: missing_file.csv
