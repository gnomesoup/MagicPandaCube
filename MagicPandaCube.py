from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import LVector3, Vec4
from panda3d.core import Material
from panda3d.core import Texture
from direct.gui.DirectGui import OnscreenText
import builtins

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

        builtins.base.disableMouse()
        # builtins.camera.setPosHpr(5, -5, 5, -45, -45, 0)  # Set the cameras' position
        builtins.camera.setPosHpr(6, -6, 6, 45, -40, 0)
        builtins.base.camLens.setNear(1)

        self.loadModels()
        self.setupLights()

    def loadModels(self):
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
        #Load a corner
        # self.corner = builtins.loader.loadModel("./corner.egg")
        # self.corner.reparentTo(render)
        # red = Material()
        # originalMat = self.corner.findMaterial("Material.004")
        # self.corner.replaceMaterial(originalMat, red)
        # originalText = self.corner.findTexture("pbr-fallback")
        # originalText.clear()
        # self.corner.clearTexture()
        self.edge = builtins.loader.loadModel("./edge.egg")
        # print(self.edge.findAllMaterials())
        sideMat = self.edge.findMaterial("Side")
        self.edge.replaceMaterial(sideMat, blue)
        frontMat = self.edge.findMaterial("Face")
        self.edge.replaceMaterial(frontMat, orange)
        self.edge.reparentTo(render)
        self.center = builtins.loader.loadModel("./center.egg")
        self.center.reparentTo(render)

    def setupLights(self):
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((.8, .8, .8, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(LVector3(0, 45, -45))
        directionalLight.setColor((0.2, 0.2, 0.2, 1))
        render.setLight(render.attachNewNode(directionalLight))
        render.setLight(render.attachNewNode(ambientLight))

app = MagicPandaCube()
app.run()