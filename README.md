# SocketProject
 Repository for my CSE434 socket project. This project is to experiment with peer-to-server communicaiton and peer-to-peer communication.
 This file contains two python scripts, manager.py and peer.py. Running manager.py will create an instace that will act as a server. Runnnig peer.py will open up a menu of options that the user can select.
 From registering as a player, to quering games and other players, initially all network communicaiton will be held between the peers and the manager as the manager will store all relevant information about registered users and occuring games.
 Once a peer requests to join or start a game, requests are made to the server for aditional polayer information so that a new game can be created, at wich point the peers will recieve the information and start a game of card golf. At this point all communicaiton will be held peer-to-peer with the manager only associated by keeping note of the game's existance and the players in it.
