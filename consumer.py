import pika
import mysql.connector
import datetime
from logger_consumer import generateLogs
import asterisk.manager

credentials = pika.PlainCredentials('admin', 'root')
connection = pika.BlockingConnection(pika.ConnectionParameters('10.0.0.121',5672,'/',pika.PlainCredentials('admin', 'root')))
channel = connection.channel()
channel.queue_declare(queue='delta', durable=True)

AMImanager = asterisk.manager.Manager()
AMImanager.connect('10.0.1.169')
AMImanager.login('awais', 'awais')
def callback(ch, method, properties, body):
    global cursor
    global sqlconnection
    body=body.decode("utf-8")
    data=eval(body)
    generateLogs.info(f" [x] Received {data}")
    ch.basic_ack(delivery_tag=method.delivery_tag)
    phone=data["phone_number"]
    if int(phone) != 0:
        response=AMImanager.originate(
        channel="SIP/auto_campaign",
        exten=103,
        context='phones', 
        priority='1', 
        timeout='8000', 
        application=None, 
        data=None, 
        caller_id="Automated Campaign", 
        run_async=False, 
        earlymedia='false', 
        account=None, 
        variables={'UEXT':phone,'NAME':data["name"]}
        )
        if str(response) == "Success":
            generateLogs.info("[+] Call was Picked Up")
            process_id=data["process_id"]
            process_id=int(process_id)+1
            time_now=str(datetime.datetime.now())
            time_now=time_now[:19]
            query=f"UPDATE customers SET `process_id`='{process_id}' , `process_time`= '{time_now}' where id={data['id']}"
            cursor.execute(query)
            sqlconnection.commit()
        else:
            generateLogs.info(" [X] Call was not Picked Up")


try:
    sqlconnection = mysql.connector.connect(host='10.0.1.98',database='campaign',user='root',password='awais')
    cursor = sqlconnection.cursor()
    channel.basic_consume(queue='delta', on_message_callback=callback)
    generateLogs.info(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
except mysql.connector.Error as error:
    generateLogs.error("Failed to update table record: {}".format(error))
finally:
    if (sqlconnection.is_connected()):
        connection.close()