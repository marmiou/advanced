#!/usr/bin/python

# This file contains a test implementation of the application class.
# This one is based on Pygcurse.

import pygcurse
import pygame

# You can import everything you need from module Game
# the Game module will chain load other modules
from Game import Game
from Game import Player
import Actors
import Maps
import CONSTANTS
import Utilities
import textwrap

#actual size of the window
SCREEN_WIDTH = 85
SCREEN_HEIGHT = 50

# the number of times to redraw the screen each second
LIMIT_FPS = 20
PANEL_HEIGHT = 7
BAR_WIDTH = 20
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

# draw the dungeon with these colors.
# dark tiles are out of the player's view.
# light tiles are illuminated by our torch.
COLOR_DARK_WALL = 'gray'
COLOR_DARK_GROUND = 'silver'
COLOR_LIGHT_WALL = 'navy'
COLOR_LIGHT_GROUND = 'teal'


class ApplicationPygcurse():
    """
    This class represents a running instance of the application.
    It connects the game logic to the user interface.
    It is a test implementation of a GUI based on Pygcurse.
    """

    #TODO easy: this class needs better documentation comments

    _game = None

    @property
    def game(self):
        """
        The game object used by this application
        """
        return self._game

    _mapConsole = None

    @property
    def mapConsole(self):
        """
        libtcod console (off screen) used to draw the main map
        """
        return self._mapConsole

    _panelConsole = None

    @property
    def panelConsole(self):
        """
        libtcod console (off screen) used to draw the panel
        """
        return self._panelConsole

    _messages = None

    @property
    def messages(self):
        """
        returns the most recent game messages
        """
        return self._messages

    def addMessage(self, new_msg):
        #split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
        for line in new_msg_lines:
            #only keep the last messages
            if len(self.messages) == MSG_HEIGHT:
                del self.messages[0]
            #add the new line
            self.messages.append(line)  # (line, color) )

    def __init__(self):
        """
        Constructor that creates a new instance of the application
        """

        #Initialize pygcurse
        self.win = pygcurse.PygcurseWindow(
            SCREEN_WIDTH, SCREEN_HEIGHT, fullscreen=False)
        pygame.display.set_caption('Crunchbang Project')

        # we will call win.update() manually after everything is drawn
        self.win.autoupdate = False

        #Prepare to receive messages from the game utilities
        #(this allows the utilities to send game messages to this application)
        self._messages = []
        Utilities.application = self

        #Create a new game object for this application
        #self._game = Game(self)

    def showMenu(self, header, options, width=20, height=10):
        """
        This function will show a menu. The application waits for user input
        before returning the selected option.
        The function will return None if the user escapes the menu.
        Arguments
            header - String, text for the header
            options - String list, text for the options
            width - Width (in characters) of the menu box
        """
        if len(options) > 26:
            raise ValueError('Cannot have a menu with more than 26 options.')

        # Show in the middle of the screen.
        menu_region = (
            self.win.centerx / 2,
            self.win.centery / 2 + (height / 2),
            width,
            height)
        
        # a list from a-n, where n is the length of our options
        hotkeys = [chr(ord('a') + i) for i in range(0, len(options))]

        # build a menu from the options list by prefixing each with a hotkey
        # then join them together with newlines.
        menu_choices = []
        for counter, option_text in enumerate(options):
            menu_choices.append('(%s) %s' % ((hotkeys[counter]), option_text))
        menu_choices = '\n'.join(menu_choices)
        
        # construct the menu as a textbox object. It recognizes newlines.
        # this guy draw a nice border for us too.
        txt = pygcurse.PygcurseTextbox(
            self.win,
            region=menu_region,
            fgcolor='white',
            bgcolor=pygcurse.ERASECOLOR,
            caption=header,
            text=menu_choices,
            margin=2,
            wrap=True,
            border='.')
        txt.update()

        # update the screen and handle keypresses
        self.win.update()
        menu_busy = True
        while menu_busy:
            key = pygcurse.waitforkeypress(LIMIT_FPS)
            if key is None:
                return None
            if key in hotkeys:
                return hotkeys.index(key)

    def showMessage(self, header, message, width=20, height=10):
        """
        This function will show a pop up message in the middle of the screen.
        It waits for the user to acknowledge the message by hitting enter or
        escape
        """
        
        # Show in the middle of the screen.
        menu_region = (
            self.win.centerx / 2,
            self.win.centery / 2 + (height / 2),
            width,
            height)

        textbox = pygcurse.PygcurseTextbox(
            self.win,
            region=menu_region,
            fgcolor='white',
            bgcolor='black',
            caption=header,
            text=message,
            margin=2,
            wrap=True,
            border='.')

        # tell the textbox to draw itself onto our win canvas
        textbox.update()

        # update the screen and handle keypresses
        self.win.update()
        menu_busy = True
        while menu_busy:
            key = pygcurse.waitforkeypress(LIMIT_FPS)
            if key is None:
                return 'Escape'
            elif key == '\r':
                return 'Enter'

    def showWelcomeScreen(self):
        
        self.win.backgroundimage = pygame.image.load(
            './media/menu_background.png')
        menu_choices = ['Start a new game',
                        'Continue previous game',
                        'Go to debug mode',
                        'Quit'
                        ]
        show_menu = True
        while show_menu:
            choice = self.showMenu('Main menu', menu_choices, 36)
            #interpret choice
            if choice is None:
                show_menu = False
            if choice == 0:
                print "Start a new game"
                self.newGame()
                self.showGameScreen()
            elif choice == 1:
                print "Continue previous game"
                self.showMessage('Oops...',
                        'I don\'t know how to load a game yet :-)', 36)
            elif choice == 2:  # quit
                print "Go to debug mode"
                self.showDebugScreen()
            elif choice == 3:
                print "Quiting"
                show_menu = False
        self.win.backgroundimage = None

    def showDebugScreen(self):
        #store the current view
        behind_window = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
        libtcod.console_blit(0, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, behind_window, 0, 0, 1.0, 1.0)

        #show the background image, at twice the regular console resolution
        img = libtcod.image_load('./media/menu_debug.png')
        libtcod.image_blit_2x(img, 0, 0, 0)

        while not libtcod.console_is_window_closed():
            #show options and wait for the player's choice
            choice = self.showMenu('Select debug option:',
                        ['Run some test code!',      # Choice 0
                        'Show me some game stuff!',  # Choice 1
                        'Back'],                     # Choice 2
                        36)
            #interpret choice
            if choice is None:
                continue
            if choice == 0:
                print "Running some test code!"
                self.runTestCode()
                self.showMessage('Test code complete!',
                        'There might be some output in the console...', 36)
                continue
            elif choice == 1:
                print "Showing some game stuff!"
                self.newGame()
                self.showGameScreen()
            elif choice == 2:  # quit
                print "Back"
                break
        #Clean up (restore whatever was behind this window)
        libtcod.console_blit(behind_window, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0, 1.0, 1.0)
        libtcod.console_flush()

    def showGameScreen(self):

        while not libtcod.console_is_window_closed():
            self.renderAll()

            #handle keys and exit game if needed
            #this allows the player to play his turn
            if self.handleKeys() == 'exit':
                break

            #Let the game play a turn
            self.game.playTurn()

    ##########################################################################
    # DebugScreen functions
    ##########################################################################
    def runTestCode(self):
        """
        This function ties into the debug menu. It is meant to allow execution
        of some test code. Feel free to change the contents of this function.
        """
        #lib = MonsterLibrary()
        #myRandom = lib.getRandomMonster(2)
        #myRat = lib.createMonster('rat')
        #print myRat
        #print myRandom
        #myRat.attack(myRandom)
        #myRat.attack(myRandom)
        #myRat.attack(myRandom)

        myMap = Maps.TownMap(CONSTANTS.MAP_WIDTH, CONSTANTS.MAP_HEIGHT)
        print myMap

    ##########################################################################
    # GameScreen functions
    ##########################################################################
    def newGame(self):
        self._messages = []
        self._game = Game(self)

    def loadGame(self, fileName):
        self.game.loadGame(fileName)

    def saveGame(self, fileName):
        self.game.saveGame(fileName)

    def renderAll(self):
        """
        This function renders the main screen
        """

        con = self.mapConsole
        libtcod.console_clear(con)
        level = self.game.currentLevel

        # draw the map tiles
        for tile in level.map.explored_tiles:
            if tile.blocked:
                # these are wall tiles
                if tile.inView:
                    # the player can see these
                    bg_color = COLOR_LIGHT_WALL
                else:
                    # these are out of sight
                    bg_color = COLOR_DARK_WALL
            else:
                # and these are floor tiles...
                if tile.inView:
                    bg_color = COLOR_LIGHT_GROUND
                else:
                    bg_color = COLOR_DARK_GROUND
            libtcod.console_set_char_background(
                con, tile.x, tile.y, bg_color, libtcod.BKGND_SET)

            # draw any actors standing on this tile.
            # includes Monsters and Portals
            for myActor in tile.actors:
                if myActor.visible:
                    actor_color = libtcod.white
                    # NOTE if the Actor base stores it's own color there is no
                    # need for type checking.
                    if type(myActor) is Actors.Portal:
                        actor_color = libtcod.purple
                    elif type(myActor) is Actors.Monster:
                        actor_color = libtcod.green
                    libtcod.console_set_default_foreground(con, actor_color)
                    libtcod.console_put_char(
                        con, tile.x, tile.y, myActor.char, libtcod.BKGND_NONE)

            #Redraw player character (makes sure it is on top)
            player = self.game.player
            libtcod.console_set_default_foreground(con, libtcod.white)
            libtcod.console_put_char(
                con, player.tile.x, player.tile.y,
                player.char, libtcod.BKGND_NONE)

        #blit the contents of "con" to the root console
        libtcod.console_blit(con, 0, 0, CONSTANTS.MAP_WIDTH, CONSTANTS.MAP_HEIGHT, 0, 0, 0)

        ##Notes on field of view
        ##
        ##Joe: Explain, the Fov is treated as a secondary map
        ##The question is do we wish to deal with it the same way?
        ##Ideally, if rooms are set before map is drawn, you save the
        ##generation of colors until inside FOV range, where you change
        ##the colors of them to match your final scheme, and then turn
        ##them back to the "shadowed" colors once player has set an
        ##"explored" option.
        ##NOTE Wesley:
        ##   I did this before in another project as handled by the Game.
        ##   After each move the Game does a look_around() and marks a monster
        ##   or tile as seen == True and in_range == True (if in fov).
        ##   Then we just draw tiles where seen, and monsters where in_range.
        ##   I will try add this tonight, it is pure python and simple and good
        ##   for learning how these things work :)

        #TODO medium: create a GUI panel
        #Frostlock: this needs some game message log first in the game logic
        panel = self.panelConsole
        libtcod.console_set_default_background(panel, libtcod.black)
        libtcod.console_clear(panel)

        ##print the game messages, one line at a time
        if self.messages is not None:
            y = 1
            for line in self.messages:
                libtcod.console_set_default_foreground(panel, libtcod.white)
                libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE,
                        libtcod.LEFT, line)
                y += 1

        if player is not None:
            #Player health bar
            self.renderBar(panel, 1, 1, BAR_WIDTH, 'HP',
                    player.currentHitPoints, player.maxHitPoints,
                    libtcod.dark_red, libtcod.darker_gray)
            #Player xp bar
            self.renderBar(panel, 1, 2, BAR_WIDTH, 'XP',
                    player.xp, player.nextLevelXp,
                    libtcod.darker_green, libtcod.darker_gray)
        if self.game.currentLevel is not None:
            #Dungeon level
            libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE,
                    libtcod.LEFT, str(self.game.currentLevel.name))

        #TODO: display names of objects under the mouse
        # Frost: this would require running this loop constantly which is not
        # happening at the moment. Currently it pauses to wait for the player to
        # hit a key.
        #libtcod.console_set_default_foreground(panel, libtcod.light_gray)
        #libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE,
        #        libtcod.LEFT, get_names_under_mouse())

        #blit the contents of "panel" to the root console
        libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH,
                PANEL_HEIGHT, 0, 0, PANEL_Y)

    def renderBar(self, panel, x, y, total_width,
            name, value, maximum, bar_color, back_color):
        """
        Helper function to render interface bars
        """
        #render a bar (HP, experience, etc). first calculate the width of the bar
        bar_width = int(float(value) / maximum * total_width)

        #render the background first
        libtcod.console_set_default_background(panel, back_color)
        libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

        #now render the bar on top
        libtcod.console_set_default_background(panel, bar_color)
        if bar_width > 0:
            libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

        #finally, some centered text with the values
        libtcod.console_set_default_foreground(panel, libtcod.white)
        libtcod.console_print_ex(panel, x + total_width / 2, y,
                libtcod.BKGND_NONE, libtcod.CENTER,
                name + ': ' + str(value) + '/' + str(maximum))

    def handleKeys(self):
        key = libtcod.console_wait_for_keypress(True)
        #TODO: Remove in next libtcod version
        #Attention: dirty hack, bug in libtcod fires keypress twice...
        key = libtcod.console_wait_for_keypress(True)

        key_char = chr(key.c)

        if key.vk == libtcod.KEY_ESCAPE:
            return 'exit'
        if self.game.state == Game.PLAYING:
            player = self.game.player
            #movement keys
            if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
                player.tryMoveOrAttack(0, -1)
            elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
                player.tryMoveOrAttack(0, 1)
            elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
                player.tryMoveOrAttack(-1, 0)
            elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
                player.tryMoveOrAttack(1, 0)
            elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
                player.tryMoveOrAttack(-1, -1)
            elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
                player.tryMoveOrAttack(1, -1)
            elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
                player.tryMoveOrAttack(-1, 1)
            elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
                player.tryMoveOrAttack(1, 1)
            #portal keys
            elif key_char == '>':
                player.tryFollowPortalDown()
            elif key_char == '<':
                player.tryFollowPortalUp()
            # update field of vision
            self.game.currentLevel.map.updateFieldOfView(
                player.tile.x, player.tile.y)

#This is where it all starts!
if __name__ == '__main__':
    myApplication = ApplicationPygcurse()
    myApplication.showWelcomeScreen()