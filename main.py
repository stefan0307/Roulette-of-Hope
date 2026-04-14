import pygame
import random
import sys
import time

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Roulette of Hope")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 36)

# Colors --------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
GRAY = (180, 180, 180)
BLUE = (60, 120, 255)

# Text --------------------
def draw_text_styled(text, x, y, color=WHITE, stroke_color=BLACK):
    base = FONT.render(text, True, color)
    stroke = FONT.render(text, True, stroke_color)
    for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
        screen.blit(stroke, (x+dx, y+dy))
    screen.blit(base, (x, y))

# Assets --------------------
background_img = pygame.image.load("assets/background.png").convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

side_img_win = pygame.image.load("assets/roulette_info.png").convert_alpha()
side_img_lose = pygame.image.load("assets/roulette_info2.png").convert_alpha()
side_img = side_img_win

roulette_img = pygame.image.load("assets/roulette.png").convert_alpha()
roulette_img = pygame.transform.scale(roulette_img, (300, 300))

pygame.mixer.music.load("assets/casino_music.mp3")
music_volume = 0.1
pygame.mixer.music.set_volume(music_volume)
pygame.mixer.music.play(-1)

# Player --------------------
player_balance = 1000
bet_amount = 50
bet_color = "RED"

# Bet Input --------------------
bet_input_active = False
bet_input_text = str(bet_amount)
bet_input_rect = pygame.Rect(520, 380, 170, 40)

# Bailout --------------------
bailout_message = ""
bailout_time = 0
pending_bailout = False

# Binary Tree --------------------
class TreeNode:
    def __init__(self, value=None):
        self.value = value
        self.left = None
        self.right = None

def build_roulette_tree():
    root = TreeNode()
    root.left = TreeNode()
    root.right = TreeNode()

    root.left.left = TreeNode("RED")
    root.left.right = TreeNode("BLACK")
    root.right.left = TreeNode("RED")
    root.right.right = TreeNode()
    root.right.right.left = TreeNode("BLACK")
    root.right.right.right = TreeNode("GREEN")
    return root

def spin_tree(node):
    while node.value is None:
        node = random.choice([node.left, node.right])
    return node.value

roulette_tree = build_roulette_tree()

# Button Class --------------------
class Button:
    def __init__(self, text, x, y, w, h, color):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

    def draw(self):
        pygame.draw.rect(screen, BLACK, self.rect.inflate(4,4))
        pygame.draw.rect(screen, self.color, self.rect)
        draw_text_styled(self.text, self.rect.x + 10, self.rect.y + 10)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# States --------------------
START, MENU, ROULETTE = "start", "menu", "roulette"
state = MENU

# Buttons Definition --------------------
quit_btn = Button("QUIT", 300, 300, 200, 60, RED)
roulette_btn = Button("ROULETTE", 300, 220, 200, 60, GREEN)
back_btn = Button("BACK", 20, 20, 120, 50, GRAY)
spin_btn = Button("SPIN", 250, 500, 200, 60, GREEN)
all_in_btn = Button("ALL IN", 520, 420, 170, 40, BLUE)

red_btn = Button("RED", 520, 250, 90, 40, RED)
black_btn = Button("BLACK", 620, 250, 100, 40, BLACK)
green_btn = Button("0", 730, 250, 40, 40, GREEN)

vol_up_btn = Button("+", 570, 520, 40, 40, GREEN)
vol_down_btn = Button("-", 520, 520, 40, 40, RED)

# Routlette State --------------------
angle = 0
spinning = False
spin_speed = 0
result_text = ""
info_text = ""

# Main Loop --------------------
running = True
while running:
    screen.blit(background_img, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Bet Input -----
        if bet_input_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                bet_amount = min(int(bet_input_text or 0), player_balance)
                bet_input_active = False
            elif event.key == pygame.K_BACKSPACE:
                bet_input_text = bet_input_text[:-1]
            elif event.unicode.isdigit():
                temp = bet_input_text + event.unicode
                if int(temp) <= player_balance:
                    bet_input_text = temp

        # State Input -----
        if state == MENU:
            if roulette_btn.clicked(event):
                state = ROULETTE
            if quit_btn.clicked(event):
                running = False

        if state == ROULETTE:
            if back_btn.clicked(event):
                state = MENU

            if spin_btn.clicked(event) and not spinning and bet_amount > 0 and bet_amount <= player_balance:
                spinning = True
                spin_speed = random.randint(20, 30)
                result_text = ""
                info_text = ""
                player_balance -= bet_amount

            if bet_input_rect.collidepoint(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
                bet_input_active = True
                bet_input_text = ""

            if all_in_btn.clicked(event):
                bet_amount = player_balance
                bet_input_text = str(bet_amount)

            if red_btn.clicked(event): bet_color = "RED"
            if black_btn.clicked(event): bet_color = "BLACK"
            if green_btn.clicked(event): bet_color = "GREEN"

            # Volume Control -----
            if vol_up_btn.clicked(event):
                music_volume = min(1.0, music_volume + 0.1)
                pygame.mixer.music.set_volume(music_volume)

            if vol_down_btn.clicked(event):
                music_volume = max(0.0, music_volume - 0.1)
                pygame.mixer.music.set_volume(music_volume)

    # Spin Logic --------------------
    if state == ROULETTE and spinning:
        angle += spin_speed
        spin_speed -= 0.4
        if spin_speed <= 0:
            spinning = False
            landed = spin_tree(roulette_tree)

            if landed == bet_color:
                win = bet_amount * (14 if landed == "GREEN" else 2)
                player_balance += win
                result_text = f"{landed} WIN +${win}"
                info_text = "Good job!"
                side_img = side_img_win
            else:
                result_text = f"{landed} LOSE"
                info_text = "Only losers quit,\nkeep going"
                side_img = side_img_lose

                if player_balance == 0:
                    pending_bailout = True
                    bailout_time = time.time()

    # Apply Bailout -----
    if pending_bailout and time.time() - bailout_time >= 0.5:
        player_balance = 10
        bailout_message = "  Your friend gave you 10 dollars, keep going!"
        bailout_time = time.time()
        pending_bailout = False

    # Draw --------------------
    if state == MENU:
        draw_text_styled("Main Menu", 330, 180)
        roulette_btn.draw()
        quit_btn.draw()

    elif state == ROULETTE:
        back_btn.draw()
        spin_btn.draw()
        all_in_btn.draw()

        red_btn.draw()
        black_btn.draw()
        green_btn.draw()

        vol_up_btn.draw()
        vol_down_btn.draw()

        draw_text_styled(f"Balance: ${player_balance}", 520, 20)
        draw_text_styled(f"Color Bet: {bet_color}", 520, 210)
        draw_text_styled("Bet Amount:", 520, 340)
        draw_text_styled(f"Volume: {int(music_volume * 100)}%", 520, 480)

        pygame.draw.rect(screen, BLUE if bet_input_active else GRAY, bet_input_rect, 2)
        draw_text_styled(bet_input_text, bet_input_rect.x + 10, bet_input_rect.y + 8)

        rotated = pygame.transform.rotate(roulette_img, angle)
        screen.blit(rotated, rotated.get_rect(center=(350, 300)))

        screen.blit(side_img, (20, 100))
        if info_text:
            draw_text_styled(info_text, 20, 260)

        if result_text:
            draw_text_styled(result_text, 270, 460)

        if bailout_message and time.time() - bailout_time < 5:
            draw_text_styled(bailout_message, 160, 100, RED)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
