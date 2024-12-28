import pygame
pygame.init()

# Set up a window
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Pygame Test Window")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))  # Black background
    pygame.display.flip()

pygame.quit()