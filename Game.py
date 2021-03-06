#!/usr/bin/python

#######################################################
# To understand the design, it is recommended to read #
# the class design documentation on the wiki first!   #
#######################################################

#This file is the main module for the game logic

#a rough class outline for a roguelike to be built with
#libtcod or another graphical front-end.
#Focus for the class design is on game logic at the moment.
#Ideally we can couple the graphics/user interface as loosely as possible.
#
#I have tried to focus on the main aspects but the model should be able
#to evolve over time. The idea is that it can be extended by inheritance,
#adding more specialised classes where needed.
#
#This file is written in python syntax and should compile, however there is no
#sense in running it by itself. Also when we go for implementation I would
#propose to split up the file in multiple modules.
#
#For illustration purposes (and to experiment I admit :-p) I have already
#added some class variables and functions. These are by no means permanent,
#consider it as examples ;-)
#
#All comments welcome!
#
# -Frost

#Chain load proprietary modules
import CONSTANTS
import Utilities
from Maps import *
from Levels import *
from Actors import *
from Libraries import *
from AI import *
from Effects import *

#Load system modules
import random

############# Classes related to User interface #################


class Application(object):
    """
    This class represents a running instance of the application.
    It connects the game logic to the user interface. It should be inherited
    by actual implementations of a graphical interface.
    """

#Frostlock:
#If we implement our own graphical interface we will probably need to add
#a class structure for it as well.
#Also to facilitate the use of an external library (like libtcod or
#pygame) we might need to add classes here.
#I haven't done this yet. I'm currently experimenting with libtcod to
#see what would be needed.
#In my case I have a "ApplicationLibtcod" class inheriting from this one.


############# Classes related to Game logic #################
class Game():
    """
    The game class contains the logic to run the game.
    It knows about turns
    It has pointers to all the other stuff, via the Game object you can drill
    down to all components
    It can save and load
    It keeps track of the levels and knows which is the current level
    At the moment I don't see the need for sub classes
    """

    #Class variables
    _application = None

    @property
    def application():
        """
        The Application object that owns this game Object
        """
        return self._application

    PLAYING = 0
    FINISHED = 1
    _state = PLAYING

    @property
    def state(self):
        """
        Returns the game state
        """
        return self._state

    _player = None

    @property
    def player(self):
        """
        The player of the game
        """
        return self._player

    #Simple array to store Level objects
    _levels = []

    @property
    def levels(self):
        """
        Returns the list of levels in this game.
        """
        return self._levels

    _currentLevel = None

    @property
    def currentLevel(self):
        """
        Returns the current level
        """
        return self._currentLevel

    @currentLevel.setter
    def currentLevel(self, level):
        """
        Sets the current level
        """
        self._currentLevel = level

    _monsterLibrary = None

    @property
    def monsterLibrary(self):
        """
        Returns the monster library used by this game.
        """
        return self._monsterLibrary

    _itemLibrary = None

    @property
    def itemLibrary(self):
        """
        Returns the item library used by this game.
        """
        return self._itemLibrary

    #constructor
    def __init__(self, owner):
        """
        Constructor to create a new game.
        Arguments
            owner - Application object that owns this game
        """
        #Initialize class variables
        self._application = owner
        self._player = None
        #reset Game
        self.resetGame()

    #functions
    def resetGame(self):
        #initialize libraries
        self._monsterLibrary = MonsterLibrary()
        self._itemLibrary = ItemLibrary()

        #clear existing levels
        self._levels = []
        #generate new levels
        prevLevel = None
        #generate a town level
        town = TownLevel(self, 1, 'Town')
        self._levels.append(town)
        self._currentLevel = town
        for i in range(1, 8):
            prevLevel = self.levels[i - 1]
            curLevel = DungeonLevel(self, i , 'Dungeon level ' + str(i))
            self._levels.append(curLevel)
            if prevLevel is not None:
                #add portal in previous level to current level
                downPortal = Portal()
                downPortal._char = '>'
                downPortal._name = 'stairs leading down into darkness'
                downPortal._message = 'You follow the stairs down, looking for more adventure.'
                downPortal.moveToLevel(prevLevel, prevLevel.getRandomEmptyTile())
                #add portal in current level to previous level
                upPortal = Portal()
                upPortal._char = '<'
                upPortal._name = 'stairs leading up'
                upPortal._message = 'You follow the stairs up, hoping to find the exit.'
                upPortal.moveToLevel(curLevel, curLevel.getRandomEmptyTile())
                #connect the two portals
                downPortal.connectTo(upPortal)

        #Create player object
        self._player = Player()
        firstLevel = self.levels[0]
        #uncomment to start in dungeon
        #firstLevel = self.levels[1]
        #self._currentLevel = firstLevel
        
        self.player.moveToLevel(firstLevel, firstLevel.getRandomEmptyTile())
        firstLevel.map.updateFieldOfView(
                self._player.tile.x, self._player.tile.y)
        #Provide some starting gear
        #potion = self.itemLibrary.createItem("minor_heal");
        #self.player.addItem(potion)
        potion = self.itemLibrary.createItem("regular_heal");
        self.player.addItem(potion)
        #potion = self.itemLibrary.createItem("major_heal");
        #self.player.addItem(potion)
        cloak = self.itemLibrary.createItem("cloak");
        self.player.addItem(cloak)
        scroll = self.itemLibrary.createItem("firenova");
        self.player.addItem(scroll)

        #Set the game state
        self._state = Game.PLAYING

        #Send welcome message to the player
        Utilities.message('You are ' + self.player.name +
                ', a young and fearless adventurer. It is time to begin your '
                + 'legendary and without doubt heroic expedition into the '
                + 'unknown. Good luck!', "GAME")

        return

    #TODO medium: implement saving and loading of gamestate
    def loadGame(self, fileName):
        return

    def saveGame(self, fileName):
        return

    def playTurn(self):
        """
        This function will handle one complete turn.
        """
        for c in self.currentLevel.characters:
            if c.state == Character.ACTIVE:
                c.takeTurn()

if __name__ == '__main__':
    print("There is not much sense in running this file.")
    print("Try running ApplicationLibtcod.")
