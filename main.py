import kivy
from enemies import *
from keyboardEvents import KeyboardListener
from screens import *
from abilities import *
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager,FadeTransition,ShaderTransition
from kivy.uix.progressbar import ProgressBar
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty

#Main Document, contains the main game, app, and hero classes


class KeyPressed(KeyboardListener):
    #handles all keyboard events and calls KeyPress when a key is pressed
    def on_keyPress(self, keyboard, keycode, text, modifier):
        #print str(keycode[1]) + " Pressed"
        self.parent.keyPress(keyboard,keycode)
        return True

class Hero(Widget):
    #main character class, handles touch based movement, and has base stats
    usingAbility = BooleanProperty(False) 
    
    def initStats(self):
        #sets default starting stats
        self.maxMana = 100
        self.maxHealth = 100
        self.manaRegen = .3
        self.healthRegen = 0
        self.mana = self.maxMana
        self.health = self.maxHealth
        self.score = 0
        self.gold = 0
    
    def on_touch_down(self,touch):
        #called when a touch is made
        if not self.parent.isPaused:
            if self.collide_point(touch.x,touch.y):
                #checks if the touch is on th hero
                touch.ud["function"] = "move" #if so,
                #tags the touch so that it can only be used to move the hero
            elif (not self.usingAbility):
                #if not touching the hero, use ability
                if self.abilityHandler.dispatch('on_touch_down', touch):
                    return True #passes the touch to the other children
                self.abilityHandler.use_activeAbility(touch)
            
    
    def on_touch_up(self,touch):
        #called when the touch is released
        if "function" in touch.ud and touch.ud["function"] == "ability":
            self.usingAbility = False
            #releases the ability's activation
            self.abilityHandler.up_activeAbility(touch)
    
    def on_touch_move(self,touch):
        #called when the touch is moved, moves the hero to the location of
        #the touch
        if not self.parent.isPaused and "function" in touch.ud:
            if touch.ud["function"] == "move":
                #only moves the hero if the touch is associated with moving
                self.center_x, self.center_y = touch.x, touch.y
            elif touch.ud["function"] == "ability":
                #otherwise, touch is associated with using an ability
                #thus, calls the ability's touch_move function
                self.abilityHandler.move_activeAbility(touch)
                
    def gotHit(self):
        # called when hero is hit
        game = self.parent
        game.hitImage = game.hitFrame_bloody
        #changes game images to reflect being hit
        self.image = self.image_hit
        Clock.schedule_once(self.restoreImage, .25)
        
    def restoreImage(self, dt=0):
        #restores the images .25 seconds later
        game = self.parent
        game.hitImage = game.hitFrame_normal
        self.image = self.image_normal


class ShooterGame(Widget):
    currentLevel = 0
    isPaused = True
    visitStore = False
    goToNextLevel = False
    previousScore = 0
    
    def addKeyboard(self):
        #called when a secret button is pushed, enables cheats
        self.add_widget(KeyPressed())
    
    def keyPress(self,keyboard,keycode):
        #keyPressed function
        if self.isPaused == False:
            levels = len(self.enemyHandler.levels)
            numbers = "1234567890"
            XDistance = self.width / 15
            YDistance = self.height / 15
            screenManager = self.parent.parent.parent
            abilities = self.hero.abilityHandler.abilities
            #wasd moves the hero
            if keycode[1] == "w":
                self.hero.center_y += YDistance
            elif keycode[1] == "s":
                self.hero.center_y -= YDistance
            elif keycode[1] == "a":
                self.hero.center_x -= XDistance
            elif keycode[1] == "d":
                self.hero.center_x += XDistance
            elif keycode[1] == "g": #sets "god" mode
                self.hero.maxHealth = 10000000
                self.hero.healthRegen = 10000
                self.hero.maxMana = 1000000
                self.hero.manaRegen = 10000
                self.hero.health = self.hero.maxHealth
                self.hero.mana = self.hero.maxMana
                self.hero.gold = 10000
            elif keycode[1] == "u":
                self.goToUpgradeScreen()
            elif keycode[1] == "i":
                abilities[0].damage = 100000
                abilities[1].damage = 100000
            elif keycode[1] == "o":
                abilities = self.hero.abilityHandler.abilities
                abilities[0].multi = not abilities[0].multi
                abilities[1].rapid = not abilities[1].rapid
            elif keycode[1] in numbers: #sets levels
                self.currentLevel = int(keycode[1]) % levels
            elif keycode[1] == "up":
                self.currentLevel = (self.currentLevel + 1) % levels
                level = self.enemyHandler.levels[self.currentLevel]
                self.verifyLevel(level, 0)
                
       
        
    def update(self, dt):
        #timerFired function
        if not self.isPaused:
            #if not paused, updates the hero's mana and health
            self.hero.health += self.hero.healthRegen
            if self.hero.health > self.hero.maxHealth:
                self.hero.health = self.hero.maxHealth
            if self.hero.usingAbility == False:
                self.hero.mana += self.hero.manaRegen
                if self.hero.mana > self.hero.maxMana:
                    self.hero.mana = self.hero.maxMana
            self.updateEnemies() #updates each enemy and each particle
            for particle in self.hero.abilityHandler.particles:
                particle.update()
    
    def updateEnemies(self): #updates each enemy on screen
        for enemy in self.enemyHandler.children:
            if enemy.dead == False:
                enemy.move()
                destruct = False
                #destruct determines if the enemy dies after updates
                if enemy.collisionCheck(self.hero):
                    #if enemy hit the hero
                    self.hero.gotHit()
                    self.hero.health -= enemy.damage
                    if self.hero.health <= 0:
                        self.gameOver()
                    destruct = True
                elif self.particleCollisions(enemy) == True:
                    #checks collisions with ability particles
                    #will return true if enemy dies
                    destruct = True
                if destruct == True: enemy.destruct()
                
    def particleCollisions(self,enemy):
        #checks for collisions with all ability particles on screen
        destruct = False
        for particle in self.hero.abilityHandler.particles:
            #runs through every particle in the ability handler
            if "Boss"  in enemy.name:
                #calls a boss specific function if enemy is a boss
                enemy.particleCollide(particle,self.hero)
            elif not enemy.isHit and particle.collisionCheck(enemy):
                #if enemy has not already been hit and collides with a particle
                enemy.health -= particle.parent.damage 
                if enemy.health <= 0:
                    self.hero.score += enemy.scoreBonus
                    self.hero.gold += enemy.scoreBonus
                    destruct = True
                else: enemy.gotHit()
                particle.destruct()
        return destruct
        
    def gameOver(self): #puts the game into game over mode
        screenManager = self.parent.parent.parent
        mainGameScreen = self.parent.parent
        if screenManager != None and mainGameScreen != None:
            #ensures that the game has not already been reset
            score = mainGameScreen.mainGame.hero.score
            #passes the score to the game over screen
            screenManager.gameOverScreen.score = score
            #unschedules all events and changes the screen to
            #the gameover screen
            Clock.unschedule(self.update)
            Clock.unschedule(self.enemyScheduler)
            screenManager.current = "GameOver"
   
    def enemyScheduler(self,dt=0): #spawns enemies at the given interval
        level = self.enemyHandler.levels[self.currentLevel]
        #locates the level object
        enemyCounts = self.enemyHandler.enemyCounts #computes the enemies left
        enemiesLeft = len(self.enemyHandler.children)
        self.verifyLevel(level, enemiesLeft) #checks for level advancement
        level = self.enemyHandler.levels[self.currentLevel]
        #relocates level object incase level changed
        if self.visitStore == True and enemiesLeft <= 0:
            self.goToUpgradeScreen()
        elif (not self.isPaused and not self.visitStore and
              not self.goToNextLevel): #if not the end of a level
            roll = random.random() #spawns a random enemy
            for i in xrange(len(level["enemyTypes"])):
                enemy = level["enemyTypes"][i]#locates enemy from level data
                enemyCount = enemyCounts[enemy.name]
                cap = level["enemyCaps"][i]
                roll -= level["enemyFrequencies"][i]
                #subtracts the freq. so that only one enemy can be spawned
                if roll < 0 and enemyCount < cap:
                    self.enemyHandler.addEnemy(enemy)
                    break #ends the loop once an enemy is spawned
    
    def verifyLevel(self, level, enemiesLeft): #checks for level advancement
        if self.hero.score - self.previousScore >= level["nextCriteria"]:
            self.goToNextLevel = True
        if self.goToNextLevel == True and enemiesLeft <= 0:
            self.goToNextLevel = False
            previousLevel = self.enemyHandler.levels[self.currentLevel]
            previousLevel["multiplier"] *= 1.75
            #scales the multiplier so that levels become harder
            previousLevel["nextCriteria"] *= 2.25
            nextLevel = self.currentLevel + 1
            self.previousScore = self.hero.score
            if nextLevel >= len(self.enemyHandler.levels):
                #modulates level if no more preset levels exist
                #essentially restarts the game with harder foes
                nextLevel = nextLevel % (len(self.enemyHandler.levels))
            self.currentLevel = nextLevel
            level = self.enemyHandler.levels[nextLevel]
            if level["goToStoreBefore"]==True:
                self.visitStore = True #vists the store if level data says so

                    
    def goToUpgradeScreen(self): #changes the screen to the upgrade screen
        screenManager = self.parent.parent.parent
        self.hero.usingAbility = False
        self.visitStore = False
        self.isPaused = True
        upgradeScreen = screenManager.upgradeScreen
        upgradeScreen.init(self.hero)#passes the upgradeScreen the hero's stats
        screenManager.current="Upgrade"
        upgradeScreen.tabbedPanel.switch_to(upgradeScreen.heroContentHeader)
        #guarantee that the first tab is the selected one
        upgradeScreen.heroContentHeader.state="down"
        upgradeScreen.exitHeader.state="normal"


class ShooterApp(App):    
    def build(self): #builds the main game
        self.initFactory()
        self.game = ScreenManager(transition= FadeTransition())
        self.initAbilities(self.game)
        self.initButtons()
        self.initTimerEvents()
        mainGame = self.game.mainScreen.mainGame
        mainGame.hero.initStats()
        self.game.upgradeScreen.hero = mainGame.hero
        return self.game #sets the screenManager as the root
    
    def initButtons(self):
        #binds all buttons to their respective functions
        self.game.gameOverScreen.restart.bind(on_press = self.restart)
        self.game.menuScreen.menu.quitButton.bind(on_press = self.stop)
        self.game.menuScreen.menu.startButton.bind(on_press = self.startGame)
        self.game.menuScreen.menu.helpButton.bind(on_press = self.loadHelp)
        self.game.pauseScreen.continueButton.bind(on_press = self.unpause)
        self.game.pauseScreen.restartButton.bind(on_press = self.restart)
        self.game.mainScreen.mainGame.pauseButton.bind(on_press = self.pause)
    
    def pause(self,button):
        #pauses the game and goes to to the pause screen
        self.game.mainScreen.mainGame.isPaused = True
        self.game.current = "Pause"
    
    def unpause(self, button=None ,dt=0):
        #unpauses the game
        self.game.current="MainGame"
        #schedules the actual unpause so that the transition ends before
        #enemies begin to move again
        Clock.schedule_once(self.notPaused, 1.0)
    
    def notPaused(self, dt=0): #sets the pause variable to False
        self.game.mainScreen.mainGame.isPaused = False
    
    def startGame(self, button):
        #called by the start game button
        self.game.current = "MainGame"
        self.game.mainScreen.mainGame.isPaused = False
    
    def loadHelp(self, button):
        #loads the help screen
        self.game.current = "Help"
    
    def initAbilities(self,game):
        #initializes the ability buttons and sets active ability
        mainGame = game.mainScreen.mainGame
        abilityHandler = mainGame.hero.abilityHandler
        abilityHandler.abilities = [MissileAbility(),SlashAbility()]
        buttons = [abilityHandler.abilityButton0,
                   abilityHandler.abilityButton1]
        abilityHandler.setActiveAbility(abilityHandler.abilities[0])
        #the above lists can be changed if new abilities are added
        for i in xrange(2):
            abilityHandler.setAbilityButton(buttons[i],
                                            abilityHandler.abilities[i])
            
    
    def initTimerEvents(self):
        #schedules all timer fired events
        mainGame = self.game.mainScreen.mainGame
        Clock.schedule_interval(mainGame.update, 1.0/60)
        Clock.schedule_interval(mainGame.enemyScheduler, .3)
    
    def reinit(self):
        #reiitializes the game after a restart
        Clock.unschedule(self.game.mainScreen.mainGame.update)
        Clock.unschedule(self.game.mainScreen.mainGame.enemyScheduler)
        self.game.remove_widget(self.game.mainScreen)
        self.game.remove_widget(self.game.upgradeScreen)
        #clears both the gameover screen and the maingame screen
        newScreen = MainGameScreen(name="MainGame")
        newUpgradeScreen = UpgradeScreen(name="Upgrade")
        #adds new screens to the game
        self.game.add_widget(newScreen)
        self.game.add_widget(newUpgradeScreen)
        self.game.mainScreen.clear_widgets()
        self.game.mainScreen = newScreen
        self.game.upgradeScreen = newUpgradeScreen
    
    def restart(self,button):
        #called by the restart button to reset the game
        self.reinit()
        #changes the screen back to the main menu
        self.game.current = "Menu"
        self.game.mainScreen.mainGame.hero.initStats()
        self.game.mainScreen.mainGame.isPaused = True
        self.game.mainScreen.mainGame.pauseButton.bind(on_press = self.pause)
        self.initAbilities(self.game)
        self.initTimerEvents()
    
    def initFactory(self): #creates factory definitions of classes
        #to be used in .kv file
        Factory.register("Hero", Hero)
        Factory.register("ShooterGame", ShooterGame)
        Factory.register("KeyPressed", KeyPressed)
        Factory.register("EnemyHandler", EnemyHandler)
        Factory.register("GameOver", GameOver)
        Factory.register("AbilityHandler", AbilityHandler)
        Factory.register("GameOverScreen", GameOverScreen)
        Factory.register("MainGameScreen", MainGameScreen)
        Factory.register("UpgradeScreen", UpgradeScreen)
        Factory.register("UpgradePage", UpgradePage)
        Factory.register("HeroUpgradePage", HeroUpgradePage)
        Factory.register("AbilityUpgradePage", AbilityUpgradePage)
        Factory.register("MenuScreen", MenuScreen)
        Factory.register("MenuLayout", MenuLayout)
        Factory.register("HelpScreen", HelpScreen)
        Factory.register("PauseScreen", PauseScreen)
        Factory.register("Pause", Pause)

if __name__ in ('__main__', '__android__'):
    ShooterApp().run()