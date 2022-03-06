#importing resources for the peer software to use
from socket import *
import sys
import time
import random

#recording the arguments for reaching the manager
managerName = sys.argv[1]
managerPort = int(sys.argv[2])

registered = False
playerSocket = socket(AF_INET, SOCK_DGRAM)
playerName = ""
playerIP= ""
playerPort= ""
playerInfo= ""
playersInformation = []
nextPlayer = ""
#variables for playing the card game
deckTemplate = ["2S", "3S", "4S", "5S", "6S", "7S", "8S", "9S", "10S", "JS", "QS", "KS", "AS", "2D", "3D", "4D", "5D", "6D", "7D", "8D", "9D", "10D", "JD", "QD", "KD", "AD", "2C", "3C", "4C", "5C", "6C", "7C", "8C", "9C", "10C", "JC", "QC", "KC", "AC", "2H", "3H", "4H", "5H", "6H", "7H", "8H", "9H", "10H", "JH", "QH", "KH", "AH"]
discardPile = []
dealerHand = []
player2Hand = []
player3Hand = []
player4Hand = []
cardDeck = []


#Function to be ran by peers when they are playing the card game
def play_game():
    global playerSocket
    global cardDeck
    global discardPile
    global dealerHand
    global player2Hand
    global player3Hand
    global player4Hand
    gameover = False
    while gameover == False:
        playerSocket = socket(AF_INET, SOCK_DGRAM)
        playerSocket.bind(('', int(playerPort)))
        modifiedmessage, serveraddress = playerSocket.recvfrom(16384)
        playerSocket.close()
        command = modifiedmessage.decode().split('|')
        #handler for siplaying general messeges
        if command[0] == "ms":
            print(command[1])
        #handler for dupdating game info across users
        if command[0] == "update":
            newdeck = command[1].split(',')
            cardDeck = []
            for x in newdeck:
                cardDeck.append(x)
            
            newdiscard = command[2].split(',')
            discardPile = []
            for x in newdiscard:
                discardPile.append(x)
            
            newdealer = command[3].split(',')
            dealerHand = []
            for x in newdealer:
                dealerHand.append(x)

            newp2 = command[4].split(',')
            player2Hand = []
            for x in newp2:
                player2Hand.append(x)

            if len(playersInformation) > 2:
                newp3 = command[5].split(',')
                player3Hand = []
                for x in newp3:
                    player3Hand.append(x)
            
            if len(playersInformation) > 3:
                newp4 = command[6].split(',')
                player4Hand = []
                for x in newp4:
                    player4Hand.append(x)

            display_game_state()


    
#function to be ran by the dealer to set up the game
def start_game():
    global cardDeck
    global dealerHand
    global discardPile
    global player2Hand
    global player3Hand
    global player4Hand
    global playersInformation

    time.sleep(2)
    messege = "Shuffling cards..."
    print(messege)
    messege = "ms|Shuffling cards..."
    for x in playersInformation:
        if x.split('-')[2] != playerName:
            peersocket = socket(AF_INET, SOCK_DGRAM)
            peersocket.sendto(messege.encode(),(x.split('-')[0], int(x.split('-')[1])))
            peersocket.close()
    
    cardDeck = deckTemplate
    random.shuffle(cardDeck)
    time.sleep(2)

    messege = "Giving players thier cards..."
    print(messege)
    messege = "ms|Giving players thier cards..."
    for x in playersInformation:
        if x.split('-')[2] != playerName:
            peersocket = socket(AF_INET, SOCK_DGRAM)
            peersocket.sendto(messege.encode(),(x.split('-')[0], int(x.split('-')[1])))
            peersocket.close()
    for x in range(6):
        dealerHand.append(cardDeck.pop() + "*")
        player2Hand.append(cardDeck.pop() + "*")
        if len(playersInformation) > 2:
            player3Hand.append(cardDeck.pop() + "*")
        if len(playersInformation) > 3:
            player4Hand.append(cardDeck.pop() + "*")
    time.sleep(2)

    messege = "Moving 1 card to descard pile..."
    print(messege)
    messege = "ms|Moving 1 card to descard pile..."
    for x in playersInformation:
        if x.split('-')[2] != playerName:
            peersocket = socket(AF_INET, SOCK_DGRAM)
            peersocket.sendto(messege.encode(),(x.split('-')[0], int(x.split('-')[1])))
            peersocket.close()
    discardPile.append(cardDeck.pop())
    time.sleep(2)

    messege = "Game starting"
    print(messege)
    messege = "ms|Game starting"
    for x in playersInformation:
        if x.split('-')[2] != playerName:
            peersocket = socket(AF_INET, SOCK_DGRAM)
            peersocket.sendto(messege.encode(),(x.split('-')[0], int(x.split('-')[1])))
            peersocket.close()

    time.sleep(2)
    send_update()
    play_turn()

#function to decide who will be the next player in turn order
def set_next_player():
    global nextPlayer
    position = 0
    for index, x in enumerate(playersInformation):
        if x == playerIP + "-" + playerPort + "-" + playerName:
            position = index
    if position + 1 == len(playersInformation):
        nextPlayer = playersInformation[0]
    else:
        nextPlayer = playersInformation[position+1]

#fucntion to update info across players and to update the display of said info
def send_update():
    global playerSocket
    messege = "update|"
    for x in cardDeck:
        messege += x + ","
    messege = messege[:-1]
    messege += "|"

    for x in discardPile:
        messege += x + ","
    messege = messege[:-1]
    messege += "|"

    for x in dealerHand:
        messege += x + ","
    messege = messege[:-1]
    messege += "|"

    for x in player2Hand:
        messege += x + ","
    messege = messege[:-1]

    if len(playersInformation) > 2:
        messege += "|"
        for x in player3Hand:
            messege += x + ","
            messege = messege[:-1]
            
    
    if len(playersInformation) > 3:
        messege += "|"
        for x in player4Hand:
            messege += x + ","
            messege = messege[:-1]
    
    for x in playersInformation:
        if x.split('-')[2] != playerName:
            print(messege)
            peersocket = socket(AF_INET, SOCK_DGRAM)
            peersocket.sendto(messege.encode(),(x.split('-')[0], int(x.split('-')[1])))
            peersocket.close()
    
    display_game_state()

#print current setup
def display_game_state():
    global playersInformation
    print("Deck: " + str(len(cardDeck)) + " cards")
    print("Discard Pile: " + discardPile[-1] + " face up")
    for index, x in enumerate(playersInformation):
        if index == 0:
            print(x.split('-')[2] + "'s Hand:")
            handtext = ""
            if "*" in dealerHand[0]:
                handtext += "**** "
            else:
                handtext += dealerHand[0] + " "
            if "*" in dealerHand[1]:
                handtext += "**** "
            else:
                handtext += dealerHand[1] + " "
            if "*" in dealerHand[2]:
                handtext += "****\n"
            else:
                handtext += dealerHand[2] + "\n"
            if "*" in dealerHand[3]:
                handtext += "**** "
            else:
                handtext += dealerHand[3] + " "
            if "*" in dealerHand[4]:
                handtext += "**** "
            else:
                handtext += dealerHand[4] + " "
            if "*" in dealerHand[5]:
                handtext += "**** "
            else:
                handtext += dealerHand[5] + " "
            print(handtext)
        if index == 1:
            print(x.split('-')[2] + "'s Hand:")
            handtext = ""
            if "*" in player2Hand[0]:
                handtext += "**** "
            else:
                handtext += player2Hand[0] + " "
            if "*" in player2Hand[1]:
                handtext += "**** "
            else:
                handtext += player2Hand[1] + " "
            if "*" in player2Hand[2]:
                handtext += "****\n"
            else:
                handtext += player2Hand[2] + "\n"
            if "*" in player2Hand[3]:
                handtext += "**** "
            else:
                handtext += player2Hand[3] + " "
            if "*" in player2Hand[4]:
                handtext += "**** "
            else:
                handtext += player2Hand[4] + " "
            if "*" in player2Hand[5]:
                handtext += "**** "
            else:
                handtext += player2Hand[5] + " "
            print(handtext)
        if index == 2:
            print(x.split('-')[2] + "'s Hand:")
            handtext = ""
            if "*" in player3Hand[0]:
                handtext += "**** "
            else:
                handtext += player3Hand[0] + " "
            if "*" in player3Hand[1]:
                handtext += "**** "
            else:
                handtext += player3Hand[1] + " "
            if "*" in player3Hand[2]:
                handtext += "****\n"
            else:
                handtext += player3Hand[2] + "\n"
            if "*" in player3Hand[3]:
                handtext += "**** "
            else:
                handtext += player3Hand[3] + " "
            if "*" in player3Hand[4]:
                handtext += "**** "
            else:
                handtext += player3Hand[4] + " "
            if "*" in player3Hand[5]:
                handtext += "**** "
            else:
                handtext += player3Hand[5] + " "
            print(handtext)
        if index == 3:
            print(x.split('-')[2] + "'s Hand:")
            handtext = ""
            if "*" in player4Hand[0]:
                handtext += "**** "
            else:
                handtext += player4Hand[0] + " "
            if "*" in player4Hand[1]:
                handtext += "**** "
            else:
                handtext += player4Hand[1] + " "
            if "*" in player4Hand[2]:
                handtext += "****\n"
            else:
                handtext += player4Hand[2] + "\n"
            if "*" in player4Hand[3]:
                handtext += "**** "
            else:
                handtext += player4Hand[3] + " "
            if "*" in player4Hand[4]:
                handtext += "**** "
            else:
                handtext += player4Hand[4] + " "
            if "*" in player4Hand[5]:
                handtext += "**** "
            else:
                handtext += player4Hand[5] + " "
            print(handtext)

def play_turn():
    print("turn")

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
                playerIP = inputIP
                playerPort = inputPort
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
        if username == playerName:
            registered = False
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
                    print("Players Found")
                    for x in range(int(players)):
                        friend = returnmessege[2+x].split('-')
                        clientSocket = socket(AF_INET, SOCK_DGRAM)
                        clientSocket.sendto(sendmessege.encode(),(friend[0], int(friend[1])))
                        clientSocket.close()
                        print("Sent connection info to player at IP: " + friend[0] + " On port: " + friend[1])
                    info = returnmessege
                    info.pop(0)
                    playersInformation = info
                    set_next_player()
                    start_game()
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
                playerSocket.settimeout(30.0)
                try:
                    modifiedMessage, serverAddress = playerSocket.recvfrom(2048)
                    returnmessege = modifiedMessage.decode()
                    playerSocket.close()
                    info = returnmessege.split(',')
                    info.pop(0)
                    playersInformation = info
                    print("Joined Game")
                    set_next_player()
                    play_game()
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
        messege = "de-register," + playerName
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        clientSocket.sendto(messege.encode(),(managerName, managerPort))
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
        clientSocket.close()
        break
    else:
        print("Error: Please use a vaild input.")
        userIn = input('Enter Command:')

