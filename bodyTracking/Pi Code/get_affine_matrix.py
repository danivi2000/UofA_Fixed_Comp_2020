"""
Use 3D points from two stereo camera setups imaging the same chessboard between them to
allow the coordinates from one setup to be mapped to those of the other (and thus get a
global coordinate system)

-Rotate a set of 3D points based on the initial guess of the angle between two camera setups.
-Then use RANSAC to match the points to those from the reference
 camera setup and get the Affine transformation matrix (that can be applied to homogeneous points).
-Applying the original 3D guess with the new R and T will properly transform points from the
 coordinate system of one camera setup to that of the reference setup.

NOTE: the initial guess is used to avoid matching the points 90,180,270deg off
"""
import numpy as np
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from find_matching_points import *


theta_guess = 45
theta = np.radians(theta_guess)
S = np.sin(theta)
C = np.cos(theta)
R_matrices = {"Rx":np.array([[ 1, 0, 0],
                                 [ 0, C,-S],
                                 [ 0, S, C]], dtype=np.float32), # rotation matrix for rotation around x-axis (on YZ plane)
                  "Ry":np.array([[ C, 0, S],
                                 [ 0, 1, 0],
                                 [-S, 0, C]], dtype=np.float32), # rotation matrix for rotation around y-axis (on XZ plane)
                  "Rz":np.array([[ C,-S, 0],
                                 [ S, C, 0],
                                 [ 0, 0, 1]], dtype=np.float32) # rotation matrix for rotation around z-axis (on XY plane)
            }



#testing
if __name__ == "__main__":
    # DEFINE THESE
    # reference_pts are the checkerboard corners from Primary Stereocamera
    # other_pts are the checkerboard corners from Secondary Stereocamera
    # define theta_guess too
    reference_pts = np.load('pts3D.npy')
    other_pts = np.load('pts3D.npy')
    rot_axis = "Ry" #for guess
    
    # calculate the points to use in RANSAC by rotating the input points from Secondary camera using the guessed angle between the cameras
    guessed_pts = R_matrices[rot_axis].dot(other_pts.T).T
    homog_pts = cv2.convertPointsToHomogeneous(guessed_pts).reshape(-1, 4)
    
    #use affine RANSAC to get correct points
    retval, out_mat, inliers = cv2.estimateAffine3D(guessed_pts, reference_pts)
    np.save("guessed_mat.npy", R_matrices[rot_axis])
    np.save("affine_mat.npy", out_mat)
    affine_pts = out_mat.dot(homog_pts.T).T
    #affine_pts = cv2.convertPointsFromHomogeneous(affine_pts).reshape(-1,3)
    

    # plot original points in blue and rotated poitns in red, fixed points in yellow
    # (WE WANT RED==YELLOW FOR PERFECT FIT)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    pts_list = [reference_pts,other_pts,guessed_pts,affine_pts]
    i = 0
    for pts in pts_list:
        color = ["b","r","y","g"][i]
        Xs = pts[:, 0]
        Ys = pts[:, 1]
        Zs = pts[:, 2]
        ax.scatter(Xs, Ys, Zs, c=color, marker='o')
        i += 1
    plt.show()