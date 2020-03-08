# import the necessary packages
from __future__ import print_function
from collections import deque
from imutils.video.pivideostream import PiVideoStream
from imutils.video import FPS
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import imutils
import time
import cv2
import numpy as np
from find_matching_points import *
import scipy
from pylsl import StreamInfo, StreamOutlet
#NOTE: scipy.spatial.distance.cdist only works if you import the NearestNeighbors from sklearn.neighbors (done in find_matching_points.py)

# Things that need to be defined for a single stereo camera setup:
# -projection matrix for left and right cameras
# -affine transformation relative to the primary camera

#TODO:
# -fix non-unique indices somehow


#lsl setup
num_markers = 10
max_Hz = 10
dimensions = 3
n_channels = num_markers*dimensions
info = StreamInfo('raspi', 'stereocam', n_channels, max_Hz, 'float32', 'raspi1')
outlet = StreamOutlet(info)
print('Created stream...')


# load affine matrix
affine_mat = np.load("affine_mat.npy")
affine_mat = np.load("identity_matrix.npy")
guessed_rot = np.load("guessed_mat.npy")

def fix_center_indices(centers):
    # find matching points, then correct the indices to have matching points aligned
    # also converts coordinates to numpy arrays to use in triangulatePoints
    centers = remove_unmatched_points(centers)
    left_points = np.array(centers["left"]).T
    right_points = np.array(centers["right"]).T
    correct_indices,_ = icp(right_points, left_points) #maps right points to left points, so reference is left points
    n_points = len(correct_indices)
    if len(np.unique(correct_indices)) != n_points:
        raise Exception("Non-unique indices")
    new_right_points = right_points.copy()
    for old_i in range(n_points):
        new_i = correct_indices[old_i]
        new_right_points[new_i] = right_points[old_i]
    centers["left"] = np.float32(centers["left"])
    centers["right"] = np.float32(new_right_points).T
    print("[INDICES]", correct_indices)
    return centers

def remove_unmatched_points(centers):
    left_points = np.array(centers["left"]).T
    right_points = np.array(centers["right"]).T
    # if they are equal sized, just return it for now (there should be other checks but haven't dont them yet
    # like checking for points in weird spots)
    if len(left_points) == len(right_points):
        return centers
    else:
        # calculate the distance to the closest point from the other side and then remove the points
        # with the greatest distance to their nearest point until both sides have the same number of
        # points
        dist = scipy.spatial.distance.cdist(left_points,right_points,'euclidean')
        num_points = min(len(left_points), len(right_points))
        if len(left_points)>len(right_points):
            longer = left_points
            longer_name = "left"
            ax = 1
        else:
            longer = right_points
            longer_name = "right"
            ax = 0
        min_dist = np.amin(dist, axis=ax)
        print("[Shortest Distances]", min_dist)
        bad_indices = []
        current_points = len(longer)
        while current_points > num_points:
            farthest = np.argmax(min_dist)
            bad_indices.append(farthest)
            min_dist[farthest] = 0
            current_points -= 1
        longer = np.delete(longer,bad_indices,0)
        centers[longer_name] = longer.T
        print("[Bad Indices]", bad_indices)
        return centers
        
            
    

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--display", type=int, default=-1,
    help="Whether or not frames should be displayed")
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="Max buffer size")
args = vars(ap.parse_args())

# blob detector parameters
params = cv2.SimpleBlobDetector_Params()
params.filterByConvexity = False
params.filterByInertia = False
params.filterByCircularity = True
params.minCircularity = 0.2
params.filterByArea = True
params.minArea = 3000 #units in pixels
params.maxArea = 40000 #units in pixels
#params.filterByColor = True
#params.blobColor = 255

# creat blob detector
detector = cv2.SimpleBlobDetector_create(params)

# initialize paramaters
lower_colour = (25,80,6) #green
upper_colour = (85,255,255) #green
#lower_colour = (20,100,100) #yellow
#upper_colour = (30,255,255) #yellow
downscale_factor = 1 # downscale for speed  (greater than one reduces the image size and increases framerate)
pts = deque(maxlen=args["buffer"])

# load camera projection matrices to triangulate points
l_proj_mat = np.load("l_proj_mat.npy")
r_proj_mat = np.load("r_proj_mat.npy")

# Camera settimgs
#cam_width = 1280
#cam_height = 480

# Final image capture settings
#scale_ratio = 0.5

# Camera resolution height must be divisible by 16, and width by 32
#cam_width = int((cam_width+31)/32)*32
#cam_height = int((cam_height+15)/16)*16
#print ("Used camera resolution: "+str(cam_width)+" x "+str(cam_height))

# calculate image size
#img_width = int (cam_width * scale_ratio)
#img_height = int (cam_height * scale_ratio)
#print ("Scaled image resolution: "+str(img_width)+" x "+str(img_height))

# created a *threaded *video stream, allow the camera sensor to warmup,
# and start the FPS counter
print("[INFO] Beginning ball tracking...")
res = (320,240)
vs = PiVideoStream(resolution=res).start() #default resolution is 320x240
img_width = vs.camera.resolution[1]//downscale_factor
time.sleep(2.0)
fps = FPS().start()
capture = True
start_time = time.time()
# capture frames continuously
while capture:
    # reset blobs from previous frame
    centers = {"left":[[],[]],
               "right":[[],[]]} #for storing x,y coordinates as [[x1,x2,x3], [y1,y2,y3]]
    split_imgs = {}
    keypoints = {"left":None,
                 "right":None}
    imgs_to_show = {}

    # grab the frame from the threaded video stream
    pair_img = vs.read()
    #split_imgs["left"] = pair_img[0:img_height,0:int(img_width/2)]
    #split_imgs["right"] = pair_img[0:img_height,int(img_width/2):img_width]
    split_imgs["left"] = pair_img[:, 0:310] #for testing with single camera
    split_imgs["right"] = pair_img[:, 10:] #for testing with single camera
    
    for side in ["left","right"]:
        frame = split_imgs[side]
        # resize frame, blur, and convert to HSV colorspace
        frame = imutils.resize(frame, width=img_width)
        blurred = cv2.GaussianBlur(frame, (9,9), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # find blobs
        thresh_img = cv2.inRange(hsv, lower_colour, upper_colour)
        thresh_img = cv2.bitwise_not(thresh_img) #invert image (supposed to help blob detection)
        keypoints[side] = detector.detect(thresh_img)

        # get center coordinates of each blob
        for i in range(len(keypoints[side])):
            centers[side][0].append(keypoints[side][i].pt[0]) # X-coordinate
            centers[side][1].append(keypoints[side][i].pt[1]) # Y-coordinate

        # check to see if the frame should be displayed to our screen
        if args["display"] > 0:
            frame_with_keypoints = cv2.drawKeypoints(frame, keypoints[side], np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            thresh_with_keypoints = cv2.drawKeypoints(cv2.cvtColor(thresh_img, cv2.COLOR_GRAY2BGR), keypoints[side], np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            #cv2.imshow(side, frame_with_keypoints)
            #cv2.imshow("Threshold %s" % side, thresh_img)
            imgs_to_show[side] = cv2.vconcat([frame_with_keypoints, thresh_with_keypoints])
            key = cv2.waitKey(1) & 0xFF 
            if key == ord("q"):
                capture = False
        else:
            if time.time()-start_time > 15:
                capture = False
            
    # triangulate points and convert to Euclidian (from Homogeneous) (only if points found in both images)
    if len(keypoints["left"])>0 and len(keypoints["right"])>0:
        #remove non-matching points and get corresponding indices between images
        centers = fix_center_indices(centers)
        pts4D = cv2.triangulatePoints(l_proj_mat, r_proj_mat, centers["left"], centers["right"])
        pts_without_affine = cv2.convertPointsFromHomogeneous(pts4D.T).reshape(-1, 3)
        # have to convert to 3d then back to homogeneous to "get" scale data stored in 4th dimension (otherwise the units are meaningless)
        # this is because the affine_matrix is calculated assuming w=1
        pts3D = cv2.convertPointsFromHomogeneous(pts4D.T).reshape(-1, 3) #pts3D is in format [[x1,y1,z1],[x2,y2,z2],...]
        pts4D = cv2.convertPointsToHomogeneous(pts3D).reshape(-1, 4) #pts3D is in format [[x1,y1,z1],[x2,y2,z2],...]
        #correct based on orientation compared to primary camera (it also converts to 3D)
        pts3D = affine_mat.dot(pts4D.T).T
        #pts3D = guessed_rot.dot(pts3D.T).T
        print("[3D POINTS]", pts3D)
        #rint("[ORIGINAL for above]", pts_without_affine)
    
    else:
        pts3D = np.array([[0,0,0]], dtype=float)
        print("[3D POINTS]", pts3D)
        
    # display nice images
    if args["display"] > 0:
        cv2.imshow("<--Left    |    Right-->", cv2.hconcat([imgs_to_show["left"], imgs_to_show["right"]]))
    
    # send data to lsl
    data_to_send = list(pts3D.reshape(-1)) #flatten to 1D
    data_to_send += [0.0]*(n_channels-len(data_to_send)) #pad with zeros to fill all channels
    outlet.push_sample(data_to_send)
    
    # update the FPS counter
    fps.update()
    

# stop the timer and display FPS
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# cleanup
cv2.destroyAllWindows()
vs.stop()