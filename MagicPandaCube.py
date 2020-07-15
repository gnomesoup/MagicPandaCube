import builtins
from panda3d.core import AmbientLight
from panda3d.core import Vec3, Vec4, Plane, Point3
from panda3d.core import Material
from panda3d.core import CollisionTraverser
from panda3d.core import CollisionHandlerQueue
from panda3d.core import CollisionNode
from panda3d.core import CollisionSphere
from panda3d.core import CollisionPlane
from panda3d.core import NodePathCollection
from direct.gui.DirectGui import OnscreenText
from direct.interval.LerpInterval import LerpHprInterval
from direct.interval.LerpInterval import LerpScaleInterval
from direct.interval.IntervalGlobal import Sequence
from direct.showbase.ShowBase import ShowBase
from panda3d.core import GeomNode
import sys

# Camera constants
CAMERADIST = 8


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


# Materials
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


def colorIf(cObject, cDirection, cMaterial, eMaterial, cCoord, cIndex):
    oldMat = cObject.findMaterial(cDirection)
    if cCoord == cIndex:
        cObject.replaceMaterial(oldMat, cMaterial)
    else:
        cObject.replaceMaterial(oldMat, eMaterial)


app = ShowBase()
app.title = OnscreenText(text="Rubik's Cube Simulator",
                              parent=builtins.base.a2dBottomCenter,
                              fg=(1, 1, 1, 1),
                              shadow=(0, 0, 0, .5),
                              pos=(0, .1),
                              scale=.1)

builtins.base.disableMouse()
# builtins.camera.setPos(CAMERADIST, CAMERADIST * .75, CAMERADIST)
builtins.camera.setPos(-CAMERADIST * .75, CAMERADIST, CAMERADIST)
builtins.camera.lookAt(0, 0, 0)
cameraRig = builtins.render.attachNewNode("CameraRig")
builtins.camera.reparentTo(cameraRig)

ambientLight = AmbientLight("ambientLight")
ambientLight.setColor((1, 1, 1, 1))
builtins.render.setLight(builtins.render.attachNewNode(ambientLight))

collisionTraverser = CollisionTraverser()
# builtins.base.cTrav = collisionTraverser

collisionHandler = CollisionHandlerQueue()

sliceTypes = {"Up": Plane(Vec3(0, 0, -1), Point3(0, 0, 1)),
              "Down": Plane(Vec3(0, 0, 1), Point3(0, 0, -1)),
              "Equator": Plane(Vec3(0, 0, 1), Point3(0, 0, 0)),
              "Front": Plane(Vec3(0, -1, 0), Point3(0, 1, 0)),
              "Back": Plane(Vec3(0, 1, 0), Point3(0, -1, 0)),
              "Standing": Plane(Vec3(0, 1, 0), Point3(0, 0, 0)),
              "Left": Plane(Vec3(-1, 0, 0), Point3(1, 0, 0)),
              "Right": Plane(Vec3(1, 0, 0), Point3(-1, 0, 0)),
              "Middle": Plane(Vec3(1, 0, 0), Point3(0, 0, 0))}


collisionSliceHolder = cameraRig.attachNewNode("collisionSlices")
collisionSlices = [None for i in range(len(sliceTypes))]
for i in range(len(sliceTypes)):
    sliceType = list(sliceTypes.keys())[i]
    cNode = CollisionNode(sliceType)
    collisionSlices[i] = collisionSliceHolder.attachNewNode(cNode)
    cNode.addSolid(CollisionPlane(sliceTypes[sliceType]))
    collisionSlices[i].setTag("sliceType", sliceType)
    # cNode.setFromCollideMask(GeomNode.getDefaultCollideMask())

cubies = [None for i in range(27)]
cubieCollisions = [None for i in range(27)]
i = 0
for x in range(3):
    for y in range(3):
        for z in range(3):
            pos = Vec3(x - 1, y - 1, z - 1)
            nodeName = "cubie" + str(x) + str(y) + str(z)
            cubies[i] = builtins.loader.loadModel("cubie")
            nodeName = "collision" + str(x) + str(y) + str(z)
            cNode = CollisionNode(nodeName)
            cNode.addSolid(CollisionSphere(0, 0, 0, .5))
            cubieCollisions[i] = cubies[i].attachNewNode(cNode)
            cubies[i].setPos(pos)
            cubies[i].setScale(.95)
            cubies[i].reparentTo(builtins.render)
            collisionTraverser.addCollider(cubieCollisions[i],
                                           collisionHandler)
            colorIf(cubies[i], "Up", yellow, black, z, 2)
            colorIf(cubies[i], "Down", white, black, z, 0)
            colorIf(cubies[i], "Front", blue, black, y, 2)
            colorIf(cubies[i], "Back", green, black, y, 0)
            colorIf(cubies[i], "Left", orange, black, x, 2)
            colorIf(cubies[i], "Right", red, black, x, 0)
            i = i + 1

tempNode = cameraRig.attachNewNode("tempNode")


def reparentToRender(task):
    print("ReparentToRender")
    global cubies
    # for cubie in cubies:
    #     cubie.wrtReparentTo(builtins.render)
    #     cubie.setScale(.95)
    # tNode = builtins.render.find("tempNode")
    # tNode.removeNode()


def getCollisionCollection(sliceType):
    ignoreSlice = None
    collisionCollection = NodePathCollection()
    collisionTraverser.traverse(collisionSliceHolder)
    collisionCount = collisionHandler.getNumEntries()
    # check if the slice is internal
    sliceKeys = list(sliceTypes.keys())
    sliceIndex = sliceKeys.index(sliceType)
    if sliceIndex % 3 == 2:
        ignoreSlice = sliceKeys[sliceIndex - 1]
        print(ignoreSlice)
    for i in range(collisionCount):
        intoNode = collisionHandler.getEntry(i).getIntoNodePath()
        tag = intoNode.findNetTag("sliceType")
        if str(tag).endswith(sliceType):
            fromNode = collisionHandler.getEntry(i).getFromNodePath()
            collisionCollection.addPath(fromNode.getParent())
    if ignoreSlice:
        for i in range(collisionCount):
            intoNode = collisionHandler.getEntry(i).getIntoNodePath()
            tag = intoNode.findNetTag("sliceType")
            if str(tag).endswith(ignoreSlice):
                fromNode = collisionHandler.getEntry(i).getFromNodePath()
                collisionCollection.removePath(fromNode.getParent())
    return collisionCollection


def rotateSlice(sliceType, hAngle, pAngle, rAngle, task):
    print("Rotate Slice: " + sliceType)
    children = tempNode.getChildren()
    children.wrtReparentTo(builtins.render)
    tempNode.clearTransform()
    nodes = getCollisionCollection(sliceType)
    nodes.wrtReparentTo(tempNode)
    # for cubie in cubies:
    #     pos = cameraRig.getPos(cubie)
    #     if int(pos[cubePos]) == cubieCoord:
    #         cubie.wrtReparentTo(tempNode)
    i = LerpHprInterval(tempNode, .2, Vec3(hAngle, pAngle, rAngle))
    i.start()


def rotateSliceTask(sliceType, hAngle, pAngle, rAngle):
    builtins.taskMgr.add(rotateSlice, "rotateSlice",
                         extraArgs=[sliceType,
                                    hAngle,
                                    pAngle,
                                    rAngle],
                         appendTask=True)


def rotateCamera(hAngle, pAngle, rAngle):
    print("Rotate Camera")
    tempNode.getChildren().wrtReparentTo(builtins.render)
    hpr = cameraRig.getHpr(builtins.render)
    i = LerpHprInterval(cameraRig, .1, Vec3(
                        hpr[0] + hAngle,
                        hpr[1] + pAngle,
                        hpr[2] + rAngle))
    i.start()


def onSpace():
    print("onSpace")
    flashRows = Sequence(name="flashRows")
    tempNode.getChildren().wrtReparentTo(builtins.render)
    tempNode.clearTransform()
    getCollisionCollection("Front").wrtReparentTo(tempNode)
    scaleBigger = LerpScaleInterval(tempNode, .2, 1.1)
    scaleOriginal = LerpScaleInterval(tempNode, .2, 1)
    flashRows.append(scaleBigger)
    flashRows.append(scaleOriginal)
    flashRows.start()


app.accept("q", sys.exit)
app.accept("space", onSpace)
app.accept("arrow_left", rotateCamera, [-90, 0, 0])
app.accept("arrow_right", rotateCamera, [90, 0, 0])
app.accept("arrow_up", rotateCamera, [0, 0, 90])
app.accept("arrow_down", rotateCamera, [0, 0, -90])
app.accept("x", rotateCamera, [0, -90, 0])
app.accept("shift-x", rotateCamera, [0, 90, 0])
app.accept("y", rotateCamera, [0, 0, -90])
app.accept("shift-y", rotateCamera, [0, 0, 90])
app.accept("z", rotateCamera, [0, -90, 0])
app.accept("shift-z", rotateCamera, [0, 90, 0])
app.accept("r", rotateSliceTask, ["Right", 0, 90, 0])
app.accept("shift-r", rotateSliceTask, ["Right", 0, -90, 0])
app.accept("l", rotateSliceTask, ["Left", 0, -90, 0])
app.accept("shift-l", rotateSliceTask, ["Left", 0, 90, 0])
app.accept("m", rotateSliceTask, ["Middle", 0, 90, 0])
app.accept("shift-m", rotateSliceTask, ["Middle", 0, -90, 0])
app.accept("f", rotateSliceTask, ["Front", 0, 0, -90])
app.accept("shift-f", rotateSliceTask, ["Front", 0, 0, 90])
app.accept("b", rotateSliceTask, ["Back", 0, 0, 90])
app.accept("shift-b", rotateSliceTask, ["Back", 0, 0, -90])
app.accept("s", rotateSliceTask, ["Standing", 0, 0, -90])
app.accept("shift-s", rotateSliceTask, ["Standing", 0, 0, 90])
app.accept("u", rotateSliceTask, ["Up", -90, 0, 0])
app.accept("shift-u", rotateSliceTask, ["Up", 90, 0, 0])
app.accept("d", rotateSliceTask, ["Down", -90, 0, 0])
app.accept("shift-d", rotateSliceTask, ["Down", 90, 0, 0])
app.accept("e", rotateSliceTask, ["Equator", -90, 0, 0])
app.accept("shift-e", rotateSliceTask, ["Equator", 90, 0, 0])

app.run()
