import kivy
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty, ListProperty
import copy

#This module contains the kv rules and class definitions for all screens
#used by the screenManager widget
# The builder string lets you use kivy language inside specific modules
# The builder string contains graphical information for each screen,
#since most of the code only defines widget properties, comments were mostly
#left out in the .kv language


Builder.load_string("""

<MenuScreen>
    name: "Menu"
    menu: menu
    
    MenuLayout:
        id: menu
        size: root.size
        pos: root.pos

<MenuLayout>
    #Defines all ui elements of the menu screen
    startButton: start_button
    helpButton: help_button
    quitButton: quit_button
    
    canvas:
        Rectangle:
            size: root.size
            pos: root.pos
            source: "images/titleScreen.jpg"
    
    Button:
        id: start_button
        background_normal: "images/buttons/startButton.gif"
        background_down: "images/buttons/startButton_down.gif"
        center: root.center_x, root.height/3.5
        size: root.width/4, root.height/10
        
    Button:
        id: help_button
        background_normal: "images/buttons/helpButton.gif"
        background_down: "images/buttons/helpButton_down.gif"
        size: root.width/4, root.height/10
        center: root.center_x, start_button.center_y - self.height

        
    Button:
        id: quit_button
        background_normal: "images/buttons/quitButton.gif"
        background_down: "images/buttons/quitButton_down.gif"
        size: root.width/4, root.height/10
        center: root.center_x, help_button.center_y - self.height
        
<HelpScreen>
    name: "Help"
    #help screen uses a scrollview to allow scrolling of the help image
    ScrollView:
        size_hint: (None,None)
        width: root.width
        height: root.height

        Button:
        #help image is a giant button that returns to the menu when tapped
            size_hint_y: None
            text: "Return"
            background_normal: "images/helpScreen.gif"
            background_down: "images/helpScreen.gif"
            center: root.width/3, self.height
            size: root.width/8, root.height * 3    
            on_press: root.returnToMenu()


<PauseScreen>
    name: "Pause"
    continueButton: continue_button
    restartButton: restart_button
    pause: pause
    
    Pause:
        id: pause
        canvas:
            Rectangle:
                size: root.size
                pos: root.pos
                source: "images/pauseScreen.gif"
            
        Button:
            id: continue_button
            background_normal: "images/buttons/unpauseButton.gif"
            background_down: "images/buttons/unpauseButton_down.gif"
            size: root.width/3, root.height/10
            center: root.center_x+self.width/8, root.height/2
            
        Button:
            id: restart_button
            background_normal: "images/buttons/restartButton.gif"
            background_down: "images/buttons/restartButton_down.gif"
            size: root.width/3, root.height/10
            center:continue_button.center_x,continue_button.center_y-self.height
            

<MainGameScreen>
    mainGame: shooter_game
    name: "MainGame"
    ShooterGame:
        pos: root.pos
        size: root.size
        id: shooter_game
        pauseButton: pause_button
        
        Button:
            id: pause_button
            background_normal: "images/buttons/pauseButton.gif"
            background_down: "images/buttons/pauseButton_down.gif"
            width: root.width/14
            height: root.height/7
            center: (root.right - self.width/2), root.height - self.height/2
        
<GameOverScreen>
    name: "GameOver"
    restart: restart_button
    gameOver: game_over
    score: 0
    
    GameOver:
        id: game_over
        
        canvas:
            Rectangle:
                size: root.size
                pos: root.pos
                source: "images/gameOverScreen.gif"
        
        Button:
            id: restart_button
            center: root.center_x+self.width/8, root.height/2
            size: root.width/3, root.height/10
            background_normal: "images/buttons/restartButton.gif"
            background_down: "images/buttons/restartButton_down.gif"
            
        Label:
            center_x: restart_button.center_x
            center_y: restart_button.center_y - 2*restart_button.height
            text: "Score:  " + str(root.score)
            font_size: 30
            bold: True
            color: (0,0,0,1)

<UpgradeScreen>
    name: "Upgrade"
    tabbedPanel: tabbedPanel
    heroPage: hero_content
    abilityPage: ability_content
    exitPage: exit
    heroGold: 0
    heroContentHeader: hero_content_header
    exitHeader: exit_header
    
    TabbedPanel:
        id: tabbedPanel
        tab_width: root.width/3
        background_image: "images/shopScreen.gif"
        
        TabbedPanelHeader:
            id: hero_content_header
            content: hero_content
            background_down: "images/tabbedPanel/heroHeader.gif"
            background_normal: "images/tabbedPanel/heroHeader_down.gif"
            
        HeroUpgradePage:
            id: hero_content
            Label:
                text: "Gold:   " + str(root.heroGold) 
                center_y: root.height * .805
                center_x: root.width * 3/4
                bold: True
                font_size: 21
                color: 0,0,0,1
        
        TabbedPanelHeader:
            content: ability_content
            background_down: "images/tabbedPanel/abilityHeader.gif"
            background_normal: "images/tabbedPanel/abilityHeader_down.gif"
            
        AbilityUpgradePage:
            id: ability_content
            selectedButton: "missileDamage"
            
            Label:
                text: "Gold:   " + str(root.heroGold) 
                center_y: root.height * .805
                center_x: root.width * 3/4
                bold: True
                font_size: 21
                color: 0,0,0,1
            
        TabbedPanelHeader:
            id: exit_header
            content: exit
            background_down: "images/tabbedPanel/exitHeader.gif"
            background_normal: "images/tabbedPanel/exitHeader_down.gif"
            
        FloatLayout:
            id: exit
            exitBtn: exit_button
            Button:
                id: exit_button
                background_normal: "images/tabbedPanel/exitTab.gif"
                background_down: "images/tabbedPanel/exitTab.gif"
                on_press: root.exit()

<UpgradePage>
    stats: {"stats": 0}
    buyButton: buy_button
    selectionAmount: self.selectionAmount
    selectionCost: self.selectionCost
    selectionLevel: self.selectionLevel
    selectedButton: "health"
    upgrade1: upgrade1
    upgrade2: upgrade2
    upgrade3: upgrade3
    upgrade4: upgrade4
    
    # Each toggle button is bound to the change selection function
    # which updates the current upgrade info at the bottom of the screen
    ToggleButton:
        id: upgrade1
        name: "upgrade1"
        state: "down"
        group: "upgrades"
        size: root.width/2.75, root.height/10
        center: root.width/4, root.height * 3/4
        on_press: root.changeSelection(self.name, self)
    
    ToggleButton:
        id: upgrade2
        name: "upgrade2"
        group: "upgrades"
        center: upgrade1.center_x, upgrade1.center_y-self.height
        size: upgrade1.size
        on_press: root.changeSelection(self.name, self)
        
    ToggleButton:
        id: upgrade3
        name: "upgrade3"
        group: "upgrades"
        center: upgrade1.center_x, upgrade1.center_y-2*self.height
        size: upgrade1.size
        on_press: root.changeSelection(self.name, self)
        
    ToggleButton:
        id: upgrade4
        name: "upgrade4"
        group: "upgrades"
        center: upgrade1.center_x, upgrade1.center_y-3*self.height
        size: upgrade1.size
        on_press: root.changeSelection(self.name, self)

    Button:
        id: buy_button
        on_press: root.purchaseUpgrade()
        size: root.width/4, root.height/10
        background_normal: "images/tabbedPanel/purchaseButton.gif"
        background_down: "images/tabbedPanel/purchaseButton_down.gif"
        center: root.width * 3/4, root.height * 3/4
        border: (0,0,0,0)
        
    Label:
        text: "Available Upgrades:"
        center_y: root.height * 3/4 + 1.2 * root.height/10
        center_x: root.width/4
        font_size: 26
        color: 0,0,0,1

    Label:
        text: "Upgrade Cost:  " + str(root.selectionCost)
        center_x: root.width/4
        center_y: root.height / 3
        font_size: 18
        color: 0,0,0,1
    Label:
        text: "Upgrade:  " + str(root.selectionAmount)
        center_x: root.width/4
        center_y: root.height / 3 - 2.25* self.font_size
        halign: "center"
        font_size: 18
        color: 0,0,0,1
    Label:
        text: "Upgrade Level:  " + str(root.selectionLevel)
        center_x: root.width/4
        center_y: root.height / 3 - 6* self.font_size
        font_size: 18
        color: 0,0,0,1

<HeroUpgradePage>
    stats: {"health":0,"healthRegen":0,"mana":0,"manaRegen":0}
    
    #grid layout displays labels of the hero's stats
    GridLayout:
        center: root.width *3/4, root.height /2
        width: root.width/3
        row_default_height: root.height /14
        rows: 5
        cols: 1
        Label:
            id: current_stats_label
            text: "Current Stats:"
            bold: True
            font_size: 23
            color: 0,0,0,1
        Label:
            text: "Health:  " + str(root.stats["health"])
            font_size: 16
            color: 0,0,0,1
        Label:
            text: "HP Regen:  " + str(root.stats["healthRegen"])
            font_size: 16
            color: 0,0,0,1
        Label:
            text: "Psy:  " + str(root.stats["mana"])
            font_size: 16
            color: 0,0,0,1
        Label:
            text: "Psy Regen:  " + str(root.stats["manaRegen"])
            font_size: 16
            color: 0,0,0,1
    
<AbilityUpgradePage>:
    stats: {"missileDamage": 0, "others": None}
    upgrades: {"multiMissile":False,"rapidSlash":False}
    selectionStatus: 0
    
    Label:
        id: current
        center_y: root.height / 2
        center_x: root.width *3/4
        text: "Current Damage/Status:"
        font_size: 20
        color: 0,0,0,1
    Label:
        center_y: current.center_y - 2.5* self.font_size
        center_x: root.width *3/4
        text: str(root.selectionStatus)
        font_size: 16
        color: 0,0,0,1

    

""")

# Each screen below has an empyt class definition to be used with the .kv rules
# in the above loader string
class HelpScreen(Screen):
    def returnToMenu(self):
        screenManager = self.parent
        screenManager.current = "Menu"    

class PauseScreen(Screen):
    pass

class MenuScreen(Screen):
    pass

class MenuLayout(Widget):
    pass

class GameOverScreen(Screen):
    pass

class GameOver(Widget):
    pass

class Pause(Widget):
    pass

class MainGameScreen(Screen):
    pass

class UpgradeScreen(Screen):
    def init(self, hero):
        #initializes all data used by the upgrade screen
        #i.e stats and abilities and gold
        self.tabbedPanel.default_tab = self.heroContentHeader
        self.hero = hero
        abilities = hero.abilityHandler.abilities
        self.heroGold = hero.gold
        self.heroPage.stats = {"health": hero.maxHealth,
                 "healthRegen": hero.healthRegen,
                 "mana": hero.maxMana,
                 "manaRegen": hero.manaRegen}
        self.abilityPage.stats = {"missileDamage": abilities[0].damage,
                                  "slashDamage": abilities[1].damage,
                                  "multiMissile": abilities[0].multi,
                                  "rapidSlash": abilities[1].rapid}
        #stats are implemented as a dictionary for easy indexing based on the
        #toggle button selection
        self.heroPage.init()
        self.abilityPage.init()

    def exit(self):
        #leaves the upgrade screen and schedules an unpause
        self.screenManager = self.parent
        mainGame = self.screenManager.mainScreen.mainGame
        Clock.schedule_once(self.unpause, 1.0)
        self.screenManager.current="MainGame"
        

    def unpause(self, dt):
        #unpauses the game
        mainGame = self.screenManager.mainScreen.mainGame
        self.reinitStats(mainGame.hero)
        self.reinitAbilities(mainGame.hero.abilityHandler.abilities)
        mainGame.isPaused = False
        
        
    def reinitStats(self, hero):
        #passes the now altered stats back to the hero class
        stats = self.heroPage.stats
        hero.maxHealth = stats["health"]
        hero.health = hero.maxHealth
        hero.healthRegen = stats["healthRegen"]
        hero.maxMana = stats["mana"]
        hero.mana = hero.maxMana
        hero.manaRegen = stats["manaRegen"]
        hero.gold = self.heroGold
        
    def reinitAbilities(self,abilities):
        #passes new altered ability data to the abilityHandler
        stats = self.abilityPage.stats
        abilities[0].damage = stats["missileDamage"]
        abilities[1].damage = stats["slashDamage"]
        abilities[0].multi = stats["multiMissile"]
        abilities[1].rapid = stats["rapidSlash"]
        

class UpgradePage(Widget):
    #main class used by each upgrade page within the upgrade screen
    def init(self):
        #initalizes button information and current selection information
        buttons = [self.upgrade1, self.upgrade2, self.upgrade3, self.upgrade4]
        for i in xrange(len(buttons)):
            button = buttons[i]
            button.name = self.keys[i]
            button.group = self.buttonGroup
            button.background_normal = "images/tabbedPanel/" + self.buttonNormals[i]
            button.background_down = "images/tabbedPanel/" + self.buttonDowns[i]
        self.selectionCost = self.upgradeCosts[self.selectedButton]
        self.selectionAmount = self.upgradeAmounts[self.selectedButton]
        self.selectionLevel = self.upgradeLevels[self.selectedButton]
        self.selectionStatus = self.stats[self.selectedButton]
        
    def changeSelection(self, selection, button):
        #updates the selection data when called by a button press
        self.selectionCost = self.upgradeCosts[selection]
        self.selectionAmount = self.upgradeAmounts[selection]
        self.selectionLevel = self.upgradeLevels[selection]
        if button != None and button.name == self.selectedButton:
            button.state = "down"
            #guarantees that a button doesn't untoggle itself
        self.selectedButton = selection
        
    def purchaseUpgrade(self): pass
        #dependant on each individual page

class HeroUpgradePage(UpgradePage):
    def __init__(self, **kwargs):
        #inits all shop information, i.e prices, amaounts, images, etc
        super(HeroUpgradePage, self).__init__(**kwargs)
        self.buttonGroup = "heroUpgrades"
        self.keys = ["health","healthRegen","mana","manaRegen"]
        self.upgradeAmounts = {"health": 20,
                               "healthRegen": .05,
                               "mana": 15,
                               "manaRegen": .05}
        self.upgradeCosts = {"health": 100,
                             "healthRegen": 300,
                             "mana": 100,
                             "manaRegen": 300}
        self.upgradeLevels = {"health": 0,
                             "healthRegen": 0,
                             "mana": 0,
                             "manaRegen": 0}
        self.buttonNormals = ["healthUpgrade.gif", "hpRegenUpgrade.gif",
                              "manaUpgrade.gif", "manaRegenUpgrade.gif"]
        self.buttonDowns = ["healthUpgrade_down.gif", "hpRegenUpgrade_down.gif",
                        "manaUpgrade_down.gif", "manaRegenUpgrade_down.gif"]
       
    def purchaseUpgrade(self): #called when the purchase button is pressed
        selection = self.selectedButton
        print selection
        stats = copy.deepcopy(self.stats)
        gold = self.parent.parent.parent.parent.heroGold
        if gold >= self.upgradeCosts[selection]:
            upgradeCosts = copy.deepcopy(self.upgradeCosts)
            upgradeAmounts = copy.deepcopy(self.upgradeAmounts)
            upgradeLevels = copy.deepcopy(self.upgradeLevels)
            #since upgrade____ is an object property, they must be reassigned
            #in order for the kivy binding to see a "change"
            self.parent.parent.parent.parent.heroGold -= upgradeCosts[selection]
            stats[selection] += upgradeAmounts[selection]
            upgradeLevels[selection] += 1
            if selection == "manaRegen" or selection == "healthRegen":
                upgradeAmounts[selection]= ( #formula used to scale costs
                    int(1000 * upgradeAmounts[selection]+4)/5*5/1000.0)
            else: #uses int division to guarantee rounding to nearest 5
                upgradeAmounts[selection]=(#different formula for nonRegen stats
                    int(1.4*upgradeAmounts[selection]+3)/5*5)
            upgradeCosts[selection] = (
                int(1.75*upgradeCosts[selection] + 3) / 5 * 5)
            self.stats = stats
            self.upgradeCosts = upgradeCosts
            self.upgradeAmounts = upgradeAmounts
            self.upgradeLevels = upgradeLevels
            self.changeSelection(self.selectedButton, None)

class AbilityUpgradePage(UpgradePage):
    def __init__(self, **kwargs):
        #initializes ability upgrade info
        super(AbilityUpgradePage, self).__init__(**kwargs)
        self.buttonGroup = "abilityUpgrades"
        self.keys = ["missileDamage","slashDamage","multiMissile","rapidSlash"]
        self.upgradeAmounts = {"missileDamage": 7.5,
                               "slashDamage": 7.5,
                               "multiMissile":
                                "\nFires 3 missiles instead of one",
                               "rapidSlash":
                                "\nRapidly creates 3 slashes at once"}
        self.upgradeCosts = {"missileDamage": 400,
                               "slashDamage": 400,
                               "multiMissile": 3000,
                               "rapidSlash": 3000}
        self.upgradeLevels = {"missileDamage": 0,
                               "slashDamage": 0,
                               "multiMissile": False,
                               "rapidSlash": False}
        self.buttonNormals = ["missileDamageUpgrade.gif",
                              "slashDamageUpgrade.gif",
                              "multiShotUpgrade.gif",
                              "rapidSlashUpgrade.gif"]
        self.buttonDowns = ["missileDamageUpgrade_down.gif",
                            "slashDamageUpgrade_down.gif",
                            "multiShotUpgrade_down.gif",
                            "rapidSlashUpgrade_down.gif"]
        
    def changeSelection(self, selection, button):
        #updates selection info when a button is pressed
        self.selectionStatus = self.stats[selection]
        super(AbilityUpgradePage,self).changeSelection(selection, button)
        
    def purchaseUpgrade(self): #called when purchas button is pressed
        selection = self.selectedButton
        stats = copy.deepcopy(self.stats)
        gold = self.parent.parent.parent.parent.heroGold
        if (gold >= self.upgradeCosts[selection] and
            stats[selection] != True):
            upgradeCosts = copy.deepcopy(self.upgradeCosts)
            upgradeAmounts = copy.deepcopy(self.upgradeAmounts)
            upgradeLevels = copy.deepcopy(self.upgradeLevels)
            self.parent.parent.parent.parent.heroGold -= upgradeCosts[selection]
            upgradeLevels[selection] += 1
            if "Damage" in selection: #damage does not scale exponentially
                stats[selection] += upgradeAmounts[selection]
                upgradeCosts[selection] = (#same formula as for hero upgrades
                    int(1.75*upgradeCosts[selection] + 3) / 5 * 5)
            else:
                stats[selection] = True
            self.stats = stats
            self.upgradeCosts = upgradeCosts
            self.upgradeAmounts = upgradeAmounts
            self.upgradeLevels = upgradeLevels
            self.changeSelection(self.selectedButton,None)

        
        
    
