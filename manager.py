#importing resources for the manager
from socket import *

#setting port for manager
serverPort = 14000

#creating socket
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

#data for manager to store
players = []
games = []


print("The server is ready to receive")
while True:
    #recieve data from client and parse it
    message, clientAddress = serverSocket.recvfrom(2048)
    modifiedMessage = message.decode()
    command = modifiedMessage.split(',')

    #handler for register command
    if command[0] == "register":
        duplicateName = False
        duplicatePort = False
        for x in players:
            if x[0] == command[1]:
                duplicateName = True
            if x[1] == command[2] and x[2] == command[3]:
                duplicatePort = True
        if duplicateName == True:
            reply = "ERROR: Username already in use!"
            serverSocket.sendto(reply.encode(), clientAddress)
        else:
            if duplicatePort == True:
                reply = "ERROR: Port already in use on IP!"
                serverSocket.sendto(reply.encode(), clientAddress)
            else:
                newPlayer = (str(command[1]), str(command[2]), str(command[3]))
                players.append(newPlayer)
                reply = "SUCCESS,You have been registered as " + str(command[1]) + " with IPv4 " + str(command[2]) + " on port " + str(command[3])
                serverSocket.sendto(reply.encode(), clientAddress)

    elif command[0] == "query players":
        playerList = ""
        for x in players:
            playerList += "User: " + x[0] + ", " + "IPv4: " + x[1] + ", " + "Port: " + x[2] + "\n"
        reply = "Players: " + str(len(players)) + "\n" + playerList
        serverSocket.sendto(reply.encode(), clientAddress)

    elif command[0] == "query games":
        gameList = ""
        for x in games:
            gameList += "Game ID: " + x + "Dealer: " + x[0] + ", " + "Player 1: " + x[1] + ", " + "Player 2: " + x[2] + "Player 3: " + x[3] + "\n"
        reply = "Games: " + str(len(games)) + "\n" + gameList
        serverSocket.sendto(reply.encode(), clientAddress)

    elif command[0] == "de-register":
        userPlayingGame = False
        for x in games:
            if x[0] == command[1] or x[1] == command[1] or x[2] == command[1] or x[3] == command[1]:
                userPlayingGame = True
        
        if userPlayingGame == False:
            userFound = False
            for index, player in enumerate(players):
                if player[0] == command[1]:
                    userFound = True
                    players.pop(index)
                    break
            if userFound == True:
                reply = "User de-registered"
            else:
                reply = "Error: User not found"
        else:
            reply = "Error: User currently in game!"
        serverSocket.sendto(reply.encode(), clientAddress)
                    
            
        
        
    