from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import pygame
import random
from math import *
from OBJLoader import *
from pygame.locals import *


class Light:
    Position = []
    Ambient = []
    Diffusion = []
    Specular = []
    randomFactor = 0

    def Enable(x, y, z):
        if x:
            glEnable(GL_LIGHT0)
        if y:
            glEnable(GL_LIGHT1)
        if z:
            glEnable(GL_LIGHT2)

    def randomize():
        Light.randomFactor += 1
        Light.Position = [0, 17, -26]
        Light.Ambient = [abs(sin(Light.randomFactor / 50)), abs(sin(
            30 + Light.randomFactor / 50)), abs(sin(60 + Light.randomFactor / 50)) ** 2, 1]
        Light.Diffusion = [abs(sin(Light.randomFactor / 100)), abs(sin(
            30 + Light.randomFactor / 100)), abs(sin(60 + Light.randomFactor / 100)) ** 2, 1]
        Light.Specular = [abs(cos(Light.randomFactor / 100)), abs(cos(
            30 + Light.randomFactor / 100)), abs(cos(60 + Light.randomFactor / 100)) ** 2, 1]

        glLightfv(GL_LIGHT0, GL_POSITION, Light.Position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, Light.Ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, Light.Diffusion)
        glLightfv(GL_LIGHT0, GL_SPECULAR, Light.Specular)

        Light.Position = [0, 10, 15]
        Light.Ambient = [0.2, 0.2, 0.4, 1]
        Light.Diffusion = [0, 0, 0.2, 0.55]
        Light.Specular = [0.5, 0.5, 0.7, 0.5]

        glLightfv(GL_LIGHT1, GL_POSITION, Light.Position)
        glLightfv(GL_LIGHT1, GL_AMBIENT, Light.Ambient)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, Light.Diffusion)
        glLightfv(GL_LIGHT1, GL_SPECULAR, Light.Specular)

        Light.Position = [0, 10, -500]
        Light.Ambient = [abs(cos(Light.randomFactor / 50)), abs(cos(
            45 + Light.randomFactor / 50)), abs(cos(90 + Light.randomFactor / 50)) ** 2, 1]
        Light.Diffusion = [abs(cos(Light.randomFactor / 100)), abs(cos(
            45 + Light.randomFactor / 100)), abs(cos(90 + Light.randomFactor / 100)) ** 2, 1]
        Light.Specular = [abs(sin(Light.randomFactor / 100)), abs(sin(
            45 + Light.randomFactor / 100)), abs(sin(90 + Light.randomFactor / 100)) ** 2, 1]

        glLightfv(GL_LIGHT2, GL_POSITION, Light.Position)
        glLightfv(GL_LIGHT2, GL_AMBIENT, Light.Ambient)
        glLightfv(GL_LIGHT2, GL_DIFFUSE, Light.Diffusion)
        glLightfv(GL_LIGHT2, GL_SPECULAR, Light.Specular)


class BlockLoader:
    model = None
    modelSizeX = modelSizeZ = 0

    def init():
        BlockLoader.model = OBJ('./Models/satellite/sat.obj', swapyz=True)
        BlockLoader.modelSizeZ = 3.1  # by testing
        BlockLoader.modelSizeX = 5


class Block:
    selectTrack = [-1, 0, 1]
    track = 0
    zLocation = 0
    frontZ = backZ = rightX = leftX = 0

    Diff = [0.4, 0.4, 0.4, 1]
    Spec = [0.4, 0.4, 0.4, 1]
    Shin = [0]
    Passed = False

    def __init__(self, z):
        self.zLocation = z
        self.track = random.choice(self.selectTrack)

    def draw(self):
        self.frontZ = self.zLocation - BlockLoader.modelSizeZ/2
        self.backZ = self.zLocation + BlockLoader.modelSizeZ/2
        self.rightX = self.track * Road.rightSide / 2 + BlockLoader.modelSizeX/2
        self.leftX = self.track * Road.rightSide / 2 - BlockLoader.modelSizeX/2

        glPushMatrix()
        glEnable(GL_FOG)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_COLOR_MATERIAL)
        Light.Enable(True, True, False)

        glTranslate((self.track * Road.rightSide / 2), 1.75, self.zLocation)
        glRotate(-90, 0, 1, 0)
        glRotate(-90, 1, 0, 0)

        glScale(0.5, 0.5, 0.5)

        glMaterialfv(GL_FRONT, GL_DIFFUSE, Block.Diff)
        glMaterialfv(GL_FRONT, GL_SPECULAR, Block.Spec)
        glMaterialfv(GL_FRONT, GL_SHININESS, Block.Shin)
        glCallList(BlockLoader.model.gl_list)

        glPopMatrix()
        glDisable(GL_COLOR_MATERIAL)
        glDisable(GL_FOG)

        if self.detectCollisionZ(Player.frontZ, Player.backZ, self.frontZ, self.backZ) \
                and self.detectCollisionX(Player.rightX, Player.leftX, self.rightX, self.leftX):
            State.currentState = State.collision
            pygame.mixer.music.set_volume(0.1)

        if self.zLocation > Player.zPos + 0 and not(self.Passed):
            Score.currentScore += 5
            self.Passed = True
        if self.zLocation > Player.zPos + 10:
            self.zLocation -= setBlocks.BlocksNumber*setBlocks.sDistance  # 500
            self.track = random.choice(self.selectTrack)
            self.Passed = False

        if State.currentState == State.playing:
            self.zLocation += 0.6

    def detectCollisionZ(self, pFront, pBack, bFront, bBack):
        if (pFront <= bBack and pBack >= bFront) or (pBack >= bFront and pFront <= bBack):
            return True
        return False

    def detectCollisionX(self, pRight, pLeft, bRight, bLeft):
        if (pLeft <= bRight and pRight >= bLeft) or (pRight >= bLeft and pLeft <= bRight):
            return True
        return False


class setBlocks:
    BlocksNumber = 35
    BlocksStart = -25
    BlocksEnd = -400
    sDistance = 12
    Blocks = []

    def init():
        BlocksZLoc = []
        BlocksZLocFiltered = []

        # generating random Z Locations
        for i in range(setBlocks.BlocksNumber):
            BlocksZLoc.append(random.randrange(
                setBlocks.BlocksStart, setBlocks.BlocksEnd, -1))

        BlocksZLoc.sort()

        # filteration
        for i in range(len(BlocksZLoc)):
            if len(BlocksZLocFiltered) > 0 and ((BlocksZLoc[i] - BlocksZLocFiltered[-1]) < setBlocks.sDistance):
                continue
            BlocksZLocFiltered.append(BlocksZLoc[i])

        for i in range(len(BlocksZLocFiltered)):
            block = Block(BlocksZLocFiltered[i])
            while len(setBlocks.Blocks) > 0 and block.track == setBlocks.Blocks[-1].track:
                block = Block(BlocksZLocFiltered[i])
            setBlocks.Blocks.append(block)

    def draw():
        for block in setBlocks.Blocks:
            block.draw()

    def reset():
        setBlocks.Blocks.clear()


class Player:
    model = None
    xPos = yPos = zPos = 0
    bounceUp = True
    rotAngle = 0
    track = 0
    frontZ = backZ = modelSizeZ = modelSizeX = rightX = leftX = 0

    Diff = [0.2, 0.2, 0.2, 1]
    Spec = [0.4, 0.4, 0.5, 1]
    Shin = [128]

    moveRight = moveLeft = 0
    nextPosition = 0

    def init():
        Player.model = OBJ('./Models/scifi_fighter/scifi.obj', swapyz=True)
        Player.modelSize = 3.5
        Player.zPos = 5

    def movementUpdate():
        Player.frontZ = Player.zPos - (Player.modelSizeZ / 2)
        Player.backZ = Player.zPos + (Player.modelSizeZ / 2)
        Player.rightX = Player.xPos + (Player.modelSizeX / 2)
        Player.leftX = Player.xPos - (Player.modelSizeX / 2)

        if State.currentState == State.playing:
            if Player.moveRight:
                Player.xPos += 0.3
                if Player.xPos >= Player.nextPosition:
                    Player.moveRight = False
                    Player.xPos = Player.nextPosition

            if Player.moveLeft:
                Player.xPos -= 0.3
                if Player.xPos <= Player.nextPosition:
                    Player.moveLeft = False
                    Player.xPos = Player.nextPosition

            if Player.bounceUp:
                Player.yPos += 0.005
                if Player.yPos >= 0.2:
                    Player.bounceUp = False
            else:
                Player.yPos -= 0.005
                if Player.yPos <= -0.2:
                    Player.bounceUp = True

    def draw():

        glPushMatrix()
        Player.movementUpdate()

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_COLOR_MATERIAL)
        Light.Enable(True, True, False)

        glTranslate(Player.xPos, Player.yPos, Player.zPos)
        glTranslate(0, 1.25, 0)  # setup model

        glRotate(-90, 1, 0, 0)
        glScale(0.7, 0.7, 0.7)

        glMaterialfv(GL_FRONT, GL_DIFFUSE, Player.Diff)
        glMaterialfv(GL_FRONT, GL_SPECULAR, Player.Spec)
        glMaterialfv(GL_FRONT, GL_SHININESS, Player.Shin)
        glCallList(Player.model.gl_list)

        glPopMatrix()
        glDisable(GL_COLOR_MATERIAL)

        Player.rotAngle += 0.3

    def reset():
        Player.xPos = Player.yPos = Player.nextPosition = 0
        Player.zPos = 5
        Player.moveLeft = Player.moveRight = False


class Skybox:
    model = None
    rotAngle = 0

    def init():
        Skybox.model = OBJ('./Models/skybox/skybox.obj')
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    def draw():

        Skybox.rotAngle += 0.05

        glEnable(GL_TEXTURE_2D)
        glDepthMask(False)
        glEnable(GL_COLOR_MATERIAL)
        Light.Enable(True, True, False)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glTranslate(0, 0, -0.75)
        glRotate(Skybox.rotAngle, 0, 1, 0)
        glScale(5, 5, 5)

        glMaterialfv(GL_FRONT, GL_DIFFUSE, Player.Diff)
        glMaterialfv(GL_FRONT, GL_SPECULAR, Player.Spec)
        glMaterialfv(GL_FRONT, GL_SHININESS, Player.Shin)

        # Skybox.model.draw()
        glCallList(Skybox.model.gl_list)

        glPopMatrix()

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        glDepthMask(True)

    def reset():
        Skybox.rotAngle = 0


class Display:
    width = 1280
    height = 720
    title = b"main"
    FPS = 300

    def init():
        glutInit()

        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(Display.width, Display.height)
        glutCreateWindow(Display.title)

        glutFullScreen()
        glutSetCursor(GLUT_CURSOR_NONE)

        glColorMaterial(GL_FRONT, GL_AMBIENT)
        glEnable(GL_LIGHTING)
        glutDisplayFunc(render)
        glutSpecialFunc(handleMovement)
        glutKeyboardFunc(handleState)

        Display.perspectiveProjection()
        Display.setCamera()

    def perspectiveProjection():
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(50, Display.width/Display.height, 1, 2500)
        # zNear should always be the lower value
        glMatrixMode(GL_MODELVIEW)

    def orthographicProjection():
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, Display.width, 0, Display.height)
        glMatrixMode(GL_MODELVIEW)

    def setCamera():
        glLoadIdentity()
        gluLookAt(0, 4.5, 10,  # eye, where the camera is located
                  0, 0, -5,  # center, where the camera is looking at
                  0, 1, 0)  # up vector


class Fog:
    def init():
        glEnable(GL_FOG)
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogfv(GL_FOG_COLOR, (0, 0, 0.5, 0.2))
        glFogf(GL_FOG_DENSITY, 0.5)
        glFogf(GL_FOG_START, 0)
        glFogf(GL_FOG_END, 300)


class Road:
    width = leftSide = rightSide = 0
    texW = texH = 0
    texture = None
    textureRepeater = 0
    ColorDiff = [0.2, 0.2, 0.25, 0.45]
    ColorSpec = [0.1, 0.1, 0.1, 0.45]
    ColorShin = [100]

    def init(w):
        Road.width = w
        Road.rightSide = w / 2
        Road.leftSide = -w / 2

        Road.texture = glGenTextures(1)
        imgLoad = pygame.image.load("./Road/RoadTexture.png")
        imgRaw = pygame.image.tostring(imgLoad, "RGBA", 1)
        Road.texW = imgLoad.get_width()
        Road.texH = imgLoad.get_height()

        glBindTexture(GL_TEXTURE_2D, Road.texture)

        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        gluBuild2DMipmaps(GL_TEXTURE_2D, 4, Road.texW,
                          Road.texH, GL_RGBA, GL_UNSIGNED_BYTE, imgRaw)

    def draw():

        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_FOG)

        Light.Enable(True, True, False)

        glMaterialfv(GL_FRONT, GL_DIFFUSE, Road.ColorDiff)
        glMaterialfv(GL_FRONT, GL_SPECULAR, Road.ColorSpec)
        glMaterialfv(GL_FRONT, GL_SHININESS, Road.ColorShin)

        Road.textureRepeater = Road.textureRepeater + 0.20
        z = Road.textureRepeater  # to ease the process

        glColor(0.45, 0.45, 0.65, 1)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, Road.texture)

        glBegin(GL_POLYGON)

        glTexCoord(0, z)
        glVertex(Road.rightSide, 0, -500)

        glTexCoord(1, z)
        glVertex(Road.rightSide, 0, 200)

        glTexCoord(1, Road.texH+z)
        glVertex(Road.leftSide, 0, 200)

        glTexCoord(0, Road.texH+z)
        glVertex(Road.leftSide, 0, -500)

        glEnd()

        glDisable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)

        glDisable(GL_COLOR_MATERIAL)


def handleMovement(key, x, y):

    if not(Player.moveRight or Player.moveLeft):
        if key == GLUT_KEY_RIGHT and Player.xPos + 6 <= Road.rightSide:
            Player.moveRight = True
            Player.nextPosition += 5

        if key == GLUT_KEY_LEFT and Player.xPos - 6 >= Road.leftSide:

            Player.moveLeft = True
            Player.nextPosition -= 5

        if key == GLUT_KEY_F1:
            print('Exiting Space Odyssey, see you later!')
            sys.exit()


class Score:
    currentScore = maxScore = 0

    def updateScore():
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        Score.drawString("Score : ", 300, 3200, 0.2)
        Score.drawString(str(Score.currentScore), 900, 3200, 0.2)
        Score.drawString("HIGH SCORE : ", 610, 6200, 0.1)
        Score.drawString(str(Score.maxScore), 1700, 6200, 0.1)
        glEnable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)

    def drawString(text, xPos, yPos, scaleFactor, lineWidth=1):
        text_encoded = text.encode()
        glLineWidth(lineWidth)
        glColor(1, 1, 1, 1)

        Display.orthographicProjection()
        glPushMatrix()
        glLoadIdentity()

        glScale(scaleFactor, scaleFactor, 1)
        glTranslate(xPos, yPos, 1)

        for x in text_encoded:
            glutStrokeCharacter(GLUT_STROKE_ROMAN, x)

        Display.perspectiveProjection()
        glPopMatrix()

    def reset():
        Score.maxScore = max(Score.maxScore, Score.currentScore)
        Score.currentScore = 0


class State:
    currentState = 1
    playing = 1
    gameExit = 2
    playAgain = 3
    collision = 4

    def updateState():
        if State.currentState == State.gameExit:
            setBlocks.reset()
            Player.reset()
            Skybox.reset()
            sys.exit(0)
        if State.currentState == State.playAgain:
            setBlocks.reset()
            setBlocks.init()
            Player.reset()
            Player.init()
            Score.reset()
            Skybox.reset()
            State.currentState = State.playing

        Light.randomize()
        Skybox.draw()
        Road.draw()
        Player.draw()
        setBlocks.draw()
        Score.updateScore()
        


def handleState(key, x, y):
    if key == b" " and State.currentState == State.collision:
        State.currentState = State.playAgain
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.74)
    if key == b"n" and State.currentState == State.collision:
        State.currentState = State.gameExit


def timer(v):
    render()
    glutTimerFunc(int((1000/Display.FPS)), timer, 10)


def render():

    glClearColor(1, 1, 1, 1)
    glEnable(GL_DEPTH_TEST)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    State.updateState()

    glutSwapBuffers()


def main():
    Display.init()
    Player.init()
    Skybox.init()
    BlockLoader.init()
    setBlocks.init()
    Road.init(20)
    Fog.init()
    glutTimerFunc(0, timer, 10)
    pygame.init()
    pygame.mixer.music.load('./Music/Beginners-Falafel.wav')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.74)
    glutMainLoop()


main()
