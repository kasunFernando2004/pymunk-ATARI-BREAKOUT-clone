#Code author: KAsun Fernando
#Code purpose: pygame mimic of Atari breakout with powerups
#Last edited: 10/01/2024

#importing neccesary modules
import pygame
import pymunk
import pymunk.pygame_util
import math
import time
import random
pygame.init()

#setting the size of the game window
WIDTH,HEIGHT = 750,600
WINDOWWIDTH,WINDOWHEIGHT=1200,600

window = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))
#initialising the ball object and impulse vector array
ball = None
impulseVector=None
# function to make the powerup rectangles change color over time
def cycle(color):
    R=color[0]
    G=color[1]
    B=color[2]
    if G==255 and B==0 and R!=255:
        R+=17
    elif R==255 and B==0 and G!=0:
        G-=17
    elif R==255 and G==0 and B!=255:
        B+=17
    elif B==255 and G==0 and R!=0:
        R-=17
    elif R==0 and B==255 and G!=255:
        G+=17
    elif R==0 and G==255 and B!=0:
        B-=17
    return([R,G,B,255])
#returns distanc between two points
def calculate_distance(p1,p2):
    return math.sqrt((p2[1]-p1[1])**2+(p2[0]-p1[0])**2)
#returns the normalised vector
def norm(vec):
    '''
    returns normalised vector
    '''
    x=vec[0]
    y=vec[1]
    normm = math.sqrt(x**2+y**2)
    x=x/normm
    y=y/normm
    return [x,y]
#returns the norm of a vector 
def norm_scalar(vec):
    '''
    returns normalised vector
    '''
    x=vec[0]
    y=vec[1]
    normm = math.sqrt(x**2+y**2)
    return normm
#cacluates angle between 2 vectors
def calculate_angle(p1,p2):
    return math.atan2(p2[1]-p1[1],p2[0]-p1[0])

#converts color hex code to 3 values representing RGB values.
def convert_hex_to_rgb(hexadecimal):
    hexadecimalString = []
    for char in hexadecimal:
        if char.upper() == "A":
            char = 10
        elif char.upper() == "B":
            char = 11
        elif char.upper() == "C":
            char = 12
        elif char.upper() == "D":
            char = 13
        elif char.upper() == "E":
            char = 14
        elif char.upper() == "F":
            char = 15
        hexadecimalString.append(char)
    RGB = [0,0,0,255]
    RGB[0] = (int(hexadecimalString[0])*16) +int(hexadecimalString[1])
    RGB[1] = (int(hexadecimalString[2])*16) +int(hexadecimalString[3])
    RGB[2] = (int(hexadecimalString[4])*16) +int(hexadecimalString[5])
    return RGB

#function for drawing things like the text on screen
def draw(space,window,draw_options,gameInfo):
    window.fill("black")
    space.debug_draw(draw_options)
    font1 = pygame.font.Font(None,28)
    font2 = pygame.font.Font(None,100)
    gameInfo.TilesRemaining=Tile.numTiles

    if  gameInfo.Lives<=0:
        gameInfo.gameState="GameOver"
        gameState = font2.render(f"{gameInfo.gameState}",True,(255,0,0,0))
        restartPromt = font1.render("Press Y to retry, X to exit",True,(255,0,0,0))
        window.blit(gameState,(WINDOWWIDTH/2-200,WINDOWHEIGHT/2))
        window.blit(restartPromt,(WINDOWWIDTH/2-140,WINDOWHEIGHT/2+100))
    elif gameInfo.TilesRemaining==0:
        gameInfo.gameState="You Win"
        gameState = font2.render(f"{gameInfo.gameState}",True,(0,255,0,0))
        window.blit(gameState,(WINDOWWIDTH/2-200,WINDOWHEIGHT/2))
    else:
        gameState = font1.render(f"game State: {gameInfo.gameState}",True,(0,0,0,0))
        window.blit(gameState,(10,120))
    timer = font1.render(f"time: {gameInfo.return_ellapsed_time():0.2f}",True,(0,0,0,0))
    lives = font1.render(f"lives remaining: {gameInfo.Lives}",True,(0,0,0,0))
    tiles = font1.render(f"tiles remaining:{gameInfo.TilesRemaining}",True,(0,0,0,0))
    curPowerup = font1.render(f"current  powerup:{gameInfo.CurPowerUp}",True,(0,0,0,0))
    if gameInfo.CurPowerUp!=None:
        curPowerupTime = font1.render(f"current powerup time:{15-gameInfo.return_powerup_ellapsed_time():0.2f}",True,(255,255,255,0))
        window.blit(curPowerupTime,(10,200))
        if 15-gameInfo.return_powerup_ellapsed_time()<0 or gameInfo.CurPowerUp=="bruh":
            gameInfo.CurPowerUp=None
            gameLogic.powerUpRemoved=1
    window.blit(timer,(10,100))
    window.blit(lives,(10,140))
    window.blit(tiles,(10,160))
    window.blit(curPowerup,(10,180))
    if gameInfo.gameState=="shooting" and gameLogic.shootingFlag==0 and gameInfo.CurPowerUp=="stickyPaddle":
        pygame.draw.line(window,(101,255,0,0),ball.body.position,(ball.body.position.x+100*impulseVector[0],ball.body.position.y+100*impulseVector[1]))

    pygame.display.update()

#class to handle the gamelogic, such as lives, the number of tiles, the powerups ect
class gameLogic():
    powerUpApplied = 0
    powerUpRemoved = 0
    shootingFlag = 1
    def __init__(self,gameState=None,Lives=None,TilesRemaining=None,CurPowerUp=None):
        self.time = time.time()
        self.gameState=gameState
        self.Lives = Lives
        self.TilesRemaining=TilesRemaining
        self.CurPowerUp = CurPowerUp
        self.CurPowerUpTime = None
    def ball_died(self): #if the ball dies and there are lives remaining, the game will go back to shooting
        self.Lives-=1
        self.gameState = "shooting"
        gameLogic.shootingFlag=1
        self.CurPowerUp = None
        gameLogic.powerUpRemoved=1

    def return_ellapsed_time(self):
        return time.time()-self.time
    def return_powerup_ellapsed_time(self):
        return time.time()-self.CurPowerUpTime
    def apply_power_up(self,duh): #duh represents which powerup to apply
        if duh==0:
            self.CurPowerUp="multipleBalls"
        elif duh == 1:
            self.CurPowerUp="biggerPaddle"
        elif duh == 2:
            self.CurPowerUp="stickyPaddle"
        self.CurPowerUpTime = time.time() #measures when the curpowerup is applied counts down from that
        gameLogic.powerUpApplied=1


gameInfo = gameLogic()
#DIM = (WIDTH,HEIGHT)
#Class to create a rectangle, will be used to create the paddle and the tiles
class Rectangle():
    def __init__(self,space,position,DIM,color,collisionType):
        self.body = pymunk.Body()
        self.shape = pymunk.Poly(self.body,[(-DIM[0]/2,-DIM[1]/2),(DIM[0]/2,-DIM[1]/2),(DIM[0]/2,DIM[1]/2),(-DIM[0]/2,DIM[1]/2)])
        self.shape.collision_type=collisionType
        self.body.position = position
        self.dimensions = DIM
        self.shape.mass = 1000
        self.shape.elasticity=1
        self.shape.friction = 0.0
        self.shape.color = color
        self.shape.object = self
        space.add(self.body,self.shape)
    
    def move_object(self): #for moving the padddle
        mousePosX,mousePosY = pygame.mouse.get_pos()
        widthh=self.dimensions[0]
        if (mousePosX<WINDOWWIDTH/2-WIDTH/2+(widthh)/2+11):
            mousePosX=WINDOWWIDTH/2-WIDTH/2+(widthh)/2+11
        if (mousePosX>WINDOWWIDTH/2+WIDTH/2-(widthh)/2-11):
            mousePosX=WINDOWWIDTH/2+WIDTH/2-(widthh)/2-11
        mousePosY = HEIGHT*(3/4)
        self.body.position = mousePosX,HEIGHT*(3/4)
    def remove_rect(self,space):  #function for removing a tile
        space.remove(self.shape,self.body)
def boundary(space): #function for drawing in the game borders
    TLx = WINDOWWIDTH/2-WIDTH/2
    TLy = 0
    barriers = [
        [(TLx,TLy),(TLx+WIDTH,TLy),(TLx+WIDTH,10),(TLx,10)],
        [(TLx,TLy),(TLx,TLy+HEIGHT),(TLx+10,TLy+HEIGHT),(TLx+10,TLy)],
        [(TLx+WIDTH,TLy),(TLx+WIDTH-10,TLy),(TLx+WIDTH-10,TLy+HEIGHT),(TLx+WIDTH,TLy+HEIGHT)],
        [(0,0),(TLx,0),(TLx,HEIGHT),(0,HEIGHT)],
        [(TLx+WIDTH,0),(WINDOWWIDTH,0),(WINDOWWIDTH,HEIGHT),(TLx+WIDTH,HEIGHT)]
    ]
    for barrier in barriers:
        body = pymunk.Body(body_type=pymunk.Body.STATIC) #static because we don't want the barriers to move
        shape = pymunk.Poly(body,barrier)
        shape.elasticity=1
        shape.color = (200,200,200,200)
        shape.collision_type = 0
        space.add(body,shape)
    bottom =[(TLx,TLy+HEIGHT+10),(TLx+WIDTH,TLy+HEIGHT+10),(TLx+WIDTH,TLy+HEIGHT+10+100),(TLx,TLy+HEIGHT+10+100)]
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape=pymunk.Poly(body,bottom)
    shape.elasticity=1
    shape.color = (0,0,0,0)
    shape.collision_type=4
    space.add(body,shape)
# class for the tiles that we are going to hit,
class Tile(Rectangle):
    numTiles = 0 #records the number of tiles
    TileList = []
    def __init__(self,space,position,DIM,color,collisionType,bruh):
        super().__init__(space,position,DIM,color,collisionType)
        Tile.numTiles+=1
        Tile.TileList.append(self)
        self.bruh = bruh
    
    def remove_tile(self,space):
        if self in Tile.TileList:
            Tile.TileList.remove(self)
        space.remove(self.shape,self.body)
        Tile.numTiles-=1

#class to create the ball object and the mini-balls for one of the powerups.
class Ball():
    def  __init__(self,space,position,radius,color,collisionType):
        self.body = pymunk.Body()
        self.radius=radius
        self.body.position=position
        self.shape = pymunk.Circle(self.body,radius)
        self.shape.collision_type=collisionType
        self.shape.mass=10
        self.shape.color=color
        self.shape.elasticity=1.0
        self.shape.friction = 0.0
        space.add(self.body,self.shape)
        self.ballshot=0
        self.shape.object=self
        self.body.angular_velocity=0 #angular velocity is set to zero, cause otherwise weird collisions occur.
    
    def apply_random_impulse(self): # used for shooting, sends it in a random direction 
        angle = (0.6*(random.random())+0.2)*math.pi
        fx = math.cos(angle)*2500
        fy = math.sin(angle)*2500
        self.ballshot+=1
        return [-fx,-fy]
    
    def apply_directed_impulse(self,object): #applies an impulse between the collision point of two objects
        if object.shape.collision_type==3 or object.shape.collision_type==5:
            huh = object.bruh
            (vx,vy)=self.body.velocity
            v= [vx,vy]
            v=norm(v)
            v[0]=(v[0]*150+100*huh)
            v[1]=(v[1]*150+100*huh)
            self.body.apply_impulse_at_local_point(v,(0,0))
        else:
            (vx,vy)=self.body.velocity
            v= [vx,vy]
            v=norm(v)
            v[0]=(v[0]*150)
            v[1]=(v[1]*150)
            self.body.apply_impulse_at_local_point(v,(0,0))

    # applies an impulse between the center of the ball and the center of the platform, unpredictable results
    def apply_platform_impulse(self,platform,ball):
        x=ball.body.position.x-platform.body.position.x
        y=ball.body.position.y-platform.body.position.y
        v=[x,y]
        v=norm(v)
        velocityNorm = norm_scalar(ball.body.velocity)
        v[0]=v[0]*velocityNorm
        v[1]=v[1]*velocityNorm
        self.body.velocity = v
        v=norm(v)
        v[0]=(v[0]*150)
        v[1]=(v[1]*150)
        self.body.apply_impulse_at_local_point(v,(0,0))
    #funciton for removing a ball from the space
    def remove_ball(self,space):
        space.remove(self.shape,self.body)
        
#function for setting up the tiles
def  initialiseTiles(space):
    tiles = []
    # a list of the colors we can use
    colors = [convert_hex_to_rgb("023788"),convert_hex_to_rgb("650D89"),convert_hex_to_rgb("920075"),convert_hex_to_rgb("F6019D"),convert_hex_to_rgb("D40078"),convert_hex_to_rgb("2DE2E6"),convert_hex_to_rgb("FF3864"),convert_hex_to_rgb("791e94"),convert_hex_to_rgb("f9c80e"),convert_hex_to_rgb("f706cf")]
    for i in range(11):
        for j  in range(5):
            if (((i!=2 and i!=8)or j!=1) and (i!=5 or j!=3)): #ignoring the special tiles
                #adds the tiles in rows where there are 11 of them
                tiles.append([(WINDOWWIDTH/2-325+(60+5)*i,HEIGHT/2+(18)*1-j*40),(60,15),colors[random.randint(0,len(colors)-1)],3,j])
    for  i in range(10):
        for j  in range(5):
            #adds the tiles in rows where there are 10 of them.
            tiles.append([(WINDOWWIDTH/2-290+(60+5)*i,HEIGHT/2+(18)*(1)-20-j*40),(60,15),colors[random.randint(0,len(colors)-1)],3,j])

    for position,size,color,collisiionType,bruh in tiles:
        Tile(space,position,size,color,collisiionType,bruh)

#collision handler
def ball_tile_collision(arbiter,space,data):
    global gameInfo
    shap1e,shap2e = arbiter.shapes
    if shap1e.collision_type==3 and shap2e.collision_type==5: #3 is  rgular tile,5 is special tile
        tileToDelete=shap1e.object
        shap2e.object.apply_directed_impulse(shap1e.object)
        if shap1e.collision_type==5: # if it hits a powerup tile, a powerup is applied
            print(tileToDelete)
            duh = random.randint(0,2)
            gameInfo.apply_power_up(duh)
    elif shap2e.collision_type==3 and shap1e.collision_type==5:
        tileToDelete=shap2e.object
        shap1e.object.apply_directed_impulse(shap2e.object)
        if shap2e.collision_type==5:
            print(tileToDelete)
            duh = random.randint(0,2)
            gameInfo.apply_power_up(duh)
    tileToDelete.remove_tile(space)


# collision handler for ball and barrier
def ball_barrier_collision(arbiter,space,data):
    shape1,shape2 = arbiter.shapes
    if shape1.collision_type==1:
        shape1.object.apply_directed_impulse(shape1.object)
    elif shape2.collision_type==1:
        shape2.object.apply_directed_impulse(shape2.object)
# collision handler for ball and platform
def ball_platform_collision(arbiter,space,data):
    global gameInfo
    shape1,shape2 = arbiter.shapes
    if shape1.collision_type==1:
        shape1.object.apply_platform_impulse(shape2.object,shape1.object)
        shape1.object.apply_directed_impulse(shape2)
    elif shape2.collision_type==1:
        shape2.object.apply_platform_impulse(shape1.object,shape2.object)
        shape2.object.apply_directed_impulse(shape1.object)
    if gameInfo.CurPowerUp=="stickyPaddle": # if the powerup is stickly paddle, we go to shooting mode, with the shooting direction shown
        gameInfo.gameState="shooting"
        gameLogic.shootingFlag=1
        if shape1.collision_type==1:
            shape1.object.remove_ball(space)
            shape1.object=None
        elif shape2.collision_type==1:
            shape2.object.remove_ball(space)
            shape2.object=None
        
    
#if th ball collides with the bottom, gameInfo is notified to tell it that the ball died
def ball_bottom_collision(arbiter,space,data):
    shape1,shape2 = arbiter.shapes
    global gameInfo
    if shape1.collision_type==1:   
        if shape1.object.radius==10: #checking if the main ball died, not the mini ball
            gameInfo.ball_died()
        shape1.object.remove_ball(space)
        print("biden")
        shape1.object = None
    elif shape2.collision_type==1:
        if shape2.object.radius==10:
            gameInfo.ball_died()
        shape2.object.remove_ball(space)
        print("biden")
        shape2.object = None



#main function
def run(window,width,height):
    runrun=True
    while runrun==True:
        #initialising values for things like the space, time, gravity ect
        run=True
        clock=pygame.time.Clock()
        fps =  60
        dt = 1/fps
        miniBalls = [None]*3
        space = pymunk.Space()
        space.gravity = (0,0)

        draw_options = pymunk.pygame_util.DrawOptions(window)
        platformWidth = 100

        #creating our objects
        platform = Rectangle(space,(WIDTH/2,HEIGHT*(3/4)),(platformWidth,10),[255,255,255,0],2)
        global ball
        ball =  Ball(space,(platform.body.position.x,platform.body.position.y),10,(255,255,255,255),1)
        global impulseVector
        Tile.numTiles=0
        Tile.TileList.clear()
        initialiseTiles(space)
        powerTile1=Tile(space,(WINDOWWIDTH/2-325+(60+5)*2,HEIGHT/2+(18)*1-1*40),(60,15),(0,255,0,0),5,1)
        powerTile2=Tile(space,(WINDOWWIDTH/2-325+(60+5)*8,HEIGHT/2+(18)*1-1*40),(60,15),(255,0,0,0),5,1)
        powerTile3=Tile(space,(WINDOWWIDTH/2-325+(60+5)*5,HEIGHT/2+(18)*1-3*40),(60,15),(0,255,0,0),5,3)
        boundary(space)
        #setting up the collision handlers
        ballTile = space.add_collision_handler(3,1)
        ballTile.post_solve=ball_tile_collision

        ballTile = space.add_collision_handler(1,5)
        ballTile.post_solve=ball_tile_collision

        ballPlatform = space.add_collision_handler(2,1)
        ballPlatform.post_solve=ball_platform_collision
        ballBarrier = space.add_collision_handler(1,0)
        ballBarrier.post_solve=ball_barrier_collision

        ballBottom = space.add_collision_handler(1,4)
        ballBottom.post_solve=ball_bottom_collision
        global gameInfo
        #initialising the gameInfo to be shooting intially,along with other stuff
        gameInfo=gameLogic("shooting",5,Tile.numTiles,None)
        print(Tile.numTiles)
        while run==True:
            #if we are in shooting mode, shoot the ball
            if gameLogic.shootingFlag==1:
                gameLogic.shootingFlag=0
                impulseVector = ball.apply_random_impulse()
            #changes the colors of the special tiles
            powerTile1.shape.color = cycle(powerTile1.shape.color)
            powerTile2.shape.color = cycle(powerTile2.shape.color)
            powerTile3.shape.color = cycle(powerTile3.shape.color)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: #for exiting out of the section
                    run = False
                    runrun=False
                    break
                if event.type == pygame.MOUSEBUTTONDOWN: # if the game state is shooting, clicking will shoot the ball
                    if gameInfo.gameState=="shooting" and gameInfo.Lives>0:
                        ball.body.apply_impulse_at_local_point(impulseVector,(0,0))
                        gameInfo.gameState="bouncing"

                            
                if gameInfo.gameState=="GameOver": # code for handling the exit
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_y:
                            run=False
                            break
                        elif event.key == pygame.K_x:
                            run = False
                            runrun=False
                            break
            #handling moving the platform
            platform.move_object()
            # if the ball is removed from the space (killed), reset 
            if ball.shape.object==None:
                ball = Ball(space,(platform.body.position.x,platform.body.position.y-16),10,(255,255,255,255),1)
            if gameInfo.gameState=="shooting" and gameInfo.Lives>0 and ball.shape.object!=None:
                ball.body.position = platform.body.position.x,platform.body.position.y-16
            
            #code for handling powerups
            # bigger paddle =>increase paddle size,
            # stickypaddle=> when the ball hits the padddle, reset to shooting mode, also shows direction ball will be shot
            # multipleBalls => creates multiple mini balls at point of impact that bouce around
            if gameLogic.powerUpApplied==1:
                gameLogic.powerUpApplied=0
                if gameInfo.CurPowerUp=="biggerPaddle":
                    mousePos = platform.body.position
                    platform.remove_rect(space)
                    NEWDIM = [200,10]
                    platform = Rectangle(space,mousePos,NEWDIM,(255,255,255,255),2)
                if gameInfo.CurPowerUp=="stickyPaddle":
                    mousePos = platform.body.position
                    platform.remove_rect(space)
                    NEWDIM = [100,10]
                    platform = Rectangle(space,mousePos,NEWDIM,(101,255,0,255),2)
                if gameInfo.CurPowerUp=="multipleBalls":
                    ballPosition = ball.body.position
                    for i in range(3):
                       miniBalls[i]=Ball(space,ballPosition,7,(255,255,255,255),1)
                       v=miniBalls[i].apply_random_impulse()
                       miniBalls[i].body.apply_impulse_at_local_point(v,(0,0))
            #handling if the miniballs are removed
            if miniBalls!=[None]*3:
                if miniBalls[0].shape.object==None and miniBalls[1].shape.object==None and miniBalls[2].shape.object==None:
                    gameInfo.CurPowerUp="bruh"
            
            if gameLogic.powerUpRemoved==1:
                gameLogic.powerUpRemoved=0
                if miniBalls!=[None]*3:
                    for ballz in miniBalls:
                        if ballz.shape.object!=None:
                            ballz.remove_ball(space)
                    miniBalls = [None]*3
                mousePos = platform.body.position
                platform.remove_rect(space)
                NEWDIM = [100,10]
                platform = Rectangle(space,mousePos,NEWDIM,(255,255,255,255),2)
                

            #updating all the new information
            draw(space,window,draw_options,gameInfo)
            ball.body.angular_velocity=0
            platform.body.angular_velocity=0
            space.step(dt)
            clock.tick(fps)  
    pygame.quit()

if __name__ == "__main__":
    run(window,WIDTH,HEIGHT)
