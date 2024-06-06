"""
Project 6- Creating a Reciever
Christian Jackson
6/6/24
"""

# Imports for file
import pika
import sys
import time
import struct
from datetime import datetime
from collections import deque

# Define deques
smoker_temps = deque(maxlen=5)  
foodA_temps = deque(maxlen=20)  
foodB_temps = deque(maxlen=20) 

def smoker_callback(ch, method, properties, body):
    """Define behavior on getting a message from the smoker queue."""
    timestamp, temperature = struct.unpack('!df', body)
    timestamp_str = datetime.fromtimestamp(timestamp).strftime("%m/%d/%y %H:%M:%S")
    print(f"Received from smoker queue: {timestamp_str} - Temperature: {temperature}F")

    # Add the new temperature reading to the deque
    smoker_temps.append(temperature)

    # Check if the temperature drop is 15F or more within the last 2.5 minutes
    if len(smoker_temps) == smoker_temps.maxlen:
        if smoker_temps[0] - temperature >= 15:
            print("Smoker alert! Temperature dropped by 15F or more in the last 2.5 minutes!")

    print("Done.")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def foodA_callback(ch, method, properties, body):
    """Define behavior on getting a message from the food A queue."""
    timestamp, temperature = struct.unpack('!df', body)
    timestamp_str = datetime.fromtimestamp(timestamp).strftime("%m/%d/%y %H:%M:%S")
    print(f"Received from food A queue: {timestamp_str} - Temperature: {temperature}F")

    # Add the new temperature reading to the deque
    foodA_temps.append(temperature)

    # Check if the temperature change is 1F or less within the last 10 minutes
    if len(foodA_temps) == foodA_temps.maxlen:
        if max(foodA_temps) - min(foodA_temps) <= 1:
            print("Food A stall alert! Temperature change is 1F or less in the last 10 minutes!")

    print("Done.")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def foodB_callback(ch, method, properties, body):
    """Define behavior on getting a message from the food B queue."""
    timestamp, temperature = struct.unpack('!df', body)
    timestamp_str = datetime.fromtimestamp(timestamp).strftime("%m/%d/%y %H:%M:%S")
    print(f"Received from food B queue: {timestamp_str} - Temperature: {temperature}F")

    # Add the new temperature reading to the deque
    foodB_temps.append(temperature)

    # Check if the temperature change is 1F or less within the last 10 minutes
    if len(foodB_temps) == foodB_temps.maxlen:
        if max(foodB_temps) - min(foodB_temps) <= 1:
            print("Food B stall alert! Temperature change is 1F or less in the last 10 minutes!")

    print("Done.")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    """Continuously listen for task messages on named queues."""
    hn = "localhost"

    try:
        # Create a blocking connection to the RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hn))
    except Exception as e:
        print()
        print("ERROR: connection to RabbitMQ server failed.")
        print(f"Verify the server is running on host={hn}.")
        print(f"The error says: {e}")
        print()
        sys.exit(1)

    try:
        # Use the connection to create a communication channel
        channel = connection.channel()

        # Declare each queue
        queues = ["01-smoker", "02-food-A", "03-food-B"]
        for queue in queues:
            channel.queue_delete(queue=queue)
            channel.queue_declare(queue=queue, durable=True)

        # Set the prefetch count to limit the number of messages being processed concurrently
        channel.basic_qos(prefetch_count=1)

        # Configure the channel to listen on each queue with corresponding callback function
        channel.basic_consume(queue="01-smoker", on_message_callback=smoker_callback, auto_ack=False)
        channel.basic_consume(queue="02-food-A", on_message_callback=foodA_callback, auto_ack=False)
        channel.basic_consume(queue="03-food-B", on_message_callback=foodB_callback, auto_ack=False)

        # Print a message to the console for the user
        print(" [*] Ready for work. To exit press CTRL+C")

        # Start consuming messages via the communication channel
        channel.start_consuming()

    except Exception as e:
        print()
        print("ERROR: something went wrong.")
        print(f"The error says: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print()
        print(" User interrupted continuous listening process.")
        sys.exit(0)
    finally:
        print("\nClosing connection. Goodbye.\n")
        connection.close()

if __name__ == "__main__":
    main()