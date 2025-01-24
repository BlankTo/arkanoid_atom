
from core.property import Pos_x, Pos_y, Shape_x, Shape_y

def check_general_contact(hitbox_A, hitbox_B):

    ax, ay, aw, ah = hitbox_A
    bx, by, bw, bh = hitbox_B

    ax -= 1
    ay -= 1
    aw += 2
    ah += 2

    x_overlap = (bx <= ax + aw) and (ax <= bx + bw)
    y_overlap = (by <= ay + ah) and (ay <= by + bh)

    return x_overlap and y_overlap

def check_contact_left(frame_id, obj, other):

    if frame_id- 1 in obj.frames_id:
        previous_obj_patch = obj.patches[frame_id - 1]
    else:
        previous_obj_patch = None

    if frame_id in obj.frames_id:
        current_obj_patch = obj.patches[frame_id]
    else:
        current_obj_patch = None

    if frame_id- 1 in other.frames_id:
        previous_other_patch = other.patches[frame_id - 1]
    else:
        previous_other_patch = None

    if frame_id in other.frames_id:
        current_other_patch = other.patches[frame_id]
    else:
        current_other_patch = None

    if current_obj_patch:
        current_obj_hitbox = (current_obj_patch.properties[Pos_x], current_obj_patch.properties[Pos_y], current_obj_patch.properties[Shape_x], current_obj_patch.properties[Shape_y])
    elif previous_obj_patch:
        current_obj_hitbox = (current_obj_patch.properties[Pos_x], current_obj_patch.properties[Pos_y], current_obj_patch.properties[Shape_x], current_obj_patch.properties[Shape_y])
    else: return False

    if current_other_patch:
        current_other_hitbox = (current_other_patch.properties[Pos_x], current_other_patch.properties[Pos_y], current_other_patch.properties[Shape_x], current_other_patch.properties[Shape_y])
    elif previous_other_patch:
        current_other_hitbox = (current_other_patch.properties[Pos_x], current_other_patch.properties[Pos_y], current_other_patch.properties[Shape_x], current_other_patch.properties[Shape_y])
    else: return False

    if check_general_contact(current_obj_hitbox, current_other_hitbox):
        print('contact')

    # check direction left with speeds after computing them

    exit()

# Example Usage
hitbox_A = (0, 0, 1, 1)  # Cube A occupies cell (0, 0)
hitbox_B = (1, 1, 1, 1)  # Cube B occupies cell (1, 1)

class Patch:
    def __init__(self, pos_x, pos_y, shape_x, shape_y):
        self.properties = {
            Pos_x: pos_x,
            Pos_y: pos_y,
            Shape_x: shape_x,
            Shape_y: shape_y,
        }

class Object:
    def __init__(self, previous_patch, current_patch):
        self.patches = [previous_patch, current_patch]
        self.frames_id = [0, 1]

prev_obj_patch = Patch(0, 0, 1, 1)
curr_obj_patch = Patch(1, 1, 1, 1)
obj = Object(prev_obj_patch, curr_obj_patch)

prev_other_patch = Patch(1, 3, 1, 1)
curr_other_patch = Patch(1, 3, 1, 1)
other = Object(prev_other_patch, curr_other_patch)

print("contact left?", check_contact_left(1, obj, other))





#####


