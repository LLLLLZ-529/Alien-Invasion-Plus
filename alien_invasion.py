import sys
import random
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
try:
    from sounds import load_sounds
except Exception:
    # 回退：若无法导入 sounds 包，提供空加载器以保证程序可运行
    def load_sounds():
        return {}
from boss import Boss
from powerup import PowerUp
from alien_bullet import AlienBullet

# 尝试导入外部 GameOverScreen（如不存在，使用简易内置实现）
try:
    from game_over_screen import GameOverScreen  # 如果你有单独文件
except Exception:
    class GameOverScreen:
        def __init__(self, screen, stats):
            self.screen = screen
            self.stats = stats
            self.font = pygame.font.Font(None, 72)
            self.small_font = pygame.font.Font(None, 36)

        def draw(self):
            self.screen.fill((0, 0, 0))
            go_text = self.font.render('GAME OVER', True, (255, 0, 0))
            go_rect = go_text.get_rect(center=(self.screen.get_width() // 2, 100))
            self.screen.blit(go_text, go_rect)
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
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return 'restart'
                    elif event.key == pygame.K_q:
                        return 'quit'
                elif event.type == pygame.QUIT:
                    return 'quit'
            return None


class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        # 限制游戏窗口不超过当前显示器，避免超出屏幕
        info = pygame.display.Info()
        max_w = max(640, info.current_w - 40)
        max_h = max(480, info.current_h - 120)
        # 允许在 settings 里预设，但不超过物理屏幕
        self.settings.screen_width = min(self.settings.screen_width, max_w)
        self.settings.screen_height = min(self.settings.screen_height, max_h)
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("Alien Invasion")

        # 载入持久化统计与音效
        self.stats = GameStats(self)  # 传入游戏实例以匹配 GameStats.__init__(ai_game)
        self.sounds = load_sounds()

        # 计分板与 UI
        self.sb = Scoreboard(self)
        self.play_button = Button(self, "Play")

        # 精灵 / 对象组
        # 创建飞船（兼容多种构造签名）
        ship_x = self.settings.screen_width // 2
        ship_y = self.settings.screen_height - 60
        try:
            self.ship = Ship(self.screen, ship_x, ship_y)
        except TypeError:
            try:
                self.ship = Ship(self, ship_x, ship_y)
            except TypeError:
                self.ship = Ship(self)
        # 兼容：确保 ship 拥有 screen 与 screen_rect，用于 center_ship() 等方法
        try:
            self.ship.screen = self.screen
            self.ship.screen_rect = self.screen.get_rect()
            # 确保 ship 能访问 settings，避免 Ship.update 中引用 self.settings 时报错
            self.ship.settings = self.settings
            # 优先使用项目中的 ship.bmp（或 images/ship.bmp），恢复原始飞船图片
            import os
            base = os.path.dirname(__file__)
            candidates = [os.path.join(base, 'ship.bmp'), os.path.join(base, 'images', 'ship.bmp')]
            for p in candidates:
                if os.path.exists(p):
                    try:
                        img = pygame.image.load(p).convert_alpha()
                        # 将加载的图片设为飞船图像并重新设置 rect（保持初始中心位置）
                        self.ship.image = img
                        self.ship.rect = self.ship.image.get_rect(center=(ship_x, ship_y))
                        break
                    except Exception:
                        continue
        except Exception:
            pass
        # 兼容性保障：确保常用属性存在，避免后续 AttributeError
        if not hasattr(self.ship, 'speed'):
            self.ship.speed = getattr(self.settings, 'ship_speed', 7)
        if not hasattr(self.ship, 'health'):
            self.ship.health = getattr(self.settings, 'ship_health', 3)
        if not hasattr(self.ship, 'max_health'):
            self.ship.max_health = getattr(self.settings, 'ship_health', 3)
        for flag in ('moving_left', 'moving_right', 'moving_up', 'moving_down', 'auto_fire'):
            if not hasattr(self.ship, flag):
                setattr(self.ship, flag, False)
        if not hasattr(self.ship, 'can_shoot'):
            self.ship.can_shoot = lambda now_ms: False
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        # 新增组
        self.alien_bullets = pygame.sprite.Group()
        self.boss_group = pygame.sprite.Group()
        self.boss_bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        self._create_fleet()

        # 初始化生命值图标
        self._init_life_icons()

        # 状态
        self.game_active = False
        self.game_over_screen = GameOverScreen(self.screen, self.stats)
        
        # 子弹发射控制
        self.last_shot_time = 0
        self.shoot_cooldown = 2000  # 最小发射间隔时间（毫秒）

    def _init_life_icons(self):
        """初始化生命值显示图标"""
        try:
            import os
            base = os.path.dirname(__file__)
            # 先尝试从images目录加载，如果不存在则尝试根目录
            ship_image_path = os.path.join(base, 'images', 'ship.bmp')
            if not os.path.exists(ship_image_path):
                ship_image_path = os.path.join(base, 'ship.bmp')
            
            original_ship = pygame.image.load(ship_image_path).convert_alpha()
            icon_size = 20
            self.life_icons = {
                'full': pygame.transform.scale(original_ship, (icon_size, icon_size)),
                'empty': None
            }
            
            # 创建失去生命值的版本（暗色版本）
            empty_ship = self.life_icons['full'].copy()
            empty_surface = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
            empty_surface.fill((50, 50, 50, 180))  # 暗灰色半透明
            empty_ship.blit(empty_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.life_icons['empty'] = empty_ship
            print(f"生命值图标初始化成功，使用图片: {ship_image_path}")
        except Exception as e:
            print(f"初始化生命值图标失败: {e}")
            self.life_icons = None

    def run_game(self):
        """Start the main loop for the game."""
        try:
            while True:
                self._check_events()

                if self.game_active:
                    now = pygame.time.get_ticks()

                    # 更新飞船（包含上下移动逻辑）
                    self.ship.update()

                    # 飞船自动连发支持（若 ship 提供此接口）
                    if getattr(self.ship, 'auto_fire', False):
                        if getattr(self.ship, 'can_shoot', None):
                            if self.ship.can_shoot(now):
                                # 兼容现有 Bullet(AlienInvasion) 构造：Bullet(self)
                                new_bullet = Bullet(self)
                                self.bullets.add(new_bullet)
                                if 'shoot' in self.sounds:
                                    try: self.sounds['shoot'].play()
                                    except Exception: pass
                        else:
                            # 旧接口：按住空格在事件处理时发射（keep for compatibility）
                            pass

                    # 敌方与玩家子弹、道具更新
                    self._update_bullets()
                    self._update_aliens()

                    # 降低外星人随机射击频率，使用可配置值
                    shoot_chance = getattr(self.settings, 'alien_shoot_chance', 0.0008)
                    if self.aliens and random.random() < shoot_chance:
                         shooter = random.choice(self.aliens.sprites())
                         self.alien_bullets.add(AlienBullet(shooter.rect.centerx, shooter.rect.bottom, speed=5))

                    # Boss 管理
                    if self.stats.level >= 4 and not self.boss_group:
                        # 触发 Boss 关（只在首次达到时生成）
                        boss = Boss(self.screen.get_width() // 2, 80)
                        # 使用外星人图标放大替代默认 Boss 外观（尽量复用 Alien 的图像）
                        try:
                            exemplar = Alien(self)
                            boss.image = pygame.transform.scale(exemplar.image, (220, 140))
                            boss.rect = boss.image.get_rect(center=(self.screen.get_width() // 2, 80))
                        except Exception:
                            pass
                        # 降低 Boss 射击频率（毫秒）
                        boss.shoot_delay = max(getattr(boss, 'shoot_delay', 800), 1400)
                        self.boss_group.add(boss)

                    # Boss 更新与射击
                    self.boss_group.update()
                    for boss in self.boss_group:
                        boss.try_shoot(self.boss_bullets, pygame.time.get_ticks())

                    # 更新外星人与 Boss 子弹与掉落
                    self.alien_bullets.update()
                    self.boss_bullets.update()
                    self.powerups.update()

                    # 处理敌方子弹击中飞船
                    self._check_ship_hit_by_enemy_bullets()

                    # 处理玩家拾取道具
                    self._check_powerup_collection()

                else:
                    # 游戏不处于激活状态 —— 若为 Game Over（无生命）则显示 Game Over 页面并处理输入
                    if self.stats.ships_left <= 0:
                        self.game_over_screen.draw()
                        action = self.game_over_screen.handle_input()
                        if action == 'restart':
                            self._restart_game()
                        elif action == 'quit':
                            # 保存高分并退出
                            self.stats.save_high_score()
                            pygame.quit()
                            sys.exit()
                    else:
                        # 未开始的界面（显示 Play 按钮），事件循环里已处理点击
                        pass

                self._update_screen()
                self.clock.tick(60)
        finally:
            # 确保退出时保存高分
            try:
                if hasattr(self, 'stats'):
                    self.stats.save_high_score()
            except Exception:
                pass

    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            # 处理窗口大小改变，动态调整屏幕与重新布局外星人
            if event.type == pygame.VIDEORESIZE:
                w, h = event.w, event.h
                self.settings.screen_width = max(320, w)
                self.settings.screen_height = max(240, h)
                # 重新创建可调整大小的屏幕
                self.screen = pygame.display.set_mode(
                    (self.settings.screen_width, self.settings.screen_height), pygame.RESIZABLE)
                # 重新布局：清理并按新尺寸创建阵列
                self.aliens.empty()
                self._create_fleet()
                if hasattr(self.ship, 'center_ship'):
                    self.ship.center_ship()
                continue

            # 如果处于 Game Over 且等待输入，则 handle_input 已在 run_game 中处理（避免重复）
            if event.type == pygame.QUIT:
                # 保存并退出
                self.stats.save_high_score()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

            # 将事件转发给 ship（支持上下移动与空格连发）
            if hasattr(self.ship, 'handle_event'):
                self.ship.handle_event(event)

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self._start_new_game()

    def _start_new_game(self):
        # Reset the game settings.
        self.settings.initialize_dynamic_settings()

        # Reset the game statistics.
        self.stats.reset_stats()
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()
        self.game_active = True

        # Get rid of any remaining bullets and aliens.
        self.bullets.empty()
        self.aliens.empty()
        self.alien_bullets.empty()
        self.boss_bullets.empty()
        self.boss_group.empty()
        self.powerups.empty()

        # Create a new fleet and center the ship.
        self._create_fleet()
        if hasattr(self.ship, 'center_ship'):
            self.ship.center_ship()

        # Hide the mouse cursor.
        pygame.mouse.set_visible(False)

    def _restart_game(self):
        """Restart from Game Over: 保持 high score 持久化，重置统计并重新开始。"""
        # 重置统计（GameStats.reset_stats 应设置 ships_left 和 score 等初始值）
        self.stats.reset_stats()
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()
        self.game_active = True

        # 清理
        self.bullets.empty()
        self.aliens.empty()
        self.alien_bullets.empty()
        self.boss_bullets.empty()
        self.boss_group.empty()
        self.powerups.empty()

        self._create_fleet()
        if hasattr(self.ship, 'center_ship'):
            self.ship.center_ship()
        pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_UP:
            if hasattr(self.ship, 'moving_up'):
                self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            if hasattr(self.ship, 'moving_down'):
                self.ship.moving_down = True
        elif event.key == pygame.K_q:
            # 保存并退出
            self.stats.save_high_score()
            pygame.quit()
            sys.exit()
        elif event.key == pygame.K_SPACE:
            # 如果使用新 ship.auto_fire 机制，按下将会被 ship.handle_event 处理；
            # 若使用旧逻辑则立即发射一次。
            if not getattr(self.ship, 'auto_fire', False):
                self._fire_bullet()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_UP:
            if hasattr(self.ship, 'moving_up'):
                self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:
            if hasattr(self.ship, 'moving_down'):
                self.ship.moving_down = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        current_time = pygame.time.get_ticks()
        
        # 检查发射间隔时间
        if current_time - self.last_shot_time < self.shoot_cooldown:
            return
        
        # 更新发射时间，无论是否成功发射
        self.last_shot_time = current_time
            
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            if 'shoot' in self.sounds:
                try: self.sounds['shoot'].play()
                except Exception: pass

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()
        self._check_bullet_boss_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions and 触发掉落。"""
        collisions = pygame.sprite.groupcollide(
                self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                # 每次击落有小概率生成道具
                for alien in aliens:
                    if random.random() < 0.08:
                        self.powerups.add(PowerUp(alien.rect.centerx, alien.rect.centery))
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens and not self.boss_group:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()

    def _check_bullet_boss_collisions(self):
        """玩家子弹击中 Boss 处理（若存在 Boss）。"""
        if not self.boss_group:
            return
        for bullet in self.bullets.copy():
            hit_boss = pygame.sprite.spritecollideany(bullet, self.boss_group)
            if hit_boss:
                # 假设 Boss 有 health 属性
                try:
                    hit_boss.health -= 10  # 子弹伤害值，可调整或读取 bullet 属性
                except Exception:
                    pass
                self.bullets.remove(bullet)
                if 'explosion' in self.sounds:
                    try: self.sounds['explosion'].play()
                    except Exception: pass
                if getattr(hit_boss, 'health', 1) <= 0:
                    hit_boss.kill()
                    # 击败 Boss 后清理并提升等级
                    self.boss_group.empty()
                    self.boss_bullets.empty()
                    self.stats.level += 1
                    self.sb.prep_level()
                    self.settings.increase_speed()

    def _update_aliens(self):
        """Check if the fleet is at an edge, then update positions."""
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break

    def _check_ship_hit_by_enemy_bullets(self):
        """检查敌方子弹击中飞船（alien_bullets / boss_bullets）并处理护盾与生命值。"""
        hit_any = False
        # 外星人子弹
        collisions = pygame.sprite.spritecollide(self.ship, self.alien_bullets, True)
        if collisions:
            hit_any = True
        # Boss 子弹
        collisions2 = pygame.sprite.spritecollide(self.ship, self.boss_bullets, True)
        if collisions2:
            hit_any = True

        if hit_any:
            # 计算伤害：默认 1，每次被击触发
            damage = 1
            if hasattr(self.ship, 'shield') and getattr(self.ship, 'shield', None):
                try:
                    damage = self.ship.shield.apply_damage(damage)
                except Exception:
                    pass
            # 若 ship 管理 health 属性
            if hasattr(self.ship, 'health'):
                try:
                    self.ship.health -= damage
                except Exception:
                    pass
            # 如果生命耗尽 -> 处理被击
            if not hasattr(self.ship, 'health') or getattr(self.ship, 'health', 1) <= 0:
                self._ship_hit()
            else:
                # 播放受击音效
                if 'hit' in self.sounds:
                    try: self.sounds['hit'].play()
                    except Exception: pass

    def _check_powerup_collection(self):
        hits = pygame.sprite.spritecollide(self.ship, self.powerups, True)
        for pu in hits:
            if pu.kind == 'shield':
                if hasattr(self.ship, 'shield') and self.ship.shield:
                    self.ship.shield.activate()
            elif pu.kind == 'heal':
                if hasattr(self.ship, 'health'):
                    max_hp = getattr(self.ship, 'max_health', 3)
                    self.ship.health = min(max_hp, self.ship.health + 1)

    def _ship_hit(self):
        """Respond to the ship being hit by an alien or losing all health."""
        if self.stats.ships_left > 0:
            # Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()
            self.alien_bullets.empty()
            self.boss_bullets.empty()
            self.boss_group.empty()
            self.powerups.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            if hasattr(self.ship, 'center_ship'):
                self.ship.center_ship()

            # Pause.
            sleep(0.5)
        else:
            # Game over: 保持 high score 写入由 finally / 主流程保证
            self.game_active = False
            pygame.mouse.set_visible(True)

    def _create_fleet(self):
        """Create the fleet of aliens in clear rows/columns based on current screen size."""
        # Use spacing computed from an exemplar alien to produce neat rows/columns.
        exemplar = Alien(self)
        alien_w, alien_h = exemplar.rect.size

        # horizontal layout: leave margins at left/right
        available_space_x = self.settings.screen_width - 2 * alien_w
        if available_space_x < alien_w:
            cols = 1
        else:
            cols = available_space_x // (2 * alien_w)

        # vertical layout: leave top margin and bottom buffer for ship
        available_space_y = self.settings.screen_height - 3 * alien_h
        if available_space_y < alien_h:
            rows = 1
        else:
            rows = available_space_y // (2 * alien_h)

        # create grid
        for row in range(int(rows)):
            for col in range(int(cols)):
                x = alien_w + 2 * alien_w * col
                y = alien_h + 2 * alien_h * row
                self._create_alien(x, y)
        # if none created (tiny screen), ensure at least one
        if not self.aliens:
            self._create_alien(self.settings.screen_width // 2, alien_h)

    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the fleet."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction() 
                self.aliens.draw(self.screen)
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        # 使用更小的下移步长以实现“慢慢向下移动”的感觉（按 settings.fleet_drop_speed 缩放）
        drop_amount = max(1, int(self.settings.fleet_drop_speed * 0.5))
        for alien in self.aliens.sprites():
            alien.rect.y += drop_amount
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        # 如果是Game Over状态，不绘制游戏元素，只显示Game Over页面
        if not self.game_active and self.stats.ships_left <= 0:
            pygame.display.flip()
            return

        # 背景
        self.screen.fill(self.settings.bg_color)

        # 玩家子弹
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        # 玩家飞船与外星人
        self.ship.blitme()
        self.aliens.draw(self.screen)

        # 敌方子弹、Boss 子弹、Boss、道具
        self.alien_bullets.draw(self.screen)
        self.boss_bullets.draw(self.screen)
        self.boss_group.draw(self.screen)
        self.powerups.draw(self.screen)

        # 显示生命值 - 使用ship.bmp图片
        if hasattr(self.ship, 'health') and self.life_icons:
            max_hp = getattr(self.ship, 'max_health', getattr(self.settings, 'ship_health', 3))
            current_hp = getattr(self.ship, 'health', max_hp)
            
            # 绘制生命值图标
            icon_spacing = 25
            start_x = 10
            start_y = 10
            
            for i in range(max_hp):
                x = start_x + i * icon_spacing
                if i < current_hp:
                    # 存在的生命值 - 完整飞船
                    self.screen.blit(self.life_icons['full'], (x, start_y))
                else:
                    # 失去的生命值 - 暗色飞船
                    self.screen.blit(self.life_icons['empty'], (x, start_y))

        # 分数与 Play 按钮
        self.sb.show_score()
        if not self.game_active and self.stats.ships_left > 0:
            self.play_button.draw_button()

        pygame.display.flip()


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()