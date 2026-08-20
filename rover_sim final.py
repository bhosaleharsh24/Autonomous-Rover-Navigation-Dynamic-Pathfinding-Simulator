import pygame
import math
import heapq
import random
 
pygame.init()
pygame.font.init()  
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Autonomous Rover Navigation & Pathfinding - Dynamic HUD")
clock = pygame.time.Clock()
 
DARK_GRAY = (30, 30, 30)
RED = (220, 50, 50)
GREEN = (50, 220, 50)
BLUE = (50, 150, 255)
YELLOW = (240, 240, 60)
WHITE = (200, 200, 200)
ORANGE = (240, 150, 40)
 
GRID_SIZE = 20
COLS = WIDTH // GRID_SIZE
ROWS = HEIGHT // GRID_SIZE
 
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

random.seed(42)
for r in range(ROWS):
    for c in range(COLS):
        if random.random() < 0.2:
            grid[r][c] = 1
 
start_grid = None
goal_grid = None
SELECT_START, SELECT_GOAL, TRAVELING = 0, 1, 2
mode = SELECT_START
 
def heuristic(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
 
def a_star(start, goal):
    neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
 
    while open_set:
        current = heapq.heappop(open_set)[1]
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
 
        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < COLS and 0 <= neighbor[1] < ROWS:
                if grid[neighbor[1]][neighbor[0]] == 1:
                    continue
                temp_g = g_score[current] + math.sqrt(dx**2 + dy**2)
                if neighbor not in g_score or temp_g < g_score[neighbor]:
                    g_score[neighbor] = temp_g
                    f_score = temp_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor))
                    came_from[neighbor] = current
    return []
 
rover_x, rover_y = 0, 0
rover_speed = 0.3
path = []
path_index = 0
 
font = pygame.font.SysFont("Consolas", 14, bold=True)
small_font = pygame.font.SysFont("Consolas", 13, bold=True)
 
def handle_click(mx, my):
    global start_grid, goal_grid, mode, rover_x, rover_y, path, path_index
 
    c, r = mx // GRID_SIZE, my // GRID_SIZE
    if not (0 <= c < COLS and 0 <= r < ROWS):
        return
    if mode == TRAVELING and c < 14 and r < 5:  #prevents object on HUD
        return
 
    if mode == SELECT_START:
        if grid[r][c] == 1:
            return 
        start_grid = (c, r)
     #converting
        rover_x = c * GRID_SIZE + GRID_SIZE // 2
        rover_y = r * GRID_SIZE + GRID_SIZE // 2
        mode = SELECT_GOAL
 
    elif mode == SELECT_GOAL:
        if grid[r][c] == 1 or (c, r) == start_grid:
            return 
        goal_grid = (c, r)
        path = a_star(start_grid, goal_grid)
        path_index = 0
        mode = TRAVELING
 
    elif mode == TRAVELING:
        
        if (c, r) == goal_grid: #the goal shouldnt be obstacle
            return
        if grid[r][c] == 0: #obstacle only on empty cell
            grid[r][c] = 1
            remaining = set(path[path_index:])
            #Dynamic rerouting
            if (c, r) in remaining or (c, r) == start_grid:
                current_rover_grid = (int(rover_x // GRID_SIZE), int(rover_y // GRID_SIZE))
                path = a_star(current_rover_grid, goal_grid)
                path_index = 0
 
running = True
while running:
    clock.tick(60)
    screen.fill(DARK_GRAY)
 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            handle_click(*event.pos)
 
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] == 1:
                pygame.draw.rect(screen, (80, 80, 80), (c * GRID_SIZE, r * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1))
 
    for pt in path:
        pygame.draw.circle(screen, YELLOW, (pt[0] * GRID_SIZE + GRID_SIZE // 2, pt[1] * GRID_SIZE + GRID_SIZE // 2), 3)
 
    if start_grid is not None:
        pygame.draw.circle(screen, ORANGE, (start_grid[0] * GRID_SIZE + GRID_SIZE // 2, start_grid[1] * GRID_SIZE + GRID_SIZE // 2), 6, 2)
 
    if goal_grid is not None:
        pygame.draw.circle(screen, GREEN, (goal_grid[0] * GRID_SIZE + GRID_SIZE // 2, goal_grid[1] * GRID_SIZE + GRID_SIZE // 2), 10)
 
    if mode == TRAVELING and path_index < len(path):
        target_x = path[path_index][0] * GRID_SIZE + GRID_SIZE // 2   #checks here are still path points remaining
        target_y = path[path_index][1] * GRID_SIZE + GRID_SIZE // 2  
 
        dx = target_x - rover_x
        dy = target_y - rover_y
        dist = math.hypot(dx, dy)
 
        if dist < rover_speed:
            path_index += 1
        else:
            rover_x += (dx / dist) * rover_speed
            rover_y += (dy / dist) * rover_speed
 
    if mode != SELECT_START:
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            for ray_len in range(0, 60):
                rx = int(rover_x + math.cos(rad) * ray_len)
                ry = int(rover_y + math.sin(rad) * ray_len)
                c, r = rx // GRID_SIZE, ry // GRID_SIZE
                if 0 <= c < COLS and 0 <= r < ROWS and grid[r][c] == 1:  #in the sensor hitting an obstacle
                    pygame.draw.line(screen, RED, (rover_x, rover_y), (rx, ry), 1)
                    break
                elif ray_len == 59:
                    pygame.draw.line(screen, BLUE, (rover_x, rover_y), (rx, ry), 1)
 
        pygame.draw.circle(screen, WHITE, (int(rover_x), int(rover_y)), 8)  #draw rover
 
    if mode == SELECT_START:
        status_text = "CLICK TO SET START POINT"
    elif mode == SELECT_GOAL:
        status_text = "CLICK TO SET GOAL POINT"
    else:
        status_text = "TARGET REACHED" if path_index >= len(path) else "AUTONOMOUS TRAVERSAL"
 
    telemetry = [
        f"POSITION: ({int(rover_x)}, {int(rover_y)})" if mode != SELECT_START else "POSITION: ---",
        f"TARGET:   ({goal_grid[0]*GRID_SIZE}, {goal_grid[1]*GRID_SIZE})" if goal_grid else "TARGET:   ---",
        f"STATUS:   {status_text}",
        f"WAYPOINTS REMAINING: {max(0, len(path) - path_index)}"
    ]
    pygame.draw.rect(screen, (10, 10, 10), (5, 5, 320, 85))
    pygame.draw.rect(screen, GREEN, (5, 5, 320, 85), 1)  
    for i, line in enumerate(telemetry):  #puts text on scrn
        text_surface = font.render(line, True, GREEN)
        screen.blit(text_surface, (12, 12 + i * 18))
 
    if mode == TRAVELING:
        hint = small_font.render("Click empty cell = place obstacle (reroutes if blocking path)", True, WHITE)
        screen.blit(hint, (10, HEIGHT - 20))

    pygame.display.flip()
pygame.quit()
