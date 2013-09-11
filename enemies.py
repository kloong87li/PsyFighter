import kivy
from kivy.uix.widget import Widget
from kivy.uix.image import Image
import random
from kivy.lang import Builder
from kivy.graphics import Ellipse, Rotate, PushMatrix, PopMatrix
from kivy.clock import Clock
from kivy.vector import Vector
import random

# This module contains all class definitions for the enemy handler
#Levels are handled bu the enemy handler
#the enemy handler manages the addition of enemies and serves as the root node
# for all enemy children
# and enemy classes
#the loader string contains rules for each enemy type (size, and canvas image)

Builder.load_string(
"""
<BasicEnemy>
    image_normal: "images/enemies/basicEnemy.gif"
    image_hit: "images/enemies/basicEnemy_hit.gif"
    image: self.image_normal
    canvas:
        Ellipse:
            source: root.image
            pos: self.pos
            size: self.size
            
<SwerveEnemy>
    image_normal: "images/enemies/swerveEnemy.gif"
    image_hit: "images/enemies/swerveEnemy_hit.gif"
    image: self.image_normal
    canvas:
        Ellipse:
            source: root.image
            size: self.size
            pos: self.pos

<HomingEnemy>
    image_normal: "images/enemies/homingEnemy.gif"
    image_hit: "images/enemies/homingEnemy_hit.gif"
    image: self.image_normal
    canvas:
        Ellipse:
            source: root.image
            size: self.size
            pos: self.pos
            
<SnakePart>
    image_normal: "images/enemies/snakePart.gif"
    image_hit: "images/enemies/snakePart_hit.gif"
    image: self.image_normal
    canvas:
        Ellipse:
            source: root.image
            size: self.size
            pos: self.pos
""")
        
class Enemy(Widget): #base enemy class
    #all enemies have the following stats associated with them:
    name = None
    isHit = False
    scoreBonus = 0
    dead = False
    health = 0
    velocity = Vector(0,0)
    image_normal = None
    image_hit = None
    shake = 0
    
    def createSelf(self,x,y): pass
    
    def applyMultiplier(self, level): #applies level multipler to enemy stats
        #this causes the levels to get progressively harder
        multiplier = level["multiplier"]
        self.scoreBonus = int(multiplier*self.scoreBonus)
        self.health *= multiplier
        self.damage *= multiplier
            
    def move(self):
        #destroys the enemy once it passes the left boundary of the screen
        if (self.right <= 0): 
            self.destruct()
    
    def gotHit(self):
        #called when any enemy gets hit
        self.isHit = True
        self.image = self.image_hit
        #changes the enemy graphic
        Clock.schedule_once(self.restoreImage, .1)
        self.shake = 8
        self.center_y += self.shake #shakes the enemy
        Clock.schedule_interval(self.shakeSelf, .02)
    
    def shakeSelf(self, dt=0):
        #applies a "jitter" effect to the enemy position
        if self.shake > 0:
            self.center_y -= 2*self.shake
            self.shake *= -1
        else:
            self.center_y += -1.5 * self.shake
            self.shake /= -2
        

    def restoreImage(self, dt=0):
        #resets the enemy image to normal after being hit
        self.isHit = False
        Clock.unschedule(self.shakeSelf)
        self.center_y -= self.shake
        #guarantees that the enemy position ends up back where it started
        self.shake = 0
        self.image = self.image_normal
    
    def collisionCheck(self,other):
        #uses kivy's built in collsion function to check whether the enemy
        #collides with another widget
        if self.collide_widget(other):
            return True
        else:
            return False
    
    def removeSelf(self,dt=0):
        #removes self from the enemy handler
        self.parent.enemyCounts[self.name] -= 1
        self.parent.remove_widget(self)
    
    def destruct(self):
        #called when enemy dies
        self.dead = True
        self.canvas.clear()
        with self.canvas:
            #changes enemy image to an explosion
            Ellipse(source="images/explode.gif",
                    size = self.size, pos = self.pos)
        Clock.schedule_once(self.removeSelf, .25)

class BasicEnemy(Enemy):
    #this enemy simply travels forward in a straight line
    #at a constant velocity
    name = "BasicEnemy"
    scoreBonus = 10
    health = 15
    damage = 25
    velocity = Vector(-10,0)
    
    def createSelf(self,x,y):
        #places self at the given position
        game = self.parent.parent
        self.center_x = x
        self.center_y = y
        self.width = game.width/12
        self.height = game.height/12
    
    def move(self):
        #moves by adding velocity to position
        self.pos = self.velocity + self.pos
        super(BasicEnemy,self).move()

        
class SwerveEnemy(Enemy):
    #an enemy that randomly turns at a random angle
    name = "SwerveEnemy"
    scoreBonus = 20
    health = 20
    damage = 25
    velocity = Vector(-6,0)
    angle = 0
    
    def createSelf(self,x,y):
        #creates self at x,y and schedules a random turn
        game = self.parent.parent
        self.center_x = x
        self.center_y = y
        self.width = game.width/12
        self.height = game.height/12
        self.angle = random.randint (-75,75)
        Clock.schedule_once(self.turn, self.nextTurnTime())

    def move(self):
        #moves by rotating the velocity by the random angle
        #then adds the velocity to pos.
        velocity = self.velocity.rotate(self.angle)
        self.pos = velocity + self.pos
        super(SwerveEnemy,self).move()
        
    def nextTurnTime(self):
        #randomly determines a next turn time
        return (.5 + random.random() * 1.5)
    
    def turn(self,dt=0):
        #generates a random angle and stores it in self
        self.angle = random.randint(-75,75)
        #schedules another random turn
        Clock.schedule_once(self.turn, self.nextTurnTime())
        
class HomingEnemy(Enemy):
    #an enemy that will target and home on the hero
    name = "HomingEnemy"
    scoreBonus = 20
    health = 15
    damage = 15
    velocity = Vector(-8,0)
    angle = 0
    
    def createSelf(self,x,y):
        #creates self at x,y
        game = self.parent.parent
        self.center_x = x
        self.center_y = y
        self.width = game.width/12
        self.height = game.height/12

    def move(self):
        #moves toward the hero's position
        angle = self.getAngle()
        #gets the angle that it needs to travel at
        #rotates the velocity and moves the enemy
        if angle < 55 and angle > (-55):
            #guarantees that the enemy can't turn more than 55 degrees
            self.angle = angle
        velocity = self.velocity.rotate(self.angle)
        self.pos = velocity + self.pos
        super(HomingEnemy,self).move()
        
    def getAngle(self):
        #calculates the angle between the hero's position and the enemy's
        hero = self.parent.parent.hero
        x = hero.center_x - self.center_x
        y = hero.center_y - self.center_y
        #utilizes kivy's vector implementation
        return Vector(x,y).angle((-1,0))
    
class SnakeBoss(Enemy):
    #the main boss enemy - a giant snake that wraps around the screen
    #and may split into segments
    name = "SnakeBoss"
    velocity = Vector(-9,0)
    angle = 0
    
    #Each snake boss has a bunch of snake parts as children
    #the children are stored in a list: self.body
    #if the part is the first one in the lsit, it behaves as a head and has
    #more health.
    
    def createSelf(self,x,y,parts=None):
        game = self.parent.parent
        if parts == None:
            #generates a new body if no parts were given
            self.body = [SnakePart() for i in xrange(13)]
            for i in xrange(len(self.body)):#inits and parents each part
                part = self.body[i]
                x = x + part.width
                self.add_widget(part)
                part.createSelf(x,y,game)
        else: #if parts were given as an argument:
            self.body = parts
            self.parent.enemyCounts[self.name] += 1
            for part in self.body:
                self.add_widget(part)
        # sets the first part in the list as the head
        self.body[0].setHeadHealth(self.body)
        self.body[0].setHeadImages()
        Clock.schedule_once(self.turn,self.nextTurnTime())
        
    def applyMultiplier(self,level):
        #applies the level multiplier to each part
        for part in self.body:
            part.applyMultiplier(level)
    
    def nextTurnTime(self): #same as swerve enemy
        return (1.5 + random.random() * 1.5)
    
    def turn(self,dt=0): #turns by 90 degrees in either direction
        turn = random.randint(1,2)
        if turn == 1:
            self.angle -= 90
        else:
            self.angle += 90
        Clock.schedule_once(self.turn, self.nextTurnTime())
    
    def move(self): #moves each part in the body
        for i in xrange(len(self.body)):
            if i == 0:
                #if the part is the first in the list, it moves as the head
                self.body[i].moveAsHead(self.velocity,self.angle)
            else: #body parts then follow the previous part in the list
                part = self.body[i]
                previousPart = self.body[i-1]
                magnitude = self.velocity.length()
                part.move(previousPart,magnitude)
                
    def particleCollide(self,particle, hero):
        #checks for collision with any part in the body
        for part in self.body:
            if (not part.isHit and not part.dead
                and particle.collisionCheck(part)):
                part.health -= particle.parent.damage 
                if part.health <= 0:
                    if part == self.body[0]:
                        #if the aprt was a head, destroy the entire snake
                        self.destroySelf(hero)
                    else: #the part dies and the snake splits
                        hero.score += part.scoreBonus
                        hero.gold += part.scoreBonus
                        self.splitSelf(part)
                        part.destruct()
                else: part.gotHit()
                particle.destruct(); break
                #break loop so each particle only hits one part
    
    def destroySelf(self,hero):
        #destructs each body part and removes self from parent
        for part in self.body:
            if part.dead != True:
                hero.score += part.scoreBonus
                hero.gold += part.scoreBonus
                part.destruct()
        Clock.schedule_once(self.removeSelf, .1)

            
    def splitSelf(self, part):
        #splits the snake into two halves
        if len(self.body) > 2: #only if body is more than two parts
            splitIndex = self.body.index(part)
            firstHalf = self.body[:splitIndex+1]
            secondHalf = self.body[splitIndex+1:]
            if len(secondHalf) > 0 and not secondHalf[0].dead:
                #guarantees that the second half doesnt die right away
                for part in secondHalf:
                    part.removeSelf(0)
                    #removes the secondHalf parts from the first half
                secondSnake = SnakeBoss() #inits a new snakeBoss
                self.parent.add_widget(secondSnake)
                secondSnake.createSelf(0,0,secondHalf)
                #splits the head's health amongst the new heads
                self.splitHeadHealth(firstHalf,secondHalf)
                self.body = firstHalf
        
        
    def splitHeadHealth(self, firstHalf, secondHalf):
        #the head's health is split among segments when split apart
        n = len(firstHalf) + len(secondHalf) + 1
        originalHealth = firstHalf[0].health
        #each head gains a proportion of the original head health
        firstHalf[0].health = originalHealth * len(firstHalf)/n
        if len(secondHalf) > 0:
            secondHalf[0].health = originalHealth * len(secondHalf)/n
    
    def collisionCheck(self,hero):
        #checks for collision with the hero for each part
        for part in self.body:    
            if part.hitHero == False and part.collide_widget(hero):
                hero.health -= part.damage
                part.hitHero = True
                Clock.schedule_once(part.unHitHero, .25)
                #adds a hit timer to the snake so that it doesnt hit the
                #hero too many times when passing through the hero
                hero.gotHit()
                if hero.health <= 0:
                       hero.parent.gameOver()

class SnakePart(Enemy):
    #class for each part of the snake boss
    name = "SnakePart"
    hitHero = False
    scoreBonus = 75
    health = 150
    partHealth = 150 #how much health each part gives the head
    headHealth = 300 #base head health
    partContribution = .5
    #determines the proportion of health that each part gives to the head as
    # a bonus
    damage = 15
    spawning = True
    
    def applyMultiplier(self, level):
        #applies level multipler to each stat of the enemy
        multiplier = level["multiplier"]
        self.scoreBonus = int(multiplier*self.scoreBonus)
        self.health *= multiplier
        self.partHealth *= multiplier
        self.headHealth *= multiplier
        self.damage *= multiplier
    
    def createSelf(self,x,y, game):
        #creates self at x,y
        #uses an aboslute position rather than the kivy defined pos
        #this is for the wrapAround implementation
        self.root = self.get_root_window()
        self.pos = (x,y)
        self.absolutePos = [x,y]
        self.width = game.width/12
        self.height = game.height/12
    
    def setHeadImages(self):
        #sets the head to use headImages
        self.image_normal = "images/enemies/snakeHead.gif"
        self.image_hit = "images/enemies/snakeHead_hit.gif"
        self.image = self.image_normal
    
    def move(self, previousPart, magnitude):
        #moves an individual part
        #first calculates the previous part's position and vectorizes it
        previousPos = (previousPart.absolutePos[0],previousPart.absolutePos[1])
        destination = Vector(previousPos[0], previousPos[1])
        current = (self.absolutePos[0], self.absolutePos[1])
        velocity = Vector(destination.x-current[0],destination.y-current[1])
        #determines velocity based on destination and current position
        if destination.distance(current) < self.width:
            #realigns the part velocity so that parts don't outrun the head
            #when the head turns
            magnitude *= velocity.length() / self.width
        velocity = velocity.normalize() * magnitude
        self.absolutePos[0] += velocity.x
        self.absolutePos[1] += velocity.y
        self.wrapAround()
    
    def setHeadHealth(self,parts):
        #sets the inital head health based on the contribution factor
        #and part base health
        n = len(parts)
        self.health = (self.headHealth + self.partContribution
                       * n * self.partHealth)
        
    
    def moveAsHead(self, velocity, angle):
        #if the part is a head, it moves normally
        velocity = velocity.rotate(angle)
        self.absolutePos[0] += velocity.x
        self.absolutePos[1] += velocity.y
        self.wrapAround()
        
    def wrapAround(self): #wraps the snake around the screen by modulating
        #the part's absolute position
        upperBound = self.root.height +  self.height
        rightBound = self.root.width +  self.width
        if (self.absolutePos[0] < rightBound and
            self.absolutePos[1] < upperBound):
            self.spawning = False
            #the snake doesnt start wrapping until it reaches the screen for
            # the first time
        if self.spawning == True:
            #if it is spawning, then the position is equal to absPosition
            self.center_x = self.absolutePos[0]
            self.center_y = self.absolutePos[1]
        else: #otherwise, modulate the position so it wraps around the screen
            self.center_x = self.absolutePos[0] % rightBound
            self.center_y = self.absolutePos[1] % upperBound
    
    def unHitHero(self,dt=0):
        #wrapper function to set hitHero variable to false
        #allows it to be called by a clock function
        self.hitHero = False
    
    def removeSelf(self,dt):
        #unparents the part from the snakeBoss and body list
        self.parent.body.remove(self)
        self.parent.remove_widget(self)
        

class EnemyHandler(Widget):
    
    #The enemy handler class manages all enemies and serves as a central node
    #for all enemy widgets, it also manages all level data
    
    #levels are definied by the enemy types, their corresponding probabilities
    # of spawning, a multiplier value, and a score criteria
    
    def initLevels(self):
        #initializes level data, place any new levels here
        self.level0 = {"enemyTypes": [BasicEnemy],
                "enemyFrequencies": [1],
                "enemyCaps": [8],
                "nextCriteria": 150,
                "multiplier": 1,
                "goToStoreBefore": False}
        
        self.level1 = {"enemyTypes": [BasicEnemy, SwerveEnemy],
                "enemyFrequencies": [.6,.4],
                "enemyCaps": [8,5],
                "nextCriteria": 500,
                "multiplier": 1,
                "goToStoreBefore": False}
        
        self.level2 = {"enemyTypes": [BasicEnemy, SwerveEnemy, HomingEnemy],
                "enemyFrequencies": [.25,.5,.25],
                "enemyCaps": [5,5,4],
                "nextCriteria": 500,
                "multiplier": 1,
                "goToStoreBefore": False}
        
        self.level3 = {"enemyTypes": [HomingEnemy],
                "enemyFrequencies": [1],
                "enemyCaps": [8],
                "nextCriteria": 750,
                "multiplier": 1.7,
                "goToStoreBefore": True}
        
        self.level4 = {"enemyTypes": [SwerveEnemy,HomingEnemy],
                "enemyFrequencies": [.3,.7],
                "enemyCaps": [5,5],
                "nextCriteria": 800,
                "multiplier": 1,
                "goToStoreBefore": False}
        
        self.level5 = {"enemyTypes": [SnakeBoss],
                "enemyFrequencies": [1],
                "enemyCaps": [1],
                "nextCriteria": 900,
                "multiplier": 1,
                "goToStoreBefore": True}
    
    
    def __init__(self, **kwargs):
        super(EnemyHandler, self).__init__(**kwargs)
        self.initLevels()
        self.enemyCounts = {"BasicEnemy":0, "SwerveEnemy":0, "HomingEnemy":0,
                            "SnakeBoss": 0}
        #keeps track of how many of each type of enemy is in the game
        self.levels = [self.level0,self.level1,self.level2,
                       self.level3, self.level4, self.level5]
        #used to access the levels as an index
    
    def addEnemy(self,enemy, dt=0):
        #adds an enemy as a child to the enemy handler and spawns in at
        # a random location to the right of the screem
        enemyWidget = enemy()
        self.add_widget(enemyWidget)
        yLocation = random.randint(0,self.parent.height)
        self.enemyCounts[enemy.name] += 1
        enemyWidget.createSelf(self.parent.right+25,yLocation)
        level = self.levels[self.parent.currentLevel]
        enemyWidget.applyMultiplier(level)
        
        
        
