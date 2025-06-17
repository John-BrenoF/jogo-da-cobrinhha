import pygame
import random
import time
import os
from plyer import notification
import logging
from datetime import datetime
import sys

# Configuração inicial do Pygame
pygame.init()
pygame.font.init()

# Configurações da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Cores

COLORS = {
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "GREEN": (0, 255, 0),
    "RED": (255, 0, 0),
    "BLUE": (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "CYAN": (0, 255, 255),
    "MAGENTA": (255, 0, 255),
    "GRAY": (128, 128, 128),
    "DARK_GREEN": (0, 100, 0),
    "DARK_RED": (139, 0, 0),
    "DARK_BLUE": (0, 0, 139)
}

# Configuração dos modos de jogo
GAME_MODES = {
    "🎮 Clássico": "classic",
    "🤖 Modo IA": "ai",
    "🌀 Modo Portal": "portal",
    "🚧 Modo Obstáculos": "obstacles",
    "🌈 Modo Colorido": "colorful",
    "🎯 Modo Precisão": "precision",
    "⚔️ Modo Competitivo": "competitive"
}

# Configuração das dificuldades
DIFFICULTY_LEVELS = {
    "🐢 Fácil": (150, 1),
    "🐍 Médio": (100, 2),
    "🔥 Difícil": (70, 3),
    "💀 Insano": (50, 5),
    "⚡ Ultra": (30, 10)
}

# Configuração dos temas
THEMES = {
    "🌙 Escuro": {
        "background": COLORS["BLACK"],
        "snake": COLORS["GREEN"],
        "food": COLORS["RED"],
        "obstacle": COLORS["YELLOW"],
        "powerup": COLORS["MAGENTA"],
        "text": COLORS["WHITE"],
        "border": COLORS["CYAN"],
        "score": COLORS["YELLOW"],
        "menu": COLORS["BLUE"]
    },
    "☀️ Claro": {
        "background": COLORS["WHITE"],
        "snake": COLORS["BLUE"],
        "food": COLORS["RED"],
        "obstacle": COLORS["YELLOW"],
        "powerup": COLORS["MAGENTA"],
        "text": COLORS["BLACK"],
        "border": COLORS["CYAN"],
        "score": COLORS["YELLOW"],
        "menu": COLORS["BLUE"]
    },
    "🎨 Neon": {
        "background": COLORS["BLACK"],
        "snake": COLORS["CYAN"],
        "food": COLORS["RED"],
        "obstacle": COLORS["YELLOW"],
        "powerup": COLORS["MAGENTA"],
        "text": COLORS["GREEN"],
        "border": COLORS["CYAN"],
        "score": COLORS["YELLOW"],
        "menu": COLORS["BLUE"]
    }
}

# Efeitos de power-up
POWERUP_EFFECTS = [
    ("+5 pontos", lambda score, speed: (score+5, speed)),
    ("-5 pontos", lambda score, speed: (max(0, score-5), speed)),
    ("Turbo!", lambda score, speed: (score, max(20, speed-40))),
    ("Lento!", lambda score, speed: (score, speed+40)),
    ("Nada acontece", lambda score, speed: (score, speed)),
]

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, COLORS["WHITE"], self.rect, 2, border_radius=10)
        
        text_surface = self.font.render(self.text, True, COLORS["WHITE"])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Jogo da Cobrinha")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.current_theme = THEMES["🌙 Escuro"]
        self.reset_game()

    def reset_game(self):
        self.snake = [[GRID_HEIGHT//2, GRID_WIDTH//2]]
        self.direction = "RIGHT"
        self.obstacles = []
        self.ai_snake = None
        self.powerups = []
        self.score = 0
        self.max_score = self.load_record()
        self.game_over = False
        self.paused = False
        self.turbo_timer = 0
        self.ai_score = 0
        self.start_time = time.time()
        self.food = self.generate_food()

    def generate_food(self):
        while True:
            pos = [random.randint(1, GRID_HEIGHT-2), random.randint(1, GRID_WIDTH-2)]
            if pos not in self.snake and pos not in self.obstacles and (self.ai_snake is None or pos not in self.ai_snake):
                return pos

    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, self.current_theme["border"], (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, self.current_theme["border"], (0, y), (SCREEN_WIDTH, y))

    def draw_snake(self):
        for i, segment in enumerate(self.snake):
            color = self.current_theme["snake"]
            if i == 0:  # Cabeça
                pygame.draw.rect(self.screen, color, 
                               (segment[1]*GRID_SIZE, segment[0]*GRID_SIZE, GRID_SIZE, GRID_SIZE))
                # Desenha os olhos
                eye_size = GRID_SIZE // 4
                if self.direction == "RIGHT":
                    pygame.draw.circle(self.screen, COLORS["BLACK"], 
                                     (segment[1]*GRID_SIZE + GRID_SIZE - eye_size, 
                                      segment[0]*GRID_SIZE + eye_size), eye_size)
                    pygame.draw.circle(self.screen, COLORS["BLACK"], 
                                     (segment[1]*GRID_SIZE + GRID_SIZE - eye_size, 
                                      segment[0]*GRID_SIZE + GRID_SIZE - eye_size), eye_size)
                elif self.direction == "LEFT":
                    pygame.draw.circle(self.screen, COLORS["BLACK"], 
                                     (segment[1]*GRID_SIZE + eye_size, 
                                      segment[0]*GRID_SIZE + eye_size), eye_size)
                    pygame.draw.circle(self.screen, COLORS["BLACK"], 
                                     (segment[1]*GRID_SIZE + eye_size, 
                                      segment[0]*GRID_SIZE + GRID_SIZE - eye_size), eye_size)
                elif self.direction == "UP":
                    pygame.draw.circle(self.screen, COLORS["BLACK"], 
                                     (segment[1]*GRID_SIZE + eye_size, 
                                      segment[0]*GRID_SIZE + eye_size), eye_size)
                    pygame.draw.circle(self.screen, COLORS["BLACK"], 
                                     (segment[1]*GRID_SIZE + GRID_SIZE - eye_size, 
                                      segment[0]*GRID_SIZE + eye_size), eye_size)
                elif self.direction == "DOWN":
                    pygame.draw.circle(self.screen, COLORS["BLACK"], 
                                     (segment[1]*GRID_SIZE + eye_size, 
                                      segment[0]*GRID_SIZE + GRID_SIZE - eye_size), eye_size)
                    pygame.draw.circle(self.screen, COLORS["BLACK"], 
                                     (segment[1]*GRID_SIZE + GRID_SIZE - eye_size, 
                                      segment[0]*GRID_SIZE + GRID_SIZE - eye_size), eye_size)
            else:  # Corpo
                pygame.draw.rect(self.screen, color, 
                               (segment[1]*GRID_SIZE, segment[0]*GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def draw_ai_snake(self):
        if self.ai_snake:
            for i, segment in enumerate(self.ai_snake):
                color = COLORS["RED"] if i == 0 else COLORS["DARK_RED"]
                pygame.draw.rect(self.screen, color, 
                               (segment[1]*GRID_SIZE, segment[0]*GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def draw_food(self):
        pygame.draw.circle(self.screen, self.current_theme["food"],
                         (self.food[1]*GRID_SIZE + GRID_SIZE//2,
                          self.food[0]*GRID_SIZE + GRID_SIZE//2),
                         GRID_SIZE//2)

    def draw_powerups(self):
        for powerup in self.powerups:
            pygame.draw.circle(self.screen, self.current_theme["powerup"],
                             (powerup[1]*GRID_SIZE + GRID_SIZE//2,
                              powerup[0]*GRID_SIZE + GRID_SIZE//2),
                             GRID_SIZE//2)

    def draw_obstacles(self):
        for obstacle in self.obstacles:
            pygame.draw.rect(self.screen, self.current_theme["obstacle"],
                           (obstacle[1]*GRID_SIZE, obstacle[0]*GRID_SIZE,
                            GRID_SIZE, GRID_SIZE))

    def draw_score(self):
        score_text = f"Score: {self.score}"
        if self.ai_snake:
            score_text += f" | IA: {self.ai_score}"
        score_text += f" | Recorde: {self.max_score}"
        score_surface = self.font.render(score_text, True, self.current_theme["score"])
        self.screen.blit(score_surface, (10, 10))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(COLORS["BLACK"])
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("GAME OVER!", True, COLORS["RED"])
        score_text = self.font.render(f"Pontuação: {self.score}", True, COLORS["WHITE"])
        record_text = self.font.render(f"Recorde: {self.max_score}", True, COLORS["WHITE"])
        
        self.screen.blit(game_over_text, 
                        (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
        self.screen.blit(score_text, 
                        (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))
        self.screen.blit(record_text, 
                        (SCREEN_WIDTH//2 - record_text.get_width()//2, SCREEN_HEIGHT//2 + 40))

    def draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(COLORS["BLACK"])
        self.screen.blit(overlay, (0, 0))

        pause_text = self.font.render("PAUSA", True, COLORS["WHITE"])
        self.screen.blit(pause_text, 
                        (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2))

    def draw_main_menu(self):
        self.screen.fill(self.current_theme["background"])
        
        title = self.font.render("🐍 JOGO DA COBRINHA 🐍", True, self.current_theme["text"])
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))

        menu_options = [
            "🎮 JOGAR",
            "🏆 RANKING",
            "⚙️ CONFIGURAÇÕES",
            "❓ AJUDA",
            "🚪 SAIR"
        ]

        buttons = []
        for i, option in enumerate(menu_options):
            button = Button(SCREEN_WIDTH//2 - 100, 150 + i*60, 200, 50, option,
                          self.current_theme["menu"], COLORS["DARK_BLUE"])
            buttons.append(button)
            button.draw(self.screen)

        return buttons

    def draw_settings(self):
        self.screen.fill(self.current_theme["background"])
        
        title = self.font.render("⚙️ CONFIGURAÇÕES ⚙️", True, self.current_theme["text"])
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))

        settings_options = [
            "🌙 Tema Escuro",
            "☀️ Tema Claro",
            "🎨 Tema Neon",
            "🔙 Voltar"
        ]

        buttons = []
        for i, option in enumerate(settings_options):
            button = Button(SCREEN_WIDTH//2 - 100, 150 + i*60, 200, 50, option,
                          self.current_theme["menu"], COLORS["DARK_BLUE"])
            buttons.append(button)
            button.draw(self.screen)

        return buttons

    def draw_ranking(self):
        self.screen.fill(self.current_theme["background"])
        
        title = self.font.render("🏆 RANKING 🏆", True, self.current_theme["text"])
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))

        try:
            with open("ranking.txt", "r") as f:
                scores = [int(line.strip()) for line in f.readlines() if line.strip().isdigit()]
                scores.sort(reverse=True)
                scores = scores[:5]  # Top 5 scores
        except:
            scores = []

        y = 150
        for i, score in enumerate(scores):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
            score_text = f"{medal} {score:>5} pontos"
            text = self.font.render(score_text, True, self.current_theme["text"])
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y))
            y += 60

        back_button = Button(SCREEN_WIDTH//2 - 100, y + 20, 200, 50, "🔙 Voltar",
                           self.current_theme["menu"], COLORS["DARK_BLUE"])
        back_button.draw(self.screen)

        return [back_button]

    def draw_help(self):
        self.screen.fill(self.current_theme["background"])
        
        title = self.font.render("❓ AJUDA ❓", True, self.current_theme["text"])
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))

        help_text = [
            "Comandos do Jogo:",
            "  ↑, ↓, ←, → ou WASD: Mover",
            "  P: Pausar/Despausar",
            "  T: Modo Turbo (temporário)",
            "  H: Mostrar esta ajuda",
            "  Q: Sair do jogo",
            "  R: Reiniciar jogo",
            "  M: Voltar ao menu",
            "",
            "Power-ups:",
            "  ⭐: Efeito aleatório",
            "  🚀: Turbo",
            "  💎: Pontos extras",
            "  ⏰: Desacelerar"
        ]

        y = 150
        for line in help_text:
            text = self.small_font.render(line, True, self.current_theme["text"])
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y))
            y += 30

        back_button = Button(SCREEN_WIDTH//2 - 100, y + 20, 200, 50, "🔙 Voltar",
                           self.current_theme["menu"], COLORS["DARK_BLUE"])
        back_button.draw(self.screen)

        return [back_button]

    def load_record(self):
        try:
            with open("record.txt", "r") as f:
                return int(f.read())
        except:
            return 0

    def save_record(self):
        if self.score > self.max_score:
            with open("record.txt", "w") as f:
                f.write(str(self.score))

    def run(self):
        running = True
        in_menu = True
        current_screen = "menu"  # menu, settings, ranking, help

        while running:
            if current_screen == "menu":
                buttons = self.draw_main_menu()
                pygame.display.flip()
                menu_active = True
                while menu_active:
                    mouse_pos = pygame.mouse.get_pos()
                    for button in buttons:
                        button.is_hovered = button.rect.collidepoint(mouse_pos)
                    self.draw_main_menu()
                    pygame.display.flip()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            menu_active = False
                        for button in buttons:
                            if button.handle_event(event):
                                if button.text == "🎮 JOGAR":
                                    current_screen = "game"
                                    menu_active = False
                                    self.reset_game()
                                elif button.text == "⚙️ CONFIGURAÇÕES":
                                    current_screen = "settings"
                                    menu_active = False
                                elif button.text == "🏆 RANKING":
                                    current_screen = "ranking"
                                    menu_active = False
                                elif button.text == "❓ AJUDA":
                                    current_screen = "help"
                                    menu_active = False
                                elif button.text == "🚪 SAIR":
                                    running = False
                                    menu_active = False
                    self.clock.tick(60)

            elif current_screen == "settings":
                buttons = self.draw_settings()
                pygame.display.flip()
                settings_active = True
                while settings_active:
                    mouse_pos = pygame.mouse.get_pos()
                    for button in buttons:
                        button.is_hovered = button.rect.collidepoint(mouse_pos)
                    self.draw_settings()
                    pygame.display.flip()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            settings_active = False
                        for button in buttons:
                            if button.handle_event(event):
                                if button.text == "🌙 Tema Escuro":
                                    self.current_theme = THEMES["🌙 Escuro"]
                                elif button.text == "☀️ Tema Claro":
                                    self.current_theme = THEMES["☀️ Claro"]
                                elif button.text == "🎨 Tema Neon":
                                    self.current_theme = THEMES["🎨 Neon"]
                                elif button.text == "🔙 Voltar":
                                    current_screen = "menu"
                                    settings_active = False
                    self.clock.tick(60)

            elif current_screen == "ranking":
                buttons = self.draw_ranking()
                pygame.display.flip()
                ranking_active = True
                while ranking_active:
                    mouse_pos = pygame.mouse.get_pos()
                    for button in buttons:
                        button.is_hovered = button.rect.collidepoint(mouse_pos)
                    self.draw_ranking()
                    pygame.display.flip()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            ranking_active = False
                        for button in buttons:
                            if button.handle_event(event):
                                if button.text == "🔙 Voltar":
                                    current_screen = "menu"
                                    ranking_active = False
                    self.clock.tick(60)

            elif current_screen == "help":
                buttons = self.draw_help()
                pygame.display.flip()
                help_active = True
                while help_active:
                    mouse_pos = pygame.mouse.get_pos()
                    for button in buttons:
                        button.is_hovered = button.rect.collidepoint(mouse_pos)
                    self.draw_help()
                    pygame.display.flip()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            help_active = False
                        for button in buttons:
                            if button.handle_event(event):
                                if button.text == "🔙 Voltar":
                                    current_screen = "menu"
                                    help_active = False
                    self.clock.tick(60)

            elif current_screen == "game":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP and self.direction != "DOWN":
                            self.direction = "UP"
                        elif event.key == pygame.K_DOWN and self.direction != "UP":
                            self.direction = "DOWN"
                        elif event.key == pygame.K_LEFT and self.direction != "RIGHT":
                            self.direction = "LEFT"
                        elif event.key == pygame.K_RIGHT and self.direction != "LEFT":
                            self.direction = "RIGHT"
                        elif event.key == pygame.K_p:
                            self.paused = not self.paused
                        elif event.key == pygame.K_r and self.game_over:
                            self.reset_game()
                        elif event.key == pygame.K_m and self.game_over:
                            current_screen = "menu"

                if not self.paused and not self.game_over:
                    # Atualiza a posição da cobra
                    new_head = self.snake[0].copy()
                    if self.direction == "UP":
                        new_head[0] -= 1
                    elif self.direction == "DOWN":
                        new_head[0] += 1
                    elif self.direction == "LEFT":
                        new_head[1] -= 1
                    elif self.direction == "RIGHT":
                        new_head[1] += 1

                    # Verifica colisão com as bordas
                    if (new_head[0] < 0 or new_head[0] >= GRID_HEIGHT or
                        new_head[1] < 0 or new_head[1] >= GRID_WIDTH):
                        self.game_over = True
                        continue

                    # Verifica colisão com a própria cobra
                    if new_head in self.snake[1:]:
                        self.game_over = True
                        continue

                    # Verifica colisão com obstáculos
                    if new_head in self.obstacles:
                        self.game_over = True
                        continue

                    # Verifica colisão com a cobra da IA
                    if self.ai_snake and new_head in self.ai_snake:
                        self.game_over = True
                        continue

                    self.snake.insert(0, new_head)

                    # Verifica se comeu a comida
                    if new_head == self.food:
                        self.score += 1
                        self.food = self.generate_food()
                        if random.random() < 0.2:
                            self.powerups.append(self.generate_food())
                    else:
                        self.snake.pop()

                    # Atualiza a cobra da IA
                    if self.ai_snake:
                        ai_direction = self.get_ai_move()
                        ai_new_head = self.ai_snake[0].copy()
                        if ai_direction == "UP":
                            ai_new_head[0] -= 1
                        elif ai_direction == "DOWN":
                            ai_new_head[0] += 1
                        elif ai_direction == "LEFT":
                            ai_new_head[1] -= 1
                        elif ai_direction == "RIGHT":
                            ai_new_head[1] += 1

                        if (0 <= ai_new_head[0] < GRID_HEIGHT and
                            0 <= ai_new_head[1] < GRID_WIDTH and
                            ai_new_head not in self.ai_snake[1:] and
                            ai_new_head not in self.obstacles and
                            ai_new_head not in self.snake):
                            self.ai_snake.insert(0, ai_new_head)
                            if ai_new_head == self.food:
                                self.ai_score += 1
                                self.food = self.generate_food()
                            else:
                                self.ai_snake.pop()

                # Desenha o jogo
                self.screen.fill(self.current_theme["background"])
                self.draw_grid()
                self.draw_obstacles()
                self.draw_powerups()
                self.draw_food()
                self.draw_snake()
                self.draw_ai_snake()
                self.draw_score()

                if self.paused:
                    self.draw_pause()
                elif self.game_over:
                    self.draw_game_over()
                    self.save_record()

                pygame.display.flip()
                self.clock.tick(10)

        pygame.quit()

    def get_ai_move(self):
        if not self.ai_snake:
            return "RIGHT"

        head = self.ai_snake[0]
        possible_moves = []
        
        # Verifica movimentos possíveis
        if head[0] > 0 and [head[0]-1, head[1]] not in self.ai_snake and [head[0]-1, head[1]] not in self.obstacles:
            possible_moves.append(("UP", abs(head[0]-1 - self.food[0]) + abs(head[1] - self.food[1])))
        if head[0] < GRID_HEIGHT-1 and [head[0]+1, head[1]] not in self.ai_snake and [head[0]+1, head[1]] not in self.obstacles:
            possible_moves.append(("DOWN", abs(head[0]+1 - self.food[0]) + abs(head[1] - self.food[1])))
        if head[1] > 0 and [head[0], head[1]-1] not in self.ai_snake and [head[0], head[1]-1] not in self.obstacles:
            possible_moves.append(("LEFT", abs(head[0] - self.food[0]) + abs(head[1]-1 - self.food[1])))
        if head[1] < GRID_WIDTH-1 and [head[0], head[1]+1] not in self.ai_snake and [head[0], head[1]+1] not in self.obstacles:
            possible_moves.append(("RIGHT", abs(head[0] - self.food[0]) + abs(head[1]+1 - self.food[1])))
        
        if possible_moves:
            return min(possible_moves, key=lambda x: x[1])[0]
        return random.choice(["UP", "DOWN", "LEFT", "RIGHT"])

if __name__ == "__main__":
    game = SnakeGame()
    game.run() 