from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight
from panda3d.core import Vec3, Vec4, LVector3f
from panda3d.core import Material
from direct.gui.DirectGui import OnscreenText
from direct.interval.LerpInterval import LerpHprInterval
from direct.interval.LerpInterval import LerpScaleInterval
from direct.interval.IntervalGlobal import Sequence, Parallel
import sys
import builtins

# Camera constants
CAMERADIST = 8
CAMERAPOS = (
    (-CAMERADIST, CAMERADIST, CAMERADIST),
    (-CAMERADIST, -CAMERADIST, CAMERADIST),
    (CAMERADIST, -CAMERADIST, CAMERADIST),
    (CAMERADIST, CAMERADIST, CAMERADIST)
    )


def hexColor(hex):
    if len(hex) < 8:
        hexa = "ff"
    else:
        hexa = hex[6:8]
    hc = [hex[0:2], hex[2:4], hex[4:6], hexa]
    color = Vec4()
    for i in range(4):
        color[i] = int("0x" + hc[i], 16) / 255
    return color


def detachWithTransform(childNode):
    pos = builtins.render.getRelativePoint(childNode, (0, 0, 0))
    nodeVector = builtins.render.getRelativeVector(childNode, (0, 1, 0))
    childNode.detachNode()
    childNode.setPos(pos)
    childNode.setHpr(nodeVector)
    return childNode


class MagicPandaCube(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        self.title = OnscreenText(text="Rubik's Cube Simulator",
                                  parent=builtins.base.a2dBottomCenter,
                                  fg=(1, 1, 1, 1),
                                  shadow=(0, 0, 0, .5),
                                  pos=(0, .1),
                                  scale=.1)

        self.accept('escape', sys.exit)  # Escape quits
        self.accept('q', sys.exit)  # Escape quits
        builtins.base.disableMouse()
        self.cameraPosition = 0
        builtins.camera.setPos(CAMERAPOS[self.cameraPosition])
        builtins.camera.lookAt(0, 0, 0)
        builtins.base.camLens.setNear(1)

        self.loadModels()
        self.setupLights()

        self.accept("arrow_right", self.rotateCube, [90])
        self.accept("arrow_left", self.rotateCube, [-90])
        self.accept("arrow_up", self.changeCameraZ, [-1])
        self.accept("arrow_down", self.changeCameraZ, [1])

        self.accept("p", self.printCoords)
        self.accept("x", self.reparentToRender, [self.cubies])

        self.accept("f", self.rotateSlice, [1, 1, 0, 0, 90])
        self.accept("shift-f", self.rotateSlice, [1, 1, 0, 0, -90])
        self.accept("r", self.rotateSlice, [0, 1, 0, 90, 0])
        self.accept("shift-r", self.rotateSlice, [0, 1, 0, -90, 0])

        print(LVector3f())

    def loadModels(self):
        black = Material()
        black.setAmbient((0, 0, 0, 1))
        white = Material()
        white.setAmbient((1, 1, 1, 1))
        blue = Material()
        blue.setAmbient(hexColor("40a4d8"))
        red = Material()
        red.setAmbient(hexColor("db3837"))
        green = Material()
        green.setAmbient(hexColor("b2c225"))
        orange = Material()
        orange.setAmbient(hexColor("f4941f"))
        yellow = Material()
        yellow.setAmbient(hexColor("fecc30"))

        self.cube = builtins.render.attachNewNode("cube")
        self.cubies = [None for i in range(27)]
        i = 0
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    cubieType = "cubie"
                    self.cubies[i] = builtins.loader.loadModel(cubieType)
                    self.cubies[i].setScale(.95)
                    self.cubies[i].setPos(x - 1, y - 1, z - 1)
                    self.cubies[i].reparentTo(render)
                    if(z == 2):
                        oldMat = self.cubies[i].findMaterial("Up")
                        self.cubies[i].replaceMaterial(oldMat, yellow)
                    else:
                        oldMat = self.cubies[i].findMaterial("Up")
                        self.cubies[i].replaceMaterial(oldMat, black)
                    if(z == 0):
                        oldMat = self.cubies[i].findMaterial("Down")
                        self.cubies[i].replaceMaterial(oldMat, white)
                    else:
                        oldMat = self.cubies[i].findMaterial("Down")
                        self.cubies[i].replaceMaterial(oldMat, black)
                    if(y == 2):
                        oldMat = self.cubies[i].findMaterial("Front")
                        self.cubies[i].replaceMaterial(oldMat, blue)
                    else:
                        oldMat = self.cubies[i].findMaterial("Front")
                        self.cubies[i].replaceMaterial(oldMat, black)
                    if(y == 0):
                        oldMat = self.cubies[i].findMaterial("Back")
                        self.cubies[i].replaceMaterial(oldMat, green)
                    else:
                        oldMat = self.cubies[i].findMaterial("Back")
                        self.cubies[i].replaceMaterial(oldMat, black)
                    if(x == 2):
                        oldMat = self.cubies[i].findMaterial("Left")
                        self.cubies[i].replaceMaterial(oldMat, orange)
                    else:
                        oldMat = self.cubies[i].findMaterial("Left")
                        self.cubies[i].replaceMaterial(oldMat, black)
                    if(x == 0):
                        oldMat = self.cubies[i].findMaterial("Right")
                        self.cubies[i].replaceMaterial(oldMat, red)
                    else:
                        oldMat = self.cubies[i].findMaterial("Right")
                        self.cubies[i].replaceMaterial(oldMat, black)
                    i = i + 1

    def setupLights(self):
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((1, 1, 1, 1))
        builtins.render.setLight(builtins.render.attachNewNode(ambientLight))

    def changeCameraXY(self, cPosition):
        self.cameraPosition = (self.cameraPosition + cPosition) % 4
        builtins.camera.setPos(CAMERAPOS[self.cameraPosition])
        builtins.camera.lookAt(0, 0, 0)

    def changeCameraZ(self, cPosition):
        currentPos = builtins.camera.getPos()
        builtins.camera.setPos(currentPos[0], currentPos[1],
                               cPosition * CAMERADIST)
        builtins.camera.lookAt(0, 0, 0)

    def rotateCube(self, angle):
        for cubie in self.cubies:
            cubie = detachWithTransform(cubie)
            cubie.reparentTo(self.cube)
        hpr = self.cube.getHpr()
        i = LerpHprInterval(self.cube, (abs(angle) / 360),
                            (hpr[0] + angle, hpr[1], hpr[2]))
        i.start()

    def rotateSlice(self, cubePos, cubieCoord, hAngle, pAngle, rAngle):
        print("Rotate Slice:")
        for cubie in self.cubies:
            cubie = detachWithTransform(cubie)
            pos = cubie.getPos()
            if int(pos[cubePos]) == cubieCoord:
                cubie.reparentTo(self.cube)
            else:
                cubie.reparentTo(builtins.render)
        hpr = self.cube.getHpr()
        i = LerpHprInterval(self.cube, .2, Vec3(hpr[0] + hAngle,
                                                hpr[1] + pAngle,
                                                hpr[2] + rAngle))
        i.start()

    def printCoords(self):
        self.flashGroups()
        for cubie in self.cubies:
            # print(cubieHost.getNode(0))
            print("Global:" + str(pos) + " " + str(int(pos[1])))

    def flashGroups(self):
        flashOn = Parallel(name="FlashGroupOn")
        flashOff = Parallel(name="FlashGroupOff")
        for cubie in self.cubies:
            cubie = detachWithTransform(cubie)
            pos = cubie.getPos()
            if int(pos[1]) == 1:
                cubie.reparentTo(self.cube)
        flashOn.append(LerpScaleInterval(self.cube, .2, 1.1))
        flashOff.append(LerpScaleInterval(self.cube, .2, 1))
        flashGroup = Sequence(flashOn, flashOff, name="FlashGroupOnOff")
        flashGroup.start()

    def reparentToRender(self, nodeList):
        for item in nodeList:
            item = detachWithTransform(item)
            item.reparentTo(builtins.render)
        print("Reparented")


app = MagicPandaCube()
app.run()
