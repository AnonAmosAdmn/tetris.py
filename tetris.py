import pygame
import random
from pygame.locals import *

# Initialize pygame
pygame.init()
pygame.font.init()

# Game settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 30
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)

# Tetrimino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]   # Z
]

SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

# Fonts
font_small = pygame.font.SysFont('Arial', 16)
font_medium = pygame.font.SysFont('Arial', 24)
font_large = pygame.font.SysFont('Arial', 32)

class Tetrimino:
    def __init__(self):
        self.shape_idx = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_idx]
        self.color = SHAPE_COLORS[self.shape_idx]
        self.x = 3  # Start position
        self.y = 0
        self.rotation = 0
    
    def rotate(self):
        # Transpose and reverse rows to rotate 90 degrees clockwise
        rotated = list(zip(*self.shape[::-1]))
        return [list(row) for row in rotated]
    
    def get_rotated_shape(self):
        return self.rotate()

class Game:
    def __init__(self):
        self.grid_width = 10
        self.grid_height = 20
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.current_piece = Tetrimino()
        self.next_piece = Tetrimino()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5  # seconds
        self.last_fall_time = 0
        self.paused = False
    
    def reset(self):
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.current_piece = Tetrimino()
        self.next_piece = Tetrimino()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5
    
    def valid_position(self, shape=None, x=None, y=None):
        if shape is None:
            shape = self.current_piece.shape
        if x is None:
            x = self.current_piece.x
        if y is None:
            y = self.current_piece.y
            
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    if (x + j < 0 or x + j >= self.grid_width or 
                        y + i >= self.grid_height or 
                        (y + i >= 0 and self.grid[y + i][x + j])):
                        return False
        return True
    
    def merge_piece(self):
        for i, row in enumerate(self.current_piece.shape):
            for j, cell in enumerate(row):
                if cell and self.current_piece.y + i >= 0:
                    self.grid[self.current_piece.y + i][self.current_piece.x + j] = self.current_piece.color
    
    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell == 0 for cell in row)]
        lines_cleared = self.grid_height - len(new_grid)
        
        if lines_cleared > 0:
            self.lines_cleared += lines_cleared
            self.score += [100, 300, 500, 800][lines_cleared - 1] * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)
            
            # Add new empty lines at the top
            for _ in range(lines_cleared):
                new_grid.insert(0, [0 for _ in range(self.grid_width)])
            
            self.grid = new_grid
    
    def move_left(self):
        if not self.paused and not self.game_over:
            if self.valid_position(x=self.current_piece.x - 1):
                self.current_piece.x -= 1
    
    def move_right(self):
        if not self.paused and not self.game_over:
            if self.valid_position(x=self.current_piece.x + 1):
                self.current_piece.x += 1
    
    def move_down(self):
        if not self.paused and not self.game_over:
            if self.valid_position(y=self.current_piece.y + 1):
                self.current_piece.y += 1
                return True
            else:
                self.merge_piece()
                self.clear_lines()
                self.current_piece = self.next_piece
                self.next_piece = Tetrimino()
                if not self.valid_position():
                    self.game_over = True
                return False
        return True
    
    def hard_drop(self):
        if not self.paused and not self.game_over:
            while self.move_down():
                pass
    
    def rotate_piece(self):
        if not self.paused and not self.game_over:
            rotated = self.current_piece.get_rotated_shape()
            if self.valid_position(shape=rotated):
                self.current_piece.shape = rotated
    
    def update(self, current_time):
        if self.paused or self.game_over:
            return
            
        if current_time - self.last_fall_time > self.fall_speed * 1000:
            self.move_down()
            self.last_fall_time = current_time
    
    def draw(self):
        screen.fill(BLACK)
        
        # Draw game board
        board_x = (SCREEN_WIDTH - self.grid_width * GRID_SIZE) // 2
        board_y = SCREEN_HEIGHT - self.grid_height * GRID_SIZE - 20
        
        # Draw grid background
        pygame.draw.rect(screen, GRAY, (board_x - 2, board_y - 2, 
                                       self.grid_width * GRID_SIZE + 4, 
                                       self.grid_height * GRID_SIZE + 4), 0)
        
        # Draw grid cells
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x]:
                    pygame.draw.rect(screen, self.grid[y][x], 
                                   (board_x + x * GRID_SIZE, 
                                    board_y + y * GRID_SIZE, 
                                    GRID_SIZE, GRID_SIZE), 0)
                pygame.draw.rect(screen, (50, 50, 50), 
                               (board_x + x * GRID_SIZE, 
                                board_y + y * GRID_SIZE, 
                                GRID_SIZE, GRID_SIZE), 1)
        
        # Draw current piece
        for i, row in enumerate(self.current_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, self.current_piece.color, 
                                    (board_x + (self.current_piece.x + j) * GRID_SIZE, 
                                     board_y + (self.current_piece.y + i) * GRID_SIZE, 
                                     GRID_SIZE, GRID_SIZE), 0)
        
        # Draw next piece preview
        next_x = board_x + self.grid_width * GRID_SIZE + 40
        next_y = board_y + 100
        
        next_text = font_medium.render("Next:", True, WHITE)
        screen.blit(next_text, (next_x, next_y - 40))
        
        for i, row in enumerate(self.next_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, self.next_piece.color, 
                                    (next_x + j * GRID_SIZE, 
                                     next_y + i * GRID_SIZE, 
                                     GRID_SIZE, GRID_SIZE), 0)
        
        # Draw score and level
        score_text = font_medium.render(f"Score: {self.score}", True, WHITE)
        level_text = font_medium.render(f"Level: {self.level}", True, WHITE)
        lines_text = font_medium.render(f"Lines: {self.lines_cleared}", True, WHITE)
        
        screen.blit(score_text, (20, 20))
        screen.blit(level_text, (20, 60))
        screen.blit(lines_text, (20, 100))
        
        # Draw controls
        controls = [
            "Controls:",
            "Left/Right Arrow: Move",
            "Up Arrow: Rotate",
            "Down Arrow: Soft Drop",
            "Space: Hard Drop",
            "P: Pause",
            "R: Restart"
        ]
        
        for i, line in enumerate(controls):
            control_text = font_small.render(line, True, WHITE)
            screen.blit(control_text, (20, SCREEN_HEIGHT - 120 + i * 20))
        
        # Draw game over or paused message
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            game_over_text = font_large.render("GAME OVER", True, RED)
            restart_text = font_medium.render("Press R to restart", True, WHITE)
            
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        
        elif self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            pause_text = font_large.render("PAUSED", True, WHITE)
            screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        pygame.display.flip()
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                
                if event.type == KEYDOWN:
                    if event.key == K_LEFT:
                        self.move_left()
                    elif event.key == K_RIGHT:
                        self.move_right()
                    elif event.key == K_DOWN:
                        self.move_down()
                    elif event.key == K_UP:
                        self.rotate_piece()
                    elif event.key == K_SPACE:
                        self.hard_drop()
                    elif event.key == K_p:
                        self.paused = not self.paused
                    elif event.key == K_r:
                        self.reset()
                    elif event.key == K_q:
                        running = False
            
            self.update(current_time)
            self.draw()
            clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()