import pygame
import math
import random
import os

# Initialize Pygame
pygame.init()

# Get current screen size
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h

# Set the screen to windowed mode with full screen size
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rotating Doors")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Door properties
door_length = 100  # Double the door length to make the doors double width
closed_angle = 0
open_angle = 90  # 90 degrees for clockwise rotation

# Number of doors and their spacing
num_doors_horizontal = WIDTH // door_length  # Number of doors to fill the width
num_doors_vertical = HEIGHT // int(1.25 * door_length)  # 1.25 +times the door length for vertical spacing
spacing_horizontal = door_length  # No gaps horizontally
spacing_vertical = int(1.25 * door_length)  # 1.25 times the door length for vertical spacing
person_height_gap = door_length // 4  # Half the door length to place the person on top of the first line of doors

# Font for rendering text
font = pygame.font.Font(None, 24)  # Smaller font size

class Door:
    def __init__(self, left_vertex, random_number):
        self.left_vertex = left_vertex
        self.angle = closed_angle
        self.is_open = False
        self.random_number = random_number

    def toggle(self):
        self.is_open = not self.is_open
        self.angle = open_angle if self.is_open else closed_angle

    def calculate_right_vertex(self):
        angle_rad = math.radians(self.angle)
        right_vertex_x = self.left_vertex[0] + door_length * math.cos(angle_rad)
        right_vertex_y = self.left_vertex[1] + door_length * math.sin(angle_rad)
        return (right_vertex_x, right_vertex_y)

    def draw(self, surface):
        right_vertex = self.calculate_right_vertex()
        pygame.draw.line(surface, BLACK, self.left_vertex, right_vertex, 1)
        text_surface = font.render(str(self.random_number), True, BLACK)
        text_rect = text_surface.get_rect(center=(self.left_vertex[0], self.left_vertex[1] + 30))
        surface.blit(text_surface, text_rect)

class Person:
    def __init__(self, x, y):
        self.x = x
        self.y = y - 20  # Adjusted position
        self.direction = 1  # 1 for right, -1 for left
        self.step_size = 2  # Adjust the movement speed
        self.load_random_gif_image()
        self.image = pygame.transform.scale(self.gif_image, (50 * 3 // 2, 50 * 3 // 2))  # Scale by 50%
        self.frame_count = 0

    def load_random_gif_image(self):
        img_folder = "img"
        gif_files = [filename for filename in os.listdir(img_folder) if filename.endswith(".gif")]
        random_gif_file = random.choice(gif_files)
        random_gif_path = os.path.join(img_folder, random_gif_file)
        self.gif_image = pygame.image.load(random_gif_path)

    def move(self):
        self.x += self.direction * self.step_size  # Adjust the movement speed

        # Change direction when reaching the window's edge
        if self.x <= 0 or self.x >= WIDTH:
            self.direction *= -1

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def animate(self):
        self.frame_count += 1
        if self.frame_count >= self.gif_image.get_rect().height:
            self.frame_count = 0
        self.image = self.gif_image.subsurface((0, self.frame_count, self.gif_image.get_rect().width, 1))

# Create doors
doors = []
for i in range(num_doors_horizontal):
    for j in range(1, num_doors_vertical):  # Start from the second line
        left_vertex = (i * spacing_horizontal, j * spacing_vertical)
        random_number = random.randint(100000, 999999)
        doors.append(Door(left_vertex, random_number))

# Create person
person = Person(WIDTH // 2, HEIGHT // 2)  # Initially placed at the center

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move the person
    person.move()

    # Animate the person
    person.animate()

    # Clear the screen
    screen.fill(WHITE)

    # Draw lines at the top of the first line of doors
    for i in range(num_doors_horizontal):
        pygame.draw.line(screen, RED, (i * spacing_horizontal, 0), ((i + 1) * spacing_horizontal, 0), 2)

    # Draw all the doors
    for door in doors:
        door.draw(screen)

    # Draw the person
    person.draw(screen)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(10)  # Adjust the speed of the animation

pygame.quit()
