import numpy as np
import matplotlib.pyplot as plt

class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        
    def __repr__(self):
        return 'Point({}, {})'.format(self.x, self.y)
    
    def __str__(self):
        return '({}, {})'.format(self.x, self.y)
    
    def asTuple(self):
        return (self.x, self.y)
    
    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Point(x, y)
    
    def __eq__(self, other):
        return self.asTuple() == other.asTuple()
    
    def __ne__(self, other):
        return self.asTuple() != other.asTuple()
    
    def __lt__(self, other):
        return self.asTuple() < other.asTuple()
            
    def __gt__(self, other):
        return self.asTuple() > other.asTuple()
        
    def __le__(self, other):
        return self.asTuple() <= other.asTuple()
        
    def __ge__(self, other):
        return self.asTuple() >= other.asTuple()
    
    def plot(self, destination):
        destination.scatter(self.x, self.y, c="black", marker='.')
        
        
class Points(list):
    def __init__(self, *points):
        super().__init__(*points)
        self.nparray()
        
    def append(self, point):
        super().append(point)
        self.npx = np.append(self.npx, point.x)
        self.npy = np.append(self.npy, point.y)
        
    def pop(self, index):
        super().pop(index)
        self.npx = np.delete(self.npx, index) 
        self.npy = np.delete(self.npy, index)
    
    def plot(self, destination):
        destination.scatter(self.npx, self.npy, c="black", marker='.')
            
    def nparray(self):
        self.npx = np.array([point.x for point in self])
        self.npy = np.array([point.y for point in self])
            
    def convexHull(self):
        sorted_points = sorted(self)
        L_upper = sorted_points[0:2]
        for idx in range(2, len(sorted_points)):
            L_upper.append(sorted_points[idx])
            while len(L_upper) > 2 and not isClockwise(*L_upper[-3:]):
                L_upper.pop(-2)
        L_lower = sorted_points[-1:-3:-1]
        for idx in range(len(sorted_points) - 3, -1, -1):
            L_lower.append(sorted_points[idx])
            while len(L_lower) > 2 and not isClockwise(*L_lower[-3:]):
                L_lower.pop(-2)
        L_lower.pop(0)
        L_lower.pop(-1)
        hull_points = Points(L_upper + L_lower)
        hull = Polygon(hull_points)
        return hull
    
    @classmethod
    def fromNPArray(cls, x, y):
        points = cls()
        for idx, _ in enumerate(x):
            points.append(Point(x[idx], y[idx]))
        points.npx = x
        points.npy = y
        return points
            
class Line:
    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end
    
    def __repr__(self):
        return 'Line({}, {})'.format(repr(self.start), repr(self.end))
    
    def __str__(self):
        return '{} -> {}'.format(self.start, self.end)
    
    def __add__(self, other: Point):
        return Line(self.start + other, self.end + other)
    
    def plot(self, destination):
        destination.plot([self.start.x, self.end.x], [self.start.y, self.end.y], c="black")
        self.start.plot(destination)
        self.end.plot(destination)
        
        
class Polygon:
    def __init__(self, points: Points):
        self.points = points
        
    def __repr__(self):
        return 'Polygon({})'.format(', '.join(map(repr, self.points)))
    
    def __str__(self):
        return ' -> '.join(map(str, self.points + [self.points[0]]))
    
    def plot(self, destination):
        self.plotBoundary(destination)
        destination.fill(self.points.npx, self.points.npy, '#0F0F0F2F')
        
    def plotBoundary(self, destination):
        tmp_points = self.points + [self.points[0]]
        for idx, _ in enumerate(self.points):
            p1 = tmp_points[idx]
            p2 = tmp_points[idx + 1]
            l = Line(p1, p2)
            l.plot(destination)
            
    def isConvex(self):
        points = self.points + [self.points[0], self.points[1]]
        for idx, _ in enumerate(points[:-2]):
            if not isClockwise(points[idx], points[idx + 1], points[idx + 2]):
                return False
        return True
            
            
def isClockwise(p1: Point, p2: Point, p3: Point):
    det = (p2.x - p1.x) * (p3.y - p1.y) - (p2.y - p1.y) * (p3.x - p1.x)
    if det < 0:
        return True
    else:
        return False