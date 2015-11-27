import riskengine
import riskgui
import random
from aihelper import *
from turbohelper import *
from risktools import *

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    
    #Get the possible actions in this state
    actions = getAllowedActions(state)
        
    #Select a Random Action
    myaction = random.choice(actions)

    print "state: ",state.turn_type
    
    if state.turn_type == 'Attack':
        myaction = actions[0]

    """ Picks the first 35 territories """
    if state.turn_type == 'PreAssign':
        assignment = preAssign(state)
        print "Armies: ", state.players[state.current_player].free_armies
        return assignment

    """ Place additional 15 armies anywhere on the map """
    if state.turn_type == 'PrePlace':
        placement = prePlace(state)
        print "Armies: ", state.players[state.current_player].free_armies
        return placement
    
    if  state.turn_type == 'Fortify':
        possible_actions = []

        for a in actions:
            if a.to_territory is not None:
                for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                    if state.owners[n] != state.current_player:
                        possible_actions.append(a)
                    
        if len(possible_actions) > 0:
            print possible_actions
            #myaction = random.choice(possible_actions)

    return myaction

def preAssign(state):

    best_action = None
    best_action_value = None
    actions = getPreAssignActions(state)

    if state.players[state.current_player].free_armies >= 30:
        for a in actions:
        
            if str(a.to_territory) == "Laos":
                action_value = 7

            elif str(a.to_territory) == "Brazil":
                action_value = 6

            elif str(a.to_territory) == "Chile":
                action_value = 5
         
            elif str(a.to_territory) == "Iceland":
                action_value = 4
          
            elif str(a.to_territory)== "Alaska":
                action_value = 3
           
            elif str(a.to_territory) == "Eastern Australia":
                action_value = 2
         
            elif str(a.to_territory) == "Greenland":
                action_value = 1

            else:
                action_value = 0

            monopoly_action = checkMonopoly(state, a.to_territory)
            if monopoly_action > 0:
                action_value = monopoly_action
            
            if best_action_value is None or action_value > best_action_value:
                best_action = a
                best_action_value = action_value
                print "Update Action: ", best_action_value         
        print "Best Action: ", best_action.to_territory

    elif state.players[state.current_player].free_armies > 22:
        for a in actions:
            
            if str(a.to_territory)== "Alaska":
                action_value = 10
         
            elif str(a.to_territory) == "Eastern Australia":
                action_value = 9
           
            elif str(a.to_territory) == "Mexico":
                action_value = 8
        
            elif str(a.to_territory) == "Western Africa":
                action_value = 7
             
            elif str(a.to_territory) == "Western Austrialia":
                action_value = 6
             
            elif str(a.to_territory) == "Columbia":
                action_value = 5
              
            elif str(a.to_territory) == "Madagascar":
                action_value = 4
               
            elif str(a.to_territory) == "Indonesia":
                action_value = 3
          
            elif str(a.to_territory) == "South Africa":
                action_value = 2
            
            elif str(a.to_territory) == "Kamchatka":
                action_value = 1
                   
            else:
                action_value = 0

            monopoly_action = checkMonopoly(state, a.to_territory)
            if monopoly_action > 0:
                action_value = monopoly_action
          
            if best_action_value is None or action_value > best_action_value:
                best_action = a
                best_action_value = action_value
                print "Update Action: ", best_action_value
                
        print "Best Action: ", best_action.to_territory
    else:
        bestPer = 0.0
        for a in actions:
            terrPer = checkPercentage(state, a.to_territory)
            monopoly_action = checkMonopoly(state, a.to_territory)
            if monopoly_action > 0:
                terrPer = monopoly_action

            if bestPer == 0.0 or terrPer > bestPer:
                best_action = a
                bestPer= terrPer  

        print "Best Action: ", best_action.to_territory
        print "Best Action Value: ", bestPer

    return best_action

def prePlace(state):

    bestPlace = None
    best_place_value = None
    actions = getPrePlaceActions(state)

    if state.players[state.current_player].free_armies > 0:
        for a in actions:
            neighNum = neighborAppeal(state, a.to_territory)

            if bestPlace == None or neighNum > best_place_value:
                bestPlace = a
                best_place_value = neighNum

    return bestPlace  

def isOurTerritory(state, territory):
    ourID = state.current_player

    if state.owners[territory.id] == ourID:
        return True
    return False

def isTheirTerritory(state, territory):
    ourID = state.current_player

    if state.owners[territory.id] != ourID and state.owners[territory.id] != None:
        return True
    return False

def neighborAppeal(state, territory):

    tAppeal = 0
    iTerr = 0
    tTerr = 0
    uTerr = 0
    troops = 0
    terrProp = None

    for c in state.board.continents:
        for t in state.board.continents[c].territories:
            if territory == state.board.territories[t].name:
                terrProp = t
    
    for neighbor in state.board.territories[terrProp].neighbors:
        if isOurTerritory(state, state.board.territories[neighbor]):
             iTerr +=1
        elif isTheirTerritory(state, state.board.territories[neighbor]):
            tTerr += 1
            troops += enemyTroops(state, neighbor)
        else:
            uTerr += 1

    totalNeighbor = iTerr + tTerr + uTerr
    if iTerr == totalNeighbor:
        return 0
    elif (totalNeighbor - iTerr) <= 2:
        tAppeal = 10
    elif (totalNeighbor - iTerr) <= 1:
        tAppeal = 20
    else:
        tAppeal = 5

    percentIncrease = checkPercentage(state, territory)
    tAppeal = ((tAppeal * percentIncrease) + troops) / state.armies[terrProp]
    print "tAppeal: ", tAppeal
   

    return tAppeal


def enemyTroops(state, territory):
    troops = state.armies[territory]
    print "Enemy Troops: ",troops
    if troops > 1:
        appeal = troops * 10
    else:
        appeal = 0

    return appeal


def checkPercentage(state, territory):
    iOwn = 0
    tOwn = 0
    uOwn = 0
    total = 0
    iPer = 0.0
    tPer = 0.0
    uPer = 0.0
    totalPer = 0.0

    for c in state.board.continents:
        for t in state.board.continents[c].territories:
            if territory == state.board.territories[t].name:
                continent = c
 
    for t in state.board.continents[continent].territories:
        print "Territory: ", state.board.territories[t].name
        if isOurTerritory(state, state.board.territories[t]):
            iOwn += 1
        elif isTheirTerritory(state, state.board.territories[t]):
            tOwn += 1 
        else:
            uOwn += 1

    num = iOwn + tOwn + uOwn
    if iOwn == num:
        return 0
    subtotal = iOwn + (num - tOwn) + (num - uOwn)  
    total = subtotal * 10
    totalPer = total / num
    return totalPer


def checkMonopoly(state, territory): 

    Owned = 0
    Appeal = 0
    notOwned = 0
    theyOwn = 0
    continent = None

    for c in state.board.continents:
        
        for t in state.board.continents[c].territories:
            if territory == state.board.territories[t].name:
                continent = c
    
    for t in state.board.continents[continent].territories:
        if isOurTerritory(state,state.board.territories[t]):
            Owned += 1
         
        elif isTheirTerritory(state, state.board.territories[t]):
            theyOwn += 1
       
        else:
            notOwned += 1
        
    if len(state.board.continents[continent].territories) == (Owned + 1) or len(state.board.continents[continent].territories) == (theyOwn + 1) or len(state.board.continents[continent].territories) == (theyOwn + Owned + 1):
        Appeal += 20     

    return Appeal


#Stuff below this is just to interface with Risk.pyw GUI version
#DO NOT MODIFY

# Determine how to call all enemy territories


            

    
def aiWrapper(function_name, occupying=None):
    game_board = createRiskBoard()
    game_state = createRiskState(game_board, function_name, occupying)
    action = getAction(game_state)
    return translateAction(game_state, action)
            
def Assignment(player):
#Need to Return the name of the chosen territory
    return aiWrapper('Assignment')
     
def Placement(player):
#Need to return the name of the chosen territory
     return aiWrapper('Placement')

    
def Attack(player):
 #Need to return the name of the attacking territory, then the name of the defender territory    
    return aiWrapper('Attack')

   
def Occupation(player,t1,t2):
 #Need to return the number of armies moving into new territory      
    occupying = [t1.name,t2.name]
    aiWrapper('Occupation',occupying)
   
def Fortification(player):
    return aiWrapper('Fortification')

