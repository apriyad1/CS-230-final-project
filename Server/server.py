'''

Reference: https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
'''

from socket import AF_INET
from socket import socket
from socket import SOCK_STREAM
from threading import Thread


clients = {}
addresses = {}
host = 'localhost'
port = 8018
buffer_size = 1024
address = (host, port)
server = socket(AF_INET, SOCK_STREAM)
server.bind(address)


# This function intercepts the incoming connections from the clients
def accept_incoming_connections():
    """Sets up handling for incoming clients"""
    while True:
        client, client_address = server.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Connected to the server", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""
    message = client.recv(buffer_size).decode("utf8")
    split = message.split('#')
    name = split[0]
    dest = ""
    if len(split) > 1:
        dest =  split[1]

    welcome = '%s Connected!! Type #QQ# to exit.' % name
    client.send(bytes(welcome, "utf8"))
    msg = "%s has joined" % name
    broadcast(msg)
    clients[client] = name

    # send the previous messages to the connected client
    old_messages = get_all_message_for_dest(name)
    for m in old_messages:
        unicast(old_messages[m], name, m)

    while True:
        message = client.recv(buffer_size).decode("utf8")
        split = message.split('#')
        msg = split[0]
        dest = split[1]

        if msg != bytes("#QQ#", "utf8"):
            if dest == "broadcast" :
                broadcast(msg, name)
            elif ',' not in dest :
                unicast(msg, dest, name)
            else :
                multicast(msg, dest, name)

        else:
            client.send(bytes("#QQ#", "utf8"))
            client.close()
            del clients[client]
            broadcast(bytes("%s has left" % name, "utf8"))
            break

# Retrieves all the messages that were sent to the user before.
# It reads all the destinationa/*/message.txt files and retrieves the messages.
def get_all_message_for_dest(destination):
    ''' returns a dictionary of strings
    The format is like this {'source' : 'message'}
    for example if UserA (destination) had received messages
    from UserB, and UserC a sample dictionary will look like -
    {UserA : msg1, UserA : msg2, UserC : msg3}'''
    return {}


# Store message in the file system. It stores the file in following manner -
# inside destination/source folder it creates a text or ureuses existing text file.
# And stores the message in the txt file. For example,
# UserA/UserB/message.txt
def store_message_in_db(source, destination, message):
    '' store the message in the database ''
    return

# Function to broadcast a message to everyne
def broadcast(msg, source=""):
    for sock in clients:
        sock.send(bytes(source + " : " + msg, "utf8"))
        if len(source) > 0:
            store_message_in_db(source, clients[sock], msg)

# Function to send a message to a particular user
def unicast(msg, dest, source=""):  
    for sock in clients:
        if clients[sock] == dest:
            sock.send(bytes(source + " : " + msg, "utf8"))
        if len(source) > 0:
            store_message_in_db(source, clients[sock], msg)

# Function to send a message to a set of users
def multicast(msg, dest, source=""):  
    dests = dest.split(',')
    for sock in clients:
        print(clients[sock])
        if clients[sock] in dests:
            sock.send(bytes(source + " : " + msg, "utf8"))
            if len(source) > 0:
                store_message_in_db(source, clients[sock], msg)


if __name__ == "__main__":
    server.listen(10)  
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()  # Starts the infinite loop.
    ACCEPT_THREAD.join()
    server.close()

