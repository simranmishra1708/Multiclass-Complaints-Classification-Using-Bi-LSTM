import logging
import os
from logging.handlers import RotatingFileHandler
from from_root import from_root
from datetime import datetime

# Constants for log configuration
LOG_DIR = 'logs'
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3  # Number of backup log files to keep

# Construct log file path
log_dir_path = os.path.join(from_root(), LOG_DIR)
os.makedirs(log_dir_path, exist_ok=True)
log_file_path = os.path.join(log_dir_path, LOG_FILE)

def configure_logger():
    """
    Configures logging with a rotating file handler and a console handler.
    """
    # Create a custom logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Define formatter
    formatter = logging.Formatter("[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s")

    # File handler with rotation
    file_handler = RotatingFileHandler(log_file_path, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Configure the logger
configure_logger()




# 1️⃣ Imports (What tools are we using?)
# import logging


# This is Python’s built-in logging system

# Used to record:

# errors

# warnings

# info messages

# debug details

# Instead of print(), production code uses logging.

# import os


# Used for file and folder operations

# Example:

# create directories

# join paths safely

# check file existence

# from logging.handlers import RotatingFileHandler


# Special logging handler

# Automatically creates new log files when the old one becomes too big

# Prevents logs from growing infinitely

# from from_root import from_root


# Custom utility function

# Returns the project root directory

# Ensures logs are always written relative to project root

# Example:

# /home/user/project_root/logs/...

# from datetime import datetime


# Used to get current date and time

# Helps create unique log file names

# 2️⃣ Log Configuration Constants (Settings)
# LOG_DIR = 'logs'


# Name of the folder where logs will be stored

# LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"


# Creates a unique log file name using current date & time

# Example filename:

# 01_03_2026_22_15_42.log


# This avoids overwriting old logs.

# MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB


# Maximum size of one log file

# Once file reaches 5 MB, a new log file is created

# BACKUP_COUNT = 3


# Number of old log files to keep

# When limit is reached:

# oldest log file is deleted automatically

# 3️⃣ Construct Log Directory Path
# log_dir_path = os.path.join(from_root(), LOG_DIR)


# Combines:

# project root path

# logs folder

# Creates an absolute path

# Example:

# /home/user/project_root/logs

# os.makedirs(log_dir_path, exist_ok=True)


# Creates the logs folder if it does not exist

# exist_ok=True means:

# no error if folder already exists

# log_file_path = os.path.join(log_dir_path, LOG_FILE)


# Full path of the log file

# Example:

# /home/user/project_root/logs/01_03_2026_22_15_42.log

# 4️⃣ Logger Configuration Function
# def configure_logger():


# Defines a function to set up logging

# Makes logging configuration reusable and clean

# 4.1 Create the Logger
# logger = logging.getLogger()


# Gets the root logger

# This logger will capture logs from the entire project

# logger.setLevel(logging.DEBUG)


# Sets the lowest level of logs to capture

# DEBUG means:

# capture everything: debug, info, warning, error, critical

# 5️⃣ Define Log Format
# formatter = logging.Formatter(
#     "[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s"
# )


# This controls how each log message looks.

# Example output:

# [ 2026-01-03 22:20:45 ] root - INFO - Model training started


# Components:

# asctime → timestamp

# name → logger name

# levelname → INFO, DEBUG, ERROR

# message → your log message

# 6️⃣ File Handler (Log to File)
# file_handler = RotatingFileHandler(
#     log_file_path,
#     maxBytes=MAX_LOG_SIZE,
#     backupCount=BACKUP_COUNT
# )


# What this does:

# Writes logs to a file

# Automatically rotates log files when size exceeds 5MB

# Keeps only last 3 backup files

# file_handler.setFormatter(formatter)


# Applies the log format to file logs

# file_handler.setLevel(logging.DEBUG)


# File will store all logs (debug + info + errors)

# Useful for deep debugging later

# 7️⃣ Console Handler (Log to Terminal)
# console_handler = logging.StreamHandler()


# Sends logs to terminal / console

# console_handler.setFormatter(formatter)


# Same format as file logs

# console_handler.setLevel(logging.INFO)


# Console shows only:

# INFO

# WARNING

# ERROR

# Hides noisy DEBUG logs from terminal

# 8️⃣ Attach Handlers to Logger
# logger.addHandler(file_handler)


# Adds file logging capability

# logger.addHandler(console_handler)


# Adds console logging capability

# Now:

# Logs go to file + console

# With different verbosity levels

# 9️⃣ Activate Logger
# configure_logger()


# Calls the function

# Logging is now active for the entire project

# From now on, anywhere in your code:

# logging.info("Data ingestion started")
# logging.error("Model failed to load")


# will automatically be logged.