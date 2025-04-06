import pygame
import random
import sys
import ctypes
import math
from pygame.locals import *

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
BLOCK_SIZE = 40  # 减小色块大小
MARGIN = 10
MAX_GUESSES = 7  # 将最大猜测次数从10改为7
COLORS = [
    (220, 60, 60),    # 红色 - 更柔和的红色
    (80, 180, 80),    # 绿色 - 更自然的绿色
    (70, 100, 220),   # 蓝色 - 更柔和的蓝色
    (230, 200, 50),   # 黄色 - 更温暖的黄色
    (180, 80, 200),   # 紫色 - 更柔和的紫色
    (60, 190, 200),   # 青色 - 更自然的青色
    (240, 130, 40)    # 橙色 - 更自然的橙色
]
COLOR_NAMES = ["红", "绿", "蓝", "黄", "紫", "青", "橙"]

# 反馈颜色
GREEN = (80, 180, 80)      # 颜色和位置都正确 - 使用与绿色相同的颜色
WHITE = (240, 240, 240)    # 颜色正确但位置错误 - 稍微柔和的白色
GRAY = (60, 60, 60)        # 颜色错误 - 稍微亮一点的灰色

# 界面颜色
BG_COLOR = (40, 44, 52)    # 更现代的深色背景
TEXT_COLOR = (240, 240, 240)  # 稍微柔和的白色文字
BUTTON_COLOR = (75, 111, 166)  # 更鲜艳的蓝色
BUTTON_HOVER_COLOR = (95, 131, 196)
BUTTON_TEXT_COLOR = (240, 240, 240)  # 稍微柔和的白色文字

# 烟花粒子系统类
class Firework:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.particles = []
        self.alive = True
        self.create_particles()
    
    def create_particles(self):
        # 创建粒子 - 优化粒子数量，减少不必要的计算
        num_particles = random.randint(25, 40)  # 略微减少粒子数量以提高性能
        self.particles = []
        
        for _ in range(num_particles):
            # 随机速度和方向
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)  # 略微减小速度范围
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # 随机颜色变化 - 使用更高效的颜色计算
            r, g, b = self.color
            color_var = (
                max(0, min(255, r + random.randint(-20, 20))),
                max(0, min(255, g + random.randint(-20, 20))),
                max(0, min(255, b + random.randint(-20, 20)))
            )
            
            # 添加粒子 - 使用更合理的生命周期和大小
            self.particles.append({
                'x': self.x,
                'y': self.y,
                'vx': vx,
                'vy': vy,
                'color': color_var,
                'alpha': 255,  # 初始透明度
                'size': random.randint(2, 4),  # 粒子大小
                'life': random.uniform(0.5, 1.2)  # 略微减少最大寿命
            })
    
    def update(self):
        # 更新所有粒子 - 使用更高效的列表推导式
        new_particles = []
        for particle in self.particles:
            # 更新位置
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            # 添加重力效果
            particle['vy'] += 0.1
            # 减少透明度和寿命
            particle['alpha'] -= 4  # 略微加快消失速度
            particle['life'] -= 0.025  # 略微加快生命消耗
            
            # 只保留活着的粒子
            if particle['alpha'] > 0 and particle['life'] > 0:
                new_particles.append(particle)
        
        # 更新粒子列表
        self.particles = new_particles
        
        # 检查烟花是否还活着
        self.alive = len(self.particles) > 0
    
    def draw(self, screen):
        # 绘制所有粒子 - 使用批量绘制提高性能
        for particle in self.particles:
            # 创建带透明度的颜色
            r, g, b = particle['color']
            color_with_alpha = (r, g, b, particle['alpha'])
            # 创建表面
            size = particle['size']
            particle_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            # 绘制粒子
            pygame.draw.circle(particle_surface, color_with_alpha, (size//2, size//2), size//2)
            # 绘制到屏幕
            screen.blit(particle_surface, (particle['x'] - size//2, particle['y'] - size//2))

# 烟花管理器类
class FireworkManager:
    def __init__(self):
        self.fireworks = []
        self.last_spawn_time = 0
        self.active = False
        self.max_fireworks = 15  # 限制最大烟花数量，防止性能问题
    
    def start_celebration(self):
        self.active = True
        self.last_spawn_time = pygame.time.get_ticks()
        # 立即添加几个烟花，使效果更加明显
        for _ in range(3):
            self.add_random_firework()
    
    def stop_celebration(self):
        self.active = False
        # 清空所有烟花
        self.fireworks.clear()
    
    def update(self):
        # 更新现有烟花 - 使用更高效的方法
        # 创建新列表存储活着的烟花
        active_fireworks = []
        
        # 更新所有烟花并只保留活着的
        for firework in self.fireworks:
            firework.update()
            if firework.alive:
                active_fireworks.append(firework)
        
        # 更新烟花列表
        self.fireworks = active_fireworks
        
        # 如果庆祝活动激活且烟花数量未超过限制，添加新烟花
        if self.active and len(self.fireworks) < self.max_fireworks:
            current_time = pygame.time.get_ticks()
            # 每隔一段时间添加新烟花
            if current_time - self.last_spawn_time > 250:  # 稍微减少间隔，使效果更连贯
                self.add_random_firework()
                self.last_spawn_time = current_time
    
    def add_random_firework(self):
        # 随机位置 - 使用更合理的范围
        x = random.randint(150, SCREEN_WIDTH - 150)
        y = random.randint(100, SCREEN_HEIGHT - 250)
        # 随机颜色 - 使用更鲜艳的颜色
        color = random.choice(COLORS)
        # 随机调整颜色亮度，使烟花更加多样化
        brightness = random.uniform(0.9, 1.2)
        bright_color = tuple(min(255, int(c * brightness)) for c in color)
        # 添加烟花
        self.fireworks.append(Firework(x, y, bright_color))
    
    def draw(self, screen):
        # 绘制所有烟花 - 按照y坐标排序，确保正确的深度效果
        for firework in sorted(self.fireworks, key=lambda f: f.y):
            firework.draw(screen)

class Game:
    def reset_game(self, difficulty='easy', num_colors=4):
        """初始化游戏状态"""
        self.difficulty = difficulty
        self.num_colors = num_colors
        self.code_length = 4
        
        # 生成密码 - 确保颜色不重复
        self._generate_secret_code()
            
        # 重置游戏状态
        self.guesses = []
        self.feedbacks = []
        self.current_guess = [-1] * self.code_length
        self.current_position = 0
        self.game_over = False
        self.win = False
        
        # 停止烟花效果
        self.firework_manager.stop_celebration()
        
        # 困难模式下，添加随机猜测
        if difficulty == 'hard':
            self.add_random_guesses()
        
        # 调试信息
        print(f"生成的密码: {[COLOR_NAMES[i] for i in self.secret_code]}")
    
    def _generate_secret_code(self):
        """生成游戏密码 - 确保颜色不重复"""
        available_colors = list(range(self.num_colors))
        self.secret_code = []
        
        for _ in range(self.code_length):
            if not available_colors:  # 如果可用颜色用完了，重新填充
                available_colors = list(range(self.num_colors))
            
            color_idx = random.choice(available_colors)
            self.secret_code.append(color_idx)
            available_colors.remove(color_idx)  # 移除已使用的颜色
    
    def add_random_guesses(self):
        """为困难模式添加5次随机猜测"""
        attempts = 0
        max_attempts = 100  # 防止无限循环
        target_guesses = 5  # 目标随机猜测数量
        
        while len(self.guesses) < target_guesses and attempts < max_attempts:
            attempts += 1
            
            # 生成一个随机猜测（确保颜色不重复）
            random_guess = self._generate_random_guess()
            
            # 检查这个猜测是否已经存在
            if random_guess in self.guesses:
                continue
                
            # 获取反馈
            feedback = self.check_guess(random_guess)
            
            # 确保没有超过2个绿色反馈，且绿色+白色不超过3个
            green_count = feedback.count(GREEN)
            white_count = feedback.count(WHITE)
            
            if green_count <= 2 and (green_count + white_count) <= 3:
                self.guesses.append(random_guess)
                self.feedbacks.append(feedback)
        
        print(f"困难模式：已添加 {len(self.guesses)} 次随机猜测")
    
    def _generate_random_guess(self):
        """生成一个随机猜测（确保颜色不重复）"""
        available_colors = list(range(self.num_colors))
        random_guess = []
        
        for _ in range(self.code_length):
            if not available_colors:  # 如果可用颜色用完了，重新填充
                available_colors = list(range(self.num_colors))
            
            color_idx = random.choice(available_colors)
            random_guess.append(color_idx)
            available_colors.remove(color_idx)
            
        return random_guess

    def __init__(self):
        # 初始化游戏窗口
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("色块解谜游戏")
        self.clock = pygame.time.Clock()
        
        # 初始化烟花管理器
        self.firework_manager = FireworkManager()
        
        # 加载字体
        self._load_fonts()
        
        # 初始化游戏状态
        self.show_instructions = True
        self.start_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 500, 200, 50)
        
        # 预渲染常用文本以提高性能
        self.cached_text = {}
        self._prerender_common_text()
        
        # 初始化游戏
        self.reset_game('easy', 4)
        
        # 添加调试信息
        print("游戏初始化完成，应显示指令界面")
    
    def _load_fonts(self):
        """加载游戏字体"""
        try:
            # 尝试使用系统中可能存在的中文字体
            font_options = ['simhei', 'simsun', 'msyh', 'simkai', 'kaiti']
            font_found = False
            
            for font_name in font_options:
                if font_name in pygame.font.get_fonts():
                    self.font = pygame.font.SysFont(font_name, 24)
                    self.small_font = pygame.font.SysFont(font_name, 18)
                    self.title_font = pygame.font.SysFont(font_name, 48)
                    font_found = True
                    print(f"使用字体: {font_name}")
                    break
            
            if not font_found:
                # 如果没有找到中文字体，使用默认字体
                self.font = pygame.font.Font(None, 24)
                self.small_font = pygame.font.Font(None, 18)
                self.title_font = pygame.font.Font(None, 48)
        except Exception as e:
            print(f"加载字体出错: {e}")
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)
            self.title_font = pygame.font.Font(None, 48)
    
    def _prerender_common_text(self):
        """预渲染常用文本以提高性能"""
        # 游戏标题
        self.cached_text['title'] = self.title_font.render("色块解谜游戏", True, (255, 215, 0))
        
        # 游戏简介
        self.cached_text['intro'] = self.font.render("猜出隐藏的颜色组合，挑战你的逻辑思维！", True, (200, 200, 200))
        
        # 操作说明
        instructions = [
            "游戏操作说明:",
            "1. 左键点击色块可以向后循环选择颜色",
            "2. 右键点击色块可以向前循环选择颜色",
            "3. 使用键盘数字键1-7可以直接选择对应颜色",
            "4. 空格键或0键可以清空当前色块",
            "5. 左右方向键可以移动选择位置",
            "6. 回车键可以提交猜测"
        ]
        
        self.cached_text['instructions'] = []
        for line in instructions:
            self.cached_text['instructions'].append(self.small_font.render(line, True, (200, 200, 200)))
        
        # 按钮文本
        self.cached_text['start_button'] = self.font.render("开始游戏", True, (255, 255, 255))
        self.cached_text['submit_button'] = self.small_font.render("提交(Enter)", True, BUTTON_TEXT_COLOR)
        self.cached_text['reset_button'] = self.small_font.render("再来一局(R)", True, BUTTON_TEXT_COLOR)
        self.cached_text['menu_button'] = self.small_font.render("主菜单(Esc)", True, BUTTON_TEXT_COLOR)
        
        # 颜色选择器标题
        self.cached_text['color_selector'] = self.small_font.render("可选颜色:", True, TEXT_COLOR)

    def draw(self):
        # 清除屏幕
        self.screen.fill(BG_COLOR)
        
        if self.show_instructions:
            # 绘制指令界面
            return self._draw_instructions()
        else:
            # 绘制游戏界面
            return self._draw_game()
    
    def _draw_instructions(self):
        """绘制指令界面"""
        # 使用预渲染的文本
        # 游戏标题
        title_rect = self.cached_text['title'].get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(self.cached_text['title'], title_rect)
        
        # 游戏简介
        intro_rect = self.cached_text['intro'].get_rect(center=(SCREEN_WIDTH//2, 160))
        self.screen.blit(self.cached_text['intro'], intro_rect)
        
        # 游戏操作说明
        for i, text in enumerate(self.cached_text['instructions']):
            self.screen.blit(text, (50, 190 + i * 25))
        
        # 绘制开始游戏按钮 - 使用圆角矩形
        button_color = (100, 100, 255) if self.start_button.collidepoint(pygame.mouse.get_pos()) else (80, 80, 200)
        pygame.draw.rect(self.screen, button_color, self.start_button, border_radius=10)
        pygame.draw.rect(self.screen, (150, 150, 255), self.start_button, 2, border_radius=10)  # 添加边框
        
        # 使用预渲染的按钮文本
        start_text = self.cached_text['start_button']
        self.screen.blit(start_text, (self.start_button.centerx - start_text.get_width()//2, 
                                    self.start_button.centery - start_text.get_height()//2))
        
        # 在说明界面绘制难度选择
        difficulty_buttons = self.draw_difficulty_buttons()
        
        # 强制更新显示
        pygame.display.update()
        return difficulty_buttons, None, None, None
        
    def _draw_game(self):
        """绘制游戏界面"""
        # 绘制游戏状态
        self.draw_game_state()
        
        # 绘制历史猜测
        self._draw_history_guesses()
        
        # 绘制当前猜测
        if not self.game_over and len(self.guesses) < MAX_GUESSES:
            self._draw_current_guess()
        
        # 绘制颜色选择器
        self.draw_color_selector()
        
        # 绘制控制按钮
        submit_rect, reset_rect, menu_rect = self.draw_buttons()
        
        # 绘制烟花效果
        if self.win:
            self.firework_manager.draw(self.screen)
        
        pygame.display.flip()
        return [], submit_rect, reset_rect, menu_rect
    
    def _draw_history_guesses(self):
        """绘制历史猜测"""
        for i, (guess, feedback) in enumerate(zip(self.guesses, self.feedbacks)):
            y = 100 + i * (BLOCK_SIZE + 20)
            
            # 绘制猜测序号
            num_text = self.font.render(f"{i+1}.", True, TEXT_COLOR)
            self.screen.blit(num_text, (MARGIN, y + BLOCK_SIZE//2 - num_text.get_height()//2))
            
            # 绘制猜测色块
            for j, color_idx in enumerate(guess):
                self.draw_block(color_idx, MARGIN + 30 + j * (BLOCK_SIZE + MARGIN), y)
            
            # 绘制反馈
            self.draw_feedback(feedback, MARGIN + 30, y, self.difficulty == 'easy')
    
    def _draw_current_guess(self):
        """绘制当前猜测"""
        current_y = 100 + len(self.guesses) * (BLOCK_SIZE + 20)
        
        # 绘制猜测序号
        num_text = self.font.render(f"{len(self.guesses)+1}.", True, TEXT_COLOR)
        self.screen.blit(num_text, (MARGIN, current_y + BLOCK_SIZE//2 - num_text.get_height()//2))
        
        # 绘制当前猜测的色块
        for i, color_idx in enumerate(self.current_guess):
            # 高亮显示当前选择位置 - 使用圆角矩形
            if i == self.current_position:
                pygame.draw.rect(self.screen, (100, 100, 255), 
                               (MARGIN + 30 + i * (BLOCK_SIZE + MARGIN) - 3, 
                                current_y - 3, 
                                BLOCK_SIZE + 6, 
                                BLOCK_SIZE + 6), 
                               3, border_radius=10)
            self.draw_block(color_idx, MARGIN + 30 + i * (BLOCK_SIZE + MARGIN), current_y)
    
    def run(self):
        """游戏主循环"""
        running = True
        print(f"游戏开始运行，指令界面状态: {self.show_instructions}")
        
        # 添加确认对话框状态变量
        self.show_confirm_dialog = False
        
        # 主游戏循环
        while running:
            # 绘制界面
            if self.show_instructions:
                self.difficulty_buttons, _, _, _ = self.draw()
            else:
                _, self.submit_rect, self.reset_rect, self.menu_rect = self.draw()
                
                # 更新烟花效果 - 只在胜利时更新
                if self.win:
                    self.firework_manager.update()
                
                # 如果需要显示确认对话框，绘制它
                if self.show_confirm_dialog:
                    self.draw_confirm_dialog()
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    running = self._handle_key_event(event)
                elif event.type == MOUSEBUTTONDOWN:
                    self._handle_mouse_event(event)
            
            # 控制帧率
            self.clock.tick(30)
        
        # 游戏退出清理
        pygame.quit()
        sys.exit()
    
    def _handle_key_event(self, event):
        """处理键盘事件"""
        # 处理ESC键
        if event.key == K_ESCAPE:
            if not self.show_instructions and not self.show_confirm_dialog:
                # 显示确认对话框
                self.show_confirm_dialog = True
            elif self.show_confirm_dialog:
                # 如果确认对话框已显示，ESC键取消
                self.show_confirm_dialog = False
            return True
        
        # 处理确认对话框的按键
        if self.show_confirm_dialog:
            if event.key == K_y or event.key == K_RETURN:  # Y键或回车确认
                self.show_instructions = True
                self.show_confirm_dialog = False
            elif event.key == K_n:  # N键取消
                self.show_confirm_dialog = False
            return True
        
        # 处理R键重置游戏
        if event.key in (114, 82):  # R键，不区分大小写
            if not self.show_instructions:
                self.reset_game(self.difficulty, self.num_colors)
            return True
        
        # 游戏进行中的按键处理
        if not self.game_over and len(self.guesses) < MAX_GUESSES and not self.show_instructions:
            # 处理方向键
            if event.key == K_LEFT:
                self.current_position = (self.current_position - 1) % self.code_length
            elif event.key == K_RIGHT:
                self.current_position = (self.current_position + 1) % self.code_length
            # 处理数字键选择颜色
            elif event.key in [K_1, K_2, K_3, K_4, K_5, K_6, K_7]:
                self._handle_color_selection(event.key - K_1)
            # 处理清空键
            elif event.key == K_0 or event.key == K_SPACE:
                self.current_guess[self.current_position] = -1
            # 处理回车键提交
            elif event.key == K_RETURN:
                if -1 not in self.current_guess:
                    self.process_guess()
        
        return True
    
    def _handle_color_selection(self, color_idx):
        """处理颜色选择"""
        if color_idx < self.num_colors:
            # 检查其他位置是否有相同颜色，如果有则清空
            for i in range(self.code_length):
                if i != self.current_position and self.current_guess[i] == color_idx:
                    self.current_guess[i] = -1  # 清空其他位置的相同颜色
            # 设置当前位置的颜色
            self.current_guess[self.current_position] = color_idx
    
    def _handle_mouse_event(self, event):
        """处理鼠标事件"""
        mouse_x, mouse_y = event.pos
        
        # 处理确认对话框的点击
        if self.show_confirm_dialog:
            self._handle_confirm_dialog_click(mouse_x, mouse_y)
            return
        
        # 处理指令界面的点击
        if self.show_instructions:
            self._handle_instructions_click(mouse_x, mouse_y)
        else:
            # 处理游戏界面的点击
            self._handle_game_click(mouse_x, mouse_y, event.button)
    
    def _handle_confirm_dialog_click(self, mouse_x, mouse_y):
        """处理确认对话框的点击"""
        # 获取确认对话框的按钮位置
        dialog_width, dialog_height = 350, 170  # 使用更新后的尺寸
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
        
        # 确认按钮
        confirm_rect = pygame.Rect(dialog_x + 70, dialog_y + 120, 80, 30)
        # 取消按钮
        cancel_rect = pygame.Rect(dialog_x + 200, dialog_y + 120, 80, 30)
        
        if confirm_rect.collidepoint(mouse_x, mouse_y):
            self.show_instructions = True
            self.show_confirm_dialog = False
        elif cancel_rect.collidepoint(mouse_x, mouse_y):
            self.show_confirm_dialog = False
    
    def _handle_instructions_click(self, mouse_x, mouse_y):
        """处理指令界面的点击"""
        # 处理开始游戏按钮点击
        if self.start_button.collidepoint(mouse_x, mouse_y):
            self.show_instructions = False
            # 使用当前选择的难度和颜色数量重置游戏
            self.reset_game(self.difficulty, self.num_colors)
        
        # 处理难度选择
        for difficulty, rect in self.difficulty_buttons:
            if rect.collidepoint(mouse_x, mouse_y):
                if isinstance(difficulty, str):
                    self.difficulty = difficulty
                else:
                    self.num_colors = difficulty
    
    def _handle_game_click(self, mouse_x, mouse_y, button):
        """处理游戏界面的点击"""
        # 如果游戏已结束，只处理按钮点击
        if self.game_over or len(self.guesses) >= MAX_GUESSES:
            self._handle_button_click(mouse_x, mouse_y)
            return
        
        # 处理颜色选择器点击
        selector_y = SCREEN_HEIGHT - 100
        for i in range(self.num_colors):
            x = MARGIN + i * (BLOCK_SIZE + MARGIN)
            color_rect = pygame.Rect(x, selector_y, BLOCK_SIZE, BLOCK_SIZE)
            if color_rect.collidepoint(mouse_x, mouse_y):
                self._handle_color_selection(i)
                return
        
        # 处理当前色块点击
        current_y = 100 + len(self.guesses) * (BLOCK_SIZE + 20)
        for i in range(self.code_length):
            block_x = MARGIN + 30 + i * (BLOCK_SIZE + MARGIN)
            block_rect = pygame.Rect(block_x, current_y, BLOCK_SIZE, BLOCK_SIZE)
            if block_rect.collidepoint(mouse_x, mouse_y):
                self.current_position = i
                self._cycle_colors(i, button == 3)  # 右键为3，左键为1
                return
        
        # 处理按钮点击
        self._handle_button_click(mouse_x, mouse_y)
    
    def _cycle_colors(self, position, reverse=False):
        """循环选择颜色"""
        # 获取当前已使用的颜色（排除当前位置的颜色）
        used_colors = []
        for j, color in enumerate(self.current_guess):
            if j != position and color != -1:
                used_colors.append(color)
        
        # 获取所有可用颜色（包括空白色）
        available_colors = [-1]  # 首先添加空白色
        for color_idx in range(self.num_colors):
            if color_idx not in used_colors:
                available_colors.append(color_idx)
        
        # 找到当前颜色在可用颜色列表中的位置
        current_color = self.current_guess[position]
        try:
            current_index = available_colors.index(current_color)
        except ValueError:
            current_index = -1
        
        # 根据方向选择颜色滚动方向
        if reverse:  # 向前滚动
            next_index = (current_index - 1) % len(available_colors)
        else:  # 向后滚动
            next_index = (current_index + 1) % len(available_colors)
        
        self.current_guess[position] = available_colors[next_index]
    
    def _handle_button_click(self, mouse_x, mouse_y):
        """处理按钮点击"""
        if hasattr(self, 'submit_rect') and self.submit_rect.collidepoint(mouse_x, mouse_y):
            if -1 not in self.current_guess:
                self.process_guess()
        elif hasattr(self, 'reset_rect') and self.reset_rect.collidepoint(mouse_x, mouse_y):
            self.reset_game(self.difficulty, self.num_colors)
        elif hasattr(self, 'menu_rect') and self.menu_rect.collidepoint(mouse_x, mouse_y):
            # 返回主菜单
            self.show_instructions = True

    def process_guess(self):
        """处理猜测结果的通用逻辑"""
        feedback = self.check_guess(self.current_guess)
        self.guesses.append(self.current_guess.copy())
        self.feedbacks.append(feedback)
        
        # 检查胜利条件
        if feedback.count(GREEN) == self.code_length:
            self.win = True
            self.game_over = True
            # 触发烟花效果
            self.firework_manager.start_celebration()
        elif len(self.guesses) >= MAX_GUESSES:
            self.game_over = True
            
        # 重置当前猜测
        self.current_guess = [-1] * self.code_length
        
        # 在简单模式下，如果某个位置猜对了，自动填入该颜色
        if self.difficulty == 'easy' and not self.game_over:
            for i, color in enumerate(feedback):
                if color == GREEN:  # 如果这个位置是绿色（完全正确）
                    self.current_guess[i] = self.guesses[-1][i]  # 使用上一次猜测的颜色
        
        self.current_position = 0
        # 删除重复的行
        # self.current_position = 0
    
    def draw_difficulty_buttons(self):
        """绘制难度选择按钮"""
        buttons = []
        y = 400  # 将游戏模式选择按钮向上移动到400
        
        # 模式选择按钮
        mode_text = self.small_font.render("游戏模式:", True, TEXT_COLOR)
        self.screen.blit(mode_text, (50, y))
        
        # 添加困难模式选项
        for i, mode in enumerate(["简单", "中等", "困难"]):
            rect = pygame.Rect(150 + i*100, y, 80, 30)  # 调整宽度以适应三个按钮
            # 确定当前难度对应的值
            mode_value = 'easy' if i == 0 else ('medium' if i == 1 else 'hard')
            
            # 增大选中与未选中状态的颜色差异
            if self.difficulty == mode_value:
                color = (120, 180, 255)  # 更亮的蓝色表示选中
                border_color = (180, 220, 255)  # 更亮的边框
                border_width = 2
            else:
                color = (60, 90, 130)  # 更暗的蓝色表示未选中
                border_color = (100, 130, 170)
                border_width = 1
                
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius=8)
            text = self.small_font.render(mode, True, BUTTON_TEXT_COLOR)
            self.screen.blit(text, (rect.x + (rect.width - text.get_width())//2, rect.y + 5))
            buttons.append((mode_value, rect))
        
        # 颜色数量选择按钮
        y += 50  # 增加间距，从50改为70，避免按钮重叠
        num_text = self.small_font.render("颜色数量:", True, TEXT_COLOR)
        self.screen.blit(num_text, (50, y))
        
        for i, num in enumerate([4, 5, 6, 7]):
            rect = pygame.Rect(150 + i*70, y, 50, 30)
            # 增大选中与未选中状态的颜色差异
            if self.num_colors == num:
                color = (120, 180, 255)  # 更亮的蓝色表示选中
                border_color = (180, 220, 255)  # 更亮的边框
                border_width = 2
            else:
                color = (60, 90, 130)  # 更暗的蓝色表示未选中
                border_color = (100, 130, 170)
                border_width = 1
                
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius=8)
            text = self.small_font.render(str(num), True, BUTTON_TEXT_COLOR)
            self.screen.blit(text, (rect.x + 15, rect.y + 5))
            buttons.append((num, rect))
        
        return buttons

    def check_guess(self, guess):
        """检查猜测结果，返回反馈列表"""
        # 在简单模式下，反馈需要与位置对应
        if self.difficulty == 'easy':
            feedback = [GRAY] * self.code_length
            
            # 创建临时列表以跟踪已匹配的位置
            secret_copy = self.secret_code.copy()
            guess_copy = guess.copy()
            
            # 首先检查位置和颜色都正确的
            for i in range(self.code_length):
                if guess[i] == self.secret_code[i]:
                    feedback[i] = GREEN
                    secret_copy[i] = guess_copy[i] = -1
            
            # 然后检查颜色正确但位置错误的
            for i in range(self.code_length):
                if guess_copy[i] != -1:
                    for j in range(self.code_length):
                        if secret_copy[j] == guess_copy[i] and secret_copy[j] != -1:
                            feedback[i] = WHITE
                            secret_copy[j] = -1
                            break
            
            return feedback
        else:  # 中等模式（原困难模式）
            feedback = []
            # 创建临时列表以跟踪已匹配的位置
            secret_copy = self.secret_code.copy()
            guess_copy = guess.copy()
            
            # 首先检查位置和颜色都正确的
            for i in range(self.code_length):
                if guess[i] == self.secret_code[i]:
                    feedback.append(GREEN)
                    secret_copy[i] = guess_copy[i] = -1
            
            # 然后检查颜色正确但位置错误的
            for i in range(self.code_length):
                if guess_copy[i] != -1:
                    for j in range(self.code_length):
                        if secret_copy[j] == guess_copy[i] and secret_copy[j] != -1:
                            feedback.append(WHITE)
                            secret_copy[j] = -1
                            break
            
            # 添加灰色反馈，确保总数为4个
            while len(feedback) < self.code_length:
                feedback.append(GRAY)
            
            return feedback

    def draw_feedback(self, feedback, x, y, is_easy_mode):
        """绘制反馈指示器"""
        if is_easy_mode:
            # 简单模式：在色块下方显示反馈，与位置对应
            # 反馈已经与位置对应，直接绘制
            for i in range(self.code_length):
                # 绘制圆角矩形
                rect_x = x + i * (BLOCK_SIZE + MARGIN)
                rect_y = y + BLOCK_SIZE + 5  # 调整位置更靠近色块
                rect_width = BLOCK_SIZE
                rect_height = 6  # 稍微减小高度
                
                # 使用与色块相同的圆角半径
                pygame.draw.rect(self.screen, feedback[i], 
                               (rect_x, rect_y, rect_width, rect_height),
                               border_radius=3)
        else:
            # 困难模式：在右侧显示反馈（按绿白灰排序）并排列成方形
            sorted_feedback = sorted(feedback, key=lambda x: (x != GREEN, x != WHITE, x != GRAY))
            
            # 计算方形布局的位置
            feedback_x = x + (self.code_length * (BLOCK_SIZE + MARGIN)) + 15
            feedback_y = y + BLOCK_SIZE//2 - 10
            
            # 2x2 方形布局
            positions = [
                (feedback_x, feedback_y),           # 左上
                (feedback_x + 12, feedback_y),      # 右上
                (feedback_x, feedback_y + 12),      # 左下
                (feedback_x + 12, feedback_y + 12)  # 右下
            ]
            
            # 绘制反馈点
            for i, color in enumerate(sorted_feedback):
                if i < 4:  # 确保不超出位置数量
                    pygame.draw.circle(self.screen, color, positions[i], 4)  # 减小圆点大小

    def draw_block(self, color_idx, x, y):
        """绘制单个色块"""
        # 统一的圆角半径
        block_radius = 8
        # 暗金色边框颜色
        border_color = (153, 124, 20)  # 暗金色
        border_width = 2  # 加粗边框
        
        if color_idx >= 0:
            # 创建渐变效果
            base_color = COLORS[color_idx]
            
            # 绘制底色 - 使用圆角矩形
            pygame.draw.rect(self.screen, base_color, (x, y, BLOCK_SIZE, BLOCK_SIZE), border_radius=block_radius)
            
            # 创建方形渐变效果
            # 计算内部方形的大小和位置
            inner_size = int(BLOCK_SIZE * 0.5)  # 内部方形为色块大小的50%
            inner_x = x + (BLOCK_SIZE - inner_size) // 2
            inner_y = y + (BLOCK_SIZE - inner_size) // 2
            
            # 创建一个更亮的颜色
            lighter_color = tuple(min(c + 100, 255) for c in base_color)
            
            # 绘制内部方形渐变
            pygame.draw.rect(self.screen, lighter_color, 
                           (inner_x, inner_y, inner_size, inner_size), 
                           border_radius=block_radius-2)  # 内部方形的圆角稍小
            
            # 绘制色块边框 - 使用暗金色和加粗边框
            pygame.draw.rect(self.screen, border_color, (x, y, BLOCK_SIZE, BLOCK_SIZE), border_width, border_radius=block_radius)
            
            # 在色块中间显示数字
            if color_idx >= 0:
                text_color = (0, 0, 0)
                
                # 渲染数字
                number_text = self.font.render(str(color_idx + 1), True, text_color)
                text_rect = number_text.get_rect(center=(x + BLOCK_SIZE//2, y + BLOCK_SIZE//2))
                self.screen.blit(number_text, text_rect)
        else:
            # 绘制空色块 - 使用圆角矩形
            pygame.draw.rect(self.screen, (50, 50, 50), (x, y, BLOCK_SIZE, BLOCK_SIZE), border_radius=block_radius)
            
            # 为空色块也添加方形渐变效果
            inner_size = int(BLOCK_SIZE * 0.5)
            inner_x = x + (BLOCK_SIZE - inner_size) // 2
            inner_y = y + (BLOCK_SIZE - inner_size) // 2
            
            # 创建一个稍微亮一点的颜色
            lighter_gray = (80, 80, 80)
            pygame.draw.rect(self.screen, lighter_gray, 
                           (inner_x, inner_y, inner_size, inner_size), 
                           border_radius=block_radius-2)
            
            # 空色块也使用相同的暗金色边框
            pygame.draw.rect(self.screen, border_color, (x, y, BLOCK_SIZE, BLOCK_SIZE), border_width, border_radius=block_radius)
            
            # 在空色块中显示 "0"
            text_color = (150, 150, 150)  # 使用灰色显示空色块的数字
            number_text = self.font.render("0", True, text_color)
            text_rect = number_text.get_rect(center=(x + BLOCK_SIZE//2, y + BLOCK_SIZE//2))
            self.screen.blit(number_text, text_rect)

    def draw_game_state(self):
        """绘制游戏状态"""
        if self.game_over:
            if self.win:
                # 为胜利文本添加闪烁效果
                pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.5  # 0到1之间的脉冲值
                size_factor = 1.0 + pulse * 0.3  # 大小变化因子
                # 使用支持中文的字体，而不是默认字体
                victory_font_size = int(36 * size_factor)  # 计算脉动的字体大小
                # 使用与游戏其他部分相同的字体，确保中文正确显示
                text = "恭喜你猜对了！"
                text_surface = self.font.render(text, True, (80, 200, 80))
                # 创建一个临时表面来实现缩放效果
                scaled_surface = pygame.transform.scale(text_surface, 
                                                      (int(text_surface.get_width() * size_factor),
                                                       int(text_surface.get_height() * size_factor)))
                text_rect = scaled_surface.get_rect(center=(SCREEN_WIDTH//2, 50))
                self.screen.blit(scaled_surface, text_rect)
            else:
                # 使用色块显示正确答案而不是中文
                text = "游戏结束！正确答案是: "
                text_surface = self.font.render(text, True, TEXT_COLOR)
                text_rect = text_surface.get_rect(midleft=(SCREEN_WIDTH//2 - 200, 50))
                self.screen.blit(text_surface, text_rect)
                
                # 绘制正确答案的色块
                for i, color_idx in enumerate(self.secret_code):
                    x = text_rect.right + 10 + i * (BLOCK_SIZE//2 + 5)
                    y = text_rect.centery - BLOCK_SIZE//4
                    pygame.draw.rect(self.screen, COLORS[color_idx], 
                                    (x, y, BLOCK_SIZE//2, BLOCK_SIZE//2), 
                                    border_radius=4)
        else:
            # 显示剩余猜测次数
            remaining = MAX_GUESSES - len(self.guesses)
            text = f"剩余猜测次数: {remaining}"
            text_surface = self.font.render(text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, 50))
            self.screen.blit(text_surface, text_rect)
            
            # 显示当前游戏模式和颜色数量
            if self.difficulty == 'easy':
                mode_name = "简单"
            elif self.difficulty == 'medium':
                mode_name = "中等"
            else:
                mode_name = "困难"
                
            mode_text = f"模式: {mode_name} | 颜色数量: {self.num_colors}"
            mode_surface = self.small_font.render(mode_text, True, TEXT_COLOR)
            self.screen.blit(mode_surface, (MARGIN, 20))

    def draw_color_selector(self):
        """绘制颜色选择器"""
        selector_y = SCREEN_HEIGHT - 100
        
        # 绘制颜色选择器
        for i in range(self.num_colors):
            x = MARGIN + i * (BLOCK_SIZE + MARGIN)
            self.draw_block(i, x, selector_y)
            
        # 绘制颜色选择器标题
        title_text = self.small_font.render("可选颜色:", True, TEXT_COLOR)
        self.screen.blit(title_text, (MARGIN, selector_y - 25))
    
    def draw_buttons(self):
        """绘制控制按钮"""
        submit_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 200, 120, 45)
        reset_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 150, 120, 45)
        menu_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 100, 120, 45)
        
        # 绘制提交按钮 - 使用圆角矩形
        color = BUTTON_HOVER_COLOR if submit_rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, submit_rect, border_radius=10)
        submit_text = self.small_font.render("提交(Enter)", True, BUTTON_TEXT_COLOR)
        self.screen.blit(submit_text, (submit_rect.centerx - submit_text.get_width()//2,
                                     submit_rect.centery - submit_text.get_height()//2))
        
        # 绘制再来一局按钮 - 使用圆角矩形
        color = BUTTON_HOVER_COLOR if reset_rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, reset_rect, border_radius=10)
        reset_text = self.small_font.render("再来一局(R)", True, BUTTON_TEXT_COLOR)
        self.screen.blit(reset_text, (reset_rect.centerx - reset_text.get_width()//2,
                                    reset_rect.centery - reset_text.get_height()//2))
        
        # 绘制返回主菜单按钮 - 使用圆角矩形
        color = BUTTON_HOVER_COLOR if menu_rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, menu_rect, border_radius=10)
        menu_text = self.small_font.render("主菜单(Esc)", True, BUTTON_TEXT_COLOR)
        self.screen.blit(menu_text, (menu_rect.centerx - menu_text.get_width()//2,
                                   menu_rect.centery - menu_text.get_height()//2))
        
        return submit_rect, reset_rect, menu_rect
        
    # 添加确认对话框绘制函数
    def draw_confirm_dialog(self):
        """绘制返回主菜单的确认对话框"""
        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # 黑色半透明
        self.screen.blit(overlay, (0, 0))
        
        # 增加对话框尺寸，确保文字能够完全显示
        dialog_width, dialog_height = 350, 170  # 增加宽度和高度
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
        
        # 绘制对话框背景
        pygame.draw.rect(self.screen, (60, 70, 90), 
                        (dialog_x, dialog_y, dialog_width, dialog_height),
                        border_radius=15)
        pygame.draw.rect(self.screen, (100, 120, 150), 
                        (dialog_x, dialog_y, dialog_width, dialog_height),
                        2, border_radius=15)
        
        # 绘制标题
        title_text = self.font.render("返回主菜单", True, (255, 255, 255))
        self.screen.blit(title_text, (dialog_x + (dialog_width - title_text.get_width())//2, dialog_y + 25))
        
        # 绘制提示文本 - 确保文字不会超出对话框
        prompt_text = self.small_font.render("确定要返回主菜单吗？当前进度将丢失。", True, (220, 220, 220))
        self.screen.blit(prompt_text, (dialog_x + (dialog_width - prompt_text.get_width())//2, dialog_y + 70))
        
        # 调整按钮位置，使其更加分散
        # 确认按钮
        confirm_rect = pygame.Rect(dialog_x + 70, dialog_y + 120, 80, 30)  # 调整Y坐标
        confirm_color = (100, 180, 100) if confirm_rect.collidepoint(pygame.mouse.get_pos()) else (80, 150, 80)
        pygame.draw.rect(self.screen, confirm_color, confirm_rect, border_radius=8)
        confirm_text = self.small_font.render("确定(Y)", True, (255, 255, 255))
        self.screen.blit(confirm_text, (confirm_rect.centerx - confirm_text.get_width()//2, 
                                      confirm_rect.centery - confirm_text.get_height()//2))
        
        # 取消按钮
        cancel_rect = pygame.Rect(dialog_x + 200, dialog_y + 120, 80, 30)  # 调整X坐标和Y坐标
        cancel_color = (180, 100, 100) if cancel_rect.collidepoint(pygame.mouse.get_pos()) else (150, 80, 80)
        pygame.draw.rect(self.screen, cancel_color, cancel_rect, border_radius=8)
        cancel_text = self.small_font.render("取消(N)", True, (255, 255, 255))
        self.screen.blit(cancel_text, (cancel_rect.centerx - cancel_text.get_width()//2, 
                                     cancel_rect.centery - cancel_text.get_height()//2))
        
        # 更新显示
        pygame.display.update()

def setup_input_method():
    """设置输入法，返回原始输入法状态"""
    original_keyboard_layout = None
    
    try:
        # 获取pygame窗口句柄
        hwnd = pygame.display.get_wm_info()['window']
        
        # 保存当前输入法状态
        original_keyboard_layout = ctypes.windll.user32.GetKeyboardLayout(0)
        print(f"保存原始输入法状态: {original_keyboard_layout}")
        
        # 使用中文拼音输入法的英文模式
        # 0x00000001 是 KLF_ACTIVATE 标志，使键盘布局立即激活
        # 0x00000804 是中文（简体）拼音输入法的代码
        result = ctypes.windll.user32.LoadKeyboardLayoutW("00000804", 0x00000001)
        
        # 切换到英文输入模式 - 模拟按下Shift键
        ctypes.windll.user32.keybd_event(0x10, 0, 0, 0)  # 按下Shift键
        ctypes.windll.user32.keybd_event(0x10, 0, 2, 0)  # 释放Shift键
        
        # 为pygame窗口设置输入法
        if hwnd != 0:
            # 向窗口发送消息以更新输入法
            ctypes.windll.user32.PostMessageW(hwnd, 0x0050, 0, result)  # 0x0050 是 WM_INPUTLANGCHANGEREQUEST
        
        print(f"切换到英文输入法: {result != 0}")
    except Exception as e:
        print(f"切换输入法失败: {e}")
    
    return original_keyboard_layout

def restore_input_method(original_keyboard_layout):
    """恢复原始输入法状态"""
    if original_keyboard_layout is None:
        return
        
    try:
        # 尝试获取pygame窗口句柄
        try:
            hwnd = pygame.display.get_wm_info()['window']
        except:
            # 如果获取失败，则使用当前前台窗口
            hwnd = ctypes.windll.user32.GetForegroundWindow()
        
        # 恢复原始输入法
        ctypes.windll.user32.ActivateKeyboardLayout(original_keyboard_layout, 0)
        if hwnd != 0:
            # 向窗口发送消息以更新输入法
            ctypes.windll.user32.PostMessageW(hwnd, 0x0050, 0, original_keyboard_layout)
        print("已恢复原始输入法状态")
    except Exception as e:
        print(f"恢复输入法失败: {e}")

if __name__ == "__main__":
    # 设置一个简单的环境变量来强制使用软件渲染
    import os
    os.environ['SDL_VIDEODRIVER'] = 'windib'  # 在Windows上使用windib驱动
    
    # 确保pygame已初始化
    if not pygame.get_init():
        pygame.init()
    
    original_keyboard_layout = None
    game = None
    
    try:
        # 创建游戏实例
        game = Game()
        
        # 设置输入法
        original_keyboard_layout = setup_input_method()
        
        # 运行游戏
        game.run()
    except Exception as e:
        # 打印错误信息
        print(f"游戏运行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 在退出前恢复原始输入法状态
        restore_input_method(original_keyboard_layout)
        
        # 确保程序不会立即退出
        pygame.quit()
        # 修复：使用更安全的方式等待用户输入
        try:
            print("按回车键退出...")
            # 使用os.read代替input()，避免sys.stdin问题
            if hasattr(os, 'read'):
                os.read(0, 1)  # 从标准输入读取一个字节
            else:
                # 如果os.read不可用，尝试使用msvcrt（Windows特有）
                try:
                    import msvcrt
                    msvcrt.getch()
                except ImportError:
                    # 如果都不可用，尝试使用input，但捕获可能的异常
                    try:
                        input()
                    except:
                        pass
        except:
            # 忽略任何可能的输入错误
            pass
            
        sys.exit(0)
