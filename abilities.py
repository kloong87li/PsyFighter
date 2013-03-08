import kivy
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
from kivy.lang import Builder
from kivy.vector import Vector
from kivy.graphics import Line, Color
from kivy.clock import Clock

#This module contains the abilityHandler class and all ability classes
#each ability has a corresponding ability particle class


Builder.load_string("""

<AbilityHandler>
    abilityButton0: ability_button0
    abilityButton1: ability_button1
    
    #definitions for each ability toggle button
    #each button is bound to the setActiveAbility function and each button has
    #an ability property that is set in the original build function of the game
    #the ability property determines which ability it represents
    
    ToggleButton:
        state: "down"
        id: ability_button0
        ability: self.ability
        group: "abilities"
        width: root.width/7
        height: root.height/7
        center: (root.right - self.width), root.height - self.height/2
        on_press: root.setActiveAbility(self.ability, self)
        border:(0,0,0,0)
    
    ToggleButton:
        id: ability_button1
        ability: self.ability
        group: "abilities"
        width: root.width/7
        height: root.height/7
        center: (root.right - 2*self.width), root.height - self.height/2
        on_press: root.setActiveAbility(self.ability,self)
        border:(0,0,0,0)


<MissileParticle>
    canvas:
        Ellipse:
            source: "images/particles/missile.gif"
            size: self.size
            pos: self.pos
            
""")

class AbilityHandler(Widget):
    #class for the ability handler
    #serves as the central node for each ability that the hero uses
    #- is a child of the hero
    activeAbility = None
    particles = []
    #list of particles is used so that the update function can update
    #each particle on the screen
    
    def setAbilityButton(self,button,ability):
        #sets each ability button the the corresponding ability object
        #each ability is a child of the handler
        button.ability = ability
        button.background_normal = ability.button
        button.background_down = ability.button_pressed
        self.add_widget(ability)

    def setActiveAbility(self,ability, button=None):
        #changes the active ability when called by a button press
        if self.activeAbility == ability and button != None:
            button.state = "down"
        else:
            self.activeAbility = ability
    
    def use_activeAbility(self, touch):
        #called by the hero, when a touch is registered
        ability = self.activeAbility
        if self.parent.mana >= ability.manaCost:
            self.parent.mana -= ability.manaCost
            #subtracts the mana cost and tags the touch with "ability"
            #so that the touch cant be used for moving
            touch.ud["function"] = "ability"
            self.parent.usingAbility = True
            #calls the ability's activate function
            ability.activate(touch)
    
    def move_activeAbility(self,touch):
        #called when the touch moves
        #the function then subtracts the mana cost and calls the corresponding
        #ability function
        ability = self.activeAbility
        if self.parent.mana >= ability.move_manaCost:
            self.parent.mana -= ability.move_manaCost
            ability.moveActivate(touch)
        elif ability.over == False:
            ability.upActivate(touch)
            ability.over = True
    
    def up_activeAbility(self,touch):
        #called when touch is released,
        #then calls the ability's upActivate function
        ability = self.activeAbility
        if ability.over == False:
            ability.upActivate(touch)
    

class Ability(Widget):
    #Base class for each ability
    #Each ability has an activate function corresponding to each touch binding
    manaCost = 0
    move_manaCost = 0
    over = False
    def activate(self,touch): pass
    def moveActivate(self,touch): pass
    def upActivate(self,touch): pass
    def endAbility(self): pass
    def addParticle(self, particle):
        self.parent.particles.append(particle)
        self.add_widget(particle)

    
class Particle(Widget):
    #ability particle class, serves as graphical representation of abilities
    def createSelf(self,x,y): pass
    def update(self):
        #checks if particle is out of bounds
        left = self.right - self.width
        bottom = self.top - self.height
        rightBound = self.parent.parent.right
        topBound = self.parent.parent.top
        if ((self.right <= 0) or (left >= rightBound) or
            (self.top <= 0) or (bottom >= topBound)):
            self.destruct()
    
    def collisionCheck(self,other):
        #checks if particle collides with other widget
        if self.collide_widget(other):
            return True
        else:
            return False
        
    def destruct(self):
        #destroys self and removes self from parent
        self.parent.parent.particles.remove(self)
        self.parent.remove_widget(self)


class MissileAbility(Ability):
    #shoots a missile towards the tapped location
    multi = False
    manaCost = 4
    damage = 15
    button = "images/buttons/missileButton.gif"
    button_pressed = "images/buttons/missileButton_pressed.gif"
    
    def activate(self,touch):
        #called when the ability is first activated
        hero = self.parent.parent
        missile = MissileParticle()
        #creates a missile particle and sets its velocity to be aimed
        #at the touch location
        self.addParticle(missile)
        missile.createSelf(hero.center_x,hero.center_y)
        firstVelocity = self.setParticleVelocity(touch,missile,hero)
        if self.multi == True:
            #if upgrade has been purchased, launches 3 missiles
            self.activateMulti(firstVelocity)
    
    def activateMulti(self, firstVelocity):
        #to launch 3 missiles, this function rotates the original velocity
        # by -10, and 10 degrees and creates the new missiles
        hero = self.parent.parent
        for angle in xrange(-10,11,20):
            hero.mana -= self.manaCost/2.0
            missile = MissileParticle()
            self.addParticle(missile)
            missile.createSelf(hero.center_x,hero.center_y)
            missile.velocity = firstVelocity.rotate(angle)
        
    
    def setParticleVelocity(self,touch,particle,hero):
        #uses vectors to calculate the angle needed for the missile
        x = touch.x - hero.center_x
        y = touch.y - hero.center_y
        missileAngle = Vector(x,y).angle((1,0))
        particle.velocity = Vector(25,0).rotate(missileAngle)
        return particle.velocity
        
class MissileParticle(Particle):
    #class for the particles launched by the missile ability
    
    def createSelf(self,x,y):
        #creates self at the given location
        self.velocity = None
        self.width = self.parent.width/4.3
        self.height = self.parent.height/4.3
        self.center_x = x
        self.center_y = y

        
    def update(self):
        #when updated, simply adds velocity to position
        self.pos = self.velocity + self.pos
        super(MissileParticle,self).update()
        
    
class SlashAbility(Ability):
    #creates slashes when the touch is dragged
    rapid = False
    manaCost = 3.5
    move_manaCost = .15
    damage = 15
    button = "images/buttons/slashButton.gif"
    button_pressed = "images/buttons/slashButton_pressed.gif"
    slash = None
    
    def activate(self,touch):
        #activates the ability by adding a slash particle to the screen
        if self.slash != None:
            #ends any existing slashes if two touches are recieved
            self.endAbility()
        self.slash = SlashParticle()
        self.addParticle(self.slash)
        self.slash.createSelf(touch)
        if self.rapid == True:
            self.activateRapid(touch)
    
    
    def endAbility(self, dt=0):
        #ends the ability and removes the line particle
        if self.slash != None:
            for slash in self.children:
                self.parent.particles.remove(slash)
                self.remove_widget(slash)
                self.slash = None
    
    def upActivate(self,touch):
    #calls the endAbility function with a delay to create a swooshing effect
        Clock.schedule_once(self.endAbility, .05)
    
    def moveActivate(self,touch):
    #when moved, a new point is added to the line particle and another point
    #is scheduled to be removed
        if ("origin" in touch.ud and self.slash != None and
            self.slash.origin == touch.ud["origin"]):
            self.slash.line.points += [touch.x, touch.y]
            Clock.schedule_once(self.slash.removePoint, .1)
            if self.rapid == True:
                #if upgrade was purchased, activates the rapidslash
                hero = self.parent.parent
                hero.mana -= self.move_manaCost
                self.moveRapid(touch)

    
    def activateRapid(self,touch):
        #rapid slash creates 2 cross slashes
        self.crossSlash1 = SlashParticle()
        self.addParticle(self.crossSlash1)
        self.crossSlash1.createSelf(touch)
        self.crossSlash2 = SlashParticle()
        self.addParticle(self.crossSlash2)
        self.crossSlash2.createSelf(touch)
    
    def addCrossPoint(self,vectorChange,angle,crossSlash):
        #the cross slash points are determined by rotating a vector from
        #the origin point of the line toi the new point
        #this creates the effect of having 3 slashes at different angles
        rotatedVector = vectorChange.rotate(angle)
        firstPoint = [crossSlash.line.points[0], crossSlash.line.points[1]]
        newPoint = [firstPoint[0]+rotatedVector[0],
                    firstPoint[1]+rotatedVector[1]]
        crossSlash.line.points += newPoint
        Clock.schedule_once(crossSlash.removePoint,.1)
    
    def moveRapid(self,touch):
        #called when the touch is moved and the rapid upgrade was purchased
        points = self.slash.line.points
        vectorChange = Vector(touch.x-points[0],touch.y-points[1])
        (angle1, angle2) = (10,-10)
        self.addCrossPoint(vectorChange,angle1,self.crossSlash1)
        self.addCrossPoint(vectorChange,angle2,self.crossSlash2)


class SlashParticle(Particle):
    #line particle class that is created by the slash ability
    origin = None
    def createSelf(self,touch):
        #creates a line in the particle's canvas
        touch.ud["origin"] = (touch.x,touch.y)
        self.origin = (touch.x, touch.y)
        with self.canvas:
            Color(51.0/255, 0/255, 255.0/255)
            self.line = Line(points=(touch.x,touch.y), width=3)
    
    def collisionCheck(self,other):
        #checks if the other widget collides with any point on the line
        points = self.line.points
        length = len(self.line.points)
        if length <= 4: return False
        for i in xrange(0,length - 1,2):
            point = (points[i],points[i+1])
            if other.collide_point(*point):
                return True
        return False
            
    def destruct(self,dt=0):
        #the line doesnt get destroyed when it hits an enemy
        pass
    
    def removePoint(self, dt=0):
        #removes the first point in the line
        #this creates the effect of the line disappearing over time
        points = self.line.points
        if len(points) > 2:
            points = points[2::]
            self.line.points = points

                
    
