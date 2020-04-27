import math
import random
import matplotlib
#matplotlib.use("TkAgg")

from ps3_visualize import *
import pylab

# === Provided class Position, do NOT change
class Position(object):
    """
    A Position represents a location in a two-dimensional room, where
    coordinates are given by floats (x, y).
    """
    def __init__(self, x, y):
        """
        Initializes a position with coordinates (x, y).
        """
        self.x = x
        self.y = y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_new_position(self, angle, speed):
        """
        Computes and returns the new Position after a single clock-tick has
        passed, with this object as the current position, and with the
        specified angle and speed.

        Does NOT test whether the returned position fits inside the room.

        angle: float representing angle in degrees, 0 <= angle < 360
        speed: positive float representing speed

        Returns: a Position object representing the new position.
        """
        old_x, old_y = self.get_x(), self.get_y()

        # Compute the change in position
        delta_y = speed * math.cos(math.radians(angle))
        delta_x = speed * math.sin(math.radians(angle))

        # Add that to the existing position
        new_x = old_x + delta_x
        new_y = old_y + delta_y

        return Position(new_x, new_y)

    def __str__(self):
        return "Position: " + str(math.floor(self.x)) + ", " + str(math.floor(self.y))

# === Problem 1
class SimpleRoom(object):
    """
    A SimpleRoom represents a rectangular region containing clean or dirty
    tiles.

    A room has a width and a height and contains (width * height) tiles. Each tile
    has some fixed amount of dirt. The tile is considered clean only when the amount
    of dirt on this tile is 0.
    """
    def __init__(self, width, height, dirt_amount):
        """
        Initializes a rectangular room with the specified width, height, and
        dirt_amount on each tile.

        width: an integer > 0
        height: an integer > 0
        dirt_amount: an integer >= 0
        """
        self.width = width
        self.height = height
        self.dirt_amount = dirt_amount
        self.tiles_dirt = {}
        for p in range(self.width):
            for q in range(self.height):
                    self.tiles_dirt[(p, q)] = self.dirt_amount #Sets each tile's dirt amount to given amount.

    def clean_tile_at_position(self, pos, capacity):
        """
        Mark the tile under the position pos as cleaned by capacity amount of dirt.

        Assumes that pos represents a valid position inside this room.

        pos: a Position object
        capacity: the amount of dirt to be cleaned in a single time-step
                  can be negative which would mean adding dirt to the tile

        Note: The amount of dirt on each tile should be NON-NEGATIVE.
              If the capacity exceeds the amount of dirt on the tile, mark it as 0.
        """
        int_x = int(pos.get_x())
        int_y = int(pos.get_y())
        if capacity <= self.tiles_dirt[(int_x, int_y)]: #Removes capacity amount of dirt if capacity is less, otherwise removes all possible dirt.
            self.tiles_dirt[(int_x, int_y)] -= capacity  
        else:
            self.tiles_dirt[(int_x, int_y)] = 0

    def is_tile_cleaned(self, m, n):
        """
        Return True if the tile (m, n) has been cleaned.

        Assumes that (m, n) represents a valid tile inside the room.

        m: an integer
        n: an integer

        Returns: True if the tile (m, n) is cleaned, False otherwise

        Note: The tile is considered clean only when the amount of dirt on this
              tile is 0.
        """
        return self.tiles_dirt[(m, n)] == 0
        
    def get_num_cleaned_tiles(self):
        """
        Returns: an integer; the total number of clean tiles in the room
        """
        num_clean_tiles = 0
        for value in self.tiles_dirt.values(): #Goes through the dirt amounts on each tile and adds 1 for each clean one.
            if value == 0:
                num_clean_tiles+=1
        return num_clean_tiles
                
        
    def is_position_in_room(self, pos):
        """
        Determines if pos is inside the room.

        pos: a Position object.
        Returns: True if pos is in the room, False otherwise.
        """
        x_cor = pos.get_x()
        y_cor = pos.get_y()
        return (0 <= x_cor < self.width and 0 <= y_cor < self.height) #If both coordinates within range
            
        
    def get_dirt_amount(self, m, n):
        """
        Return the amount of dirt on the tile (m, n)

        Assumes that (m, n) represents a valid tile inside the room.

        m: an integer
        n: an integer

        Returns: an integer
        """
        return self.tiles_dirt[(m, n)]

    def get_num_tiles(self):
        """
        Returns: an integer; the total number of tiles in the room
        """
        return len(self.tiles_dirt)


    def get_random_position(self):
        """
        Returns: a Position object; a random position inside the room
        """
        a = random.uniform(0,self.width)
        b = random.uniform(0,self.height)
        return Position(a, b)

class Robot(object):
    """
    Represents a robot cleaning a particular room.

    At all times, the robot has a particular position and direction in the room.
    The robot also has a fixed speed and a fixed cleaning capacity.

    Subclasses of Robot should provide movement strategies by implementing
    update_position_and_clean, which simulates a single time-step.
    """
    def __init__(self, room, speed, capacity):
        """
        Initializes a Robot with the given speed and given cleaning capacity in the
        specified room. The robot initially has a random direction and a random
        position in the room.

        room:  a SimpleRoom object.
        speed: a float (speed > 0)
        capacity: a positive integer; the amount of dirt cleaned by the robot
                  in a single time-step
        """
        self.room = room
        self.speed = speed
        self.capacity = capacity
        self.position = room.get_random_position()
        self.direction = random.uniform(0,360) 

        

    def get_robot_position(self):
        """
        Returns: a Position object giving the robot's position in the room.
        """
        
        return self.position

    def get_robot_direction(self):
        """
        Returns: a float d giving the direction of the robot as an angle in
        degrees, 0.0 <= d < 360.0.
        """
        
        return self.direction
    
    def set_robot_position(self, position):
        """
        Set the position of the robot to position.

        position: a Position object.
        """
        self.position = position

    def set_robot_direction(self, direction):
        """
        Set the direction of the robot to direction.

        direction: float representing an angle in degrees
        """
        self.direction = direction

    def update_position_and_clean(self):
        """
        Simulates the passage of a single time-step.

        Moves robot to new position and cleans tile according to robot movement
        rules.
        """
        # do not change -- implement in subclasses
        raise NotImplementedError

# === Problem 2
class StandardRobot(Robot):
    """
    A StandardRobot is a Robot with the standard movement strategy.

    At each time-step, a StandardRobot attempts to move in its current
    direction; when it would hit a wall, it *instead*
    chooses a new direction randomly.
    """
    def update_position_and_clean(self):
        """
        Simulates the passage of a single time-step.

        Calculate the next position for the robot.

        If that position is valid, move the robot to that position. Mark the
        tile it is on as having been cleaned by capacity amount.

        If the new position is invalid, do not move or clean the tile, but
        rotate once to a random new direction.
        """
# Calculate possible new position. See if position is valid. If valid, set robot position to new position.
# If not valid, set direction to random direction and repeat process. 
        new_position = self.position.get_new_position(self.direction, self.speed)
        if self.room.is_position_in_room(new_position):
            self.set_robot_position(new_position)
            self.room.clean_tile_at_position(self.position, self.capacity)
        else:
            self.set_robot_direction(random.uniform(0,360))

#test_robot_movement(StandardRobot, SimpleRoom)

# === Problem 3
class CheapRobot(Robot):
    """
    A CheapRobot is a robot that may accidentally dirty a tile. A CheapRobot will
    dirty the tile it is on by dirty_amount units and pick a new, random direction for itself
    with probability p = 0.05 rather than simply cleaning the tile it moves to.
    """
    p = 0.05
    dirty_amount = 1

    @staticmethod
    def set_dirt_probability(prob):
        """
        Sets the probability of the robot accidentally dirtying the tile equal to prob.

        prob: a float (0 <= prob <= 1)
        """
        CheapRobot.p = prob

    @staticmethod
    def set_dirt_amount(amount):
        """
        Sets the amount of dirt that the CheapRobot may accidentally drop on the tile.

        amount: an int (amount > 0)
        """
        CheapRobot.dirty_amount = amount

    def drops_dirt(self):
        """
        Answers the question: Does the robot accidentally drop dirt on the tile
        at this timestep?
        The robot drops dirt with probability p.

        returns: True if the robot drops dirt on its tile, False otherwise.
        """
        return random.random() < CheapRobot.p

    def update_position_and_clean(self):
        """
        Simulates the passage of a single time-step.

        Check if the robot accidentally releases dirt. If so, dirty the current
        tile by dirty_amount and change its direction randomly.

        If the robot does not accidentally drop dirt, the robot should behave like
        StandardRobot at this time-step (checking if it can move to a new position,
        move there and clean if it can, pick a new direction and stay stationary if it can't)
        """
        
        
        # If the robot drops dirt,
        if self.drops_dirt():
            self.room.clean_tile_at_position(self.get_robot_position(), -CheapRobot.dirty_amount)
            self.set_robot_direction(random.uniform(0,360))
        # If the robot does not drop dirt,
        else:
            new_position = self.position.get_new_position(self.direction, self.speed)
            # Cleans tile in new position if valid. 
            if self.room.is_position_in_room(new_position):
                self.set_robot_position(new_position)
                self.room.clean_tile_at_position(self.position, self.capacity)
            # Otherwise changes direction.
            else:
                self.set_robot_direction(random.uniform(0,360))
#test_robot_movement(CheapRobot, SimpleRoom)


# === Problem 4
class SuperbRobot(Robot):
    """
    A SuperbRobot is a robot that moves extra fast and can clean two tiles in one
    timestep.

    It moves in its current direction, cleans the tile it lands on, and continues
    moving in that direction and cleans the second tile it lands on, all in one
    unit of time.

    If the SuperbRobot hits a wall when it attempts to move in its current direction,
    it may dirty the current tile by one unit because it moves very fast and can
    knock dust off of the wall.

    """
    p = 0.1337

    @staticmethod
    def set_dirty_probability(prob):
        """
        Sets the probability of getting the tile dirty equal to PROB.

        prob: a float (0 <= prob <= 1)
        """
        SuperbRobot.p = prob

    def dirties_tile(self):
        """
        Answers the question: Does this SuperbRobot dirty the tile if it hits the wall at full speed?
        A SuperbRobot dirties a tile with probability p.

        returns: True if the SuperbRobot dirties the tile, False otherwise.
        """
        return random.random() < SuperbRobot.p

    def update_position_and_clean(self):
        """
        Simulates the passage of a single time-step.

        Within one time step (i.e. one call to update_position_and_clean), there are
        three possible cases:

        1. The next position in the current direction at the robot's given speed is
           not a valid position in the room, so the robot stays at its current position
           without cleaning the tile. The robot then turns to a random direction.

        2. The robot successfully moves forward one position in the current direction
           at its given speed. Let's call this Position A. The robot cleans Position A.
           The next position in the current direction is not a valid position in the
           room, so it does not move to the new location. With probability p, it dirties
           Position A by 1. Regardless of whether or not the robot dirties Position A,
           the robot will turn to a random direction.

        3. The robot successfully moves forward two positions in the current direction
           at its given speed. It cleans each position that it lands on.
        """

        # Possibility 1:
        new_position = self.position.get_new_position(self.direction, self.speed)
        if not self.room.is_position_in_room(new_position):
            self.set_robot_direction(random.uniform(0,360))
        # The 1st new position is in the room. Arrive at and clean this position.
        else:  
            self.set_robot_position(new_position)
            self.room.clean_tile_at_position(self.position, self.capacity)
            # Generate 2nd new position in same direction as before.
            new_position = self.position.get_new_position(self.direction, self.speed) 
            # Check if 2nd new position is valid. 
            # If valid:
            if self.room.is_position_in_room(new_position):
                # The 2nd new position is in the room. Arrive at and clean this position.
                self.set_robot_position(new_position)
                self.room.clean_tile_at_position(self.position, self.capacity)
            # If not valid:
            else:
                # Dirties Position A with probability p
                if self.dirties_tile():
                    # Dirties tile
                    self.room.clean_tile_at_position(self.get_robot_position(), -1)
                # Changes direction regardless. 
                self.set_robot_direction(random.uniform(0,360))
    


#test_robot_movement(SuperbRobot, SimpleRoom)

# === Problem 5
def run_simulation(num_robots, speed, capacity, width, height, dirt_amount, min_coverage, num_trials,
                  robot_type):
    """
    Runs num_trials trials of the simulation and returns the mean number of
    time-steps needed to clean the fraction min_coverage of the room.

    The simulation is run with num_robots robots of type robot_type, each
    with the input speed and capacity in a room of dimensions width x height
    with the dirt dirt_amount on each tile. Each trial is run in its own SimpleRoom
    with its own robots.

    num_robots: an int (num_robots > 0)
    speed: a float (speed > 0)
    capacity: an int (capacity >0)
    width: an int (width > 0)
    height: an int (height > 0)
    dirt_amount: an int
    min_coverage: a float (0 <= min_coverage <= 1.0)
    num_trials: an int (num_trials > 0)
    robot_type: class of robot to be instantiated (e.g. StandardRobot or
                CheapRobot)
    """

    # Set steps to zero initially. 
    steps = 0 
    # Go through all the trials.
    for i in range(num_trials):
        # Initialize room object
        room = SimpleRoom (width, height, dirt_amount)
        # Initializes robot object
        robot = robot_type(room, speed, capacity)
        coverage = 0
        # Check if minimum coverage has been achieved.       
        while coverage < min_coverage:
            steps +=1
            # Update and clean for each robot
            for i in range(num_robots):
                robot.update_position_and_clean()
            # Update coverage.
            coverage = float(room.get_num_cleaned_tiles()/room.get_num_tiles())
    return steps/num_trials
       

            


print ('avg time steps: ' + str(run_simulation(1, 1.0, 1, 5, 5, 3, 1.0, 50, StandardRobot)))
print ('avg time steps: ' + str(run_simulation(1, 1.0, 1, 10, 10, 3, 0.8, 50, StandardRobot)))
print ('avg time steps: ' + str(run_simulation(1, 1.0, 1, 10, 10, 3, 0.9, 50, StandardRobot)))
print ('avg time steps: ' + str(run_simulation(1, 1.0, 1, 20, 20, 3, 0.5, 50, StandardRobot)))
print ('avg time steps: ' + str(run_simulation(3, 1.0, 1, 20, 20, 3, 0.5, 50, StandardRobot)))

def show_plot_compare_strategies(title, x_label, y_label):
    """
    Produces a plot comparing the three robot strategies in a 20x20 room with 80%
    minimum coverage.
    """
    num_robot_range = range(1, 11)
    times1 = []
    times2 = []
    times3 = []
    for num_robots in num_robot_range:
        print ("Plotting", num_robots, "robots...")
        times1.append(run_simulation(num_robots, 1.0, 1, 20, 20, 3, 0.8, 20, StandardRobot))
        times2.append(run_simulation(num_robots, 1.0, 1, 20, 20, 3, 0.8, 20, CheapRobot))
        times3.append(run_simulation(num_robots, 1.0, 1, 20, 20, 3, 0.8, 20, SuperbRobot))
    pylab.plot(num_robot_range, times1)
    pylab.plot(num_robot_range, times2)
    pylab.plot(num_robot_range, times3)
    pylab.title(title)
    pylab.legend(('StandardRobot', 'CheapRobot', 'SuperbRobot'))
    pylab.xlabel(x_label)
    pylab.ylabel(y_label)
    pylab.show()

def show_plot_room_shape(title, x_label, y_label):
    """
    Produces a plot showing dependence of cleaning time on room shape.
    """
    aspect_ratios = []
    times1 = []
    times2 = []
    times3 = []
    for width in [10, 20, 25, 50]:
        height = int(300/width)
        print ("Plotting cleaning time for a room of width:", width, "by height:", height)
        aspect_ratios.append(float(width) / height)
        times1.append(run_simulation(2, 1.0, 1, width, height, 3, 0.8, 200, StandardRobot))
        times2.append(run_simulation(2, 1.0, 1, width, height, 3, 0.8, 200, CheapRobot))
        times3.append(run_simulation(2, 1.0, 1, width, height, 3, 0.8, 200, SuperbRobot))
    pylab.plot(aspect_ratios, times1, 'o-')
    pylab.plot(aspect_ratios, times2, 'o-')
    pylab.plot(aspect_ratios, times3, 'o-')
    pylab.title(title)
    pylab.legend(('StandardRobot', 'CheapRobot', 'SuperbRobot'), fancybox=True, framealpha=0.5)
    pylab.xlabel(x_label)
    pylab.ylabel(y_label)
    pylab.show()


show_plot_compare_strategies('Time to clean 80% of a 20x20 room, for various numbers of robots','Number of robots','Time (steps)')
show_plot_room_shape('Time to clean 80% of a 300-tile room for various room shapes','Aspect Ratio', 'Time (steps)')