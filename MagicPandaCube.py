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
from direct.gui.DirectGui import OnscreenImage
from direct.gui.DirectGui import DirectDialog
from direct.gui.DirectGui import DirectButton
from direct.gui.DirectGui import DGG
from direct.interval.LerpInterval import LerpHprInterval
from direct.interval.LerpInterval import LerpScaleInterval
from direct.interval.IntervalGlobal import Sequence, Wait
from direct.showbase.ShowBase import ShowBase
import sys
import random


# GUI functions
def button(buttonText, buttonPos, buttonCommand):
    DirectButton(text=(buttonText),
                 text_scale=2,
                 text_pos=(0, -.6),
                 scale=0.07,
                 pos=buttonPos,
                 frameSize=(-2, 2, -2, 2),
                 command=buttonCommand)


def helpDialog():
    print("Help!")
    gameInfo.show()


def randomizeList(num):
    i = 0
    outList = []
    while i < num:
        r = random.randint(0, 17)
        key = list(rotateSliceArguments.keys())[r]
        if i > 0 and outList[-1][0] == key[0]:
            continue
        i = i + 1
        outList.append(key)
    print(outList)
    return outList


def randomizeCube():
    global s
    print("Randomize")
    rotateList = randomizeList(20)
    i = 0
    for rotation in rotateList:
        args = rotateSliceArguments[rotation]
        builtins.taskMgr.doMethodLater(i * .3, rotateSliceTask,
                                       name="randomize" + str(i),
                                       extraArgs=args)
        i = i + 1
    return rotateList


# model functions
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


def colorIf(cObject, cDirection, cMaterial, eMaterial, cCoord, cIndex):
    oldMat = cObject.findMaterial(cDirection)
    if cCoord == cIndex:
        cObject.replaceMaterial(oldMat, cMaterial)
    else:
        cObject.replaceMaterial(oldMat, eMaterial)


# game action functions


def getCollisionCollection(sliceType):
    ignoreSlice = None
    # create a collection of nodes that motch
    collisionCollection = NodePathCollection()
    # run the check for collisions
    collisionTraverser.traverse(collisionSliceHolder)
    collisionCount = collisionHandler.getNumEntries()
    # check if the slice is internal
    sliceKeys = list(sliceTypes.keys())
    sliceIndex = sliceKeys.index(sliceType)
    if sliceIndex % 3 == 2:
        ignoreSlice = sliceKeys[sliceIndex - 1]
    # go through the collisions an check for a match
    for i in range(collisionCount):
        intoNode = collisionHandler.getEntry(i).getIntoNodePath()
        tag = intoNode.findNetTag("sliceType")
        if str(tag).endswith(sliceType):
            fromNode = collisionHandler.getEntry(i).getFromNodePath()
            collisionCollection.addPath(fromNode.getParent())
    # remove extra nodes if the slice is an internal one
    if ignoreSlice:
        for i in range(collisionCount):
            intoNode = collisionHandler.getEntry(i).getIntoNodePath()
            tag = intoNode.findNetTag("sliceType")
            if str(tag).endswith(ignoreSlice):
                fromNode = collisionHandler.getEntry(i).getFromNodePath()
                collisionCollection.removePath(fromNode.getParent())
    # return the matched collisions
    return collisionCollection


def checkSolved():
    solved = True
    print("checkSolve")
    for i in range(3):
        matchCount = [0, 0, 0]
        matchPos = None
        for cubie in cubies:
            name = cubie.name
            originalPos = (int(name[5]) - 1,
                           int(name[6]) - 1,
                           int(name[7]) - 1)
            pos = cubie.getPos(builtins.render)
            currentPos = (round(pos[0]), round(pos[1]), round(pos[2]))
            if currentPos[i] == 1:
                if matchPos is None:
                    matchPos = originalPos
                for j in range(3):
                    if matchPos[j] == originalPos[j]:
                        matchCount[j] = matchCount[j] + 1
        print(matchCount)
        if 9 not in matchCount:
            solved = False
    if solved:
        print("Solved!")


def rotateSlice(sliceType, hAngle, pAngle, rAngle):
    children = tempNode.getChildren()
    children.wrtReparentTo(builtins.render)
    tempNode.clearTransform()
    nodes = getCollisionCollection(sliceType)
    nodes.wrtReparentTo(tempNode)
    i = LerpHprInterval(tempNode, 0.2, Vec3(hAngle, pAngle, rAngle))
    return i


def rotateSliceTask(sliceType, hAngle, pAngle, rAngle):
    global s
    if s:
        s.finish()
    i = rotateSlice(sliceType, hAngle, pAngle, rAngle)
    s = Sequence(i, name="rotate" + sliceType)
    s.start()


def rotateCube(hAngle, pAngle, rAngle):
    referenceHpr = referenceNode.getHpr(builtins.render)
    referenceNode.setHpr(referenceHpr[0] + hAngle,
                         referenceHpr[1] + pAngle,
                         referenceHpr[2] + rAngle)
    if tempNode.getNumChildren() > 0:
        tempNode.getChildren().wrtReparentTo(builtins.render)
    tempNode.clearTransform()
    for cubie in cubies:
        cubie.wrtReparentTo(tempNode)
    i = LerpHprInterval(tempNode, 0.1, Vec3(hAngle, pAngle, rAngle))
    return i


def rotateCubeTask(hAngle, pAngle, rAngle):
    global s
    if s:
        s.finish()
    i = rotateCube(hAngle, pAngle, rAngle)
    s = Sequence(i, name="roateCube")
    s.start()


# Camera constants
CAMERADIST = 8

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


# Dictionary of moves
rotateSliceArguments = {
    "U": ["Up", -90, 0, 0],
    "U'": ["Up", 90, 0, 0],
    "U2": ["Up", -180, 0, 0],
    "D": ["Down", -90, 0, 0],
    "D'": ["Down", 90, 0, 0],
    "D2": ["Down", -180, 0, 0],
    "F": ["Front", 0, 0, -90],
    "F'": ["Front", 0, 0, 90],
    "F2": ["Front", 0, 0, -180],
    "B": ["Back", 0, 0, 90],
    "B'": ["Back", 0, 0, -90],
    "B2": ["Back", 0, 0, 180],
    "L": ["Left", 0, -90, 0],
    "L'": ["Left", 0, 90, 0],
    "L2": ["Left", 0, -180, 0],
    "R": ["Right", 0, 90, 0],
    "R'": ["Right", 0, -90, 0],
    "R2": ["Right", 0, 180, 0],
    "E": ["Equator", -90, 0, 0],
    "E'": ["Equator", 90, 0, 0],
    "E2": ["Equator", -180, 0, 0],
    "S": ["Standing", 0, 0, -90],
    "S'": ["Standing", 0, 0, 90],
    "S2": ["Standing", 0, 0, -180],
    "M": ["Middle", 0, 90, 0],
    "M'": ["Middle", 0, -90, 0],
    "M2": ["Middle", 0, -180, 0]
}


# Let the game begin
app = ShowBase()
app.title = OnscreenText(
    text="Rubik's Cube Simulator",
    parent=builtins.base.a2dBottomCenter,
    fg=(1, 1, 1, 1),
    shadow=(0, 0, 0, 0.5),
    pos=(0, 0.1),
    scale=0.1,
)

# Load an image object
imagePath = "galaxy.jpg"
background = OnscreenImage(parent=builtins.render2dp, image=imagePath)
# Force the rendering to render the background image first
# (so that it will be put to the bottom of the scene since
# other models will be necessarily drawn on top)
builtins.base.cam2dp.node().getDisplayRegion(0).setSort(-20)

builtins.base.disableMouse()
# builtins.camera.setPos(CAMERADIST, CAMERADIST * .75, CAMERADIST)
builtins.camera.setPos(-CAMERADIST * 0.75, CAMERADIST, CAMERADIST)
builtins.camera.lookAt(0, 0, 0)
cameraRig = builtins.render.attachNewNode("CameraRig")
builtins.camera.reparentTo(cameraRig)

ambientLight = AmbientLight("ambientLight")
ambientLight.setColor((1, 1, 1, 1))
builtins.render.setLight(builtins.render.attachNewNode(ambientLight))

collisionTraverser = CollisionTraverser()
# builtins.base.cTrav = collisionTraverser
collisionHandler = CollisionHandlerQueue()


sliceTypes = {
    "Up": Plane(Vec3(0, 0, -1), Point3(0, 0, 1)),
    "Down": Plane(Vec3(0, 0, 1), Point3(0, 0, -1)),
    "Equator": Plane(Vec3(0, 0, 1), Point3(0, 0, 0)),
    "Front": Plane(Vec3(0, -1, 0), Point3(0, 1, 0)),
    "Back": Plane(Vec3(0, 1, 0), Point3(0, -1, 0)),
    "Standing": Plane(Vec3(0, 1, 0), Point3(0, 0, 0)),
    "Left": Plane(Vec3(-1, 0, 0), Point3(1, 0, 0)),
    "Right": Plane(Vec3(1, 0, 0), Point3(-1, 0, 0)),
    "Middle": Plane(Vec3(1, 0, 0), Point3(0, 0, 0)),
}


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
            cubies[i].name = nodeName
            nodeName = "collision" + str(x) + str(y) + str(z)
            cNode = CollisionNode(nodeName)
            cNode.addSolid(CollisionSphere(0, 0, 0, 0.5))
            cubieCollisions[i] = cubies[i].attachNewNode(cNode)
            cubies[i].setPos(pos)
            cubies[i].setScale(0.95)
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
referenceNode = builtins.render.attachNewNode("referenceNode")
collisionTraverser.traverse(collisionSliceHolder)

# placeholder for sequence
s = None

app.accept("q", sys.exit)
app.accept("space", checkSolved)
app.accept("arrow_left", rotateCubeTask, [-90, 0, 0])
app.accept("arrow_right", rotateCubeTask, [90, 0, 0])
app.accept("arrow_up", rotateCubeTask, [0, 90, 0])
app.accept("arrow_down", rotateCubeTask, [0, -90, 0])
app.accept("x", rotateCubeTask, [0, 90, 0])
app.accept("shift-x", rotateCubeTask, [0, -90, 0])
app.accept("y", rotateCubeTask, [0, 0, -90])
app.accept("shift-y", rotateCubeTask, [0, 0, 90])
app.accept("z", rotateCubeTask, [-90, 0, 0])
app.accept("shift-z", rotateCubeTask, [90, 0, 0])
app.accept("r", rotateSliceTask, rotateSliceArguments["R"])
app.accept("shift-r", rotateSliceTask, rotateSliceArguments["R'"])
app.accept("l", rotateSliceTask, rotateSliceArguments["L"])
app.accept("shift-l", rotateSliceTask, rotateSliceArguments["L'"])
app.accept("m", rotateSliceTask, rotateSliceArguments["M"])
app.accept("shift-m", rotateSliceTask, rotateSliceArguments["M'"])
app.accept("f", rotateSliceTask, rotateSliceArguments["F"])
app.accept("shift-f", rotateSliceTask, rotateSliceArguments["F'"])
app.accept("b", rotateSliceTask, rotateSliceArguments["B"])
app.accept("shift-b", rotateSliceTask, rotateSliceArguments["B'"])
app.accept("s", rotateSliceTask, rotateSliceArguments["S"])
app.accept("shift-s", rotateSliceTask, rotateSliceArguments["S'"])
app.accept("u", rotateSliceTask, rotateSliceArguments["U"])
app.accept("shift-u", rotateSliceTask, rotateSliceArguments["U'"])
app.accept("d", rotateSliceTask, rotateSliceArguments["D"])
app.accept("shift-d", rotateSliceTask, rotateSliceArguments["D'"])
app.accept("e", rotateSliceTask, rotateSliceArguments["E"])
app.accept("shift-e", rotateSliceTask, rotateSliceArguments["E'"])
app.accept("3", randomizeCube)
app.accept("?", helpDialog)

gameInfo = DirectDialog(frameSize=(-.8, .8, -.8, .8),
                        fadeScreen=.4,
                        relief=DGG.FLAT)
gameInfo.hide()

button("s", (-1, 0, -.5), randomizeCube)
button("?", (-1, 0, -.8), helpDialog)

app.run()
