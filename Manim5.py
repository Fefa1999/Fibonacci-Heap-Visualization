from manim import *
from manim.typing import Point3D
from manim.typing import Vector3
from typing import Self
from typing import TypedDict

#DO YOU HAVE TO STATE DELETIONS OF OBJECTS IN PYTHON TO HELP GARBAGE COLLECTER

#New Scene class with a dictonary of keys and newdot pointers
class FiboScene(MovingCameraScene):
    def __init__(self, *args, **kwargs):
        self.min_node: self.FiboDot = None
        self.root = list[self.FiboDot]()
        self.mobjsTOmove = list[self.FiboDot]()
        self.storedAnimations = list[Animation]()
        self.nodeDic = dict[int, self.FiboDot]()
        self.defaultAddPoint = [0.0, 3.0, 0.0]
        self.height = 7.993754879000781                                                                                                                                                                                              
        self.width = 14.222222222222221
        self.multp = 0
        super().__init__(*args, **kwargs)

    #New dot class. A manim dot with children. #TODO maybe make all functions such as move_to automatik points to dot
    class FiboDot:
        dot: Dot
        id: int
        parrentKey: int
        children: list[Self]
        widthOfChildren: int
        dot: Dot
        arrow: Line = None
        numberLabel: Text
        #target: Point3D #Not used ATM
        def __init__(self, idKey: int):
            self.id = idKey
            self.children = list[Self]()
            #self.widthOfChildren = int()
            #self.parrentKey = int()
            #self.arrow = Line()
            #self.numberLabel = Text("")
    

    def space_list_dots_by_tree_width(self, lst: list[FiboDot], isToTarget: bool, direction: Vector3 = LEFT, **kwargs):
        if isToTarget:
            for m1, m2 in zip(lst, lst[1:]):
                m2.dot.target.next_to(m1.dot.target, direction, (m1.widthOfChildren), **kwargs)
        else:
            for m1, m2 in zip(lst, lst[1:]):
                m2.dot.next_to(m1.dot, direction, (m1.widthOfChildren), **kwargs)
        return lst

    def getRootKeyIndex(self, root: list, key: int):
        for n in range(len(root)):
            a = root[n]
            if a.id == key:
                return n
        return -1

    #Creates a FiboDot with a dot at "location", and numberLabel showing numberl, and return it without adding it to scene.
    def createDot(self, point: Point3D, number: int, id: int):
        fiboDot = self.FiboDot(id)
        fiboDot.dot = Dot(point, radius=0.2, color=BLUE)
        label = Text(str(number), font_size=18).move_to(fiboDot.dot.get_center())#.set_z_index(1) #Why is set_z_index soooo slow? #And Stroke width???
        fiboDot.numberLabel = label
        fiboDot.widthOfChildren = fiboDot.dot.radius*2
        return fiboDot

    #Inserts the dot onto the scene and adds it to a vgroup (Root), then calls for a repositioning of the nodes.
    def insertDot(self, number: int, isAnimation: bool, id: int):
        fiboDot = self.createDot(self.defaultAddPoint, number, id)
        self.nodeDic[id] = fiboDot
        self.root.append(fiboDot)

        if isAnimation:
            self.play(FadeIn(fiboDot.dot, fiboDot.numberLabel))
        else:
            self.add(fiboDot.dot, fiboDot.numberLabel)

        if len(self.root) == 1:
            if isAnimation:
                self.play(fiboDot.dot.animate.move_to([0, 2, 0]), fiboDot.numberLabel.animate.move_to([0, 2, 0]))
                return
            else:
                fiboDot.dot.move_to([0, 2, 0])
                fiboDot.numberLabel.move_to([0, 2, 0])
                return

        if isAnimation:
            self.animateRoot((len(self.root)-1))
        else:
            self.moveRoot((len(self.root)-1))

        self.adjust_camera(isAnimation)
        return fiboDot  #TODO is returning fiboDot needed?????           

    def adjust_camera(self, isAnimation): #Fix should have soooo many lookups.
        mostLeftNode = self.get_left_most_dot(self.root)
        mostRightNode = self.root[len(self.root)-1]

        rightPoint = mostRightNode.dot.get_right()
        leftPoint = mostLeftNode.dot.get_left()

        newWidth = rightPoint[0]-leftPoint[0]
        self.defaultAddPoint[0] = (rightPoint[0]+leftPoint[0])/2
        self.defaultAddPoint[1] = rightPoint[1]+1.0

        boarderRight = self.camera.frame.get_right()[0]
        boarderLeft = self.camera.frame.get_left()[0]

        if newWidth+2 > (self.camera.frame_width) or boarderLeft > (leftPoint[0]+1) or boarderRight < (rightPoint[0]+1): # +4 is secureing padding
            newCenter = (((rightPoint[0]+leftPoint[0])/2), ((rightPoint[1]+leftPoint[1])/2), ((rightPoint[2]+leftPoint[2])/2))
            if isAnimation:
                self.play(self.camera.frame.animate.set(width=self.camera.frame_width * 1.3).move_to(newCenter))
            else: 
                self.camera.frame.set(width=self.camera.frame_width * 1.3).move_to(newCenter)
    
    def get_left_most_dot(self, group: list[FiboDot]):
        if len(group) == 0:
            return #TODO should it return something to tell it failed??
        
        def aux(a: self.FiboDot):
            if len(a.children) > 0:
                return aux(a.children[len(a.children)-1])
            else:
                return a
        
        return aux(group[0])

    def createChild(self, parrentKey: int, childKey: int, isAnimation: bool):
        #Finding parrent and child
        rootParrentIndex = self.getRootKeyIndex(self.root, parrentKey)
        if rootParrentIndex<0:
            return  #TODO should it return something to tell it failed??
        parrentMojb = self.root[rootParrentIndex]
        rootChildIndex = self.getRootKeyIndex(self.root, childKey)
        if rootChildIndex<0:
            return  #TODO should it return something to tell it failed??
        childMojb = self.root[rootChildIndex]
        childMojb.parrentKey = parrentKey

        #Adding child to parrent and removing from root
        parrentMojb.children.append(childMojb)
        self.root.remove(childMojb)

        #creating arrow
        pointer = Line(childMojb.dot,parrentMojb.dot)
        childMojb.arrow = pointer

        #Calculation new widths.
        gainedWidth = int() 
        if len(parrentMojb.children) == 1:
            gainedWidth = 0
        else:
            gainedWidth = childMojb.widthOfChildren + childMojb.dot.radius*2
        parrentMojb.widthOfChildren += gainedWidth

        if isAnimation:
            self.storedAnimations.append(FadeIn(pointer))
            firstIndexOfChange = min(rootParrentIndex,rootChildIndex)
            self.animateRoot(firstIndexOfChange)
        else:
            self.moveRoot(rootParrentIndex)
            self.add(pointer)

    def animateRoot(self, startIndex: int, deletedRootDotCenter: Point3D = None): #Must be done smart. aka move the lesser tree. Or moving fixed distance if child is at the ends.
        def aux (rootIndex: int, lastDotDestination: Point3D):
            if rootIndex == len(self.root):
                return
            currentDot = self.root[rootIndex]
            if not isinstance(currentDot, self.FiboDot): #TODO why is this still needed?
                return 
            currentDot.dot.target = Dot(point=currentDot.dot.get_center(), radius=currentDot.dot.radius, color=currentDot.dot.color)
            currentDot.dot.target.set_x(lastDotDestination[0]+currentDot.widthOfChildren+currentDot.dot.radius*2).set_y(lastDotDestination[1])
            self.mobjsTOmove.append(currentDot)
            self.animateChildren(currentDot, currentDot.dot.target)
            
            aux(rootIndex+1, currentDot.dot.target.get_center())
            return

        rootNodeAtIndex = self.root[startIndex]
        leftRootDotLocation = rootNodeAtIndex.dot.get_center()
        if startIndex == 0 and not (deletedRootDotCenter is  None):
            leftRootDotLocation = deletedRootDotCenter
        elif startIndex == 0: 
            leftRootDotLocation[0] -= (rootNodeAtIndex.widthOfChildren+rootNodeAtIndex.dot.radius*2)
        else: 
            leftRootDotLocation = self.root[startIndex-1].dot.get_center()

        aux(startIndex, leftRootDotLocation)

        self.buildAnimation()
        self.executeStoredAnimations()
        return

    def moveRoot(self, startIndex: int):
        if startIndex == 0:
            rootDot = self.root[startIndex]
            self.moveChildren(rootDot)

        def aux (root: list[self.FiboDot], rootIndex: int, lastDotDestination: Dot):
            if rootIndex == len(root):
                return []
            
            currentDot = root[rootIndex]
            currentDot.dot.set_x(lastDotDestination.get_x()+currentDot.widthOfChildren+currentDot.dot.radius*2).set_y(lastDotDestination.get_y())
            currentDot.numberLabel.move_to(currentDot.dot.get_center())

            self.moveChildren(currentDot)
            
            aux(root, rootIndex+1, currentDot.dot)

        aux(self.root, startIndex, self.root[startIndex-1].dot)
        return

    def animateChildren(self, parrentMojb: FiboDot, parrentTarget: FiboDot): #TODO need to be made into a transform method where it can collect all animation and then move.
        if len(parrentMojb.children)==0:
            return

        #First child which the other children should be alinged left of
        baseChild = parrentMojb.children[0]
        baseChild.dot.target = Dot(point=baseChild.dot.get_center(), radius=baseChild.dot.radius, color=baseChild.dot.color).set_y(parrentTarget.get_y()-1.5).align_to(parrentTarget, RIGHT)
        self.mobjsTOmove.append(baseChild)

        for i in range(len(parrentMojb.children)-1):
            child =  parrentMojb.children[i+1]
            child.dot.target = Dot(point=child.dot.get_center(), radius=child.dot.radius, color=child.dot.color)
            self.mobjsTOmove.append(child)
        
        #Arrange based on first child.
        self.space_list_dots_by_tree_width(parrentMojb.children, True)

        for n in range(len(parrentMojb.children)):
            self.animateChildren(parrentMojb.children[n], parrentMojb.children[n].dot.target)
        return
        
    def moveChildren(self, parrentMojb: FiboDot):
        if len(parrentMojb.children)==0:
            return
        
        #Set first childs new location
        parrentMojb.children[0].dot.set_y(parrentMojb.dot.get_y()-1).align_to(parrentMojb.dot, RIGHT)
        
        #Arrange rest based on first
        self.space_list_dots_by_tree_width(parrentMojb.children, False)

        #Move arrows and recursively move childrens og children
        parrentsBottom = parrentMojb.dot.get_bottom()
        for n in parrentMojb.children:
            n.numberLabel.move_to(n.dot.get_center())
            n.arrow.put_start_and_end_on(n.dot.get_top(), parrentsBottom)
            self.moveChildren(n)

    def delete(self, deleteDotID: int, isAnimation: bool):
        deleteDot = self.nodeDic.get(deleteDotID)
        index = self.getRootKeyIndex(self.root, deleteDotID)

        lastRootElement = len(self.root) == 1

        self.root.remove(deleteDot)
    
        childrenArrows = []
        if (len(deleteDot.children)>0):
            deleteDot.children.reverse() #TODO should it be reversed? Reverse determent the movement and place to root
            for n in deleteDot.children:
                childrenArrows.append(n.arrow)
                n.arrow = None
                n.parrentKey = None
                self.root.append(n)

        if isAnimation:
            for n in childrenArrows:
                self.storedAnimations.append(FadeOut(n))
            self.storedAnimations.append(FadeOut(deleteDot.dot))
            self.storedAnimations.append(FadeOut(deleteDot.numberLabel))
            if not lastRootElement and index == 0:
                self.animateRoot(index, deleteDot.dot.get_center())
            else:
                self.animateRoot(index)
            self.adjust_camera(isAnimation) #TODO Should it be animated with the others??
        else:
            #self.remove(deleteDot.text)
            self.remove(deleteDot)
            self.moveRoot(index-1)
            for n in childrenArrows:
                self.remove(n)

    def setMin(self, min_id):
        min_node_index = self.getRootKeyIndex(self.root, min_id)
        if not isinstance(min_node_index, int):
            return
        minFiboNode = self.root[min_node_index]
        if self.min_node is not None:
            self.min_node.dot.fade_to(BLUE, 1)

        self.min_node = minFiboNode
        minFiboNode.dot.fade_to(RED, 100)

    def buildAnimation(self):
        listOfAnimations = list[Animation]()
        for n in self.mobjsTOmove:
            listOfAnimations.append(MoveToTarget(n.dot))
            listOfAnimations.append(n.numberLabel.animate.move_to(n.dot.target.get_center()))
            if n.arrow != None:
                listOfAnimations.append(n.arrow.animate.put_start_and_end_on(n.dot.target.get_top(), self.nodeDic[n.parrentKey].dot.target.get_bottom()))
            n.target = None
        self.mobjsTOmove = list[self.FiboDot]()
        self.storedAnimations.extend(listOfAnimations)
        return 

    def executeStoredAnimations(self):
        self.play(*self.storedAnimations)
        self.storedAnimations = list[Animation]()
        return

    def adjust_camera_after_consolidate(self): #Fix should have soooo many lookups.
        mostLeftNode = self.get_left_most_dot(self.root)
        mostRightNode = self.root[len(self.root)-1]

        if isinstance(mostLeftNode, self.FiboDot) and isinstance(mostRightNode, self.FiboDot):
            rightPoint = mostRightNode.dot.get_right()
            leftPoint = mostLeftNode.dot.get_left()

            self.defaultAddPoint[0] = (rightPoint[0]+leftPoint[0])/2
            self.defaultAddPoint[1] = rightPoint[1]+1.0
            currentWidthOfHeap = rightPoint[0]-leftPoint[0]
            newWidth = self.width
            while newWidth < currentWidthOfHeap:
                newWidth = newWidth * 2
            
            if newWidth == self.width:
                self.multp = 0
            else: 
                self.multp = newWidth / self.width

            newCenter: Point3D = (((rightPoint[0]+leftPoint[0])/2), (self.multp * 2)*-1, (rightPoint[2]+leftPoint[2])/2)

            self.play(self.camera.frame.animate.move_to(newCenter).set(width=newWidth))

