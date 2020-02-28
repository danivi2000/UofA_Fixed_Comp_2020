import time
from random import random as rand
from pylsl import StreamInfo, StreamOutlet

num_channels = 8

info = StreamInfo('BioSemi', 'EEG', num_channels, 100, 'float32', 'myuid34234')
outlet = StreamOutlet(info)

print("Now sending data...")
while True:
    mysample = [rand() for _ in range(num_channels)]
    outlet.push_sample(mysample)
    time.sleep(0.01)
