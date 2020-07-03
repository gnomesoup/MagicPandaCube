from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import LVector3, Vec4
from panda3d.core import Material
from panda3d.core import Texture
from panda3d.core import NodePath
from direct.gui.DirectGui import OnscreenText
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
        self.accept('Q', sys.exit)  # Escape quits
        builtins.base.disableMouse()
        self.cameraPosition = 0
        builtins.camera.setPos(CAMERAPOS[self.cameraPosition])
        builtins.camera.lookAt(0, 0, 0)
        builtins.base.camLens.setNear(1)

        self.loadModels()
        self.setupLights()

        self.accept("arrow_right", self.changeCameraXY, [1])
        self.accept("arrow_left", self.changeCameraXY, [-1])
        self.accept("arrow_up", self.changeCameraZ, [-1])
        self.accept("arrow_down", self.changeCameraZ, [1])

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

        # #Load a corner
        # self.corner = builtins.loader.loadModel("./corner.egg")
        # self.corner.reparentTo(builtins.render)
        # faceMat = self.corner.findMaterial("Face")
        # self.corner.replaceMaterial(faceMat, blue)
        # sideMat = self.corner.findMaterial("Side")
        # self.corner.replaceMaterial(sideMat, blue)
        # topMat = self.corner.findMaterial("Top")
        # self.corner.replaceMaterial(topMat, blue)

        # self.edge = builtins.loader.loadModel("./edge.egg")
        # sideMat = self.edge.findMaterial("Side")
        # self.edge.replaceMaterial(sideMat, orange)
        # faceMat = self.edge.findMaterial("Face")
        # self.edge.replaceMaterial(faceMat, orange)

        # self.center = builtins.loader.loadModel("./center.egg")
        # faceMat = self.center.findMaterial("Face")
        # self.center.replaceMaterial(faceMat, yellow)

        self.cube = builtins.render.attachNewNode("cube")
        self.cube.setPos(-1.05, -1.05, -1.05)
        self.cubies = [None for i in range(27)]
        i = 0
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    cubieType = "cubie"
                    self.cubies[i] = builtins.loader.loadModel(cubieType)
                    self.cubies[i].setPos(x * 1.05, y * 1.05, z * 1.05)
                    self.cubies[i].reparentTo(self.cube)
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
                    # print(str(i) + ":" + str(x) + ", " + str(y) + ", " + str(z) + ":" + cubieType)

    def setupLights(self):
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((.8, .8, .8, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(LVector3(0, 45, -45))
        directionalLight.setColor((0.2, 0.2, 0.2, 1))
        builtins.render.setLight(builtins.render.attachNewNode(directionalLight))
        builtins.render.setLight(builtins.render.attachNewNode(ambientLight))

    def changeCameraXY(self, cPosition):
        self.cameraPosition = (self.cameraPosition + cPosition) % 4
        builtins.camera.setPos(CAMERAPOS[self.cameraPosition])
        builtins.camera.lookAt(0, 0, 0)

    def changeCameraZ(self, cPosition):
        currentPos = builtins.camera.getPos()
        builtins.camera.setPos(currentPos[0], currentPos[1], cPosition * CAMERADIST)
        builtins.camera.lookAt(0, 0, 0)

app = MagicPandaCube()
app.run()