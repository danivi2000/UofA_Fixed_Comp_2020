from marker_class import Marker
from scipy.spatial.distance import cdist
import numpy as np
from collections import OrderedDict
from collections import deque
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from random import random


class Skeleton:
    """ Track markers on a person over consecutive frames given the location of
        markers from various sources with known or unknown identity.

        NOTE: you MUST update the skeleton every frame

        eg. Detecting green circular markers using a sterocamera and then using those 3D locations
            to match each identified point to a marker on the skeleton and update the new position.
    """
    n_dims = 3 #3-dimensional skeleton
    origin = "spine_base"
    # each point references only those connected directly to it moving away from spine base, in the format ((joint,dist),(joint,dist),..)
    # any point that has nothing outwards of it is an empty tuple
    # NOTE: ***** DON'T FORGET TO PUT A COMMA AFTER THE ITEM IF IT IS LENGTH 1 TO KEEP IT A NESTED TUPLE ******
    anatomical_connections = {"spine_base": {("l_hip",0.33),("r_hip",0.33),("chest",1.1)},
                              "l_hip": {("l_knee",0.6)},
                              "r_hip": {("r_knee",0.6)},
                              "chest": {("r_shoulder",0.45),("l_shoulder",0.45)},
                              "l_knee": {("l_foot",0.6)},
                              "r_knee": {("r_foot",0.6)},
                              "l_foot": {},
                              "r_foot": {},
                              "l_shoulder": {("l_elbow",0.4)},
                              "r_shoulder": {("r_elbow",0.4)},
                              "l_elbow": {("l_hand",0.4)},
                              "r_elbow": {("r_hand",0.3)},
                              "l_hand": {},
                              "r_hand": {}}

    def __init__(self):
        self.markers = OrderedDict()
        self.tracking_threshold = 10

    def add_marker(self, marker_position, initpos=[0,0,0]):
        if marker_position not in Skeleton.anatomical_connections:
            raise ValueError("%s is not an allowable part to track." % marker_position)
        self.markers[marker_position] = Marker(marker_position, initpos)

    def assign_to_nearest_marker(self, points):
        """
        Find nearest marker position for each point (from stereocameras) and use all points
        that are nearest to a marker to get the new marker position.

        NOTE: this does not do anything to markers that are non-visible
        """
        if np.shape(points)[1] != Skeleton.n_dims:
            # if no points are given, just assume no markers are visible and return
            if points.size == 0:
                for marker in self.markers.values():
                    marker.set_to_invisible()
                return
            # if there is data but wrong dimensions, cannot proceed
            else:
                raise ValueError("Wrong dimensions on points")
        marker_positions = self.get_marker_positions()
        distances = cdist(points, marker_positions)
        closest_indices = np.argmin(distances, axis=1)
        # for each marker "X", average all the points that have marker "X" as
        # their closest marker
        for i, name in enumerate(self.markers):
            # ONLY update the position with the average of the points if there are points
            # close to the marker
            close_points = np.where(closest_indices==i)[0] #find all points whose nearest marker is the current one
            if close_points.size > 0:
                mean_pos = np.mean(points[close_points], axis=0) #"flatten" array by averaging
                self.markers[name].set_to_visible()
                self.markers[name].update_pos(mean_pos, update_history=False)
            # if there are no points near the marker, the marker is set to invisible and then estimate
            else:
                self.markers[name].set_to_invisible()

    def estimate_invisible_markers(self, estimation_type="linear_extrapolate"):
        """Estimates positions of all invisible markers"""
        invisible_markers = self.get_invisible_markers()
        # visible_markers = self.get_visible_markers()
        if estimation_type=="linear_extrapolate":
            for marker in invisible_markers:
                prev_pos = marker.get_previous_positions()
                extrapolated_point = self.linear_extrapolate(prev_pos)
                marker.update_pos(extrapolated_point, update_history=False)

    def linear_extrapolate(self, previous_positions):
        deltas = np.diff(previous_positions, axis=0)
        avg_vector = np.mean(deltas, axis=0)
        extrapolated_point = np.add(previous_positions[-1], avg_vector) # extend average vector by one frame
        return extrapolated_point

    def get_invisible_markers(self, property_to_get=None):
        # no property returns the Marker objects
        if property:
            if property == "name":
                return [marker.name for marker in self.markers.values() if not marker.is_visible()]
            if property == "position":
                return [marker.get_pos() for marker in self.markers.values() if not marker.is_visible()]
        return [marker for marker in self.markers.values() if not marker.is_visible()]

    def get_visible_markers(self, property_to_get=None):
        # no property returns the Marker objects
        if property:
            if property == "name":
                return [marker.name for marker in self.markers.values() if marker.is_visible()]
            if property == "position":
                return [marker.get_pos() for marker in self.markers.values() if marker.is_visible()]
        return [marker for marker in self.markers.values() if marker.is_visible()]

    def get_marker_positions(self):
        """Get position for each marker stored in the skeleton and return as numpy array"""
        if self.num_markers() > 0:
            positions = np.zeros((self.num_markers(),Skeleton.n_dims), dtype=float)
            for i, marker in enumerate(self.markers.values()):
                positions[i] = marker.get_pos()
            return positions

    def num_markers(self):
        return len(self.markers)

    def apply_rigid_body(self):
        # start from an origin and move outwards, correcting each point on a limb as you move towards periphery
        # until you reach the end of the limb and all sublimbs
        stack = [Skeleton.origin]

        while len(stack) > 0:
            reference_joint = stack.pop()
            for next_joint, rigid_dist in Skeleton.anatomical_connections[reference_joint]:
                if (reference_joint in self.markers) and (next_joint in self.markers): #only adjust distance if the two joints are currently being tracked
                    reference_pos = self.markers[reference_joint].get_pos()
                    next_pos = self.markers[next_joint].get_pos()
                    real_dist = cdist([reference_pos], [next_pos])
                    t_value = float(rigid_dist/real_dist)
                    corrected_next_pos = self.find3Dpoint(reference_pos, next_pos, t_value)
                    self.markers[next_joint].update_pos(corrected_next_pos, update_history=True)
                    corrected_dist = cdist([reference_pos], [corrected_next_pos])
                    # print("[%s-->%s]  Ex:%0.2f  Ac:%0.2f  Corrected:%0.2f" % (reference_joint, next_joint, rigid_dist, real_dist, corrected_dist))
                # next path to explore (even if not being tracked, further parts of the limb may be tracked)
                stack.append(next_joint) 
        
    def find3Dpoint(self, point1, point2, t):
        """
        A t value of 1 will return point2 since it is one unit distance away from point2.
        The unit distance is the magnitude of the direction vector from point1, and the direction
        vector is determined from the difference between point2-point1. Which ultimately means the unit
        distance is the distance between point1 and point2.

        Point1 is the reference, so t=0 will return point1.

        If you want a point between point1 and point2,    use 0<t<1.
        If you want a point past point2 (away from point1), use t>1.
        If you want a point past point1 (away from point2), use t<0.
        """
        d = np.subtract(point2,point1) #direction vector defined as the elementwise difference between the points
        t_d = np.dot(t,d)
        return np.add(point1, t_d) # r = r0 + t(d)
                

    def __repr__(self):
        heading = "SKELETON DATA"
        top = "~" * len(heading)
        bottom = "^" * len(heading)
        out_list = []
        out_list.append(top)
        out_list.append(heading)
        if self.num_markers() > 0:
            for name, marker in self.markers.items():
                out_list.append("@" + name + ": %r" % marker)
        else:
            out_list.append("no markers")
        out_list.append(bottom)
        return "\n".join(out_list)

    def __str__(self):
        heading = "SKELETON DATA"
        top = "~" * len(heading)
        bottom = "^" * len(heading)
        out_list = []
        out_list.append(top)
        out_list.append(heading)
        if self.num_markers() > 0:
            for name, marker in self.markers.items():
                out_list.append("@" + name + ": " + str(marker.get_pos()) + " | Visible: " + str(marker.is_visible()))
        else:
            out_list.append("no markers")
        out_list.append(bottom)
        return "\n".join(out_list)

    def update(self, points):
        """
        CALL THIS EVERY FRAME
        points: 3D points for each marker detected from each stereo camera setup (in no particular order,
        but must be a Nx3 numpy array  ie. [[x1,y1,z1],
                                            [x2,y2,z2])
        """
        # update the marker positions using the points given
        self.assign_to_nearest_marker(points)
        # for any hidden markers, estimate their location and update
        self.estimate_invisible_markers()
        # apply anatomical connections to get more reasonable result
        self.apply_rigid_body()

    def plot3D(self):
        ax = plt.gca(projection='3d')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        pts = self.get_marker_positions()
        Xs = pts[:, 0]
        Ys = pts[:, 1]
        Zs = pts[:, 2]
        ax.scatter(Xs, Ys, Zs, c="b", marker='o')
        for i, name in enumerate(self.markers):
            ax.text(Xs[i], Ys[i], Zs[i], name)
        plt.show()

    def plot3D_connections(self):
        """NONFUNCTIONAL
        """
        ax = plt.gca(projection='3d')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        stack = [Skeleton.origin]
        while len(stack) > 0:
            reference_joint = stack.pop()
            for next_joint, rigid_dist in Skeleton.anatomical_connections[reference_joint]:
                if (reference_joint in self.markers) and (next_joint in self.markers): #only adjust distance if the two joints are currently being tracked
                    reference_pos = self.markers[reference_joint].get_pos()
                    next_pos = self.markers[next_joint].get_pos()
                    ax.plot([reference_pos[0]]+[next_pos[0]], [reference_pos[1]]+[next_pos[1]], [reference_pos[2]]+[next_pos[2]], c="b")
                # next path to explore (even if not being tracked, further parts of the limb may be tracked)
                stack.append(next_joint) 
        pts = self.get_marker_positions()
        Xs = pts[:, 0]
        Ys = pts[:, 1]
        Zs = pts[:, 2]
        for i, name in enumerate(self.markers):
            ax.text(Xs[i], Ys[i], Zs[i], name)
        ax.set_xlim3d(-1,1)
        ax.set_ylim3d(-1,1)
        ax.set_zlim3d(-1,1)
        plt.show()
        



def test1():
    sk = Skeleton()
    sk.add_marker("spine_base", initpos=[0,0,0])
    sk.add_marker("l_knee", initpos=[-0.7,-0.5,0])
    sk.add_marker("l_foot", initpos=[-1,-1,0])
    sk.add_marker("r_knee", initpos=[0.7,-0.5,0])
    sk.add_marker("r_foot", initpos=[1,-1,0])
    sk.add_marker("l_hip", initpos=[-0.3,-0.1,0])
    sk.add_marker("r_hip", initpos=[0.3,-0.1,0])
    sk.add_marker("chest", initpos=[0,1,0])
    sk.add_marker("l_shoulder", initpos=[-0.4,1,0])
    sk.add_marker("r_shoulder", initpos=[0.4,1,0])
    print(sk)
    print()
    # points = np.array([[0,0,-0.1],[0,1.1,-0.1]])
    # print(sk)
    # print()
    # next_points = np.array([[5,5,5],[4,4,4],[1,1,1]])
    # sk.update(next_points)
    # print(sk)
    # print()
    # next_points = np.array([[500,500,400],[-30,-40,-39.4]])
    # sk.update(next_points)
    # print(sk)
    # print()
    for i in range(100):
        sk.update(np.array([[]]))
    print(sk)
    print()
    sk.plot3D()

def test2():
    sk = Skeleton()
    sk.add_marker("spine_base", initpos=[random(),random(),random()])
    sk.add_marker("l_knee", initpos=[random(),random(),random()])
    sk.add_marker("l_foot", initpos=[random(),random(),random()])
    sk.add_marker("r_knee", initpos=[random(),random(),random()])
    sk.add_marker("r_foot", initpos=[random(),random(),random()])
    sk.add_marker("l_hip", initpos=[random(),random(),random()])
    sk.add_marker("r_hip", initpos=[random(),random(),random()])
    sk.add_marker("chest", initpos=[random(),random(),random()])
    sk.add_marker("l_shoulder", initpos=[random(),random(),random()])
    sk.add_marker("r_shoulder", initpos=[random(),random(),random()])
    # should drag points towards reasonable positions
    sk.add_marker("r_elbow", initpos=[random(),random(),random()])
    sk.add_marker("l_elbow", initpos=[random(),random(),random()])
    sk.add_marker("l_hand", initpos=[random(),random(),random()])
    sk.add_marker("r_hand", initpos=[random(),random(),random()])
    sk.plot3D_connections()
    for i in range(100):
        sk.update(np.array([[]]))
    sk.plot3D_connections()

def test3():
    sk = Skeleton()
    sk.add_marker("spine_base", initpos=[0,0,0])
    sk.add_marker("l_knee", initpos=[-0.7,-0.5,0.3])
    sk.add_marker("l_foot", initpos=[-1,-1,0])
    sk.add_marker("r_knee", initpos=[0.7,-0.5,0.3])
    sk.add_marker("r_foot", initpos=[1,-1,0])
    sk.add_marker("l_hip", initpos=[-0.3,-0.1,0])
    sk.add_marker("r_hip", initpos=[0.3,-0.1,0])
    sk.add_marker("chest", initpos=[0,1,0])
    sk.add_marker("l_shoulder", initpos=[-0.4,1,0])
    sk.add_marker("r_shoulder", initpos=[0.4,1,0])
    for i in range(100):
        sk.update(np.array([[]]))
    sk.plot3D_connections()

if __name__ == "__main__":
    # test1()
    # test2()
    test3()