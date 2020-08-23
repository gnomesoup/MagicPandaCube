import builtins
from panda3d.core import AmbientLight
from panda3d.core import BitMask32
from panda3d.core import Vec3, Vec4, Point3, Point2
from panda3d.core import Plane
from panda3d.core import Material
from panda3d.core import CollisionTraverser
from panda3d.core import CollisionHandlerQueue
from panda3d.core import CollisionNode
from panda3d.core import CollisionPolygon
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
from datetime import datetime
import random
import sys
import math


class MagicCube(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.title = OnscreenText(
            text="Rubik's Cube Simulator",
            parent=base.a2dTopCenter,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.5),
            pos=(0, -0.15),
            scale=0.1,
        )

        self.countText = OnscreenText(
            text="Turns: 0",
            parent=base.a2dBottomRight,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.5),
            pos=(-0.2, 0.1),
            scale=0.05
        )

        self.playButtonImages = (
            loader.loadTexture(
                "./baseline_play_circle_outline_white_48dp.png"
                ),
            loader.loadTexture(
                "./baseline_play_circle_outline_black_48dp.png"
                ),
            loader.loadTexture(
                "./baseline_play_circle_outline_white_48dp.png"
                ),
            loader.loadTexture(
                "./baseline_play_circle_outline_white_48dp.png"
                )
        )
        self.replayButtonImages = (
            loader.loadTexture("./baseline_replay_white_48dp.png"),
            loader.loadTexture("./baseline_replay_black_48dp.png"),
            loader.loadTexture("./baseline_replay_white_48dp.png"),
            loader.loadTexture("./baseline_replay_white_48dp.png")
        )

        self.playButton = DirectButton(
            text=("", "", "Shuffle", ""),
            text_scale=1.3,
            text_pos=(4.5, -.3),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 0.5),
            frameTexture=self.playButtonImages,
            scale=0.05,
            pos=(.2, .1, .15),
            frameSize=(-2, 2, -2, 2),
            relief=DGG.FLAT,
            parent=base.a2dBottomLeft,
            command=self.randomizeCube
            )
        self.playButton.setTransparency(TransparencyAttrib.MAlpha)

        self.replayButton = DirectButton(
            text=("", "", "Reset Cube", ""),
            text_scale=1.3,
            text_pos=(5.5, -.325),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 0.5),
            frameTexture=self.replayButtonImages,
            scale=0.05,
            pos=(.2, .1, .15),
            frameSize=(-1.75, 1.75, -1.75, 1.75),
            relief=DGG.FLAT,
            parent=base.a2dBottomLeft,
            command=self.cubieReset
            )
        self.replayButton.setTransparency(TransparencyAttrib.MAlpha)
        self.replayButton.hide()

        self.background = OnscreenImage(
            parent=render2dp, image="galaxy.jpg"
            )
        # Force the rendering to render the background image first
        # (so that it will be put to the bottom of the scene since
        # other models will be necessarily drawn on top)
        base.cam2dp.node().getDisplayRegion(0).setSort(-20)
        # disable default mouse behavior
        base.disableMouse()

        # Setup camera
        cameraDist = 8
        camera.setPos(-cameraDist * 0.75, cameraDist, cameraDist)
        camera.lookAt(0, 0, 0)

        # Setup lights
        self.ambientLight = AmbientLight("ambientLight")
        self.ambientLight.setColor((1, 1, 1, 1))
        self.render.setLight(
            render.attachNewNode(self.ambientLight)
            )

        # Define slice types
        self.sliceTypes = {
            "Up": Plane(Vec3(0, 0, 1), Point3(0, 0, 1)),
            "Down": Plane(Vec3(0, 0, -1), Point3(0, 0, -1)),
            "Equator": Plane(Vec3(0, 0, -1), Point3(0, 0, 0)),
            "Front": Plane(Vec3(0, 1, 0), Point3(0, 1, 0)),
            "Back": Plane(Vec3(0, -1, 0), Point3(0, -1, 0)),
            "Standing": Plane(Vec3(0, 1, 0), Point3(0, 0, 0)),
            "Left": Plane(Vec3(1, 0, 0), Point3(1, 0, 0)),
            "Right": Plane(Vec3(-1, 0, 0), Point3(-1, 0, 0)),
            "Middle": Plane(Vec3(1, 0, 0), Point3(0, 0, 0)),
        }

        self.black = Material()
        self.black.setAmbient((0, 0, 0, 1))
        self.white = Material()
        self.white.setAmbient((1, 1, 1, 1))
        self.blue = Material()
        self.blue.setAmbient(self.hexColor("40a4d8"))
        self.red = Material()
        self.red.setAmbient(self.hexColor("db3837"))
        self.green = Material()
        self.green.setAmbient(self.hexColor("b2c225"))
        self.orange = Material()
        self.orange.setAmbient(self.hexColor("f4941f"))
        self.yellow = Material()
        self.yellow.setAmbient(self.hexColor("fecc30"))

        # Dictionary of moves
        self.rotateSliceArguments = {
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

        # Setup collision environment
        self.collisionTraverser = CollisionTraverser()
        self.collisionHandler = CollisionHandlerQueue()

        # Add mouse picking
        self.pickerNode = CollisionNode("pickerNode")
        self.pickerNodePath = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.mouseRay = CollisionRay()
        self.pickerNode.addSolid(self.mouseRay)
        self.collisionTraverser.addCollider(
            self.pickerNodePath, self.collisionHandler
            )

        # Setup Geometry
        self.cubies = NodePathCollection()
        self.cubies.reserve(27)
        self.cubieCollisions = NodePathCollection()
        self.cubieCollisions.reserve(54)
        self.cubieSetup()
        self.rotationNode = render.attachNewNode("rotationNode")

        # placeholder for sequence
        self.moveSequence = None
        self.turnCount = 0
        self.gameStarted = False
        self.gameTime = None
        self.dragging = False
        self.dragSlices = []
        self.dragStartPoints = None
        taskMgr.add(self.mouseTask, "mouseTask")
        self.acceptInput()

    # GUI functions
    def cubieSetup(self):
        i = 0
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    pos = Vec3(x - 1, y - 1, z - 1)
                    cubie = render.attachNewNode("cubie")
                    cubieModel = loader.loadModel("cubie")
                    cubieModel.setScale(0.95)
                    cubieModel.reparentTo(cubie)
                    cubie.setPos(pos)
                    cubie.reparentTo(render)
                    sideCount = 0
                    name = ""
                    if self.colorIf(
                        cubie, "Up",
                        self.yellow, self.black,
                        z, 2
                    ):
                        sideCount = sideCount + 1
                        name += "Y"
                        cNode = CollisionNode("Yellow")
                        quad = CollisionPolygon(Point3(-.5, -.5, .5),
                                                Point3(.5, -.5, .5),
                                                Point3(.5, .5, .5),
                                                Point3(-.5, .5, .5))
                        cNode.addSolid(quad)
                        self.cubieCollisions.addPath(
                            cubie.attachNewNode(cNode)
                            )
                    if self.colorIf(
                        cubie, "Down",
                        self.white, self.black,
                        z, 0
                    ):
                        sideCount = sideCount + 1
                        name += "W"
                        cNode = CollisionNode("White")
                        quad = CollisionPolygon(
                            Point3(-.5, -.5, -.5),
                            Point3(-.5, .5, -.5),
                            Point3(.5, .5, -.5),
                            Point3(.5, -.5, -.5)
                            )
                        cNode.addSolid(quad)
                        self.cubieCollisions.addPath(
                            cubie.attachNewNode(cNode)
                            )
                    if self.colorIf(
                        cubie, "Front",
                        self.blue, self.black,
                        y, 2
                    ):
                        sideCount = sideCount + 1
                        name += "B"
                        cNode = CollisionNode("Blue")
                        quad = CollisionPolygon(Point3(-.5, .5, -.5),
                                                Point3(-.5, .5, .5),
                                                Point3(.5, .5, .5),
                                                Point3(.5, .5, -.5))
                        cNode.addSolid(quad)
                        self.cubieCollisions.addPath(
                            cubie.attachNewNode(cNode)
                            )
                    if self.colorIf(
                        cubie, "Back",
                        self.green, self.black,
                        y, 0
                    ):
                        sideCount = sideCount + 1
                        name += "G"
                        cNode = CollisionNode("Green")
                        quad = CollisionPolygon(Point3(-.5, -.5, -.5),
                                                Point3(.5, -.5, -.5),
                                                Point3(.5, -.5, .5),
                                                Point3(-.5, -.5, .5))
                        cNode.addSolid(quad)
                        self.cubieCollisions.addPath(
                            cubie.attachNewNode(cNode)
                            )
                    if self.colorIf(
                        cubie, "Left",
                        self.orange, self.black,
                        x, 2
                    ):
                        sideCount = sideCount + 1
                        name += "O"
                        cNode = CollisionNode("Orange")
                        quad = CollisionPolygon(Point3(.5, -.5, -.5),
                                                Point3(.5, .5, -.5),
                                                Point3(.5, .5, .5),
                                                Point3(.5, -.5, .5))
                        cNode.addSolid(quad)
                        self.cubieCollisions.addPath(
                            cubie.attachNewNode(cNode)
                            )
                    if self.colorIf(
                        cubie, "Right",
                        self.red, self.black,
                        x, 0
                    ):
                        sideCount = sideCount + 1
                        name += "R"
                        cNode = CollisionNode("Red")
                        quad = CollisionPolygon(Point3(-.5, -.5, -.5),
                                                Point3(-.5, -.5, .5),
                                                Point3(-.5, .5, .5),
                                                Point3(-.5, .5, -.5))
                        cNode.addSolid(quad)
                        self.cubieCollisions.addPath(
                            cubie.attachNewNode(cNode)
                            )
                    if len(name) == 3:
                        name = "corner" + name
                    elif len(name) == 2:
                        name = "edge" + name
                    elif len(name) == 1:
                        name = "center" + name
                    else:
                        name = "internal"
                    cNode.setIntoCollideMask(BitMask32.bit(1))
                    cubie.setPythonTag("sideCount", sideCount)
                    cubie.setPythonTag("originalPos", pos)
                    cubie.name = name
                    self.cubies.addPath(cubie)
                    i = i + 1

    def cubieReset(self):
        global turnCount
        turnCount = 0
        self.checkSolved()
        self.cubies.reparentTo(render)
        for cubie in self.cubies:
            pos = cubie.getPythonTag("originalPos")
            cubie.setPos(pos)
            cubie.setHpr(0, 0, 0)
        self.playButton.show()
        self.replayButton.hide()
        self.title.setText(" ")

    def randomizeList(self, num):
        i = 0
        outList = []
        while i < num:
            r = random.randint(0, 17)
            key = list(self.rotateSliceArguments.keys())[r]
            if i > 0 and outList[-1][0] == key[0]:
                continue
            i = i + 1
            outList.append(key)
        return outList

    def randomizeCube(self):
        self.ignoreAll()
        self.cubieReset()
        self.playButton.hide()
        print("Randomize")
        rotateList = self.randomizeList(20)
        i = 0
        if self.moveSequence:
            self.moveSequence.finish()
        self.moveSequence = Sequence(name="randomize")
        for rotation in rotateList:
            args = self.rotateSliceArguments[rotation]
            # s.append(rotateSlice(args[0], args[1], args[2], args[3]))
            taskMgr.doMethodLater(
                i * .3, self.rotateSliceTask,
                name="randomize" + str(i),
                extraArgs=args + [False]
                )
            i = i + 1
        taskMgr.doMethodLater(
            i * .3, self.acceptInput,
            name="acceptInput",
            extraArgs=[]
            )
        randomizeReport = " ".join(rotateList)
        print(randomizeReport)
        self.gameStarted = True
        self.title.setText(randomizeReport)
        return randomizeReport

    def hexColor(self, h):
        if len(h) < 8:
            ha = "ff"
        else:
            ha = h[6:8]
        hc = [h[0:2], h[2:4], h[4:6], ha]
        color = Vec4()
        for i in range(4):
            color[i] = int("0x" + hc[i], 16) / 255
        return color

    def colorIf(
        self,
        cObject,
        cDirection,
        cMaterial,
        eMaterial,
        cCoord,
        cIndex
    ):
        oldMat = cObject.findMaterial(cDirection)
        if cCoord == cIndex:
            cObject.replaceMaterial(oldMat, cMaterial)
            return True
        else:
            cObject.replaceMaterial(oldMat, eMaterial)
            return False

    # game action functions
    def getCubiesInSlice(self, sliceType):
        sliceCollection = NodePathCollection()
        slicePlane = self.sliceTypes[sliceType]
        for cubie in self.cubies:
            pos = cubie.getPos(render)
            d = slicePlane.distToPlane(pos)
            if d < 0.1 and d > -0.1:
                sliceCollection.addPath(cubie)
        return sliceCollection

    def checkSolved(self):
        solved = True
        for i in range(3):
            matchPosCount = [0, 0, 0]
            matchPos = None
            matchHpr = None
            for cubie in self.cubies:
                originalPos = cubie.getPythonTag("originalPos")
                pos = cubie.getPos(render)
                hpr = cubie.getHpr(render)
                currentPos = (round(pos[0]), round(pos[1]), round(pos[2]))
                currentHpr = Vec3(
                    abs(round(hpr[0])),
                    abs(round(hpr[1])),
                    abs(round(hpr[2]))).normalized()
                if currentPos[i] == 1:
                    if matchPos is None:
                        matchPos = originalPos
                        matchHpr = currentHpr
                    for j in range(3):
                        if (
                            matchPos[j] == originalPos[j] and (
                                matchHpr == currentHpr
                                or cubie.getPythonTag("sideCount") == 1
                                )
                        ):
                            matchPosCount[j] = matchPosCount[j] + 1
            # print(matchPosCount)
            if 9 not in matchPosCount:
                solved = False
        if solved and self.gameStarted:
            children = self.rotationNode.getChildren()
            children.wrtReparentTo(render)
            self.rotationNode.clearTransform()
            self.cubies.wrtReparentTo(self.rotationNode)
            if self.moveSequence:
                self.moveSequence.finish()
            self.moveSequence = Sequence(
                LerpScaleInterval(self.rotationNode, 0.2, 1.1),
                LerpScaleInterval(self.rotationNode, 0.2, 1),
                name="congratulate")
            self.moveSequence.start()
            gameTimeReport = ""
            if self.gameTime:
                gameFinishTime = (datetime.now() - self.gameTime).seconds
                if gameFinishTime > 60:
                    gameTimeReport = str(gameFinishTime//60) + "m "
                gameTimeReport = (
                    gameTimeReport
                    + str(gameFinishTime % 60)
                    + "s"
                    )
                gameTimeReport = (
                    "Solved in "
                    + str(gameTimeReport)
                    + " with "
                    + str(self.turnCount)
                    + " turns"
                    )
            self.title.setText(gameTimeReport)
            self.turnCount = 0
            print("Solved!")
            self.gameStarted = False
            self.playButton.show()
            self.replayButton.hide()
        self.countText.setText("Turns: " + str(self.turnCount))
        return solved

    def rotateSlice(self, sliceType, hAngle, pAngle, rAngle):
        children = self.rotationNode.getChildren()
        children.wrtReparentTo(render)
        self.rotationNode.clearTransform()
        nodes = self.getCubiesInSlice(sliceType)
        nodes.wrtReparentTo(self.rotationNode)
        i = LerpHprInterval(
            self.rotationNode,
            0.2,
            Vec3(hAngle, pAngle, rAngle)
            )
        return i

    def rotateSliceTask(
        self,
        sliceType,
        hAngle,
        pAngle,
        rAngle,
        addTurn=True
    ):
        if self.moveSequence:
            self.moveSequence.finish()
        self.moveSequence = Sequence(
            self.rotateSlice(sliceType, hAngle, pAngle, rAngle),
            Func(self.checkSolved),
            name="rotate" + sliceType
            )
        self.moveSequence.start()
        if addTurn:
            if self.turnCount == 0:
                self.title.setText(" ")
                self.gameTime = datetime.now()
            self.turnCount += 1

    def rotateCube(self, hAngle, pAngle, rAngle):
        # referenceHpr = self.referenceNode.getHpr(render)
        # referenceNode.setHpr(referenceHpr[0] + hAngle,
        #                     referenceHpr[1] + pAngle,
        #                     referenceHpr[2] + rAngle)
        if self.rotationNode.getNumChildren() > 0:
            self.rotationNode.getChildren().wrtReparentTo(render)
        self.rotationNode.clearTransform()
        self.cubies.wrtReparentTo(self.rotationNode)
        i = LerpHprInterval(
            self.rotationNode, 0.1,
            Vec3(hAngle, pAngle, rAngle))
        return i

    def rotateCubeTask(self, hAngle, pAngle, rAngle):
        if self.moveSequence:
            self.moveSequence.finish()
        i = self.rotateCube(hAngle, pAngle, rAngle)
        self.moveSequence = Sequence(i, name="rotateCube")
        self.moveSequence.start()

    def acceptInput(self):
        self.accept("q", sys.exit)
        self.accept("space", self.onSpace)
        self.accept("arrow_left", self.rotateCubeTask, [-90, 0, 0])
        self.accept("arrow_right", self.rotateCubeTask, [90, 0, 0])
        self.accept("arrow_up", self.rotateCubeTask, [0, 90, 0])
        self.accept("arrow_down", self.rotateCubeTask, [0, -90, 0])
        self.accept("x", self.rotateCubeTask, [0, 90, 0])
        self.accept("shift-x", self.rotateCubeTask, [0, -90, 0])
        self.accept("y", self.rotateCubeTask, [-90, 0, 0])
        self.accept("shift-y", self.rotateCubeTask, [90, 0, 0])
        self.accept("z", self.rotateCubeTask, [0, 0, -90])
        self.accept("shift-z", self.rotateCubeTask, [0, 0, 90])
        self.accept(
            "r", self.rotateSliceTask,
            self.rotateSliceArguments["R"]
            )
        self.accept(
            "shift-r", self.rotateSliceTask,
            self.rotateSliceArguments["R'"]
            )
        self.accept(
            "l", self.rotateSliceTask,
            self.rotateSliceArguments["L"]
            )
        self.accept(
            "shift-l", self.rotateSliceTask,
            self.rotateSliceArguments["L'"]
            )
        self.accept(
            "m", self.rotateSliceTask,
            self.rotateSliceArguments["M"]
            )
        self.accept(
            "shift-m", self.rotateSliceTask,
            self.rotateSliceArguments["M'"]
            )
        self.accept(
            "f", self.rotateSliceTask,
            self.rotateSliceArguments["F"]
            )
        self.accept(
            "shift-f", self.rotateSliceTask,
            self.rotateSliceArguments["F'"]
            )
        self.accept(
            "b", self.rotateSliceTask,
            self.rotateSliceArguments["B"]
            )
        self.accept(
            "shift-b", self.rotateSliceTask,
            self.rotateSliceArguments["B'"]
            )
        self.accept(
            "s", self.rotateSliceTask,
            self.rotateSliceArguments["S"]
            )
        self.accept(
            "shift-s", self.rotateSliceTask,
            self.rotateSliceArguments["S'"]
            )
        self.accept(
            "u", self.rotateSliceTask,
            self.rotateSliceArguments["U"]
            )
        self.accept(
            "shift-u", self.rotateSliceTask,
            self.rotateSliceArguments["U'"]
            )
        self.accept(
            "d", self.rotateSliceTask, self.rotateSliceArguments["D"]
            )
        self.accept(
            "shift-d", self.rotateSliceTask,
            self.rotateSliceArguments["D'"]
            )
        self.accept(
            "e", self.rotateSliceTask,
            self.rotateSliceArguments["E"]
            )
        self.accept(
            "shift-e", self.rotateSliceTask, self.rotateSliceArguments["E'"]
        )
        self.accept("3", self.randomizeCube)
        # self.accept("?", self.helpDialog)
        self.accept("mouse1", self.grabCubie)
        self.accept("mouse1-up", self.releaseCubie)
        if self.gameStarted:
            self.replayButton.show()

    def getXYVectorLength(self, v):
        return math.sqrt(pow(v.x, 2) + pow(v.y, 2))

    # Mouse functions
    def mouseTask(self, task):
        # First check if we have the mouse in the window
        if self.mouseWatcherNode.hasMouse():
            # Get the position of the mouse and make the collision ray follow
            self.mousePos = self.mouseWatcherNode.getMouse()
            if not self.dragging:
                self.mouseRay.setFromLens(
                    self.camNode,
                    self.mousePos.getX(),
                    self.mousePos.getY()
                    )
                # Check for collisions and sort them
                self.collisionTraverser.traverse(render)
                if self.collisionHandler.getNumEntries() > 0:
                    self.collisionHandler.sortEntries()
                    self.currentEntry = self.collisionHandler.getEntry(0)
                    nodeUnderMouse = self.currentEntry.getIntoNode()
                    self.onCubie = nodeUnderMouse.getParent(0)
                else:
                    self.onCubie = False
            else:
                pos3d = Point3()
                nearPoint = Point3()
                farPoint = Point3()
                base.camLens.extrude(
                    self.mousePos,
                    nearPoint,
                    farPoint)
                dragVectors = []
                for dragSlice, startPoint in zip(
                    self.dragSlices, self.dragStartPoints
                ):
                    slicePlane = self.sliceTypes[dragSlice]
                    if slicePlane.intersectsLine(
                        pos3d,
                        render.getRelativePoint(
                            camera, nearPoint
                        ),
                        render.getRelativePoint(
                            camera, farPoint
                        )
                    ):
                        dragVector = pos3d - startPoint
                        dragVectors.append(dragVector)
                m = max(dragVectors, key=self.getXYVectorLength)
                i = dragVectors.index(m)
                print(self.dragSlices[i])
        return task.again

    def grabCubie(self):
        print("mouseClickDown")
        if not self.dragging:
            if self.onCubie:
                self.dragging = render.find("**/" + self.onCubie.name)
                dragStartPoint = self.mousePos
                collisionNormal = self.currentEntry.getSurfaceNormal(
                    render
                    )
                collisionNormal = Vec3(
                    round(collisionNormal[0]),
                    round(collisionNormal[1]),
                    round(collisionNormal[2])
                    )
                print(" ")
                print(self.dragging.name)
                self.dragSlices = []
                for key, value in self.sliceTypes.items():
                    pos = self.dragging.getPos(render)
                    d = value.distToPlane(pos)
                    if d < 0.1 and d > -0.1:
                        if (collisionNormal != value.getNormal()):
                            self.dragSlices.append(key)
                            print(key)
                # self.cubies.wrtReparentTo(render)
                # self.rotationNode.clearTransform()
                # nodes = self.getCubiesInSlice(self.dragSlices[0])
                # nodes.wrtReparentTo(self.rotationNode)
            else:
                # self.cubies.wrtReparentTo(self.rotationNode)
                self.dragging = self.rotationNode
                self.dragSlices = ["Equator", "Middle"]
            self.dragStartPoints = []
            for dragSlice in self.dragSlices:
                dragPlane = self.sliceTypes[dragSlice]
                dragStartPoint = self.getMousePointOnPlane(dragPlane)
                self.dragStartPoints.append(dragStartPoint)

    def releaseCubie(self):
        if self.onCubie or self.dragging:
            self.dragging = False

    def getMousePointOnPlane(self, plane):
        dragStartPoint = Point3()
        nearPoint = Point3()
        farPoint = Point3()
        base.camLens.extrude(
            self.mousePos,
            nearPoint,
            farPoint
        )
        plane.intersectsLine(
            dragStartPoint,
            render.getRelativePoint(
                camera, nearPoint
            ),
            render.getRelativePoint(
                camera, farPoint
            )
        )
        return dragStartPoint

    def onSpace(self):
        # print("self.rotationNode Children:")
        # print(self.rotationNode.getChildren())
        for cubie in self.cubies:
            print(cubie.name + ":" + str(cubie.getPos(render)))


magicCube = MagicCube()
magicCube.run()
