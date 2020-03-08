import numpy as np
from collections import deque

class Marker:

    n_dims = 3

    def __init__(self, name, initpos=np.array([0,0,0],dtype=float), memory_size=3):
        
        if len(initpos) != 3:
            raise ValueError("Position must be a 1x3 array or list.")
        if isinstance(initpos, type(np.array([]))):
            self.pos = initpos
        else:
            self.pos = np.array(initpos, dtype=float)
        self.visible = False
        self.name = name
        self.memory_size = memory_size
        self.old_pos = deque([self.pos]*self.memory_size, maxlen=self.memory_size)

    def update_pos(self, new_pos, update_history=False):
        if len(new_pos) != Marker.n_dims:
            raise Exception("Incorrect dimensions for updating positon")
        if update_history:
            self.old_pos.popleft()
            self.old_pos.append(self.pos)
        self.pos = np.array(new_pos, dtype=float)

    def get_pos(self):
        return self.pos

    def get_previous_positions(self, stop_drift=True):
        """
        Stop drift will set all previous positions to current position if the marker has not been
        visible for the length of it's memory.

        Return: numpy array of previous positions and current position of marker 
                from oldest to newest going from row 0->self.memory_size+1 (current position at end)
        """
        previous_points = np.zeros((self.memory_size+1, Marker.n_dims))
        try:
            for i in range(self.memory_size):
                previous_points[i][:] = self.old_pos[i]
        except IndexError:
            pass
        previous_points[self.memory_size][:] = self.pos
        return previous_points

    def set_to_visible(self):
        self.visible = True

    def set_to_invisible(self):
        # call if you don't want to update position (ie. not a complete frame time)
        self.visible = False

    def is_visible(self):
        return self.visible

    def __repr__(self):
        out_list = []
        out_list.append("Marker<<")
        out_list.append("Name: %s,  " % self.name)
        out_list.append("Previous Positions: %s,  " % str(self.old_pos))
        out_list.append("Current Position: %s,  " % str(self.pos))
        out_list.append("Visible: %s" % str(self.visible))
        out_list.append(">>")
        return "".join(out_list)

if __name__ == "__main__":
    mk = Marker("test")
    print(mk.get_previous_positions())
    print()
    mk.update_pos([1,1,1])
    print(mk.get_previous_positions())
    print()
    mk.update_pos([2,2,2])
    print(mk.get_previous_positions())
    print()
    mk.update_pos([3,2,2])
    print(mk.get_previous_positions())
    print()
    mk.update_pos([4,2,2])
    print(mk.get_previous_positions())
    print()
    mk.update_pos([5,2,2])
    print(mk.get_previous_positions())