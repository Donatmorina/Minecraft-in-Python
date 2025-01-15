from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise
import random, math

#Initialize Perlin noise
noise = PerlinNoise(octaves=3, seed=random.randint(1, 1000))

#Create an instance of the Ursina app
app = Ursina()

#Define the constants
MIN_HEIGHT = -5
BLOCK_KEYS = ["grass", "dirt", "stone", "bedrock"]

#Define the game variables
selected_block_index = 0

#Create player, position and mouse sensitivity
player = FirstPersonController(
    mouse_sensitivity=Vec2(100, 100),
    position=(0, 5, 0),
)

#Load custom textures, the textures need to be converted to .obj file to look better 
textures = {
    "stone": load_texture("wallStone.png"),
    "bedrock": load_texture("stone07.png"),
    "dirt": load_texture("groundMud.png"),
    "grass": load_texture("groundEarth.png"),
}

#Define block types with textures
block_properties = {
    block: {"texture": textures[block], "color": color.white} for block in BLOCK_KEYS
}

#Create the hand entity for block interactions
class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model="cube",
            texture="white_cube",
            scale=0.2,
            rotation=Vec3(150, -10, 0),
            position=Vec2(0.4, -0.6),
        )

    def active(self, action="place"):
        if action == "place":
            self.animate("rotation", Vec3(170, -10, 0), duration=0.2, curve=curve.in_out_sine)
            self.animate("rotation", Vec3(150, -10, 0), duration=0.2, curve=curve.in_out_sine, delay=0.2)
        elif action == "break":
            self.animate("rotation", Vec3(130, -10, 0), duration=0.2, curve=curve.in_out_sine)
            self.animate("rotation", Vec3(150, -10, 0), duration=0.2, curve=curve.in_out_sine, delay=0.2)

hand = Hand()

#Define Block class
class Block(Entity):
    def __init__(self, position, block_type):
        super().__init__(
            position=position,
            model="cube",
            scale=1,
            origin_y=-0.5,
            texture=block_properties[block_type]["texture"],
            collider="box",
        )
        self.block_type = block_type

#Add mini block preview
mini_block = Entity(
    parent=camera,
    model="cube",
    scale=0.2,
    texture="white_cube",
    position=(0.35, -0.25, 0.5),
    rotation=(-15, -30, -5),
)

#Create the ground (10 by 10 size)
for x in range(-10, 10):
    for z in range(-10, 10):
        height = math.floor(noise([x * 0.02, z * 0.02]) * 7.5)
        for y in range(height, MIN_HEIGHT - 1, -1):
            block_type = (
                "bedrock" if y == MIN_HEIGHT else
                "grass" if y == height else
                "stone" if height - y > 2 else
                "dirt"
            )
            Block((x, y + MIN_HEIGHT, z), block_type)

#Create block selection bar, press 1 for grass, 2 for dirt, 3 for stone, and 4 for bedrock!
selection_bar = [
    Entity(
        parent=camera.ui,
        model="cube",
        texture=block_properties[block]["texture"],
        color=block_properties[block]["color"],
        scale=(0.1, 0.1, 0.1),
        position=(-0.4 + i * 0.12, -0.45, 0),
    )
    for i, block in enumerate(BLOCK_KEYS)
]

#Highlight around the selected block
selection_highlight = Entity(
    parent=camera.ui,
    model="quad",
    color=color.azure,
    scale=(0.12, 0.12),
    position=selection_bar[selected_block_index].position,
    origin=(0, 0),
)

#Update selection highlight
def update_selection_highlight():
    selection_highlight.position = selection_bar[selected_block_index].position

#Handle input events
def input(key):
    global selected_block_index

    #Place block
    if key == "right mouse down":
        hit_info = raycast(camera.world_position, camera.forward, distance=10)
        if hit_info.hit:
            Block(hit_info.entity.position + hit_info.normal, BLOCK_KEYS[selected_block_index])
            hand.active(action="place")

    #Delete block
    if key == "left mouse down" and mouse.hovered_entity:
        if mouse.hovered_entity.block_type != "bedrock":
            destroy(mouse.hovered_entity)
            hand.active(action="break")

    #Change block type
    if key in ["1", "2", "3", "4"]:
        selected_block_index = int(key) - 1
        update_selection_highlight()

#Update mini block preview
def update():
    mini_block.texture = block_properties[BLOCK_KEYS[selected_block_index]]["texture"]

#Run the app, press SHIFT + Q to close the game
app.run()
