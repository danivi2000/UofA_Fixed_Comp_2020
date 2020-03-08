"""
Read data from a single Raspi/Stereocamera setup streaming the position of all visible markers.
"""

from pylsl import StreamInlet, resolve_stream
import numpy as np
from skeleton_class import Skeleton
from marker_class import Marker

# first resolve a stereocam stream on the lab network
print("looking for a stereocam stream...")
streams = resolve_stream('type', 'stereocam')
n_markers = 10
n_dimensions = 3
marker_names = ["r_foot", "l_foot","l_knee","r_knee","l_hip","r_hip","spine_base","chest","l_shoulder","r_shoulder"]
initial_marker_positions = []
if len(marker_names) != n_markers:
    raise Exception("Error: mismatch between number of markers and body parts to track.")
sk = Skeleton()
for name in marker_names:
    sk.add_marker(name)

# create a new inlet to read from the stream
inlet = StreamInlet(streams[0])
centroids = np.zeros((n_markers, n_dimensions))
while True:
    # grab each sample (containing 3D location of each marker)
    sample, timestamp = inlet.pull_sample()
    sample = np.array(sample)
    sample = sample.reshape(n_markers, n_dimensions)

    #update skeleton data
    sk.update(sample)
    print(sk.get_marker_positions())
    # print(sample,"@",timestamp, end='\n\n')