import mysql.connector
import pika
from logger_producer import genlog
credentials = pika.PlainCredentials('admin', 'root')
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters('10.0.0.121',5672,'/',credentials))
    channel = connection.channel()
    channel.queue_declare(queue='delta', durable=True)
    try:
        connection = mysql.connector.connect(host='10.0.1.98',database='campaign',user='root',password='awais')
        if connection.is_connected():
            genlog.info("Connection Established with MySQL Server")
            cursor = connection.cursor()
            cursor.execute("select * from customers;")
            Result=cursor.fetchall()
            if len(Result) == 0:
                genlog.info("Query Returned Nothing ! [ Nothing to Publish ]")
            else:
                for result in Result:
                    dictionary={"id":result[0],"name":result[1],"phone_number":result[2],"email":result[3],"process_id":result[4],"process_time":result[5]}                    
                    channel.basic_publish(exchange='', routing_key='delta', body=str(dictionary))
                    genlog.info("Publish Successfull")
    except mysql.connector.Error as e:
        genlog.error(f"Error while connecting to MySQL : {e}")
        
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
except:
    genlog.error("Error while connecting to RabbitMQ Server !!") 