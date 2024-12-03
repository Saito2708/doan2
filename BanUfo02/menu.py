import pygame
import sys
import subprocess
import pygame_gui
import os
import pickle

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width, screen_height = 1000, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Game Menu")

clock = pygame.time.Clock()

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
blue = (0, 0, 255)
transparent_black = (0, 0, 0, 150)
hover_button_color = (70, 170, 220)
hover_button_delete_color = (254, 57, 57)

# Load assets
background_image = pygame.image.load('img/bgStart.jpg')
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# Path to save files
save_path = 'inforPlayer/'

# Draw text with background function
def draw_text(text, font, color, surface, x, y, bg_color=None):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    if bg_color:
        background_rect = textrect.inflate(20, 10)  # Create a background rect with some padding
        s = pygame.Surface(background_rect.size, pygame.SRCALPHA)
        s.fill(bg_color)
        surface.blit(s, background_rect.topleft)
    surface.blit(textobj, textrect)

# Draw rounded rectangle function
def draw_rounded_rect(surface, rect, color, corner_radius):
    if corner_radius > 0:
        pygame.draw.rect(surface, color, rect, border_radius=corner_radius)
    else:
        pygame.draw.rect(surface, color, rect)

# Input name function
def input_name():
    manager = pygame_gui.UIManager((screen_width, screen_height))
    input_box = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect(screen_width / 2 - 100, screen_height / 2 - 50, 200, 30),
        manager=manager
    )
    input_box.set_text('')  # Clear initial text if any
    while True:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    name = input_box.get_text()
                    if name:
                        return name
            manager.process_events(event)
        manager.update(time_delta)
        screen.blit(background_image, (0, 0))
        draw_text('Input Your Name:', small_font, white, screen, screen_width / 2, screen_height / 2 - 100, transparent_black)
        manager.draw_ui(screen)  # Draw the pygame_gui interface
        pygame.display.flip()

# Function to load saved games
def load_saved_games():
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    saved_games = []
    for filename in os.listdir(save_path):
        if filename.endswith('.pkl'):
            with open(os.path.join(save_path, filename), 'rb') as file:
                try:
                    game_data = pickle.load(file)
                    game_data['filename'] = filename  # Add filename to game data
                    saved_games.append(game_data)
                except (EOFError, pickle.UnpicklingError):
                    continue
    return saved_games

# Function to choose or create a game
def choose_or_create_game():
    saved_games = load_saved_games()
    manager = pygame_gui.UIManager((screen_width, screen_height))
    buttons = []

    if saved_games:
        for i, game in enumerate(saved_games):
            name = game.get('name', os.path.splitext(game['filename'])[0])  # Use base name of the file if name is unknown
            button_rect = pygame.Rect(screen_width / 2 - 100, screen_height / 3 + i * 60, 200, 50)
            delete_button_rect = pygame.Rect(screen_width / 2 + 110, screen_height / 3 + i * 60, 50, 50)
            buttons.append((button_rect, delete_button_rect, name, game['filename']))
        new_game_button_rect = pygame.Rect(screen_width / 2 - 100, screen_height / 2 + 50 + len(saved_games) * 60, 200, 50)
        buttons.append((new_game_button_rect, None, 'New Game', None))
    else:
        return input_name()

    while True:
        time_delta = clock.tick(60)/1000.0
        mx, my = pygame.mouse.get_pos()
        click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
            manager.process_events(event)
        
        manager.update(time_delta)
        screen.blit(background_image, (0, 0))
        draw_text('Choose a game or create a new one:', small_font, white, screen, screen_width / 2, screen_height / 4, transparent_black)
        
        for button_rect, delete_button_rect, name, filename in buttons:
            if button_rect.collidepoint((mx, my)):
                draw_rounded_rect(screen, button_rect, hover_button_color, 10)
                if click:
                    if name == 'New Game':
                        return input_name()
                    else:
                        return name
            else:
                draw_rounded_rect(screen, button_rect, transparent_black, 10)
            draw_text(name, small_font, white, screen, button_rect.centerx, button_rect.centery)
            
            if delete_button_rect:
                if delete_button_rect.collidepoint((mx, my)):
                    draw_rounded_rect(screen, delete_button_rect, hover_button_delete_color, 10)
                    if click:
                        os.remove(os.path.join(save_path, filename))
                        return choose_or_create_game()  # Reload the menu after deleting
                else:
                    draw_rounded_rect(screen, delete_button_rect, transparent_black, 10)
                draw_text('X', small_font, white, screen, delete_button_rect.centerx, delete_button_rect.centery)

        manager.draw_ui(screen)
        pygame.display.flip()

# Main menu function
def main_menu():
    click = False
    while True:
        screen.blit(background_image, (0, 0))
        draw_text('PEACE UFO', font, white, screen, screen_width / 2, screen_height / 4, transparent_black)

        mx, my = pygame.mouse.get_pos()

        button_1 = pygame.Rect(screen_width / 2 - 100, screen_height / 2 - 50, 200, 50)
        button_2 = pygame.Rect(screen_width / 2 - 100, screen_height / 2 + 10, 200, 50)

        buttons = [button_1, button_2,]
        button_texts = ['Start Game', 'Quit']
        
        for i, button in enumerate(buttons):
            if button.collidepoint((mx, my)):
                draw_rounded_rect(screen, button, hover_button_color, 10)
                if click:
                    if i == 0:
                        player_name = choose_or_create_game()
                        # Run Game.py with player name
                        subprocess.run(["python", "Game.py", player_name])
                    elif i == 1:
                        pygame.quit()
                        sys.exit()
                        
            else:
                draw_rounded_rect(screen, button, transparent_black, 10)
            draw_text(button_texts[i], small_font, white, screen, button.centerx, button.centery)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()

# Run main menu
main_menu()
