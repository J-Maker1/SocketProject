#importing resources for the peer software to use
from socket import *
import sys
import time

#recording the arguments for reaching the manager
managerName = sys.argv[1]
managerPort = int(sys.argv[2])

registered = False
playerSocket = socket(AF_INET, SOCK_DGRAM)
playerName = ""

def play_game():
    print("Test")

print(
"0: Exit \n1: Register \n2: Query Players \n3: Query Games \n4: De-register \n5: Start A Game \n6: Join A Game"
)
userIn = input('Enter Command: ')
while userIn != 0:

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
                playerName = username
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

    #condition to query the start of a game
    elif userIn == '5':
        if registered == True:
            players = input('How many players do you wish to play with? 1-3: ')
            if players != '1' and players != '2' and players != '3':
                print("Error: Invalid number of players requested.\n")
            else:
                messege = "start," + players + "," + playerName
                clientSocket = socket(AF_INET, SOCK_DGRAM)
                clientSocket.sendto(messege.encode(),(managerName, managerPort))
                modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
                clientSocket.close()
                returnmessege = modifiedMessage.decode().split(',')
                sendmessege = modifiedMessage.decode()
                if returnmessege[0] == "SUCCESS":
                    print("Game created")
                    for x in range(int(players)):
                        friend = returnmessege[2+x].split('-')
                        clientSocket = socket(AF_INET, SOCK_DGRAM)
                        clientSocket.sendto(sendmessege.encode(),(friend[0], int(friend[1])))
                        clientSocket.close()
                        print("Sent to: " + friend[0] + " At port: " + friend[1])
                else:
                    print(returnmessege)
        else:
            print("Error: Must be registered to start a game.")
        userIn = input('Enter Command:')

    #An extra adition to switch the user into listening mode to be pulled into a game
    elif userIn == '6':
        if registered == True:
            messege = "waiting," + playerName
            clientSocket = socket(AF_INET, SOCK_DGRAM)
            clientSocket.sendto(messege.encode(),(managerName, managerPort))
            modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
            clientSocket.close()
            returnmessege = modifiedMessage.decode()
            if returnmessege == "SUCCESS":
                print("Waiting for game...")
                playerSocket.settimeout(10.0)
                try:
                    modifiedMessage, serverAddress = playerSocket.recvfrom(2048)
                    returnmessege = modifiedMessage.decode()
                    print(returnmessege)
                    playerSocket.close()
                except:
                    print("Wasn't picked up for game.")
                    messege = "waiting," + playerName
                    clientSocket = socket(AF_INET, SOCK_DGRAM)
                    clientSocket.sendto(messege.encode(),(managerName, managerPort))
                    modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
                    clientSocket.close()
            else:
                print("Soemthing went wrong")
        else:
            print("Error: Must be registered to play in a game.")
        userIn = input('Enter Command:')

    elif userIn == '0':
        break
    else:
        print("Error: Please use a vaild input.")
        userIn = input('Enter Command:')

