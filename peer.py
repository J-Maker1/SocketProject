#importing resources for the peer software to use
from socket import *
import sys

#recording the arguments for reaching the manager
managerName = sys.argv[1]
managerPort = int(sys.argv[2])

registered = False
playerSocket = socket(AF_INET, SOCK_DGRAM)


print(
"1: Register \n2: Query Players \n3: Query Games \n4: De-register \n5: Exit"
)
userIn = input('Enter Command: ')
while userIn != 5:

    #Condition for registering. A username, IP, and Port are requested, a command is sent, and a reply is returned. Based on the reply, the conditional statement will notify the user of it and adjust some variables for future use of the command
    if userIn == '1':
        #check if peer already registered theirself
        if registered == False:
            registered = True
            username = input('Enter Username: ')
            inputIP = input('Enter IPv4: ')
            inputPort = input('Enter Port: ')
            clientSocket = socket(AF_INET, SOCK_DGRAM)
            
            #send command 'register' along with command argument
            message = "register," + username + "," + str(inputIP) + "," + str(inputPort)
            clientSocket.sendto(message.encode(),(managerName, managerPort))
            
            #recieve reply from server
            modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
            clientSocket.close()
            returnmessege = modifiedMessage.decode().split(',')
            
            #if success we notify the user and make an official player socket bound to an open port specified from the server
            if returnmessege[0] == "SUCCESS":
                playerSocket.bind(('', int(inputPort)))
                print(returnmessege[1])
            #if reply is a failure
            else:
                print(returnmessege)
                registered = False

        else:
            print("Error: Already Registerd")

        
        userIn = input('Enter Command: ')

    #condition for querying players, User selects option, command is sent, and a reply is recieved    
    elif userIn == '2':
        messege = "query players"
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        clientSocket.sendto(messege.encode(),(managerName, managerPort))
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
        clientSocket.close()
        returnmessege = modifiedMessage.decode()
        print(returnmessege)

        userIn = input('Enter Command:')
    
    #condition for querying games. User selects option, command is sent to server, and a reply is recieved
    elif userIn == '3':
        messege = "query games"
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        clientSocket.sendto(messege.encode(),(managerName, managerPort))
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
        clientSocket.close()
        returnmessege = modifiedMessage.decode()
        print(returnmessege)

        userIn = input('Enter Command:')
        
    #Condition for de-registering. User selects command and types in user name and waits for the server's reply
    elif userIn == '4':
        username = input('Enter User To De-Register: ')
        messege = "de-register," + username
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        clientSocket.sendto(messege.encode(),(managerName, managerPort))
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
        clientSocket.close()
        returnmessege = modifiedMessage.decode()
        print(returnmessege)

        userIn = input('Enter Command:')
    elif userIn == '5':
        break
    else:
        print("Error: Please use a vaild input.")
        userIn = input('Enter Command:')
