#importing resources for the manager
from socket import *
from sre_constants import SUCCESS

#setting port for manager
serverPort = 14000

#creating socket
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

#data for manager to store
players = []
games = []
gameID = 0

print("The server is ready to receive")
while True:
    #recieve data from client and parse it
    message, clientAddress = serverSocket.recvfrom(2048)
    modifiedMessage = message.decode()
    command = modifiedMessage.split(',')

    #handler for register command. Checks for duplicates of the name and for duplicates of the port on the same IPs
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
                newPlayer = (str(command[1]), str(command[2]), str(command[3]), "Not In Game")
                players.append(newPlayer)
                reply = "SUCCESS,You have been registered as " + str(command[1]) + " with IPv4 " + str(command[2]) + " on port " + str(command[3])
                serverSocket.sendto(reply.encode(), clientAddress)

    
    #Query players, just counts the number of players and builds a string to best print out the data of the players and sends the string back to the client
    elif command[0] == "query players":
        playerList = ""
        for x in players:
            playerList += "User: " + x[0] + ", " + "IPv4: " + x[1] + ", " + "Port: " + x[2] + ", " + x[3] + "\n"
        reply = "Players: " + str(len(players)) + "\n" + playerList
        serverSocket.sendto(reply.encode(), clientAddress)


    #Query games, just counts the number of games and builds a string to best print out the data of the players and sends the string back to the client
    elif command[0] == "query games":
        gameList = ""
        for x in games:
            gameList += "Game ID: " + x[0] + ", " + "Dealer: " + x[1] + ", " + "Player 1: " + x[2] + ", " + "Player 2: " + x[3] + ", " + "Player 3: " + x[4] + "\n"
        reply = "Games: " + str(len(games)) + "\n" + gameList
        serverSocket.sendto(reply.encode(), clientAddress)


    #De-register checks for if the player is in a game, if not then it checks for if the player actually exists, if they do, then the server removes them from the player list. If there's an issue, it creates an error messege
    elif command[0] == "de-register":
        userPlayingGame = False
        for x in games:
            if x[1] == command[1] or x[2] == command[1] or x[3] == command[1] or x[4] == command[1]:
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


    if command[0] == "start":
        searchNumber = int(command[1])
        playersFound = []
        dealerIndex = 0
        playernames = ["", "NONE", "NONE"]
        for index, player in enumerate(players):
            if searchNumber == 0:
                break
            if player[3] == "Waiting For Game":
                playersFound.append(index)
                searchNumber = searchNumber - 1
       
        if searchNumber != 0:
            reply = "Error: Not enough available players."
        else:
            reply = "SUCCESS"
            for index, player in enumerate(players):
                if player[0] == command[2]:
                    dealerIndex = index
                    reply += "," + player[1] + "-" + player[2] + "-" + player[0]
                    y = list(player)
                    y[3] = "In Game"
                    x = tuple(y)
                    players[index] = x
            
            for index, x in enumerate(playersFound):
                y = list(players[x])
                y[3] = "In Game"
                players[x] = tuple(y)
                reply += "," + players[x][1] + "-" + players[x][2] + "-" + players[x][0]
                playernames[index] = players[x][0]

            gameID += 1
            newGame = (str(gameID), players[dealerIndex][0], playernames[0], playernames[1], playernames[2])
            games.append(newGame)
        serverSocket.sendto(reply.encode(), clientAddress)

    if command[0] == "waiting":
        reply = "Error"
        for index, player in enumerate(players):
            if player[0] == command[1] and player[3] == "Not In Game":
                y = list(player)
                y[3] = "Waiting For Game"
                x = tuple(y)
                players[index] = x
                reply = "SUCCESS"
            if player[0] == command[1] and player[3] == "Waiting For Game":
                y = list(player)
                y[3] = "Not In Game"
                x = tuple(y)
                players[index] = x
                reply = "SUCCESS"
        serverSocket.sendto(reply.encode(), clientAddress)
            
            

