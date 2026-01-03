# from src.logger import logging

# logging.debug("This is a debug message from demo.py")
# logging.info("This is an info message from demo.py")
# logging.warning("This is a warning message from demo.py")
# logging.error("This is an error message from demo.py")      

# from src.exception import MyException   
# import sys

# try:
#     a = 1 / 0
# except Exception as e:
#     logging.info(e)
#     raise MyException(e, sys) from e

from src.pipline.training_pipeline import TrainPipeline
training_pipeline = TrainPipeline()
training_pipeline.run_pipeline()