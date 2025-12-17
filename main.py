import pygame
import car
pygame.init()


WIDTH = 800
HEIGHT = 600

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Top-Down")
clock = pygame.time.Clock()

running = True

car_obj = car.Car()


while running:
    clock.tick(60) # 60 FPS ist fürn Arsch
    dt = clock.get_time() / 1000
    throttle_input = 0
    steering_input = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                throttle_input = 1
            elif event.key == pygame.K_s:
                throttle_input = -1
            if event.key == pygame.K_a:
                steering_input = -1
            elif event.key == pygame.K_d:
                steering_input = 1

    car_obj.update(dt, steering_input, throttle_input)
    pygame.display.flip()

