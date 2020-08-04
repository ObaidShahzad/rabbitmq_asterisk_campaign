import logging
LOG_FORMAT="%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename='producer.log',level=logging.INFO,format=LOG_FORMAT)

genlog=logging.getLogger()