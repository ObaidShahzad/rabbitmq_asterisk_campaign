import logging

logging.basicConfig(filename='consumer.log',level=logging.INFO,format='%(asctime)s:%(levelname)s:%(message)s')
generateLogs=logging.getLogger()    