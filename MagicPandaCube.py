import builtins
from panda3d.core import AmbientLight
from panda3d.core import BitMask32
from panda3d.core import Vec3, Vec4, Plane, Point3
from panda3d.core import Material
from panda3d.core import CollisionTraverser
from panda3d.core import CollisionHandlerQueue
from panda3d.core import CollisionNode
from panda3d.core import CollisionSphere
from panda3d.core import CollisionPlane
from panda3d.core import CollisionRay
from panda3d.core import NodePathCollection
from panda3d.core import TransparencyAttrib
from direct.gui.DirectGui import OnscreenText
from direct.gui.DirectGui import OnscreenImage
from direct.gui.DirectGui import DirectDialog
from direct.gui.DirectGui import DirectButton
from direct.gui.DirectGui import DGG
from direct.interval.LerpInterval import LerpHprInterval
from direct.interval.LerpInterval import LerpScaleInterval
from direct.interval.IntervalGlobal import Sequence, Func
from direct.showbase.ShowBase import ShowBase
import sys
import random
from datetime import datetime


# GUI functions
def button(buttonText,
           buttonPos,
           buttonCommand,
           buttonTextures,
           buttonFrameSize):
    button = DirectButton(text=("", "", buttonText, ""),
                          text_scale=1.3,
                          text_pos=(4.5, -.3),
                          text_fg=(1, 1, 1, 1),
                          text_shadow=(0, 0, 0, 0.5),
                          frameTexture=buttonTextures,
                          scale=0.05,
                          pos=buttonPos,
                          frameSize=(-buttonFrameSize,
                                     buttonFrameSize,
                                     -buttonFrameSize,
                                     buttonFrameSize),
                          relief=DGG.FLAT,
                          parent=builtins.base.a2dBottomLeft,
                          command=buttonCommand)
    button.setTransparency(TransparencyAttrib.MAlpha)
    return button


def helpDialog():
    print("Help!")
    gameInfo.show()


def cubieSetup():
    global cubies
    global cubieCollisions
    i = 0
    for x in range(3):
        for y in range(3):
            for z in range(3):
                pos = Vec3(x - 1, y - 1, z - 1)
                nodeName = "cubie" + str(x) + str(y) + str(z)
                cubie = builtins.loader.loadModel("cubie")
                nodeName = "collision" + str(x) + str(y) + str(z)
                cNode = CollisionNode(nodeName)
                cNode.addSolid(CollisionSphere(0, 0, 0, 0.5))
                cNode.setIntoCollideMask(BitMask32.bit(1))
                cubieCollisions.addPath(cubie.attachNewNode(cNode))
                cubie.setPos(pos)
                cubie.setScale(0.95)
                cubie.reparentTo(builtins.render)
                collisionTraverser.addCollider(cubieCollisions[i],
                                               collisionHandler)
                sideCount = 0
                name = ""
                if colorIf(cubie, "Up", yellow, black, z, 2):
                    sideCount = sideCount + 1
                    name += "Y"
                if colorIf(cubie, "Down", white, black, z, 0):
                    sideCount = sideCount + 1
                    name += "W"
                if colorIf(cubie, "Front", blue, black, y, 2):
                    sideCount = sideCount + 1
                    name += "B"
                if colorIf(cubie, "Back", green, black, y, 0):
                    sideCount = sideCount + 1
                    name += "G"
                if colorIf(cubie, "Left", orange, black, x, 2):
                    sideCount = sideCount + 1
                    name += "O"
                if colorIf(cubie, "Right", red, black, x, 0):
                    sideCount = sideCount + 1
                    name += "R"
                if len(name) == 3:
                    name = "corner" + name
                elif len(name) == 2:
                    name = "edge" + name
                elif len(name) == 1:
                    name = "center" + name
                else:
                    name = "internal"
                cubie.setPythonTag("sideCount", sideCount)
                cubie.setPythonTag("originalPos", pos)
                cubie.name = name
                cubies.addPath(cubie)
                i = i + 1


def cubieReset():
    global turnCount
    turnCount = 0
    checkSolved()
    cubies.reparentTo(builtins.render)
    for cubie in cubies:
        # name = cubie.name
        # pos = Vec3(int(name[5]) - 1,
        #            int(name[6]) - 1,
        #            int(name[7]) - 1)
        pos = cubie.getPythonTag("originalPos")
        cubie.setPos(pos)
        cubie.setHpr(0, 0, 0)
    playButton.show()
    rePlayButton.hide()


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
    return outList


def randomizeCube():
    global s
    global gameStarted
    app.ignoreAll()
    cubieReset()
    playButton.hide()
    print("Randomize")
    rotateList = randomizeList(20)
    i = 0
    if s:
        s.finish()
    s = Sequence(name="randomize")
    for rotation in rotateList:
        args = rotateSliceArguments[rotation]
        # s.append(rotateSlice(args[0], args[1], args[2], args[3]))
        builtins.taskMgr.doMethodLater(i * .3, rotateSliceTask,
                                       name="randomize" + str(i),
                                       extraArgs=args + [False])
        i = i + 1
    builtins.taskMgr.doMethodLater(i * .3, acceptInput,
                                   name="acceptInput",
                                   extraArgs=[app])
    randomizeReport = " ".join(rotateList)
    print(randomizeReport)
    gameStarted = True
    app.title.setText(randomizeReport)
    return randomizeReport


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
        return True
    else:
        cObject.replaceMaterial(oldMat, eMaterial)
        return False


# game action functions
def getCubiesInSlice(sliceType):
    sliceCollection = NodePathCollection()
    slicePoint = sliceTypes[sliceType]
    for i in range(3):
        if slicePoint[i] != 0:
            sliceIndex = i
            sliceIndexValue = slicePoint[i]
    for cubie in cubies:
        pos = cubie.getPos(builtins.render)
        if round(pos[sliceIndex]) == sliceIndexValue:
            sliceCollection.addPath(cubie)
    return sliceCollection


def checkSolved():
    global s
    global turnCount
    global gameStarted
    solved = True
    # print("checkSolved")
    for i in range(3):
        matchPosCount = [0, 0, 0]
        matchPos = None
        matchHpr = None
        for cubie in cubies:
            originalPos = cubie.getPythonTag("originalPos")
            pos = cubie.getPos(builtins.render)
            hpr = cubie.getHpr(builtins.render)
            currentPos = (round(pos[0]), round(pos[1]), round(pos[2]))
            currentHpr = Vec3(abs(round(hpr[0])),
                              abs(round(hpr[1])),
                              abs(round(hpr[2]))).normalized()
            if currentPos[i] == 1:
                if matchPos is None:
                    matchPos = originalPos
                    matchHpr = currentHpr
                # print(name)
                # print(str(matchPos) + " == " + str(originalPos))
                # print(str(matchHpr) + " == " + str(currentHpr))
                # print(cubie.getPythonTag("sideCount"))
                for j in range(3):
                    if (
                        matchPos[j] == originalPos[j]
                        and (matchHpr == currentHpr
                             or cubie.getPythonTag("sideCount") == 1)
                    ):
                        matchPosCount[j] = matchPosCount[j] + 1
        # print(matchPosCount)
        if 9 not in matchPosCount:
            solved = False
    if solved and gameStarted:
        children = tempNode.getChildren()
        children.wrtReparentTo(builtins.render)
        tempNode.clearTransform()
        cubies.wrtReparentTo(tempNode)
        if s:
            s.finish()
        s = Sequence(LerpScaleInterval(tempNode, 0.2, 1.1),
                     LerpScaleInterval(tempNode, 0.2, 1),
                     name="congratulate")
        s.start()
        gameTimeReport = ""
        if gameTime:
            gameFinishTime = (datetime.now() - gameTime).seconds
            if gameFinishTime > 60:
                gameTimeReport = str(gameFinishTime//60) + "m "
            gameTimeReport = gameTimeReport + str(gameFinishTime % 60) + "s"
            gameTimeReport = ("Solved in "
                              + str(gameTimeReport)
                              + " with "
                              + str(turnCount)
                              + " turns")
        app.title.setText(gameTimeReport)
        turnCount = 0
        print("Solved!")
        gameStarted = False
        playButton.show()
        rePlayButton.hide()
    countText.setText("Turns: " + str(turnCount))
    return solved


def rotateSlice(sliceType, hAngle, pAngle, rAngle):
    children = tempNode.getChildren()
    children.wrtReparentTo(builtins.render)
    tempNode.clearTransform()
    # nodes = getCollisionCollection(sliceType)
    nodes = getCubiesInSlice(sliceType)
    nodes.wrtReparentTo(tempNode)
    # print("tempNode Children:")
    # print(tempNode.getChildren())
    i = LerpHprInterval(tempNode, 0.2, Vec3(hAngle, pAngle, rAngle))
    return i


def rotateSliceTask(sliceType, hAngle, pAngle, rAngle, addTurn=True):
    global s
    global turnCount
    global gameTime
    if s:
        s.finish()
    s = Sequence(rotateSlice(sliceType, hAngle, pAngle, rAngle),
                 Func(checkSolved),
                 name="rotate" + sliceType)
    s.start()
    if addTurn:
        if turnCount == 0:
            app.title.setText(" ")
            gameTime = datetime.now()
        turnCount = turnCount + 1


def rotateCube(hAngle, pAngle, rAngle):
    referenceHpr = referenceNode.getHpr(builtins.render)
    referenceNode.setHpr(referenceHpr[0] + hAngle,
                         referenceHpr[1] + pAngle,
                         referenceHpr[2] + rAngle)
    if tempNode.getNumChildren() > 0:
        tempNode.getChildren().wrtReparentTo(builtins.render)
    tempNode.clearTransform()
    cubies.wrtReparentTo(tempNode)
    i = LerpHprInterval(tempNode, 0.1, Vec3(hAngle, pAngle, rAngle))
    return i


def rotateCubeTask(hAngle, pAngle, rAngle):
    global s
    if s:
        s.finish()
    i = rotateCube(hAngle, pAngle, rAngle)
    s = Sequence(i, name="roateCube")
    s.start()


def acceptInput(app):
    app.accept("q", sys.exit)
    app.accept("space", onSpace)
    app.accept("arrow_left", rotateCubeTask, [-90, 0, 0])
    app.accept("arrow_right", rotateCubeTask, [90, 0, 0])
    app.accept("arrow_up", rotateCubeTask, [0, 90, 0])
    app.accept("arrow_down", rotateCubeTask, [0, -90, 0])
    app.accept("x", rotateCubeTask, [0, 90, 0])
    app.accept("shift-x", rotateCubeTask, [0, -90, 0])
    app.accept("y", rotateCubeTask, [-90, 0, 0])
    app.accept("shift-y", rotateCubeTask, [90, 0, 0])
    app.accept("z", rotateCubeTask, [0, 0, -90])
    app.accept("shift-z", rotateCubeTask, [0, 0, 90])
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
    # app.accept("mouse1", grabCubie)
    # app.accept("mouse1-up", releaseCubie)
    if gameStarted:
        rePlayButton.show()


# Mouse functions
def mouseTask(task):
    global mousePos
    if app.mouseWatcherNode.hasMouse():
        mousePos = app.mouseWatcherNode.getMouse()
        mouseRay.setFromLens(app.camNode,
                             mousePos.getX(),
                             mousePos.getY())
        # collisionTraverser.traverse(collisionSliceHolder)
        # if collisionHandler.getNumEntries() > 0:
        #     collisionHandler.sortEntries()
        #     intoNode = collisionHandler.getEntry(0).getIntoNode()
        #     app.title.setText(intoNode.getParent(0).name)
    return task.cont


# def grabCubie():
#     pass


# def releaseCubie():
#     pass


def onSpace():
    # print("tempNode Children:")
    # print(tempNode.getChildren())
    for cubie in cubies:
        print(cubie.name + ":" + str(cubie.getPos(builtins.render)))

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
    "D": ["Down", 90, 0, 0],
    "D'": ["Down", -90, 0, 0],
    "D2": ["Down", 180, 0, 0],
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
    "E": ["Equator", 90, 0, 0],
    "E'": ["Equator", -90, 0, 0],
    "E2": ["Equator", 180, 0, 0],
    "S": ["Standing", 0, 0, -90],
    "S'": ["Standing", 0, 0, 90],
    "S2": ["Standing", 0, 0, -180],
    "M": ["Middle", 0, -90, 0],
    "M'": ["Middle", 0, 90, 0],
    "M2": ["Middle", 0, -180, 0]
}


# Let the game begin
app = ShowBase()
app.title = OnscreenText(
    text="Rubik's Cube Simulator",
    parent=builtins.base.a2dTopCenter,
    fg=(1, 1, 1, 1),
    shadow=(0, 0, 0, 0.5),
    pos=(0, -0.15),
    scale=0.1,
)

countText = OnscreenText(
    text="Turns: 0",
    parent=builtins.base.a2dBottomRight,
    fg=(1, 1, 1, 1),
    shadow=(0, 0, 0, 0.5),
    pos=(-0.2, 0.1),
    scale=0.05
)

playButtonImages = (
    builtins.loader.loadTexture("./baseline_play_circle_outline_white_48dp.png"),
    builtins.loader.loadTexture("./baseline_play_circle_outline_black_48dp.png"),
    builtins.loader.loadTexture("./baseline_play_circle_outline_white_48dp.png"),
    builtins.loader.loadTexture("./baseline_play_circle_outline_white_48dp.png")
)
replayButtonImages = (
    builtins.loader.loadTexture("./baseline_replay_white_48dp.png"),
    builtins.loader.loadTexture("./baseline_replay_black_48dp.png"),
    builtins.loader.loadTexture("./baseline_replay_white_48dp.png"),
    builtins.loader.loadTexture("./baseline_replay_white_48dp.png")
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
collisionHandler = CollisionHandlerQueue()

# Add mouse picking
pickerNode = CollisionNode("pickerNode")
pickerNodePath = builtins.camera.attachNewNode(pickerNode)
pickerNode.setFromCollideMask(BitMask32.bit(2))
mouseRay = CollisionRay()
pickerNode.addSolid(mouseRay)
collisionTraverser.addCollider(pickerNodePath, collisionHandler)
pickerNodePath.show()

# sliceTypes = {
#     "Up": Plane(Vec3(0, 0, -1), Point3(0, 0, 1)),
#     "Down": Plane(Vec3(0, 0, 1), Point3(0, 0, -1)),
#     "Equator": Plane(Vec3(0, 0, 1), Point3(0, 0, 0)),
#     "Front": Plane(Vec3(0, -1, 0), Point3(0, 1, 0)),
#     "Back": Plane(Vec3(0, 1, 0), Point3(0, -1, 0)),
#     "Standing": Plane(Vec3(0, 1, 0), Point3(0, 0, 0)),
#     "Left": Plane(Vec3(-1, 0, 0), Point3(1, 0, 0)),
#     "Right": Plane(Vec3(1, 0, 0), Point3(-1, 0, 0)),
#     "Middle": Plane(Vec3(1, 0, 0), Point3(0, 0, 0)),
# }
sliceTypes = {
    "Up": Point3(0, 0, 1),
    "Down": Point3(0, 0, -1),
    "Equator": Point3(0, 0, 0),
    "Front": Point3(0, 1, 0),
    "Back": Point3(0, -1, 0),
    "Standing": Point3(0, 0, 0),
    "Left": Point3(1, 0, 0),
    "Right": Point3(-1, 0, 0),
    "Middle": Point3(0, 0, 0),
}


# collisionSliceHolder = cameraRig.attachNewNode("collisionSlices")
# collisionSlices = [None for i in range(len(sliceTypes))]
# for i in range(len(sliceTypes)):
#     sliceType = list(sliceTypes.keys())[i]
#     cNode = CollisionNode(sliceType)
#     cNode.setFromCollideMask(BitMask32.bit(1))
#     collisionSlices[i] = collisionSliceHolder.attachNewNode(cNode)
#     collisionSlices[i].node().setFromCollideMask(BitMask32.bit(1))
#     cNode.addSolid(CollisionPlane(sliceTypes[sliceType]))
#     collisionSlices[i].setTag("sliceType", sliceType)
    # if sliceType in ("Right", "Left", "Middle"):
    #     collisionSlices[i].show()
    # cNode.setFromCollideMask(GeomNode.getDefaultCollideMask())

gameInfo = DirectDialog(frameSize=(-.8, .8, -.8, .8),
                        fadeScreen=.4,
                        relief=DGG.FLAT)
gameInfo.hide()

playButton = button("Shuffle", (.2, .1, .15), randomizeCube,
                    playButtonImages, 2)
rePlayButton = button("   Reset Cube", (.2, .1, .15), cubieReset,
                      replayButtonImages, 1.75)
rePlayButton.hide()

cubies = NodePathCollection()
cubies.reserve(27)
cubieCollisions = NodePathCollection()
cubieCollisions.reserve(27)
cubieSetup()

tempNode = cameraRig.attachNewNode("tempNode")
referenceNode = builtins.render.attachNewNode("referenceNode")
# collisionTraverser.traverse(collisionSliceHolder)

# placeholder for sequence
s = None
turnCount = 0
gameStarted = False
gameTime = None
builtins.taskMgr.add(mouseTask, "mouseTask")
acceptInput(app)
app.run()
