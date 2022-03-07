#importing resources for the peer software to use
from ast import mod
from calendar import c
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
dealerScore = 0
p2Score = 0
p3Score = 0
p4Score = 0
round = 1
reset = False
endgame = False

#Function to be ran by peers when they are playing the card game
def play_game():
    global playerSocket
    global cardDeck
    global discardPile
    global dealerHand
    global player2Hand
    global player3Hand
    global player4Hand
    global dealerScore
    global p2Score
    global p3Score
    global p4Score
    global reset
    global endgame
    gameover = False
    #loop of listening and parsing of recieved messeges
    while gameover == False:
        if reset == True:
            reset = False
            dealerHand = []
            player2Hand = []
            player3Hand = []
            player4Hand = []
            discardPile = []
            cardDeck = []
            start_game()
        if endgame == True:
            end_game_protocol()
            gameover = True
            break
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
            print("\n\n\n")
            display_game_state()
        
        #handler for changing wich player is running
        if command[0] == "change_turn":
            player = command[1].split('-')
            if player[2] == playerName:
                play_turn()
        #handler for updating the score amongst users
        if command[0] == "update_score":
            dealerScore = int(command[1])
            p2Score = int(command[2])
            p3Score = int(command[3])
            p4Score = int(command[4])
        #handler to reset the game after the end of a round
        if command[0] == "reset":
            dealerHand = []
            player2Hand = []
            player3Hand = []
            player4Hand = []
            discardPile = []
            cardDeck = []
            start_game()
        #handler for whent the game ends
        if command[0] == "endgame":
            if playersInformation[0].split('-')[2] == playerName:
                time.sleep(2.0)
                messege = "endgame"
                for x in playersInformation:
                    if x.split('-')[2] != playerName:
                        peersocket = socket(AF_INET, SOCK_DGRAM)
                        peersocket.sendto(messege.encode(),(x.split('-')[0], int(x.split('-')[1])))
                        peersocket.close()
                end_game_protocol()
            gameover = True
#function to send the server an end game notification
def end_game_protocol():
    messege = "end," + playerName
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.sendto(messege.encode(),(managerName, managerPort))
    modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
    clientSocket.close()
    if modifiedMessage.decode() == "SUCCESS":
        print("Game ended successfully")
    else:
        print("Error Ending Game")
    
#function to be ran by the dealer to set up the game
def start_game():
    global cardDeck
    global dealerHand
    global discardPile
    global player2Hand
    global player3Hand
    global player4Hand
    global playersInformation
    #base variable initialization
    time.sleep(2)
    messege = "Shuffling cards..."
    print(messege)
    send_mesg(messege)
    
    cardDeck = list(deckTemplate)
    random.shuffle(cardDeck)
    time.sleep(2)

    messege = "Giving players thier cards..."
    print(messege)
    send_mesg(messege)

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
    send_mesg(messege)

    discardPile.append(cardDeck.pop())
    discardPile[-1][:-1]
    time.sleep(2)

    messege = "Game starting"
    print(messege)
    send_mesg(messege)
    #update the game and pass off the turn
    time.sleep(2)
    send_update()

    time.sleep(2)
    messege = "change_turn|" + nextPlayer
    for x in playersInformation:
        if x.split('-')[2] != playerName:
            peersocket = socket(AF_INET, SOCK_DGRAM)
            peersocket.sendto(messege.encode(),(x.split('-')[0], int(x.split('-')[1])))
            peersocket.close()
    #dealer must join the other non playing players in waiting for their turn
    play_game()

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
    #determining what to do for more then 2 players
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
            peersocket = socket(AF_INET, SOCK_DGRAM)
            peersocket.sendto(messege.encode(),(x.split('-')[0], int(x.split('-')[1])))
            peersocket.close()

    print("\n\n\n")
    display_game_state()

#function to be used to send a messege to all players in a game    
def send_mesg(msg):
    messege = "ms|" + msg
    for x in playersInformation:
        if x.split('-')[2] != playerName:
            peersocket = socket(AF_INET, SOCK_DGRAM)
            peersocket.sendto(messege.encode(),(x.split('-')[0], int(x.split('-')[1])))
            peersocket.close()

#print current state of the game
def display_game_state():
    global playersInformation
    print("Deck: " + str(len(cardDeck)) + " cards")
    print("Discard Pile: " + discardPile[-1] + " face up")
    #handler for displaying cards based on if they are face down or not
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
#function that handles the logic for hwo the program will play the game
def play_turn():
    global dealerHand
    global player2Hand
    global player3Hand
    global player4Hand
    time.sleep(2.0)
    print(playerName + "'s Turn:")
    send_mesg(playerName + "'s Turn:")
    hand = []
    #figure out what hand the player uses
    for index, x in enumerate(playersInformation):
        if x.split('-')[2] == playerName:
            if index == 0:
                hand = dealerHand
            elif index == 1:
                hand = player2Hand
            elif index == 2:
                hand = player3Hand
            elif index == 3:
                hand = player4Hand

    #determine if the plaeyr needs to flip their first two cards
    alldown = True
    for x in hand:
        if "*" not in x:
            alldown = False
    if alldown == True:
        time.sleep(2.0)
        send_mesg("Flipping two cards")
        print("Flipping two cards")
        x = random.randint(0,2) 
        hand[x] = hand[x][:-1]
        x = random.randint(3,5) 
        hand[x] = hand[x][:-1]
        time.sleep(2.0)
        send_update()
    chosencard = ""
    chosenindex = 0
    viewedcard= ""
    viewindex = 0
    #picking highest value card
    for index, x in enumerate(hand):
        if "*" not in x:
            if chosencard == "":
                chosencard = x
                chosenindex = index
            else:
                viewedcard = x
                if compare_cards(chosencard, viewedcard) == 1:
                    chosencard = viewedcard
                    chosenindex = index
    #steal extension
    chance = random.randint(1, 10)
    steal = False
    if chance >= 8:
        victim = playersInformation.index(nextPlayer)
        if victim == 0:
            for index, x in enumerate(dealerHand):
                if "*" not in x and compare_cards(chosencard, x) == 0:
                    steal = True
                    temp = chosencard
                    hand[chosenindex] = x
                    dealerHand[index] = temp
                    break
        elif victim == 1:
            for index, x in enumerate(player2Hand):
                if "*" not in x and compare_cards(chosencard, x) == 0:
                    steal = True
                    temp = chosencard
                    hand[chosenindex] = x
                    player2Hand[index] = temp
                    break
        elif victim == 3:
            for index, x in enumerate(player3Hand):
                if "*" not in x and compare_cards(chosencard, x) == 0:
                    steal = True
                    temp = chosencard
                    hand[chosenindex] = x
                    player3Hand[index] = temp
                    break
        else:
            for index, x in enumerate(player4Hand):
                if "*" not in x and compare_cards(chosencard, x) == 0:
                    steal = True
                    temp = chosencard
                    hand[chosenindex] = x
                    player4Hand[index] = temp
                    break
    if steal == True:
        time.sleep(2.0)
        send_mesg("Stole card from " + nextPlayer.split('-')[2])
        print("Stole card from " + nextPlayer.split('-')[2])
    #logic for playing game, comparing cards, and which to swap
    if compare_cards(chosencard, discardPile[-1]) == 0 and steal == False:
        time.sleep(2.0)
        send_mesg("Switching card with discard pile")
        print("Switching card with discard pile")
        x = discardPile[-1]
        discardPile[-1] = chosencard
        hand[chosenindex] = x
    elif compare_cards(chosencard, discardPile[-1]) != 0 and steal == False:
        facedwn = False
        for index, x in enumerate(hand):
            if "*" in x:
                chosenindex = index
                facedwn = True
                break
        if facedwn == True and len(cardDeck) != 0:
            time.sleep(2.0)
            send_mesg("Switching face down card with drawn card from deck")
            print("Switching face down card with drawn card from deck")
            hand[chosenindex] = hand[chosenindex][:-1]
            discardPile.append(hand[chosenindex])
            hand[chosenindex] = cardDeck.pop()
            hand[chosenindex] = hand[chosenindex]
        elif facedwn == True and len(cardDeck) == 0:
            time.sleep(2.0)
            send_mesg("Switching face down card with card from discard pile")
            print("Switching face down card with card from discard pile")
            hand[chosenindex] = hand[chosenindex][:-1]
            x = hand[chosenindex]
            hand[chosenindex] = discardPile[-1]
            discardPile[-1] = x
        elif facedwn == False and len(cardDeck) != 0:
            time.sleep(2.0)
            send_mesg("Switching highest card with drawn card from deck")
            print("Switching highest card with drawn card from deck")
            discardPile.append(hand[chosenindex])
            hand[chosenindex] = cardDeck.pop()
        elif facedwn == False and len(cardDeck) == 0:
            time.sleep(2.0)
            send_mesg("Switching highest card with card from discard pile")
            print("Switching highest card with card from discard pile")
            x = hand[chosenindex]
            hand[chosenindex] = discardPile[-1]
            discardPile[-1] = x
    time.sleep(2.0)
    send_update()
    #checking for if the round should end
    endround = True
    for x in dealerHand:
        if "*" in x:
            endround = False
            break
    if endround == True:
        for x in player2Hand:
            if "*" in x:
                endround = False
                break
    if endround == True:
        for x in player3Hand:
            if "*" in x:
                endround = False
                break
    if endround == True:
        for x in player4Hand:
            if "*" in x:
                endround = False
                break
    
    if endround == True:
        time.sleep(2.0)
        end_game_round()
    else:
        time.sleep(2.0)
        messege = "change_turn|" + nextPlayer
        for x in playersInformation:
            if x.split('-')[2] != playerName:
                peersocket = socket(AF_INET, SOCK_DGRAM)
                peersocket.sendto(messege.encode(),(x.split('-')[0], int(x.split('-')[1])))
                peersocket.close()

#function for handeling the end of a round
def end_game_round():
    global dealerScore
    global p2Score
    global p3Score
    global p4Score
    global dealerHand
    global player2Hand
    global player3Hand
    global player4Hand
    global round
    global discardPile
    global cardDeck
    result = ""
    global reset
    global endgame
    #calculating dealer score
    if get_card_score(dealerHand[0]) == get_card_score(dealerHand[3]):
        dealerScore += 0
    else:
        dealerScore += get_card_score(dealerHand[0]) + get_card_score(dealerHand[3])
    if get_card_score(dealerHand[1]) == get_card_score(dealerHand[4]):
        dealerScore += 0
    else:
        dealerScore += get_card_score(dealerHand[1]) + get_card_score(dealerHand[4])
    if get_card_score(dealerHand[2]) == get_card_score(dealerHand[5]):
        dealerScore += 0
    else:
        dealerScore += get_card_score(dealerHand[2]) + get_card_score(dealerHand[5])

    result = playersInformation[0].split('-')[2] + "'s Score: " + str(dealerScore) + "   "

    #calculate p2Score
    if get_card_score(player2Hand[0]) == get_card_score(player2Hand[3]):
        p2Score += 0
    else:
        p2Score += get_card_score(player2Hand[0]) + get_card_score(player2Hand[3])
    if get_card_score(player2Hand[1]) == get_card_score(player2Hand[4]):
        p2Score += 0
    else:
        p2Score += get_card_score(player2Hand[1]) + get_card_score(player2Hand[4])
    if get_card_score(player2Hand[2]) == get_card_score(player2Hand[5]):
        p2Score += 0
    else:
        p2Score += get_card_score(player2Hand[2]) + get_card_score(player2Hand[5])
    
    result += playersInformation[1].split('-')[2] + "'s Score: " + str(p2Score) + "   "

    #calculate p3Score
    if len(playersInformation) > 2:
        if get_card_score(player3Hand[0]) == get_card_score(player3Hand[3]):
            p3Score += 0
        else:
            p3Score += get_card_score(player3Hand[0]) + get_card_score(player3Hand[3])
        if get_card_score(player3Hand[1]) == get_card_score(player3Hand[4]):
            p3Score += 0
        else:
            p3Score += get_card_score(player3Hand[1]) + get_card_score(player3Hand[4])
        if get_card_score(player3Hand[2]) == get_card_score(player3Hand[5]):
            p3Score += 0
        else:
            p3Score += get_card_score(player3Hand[2]) + get_card_score(player3Hand[5])
        
        result += playersInformation[2].split('-')[2] + "'s Score: " + str(p3Score) + "   "

    #calculate p4Score
    if len(playersInformation) > 3:
        if get_card_score(player4Hand[0]) == get_card_score(player4Hand[3]):
            p4Score += 0
        else:
            p4Score += get_card_score(player4Hand[0]) + get_card_score(player4Hand[3])
        if get_card_score(player4Hand[1]) == get_card_score(player4Hand[4]):
            p4Score += 0
        else:
            p4Score += get_card_score(player4Hand[1]) + get_card_score(player4Hand[4])
        if get_card_score(player4Hand[2]) == get_card_score(player4Hand[5]):
            p4Score += 0
        else:
            p4Score += get_card_score(player4Hand[2]) + get_card_score(player4Hand[5])

        result += playersInformation[3].split('-')[2] + "'s Score: " + str(p4Score) + "   "

    time.sleep(2.0)
    print("Round over. Results: " + result)
    send_mesg("Round over. Results: " + result)

    time.sleep(2.0)
    update_score()
    #checking if the game should end
    if round != 9:
        round += 1
        time.sleep(2.0)
        print("Starting New Round")
        send_mesg("Starting New Round")
        if playersInformation[0].split('-')[2] == playerName:
            reset = True
        else:
            time.sleep(2.0)
            messege = "reset"
            peersocket = socket(AF_INET, SOCK_DGRAM)
            peersocket.sendto(messege.encode(),(playersInformation[0].split('-')[0], int(playersInformation[0].split('-')[1])))
            peersocket.close()
    else:
        time.sleep(2.0)
        print("GAME OVER" )
        send_mesg("GAME OVER")
        if playersInformation[0].split('-')[2] == playerName:
            endgame = True
            time.sleep(2.0)
            messege = "endgame"
            for x in playersInformation:
                if x.split('-')[2] != playerName:
                    peersocket = socket(AF_INET, SOCK_DGRAM)
                    peersocket.sendto(messege.encode(),(x.split('-')[0], int(x.split('-')[1])))
                    peersocket.close()
                    endgame = True
        else:
            time.sleep(2.0)
            messege = "endgame"
            peersocket = socket(AF_INET, SOCK_DGRAM)
            peersocket.sendto(messege.encode(),(playersInformation[0].split('-')[0], int(playersInformation[0].split('-')[1])))
            peersocket.close()
            

#funciton to update score
def update_score():
    messege = "update_score|" + str(dealerScore) + "|" + str(p2Score) + "|" + str(p3Score) + "|" + str(p4Score)
    for x in playersInformation:
        if x.split('-')[2] != playerName:
            peersocket = socket(AF_INET, SOCK_DGRAM)
            peersocket.sendto(messege.encode(),(x.split('-')[0], int(x.split('-')[1])))
            peersocket.close()

#function to return card value
def get_card_score(card):
    c = 0
    if "2" in card:
        c = -2
    elif "3" in card:
        c = 3
    elif "4" in card:
        c = 4
    elif "5" in card:
        c = 5
    elif "6" in card:
        c = 6
    elif "7" in card:
        c = 7
    elif "8" in card:
        c = 8
    elif "9" in card:
        c = 9
    elif "10" in card:
        c = 10
    elif "J" in card:
        c = 10
    elif "Q" in card:
        c = 10
    elif "K" in card:
        c = 0
    elif "A" in card:
        c = 1
    return c

#function tool to determine wich card has a higher value
def compare_cards(cc, vc):
    c = 0
    v = 0
    if "2" in cc:
        c = -2
    elif "3" in cc:
        c = 3
    elif "4" in cc:
        c = 4
    elif "5" in cc:
        c = 5
    elif "6" in cc:
        c = 6
    elif "7" in cc:
        c = 7
    elif "8" in cc:
        c = 8
    elif "9" in cc:
        c = 9
    elif "10" in cc:
        c = 10
    elif "J" in cc:
        c = 10
    elif "Q" in cc:
        c = 10
    elif "K" in cc:
        c = 0
    elif "A" in cc:
        c = 1
    
    if "2" in vc:
        v = 2
    elif "3" in vc:
        v = 3
    elif "4" in vc:
        v = 4
    elif "5" in vc:
        v = 5
    elif "6" in vc:
        v = 6
    elif "7" in vc:
        v = 7
    elif "8" in vc:
        v = 8
    elif "9" in vc:
        v = 9
    elif "10" in vc:
        v = 10
    elif "J" in vc:
        v = 10
    elif "Q" in vc:
        v = 10
    elif "K" in vc:
        v = 0
    elif "A" in vc:
        v = 1
    
    if c > v:
        return 0
    else:
        return 1

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

