from math import ceil
from math import acos
import random
# NO OTHER IMPORTS ALLOWED!

class Constants:
    """
    A collection of game-specific constants.

    """
    # width and height of keepers
    KEEPER_WIDTH = 30
    KEEPER_HEIGHT = 30

    # width and height of animals
    ANIMAL_WIDTH = 30
    ANIMAL_HEIGHT = 30

    # width and height of food
    FOOD_WIDTH = 10
    FOOD_HEIGHT = 10

    # width and height of rocks
    ROCK_WIDTH = 50
    ROCK_HEIGHT = 50

    # thickness of the path
    PATH_THICKNESS = 30

    CRAZY_NAP_LENGTH = 125

    CRAZY_ENDURANCE = 6

    TRAINEE_THRESHOLD = 3

    TEXTURES = {
        'rock': '1f5ff',
        'animal': '1f418',
        'SpeedyZookeeper': '1f472',
        'ThriftyZookeeper': '1f46e',
        'CheeryZookeeper': '1f477',
        'food': '1f34e',
        'Demon': '1f479',
        'VHS': '1f4fc',
        'TraineeZookeeper': '1f476',
        'CrazyZookeeper': '1f61c',
        'SuperZookeeper': '1f40e',
        'SleepingZookeeper': '1f634',
        'FreezeDemon': '1f63b'
    }

    FORMATION_INFO = {'SpeedyZookeeper':
                       {'price': 9,
                        'interval': 55,
                        'throw_speed_mag': 20},
                      'ThriftyZookeeper':
                       {'price': 7,
                        'interval': 45,
                        'throw_speed_mag': 7},
                      'CheeryZookeeper':
                       {'price': 10,
                        'interval': 35,
                        'throw_speed_mag': 2}, 
                        'SuperZookeeper':
                       {'price': 8,
                        'interval': 5,
                        'throw_speed_mag': 20},
                      'TraineeZookeeper':
                       {'price': 4,
                        'interval': 65,
                        'throw_speed_mag': 1},
                      'CrazyZookeeper':
                        {'price': 11,
                         'interval': 10,
                         'throw_speed_mag': 13},

                      'Demon': 
                       {'width': 50,
                        'height': 50,
                        'radius': 75,
                        'multiplier': 2,
                        'price': 8},
                        'FreezeDemon':
                          {'width': 50,
                        'height': 50,
                        'radius': 75,
                        'multiplier': 0,
                        'price': 5},
                      'VHS':
                       {'width': 30,
                        'height': 30,
                        'radius': 75, 
                        'multiplier': 0.5,
                        'price': 5}}
class NotEnoughMoneyError(Exception):
    """A custom exception to be used when insufficient funds are available
    to hire new zookeepers."""
    pass

# New spec for timestep(self, mouse):
# 
# (0. Do not take any action if the player is already defeated.)
#  1. Compute the new speed of animals based on the presence of nearby VHS cassettes or demons.
#  2. Compute any changes in formation locations and remove any off-board formations.
#  3. Handle any food-animal collisions, and remove the fed animals and the eaten food.
#  4. Upgrade trainee zookeeper if needed.
#  5. Throw new food if possible.
#  6. Spawn a new animal from the path's start if needed.
#  7. Handle mouse input, which is the integer tuple coordinate of a player's click, the string 
#     label of a particular particular zookeeper type, `'Demon'`, `'VHS'`, or `None`.
#  8. Redeem one dollar per animal fed this timestep.
#  9. Check for the losing condition.

################################################################################
################################################################################


class Game:
    def __init__(self, game_info):
        """Initializes the game.

        `game_info` is a dictionary formatted in the following manner:
          { 'width': The width of the game grid, in an integer (i.e. number of pixels).
            'height': The height of the game grid, in an integer (i.e. number of pixels).
            'rocks': The set of tuple rock coordinates.
            'path_corners': An ordered list of coordinate tuples. The first
                            coordinate is the starting point of the path, the
                            last point is the end point (both of which lie on
                            the edges of the gameboard), and the other points
                            are corner ("turning") points on the path.
            'money': The money balance with which the player begins.
            'spawn_interval': The interval (in timesteps) for spawning animals
                              to the game.
            'animal_speed': The magnitude of the speed at which the animals move
                            along the path, in units of grid distance traversed
                            per timestep.
            'num_allowed_unfed': The number of animals allowed to finish the
                                 path unfed before the player loses.
          }
        """
        self.width = game_info['width']
        self.height = game_info['height']
        self.rocks = game_info['rocks']
        self.path_corners = game_info['path_corners']
        self.money = game_info['money']
        self.spawn_interval = game_info['spawn_interval']
        self.animal_speed = game_info['animal_speed']
        self.num_allowed_unfed = game_info['num_allowed_unfed']
        self.pathcoordlist = othergenpath(self.path_corners)
        self.animal_texture = Constants.TEXTURES['animal']
        self.animal_size = (Constants.ANIMAL_WIDTH, Constants.ANIMAL_HEIGHT)
        # Initialize each type of formation as a set
        self.animal_set = set()
        self.rock_set = set()
        self.food_set = set()
        self.demon_set = set()
        self.VHS_set = set()
        self.pathcorner_objects = set()
        self.formation_type = "~"
        self.demon_width = Constants.FORMATION_INFO["Demon"]["width"]
        self.demon_height = Constants.FORMATION_INFO["Demon"]["height"]
        self.demon_texture = Constants.TEXTURES['Demon']
        self.VHS_width = Constants.FORMATION_INFO["VHS"]["width"]
        self.VHS_height = Constants.FORMATION_INFO["VHS"]["height"]
        self.VHS_texture = Constants.TEXTURES['VHS']
        self.food_keeper = {}
        self.TRAINEE_THRESHOLD = Constants.TRAINEE_THRESHOLD
        self.formation_selected = None
        for i in range(len(self.path_corners) - 1):
            # if horizontal path segment
            if self.path_corners[i][1] == self.path_corners[i + 1][1]:
                centre = (self.path_corners[i][0] / 2 + self.path_corners[i + 1][0] / 2, self.path_corners[i][1])
                width = abs(self.path_corners[i + 1][0] - self.path_corners[i][0]) + Constants.PATH_THICKNESS
                height = Constants.PATH_THICKNESS
                path_rectangle = (centre, width, height)
            # if vertical path segment
            else:
                centre = (self.path_corners[i][0], self.path_corners[i][1] / 2 + self.path_corners[i + 1][1] / 2)
                height = abs(self.path_corners[i + 1][1] - self.path_corners[i][1]) + Constants.PATH_THICKNESS
                width = Constants.PATH_THICKNESS
                path_rectangle = (centre, width, height)
            self.pathcorner_objects.add(path_rectangle)
        self.zookeeper_set = set()
        self.zookeeper_size = (Constants.KEEPER_WIDTH, Constants.KEEPER_HEIGHT)
        for rock_loc_tuple in self.rocks:
            rock_loc = rock_loc_tuple
            rock_texture = Constants.TEXTURES['rock']
            rock_size = (Constants.ROCK_WIDTH, Constants.ROCK_HEIGHT)
            self.rock_set.add(Formation(rock_loc, rock_texture, rock_size))
        # Initialize game-clock as 0 and increase it by 1 at every timestep
        self.gameclock = 0
        self.status = "ongoing"
#        self.zookeeper_held = None
        self.zookeeper_location = None
        self.zookeeper_placed = None
        self.zookeeper_aimdir = None
        self.money_left = game_info['money']

    def render(self):
        """Renders the game in a form that can be parsed by the UI.

        Returns a dictionary of the following form:
          { 'formations': A list of dictionaries in any order, each one
                          representing a formation. The list should contain 
                          the formations of all animals, zookeepers, rocks, 
                          and food. Each dictionary has the key/value pairs:
                             'loc': (x, y), 
                             'texture': texture, 
                             'size': (width, height)
                          where `(x, y)` is the center coordinate of the 
                          formation, `texture` is its texture, and `width` 
                          and `height` are its dimensions. Zookeeper
                          formations have an additional key, 'aim_dir',
                          which is None if the keeper has not been aimed, or a 
                          tuple `(aim_x, aim_y)` representing a unit vector 
                          pointing in the aimed direction.
            'money': The amount of money the player has available.
            'status': The current state of the game which can be 'ongoing' or 'defeat'.
            'num_allowed_remaining': The number of animals which are still
                                     allowed to exit the board before the game
                                     status is `'defeat'`.
          }
        """
        dict_returned = {}
        self.formations = []
        # rocks is a set of tuple coordinates
#        for rock in self.rock_set:
#            rock_dict = rock.render_helper()
#            self.formations.append(rock_dict)
        dict_returned['formations'] = self.formations
        dict_returned['money'] = self.money_left
        dict_returned['status'] = self.status
        dict_returned['num_allowed_remaining'] = self.num_allowed_unfed
        for animal in self.animal_set:
            animal_dict = animal.render_helper()
            dict_returned['formations'].append(animal_dict)

        for rock in self.rock_set:
            rock_dict = rock.render_helper()
            dict_returned['formations'].append(rock_dict)
        for demon in self.demon_set:
            demon_dict = {}
            demon_dict['loc'] = demon.loc
            demon_dict['texture'] = demon.texture
            demon_dict['size'] = demon.size
            dict_returned['formations'].append(demon_dict)
        for VHS in self.VHS_set:
            VHS_dict = {}
            VHS_dict['loc'] = VHS.loc
            VHS_dict['texture'] = VHS.texture
            VHS_dict['size'] = VHS.size
            dict_returned['formations'].append(VHS_dict)
            
            
            
        for zookeeper in self.zookeeper_set:
            zookeeper_dict = {}
            zookeeper_dict['loc'] = zookeeper.get_location()
            zookeeper_dict['texture'] = zookeeper.texture
            zookeeper_dict['size'] = zookeeper.size
            zookeeper_dict['aim_dir'] = zookeeper.get_aim_dir()
            dict_returned['formations'].append(zookeeper_dict)
#            dict_returned['formations'].append({'loc':animal.loc, 'texture':animal.texture, 'size':animal.size})
        for food in self.food_set:
            food_dict = {}
            food_dict['loc'] = food.loc
            food_dict['texture'] = food.texture
            food_dict['size'] = food.size
            dict_returned['formations'].append(food_dict)
        
#        print ("self.food_set:", self.food_set)
        return dict_returned
    
    def location_in_grid(self, location):
        """
        This function will check if a given location is in the given game's board.
        """
        if 0 <= location[0] < self.width:
            if 0 <= location[1] < self.height:
                return True
        return False
     
    def formation_placeable(self, formation, location, width, height):
        """
        This function will check if the selected zookeeper can be placed at the given location.
        """
        overlapped = False
        tuple2 = (location, width, height)
        for rock in self.rock_set:
            tuple1 = (rock.loc, rock.size[0], rock.size[1])
            overlapped = overlap_checker(tuple1, tuple2)
            if overlapped == True:
                return False
        for path_rectangle in self.pathcorner_objects:
            tuple1 = path_rectangle
            overlapped = overlap_checker(tuple1, tuple2)
            if overlapped == True:
                return False
        
        for demon in self.demon_set:
            centre, width, height = demon.loc, width, height
            tuple1 = (centre, width, height)
            overlapped = overlap_checker(tuple1, tuple2)
            if overlapped == True:
                return False
        for VHS in self.VHS_set:
            centre, width, height = VHS.loc, width, height
            tuple1 = (centre, width, height)
            overlapped = overlap_checker(tuple1, tuple2)
            if overlapped == True:
                return False
        
        for keeper2 in self.zookeeper_set:
            centre, width, height = keeper2.get_location(), width, height
            tuple1 = (centre, width, height)
            overlapped = overlap_checker(tuple1, tuple2)
            if overlapped == True:
                return False
        
        return not overlapped
        
    def timestep(self, mouse=None):
        """Simulates the evolution of the game by one timestep.

        In this order:
            (0. Do not take any action if the player is already defeated.)
            1. Compute any changes in formation locations, then remove any
                off-board formations.
            2. Handle any food-animal collisions, and remove the fed animals
                and eaten food.
            3. Throw new food if possible.
            4. Spawn a new animal from the path's start if needed.
            5. Handle mouse input, which is the integer coordinate of a player's
               click, the string label of a particular zookeeper type, or `None`.
            6. Redeem one unit money per animal fed this timestep.
            7. Check for the losing condition to update the game status if needed.
         New spec for timestep(self, mouse):
         
         (0. Do not take any action if the player is already defeated.)
          1. Compute the new speed of animals based on the presence of nearby VHS cassettes or demons.
          2. Compute any changes in formation locations and remove any off-board formations.
          3. Handle any food-animal collisions, and remove the fed animals and the eaten food.
          4. Upgrade trainee zookeeper if needed.
          5. Throw new food if possible.
          6. Spawn a new animal from the path's start if needed.
          7. Handle mouse input, which is the integer tuple coordinate of a player's click, the string 
             label of a particular particular zookeeper type, `'Demon'`, `'VHS'`, or `None`.
          8. Redeem one dollar per animal fed this timestep.
          9. Check for the losing condition.
        
        """
        # Keep track of numbers of animals fed in this timestep
        animals_fed = 0
#        if mouse != None:
#            print ("Mouse click right now is", mouse)
#            print ("The formations right now are")
#            for formation in self.formations:
##                if formation['texture'] != '1f418':
#                print (formation)
#        
        
        # 0.
        if self.status == 'defeat':
            return
            # End Game
            
        # The animal speed should go back to normal if it is no longer in the radius 
        
        # 1. Compute the new speed of animals based on the presence of nearby VHS cassettes or demons.
        for animal in self.animal_set.copy():
            for demon in self.demon_set.copy():
                if distance(animal.loc, demon.loc) <= demon.range_radius:
                    animal.animal_speed *= demon.speed_multiplier
            for vhs_cassette in self.VHS_set.copy():
                if distance(animal.loc, vhs_cassette.loc) <= vhs_cassette.range_radius:
                    animal.animal_speed *= vhs_cassette.speed_multiplier
            
            
            
            
        # 2. Compute any changes in formation locations and remove any off-board formations.
        for animal in self.animal_set.copy():
            animal.new_update_location()
            if animal.loc == (float('inf'), float('inf')):
                self.animal_set.remove(animal)
                self.num_allowed_unfed -=1
        # Compute change in food locations
        for food_item in self.food_set.copy():
            food_item.food_update_location()
            if not self.location_in_grid(food_item.loc):
                self.food_set.remove(food_item)
        
        
        # 3. Handle any food-animal collisions, and remove the fed animals and eaten food.
        foods_to_remove = set()
        animals_to_remove = set()
        for food in self.food_set.copy():
            food_tuple = (food.loc, food.size[0], food.size[0])
            for animal in self.animal_set.copy():
                animal_tuple = (animal.loc, animal.size[0], animal.size[0])
                # Check if any collisions
                if overlap_checker(food_tuple, animal_tuple):
                    foods_to_remove.add(food)
                    animals_to_remove.add(animal)
                    animals_fed += 1
                    # Add one to the food score of the zookeeper that threw the food if it was a TraineeZookeeper
#                    keeper = self.food_keeper[food]
#                    if isinstance(keeper, TraineeZookeeper):
#                        keeper.food_score += 1
        animals_fed = len(animals_to_remove)
        for food in foods_to_remove:
            self.food_set.remove(food)
            keeper = self.food_keeper[food]
            if isinstance(keeper, TraineeZookeeper):
                keeper.food_score += 1
        for animal in animals_to_remove:
            self.animal_set.remove(animal)
        # 4. Upgrade trainee zookeeper if needed.
        for zookeeper in self.zookeeper_set:
            if zookeeper.throw_interval == Constants.FORMATION_INFO['TraineeZookeeper']['interval']:
                if zookeeper.food_score >= self.TRAINEE_THRESHOLD:
                    zookeeper.upgrade(self.gameclock)
        # 5. Throw new food if possible.
        
        # You iterate over the zookeepers
        for zookeeper in self.zookeeper_set:
            if zookeeper.aim_dir != None and not isinstance(zookeeper, CrazyZookeeper):
            # Check if the zookeeper should be throwing at this timestep
                if (self.gameclock - zookeeper.timewhenplaced) % zookeeper.throw_interval == 0:
                    for animal in self.animal_set:
                        # Check if any animal in line of sight
                        if los_intersects(animal.loc, animal.size[0], zookeeper.loc, zookeeper.aim_dir):
                            # Throw food
                            texture = Constants.TEXTURES["food"]
                            size = (Constants.FOOD_WIDTH, Constants.FOOD_WIDTH)
#                            print ("Added Food")
                            food_item = Food(zookeeper.loc, texture, size, zookeeper.throw_speed, zookeeper.aim_dir)
                            self.food_set.add(food_item)
                            # Use dictionary mapping each food item thrown to the zookeeper that threw it
                            self.food_keeper[food_item] = zookeeper
                            break
                        pass
            elif zookeeper.aim_dir != None and isinstance(zookeeper, CrazyZookeeper):
                if not zookeeper.asleep:
                    # If it's awake, you want to throw food the same way as usual but also increase its throw count
                    if (self.gameclock - zookeeper.timewhenplaced) % zookeeper.throw_interval == 0:
                        for animal in self.animal_set:
                            # Check if any animal in line of sight
                            if los_intersects(animal.loc, animal.size[0], zookeeper.loc, zookeeper.aim_dir):
                                # Throw food
                                texture = Constants.TEXTURES["food"]
                                size = (Constants.FOOD_WIDTH, Constants.FOOD_WIDTH)
    #                            print ("Added Food")
                                food_item = Food(zookeeper.loc, texture, size, zookeeper.throw_speed, zookeeper.aim_dir)
                                self.food_set.add(food_item)
                                # Use dictionary mapping each food item thrown to the zookeeper that threw it
                                self.food_keeper[food_item] = zookeeper
                                zookeeper.throw_count += 1
                                if zookeeper.throw_count%Constants.CRAZY_ENDURANCE == 0:
                                    zookeeper.fall_asleep()
                                break
                            pass
                else:
                    # When the zookeeper is asleep, you want to increase the time since asleep by 1
                    zookeeper.timeasleep += 1
                    if zookeeper.timeasleep % Constants.CRAZY_NAP_LENGTH == 0:
                        zookeeper.wake_up()
            
                
        
        
        # 6. Spawn a new animal from the path's start if needed.. 
#        print (self.spawn_interval)
        if self.gameclock % self.spawn_interval == 0:
            
            # Spawn animal here
            added_animal = Animal(self.pathcoordlist[0], self.animal_texture, self.animal_size, self.animal_speed, self.pathcoordlist)
            
            self.animal_set.add(added_animal)
#            print (self.animal_set)

        # 7. Handle mouse input, which is the integer tuple coordinate of a player's click, the string 
        #    label of a particular particular zookeeper type, `'Demon'`, `'VHS'`, or `None`.
        

        
        if mouse != None:
            # If the mouse click is a string, it's referring to a zookeeper
            if type(mouse) == str:
                
                if mouse == "Demon":
                    demon_width = Constants.FORMATION_INFO["Demon"]["width"]
                    demon_height = Constants.FORMATION_INFO["Demon"]["height"]
                    demon_texture = Constants.TEXTURES['Demon']
                    self.formation_selected = Demon(demon_texture, (demon_width, demon_height))
                    self.formation_type = "Demon"
                elif mouse == "VHS":
                    VHS_width = Constants.FORMATION_INFO["VHS"]["width"]
                    VHS_height = Constants.FORMATION_INFO["VHS"]["height"]
                    VHS_texture = Constants.TEXTURES['VHS']
                    self.formation_selected = VHS(VHS_texture, (VHS_width, VHS_height))
                    self.formation_type = "VHS"
                else:
                    size = self.zookeeper_size
                    self.formation_type = "Zookeeper"
                if mouse == 'SpeedyZookeeper':
                    texture = Constants.TEXTURES['SpeedyZookeeper']
                    self.formation_selected = SpeedyZookeeper(texture, size)
                elif mouse == 'ThriftyZookeeper':
                    texture = Constants.TEXTURES['ThriftyZookeeper']
                    self.formation_selected = ThriftyZookeeper(texture, size)
                elif mouse == 'CheeryZookeeper':
                    texture = Constants.TEXTURES['CheeryZookeeper']
                    self.formation_selected = CheeryZookeeper(texture, size)
                elif mouse == 'TraineeZookeeper':
                    texture = Constants.TEXTURES['TraineeZookeeper']
                    self.formation_selected = TraineeZookeeper(texture, size)
                elif mouse == 'CrazyZookeeper':
                    texture = Constants.TEXTURES['CrazyZookeeper']
                    self.formation_selected = CrazyZookeeper(texture, size)
                elif mouse == 'SuperZookeeper':
                    texture = Constants.TEXTURES['SuperZookeeper']
                    self.formation_selected = SuperZookeeper(texture, size)
                # Check if enough money
                
            # If the mouse click is not none and it's not a string, it must be a location tuple.
            # This will refer to the zookeeper's location if a zookeeper is selected but not placed yet.
            # It will refer to the aim direction if a zookeeper has just been placed.
            elif type(mouse) == tuple:
                if self.formation_selected == None:
                    pass
                elif self.formation_selected.price > self.money_left:
                    raise NotEnoughMoneyError
                    
                elif self.formation_type == "Demon":
                    if self.formation_placeable(self.formation_selected, mouse, self.demon_width, self.demon_height):
#                        print ("Placing demon at", mouse)
                        self.formation_selected.set_location(mouse)
                        self.money_left -= self.formation_selected.price
                        self.demon_set.add(self.formation_selected)
                        self.formation_selected = None
                        
#                    else:
#                        print ("Demon not placeable at", self.formation_selected.loc)
                    
                elif self.formation_type == "VHS":
                    if self.formation_placeable(self.formation_selected, mouse, self.VHS_width, self.VHS_height):
                        self.formation_selected.set_location(mouse)
                        self.money_left -= self.formation_selected.price
                        self.VHS_set.add(self.formation_selected)
                        self.formation_selected = None

                
                elif self.formation_type == "Zookeeper":  
                    if self.zookeeper_placed != True:
                        # This means this is where the player wants to place the zookeeper
                        if self.formation_placeable(self.formation_selected, mouse, Constants.KEEPER_WIDTH, Constants.KEEPER_HEIGHT):
                            self.formation_selected.set_location(mouse)
                            self.zookeeper_location = mouse
                            self.zookeeper_placed = True
                            self.money_left -= self.formation_selected.price
                            self.zookeeper_set.add(self.formation_selected)
                            self.formation_selected.set_timewhenplaced(self.gameclock + 1) 
                            
                    else:
                        # This means this is the direction the player wants the zookeeper to aim
                        if self.zookeeper_location != mouse:
                            aim_dir = unit_vectorify(self.zookeeper_location, mouse)
                            self.formation_selected.set_aim_dir(aim_dir)
                            self.zookeeper_placed = False
                            self.formation_selected = None
            
        # 8. Redeem one dollar per animal fed this timestep. 
        self.money_left += animals_fed
        
        # 9. 
        if self.num_allowed_unfed < 0:
            self.status = 'defeat'
            
        self.gameclock += 1
################################################################################
################################################################################
# TODO: Add a Formation class and at least two additional classes here.
def unit_vectorify(loc1, loc2):
    """
    If the zookeeper is placed at location 1 and then the player clicks location 2,
    this will return the unit vector in the direction loc1 to loc2
    """
    dir_vector = (loc2[0] - loc1[0], loc2[1] - loc1[1])
    magnitude = (dir_vector[0]**2 + dir_vector[1]**2)**0.5
    unit_vec = (dir_vector[0] / magnitude, dir_vector[1] / magnitude)
    return unit_vec
    

def overlap_checker(tuple1, tuple2):
    """
    This function will take in two tuples representing rectangles both of the form
    (centre, width, height) and check if they overlap
    """
    centre1, width1, height1 = tuple1[0], tuple1[1], tuple1[2]
    centre2, width2, height2 = tuple2[0], tuple2[1], tuple2[2]
    # The corners will be in the order top-left, bottom-left, top-right and bottom-right
    rectangle1 = [(centre1[0] + i*width1/2, centre1[1] + j*height1/2) for i in [-1,1] for j in [-1,1]]
    rectangle2 = [(centre2[0] + i*width2/2, centre2[1] + j*height2/2) for i in [-1,1] for j in [-1,1]]
    return overlap_helper(rectangle1, rectangle2)
    

def overlap_helper(rectangle1, rectangle2):
    l1, r1 = rectangle1[0], rectangle1[3]
    l2, r2 = rectangle2[0], rectangle2[3]
    
    if(l1[0] >= r2[0] or l2[0] >= r1[0]): 
        return False
    
    if(l1[1] >= r2[1] or l2[1] >= r1[1]): 
        return False
  
    return True



def distance(loc1, loc2):
    """
    This function will calculate the distance between two locations (w1, h1) and (w2, h2)
    """
    w1, h1, w2, h2 = loc1[0], loc1[1], loc2[0], loc2[1]
    dist = ((w2 - w1)**2 + (h2 - h1)**2)**(1/2)
    return dist
def path_direct(pc1, pc2):
    """
    This function will get you the direction of the path between two path corners
    """
    if pc1[0] == pc2[0]:
        if pc1[1] < pc2[1]:
            return "down"
        else:
            return "up"
    if pc1[1] == pc2[1]:
        if pc1[0] < pc2[0]:
            return "right"
        else:
            return "left"
class Formation:
    def __init__(self, loc, texture, size):
        self.loc = loc
        self.texture = texture
        self.size = size
    # Add method
    def render_helper(self):
        render_dict = {}
        render_dict['loc'] = self.loc
        render_dict['texture'] = self.texture
        render_dict['size'] = self.size
        return render_dict
#    def food_location_updater()
class Zookeeper(Formation):
    def __init__(self, texture, size):
        self.texture = texture
        self.size = size
        self.aim_dir = None
    def set_aim_dir(self, aim_dir):
        self.aim_dir = aim_dir
    def get_aim_dir(self):
        return self.aim_dir
    def set_location(self, loc):
        self.loc = loc
    def get_location(self):
        return self.loc
    def get_size(self, size):
        return self.size
    def set_timewhenplaced(self, time):
        self.timewhenplaced = time
# if the timestep immediately after that on which a zookeeper is placed has count X and the keeper's throw interval 
# is I, then that zookeeper can only throw food on timesteps X, X+I, X+2*I 
        
# One way we can do this is record for each zookeeper the timestep immediately after it was placed and
# store that as timewhenplaced attribute for the specific zookeeper object. 
class SpeedyZookeeper(Zookeeper):
    def __init__(self, texture, size):
#        self.loc = loc
        self.texture = texture
        self.size = size
        self.price = 9
        self.throw_interval = 55
        self.throw_speed = 20
        self.aim_dir = None
class ThriftyZookeeper(Zookeeper):
    def __init__(self, texture, size):
#        self.loc = loc
        self.texture = texture
        self.size = size
        self.price = 7
        self.throw_interval = 45
        self.throw_speed = 7
        self.aim_dir = None
class CheeryZookeeper(Zookeeper):
    def __init__(self, texture, size):
#        self.loc = loc
        self.texture = texture
        self.size = size
        self.price = 10
        self.throw_interval = 35
        self.throw_speed = 2
        self.aim_dir = None
class TraineeZookeeper(Zookeeper):
    def __init__(self, texture, size):
        self.texture = texture
        self.size = size
        self.price = 4
        self.throw_interval = 65
        self.throw_speed = 1
        self.aim_dir = None
        self.food_score = 0
    def upgrade(self, game_clock):
        self.price = 9
        self.throw_speed = Constants.FORMATION_INFO["SpeedyZookeeper"]["throw_speed_mag"]
        self.throw_interval = Constants.FORMATION_INFO["SpeedyZookeeper"]['interval']
        self.texture = Constants.TEXTURES["SpeedyZookeeper"]
        self.set_timewhenplaced(game_clock)
class CrazyZookeeper(Zookeeper):
    def __init__(self, texture, size):
        self.texture = Constants.TEXTURES["CrazyZookeeper"]
        self.size = size
        self.price = 11
        self.throw_interval = 10
        self.throw_speed = 13
        self.aim_dir = None
        self.asleep = False
        self.CRAZY_ENDURANCE = Constants.CRAZY_ENDURANCE
        self.CRAZY_NAP_LENGTH = Constants.CRAZY_NAP_LENGTH
        self.throw_count = 0
        self.timesinceplaced = 0
        self.timeasleep = 0
    def fall_asleep(self):
         
        self.asleep = True
        self.texture = Constants.TEXTURES["SleepingZookeeper"] 
    def wake_up(self):
        
        self.asleep = False
        self.texture = Constants.TEXTURES["CrazyZookeeper"] 

class SuperZookeeper(Zookeeper):
    def __init__(self, texture, size):
#        self.loc = loc
        self.texture = texture
        self.size = size
        self.price = 8
        self.throw_speed = random.randint(10,20)
        self.throw_interval = random.randint(5,10)
#        self.throw_speed = Constants.FORMATION_INFO["SuperZookeeper"]["throw_speed_mag"]
#        self.throw_interval = Constants.FORMATION_INFO["SuperZookeeper"]['interval']
        self.aim_dir = None        
        
class Animal(Formation):
    def __init__(self, loc, texture, size, animal_speed, pathcoordlist):
        self.loc = loc
        self.texture = texture
        self.size = size
        self.original_speed = animal_speed * 1
        self.animal_speed = animal_speed
#        self.path_corners = path_corners
        self.pathcoordlist = pathcoordlist
        self.locindex = 0
        
    def new_update_location(self):
        self.locindex += ceil(self.animal_speed)
#        currentlocindex = self.pathcoordlist.index(self.loc)
#        newlocindex = currentlocindex + self.animal_speed
        if self.locindex < len(self.pathcoordlist):
            new_loc = self.pathcoordlist[self.locindex]
        else:
            new_loc = (float('inf'), float('inf'))
        self.loc = new_loc
        self.animal_speed = self.original_speed

class Food(Formation):
    def __init__(self, loc, texture, size, food_speed, food_dir):
        self.loc = loc
        self.texture = texture
        self.size = size
        self.food_speed = food_speed
        self.food_dir = food_dir
    
    def food_update_location(self):
        # It's moving in food_dir with food_speed starting from loc
        change_in_loc = (self.food_dir[0] * self.food_speed, self.food_dir[1] * self.food_speed)
        new_loc = (self.loc[0] + change_in_loc[0], self.loc[1] + change_in_loc[1])
#        print (self.loc, new_loc)
#        if Game.location_in_grid(new_loc):
        self.loc = new_loc
        
class Demon(Formation):
    def __init__(self, texture, size):
#        self.loc = loc
        self.texture = texture
        self.size = size
        self.price = 8
        self.range_radius = Constants.FORMATION_INFO["Demon"]['radius']
        self.speed_multiplier = Constants.FORMATION_INFO["Demon"]['multiplier']
    def set_location(self, loc):
        self.loc = loc
class VHS(Formation):
    def __init__(self, texture, size):
#        self.loc = loc
        self.texture = texture
        self.size = size
        self.price = 5
        self.range_radius = Constants.FORMATION_INFO["VHS"]['radius']
        self.speed_multiplier = Constants.FORMATION_INFO["VHS"]['multiplier']
    def set_location(self, loc):
        self.loc = loc        
         






################################################################################
################################################################################
def othergenpath(path_corners):
    listed_path = []
    for i in range(len(path_corners) - 1):
        pc1 = path_corners[i]
        pc2 = path_corners[i + 1]
        path_direction = path_direct(pc1, pc2)
        if path_direction == "right":
            bw_list = [(pc1[0] + i, pc1[1]) for i in range(abs(pc1[0] - pc2[0]))]
        elif path_direction == "left":
            bw_list = [(pc1[0] - i, pc1[1]) for i in range(abs(pc1[0] - pc2[0]))]
        elif path_direction == "down":
            bw_list = [(pc1[0], pc1[1] + i) for i in range(abs(pc1[1] - pc2[1]))]
        elif path_direction == "up":
            bw_list = [(pc1[0], pc1[1] - i) for i in range(abs(pc1[1] - pc2[1]))]
        listed_path.extend(bw_list)
    listed_path.append(pc2)
    return listed_path


def angle_from_vectors(v1, v2):
    """
    This function will return the angle between two vectors
    """
    dot_prod = v1[0]*v2[0] + v1[1]*v2[1]
    mag_v1 = (v1[0]**2 + v1[1]**2)**0.5
    mag_v2 = (v2[0]**2 + v2[1]**2)**0.5
    
    
    return acos(dot_prod/(mag_v1 * mag_v2))

def corners_generator(tuple1):
    """
    This function will take in a tuple representing a rectangle of the form
    (centre, width, height) and return the corners in the order 
    top-left, bottom-left, top-right and bottom-right
    """
    centre1, width1, height1 = tuple1[0], tuple1[1], tuple1[2]
    rectangle1 = [(centre1[0] + i*width1/2, centre1[1] + j*height1/2) for i in [-1,1] for j in [-1,1]]
    return rectangle1

def los_intersects(animal_location, animal_thickness, zookeeper_location, zookeeper_aim_dir):
    """
    This function will check if an animal of a given thickness at a given location
    intersects the line of sight of the zookeeper
    """
    zx = zookeeper_location[0]
    zy = zookeeper_location[1]
    
    anim_rec = corners_generator((animal_location, animal_thickness, animal_thickness))
    # Line segment from top-left to bottom-left is 
    lstlbl = [anim_rec[0], anim_rec[1]]
    # Line segment from top-left to top-right is
    lstltr = [anim_rec[0], anim_rec[2]]
    # Line segment from bottom-right to bottom-left is 
    lsbrbl = [anim_rec[3], anim_rec[1]]
    # Line segment from bottom-right to top-right is
    lsbrtr = [anim_rec[3], anim_rec[2]]
    
    segments_list = [lstlbl, lstltr, lsbrbl, lsbrtr]
    
    for segment in segments_list:
        ve_1 = (segment[0][0] - zx, segment[0][1] - zy)
        ve_2 = (segment[1][0] - zx, segment[1][1] - zy)
        theta_ve1_ve2 = angle_from_vectors(ve_1, ve_2)
        theta_ve1_vray = angle_from_vectors(ve_1, zookeeper_aim_dir)
        theta_ve2_vray = angle_from_vectors(ve_2, zookeeper_aim_dir)
        if abs(theta_ve1_ve2 - (theta_ve1_vray + theta_ve2_vray)) < 0.001:
            return True
    
    
    return False
if __name__ == '__main__':
    path_corners = [(0,350), (200, 350), (200,150), (400, 150), (400,300),  (640, 300)]
    pathcoordlist = othergenpath(path_corners)
    my_animal = Animal((150, 350), '1f418', 30, 100, pathcoordlist)
    my_animal.animal_speed = 200
    my_animal.size = 30
    my_animal.texture = '1f418'
    my_animal.loc = (550, 300)
    my_animal.path_corners = [(0,350), (200, 350), (200,150), (400, 150), (400,300),  (640, 300)]
    pathcorners2 = [(0,0), (3,0), (3,5), (1,5), (1,4)]
    my_animal.new_update_location()
    loc1 = (1,3)
    loc2 = (4,4)