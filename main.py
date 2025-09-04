import pygame
import asyncio
# import sys
import random, time
from pygame.locals import *

import words as w
random.seed(time.time())
L = w.word_list

# Initialize Pygame
pygame.init()

# Screen dimensions - expanded to fit all elements
WIDTH, HEIGHT = 1000, 800  # Increased from 800x600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wordle-like Game with Countdown Timer")

# Colors
BACKGROUND = (28, 28, 36)
GRID_BG = (58, 58, 70)
GRID_BORDER = (86, 86, 104)
LETTER_BG = (44, 44, 56)
LETTER_CORRECT = (106, 170, 100)  # Green
LETTER_PRESENT = (201, 180, 88)   # Yellow
LETTER_ABSENT = (120, 124, 126)   # Gray
TEXT_COLOR = (240, 240, 240)
TIMER_BG = (40, 40, 50)
TIMER_NORMAL = (120, 180, 240)
TIMER_WARNING = (240, 80, 80)
WHITE = (255, 255, 255)

# Game settings
GRID_SIZE = 5
GRID_ROWS = 6
GRID_MARGIN = 50
CELL_SIZE = 70  # Slightly larger cells
CELL_MARGIN = 10

# Fonts
# font_large = pygame.font.SysFont('Arial', 48, bold=True)
# font_medium = pygame.font.SysFont('Arial', 36)
# font_small = pygame.font.SysFont('Arial', 28)
# font_timer = pygame.font.SysFont('Arial', 40, bold=True)

font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 28)
font_timer = pygame.font.Font(None, 40)

# Timer settings
TOTAL_SECONDS = 150  # 2 minutes 30 seconds
remaining_time = TOTAL_SECONDS
timer_active = True
start_time = pygame.time.get_ticks()

# Game data
current_row = 0
current_col = 0
game_board = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_ROWS)]
word_to_guess = L[random.randint(0,len(L))].upper()  # Select random word from word_list
feedback = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_ROWS)]  # 0 = empty, 1 = absent, 2 = present, 3 = correct

def draw_grid():
    """Draw the game grid with letters"""
    grid_width = GRID_SIZE * (CELL_SIZE + CELL_MARGIN) - CELL_MARGIN
    grid_height = GRID_ROWS * (CELL_SIZE + CELL_MARGIN) - CELL_MARGIN
    start_x = (WIDTH - grid_width) // 2
    start_y = (HEIGHT - grid_height) // 2 - 50
    
    for row in range(GRID_ROWS):
        for col in range(GRID_SIZE):
            x = start_x + col * (CELL_SIZE + CELL_MARGIN)
            y = start_y + row * (CELL_SIZE + CELL_MARGIN)
            
            # Determine cell color based on feedback
            if feedback[row][col] == 0:  # Empty
                cell_color = LETTER_BG
            elif feedback[row][col] == 1:  # Absent
                cell_color = LETTER_ABSENT
            elif feedback[row][col] == 2:  # Present
                cell_color = LETTER_PRESENT
            else:  # Correct
                cell_color = LETTER_CORRECT
            
            # Draw cell background
            pygame.draw.rect(screen, cell_color, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, GRID_BORDER, (x, y, CELL_SIZE, CELL_SIZE), 2)
            
            # Draw letter if present
            if game_board[row][col]:
                letter = font_medium.render(game_board[row][col], True, TEXT_COLOR)
                screen.blit(letter, (x + CELL_SIZE//2 - letter.get_width()//2, 
                                     y + CELL_SIZE//2 - letter.get_height()//2))

def draw_timer():
    """Draw the countdown timer at bottom left"""
    # Calculate remaining time
    minutes = remaining_time // 60
    seconds = remaining_time % 60
    timer_text = f"{minutes:02d}:{seconds:02d}"
    
    # Change color to red when time is low
    timer_color = TIMER_WARNING if remaining_time <= 15 else TIMER_NORMAL
    
    # Draw timer background
    pygame.draw.rect(screen, TIMER_BG, (20, HEIGHT - 70, 150, 50), border_radius=10)
    pygame.draw.rect(screen, timer_color, (20, HEIGHT - 70, 150, 50), 3, border_radius=10)
    
    # Draw timer text
    timer_surface = font_timer.render(timer_text, True, timer_color)
    screen.blit(timer_surface, (95 - timer_surface.get_width()//2, HEIGHT - 55))

def draw_title():
    """Draw the game title"""
    title = font_large.render("WORDLE-TIMER", True, (120, 200, 255))
    subtitle = font_small.render("Type letters to play", True, (180, 180, 200))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 90))

def draw_keyboard():
    """Draw an on-screen keyboard visualization"""
    keyboard_rows = [
        "QWERTYUIOP",
        "ASDFGHJKL",
        "ZXCVBNM"
    ]
    
    start_y = HEIGHT - 200  # Adjusted position
    
    for row_idx, row in enumerate(keyboard_rows):
        start_x = (WIDTH - (len(row) * (45 + 5))) // 2
        
        for idx, key in enumerate(row):
            x = start_x + idx * 50  # Slightly wider keys
            y = start_y + row_idx * 55  # Slightly taller rows
            
            # Draw key
            pygame.draw.rect(screen, LETTER_BG, (x, y, 45, 45), border_radius=5)
            pygame.draw.rect(screen, GRID_BORDER, (x, y, 45, 45), 2, border_radius=5)
            
            # Draw letter
            letter = font_small.render(key, True, TEXT_COLOR)
            screen.blit(letter, (x + 22 - letter.get_width()//2, y + 22 - letter.get_height()//2))

def draw_instructions():
    """Draw game instructions"""
    lines = [
        "HOW TO PLAY:",
        "- Try to guess the hidden word",
        "- Green: correct letter in correct position",
        "- Yellow: correct letter in wrong position",
        "- Gray: letter not in the word",
        "- You have 2 minutes 30 seconds to solve!"
    ]
    
    y_pos = HEIGHT - 400  # Adjusted position
    for i, line in enumerate(lines):
        color = (200, 220, 255) if i == 0 else (180, 200, 220)
        size = font_small if i > 0 else font_medium
        text = size.render(line, True, color)
        screen.blit(text, (WIDTH - 350, y_pos))  # Adjusted position
        y_pos += 35 if i == 0 else 30

def draw_time_up_message():
    """Draw the time up message"""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((20, 20, 30, 200))
    screen.blit(overlay, (0, 0))
    
    message = font_large.render("TIME'S UP!", True, TIMER_WARNING)
    solution = font_medium.render(f"The word was: {word_to_guess}", True, LETTER_CORRECT)
    restart = font_small.render("Press SPACE to play again", True, (180, 220, 255))
    
    screen.blit(message, (WIDTH//2 - message.get_width()//2, HEIGHT//2 - 80))
    screen.blit(solution, (WIDTH//2 - solution.get_width()//2, HEIGHT//2))
    screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 80))

def check_word(guess):
    """Check the guessed word against the target word"""
    result = [0] * GRID_SIZE  # Initialize all as absent (0)
    target_list = list(word_to_guess)
    guess_list = list(guess)
    
    # First pass for correct letters
    for i in range(GRID_SIZE):
        if guess_list[i] == target_list[i]:
            result[i] = 3  # Correct
            target_list[i] = None  # Mark as used
    
    # Second pass for present letters
    for i in range(GRID_SIZE):
        if result[i] != 3:  # If not already correct
            if guess_list[i] in target_list:
                result[i] = 2  # Present
                target_list[target_list.index(guess_list[i])] = None  # Mark as used
    
    return result

def reset_game():
    """Reset the game state"""
    global game_board, feedback, current_row, current_col, remaining_time, timer_active, start_time, word_to_guess
    game_board = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_ROWS)]
    feedback = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_ROWS)]
    current_row = 0
    current_col = 0
    remaining_time = TOTAL_SECONDS
    timer_active = True
    start_time = pygame.time.get_ticks()
    word_to_guess = L[random.randint(0,len(L))].upper()  # Select a new random word

# Main game loop

running = True
game_over = False

async def main():
    global running, game_over, remaining_time, timer_active, current_guess, current_row, current_col, elapsed_seconds

    while running:
        clock = pygame.time.Clock()
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            
            if event.type == KEYDOWN:
                if not game_over:
                    # Handle letter input
                    if event.key == K_RETURN and current_col == GRID_SIZE:
                        # Get the current guess
                        current_guess = ''.join(game_board[current_row])
                        
                        # Check if the guess is valid (5 letters)
                        if len(current_guess) == GRID_SIZE:
                            # Check the word and get feedback
                            feedback[current_row] = check_word(current_guess)
                            
                            # Move to next row
                            current_row += 1
                            current_col = 0
                            
                            # Check if word was guessed correctly
                            if all(f == 3 for f in feedback[current_row-1]):
                                game_over = True
                                timer_active = False
                            
                            # Check if we've run out of rows
                            elif current_row >= GRID_ROWS:
                                game_over = True
                                timer_active = False
                    
                    # Handle backspace
                    elif event.key == K_BACKSPACE and current_col > 0:
                        current_col -= 1
                        game_board[current_row][current_col] = ''
                    
                    # Handle letter input
                    elif current_col < GRID_SIZE and event.unicode.isalpha():
                        game_board[current_row][current_col] = event.unicode.upper()
                        current_col += 1
                else:
                    # After game over, space restarts
                    if event.key == K_SPACE:
                        reset_game()
                        game_over = False
        
        # Update timer
        if timer_active and not game_over:
            elapsed_seconds = (pygame.time.get_ticks() - start_time) // 1000
            remaining_time = max(0, TOTAL_SECONDS - elapsed_seconds)
            
            if remaining_time == 0:
                timer_active = False
                game_over = True
        
        # Drawing
        screen.fill(BACKGROUND)
        
        # Draw decorative elements
        pygame.draw.circle(screen, (80, 120, 180, 100), (100, 100), 70)
        pygame.draw.circle(screen, (180, 100, 140, 100), (WIDTH-150, HEIGHT-150), 90)
        
        # Draw game elements
        draw_title()
        draw_grid()
        draw_timer()
        draw_keyboard()
        draw_instructions()
        
        # Draw game over message if needed
        if game_over:
            draw_time_up_message()
        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
