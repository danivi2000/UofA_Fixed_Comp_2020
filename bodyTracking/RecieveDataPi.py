"""
Read data from a single Raspi/Stereocamera setup streaming the position of all visible markers.
"""

from pylsl import StreamInlet, resolve_stream
import numpy as np
import sys
from skeleton_class import Skeleton
from marker_class import Marker
import threading
import time
import os


# Global Variables
mutex = threading.Lock()

sk = Skeleton()

n_markers = 10
n_dimensions = 3
marker_names = ["r_foot", "l_foot", "l_knee", "r_knee", "l_hip", "r_hip", "spine_base", "chest", "l_shoulder",
                "r_shoulder"]
initial_marker_positions = []

for name in marker_names:
    sk.add_marker(name)

if len(marker_names) != n_markers:
    raise Exception("Error: mismatch between number of markers and body parts to track.")


class Stream:

    def __init__(self, camera='stereocam'):
        # first resolve a stereocam stream on the lab network
        print("looking for a stereocam stream...")
        #self.streams = resolve_stream('type', camera)

        # create a new inlet to read from the stream
        #self.inlet = StreamInlet(self.streams[0])
        self.centroids = np.zeros((n_markers, n_dimensions))

    def stream_data(self):

        while True:
            # grab each sample (containing 3D location of each marker)
            sample, timestamp = self.inlet.pull_sample()
            sample = np.array(sample)
            sample = sample.reshape(n_markers, n_dimensions)

            # update skeleton data, protect with mutex
            mutex.acquire()
            try:
                print("thread: {}".format(threading.current_thread().name))
                print("ID {}".format(os.getpid()))
                sk.update(sample)
                self.centroids = self.centroids + 1
                print(sk.get_marker_positions())
                print(self.centroids)
                # print(sample,"@",timestamp, end='\n\n')
            finally:
                mutex.release()
                print('done')
            time.sleep(1)


def main():

    n_cameras = sys.argv[1]
    threads = []
    streams = []

    # Create threads
    for i in range(int(n_cameras)):
        streams.append(Stream('stereocam'+str(i)))
        threads.append(threading.Thread(target=streams[i].stream_data, name='t'+str(i)))

    # Start all threads
    for thread in threads:
        thread.start()

    # Join all threads
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
