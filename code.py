from cmu_112_graphics import *
import os
import copy
import socket
import pickle
import time


class MyApp(App):

################################################################################
# The assets used for this game:
# Sprites for the Units - https://aekashics.itch.io/aekashics-librarium-librarium-static-batch-megapack
# Sprites for the bases(portals) - https://elthen.itch.io/2d-pixel-art-portal-sprites
# Sprites for the giants - https://darkpixel-kronovi.itch.io/mecha-golem-free?download
# Sprites for projectiles - https://www.gamedeveloperstudio.com/graphics/viewgraphic.php?item=1v4p793q186p7d9n0e
# Picture for background - https://www.freelancer.is/contest/Need-Background-for-D-Platformer-Game-We-will-work-for-more-after-the-contest-1372733-byentry-22150937?w=f&ngsw-bypass=
# Picture for the homepage - https://www.artstation.com/artwork/ZolX
################################################################################

# The network class is used to classify this as a client and for the Player v Player mode   
    class Network(object):
        # uses these parameters to connect
        def __init__ (self):
            self.header = 64   # used for decoding 
            self.port = 5050   # specific port
            self.server = '3.12.198.85'   # specific server
            self.addr = (self.server, self.port)
            self.format = 'utf-8'   # format of encryption
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # creates a socket object 
        
        # connects to server
        def connect(self):
            self.client.connect(self.addr)   #connects said socket
        
        # sends an object by relaying the legnth and then its pickled version
        def send(self,msg):
            message = pickle.dumps(msg)   
            messageLength = len(message)
            sendLength = str(messageLength).encode(self.format)
            sendLength += b' ' * (self.header - len(sendLength))
            self.client.send(sendLength)
            self.client.send(message)
        
        # procedure for continually pinging and receiving info from server
        def receive(self):
            message = 'REQUEST'
            message = pickle.dumps(message)
            messageLength = len(message)
            sendLength = str(messageLength).encode(self.format)
            sendLength += b' ' * (self.header - len(sendLength))
            self.client.send(sendLength)
            self.client.send(message)
            # this part is decoding and unpickling the reply from server
            replyLength = self.client.recv(self.header).decode(self.format)
            if replyLength:
                replyLength = int(replyLength)
                reply = pickle.loads(self.client.recv(replyLength))
                return(reply)

#Unit class contains subclasses of each type of unit which describes it
    class Units(object):
        def __init__(self,health,attack,movespd,range,cost):
            self.health = health   # current hp of the unit
            self.maxHealth = health # original hp of the unit
            self.attack = attack   # the damage per attack
            self.moveSpeed = movespd   # how fast the unit moves
            self.range = range   # how far the unit can attack
            self.cost = cost   # how much the unit will cost
            self.state = 'walk'   # what the unit is doing
            self.spriteCounter = 0  # for animation purposes
       
    class Base(Units):
        def __init__(self,absPos,relPos):
            self.health = 300
            self.maxHealth = 300   # maxHealth used for healthbar purposes
            self.absPos = absPos   # absPos and relPos is used for scrolling
            self.relPos = relPos
    
    # these giants are not normal units; they are the towers for defense 
    class Giant(Units):
        def __init__(self):
            self.age = 1
            self.attack = 2 * self.age
            self.range = 500
            self.state = 'idle'

        def action(self):
            if self.state == 'idle':
                return 2
            elif self.state == 'rangedFight':
                return 4
            elif self.state == 'meleeFight':
                return 6

# the different tuples represent which frame range is used    
    class Bat(Units):
        spritesheet = 0
        
        def __init__(self):
            super().__init__(8,1,40,0,200)
            self.type = 'light'
            
        def action(self):
            if self.state == 'walk':
                return (0,4)
            elif self.state == 'fight':
                return (38,42)

    class Owl(Units):
        spritesheet = 1
        def __init__(self): 
            super().__init__(7,2,25,200,250)
            self.projectile = 1   # number represents index of the sprite in self.projectiles
            self.type = 'light'
        
        def action(self):
            if self.state == 'walk':
                return (0,9)
            elif self.state == 'fight':
                return (9,21)
                    
    class Peacock(Units):
        spritesheet = 2
        def __init__(self):
            super().__init__(12,7,20,0,250)
            self.type = 'midweight'

        def action(self):
            if self.state == 'walk':
                return (27,36)
            elif self.state == 'fight':
                return (36,50)
                
    class Rat(Units):
        spritesheet = 3
        def __init__(self): 
            super().__init__(30,10,10,0,700)
            self.type = 'heavy'

        def action(self):
            if self.state == 'walk':
                return (9,18)
            elif self.state == 'fight':
                return (18,32)

    class Anubis(Units):
        spritesheet = 4
        def __init__(self): 
            super().__init__(15,2,20,0,200)
            self.type = 'midweight'

        def action(self):
            if self.state == 'walk':
                return (42,48)
            elif self.state == 'fight':
                return (2,6)
    
    class Knight(Units):
        spritesheet = 5
        def __init__(self): 
            super().__init__(12,2,30,250,300)
            self.projectile = 0
            self.type = 'midweight'

        def action(self):
            if self.state == 'walk':
                return (0,5)
            elif self.state == 'fight':
                return (11,13)
    
    class Slime(Units):
        spritesheet = 6
        def __init__(self): 
            super().__init__(30,6,15,0,250)
            self.type = 'heavy'

        def action(self):
            if self.state == 'walk':
                return (9,14)
            elif self.state == 'fight':
                return (21,26)

    class Spore(Units):
        spritesheet = 7
        def __init__(self): 
            super().__init__(50,8,45,0,800)
            self.type = 'light'

        def action(self):
            if self.state == 'walk':
                return (27,36)
            elif self.state == 'fight':
                return (0,5)
    
    class EarthWorm(Units):
        spritesheet = 8
        def __init__(self): 
            super().__init__(12,1,35,0,150)
            self.type = 'light'

        def action(self):
            if self.state == 'walk':
                return (18,27)
            elif self.state == 'fight':
                return (3,5)
    
    class Golem(Units):
        spritesheet = 9
        def __init__(self): 
            super().__init__(35,8,10,0,275)
            self.type = 'heavy'

        def action(self):
            if self.state == 'walk':
                return (6,11)
            elif self.state == 'fight':
                return (18,27)
    
    class Phoenix(Units):
        spritesheet = 10
        def __init__(self): 
            super().__init__(20,10,25,300,300)
            self.projectile = 4
            self.type = 'midweight'

        def action(self):
            if self.state == 'walk':
                return (27,36)
            elif self.state == 'fight':
                return (9,18)
    
    class WereWolf(Units):
        spritesheet = 11
        def __init__(self): 
            super().__init__(40,6,50,0,800)
            self.type = 'light'

        def action(self):
            if self.state == 'walk':
                return (0,6)
            elif self.state == 'fight':
                return (12,15)
    
    class DoppelSlime(Units):
        spritesheet = 12
        def __init__(self): 
            super().__init__(20,10,20,0,225)
            self.type = 'heavy'

        def action(self):
            if self.state == 'walk':
                return (15,21)
            elif self.state == 'fight':
                return (9,18)
    
    class Slayer(Units):
        spritesheet = 13
        def __init__(self): 
            super().__init__(23,6,30,0,300)
            self.projectile = 2
            self.type = 'light'

        def action(self):
            if self.state == 'walk':
                return (27,35)
            elif self.state == 'fight':
                return (11,15)
    
    class Whale(Units):
        spritesheet = 14
        def __init__(self): 
            super().__init__(50,6,20,0,375)
            self.type = 'heavy'

        def action(self):
            if self.state == 'walk':
                return (36,45)
            elif self.state == 'fight':
                return (2,7)

    class Wyvern(Units):
        spritesheet = 15
        def __init__(self): 
            super().__init__(50,20,30,275,800)
            self.projectile = 5
            self.type = 'midweight'

        def action(self):
            if self.state == 'walk':
                return (0,8)
            elif self.state == 'fight':
                return (36,42)

    class Angel(Units):
        spritesheet = 16
        def __init__(self): 
            super().__init__(30,9,25,150,250)
            self.type = 'midweight'

        def action(self):
            if self.state == 'walk':
                return (27,36)
            elif self.state == 'fight':
                return (0,9)
    
    class Boss(Units):
        spritesheet = 17
        def __init__(self): 
            super().__init__(37,6,15,0,300)
            self.type = 'heavy'

        def action(self):
            if self.state == 'walk':
                return (27,36)
            elif self.state == 'fight':
                return (0,7)
    
    class Overmind(Units):
        spritesheet = 18
        def __init__(self): 
            super().__init__(25,5,40,0,300)
            self.type = 'light'

        def action(self):
            if self.state == 'walk':
                return (5,13)
            elif self.state == 'fight':
                return (4,7)
    
    class Spike(Units):
        spritesheet = 19
        def __init__(self): 
            super().__init__(65,17,30,400,1000)
            self.projectile = 3
            self.type = 'light'

        def action(self):
            if self.state == 'walk':
                return (0,9)
            elif self.state == 'fight':
                return (9,15)

################################################################################
# These are the functions for game functionality 
################################################################################    
  
    def appStarted(self):  
        self.home = True   # homescreen checker
        self.instructions = False   # instruction page checker
        self.pvp = False   # pvp mode checker
        self.paused = False   
        self.gameOver = False
        self.timerDelay = 1
        self.sheets = []   # contains all the spritesheets of the units
        self.homeScreen = self.loadImage('Assets/Backgrounds/Homescreen.jpg')   # picture for the homescreen
        self.background = self.loadImage('Assets/Backgrounds/background.png')   # background for the game
        self.age = 0   # current age
        self.enemyAge = 0   
        self.exp = 0   # used for leveling up
        self.enemyExp = 0
        self.expCounter = 0   # used for timing purposes
        self.alive = []   # all the ally units that are alive right now
        self.enemyAlive = []
        self.sprites = []   # contains all the pictures of the frames of the units
        self.enemySprites = []
        self.spriteCounters = []   # counters count which frame the unit is on
        self.enemySpriteCounters = []
        self.absLocation = []   # abs and rel locations used for scrolling purposes
        self.relLocation= []
        self.enemyAbsLocation = []
        self.enemyRelLocation = []
        self.icons = []   # image of the unit in the button for the interface
        self.allyBase = self.Base(.05 * self.width, .05 * self.width)
        self.enemyBase = self.Base( 1.95 * self.width, 1.95 * self.width)
        self.baseSprites = []   # for the two bases
        self.baseCounter = 0   # samefunction as the sprite counters
        self.baseAnimate()   
        # list of the types of all the classes
        self.types = ['light','light','midweight','heavy','midweight','midweight', \
            'heavy','light','light','heavy','midweight','light','heavy','light','heavy','midweight','midweight', 'heavy', 'light', 'light']
        # list of the costs of all the classes
        self.costs = [200,250,250,700,200,300,250,800,150,275,300,800,225,300,375,800,250,300,300,1000]
        self.money = 600
        self.enemyMoney = 600
        self.enemyAICounter = 0   # used for timing how often the AI is called
        self.giants = []   # used for the defensive turrets
        self.giantSprites = []
        self.giantSpriteCounters = []
        self.giantSpawn()
        self.giantAnimate()
        self.projectiles = []   # keeping track of the different projectiles
        self.enemyProjectiles = []  
        self.projectileSprites = []
        self.enemyProjectileSprites = []   
        self.projectilesAttack = []
        self.enemyProjectilesAttack = []
        self.projectileAbsLocation = []
        self.projectileRelLocation = []
        self.enemyProjectileAbsLocation = []
        self.enemyProjectileRelLocation = []
        self.projectileTypes = []
        self.enemyProjectileTypes = []
        self.iconLoader()   # prepares some assets beforehand so it is smoother in-game
        self.net = None   # called upon and defined when PVP is requested
            
    # Loads and imports different images for the icons of the units and projectiles
    def iconLoader(self):
        path = 'Assets/Sprites'
        # goes through every folder and image within the folder for the icons
        for folder in os.listdir(path):
            images = os.listdir(path + '/' + folder)
            for spritesheets in images:
                sheet = self.loadImage(path + '/' + folder + '/' + spritesheets)
                self.sheets.append(sheet)
                icon = sheet.crop((0,0,512,512))
                icon = sprite = self.scaleImage(icon, (self.height / 700 + self.width / 1400) / 12)
                self.icons.append(icon)
        # this is for the projectiles which are added like the spritesheets to the
        # self.projectileSprites and self.enemyProjectileSprites lists
        path = 'Assets/Projectiles'
        for spritesheet in os.listdir(path):
            pic = self.loadImage (path + '/' + spritesheet)
            self.projectileSprites.append(pic)
            self.enemyProjectileSprites.append(pic.transpose(Image.FLIP_LEFT_RIGHT))

    def keyPressed(self,event):
        if event.key == 'p':
            self.paused = not(self.paused)
        elif event.key == 'b':   # to exit out of the instructions page
            if self.instructions:
                self.instructions = False
                self.home = True
        # remaining part is used for scrolling left and right
        # if a is pressed and your display window can still scroll left,
        # everything will have their relative position shift while their absolute
        # positions stays the same
        elif event.key == 'a' and (self.allyBase.relPos < (.1  * self.width)):
            self.allyBase.relPos += self.width * .1
            self.enemyBase.relPos += self.width * .1
            for pos in range(len(self.relLocation)):
                self.relLocation[pos] += self.width * .1
            for pos in range(len(self.enemyRelLocation)):
                self.enemyRelLocation[pos] += self.width * .1
            for pos in range(len(self.projectileRelLocation)):
                self.projectileRelLocation[pos] += self.width * .1
            for pos in range(len(self.enemyProjectileRelLocation)):
                self.enemyProjectileRelLocation[pos] += self.width * .1
        # if d is pressed and your display window can still scroll right
        elif event.key == 'd' and (self.enemyBase.relPos > (.95 * self.width)):
            self.allyBase.relPos -= self.width * .1
            self.enemyBase.relPos -= self.width * .1
            for pos in range(len(self.relLocation)):
                self.relLocation[pos] -= self.width * .1
            for pos in range(len(self.enemyRelLocation)):
                self.enemyRelLocation[pos] -= self.width * .1
            for pos in range(len(self.projectileRelLocation)):
                self.projectileRelLocation[pos] -= self.width * .1
            for pos in range(len(self.enemyProjectileRelLocation)):
                self.enemyProjectileRelLocation[pos] -= self.width * .1

    # function for summoning a new unit on our side                  
    def spawn(self,unit):
        self.alive.append(unit)
        self.spriteCounters.append(0)
        self.absLocation.append(self.allyBase.absPos)
        self.relLocation.append(self.allyBase.relPos)
        self.money -= unit.cost
        self.Animate()
    
    # same thing as above but for summoning for the opponent
    def enemySpawn(self,unit):
        self.enemyAlive.append(unit)
        self.enemySpriteCounters.append(0)
        self.enemyAbsLocation.append(self.enemyBase.absPos)
        self.enemyRelLocation.append(self.enemyBase.relPos)
        self.enemyMoney -= unit.cost
        self.enemyAnimate() 

    # same concept as above but written so it is only meant to be called once
    # (the giants are the turrets so they only need to be spawned once each)
    def giantSpawn(self):
        giant = 'giant'
        giant = self.Giant()
        self.giants.append(giant)
        self.giantSpriteCounters.append(0)
        enemyGiant = 'enemyGiant' 
        enemyGiant = self.Giant()
        self.giants.append(enemyGiant)
        self.giantSpriteCounters.append(0)

    def mousePressed(self,event):
        # the different buttons on the homepage
        if self.home:
            # p v ai button
            if ((.35 * self.width) <= event.x <= (.65 * self.width)) and ((.35 * self.height) <= event.y <= (.45 * self.height)):
                self.home = False
            # p v p button
            elif ((.35 * self.width) <= event.x <= (.65 * self.width)) and ((.55 * self.height) <= event.y <= (.65 * self.height)):
                self.home = False
                self.pvp = True
                self.net = self.Network()   # defines self.net here as an instance
                self.net.connect()   # initiates connection
            # instruction button
            elif ((.35 * self.width) <= event.x <= (.65 * self.width)) and ((.75 * self.height) <= event.y <= (.85 * self.height)):
                self.home = False
                self.instructions = True
            # if in-game (either p v p or p v ai)
        if not(self.home) and not(self.instructions) and not(self.gameOver):
            if (.85 * self.height) <= event.y <= (.99 * self.height):
                #leftmost button
                if (.01 * self.width) <= event.x <= (.09 * self.width):
                    if self.age == 0 and self.money >= self.costs[0]:
                        newBat = 'bat' + str(len(self.sprites))   # this is so we can differentiate copies of an unit
                        newBat = self.Bat()
                        self.spawn(newBat)
                    elif self.age == 1 and self.money >= self.costs[4]:
                        newAnubis = 'anubis'+ str(len(self.sprites))
                        newAnubis = self.Anubis()
                        self.spawn(newAnubis)
                    elif self.age == 2 and self.money >= self.costs[8]:
                        newEarthworm = 'earthworm'+ str(len(self.sprites))
                        newEarthworm = self.EarthWorm()
                        self.spawn(newEarthworm)
                    elif self.age == 3 and self.money >= self.costs[12]:
                        newDoppelSlime = 'doppelslime'+ str(len(self.sprites))
                        newDoppelSlime = self.DoppelSlime()
                        self.spawn(newDoppelSlime)
                    elif self.age == 4 and self.money >= self.costs[16]:
                        newAngel = 'angel'+ str(len(self.sprites))
                        newAngel = self.Angel()
                        self.spawn(newAngel)
                # second button
                elif (.12 * self.width) <= event.x <= (.2 * self.width):
                    if self.age == 0 and self.money >= self.costs[1]:
                        newOwl = 'owl' + str(len(self.sprites))
                        newOwl = self.Owl()
                        self.spawn(newOwl)
                    elif self.age == 1 and self.money >= self.costs[5]:
                        newKnight = 'knight'+ str(len(self.sprites))
                        newKnight = self.Knight()
                        self.spawn(newKnight)
                    elif self.age == 2 and self.money >= self.costs[9]:
                        newGolem = 'golem'+ str(len(self.sprites))
                        newGolem = self.Golem()
                        self.spawn(newGolem)
                    elif self.age == 3 and self.money >= self.costs[13]:
                        newSlayer = 'slayer'+ str(len(self.sprites))
                        newSlayer = self.Slayer()
                        self.spawn(newSlayer)
                    elif self.age == 4 and self.money >= self.costs[17]:
                        newBoss = 'boss'+ str(len(self.sprites))
                        newBoss = self.Boss()
                        self.spawn(newBoss)
                # third button
                elif (.23 * self.width) <= event.x <= (.31 * self.width):
                    if self.age == 0 and self.money >= self.costs[2]:
                        newPeacock = 'peacock' + str(len(self.sprites))
                        newPeacock = self.Peacock()
                        self.spawn(newPeacock)
                    elif self.age == 1 and self.money >= self.costs[6]:
                        newSlime = 'slime'+ str(len(self.sprites))
                        newSlime = self.Slime()
                        self.spawn(newSlime)
                    elif self.age == 2 and self.money >= self.costs[10]:
                        newPhoenix = 'phoenix'+ str(len(self.sprites))
                        newPhoenix = self.Phoenix()
                        self.spawn(newPhoenix)
                    elif self.age == 3 and self.money >= self.costs[14]:
                        newWhale = 'whale'+ str(len(self.sprites))
                        newWhale = self.Whale()
                        self.spawn(newWhale)
                    elif self.age == 4 and self.money >= self.costs[18]:
                        newOvermind = 'overmind'+ str(len(self.sprites))
                        newOvermind = self.Overmind()
                        self.spawn(newOvermind)
                # fourth button
                elif (.34 * self.width) <= event.x <= (.42 * self.width):
                    if self.age == 0 and self.money >= self.costs[3]:
                        newRat = 'rat' + str(len(self.sprites))
                        newRat = self.Rat()
                        self.spawn(newRat)
                    elif self.age == 1 and self.money >= self.costs[7]:
                        newSpore = 'spore ' + str(len(self.sprites))
                        newSpore = self.Spore()
                        self.spawn(newSpore)
                    elif self.age == 2 and self.money >= self.costs[11]:
                        newWerewolf = 'werewolf'+ str(len(self.sprites))
                        newWerewolf = self.WereWolf()
                        self.spawn(newWerewolf)
                    elif self.age == 3 and self.money >= self.costs[15]:
                        newWyvern = 'wyvern'+ str(len(self.sprites))
                        newWyvern = self.Wyvern()
                        self.spawn(newWyvern)
                    elif self.age == 4 and self.money >= self.costs[19]:
                        newSpike = 'spike'+ str(len(self.sprites))
                        newSpike = self.Spike()
                        self.spawn(newSpike)

    # function creates the sprites for newly summoned units and updates the old sprites if they change action
    # modified version of the sprite animations at https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html
    def Animate(self):
        for count in range(len(self.alive)):
            unit = self.alive[count]
            pic = self.sheets[unit.spritesheet]
            (start,end) = unit.action()   # unit.action returns the specific frames of the spritesheet to be used
            unitSprite = []
            for i in range(start,end):
                sprite = pic.crop((0 + 512 * (i % 9) , 0 + 512 * (i // 9),\
                        512 + 512 * (i % 9), 512 + 512 * (i //9 ) ))
                sprite = self.scaleImage(sprite, (self.height / 700 + self.width / 1400) / 6)
                sprite = sprite.transpose(Image.FLIP_LEFT_RIGHT)
                unitSprite.append(sprite)
            if count >= len(self.sprites):   
                self.sprites.append(unitSprite)   # if new unit, puts in the frames to be used
            else:
                self.sprites[count] = unitSprite   # replaces the current frames to draw from with new ones

    # essentially the same as above function but for the enemy's version of their 
    # lists, also notice that there is no transposing
    def enemyAnimate(self):
        for count in range(len(self.enemyAlive)):
            unit = self.enemyAlive[count]
            pic = self.sheets[unit.spritesheet]
            (start,end) = unit.action()
            unitSprite = []
            for i in range(start,end):
                sprite = pic.crop((0 + 512 * (i % 9) , 0 + 512 * (i // 9),\
                        512 + 512 * (i % 9), 512 + 512 * (i //9 ) ))
                sprite = self.scaleImage(sprite, (self.height / 700 + self.width / 1400) / 6)
                unitSprite.append(sprite)
            if count >= len(self.enemySprites):
                self.enemySprites.append(unitSprite)
            else:
                self.enemySprites[count] = unitSprite
    
    # same thing but for the two giants, only meant to be called once at the start
    def giantAnimate(self):
        giantPic = self.loadImage('Assets/Sprites/Defense/Giant.png')
        giantProjectile = self.loadImage('Assets/Sprites/Defense/Giant_Projectile.png')
        giantProjectile = self.scaleImage(giantProjectile, 3)
        self.giantSprites.append(giantProjectile)   #projectiles of both giants added
        self.giantSprites.append(giantProjectile.transpose(Image.FLIP_LEFT_RIGHT))
        enemySprites = []
        sprites=[]
        for i in range(4):
            sprite = giantPic.crop((0 + 100 * i  , 0, 100 + 100 * i , 100))
            sprite = self.scaleImage(sprite, 3)
            enemySprite = sprite.transpose(Image.FLIP_LEFT_RIGHT)   # transposing it for one side
            sprites.append(sprite)
            enemySprites.append(enemySprite)
        self.giantSprites.append(sprites)   # idle frames of both giants added
        self.giantSprites.append(enemySprites)
        enemySprites = []
        sprites = []
        for i in range(9):
            sprite = giantPic.crop((0 + 100 * i  , 200, 100 + 100 * i , 300))
            sprite = self.scaleImage(sprite, 3)
            enemySprite = sprite.transpose(Image.FLIP_LEFT_RIGHT)
            sprites.append(sprite)
            enemySprites.append(enemySprite)
        self.giantSprites.append(sprites + sprites[::-1])   # ranged attack frames added
        self.giantSprites.append(enemySprites + enemySprites[::-1])
        enemySprites = []
        sprites = []
        for i in range(7):
            sprite = giantPic.crop((0 + 100 * i  , 400, 100 + 100 * i , 500))
            sprite = self.scaleImage(sprite, 3)
            enemySprite = sprite.transpose(Image.FLIP_LEFT_RIGHT)
            sprites.append(sprite)
            enemySprites.append(enemySprite)   
        self.giantSprites.append(sprites)   #melee attack frames added
        self.giantSprites.append(enemySprites)
    
    #similar to animate functions above but for the two bases, only called once
    def baseAnimate(self):
        # ally base
        pic = self.loadImage("Assets/Backgrounds/allyPortal.png") 
        allyBaseSprites = []
        for i in range(4):
            sprite = pic.crop((0 + 512 * i  , 0 + 512 * (i//3), 512 + 512 * i , 512 + 512 * (i//3) ))
            sprite = self.scaleImage(sprite, (self.height / 700 + self.width / 1400) / 4) 
            allyBaseSprites.append(sprite)   
        self.baseSprites.append(allyBaseSprites)  
        # enemy base  
        pic2 = self.loadImage("Assets/Backgrounds/enemyPortal.png")     
        enemyBaseSprites = []   
        for i in range(4):
            sprite = pic2.crop((0 + 512 * i  , 0 + 512 * (i//3), 512 + 512 * i , 512 + 512 * (i//3) ))
            sprite = self.scaleImage(sprite, (self.height / 700 + self.width / 1400) / 4)  
            sprite = sprite.transpose(Image.FLIP_LEFT_RIGHT) 
            enemyBaseSprites.append(sprite)
        self.baseSprites.append(enemyBaseSprites)

    # distance between two units
    def dist(self,x1,x2):
        return ( (x1 - 512 * ((self.height / 700 + self.width / 1400) / 12)) - \
            (x2 + 512 * ((self.height / 700 + self.width / 1400) / 12))   )

    # controls the movement of units and changes their actions 
    def movement(self):
        for unit in range(len(self.alive)):
            # animates them (moves their frame to the next)
            self.spriteCounters[unit] = (1 + self.spriteCounters[unit]) % len(self.sprites[unit])
            if unit == 0:
                if (len(self.enemyAlive) > 0):
                    # if the enemy is within range of attack, change from 'walk' to 'fight'
                    if self.dist(self.enemyAbsLocation[0], self.absLocation[0]) <= self.alive[0].range:
                        if self.alive[0].state == 'walk':
                            self.alive[0].state = 'fight'
                            self.spriteCounters[0] = 0
                            self.Animate()
                    else:
                    # if no enemy is not within attack range and you are in 'fight' state
                        if self.alive[0].state == 'fight':
                            self.alive[0].state = 'walk'
                            self.spriteCounters[0] = 0
                            self.Animate()
                    # if there is still room to move forward, move
                    if (self.dist(self.enemyAbsLocation[0], self.absLocation[0]) >= 0):
                        self.absLocation[0] += self.alive[0].moveSpeed
                        self.relLocation[0] += self.alive[0].moveSpeed
                # if there are no enemy units and room to move, make sure you are in 
                # 'walk' state and then move
                elif (self.dist(self.enemyBase.absPos, self.absLocation[0]) > 0):
                    if self.alive[0].state != 'walk':
                        self.alive[0].state = 'walk'
                        self.spriteCounters[unit] = 0
                        self.Animate()
                    self.absLocation[0] += self.alive[0].moveSpeed
                    self.relLocation[0] += self.alive[0].moveSpeed
                # if the base is within attack range, change to 'fight' state
                elif (self.dist(self.enemyBase.absPos, self.absLocation[0]) <= self.alive[0].range):
                    if self.alive[0].state != 'fight':
                        self.alive[0].state = 'fight'
                        self.spriteCounters[unit] = 0
                        self.Animate()
            else:   # if you are not the first unit anymore
                # same thing as above for when enemies are within attack range (basically only ranged)
                if (len(self.enemyAlive) > 0):
                    if (self.dist(self.enemyAbsLocation[0], self.absLocation[unit]) <= self.alive[unit].range):
                        if self.alive[unit].state == 'walk':
                            self.alive[unit].state = 'fight'
                            self.spriteCounters[unit] = 0
                            self.Animate()
                    # move while you attack if you can, since you are ranged. This also avoids collisions
                    if (self.dist(self.absLocation[unit-1],self.absLocation[unit]) > self.alive[unit].moveSpeed):
                        self.absLocation[unit] += self.alive[unit].moveSpeed
                        self.relLocation[unit] += self.alive[unit].moveSpeed
                else:   # if no enemies are alive 
                    # if enemy base is within attack range, change to 'fight' state
                    if (self.dist(self.enemyBase.absPos, self.absLocation[unit]) <= self.alive[unit].range):
                        if self.alive[unit].state != 'fight':
                            self.alive[unit].state = 'fight'
                            self.spriteCounters[unit] = 0
                            self.Animate()
                    # if not, just walk state and move if you don't collide
                    elif self.alive[unit].state == 'fight':
                        self.alive[unit].state = 'walk'
                        self.spriteCounters[unit] = 0
                        self.Animate()
                    if (self.dist(self.absLocation[unit-1],self.absLocation[unit]) > self.alive[unit].moveSpeed):
                        self.absLocation[unit] += self.alive[unit].moveSpeed
                        self.relLocation[unit] += self.alive[unit].moveSpeed
    
    # same thing as above but for enemies
    def enemyMovement(self):
        for unit in range(len(self.enemyAlive)):
            self.enemySpriteCounters[unit] = (1 + self.enemySpriteCounters[unit]) % len(self.enemySprites[unit])
            if unit == 0: 
                if (len(self.alive) > 0):
                    if (self.dist(self.enemyAbsLocation[0], self.absLocation[0]) <= self.enemyAlive[0].range):
                        if self.enemyAlive[0].state == 'walk':
                            self.enemyAlive[0].state = 'fight'
                            self.enemySpriteCounters[0] = 0
                            self.enemyAnimate()
                    else:
                        if self.enemyAlive[0].state == 'fight':
                            self.enemyAlive[0].state = 'walk'
                            self.enemySpriteCounters[0] = 0
                            self.Animate()
                        if (self.dist(self.enemyAbsLocation[0], self.absLocation[0],) >= 0):
                            self.enemyAbsLocation[0] -= self.enemyAlive[0].moveSpeed
                            self.enemyRelLocation[0] -= self.enemyAlive[0].moveSpeed
                elif (self.dist(self.enemyAbsLocation[0], self.allyBase.absPos)) > 0:
                    if self.enemyAlive[0].state != 'walk':
                        self.enemyAlive[0].state = 'walk'
                        self.enemySpriteCounters[unit] = 0
                        self.enemyAnimate()
                    self.enemyAbsLocation[0] -= self.enemyAlive[0].moveSpeed
                    self.enemyRelLocation[0] -= self.enemyAlive[0].moveSpeed
                elif (self.dist(self.enemyAbsLocation[0], self.allyBase.absPos)) <= self.enemyAlive[0].range:
                    if self.enemyAlive[0].state != 'fight':
                        self.enemyAlive[0].state = 'fight'
                        self.enemySpriteCounters[unit] = 0
                        self.enemyAnimate()
            else:
                if (len(self.alive) > 0):
                    if (self.dist(self.enemyAbsLocation[unit], self.absLocation[0]) <= self.enemyAlive[unit].range):
                        if self.enemyAlive[unit].state == 'walk':
                            self.enemyAlive[unit].state = 'fight'
                            self.enemySpriteCounters[unit] = 0
                            self.enemyAnimate()
                    if (self.dist(self.enemyAbsLocation[unit],self.enemyAbsLocation[unit-1]) > self.enemyAlive[unit].moveSpeed):
                        self.enemyAbsLocation[unit] -= self.enemyAlive[unit].moveSpeed
                        self.enemyRelLocation[unit] -= self.enemyAlive[unit].moveSpeed
                else:
                    if (self.dist(self.enemyAbsLocation[unit], self.allyBase.absPos)) <= self.enemyAlive[unit].range:
                        if self.enemyAlive[unit].state != 'fight':
                            self.enemyAlive[unit].state = 'fight'
                            self.enemySpriteCounters[unit] = 0
                            self.enemyAnimate()
                    elif self.enemyAlive[unit].state == 'fight':
                            self.enemyAlive[unit].state = 'walk'
                            self.enemySpriteCounters[unit] = 0
                            self.enemyAnimate() 
                    if (self.dist(self.enemyAbsLocation[unit],self.enemyAbsLocation[unit-1]) > self.enemyAlive[unit].moveSpeed):
                        self.enemyAbsLocation[unit] -= self.enemyAlive[unit].moveSpeed
                        self.enemyRelLocation[unit] -= self.enemyAlive[unit].moveSpeed

    # same function as functions above but for the giant
    def giantAction(self):
        giant = self.giants[0]
        # animates the giant
        self.giantSpriteCounters[0] = (1 + self.giantSpriteCounters[0]) % len(self.giantSprites[giant.action()])
        if (len(self.enemyAlive) > 0):
            # if enemy is within attack range , change to 'rangedFight' state
            if 0 < self.dist(self.enemyAbsLocation[0], self.allyBase.absPos) <= giant.range:
                if giant.state != 'rangedFight':
                    giant.state = 'rangedFight'
                    self.giantSpriteCounters[0] = 0
            # if they are right in front of base, change to 'meleeFight' state
            elif self.dist(self.enemyAbsLocation[0], self.allyBase.absPos) <= 0:
                if giant.state != 'meleeFight':
                    giant.state = 'meleeFight'
                    self.giantSpriteCounters[0] = 0
            else:
                if giant.state != 'idle':
                    giant.state = 'idle'
                    self.giantSpriteCounters[0] = 0
        # if no enemies are left, go 'idle' if not already
        elif giant.state != 'idle':
                giant.state = 'idle'
                self.giantSpriteCounters[0] = 0
    
    # same thing as above but for enemy giant
    def enemyGiantAction(self):
        giant = self.giants[1]
        self.giantSpriteCounters[1] = (1 + self.giantSpriteCounters[1]) % len(self.giantSprites[giant.action()+ 1])
        if (len(self.alive) > 0):
            if 0 < self.dist(self.enemyBase.absPos, self.absLocation[0]) <= giant.range:
                if giant.state != 'rangedFight':
                    giant.state = 'rangedFight'
                    self.giantSpriteCounters[1] = 0
            elif self.dist(self.enemyBase.absPos, self.absLocation[0]) <= 0:
                if giant.state != 'meleeFight':
                    giant.state = 'meleeFight'
                    self.giantSpriteCounters[1] = 0
            else:
                if giant.state != 'idle':
                    giant.state = 'idle'
                    self.giantSpriteCounters[1] = 0
        elif giant.state != 'idle':
            giant.state = 'idle'
            self.giantSpriteCounters[1] = 0

    # combat system 
    def fighting(self):
        #ally units
        for unit in range(len(self.alive)):
            #if you are in 'fight' state and is a melee...
            if self.alive[unit].state == 'fight' and self.alive[unit].range == 0:   
                if (self.spriteCounters[unit] == len(self.sprites[unit]) -1) and len(self.enemyAlive) > 0:   # end of animation frames
                    # take away the enemy hp, damage calc function accounts for type effctiveness
                    self.enemyAlive[0].health -= self.alive[unit].attack * self.damageCalc(self.alive[unit].type, self.enemyAlive[0].type)   
                # if you are hitting the enemy base
                elif (self.spriteCounters[unit] == len(self.sprites[unit]) -1) and self.dist(self.enemyBase.absPos, self.absLocation[unit]) <= 0:
                    self.enemyBase.health -= self.alive[unit].attack
            #if you are in 'fight' state and is a ranged...
            elif self.alive[unit].state == 'fight' and self.alive[unit].range > 0:
                if (self.spriteCounters[unit] == len(self.sprites[unit]) // 2) and len(self.enemyAlive) > 0:   # middle of animation frames
                    # spawn a projectile with your characteristics
                    self.projectiles.append(self.projectileSprites[self.alive[unit].projectile])
                    self.projectilesAttack.append(self.alive[unit].attack)
                    self.projectileAbsLocation.append(self.absLocation[unit])
                    self.projectileRelLocation.append(self.relLocation[unit])
                    self.projectileTypes.append(self.alive[unit].type)
            # if you are hitting enemy base
                elif (self.spriteCounters[unit] == len(self.sprites[unit]) // 2) and self.dist(self.enemyBase.absPos, self.absLocation[unit]) <= self.alive[unit].range:
                    self.projectiles.append(self.projectileSprites[self.alive[unit].projectile])
                    self.projectilesAttack.append(self.alive[unit].attack)
                    self.projectileAbsLocation.append(self.absLocation[unit])
                    self.projectileRelLocation.append(self.relLocation[unit])
                    self.projectileTypes.append(self.alive[unit].type)
        # same thing but for enemy units
        for unit in range(len(self.enemyAlive)):
            if self.enemyAlive[unit].state == 'fight' and self.enemyAlive[unit].range == 0:
                if (self.enemySpriteCounters[unit] == len(self.enemySprites[unit])-1) and len(self.alive) > 0:
                        self.alive[0].health -= self.enemyAlive[unit].attack * self.damageCalc(self.enemyAlive[unit].type, self.alive[0].type)
                elif (self.enemySpriteCounters[unit] == len(self.enemySprites[unit])-1) and self.dist(self.enemyAbsLocation[unit],self.allyBase.absPos) <= 0:
                        self.allyBase.health -= self.enemyAlive[unit].attack
            elif self.enemyAlive[unit].state == 'fight' and self.enemyAlive[unit].range > 0:
                if (self.enemySpriteCounters[unit] == len(self.enemySprites[unit]) // 2) and len(self.enemyAlive) > 0:
                    self.enemyProjectiles.append(self.enemyProjectileSprites[self.enemyAlive[unit].projectile])
                    self.enemyProjectilesAttack.append(self.enemyAlive[unit].attack)
                    self.enemyProjectileAbsLocation.append(self.enemyAbsLocation[unit])
                    self.enemyProjectileRelLocation.append(self.enemyRelLocation[unit])
                    self.enemyProjectileTypes.append(self.enemyAlive[unit].type)
                elif (self.enemySpriteCounters[unit] == len(self.enemySprites[unit]) // 2) and self.dist(self.enemyAbsLocation[unit],self.allyBase.absPos) <= self.enemyAlive[unit].range:
                    self.enemyProjectiles.append(self.enemyProjectileSprites[self.enemyAlive[unit].projectile])
                    self.enemyProjectilesAttack.append(self.enemyAlive[unit].attack)
                    self.enemyProjectileAbsLocation.append(self.enemyAbsLocation[unit])
                    self.enemyProjectileRelLocation.append(self.enemyRelLocation[unit])
                    self.enemyProjectileTypes.append(self.enemyAlive[unit].type)

    # combat system for the giants, 
    def giantFight(self):
        giant = self.giants[0]
        # if melee state, hit them end of frames
        if giant.state == 'meleeFight':
                if (self.giantSpriteCounters[0] == len(self.giantSprites[giant.action()]) -1) and len(self.enemyAlive) > 0:
                    self.enemyAlive[0].health -= giant.attack
        # if ranged state, spawn projectile middle of frame
        elif giant.state == 'rangedFight':
                if (self.giantSpriteCounters[0] == len(self.giantSprites[giant.action()]) //2) and len(self.enemyAlive) > 0:
                    self.projectiles.append(self.giantSprites[0])
                    self.projectilesAttack.append(giant.attack)
                    self.projectileAbsLocation.append(self.allyBase.absPos + 50)
                    self.projectileRelLocation.append(self.allyBase.relPos + 50)
                    self.projectileTypes.append("heavy")
        # same thing but for enemy giant
        enemyGiant = self.giants[1]
        if enemyGiant.state == 'meleeFight':
                if (self.giantSpriteCounters[1] == len(self.giantSprites[enemyGiant.action()]) -1) and len(self.alive) > 0:
                    self.alive[0].health -= enemyGiant.attack
        elif enemyGiant.state == 'rangedFight':
                if (self.giantSpriteCounters[1] == len(self.giantSprites[enemyGiant.action()]) //2) and len(self.alive) > 0:
                    self.enemyProjectiles.append(self.giantSprites[1])
                    self.enemyProjectilesAttack.append(enemyGiant.attack)
                    self.enemyProjectileAbsLocation.append(self.enemyBase.absPos - 50)
                    self.enemyProjectileRelLocation.append(self.enemyBase.relPos - 50)
                    self.enemyProjectileTypes.append("heavy")

    # damage calculation for the different types, inspired by Pokemon!
    def damageCalc(self,unit1,unit2):
        if unit1 == 'light' and unit2 == 'light':
            return 1
        elif unit1 == 'midweight' and unit2 == 'light':
            return 0.5
        elif unit1 == 'heavy' and unit2 == 'light':
            return 1.5
        elif unit1 == 'light' and unit2 == 'midweight':
            return 1.5
        elif unit1 == 'midweight' and unit2 == 'midweight':
            return 1
        elif unit1 == 'heavy' and unit2 == 'midweight':
            return 0.5
        if unit1 == 'light' and unit2 == 'heavy':
            return 0.5
        elif unit1 == 'midweight' and unit2 == 'heavy':
            return 1.5
        else:
            return 1

    # controls the movement of projectiles and their collision mechanics
    def projectileMovement(self):
        index = 0
        while index < len(self.projectiles):
            # if a projectile collides
            if len(self.enemyAlive) > 0 and self.dist(self.enemyAbsLocation[0],self.projectileAbsLocation[index]) < 25:
                self.enemyAlive[0].health -= self.projectilesAttack[index] * self.damageCalc(self.projectileTypes[index], self.enemyAlive[0].type)
                self.projectilesAttack.pop(index)
                self.projectileAbsLocation.pop(index)
                self.projectileRelLocation.pop(index)
                self.projectileTypes.pop(index)
                self.projectiles.pop(index)
            # if an extra step in movement will result in collision anyways
            elif self.dist(self.enemyBase.absPos,self.projectileAbsLocation[index]) < 25:
                self.enemyBase.health-= self.projectilesAttack[index] 
                self.projectilesAttack.pop(index)
                self.projectileAbsLocation.pop(index)
                self.projectileRelLocation.pop(index)
                self.projectileTypes.pop(index)
                self.projectiles.pop(index)
            else:
                self.projectileAbsLocation[index] += 25
                self.projectileRelLocation[index] += 25
                index += 1
        # same thing but for enemy projectiles
        index = 0
        while index < len(self.enemyProjectiles):
            if len(self.alive) > 0 and self.dist(self.enemyProjectileAbsLocation[index],self.absLocation[0]) < 25:
                self.alive[0].health -= self.enemyProjectilesAttack[index] * self.damageCalc(self.enemyProjectileTypes[index],self.alive[0].type)
                self.enemyProjectilesAttack.pop(index)
                self.enemyProjectileAbsLocation.pop(index)
                self.enemyProjectileRelLocation.pop(index)
                self.enemyProjectileTypes.pop(index)
                self.enemyProjectiles.pop(index)
            elif self.dist(self.enemyProjectileAbsLocation[index],self.allyBase.absPos) < 25:
                self.allyBase.health -= self.enemyProjectilesAttack[index] 
                self.enemyProjectilesAttack.pop(index)
                self.enemyProjectileAbsLocation.pop(index)
                self.enemyProjectileRelLocation.pop(index)
                self.enemyProjectileTypes.pop(index)
                self.enemyProjectiles.pop(index)
            else:
                self.enemyProjectileAbsLocation[index] -= 25
                self.enemyProjectileRelLocation[index] -= 25
                index += 1

    # death of units
    def death(self):
        if len(self.alive) > 0 and self.alive[0].health <= 0:
            self.enemyExp += self.alive[0].cost
            self.alive.pop(0)
            self.sprites.pop(0)
            self.spriteCounters.pop(0)
            self.absLocation.pop(0)
            self.relLocation.pop(0)      
        if len(self.enemyAlive) > 0 and self.enemyAlive[0].health <= 0:
            self.exp += self.enemyAlive[0].cost
            self.enemyAlive.pop(0)
            self.enemySprites.pop(0)
            self.enemySpriteCounters.pop(0)
            self.enemyAbsLocation.pop(0)
            self.enemyRelLocation.pop(0)
            
    # tree of if statements for enemy AI to decide what to put out
    def enemyAI(self):
        # only sends out units every so often
        self.enemyAICounter += 1
        if self.enemyAICounter % 35 == 0:
            # counts what types of units the enemy has most of
            if (len(self.enemyAlive) < 5):
                light = 0
                medium = 0
                heavy = 0
                for unit in self.alive: 
                    if unit.type == 'light':
                        light += 1
                    elif unit.type == 'mediumweight':
                        medium += 1
                    else:
                        heavy += 1
                # the following are different, specific conditions that may be met
                # if no condition is met, the ai will choose to save money until needed
                if self.enemyAge == 0:
                    if len(self.alive) == 0 and len(self.enemyAlive) < 1:
                        if self.enemyMoney >= self.costs[2]:
                            newPeacock = 'peacock'+ str(len(self.enemySprites))
                            newPeacock = self.Peacock()
                            self.enemySpawn(newPeacock)
                        elif self.enemyMoney >= self.costs[0]:
                            newBat = 'bat' + str(len(self.enemySprites))
                            newBat = self.Bat()
                            self.enemySpawn(newBat)
                    elif len(self.alive) > 0:
                        if max(light,medium,heavy) == medium:
                            if (self.alive[0].type == 'medium' or self.dist(self.enemyBase.absPos, self.absLocation[0]) <= 500) and self.enemyMoney >= self.costs[0]:
                                newBat = 'bat' + str(len(self.enemySprites))
                                newBat = self.Bat()
                                self.enemySpawn(newBat)
                            elif self.enemyMoney >= self.costs[1]:
                                newOwl = 'owl'+ str(len(self.enemySprites))
                                newOwl = self.Owl() 
                                self.enemySpawn(newOwl)
                        elif max(light,medium,heavy) == light and self.enemyMoney >= self.costs[1]:
                            newRat = 'rat'+ str(len(self.sprites))
                            newRat = self.Rat()
                            self.enemySpawn(newRat) 
                        elif self.alive[0].type == 'heavy' and self.enemyMoney >= self.costs[2]:
                            newPeacock = 'peacock'+ str(len(self.enemySprites))
                            newPeacock = self.Peacock()
                            self.enemySpawn(newPeacock)
                        elif self.dist(self.enemyBase.absPos, self.absLocation[0]) <= 500 and self.enemyMoney >= self.costs[0]:
                            if self.enemyMoney >= self.costs[3]:
                                newRat = 'rat'+ str(len(self.sprites))
                                newRat = self.Rat()
                                self.enemySpawn(newRat) 
                            elif self.enemyMoney >= self.costs[2]:
                                newPeacock = 'peacock'+ str(len(self.enemySprites))
                                newPeacock = self.Peacock()
                                self.enemySpawn(newPeacock)
                            elif self.enemyMoney >= self.costs[1]:
                                newOwl = 'owl'+ str(len(self.enemySprites))
                                newOwl = self.Owl() 
                                self.enemySpawn(newOwl)
                            else:
                                newBat = 'bat' + str(len(self.enemySprites))
                                newBat = self.Bat()
                                self.enemySpawn(newBat)
                elif self.enemyAge == 1:
                    if len(self.alive) == 0 and len(self.enemyAlive) < 1:
                        if self.enemyMoney >= self.costs[6]:
                            newSlime = 'slime'+ str(len(self.sprites))
                            newSlime = self.Slime()
                            self.enemySpawn(newSlime)
                        elif self.enemyMoney >= self.costs[4]:
                            newAnubis = 'anubis'+ str(len(self.sprites))
                            newAnubis = self.Anubis()
                            self.enemySpawn(newAnubis)
                    elif len(self.alive) > 0:
                        if max(light,medium,heavy) == medium and self.enemyMoney >= self.costs[7]:
                            newSpore = 'spore ' + str(len(self.sprites))
                            newSpore = self.Spore()
                            self.enemySpawn(newSpore)
                        elif max(light,medium,heavy) == heavy:
                            if len(self.enemyAlive) == 0 and self.enemyMoney >= self.costs[4]:
                                newAnubis = 'anubis'+ str(len(self.sprites))
                                newAnubis = self.Anubis()
                                self.enemySpawn(newAnubis)
                            elif self.alive[0].type == 'heavy' and self.enemyMoney >= self.costs[5]:
                                newKnight = 'knight'+ str(len(self.sprites))
                                newKnight = self.Knight()
                                self.enemySpawn(newKnight)
                        elif max(light,medium,heavy) == light and self.enemyMoney >= self.costs[6]:
                                newSlime = 'slime'+ str(len(self.sprites))
                                newSlime = self.Slime()
                                self.enemySpawn(newSlime)
                        elif self.dist(self.enemyBase.absPos, self.absLocation[0]) <= 500 and self.enemyMoney >= self.costs[4]:
                            if self.enemyMoney >= self.costs[7]:
                                newSpore = 'spore ' + str(len(self.sprites))
                                newSpore = self.Spore()
                                self.enemySpawn(newSpore)
                            elif self.enemyMoney >= self.costs[6]:
                                newSlime = 'slime'+ str(len(self.sprites))
                                newSlime = self.Slime()
                                self.enemySpawn(newSlime)
                            else:
                                newAnubis = 'anubis'+ str(len(self.sprites))
                                newAnubis = self.Anubis()
                                self.enemySpawn(newAnubis)
                elif self.enemyAge == 2:
                    if len(self.alive) == 0 and len(self.enemyAlive) < 1:
                        if self.enemyMoney >= self.costs[8]:
                            newEarthworm = 'earthworm'+ str(len(self.sprites))
                            newEarthworm = self.EarthWorm()
                            self.enemySpawn(newEarthworm)
                    elif len(self.alive) > 0:
                        if max(light,medium,heavy) == medium and self.enemyMoney >= self.costs[8]:        
                            if (self.alive[0].type == 'medium' and self.dist(self.enemyBase.absPos, self.absLocation[0]) <= 500) and self.enemyMoney >= self.costs[11]:
                                newWerewolf = 'werewolf'+ str(len(self.sprites))
                                newWerewolf = self.WereWolf()
                                self.enemySpawn(newWerewolf)
                            elif self.alive[0].type == 'medium':
                                newEarthworm = 'earthworm'+ str(len(self.sprites))
                                newEarthworm = self.EarthWorm()
                                self.enemySpawn(newEarthworm)
                        elif max(light,medium,heavy) == heavy and self.enemyMoney >= self.costs[10]:
                            if len(self.enemyAlive) > 0:
                                newPhoenix = 'phoenix'+ str(len(self.sprites))
                                newPhoenix = self.Phoenix()
                                self.enemySpawn(newPhoenix)
                        elif max(light,medium,heavy) == light and self.enemyMoney >= self.costs[9]:
                            newGolem = 'golem'+ str(len(self.sprites))
                            newGolem = self.Golem()
                            self.enemySpawn(newGolem)
                        elif self.dist(self.enemyBase.absPos, self.absLocation[0]) <= 500 and self.enemyMoney >= self.costs[8]:
                            if self.enemyMoney >= self.costs[11]:
                                newWerewolf = 'werewolf'+ str(len(self.sprites))
                                newWerewolf = self.WereWolf()
                                self.enemySpawn(newWerewolf)
                            elif self.enemyMoney >= self.costs[9]:
                                newGolem = 'golem'+ str(len(self.sprites))
                                newGolem = self.Golem()
                                self.enemySpawn(newGolem)
                            else:
                                newEarthworm = 'earthworm'+ str(len(self.sprites))
                                newEarthworm = self.EarthWorm()
                                self.enemySpawn(newEarthworm)
                elif self.enemyAge == 3:
                    if len(self.alive) == 0 and len(self.enemyAlive) < 1:
                        if self.enemyMoney >= self.costs[14]:
                            newWhale = 'whale'+ str(len(self.sprites))
                            newWhale = self.Whale()
                            self.enemySpawn(newWhale)
                        elif self.enemyMoney >= self.costs[12]:
                            newDoppelSlime = 'doppelslime'+ str(len(self.sprites))
                            newDoppelSlime = self.DoppelSlime()
                            self.enemySpawn(newDoppelSlime)
                    elif len(self.alive) > 0:
                        if max(light,medium,heavy) == medium and self.enemyMoney >= self.costs[13]:
                            if self.alive[0].type == 'medium':
                                newSlayer = 'slayer'+ str(len(self.sprites))
                                newSlayer = self.Slayer()
                                self.enemySpawn(newSlayer)
                        elif max(light,medium,heavy) == heavy and self.enemyMoney >= self.costs[15]:
                            newWyvern = 'wyvern'+ str(len(self.sprites))
                            newWyvern = self.Wyvern()
                            self.enemySpawn(newWyvern)
                        elif max(light,medium,heavy) == light and self.enemyMoney >= self.costs[12]:
                            if self.enemyMoney >= self.costs[14]:
                                newWhale = 'whale'+ str(len(self.sprites))
                                newWhale = self.Whale()
                                self.enemySpawn(newWhale)
                            else:
                                newDoppelSlime = 'doppelslime'+ str(len(self.sprites))
                                newDoppelSlime = self.DoppelSlime()
                                self.enemySpawn(newDoppelSlime)
                        elif self.dist(self.enemyBase.absPos, self.absLocation[0]) <= 500 and self.enemyMoney >= self.costs[12]:
                            if self.enemyMoney >= self.costs[15]:
                                newWyvern = 'wyvern'+ str(len(self.sprites))
                                newWyvern = self.Wyvern()
                                self.enemySpawn(newWyvern)
                            elif self.enemyMoney >= self.costs[14]:
                                newWhale = 'whale'+ str(len(self.sprites))
                                newWhale = self.Whale()
                                self.enemySpawn(newWhale)
                            elif self.enemyMoney >= self.costs[13]:
                                newSlayer = 'slayer'+ str(len(self.sprites))
                                newSlayer = self.Slayer()
                                self.enemySpawn(newSlayer)
                            else:
                                newDoppelSlime = 'doppelslime'+ str(len(self.sprites))
                                newDoppelSlime = self.DoppelSlime()
                                self.enemySpawn(newDoppelSlime)
                else:
                    if len(self.alive) == 0 and len(self.enemyAlive) < 1:
                        if self.enemyMoney >= self.costs[17]:
                            newBoss = 'boss'+ str(len(self.sprites))
                            newBoss = self.Boss()
                            self.enemySpawn(newBoss)
                        elif self.enemyMoney >= self.costs[16]:
                            newAngel = 'angel'+ str(len(self.sprites))
                            newAngel = self.Angel()
                            self.enemySpawn(newAngel)
                    elif len(self.alive) > 0:
                        if max(light,medium,heavy) == medium and self.enemyMoney >= self.costs[18]:
                            if self.alive[0].type == 'medium' and self.enemyMoney >= self.costs[19]:
                                newSpike = 'spike'+ str(len(self.sprites))
                                newSpike = self.Spike()
                                self.enemySpawn(newSpike)
                            else:
                                newOvermind = 'overmind'+ str(len(self.sprites))
                                newOvermind = self.Overmind()
                                self.enemySpawn(newOvermind)
                        elif max(light,medium,heavy) == heavy and self.enemyMoney >= self.costs[16]:
                            newAngel = 'angel'+ str(len(self.sprites))
                            newAngel = self.Angel()
                            self.enemySpawn(newAngel)
                        elif max(light,medium,heavy) == light and self.enemyMoney >= self.costs[17]:
                            newBoss = 'boss'+ str(len(self.sprites))
                            newBoss = self.Boss()
                            self.enemySpawn(newBoss)
                        elif self.dist(self.enemyBase.absPos, self.absLocation[0]) <= 500 and self.enemyMoney >= self.costs[16]:
                            if self.enemyMoney >= self.costs[19]:
                                newSpike = 'spike'+ str(len(self.sprites))
                                newSpike = self.Spike()
                                self.enemySpawn(newSpike)
                            elif self.alive[0].type == 'mediumweight' and self.enemyMoney >= self.costs[18]:
                                newOvermind = 'overmind'+ str(len(self.sprites))
                                newOvermind = self.Overmind()
                                self.enemySpawn(newOvermind)
                            elif self.alive[0].type == 'light' and self.enemyMoney >= self.costs[17]:
                                newBoss = 'boss'+ str(len(self.sprites))
                                newBoss = self.Boss()
                                self.enemySpawn(newBoss)
                            else:
                                newAngel = 'angel'+ str(len(self.sprites))
                                newAngel = self.Angel()
                                self.enemySpawn(newAngel)

    # function for evolving and auto exp gain
    def evolving(self):
        self.expCounter += 1
        if self.exp >= 2500 and self.age < 5:
            self.age += 1
            self.allyBase.health += 300
            self.allyBase.maxHealth += 300
            self.exp = 0
        if self.enemyExp >= 2500 and self.enemyAge < 5:
            self.enemyAge += 1
            self.enemyBase.health += 300
            self.enemyBase.maxHealth += 300
            self.enemyExp = 0
        if self.expCounter % 3 == 0:
            self.exp += 1
            self.enemyExp += 1
    
    def timerFired(self):
        # if either base reaches zero hp
        if (self.allyBase.health <= 0) or (self.enemyBase.health <= 0):
            self.gameOver = True
        if not(self.gameOver):  
            # home screen fitting
            if self.home:
                self.homeScreen = self.homeScreen.resize((self.width,self.height))
            # P v AI
            elif not(self.home) and not(self.paused) and not(self.pvp):
                self.background = self.background.resize((self.width,self.height))
                self.evolving()
                self.giantAction()
                self.enemyGiantAction()
                self.enemyAI()
                self.death()
                self.projectileMovement()
                self.fighting()
                self.giantFight()
                self.movement()
                self.enemyMovement()
                self.baseCounter = (1 + self.baseCounter) % 3
                self.money += 1
                self.enemyMoney += 1
            # P v P
            elif not(self.home) and not(self.paused) and self.pvp:
                self.background = self.background.resize((self.width,self.height))
                # constantly sending info to server about ally units
                self.net.send([self.alive,self.spriteCounters,self.absLocation])   
                # constantly updates enemies based off info from server
                self.updateEnemy(self.net.receive()) 
                self.evolving()
                self.giantAction()
                self.enemyGiantAction()
                self.death()
                self.projectileMovement()
                self.fighting()
                self.giantFight()
                self.movement()
                self.enemyMovement()
                self.baseCounter = (1 + self.baseCounter) % 3
                self.money += 3
             
    # updates enemies based off of server info of enemyAlive,enemySpriteCounters,enemyAbsLocation
    def updateEnemy(self, message):
        # if not length 3, then it's not the info we want/need
        if len(message) == 3:
            self.enemyAlive = message[0]
            self.enemyAnimate()
            self.enemySpriteCounters = message[1]
            newEnemyAbsLocation = []
            newEnemyRelLocation= []
            # setting locations accoring to server info
            for absLocation in message[2]:
                newEnemyAbsLocation.append(self.enemyBase.absPos - absLocation)
                newEnemyRelLocation.append(self.enemyBase.relPos - (absLocation - self.allyBase.absPos))
            self.enemyAbsLocation = newEnemyAbsLocation
            self.enemyRelLocation = newEnemyRelLocation
        
    # instructions for drawing the UI
    def interface(self,canvas): 
        # background
        canvas.create_image(self.width/2, self.height/2, image=ImageTk.PhotoImage(self.background))
        # this draws the buttons for summoning the units
        for unit in range(4):
            canvas.create_rectangle((.01 + .11 * unit)*self.width, .83 * self.height, (.09 + .11 * unit) * self.width, .85 * self.height, fill = 'lightgreen')
            canvas.create_text((.05 + .11 * unit) * self.width, .84 * self.height, text = f'{self.types[4 * self.age + unit]}', font = "Helvetica 10 bold")
            canvas.create_rectangle((.01 + .11 * unit) * self.width, .85 * self.height, (.09 + .11 * unit) * self.width, .99 * self.height, fill = "Teal")
            canvas.create_image((.05 + .11 * unit) * self.width, .88 * self.height, image = ImageTk.PhotoImage(self.icons[4 * self.age + unit]))
            canvas.create_rectangle((.01  + .11 * unit) * self.width, .95 * self.height, (.09 + .11 * unit) * self.width, .99 * self.height, fill = "White")
            canvas.create_text((.05 + .11 * unit) * self.width, .97 * self.height, text = f'${self.costs[4 * self.age + unit]}', font = "Helvetica 15 bold")
        # this draws the exp bar    
        if self.age < 5:
            canvas.create_rectangle(.75 * self.width, .05 * self.height, .85 * self.width, .15 * self.height, fill = "White" )
            canvas.create_rectangle(.75 * self.width, .05 * self.height, .75 * self.width + (self.exp / 2500) * (.1 * self.width), .15 * self.height, fill = "lightblue")
            canvas.create_text(.8 * self.width, .1 * self.height, text = f'{self.exp} / 2500 EXP', font = 'Helvetica 12 bold')
        # this is the gold
        canvas.create_text(.05 * self.width, .1 * self.height, text = f'${self.money}', font = "Helvetica 25 bold")  

    # draw health bars above units
    def drawHealthbars(self,canvas):
        for sprite in range(len(self.alive)):
            unit = self.alive[sprite]
            pos = self.relLocation[sprite]
            canvas.create_rectangle(pos-25, .66 * self.height, pos + 25, .67 * self.height, fill = "white")
            canvas.create_rectangle(pos-25, .66 * self.height, pos - 25 + (50 * (unit.health / unit.maxHealth)), .67 * self.height, fill = "green")
        for sprite in range(len(self.enemyAlive)):
            unit = self.enemyAlive[sprite]
            pos = self.enemyRelLocation[sprite]
            canvas.create_rectangle(pos-25, .66 * self.height, pos + 25, .67 * self.height, fill = "white")
            canvas.create_rectangle(pos-25, .66 * self.height, pos - 25 + (50 * (unit.health / unit.maxHealth)), .67 * self.height, fill = "green")
        canvas.create_rectangle(self.allyBase.relPos-25, .56 * self.height, self.allyBase.relPos + 25, .57 * self.height, fill = "white")
        canvas.create_rectangle(self.allyBase.relPos-25, .56 * self.height, 
        self.allyBase.relPos - 25 + (50 * (self.allyBase.health / self.allyBase.maxHealth)), .57 * self.height, fill = "green")
        
    # draws the sprites of the units
    def drawSprites(self,canvas):
        for sprite in range(len(self.sprites)):
            unit = self.sprites[sprite]
            canvas.create_image(self.relLocation[sprite], .70 * self.height, \
                image=ImageTk.PhotoImage(unit[self.spriteCounters[sprite]]))
        for sprite in range(len(self.enemySprites)):
            unit = self.enemySprites[sprite]
            canvas.create_image(self.enemyRelLocation[sprite], .70 * self.height, \
                image=ImageTk.PhotoImage(unit[self.enemySpriteCounters[sprite]]))

    # draws the giants
    def drawGiants(self,canvas):
        giant = self.giants[0]
        canvas.create_image(self.allyBase.relPos + 50, .72 * self.height, \
            image=ImageTk.PhotoImage(self.giantSprites[giant.action()][self.giantSpriteCounters[0]]))
        enemyGiant = self.giants[1]
        canvas.create_image(self.enemyBase.relPos - 50, .72 * self.height, \
            image=ImageTk.PhotoImage(self.giantSprites[enemyGiant.action()+1][self.giantSpriteCounters[1]]))

    # draws the projectiles
    def drawProjectiles(self,canvas):
        for count in range(len(self.projectiles)):
            canvas.create_image(self.projectileRelLocation[count], .72 * self.height, \
                image=ImageTk.PhotoImage(self.projectiles[count]))
        for i in range(len(self.enemyProjectiles)):
            canvas.create_image(self.enemyProjectileRelLocation[i], .75 * self.height, \
                image=ImageTk.PhotoImage(self.enemyProjectiles[i]))

    # draws the bases
    def drawBases(self,canvas):
        canvas.create_image(self.allyBase.relPos, .68 * self.height, \
            image=ImageTk.PhotoImage(self.baseSprites[0][self.baseCounter]))
        canvas.create_image(self.enemyBase.relPos, .68 * self.height, \
            image=ImageTk.PhotoImage(self.baseSprites[1][self.baseCounter]))

    # draws the home screen
    def drawHomeScreen(self,canvas):
        canvas.create_image(self.width/ 2, self.height/2, image = ImageTk.PhotoImage(self.homeScreen))
        canvas.create_text(.5 * self.width, .2 * self.height, text = "MONSTER WARS", fill= 'white', font = "verdana 50 bold italic")
        canvas.create_text(.5 * self.width, .28 * self.height, text = 'A 15-112 TERM PROJECT', fill ='white', font= 'verdana 20 italic')
        canvas.create_rectangle( .35 * self.width, .35 * self.height,  .65 * self.width, .45 * self.height, fill='white', outline = 'white')
        canvas.create_text(.5 * self.width, .4 * self.height, text = 'Player Vs. AI', font = 'verdana 20 italic')
        canvas.create_rectangle( .35 * self.width, .55 * self.height,  .65 * self.width, .65 * self.height, fill='white', outline = 'white')
        canvas.create_text(.5 * self.width, .6 * self.height, text = 'Player Vs. Player', font = 'verdana 20 italic')
        canvas.create_rectangle( .35 * self.width, .75 * self.height,  .65 * self.width, .85 * self.height, fill='white', outline = 'white')
        canvas.create_text(.5 * self.width, .8 * self.height, text = 'Instructions', font = 'verdana 20 italic')

    # draws the paused box
    def drawPaused(self,canvas):
        canvas.create_rectangle(.35 * self.width, .4 * self.height, .65 * self.width, .6 * self.height, fill = "white")
        canvas.create_text( .5 * self.width, .5 * self.height, text= 'PAUSED', font = 'verdana 25 bold italic')

    # draws the game over screen
    def drawGameOver(self,canvas):
        canvas.create_text(self.width/2, self.height/2 - 100, text= "GAME OVER", font = 'verdana 70 bold italic', fill = 'red')
        canvas.create_text(self.width/2, self.height/2 + 75, text= "Thanks for playing!", font = 'verdana 25 bold italic', fill = 'black')

    # draws the instructions page
    def drawInstructions(self,canvas):
        canvas.create_text(.5 * self.width, .1 * self.height, 
        text = "Thank you for playing this game! I really, really \
 do appreciate that!", font = 'verdana 25 italic')
        canvas.create_text(.5 * self.width, .15 * self.height, 
        text = "But enough of that, here's what you came for...", 
        font = 'verdana 25 italic')
        canvas.create_text(.5 * self.width, .25 * self.height, 
        text = "Playing the game is quite simple: Just click the unit you want\
 to buy when you can afford them!", font = 'verdana 20 italic')
        canvas.create_text(.5 * self.width, .35 * self.height, 
        text = "Those units have types = Light, Mediumweight or Heavy!",
            font = 'verdana 20 italic')
        canvas.create_text(.5 * self.width, .45 * self.height, 
        text = "Light does more damage to Mediumweight, which in turn does more\
 to Heavy.", font = 'verdana 20 italic')
        canvas.create_text(.5 * self.width, .55 * self.height, 
        text = "The opposite is true for their resistances!", 
        font = 'verdana 20 italic')
        canvas.create_text(.5 * self.width, .65 * self.height, 
        text = "To scroll left and right, use the 'A' and 'D' keys!", 
        font = 'verdana 20 italic')
        canvas.create_text(.5 * self.width, .75 * self.height, \
        text = "To pause and unpause during a P v AI, use the 'P' key!", 
        font = 'verdana 20 italic')
        canvas.create_text(.5 * self.width, .85 * self.height, \
        text = "Press 'b' from here to go back to the home screen, enjoy!", 
        font = 'verdana 20 italic')

    def redrawAll(self,canvas):
        if self.gameOver:
            self.drawGameOver(canvas)
        elif self.instructions:
            self.drawInstructions(canvas)
        elif self.home:
            self.drawHomeScreen(canvas)
        elif not(self.home):
            self.interface(canvas)
            self.drawGiants(canvas)
            self.drawBases(canvas)
            self.drawSprites(canvas)
            self.drawProjectiles(canvas)
            self.drawHealthbars(canvas)
            if self.paused:
                self.drawPaused(canvas)

    
MyApp(width=1400, height=700)