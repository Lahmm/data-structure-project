from typing import List
from collections import namedtuple
import time


class Point(namedtuple("Point", "x y")):
    def __repr__(self) -> str:
        return f'Point{tuple(self)!r}'


class Rectangle(namedtuple("Rectangle", "lower upper")):
    def __repr__(self) -> str:
        return f'Rectangle{tuple(self)!r}'

    def is_contains(self, p: Point) -> bool:
        return self.lower.x <= p.x <= self.upper.x and self.lower.y <= p.y <= self.upper.y


class Node(namedtuple("Node", "location left right")):
    """
    location: Point
    left: Node
    right: Node
    """
    def __repr__(self):
        return f'{tuple(self)!r}'


class KDTree:
    """k-d tree"""

    def __init__(self):
        self._root = None
        self._n = 0

    def insert(self, p: List[Point]):
        """insert a list of points"""
        def insert_rec(p: List[Point],depth):
            """
            p : a list of points
            depth : record the depth of the tree and get the dimension
            """
            if len(p) == 0:
                return None 
            """
            If the list p is none, the stop the recursion
            """ 

            # Select sorting dimension
            axis = depth % 2 
            """
            Take the remainder of the depth, the value is 0 or 1 , which means x-axis or y-axis respectively
            """

            # Create a new list which is order
            p_sorted = sorted(p, key= lambda p: p[axis]) 
            """
            Create a new list which is ordered, the code[key= lambda p: p[axis]]is written to select the dimension.
            When axis = 0, then the list is sorted by x [Point(x)], 1 is y
            """
            # Get the median index
            mid_idx = len(p_sorted) // 2
            """
            Find the median value of the list and make it as the root of the tree
            """

            # Create a node
            self._root = Node(p_sorted[mid_idx],insert_rec(p_sorted[:mid_idx], depth+1),insert_rec(p_sorted[mid_idx+1:], depth+1))
            """
            Create a new node, and do the recursive step at the node's left child and right child in a new separate list from the old points list.
            The rule to separate the old list is as the BST, but the dimension will change as the recursive goes on (It changes frome x to y in a two-dimension KD-tree)
            """
            return self._root
        return insert_rec(p,0)
            

    def range(self, rectangle: Rectangle) -> List[Point]:
        """range query"""
        def range_rec(node:Node, depth, r:Rectangle):
            if node is None:
                return []
            """
            node : a given node as the target
            depth : record the depth of the tree and get the dimension
            """
            
            axis = depth % 2
            result = []
            if r.is_contains(node.location):
                result.append(node.location)
            """
            If the node is in the rectangle, then put it in the result list
            """
            if rectangle.lower[axis] <= node.location[axis]:
                result.extend(range_rec(node.left, depth+1, rectangle))
            """
            If the value of x or y of the node's point is smaller than the rectangle, then we know that the node is at the left of the rectangle.
            So we should find whether the nodes at the given node's right is in the rectangle.
            Since the function range_rec will return a list, so we need to use the build function extend, which will add a iterator to the list.
            """
            if node.location[axis] <= rectangle.upper[axis]:
                result.extend(range_rec(node.right, depth+1, rectangle))
            """
            If the value of x or y of the node's point is larger than the rectangle, then we know that the node is at the right of the rectangle.
            So we should find whether the nodes at the given node's left is in the rectangle.
            """
            return result
        
        return range_rec(self._root, 0, rectangle)

    # Bonus assignment
    def knn(self, target:Node,k):
        """find the nearest neighbor, which means that k = 1"""
        class _classifier(namedtuple('classifier', 'location distance')):
            """
            location: Point
            distance: int
            """
            def __repr__(self):
                return f'{tuple(self)!r}'
        """
        The mean reason I create the classifier is to store the node's point and the distance to the target.
        This mapping helps us find the location of the nearest node to the target node.
        """
                
        def distance(node:Node) -> _classifier:
            if node is None:
                return None
            dim = len(node.location)
            dis = 0
            for i in range(dim):
                dis = dis + (target.location[i] - node.location[i])**2
            cur_classifier = _classifier(location= node.location, distance=dis**0.5)
            return cur_classifier
        """
        The code is to calcualte the distance between given node and the target.
        """
        
        def knn_rec(node:Node):
            if node is None:
                return None
            result = []
            result.append(distance(node))
            if node.left is not None:
                result.extend(knn_rec(node.left))
            if node.right is not None:
                result.extend(knn_rec(node.right))
        
            
            result_sorted = sorted(result, key=lambda classifier: classifier[1])
            return result_sorted[:k] # How many neighbor you want
        """
        The recursive step is to find all distance of nodes in a K-D tree to the target .
        """
        
        return knn_rec(self._root,)[0].location


def range_test():
    points = [Point(7, 2), Point(5, 4), Point(9, 6), Point(4, 7), Point(8, 1), Point(2, 3)]
    kd = KDTree()
    kd.insert(points)
    result = kd.range(Rectangle(Point(0, 0), Point(6, 6)))
    assert sorted(result) == sorted([Point(2, 3), Point(5, 4)])


def performance_test():
    points = [Point(x, y) for x in range(1000) for y in range(1000)]

    lower = Point(500, 500)
    upper = Point(504, 504)
    rectangle = Rectangle(lower, upper)
    #  naive method
    start = int(round(time.time() * 1000))
    result1 = [p for p in points if rectangle.is_contains(p)]
    end = int(round(time.time() * 1000))
    print(f'Naive method: {end - start}ms')

    kd = KDTree()
    kd.insert(points)
    # k-d tree
    start = int(round(time.time() * 1000))
    result2 = kd.range(rectangle)
    end = int(round(time.time() * 1000))
    print(f'K-D tree: {end - start}ms')

    assert sorted(result1) == sorted(result2)

def knn_test():
    points = [Point(7, 2), Point(5, 4), Point(9, 6), Point(4, 7), Point(8, 1), Point(2, 3)]
    kd = KDTree()
    kd.insert(points)
    p = Node(Point(5,3), None, None)
    assert kd.knn(p,1) == Point(5,4)
    print(kd.knn(p,1))
    


if __name__ == '__main__':
    print('Range test:')
    range_test()
    print('Range test valid, do performance test:')
    performance_test()
    print('Performance test valid, check the nearest neighbor of point(5,3):')
    knn_test()