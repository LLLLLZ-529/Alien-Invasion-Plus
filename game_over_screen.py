import pygame

class GameOverScreen:
    """简洁的 Game Over 页面（可被 alien_invasion.py 导入使用）。"""
    def __init__(self, screen, stats):
        self.screen = screen
        self.stats = stats
        self.font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 36)

    def draw(self):
        """绘制 Game Over 界面并刷新显示。"""
        self.screen.fill((0, 0, 0))

        game_over_text = self.font.render('GAME OVER', True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(self.screen.get_width() // 2, 100))
        self.screen.blit(game_over_text, game_over_rect)

        score_text = self.small_font.render(f'Score: {self.stats.score}', True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.screen.get_width() // 2, 250))
        self.screen.blit(score_text, score_rect)

        high_text = self.small_font.render(f'High Score: {self.stats.high_score}', True, (255, 255, 0))
        high_rect = high_text.get_rect(center=(self.screen.get_width() // 2, 320))
        self.screen.blit(high_text, high_rect)

        restart_text = self.small_font.render('Press SPACE to Restart or Q to Quit', True, (0, 255, 0))
        restart_rect = restart_text.get_rect(center=(self.screen.get_width() // 2, 450))
        self.screen.blit(restart_text, restart_rect)

    def handle_input(self):
        """处理 Game Over 时的按键输入：返回 'restart' 或 'quit' 或 None。"""
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return 'restart'
                elif event.key == pygame.K_q:
                    return 'quit'
            elif event.type == pygame.QUIT:
                return 'quit'
        return None