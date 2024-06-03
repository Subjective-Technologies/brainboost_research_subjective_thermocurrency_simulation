import pygame
import math
import random
import os
from PIL import Image

# Initialize Pygame
pygame.init()

# Get current screen size with margins
info = pygame.display.Info()
MARGIN = 50
WIDTH, HEIGHT = info.current_w - 2 * MARGIN, info.current_h - 2 * MARGIN

# Set the screen to windowed mode with adjusted size
screen = pygame.display.set_mode((WIDTH + 2 * MARGIN, HEIGHT + 2 * MARGIN))
pygame.display.set_caption("Rotating Doors")

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
COLOR_CHOICES = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 165, 0), (165, 42, 42),
    (128, 0, 128), (255, 20, 147), (0, 255, 255), (255, 255, 0), (0, 128, 128)
]

# Door properties
door_length = 100
closed_angle = 0
open_angle = 90

# Number of doors and their spacing
num_doors_horizontal = WIDTH // door_length
num_doors_vertical = HEIGHT // int(1.25 * door_length)  # Reduce the vertical space between doors
spacing_horizontal = door_length
spacing_vertical = int(1.25 * door_length)  # Reduce the vertical space between doors
vertical_shift = MARGIN + 50  # Lower the door lines
line_shift = 20  # Adjust this to place numbers closer to doors

# Font for rendering text
font = pygame.font.Font(None, 24)

class Door:
    def __init__(self, left_vertex, random_number, color):
        self.left_vertex = left_vertex
        self.angle = closed_angle
        self.is_open = False
        self.random_number = random_number
        self.color = color
        self.highlighted_digits = [False, False, False]
        self.highlighted_color = [None, None, None]

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
        pygame.draw.line(surface, self.color, self.left_vertex, right_vertex, 1)
        
        random_number_str = str(self.random_number).zfill(6)
        combined_surface = pygame.Surface((door_length, font.get_height()), pygame.SRCALPHA)
        x_offset = 0
        for i in range(3):
            color = self.highlighted_color[i] if self.highlighted_digits[i] else self.color
            text_surface = font.render(random_number_str[i*2:(i+1)*2], True, color)
            combined_surface.blit(text_surface, (x_offset, 0))
            x_offset += text_surface.get_width()
        
        text_rect = combined_surface.get_rect(center=(self.left_vertex[0] + door_length / 2, self.left_vertex[1] + line_shift))  # Center text below door
        surface.blit(combined_surface, text_rect)

    def highlight_next_digit(self, color):
        for i in range(3):
            if not self.highlighted_digits[i]:
                self.highlighted_digits[i] = True
                self.highlighted_color[i] = color
                break

class Person:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y  # Move above the first line of doors
        self.direction = 1
        self.step_size = 4
        self.random_number = random.randint(10, 99)
        self.color = color
        self.load_random_gif_frames()
        self.frame_count = 0
        self.number_change_interval = 150  # 5 seconds at 30 FPS
        self.number_frame_count = 0

    def load_random_gif_frames(self):
        img_folder = "img"
        gif_files = [filename for filename in os.listdir(img_folder) if filename.endswith(".gif")]
        random_gif_file = random.choice(gif_files)
        random_gif_path = os.path.join(img_folder, random_gif_file)
        
        pil_image = Image.open(random_gif_path)
        self.frames = []

        try:
            while True:
                frame = pil_image.copy()
                frame = frame.convert("RGBA")
                pygame_image = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
                scaled_frame = pygame.transform.scale(pygame_image, (int(pil_image.width * 0.7), int(pil_image.height * 0.7)))  # Scale down to 70%
                self.frames.append(scaled_frame)
                pil_image.seek(pil_image.tell() + 1)
        except EOFError:
            pass

    def move(self):
        self.x += self.direction * self.step_size

        if self.x < MARGIN:
            self.x = MARGIN
            self.direction *= -1
            self.frames = [pygame.transform.flip(frame, True, False) for frame in self.frames]
        elif self.x > WIDTH + MARGIN - self.frames[0].get_width():
            self.x = WIDTH + MARGIN - self.frames[0].get_width()
            self.direction *= -1
            self.frames = [pygame.transform.flip(frame, True, False) for frame in self.frames]

    def update_number(self):
        self.number_frame_count += 1
        if self.number_frame_count >= self.number_change_interval:
            self.random_number = random.randint(10, 99)
            self.number_frame_count = 0

    def draw(self, surface):
        current_frame = self.frames[self.frame_count // 1]
        surface.blit(current_frame, (self.x, self.y))
        text_surface = font.render(str(self.random_number), True, self.color)
        text_rect = text_surface.get_rect(center=(self.x + current_frame.get_width() // 2, self.y - 20))  # Position text above person
        pygame.draw.circle(surface, self.color, text_rect.center, text_rect.width // 2 + 10, 1)  # Draw hollow circle around number
        surface.blit(text_surface, text_rect)

    def animate(self):
        self.frame_count += 1
        if self.frame_count >= len(self.frames) * 1:
            self.frame_count = 0

    def check_highlight_door(self, doors):
        for door in doors:
            if door.left_vertex[0] <= self.x <= door.left_vertex[0] + door_length:
                door_random_number_str = str(door.random_number).zfill(6)
                for i in range(3):
                    if door_random_number_str[i*2:(i+1)*2] == str(self.random_number).zfill(2):
                        if i == 0 or (i > 0 and door.highlighted_digits[i-1] and door.highlighted_color[i-1] == self.color):
                            door.highlight_next_digit(self.color)
                            break

# Create doors
doors = []
door_dict = {}
for i in range(num_doors_horizontal):
    for j in range(num_doors_vertical):
        left_vertex = (i * spacing_horizontal + MARGIN, j * spacing_vertical + vertical_shift)
        random_number = random.randint(100000, 999999)
        color = WHITE if (i + j) % 2 == 0 else YELLOW
        door = Door(left_vertex, random_number, color)
        doors.append(door)
        door_dict[random_number] = door

# Create people
people = []
initial_y = doors[0].left_vertex[1] - 40  # Position people just above the first line of doors
for color in COLOR_CHOICES[:10]:  # Using only the first 10 colors
    for _ in range(3):
        x = random.randint(MARGIN, WIDTH + MARGIN)
        people.append(Person(x, initial_y, color))

# Main loop
running = True
clock = pygame.time.Clock()
door_toggle_interval = 60  # Interval in frames to toggle doors
frame_count = 0

def door_open(random_number):
    if random_number in door_dict:
        door_dict[random_number].toggle()

def door_close(random_number):
    if random_number in door_dict:
        door_dict[random_number].toggle()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move and animate all people
    for person in people:
        person.move()
        person.animate()
        person.update_number()
        person.check_highlight_door(doors)

    # Toggle random door on the first line at regular intervals
    if frame_count % door_toggle_interval == 0:
        random_door_index = random.randint(0, num_doors_horizontal - 1)
        door = doors[random_door_index]
        door.toggle()
        print(f"Door at index {random_door_index} toggled to {'open' if door.is_open else 'closed'}")

        if door.is_open:
            # Check if any person is on top of the opened door
            for person in people:
                person_feet_y = person.y + person.frames[0].get_height()
                door_top_y = door.left_vertex[1] - 10  # Adjust to make sure the detection is more accurate
                if door.left_vertex[0] <= person.x <= door.left_vertex[0] + door_length and person_feet_y >= door_top_y and person_feet_y < door.left_vertex[1]:
                    print(f"Person at x: {person.x}, y: {person.y} falls through door at {door.left_vertex}")
                    # Move the person to the line below
                    below_door_index = random_door_index + num_doors_horizontal
                    if below_door_index < len(doors):
                        below_door = doors[below_door_index]
                        person.y = below_door.left_vertex[1] - 40  # Position person above the door line
                        person.x = door.left_vertex[0]  # Align the person with the door below
                        break

    frame_count += 1

    # Clear the screen
    screen.fill(BLACK)

    # Draw all the doors
    for door in doors:
        door.draw(screen)

    # Draw all the people
    for person in people:
        person.draw(screen)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(30)

pygame.quit()
