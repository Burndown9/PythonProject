"""
Project Name: Test Game
Project Author: Jacob Hayes
Project Date: 27 Dec 2024

Packages used: collections, os, pygame, random

Credit and sincere thanks to:
OpenGameArt.org
    Buch (opengameart.org/users/buch)
    Ravenmore (dycha.net, opengameart.org/users/ravenmore)

"""

"""IMPORTS"""
from collections import deque   #for handling cascading merges
import os                       #for pathing purposes
import pygame                   #for handling game functionality
import random                   #for that delicious RNG
""""""

"""SETUP"""
# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 640
GRID_SIZE = 5  # 5x5 grid
CELL_SIZE = 128  # Size of each cell

# Colors
BACKGROUND_COLOR = (50, 50, 50)
GRID_COLOR = (200, 200, 200)
ITEM_COLOR = (100, 150, 250)

# Set up screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Merge Game")

# Create grid positions
grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]


#preload all icons
preloaded_images = {
    "coin_level1" : "Resources/512/coin.png",
    "coin_level2" : "Resources/512/envelope.png",
    "coin_level3" : "Resources/512/tome.png",
}

#resize all preloaded icons
for key, filepath in preloaded_images.items():
    print(f"Processing {key}: {filepath}")
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
    else:
        try:
            # Load and scale the image
            image = pygame.image.load(filepath)
            scaled_image = pygame.transform.scale(image, (CELL_SIZE // 2, CELL_SIZE // 2))
            preloaded_images[key] = scaled_image  # Replace the path with the Surface object
        except pygame.error as e:
            print(f"Error loading image '{filepath}': {e}")

#verify that the dictionary was loaded successfully
for key, image in preloaded_images.items():
    if isinstance(image, pygame.Surface):
        print(f"{key} successfully loaded and transformed.")
    else:
        print(f"Failed to transform {key}.")
""""""


"""CLASSES"""
class Item:
    def __init__(self, name, traits, icons, level=1):
        self.name = name
        self.traits = traits  # List of traits, e.g., ["Armor", "Headgear", "Elemental"]
        self.icons = icons  # List of images for each level
        self.level = level  # Current level

    def can_merge_with(self, other):
        # Check if items are the same type and not at max level
        return (
            isinstance(other, Item) and
            self.name == other.name and
            self.level == other.level and
            self.level < len(self.icons)
        )

    def merge(self):
        # Upgrade the item to the next level
        if self.level < len(self.icons):
            self.level += 1

    def get_icon(self):
        # Return the icon corresponding to the current level
        #print(f"Returning {self.icons[self.level-1]}")
        return self.icons[self.level - 1]

# Example: Defining a specific item
class Coin(Item):
    def __init__(self, level=1):
        super().__init__(
            name="Coin",
            traits=["Currency"],
            icons=[preloaded_images["coin_level1"], preloaded_images["coin_level2"], preloaded_images["coin_level3"]],
            level=level
        )

""""""

#item registry with weights of 1 total
ITEM_CLASSES = {
    Coin: 1.0,
}


"""FUNCTIONS"""
# Helper function to draw the grid and items
def draw_grid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = col * CELL_SIZE + (SCREEN_WIDTH - GRID_SIZE * CELL_SIZE) // 2
            y = row * CELL_SIZE + (SCREEN_HEIGHT - GRID_SIZE * CELL_SIZE) // 2
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRID_COLOR, rect, 2)

            item = grid[row][col]
            if item:
                x = col * CELL_SIZE + (SCREEN_WIDTH - GRID_SIZE * CELL_SIZE) // 2 + CELL_SIZE // 4
                y = row * CELL_SIZE + (SCREEN_HEIGHT - GRID_SIZE * CELL_SIZE) // 2 + CELL_SIZE // 4
                icon = item.get_icon()
                if isinstance(icon, pygame.Surface):
                    # print(f"Blitting icon for {item.name} at level {item.level}")
                    screen.blit(icon, (x, y))  # blit the Surface object
                else:
                    print(f"Error: {item.name} at level {item.level} returned {icon}")



# Function to spawn items
def spawn_item():
    empty_cells = [(row, col) for row in range(GRID_SIZE) for col in range(GRID_SIZE) if grid[row][col] is None]
    if empty_cells:
        row, col = random.choice(empty_cells)
        #item_class = random.choices(list(ITEM_CLASSES.keys()), weights=ITEM_CLASSES.values())[0] #item types
        grid[row][col] = new_item = random.choice(list(ITEM_CLASSES.keys()))()
        new_item.row = row
        new_item.col = col
        play_spawn_animation(screen, new_item)

def get_neighbors(row, col):
    matches = []
    item = grid[row][col]
    for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        new_row, new_col = row + d_row, col + d_col
        if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
            neighbor = grid[new_row][new_col]
            if neighbor is not None and item.can_merge_with(neighbor):
                matches.append((new_row, new_col))

    return matches

def check_and_merge(row, col):
    # Initialize a queue for cascading merges
    merge_queue = deque([(row, col)])

    while merge_queue:
        current_row, current_col = merge_queue.popleft()
        item = grid[current_row][current_col]

        if item is None:
            continue #skip empty cells


        print(f"Checking for merge on {item.name} at ({row}, {col}).")

        neighbors = get_neighbors(row, col)
        print(f"Found {len(neighbors)} neighbors: {neighbors}")

        if len(neighbors) >= 2:
            play_merge_animation(screen, item, neighbors)
            print(f"Merging {item.name} at ({row}, {col}) with neighbors.")

            item.merge()
            print(f"{item.name} upgraded to level {item.level}.")

            play_spawn_animation(screen, item)

            #for each neighbor cell, clear and recheck
            for n_row, n_col in neighbors:
                print(f"Clearing neighbor at ({n_row}, {n_col}).")
                grid[n_row][n_col] = None

                # Add cleared cells to the queue for further checks (for respawning logic)
                merge_queue.append((n_row, n_col))

            # Recheck the current cell after upgrading
            merge_queue.append((current_row, current_col))

def play_merge_animation(screen, item, neighbors):
    animation_duration = 300  # in milliseconds
    frames = 30
    clock = pygame.time.Clock()

    # Calculate the animation steps
    shrink_factor = 0.8
    scale_steps = [(1 - shrink_factor) / frames * i + shrink_factor for i in range(frames)]

    # remove the item from the grid temporarily
    grid[item.row][item.col] = None

    for scale in scale_steps:
        screen.fill(BACKGROUND_COLOR)  # Redraw the screen to clear previous frame

        #redraw the grid
        draw_grid()

        # Draw the merging item with shrinking effect
        item_icon = pygame.transform.scale(item.get_icon(), (int(CELL_SIZE * scale), int(CELL_SIZE * scale)))
        item_rect = item_icon.get_rect(center=((item.col + 1) * CELL_SIZE, (item.row + 0.5) * CELL_SIZE))
        screen.blit(item_icon, item_rect)

        # Draw the neighbors with shrinking effect
        """
        for n_row, n_col in neighbors:
            neighbor = grid[n_row][n_col]
            if neighbor:
                neighbor_icon = pygame.transform.scale(neighbor.get_icon(), (int(CELL_SIZE * scale), int(CELL_SIZE * scale)))
                neighbor_rect = neighbor_icon.get_rect(center=((n_col + 0.5) * CELL_SIZE, (n_row + 0.5) * CELL_SIZE))
                screen.blit(neighbor_icon, neighbor_rect)
        """

        pygame.display.flip()
        clock.tick(frames // (animation_duration / 1000))


    # return the item to the grid
    grid[item.row][item.col] = item


def play_spawn_animation(screen, item):
    animation_duration = 200  # in milliseconds
    frames = 20
    clock = pygame.time.Clock()

    #remove the item from the grid temporarily
    grid[item.row][item.col] = None

    for i in range(frames):
        scale = (i + 1) / frames
        screen.fill(BACKGROUND_COLOR)  # Clear screen for animation

        #redraw the grid
        draw_grid()

        # Draw the item with growing effect
        item_icon = pygame.transform.scale(item.get_icon(), (int(CELL_SIZE * scale), int(CELL_SIZE * scale)))
        item_rect = item_icon.get_rect(center=((item.col+1) * CELL_SIZE, (item.row+0.5) * CELL_SIZE))
        screen.blit(item_icon, item_rect)

        pygame.display.flip()
        clock.tick(frames // (animation_duration / 1000))

    #return the item to the grid
    grid[item.row][item.col] = item

"""GAME LOOP"""
# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN: #any keypress
            spawn_item()

            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    check_and_merge(row, col)

    # Clear screen
    screen.fill(BACKGROUND_COLOR)

    # Draw grid and items
    draw_grid()

    # Update screen
    pygame.display.flip()

pygame.quit()
