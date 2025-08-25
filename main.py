import pygame
import json
import random
import os
import math
from game_logger import game_logger

# --- Constants ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
SPRITE_SIZE = 40
INITIAL_SIZE = 40
SIZE_INCREMENT = 1  # Pixels to grow per death (very gradual)
MAX_SIZE = 80  # Maximum size before speed boost kicks in (reduced)
SPEED_INCREMENT = 0.02  # Speed multiplier increment after max size

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)
YELLOW = (255, 255, 0)

# --- The Combatant Class ---
# This class represents each follower in the battle.
class Follower(pygame.sprite.Sprite):
    def __init__(self, user_data):
        # Call the parent class (Sprite) constructor
        super().__init__()

        self.username = user_data.get("instagram_username", "Unknown")
        self.current_size = INITIAL_SIZE
        self.speed_multiplier = 1.0
        
        # Store the original image for resizing
        self.original_image = None
        
        # --- Robust Image Loading with Circular Mask ---
        try:
            # The blueprint specifies loading the user's profile picture from a local path
            profile_path = user_data["profile_pic_path"]
            temp_image = pygame.image.load(profile_path).convert_alpha()
            self.original_image = temp_image  # Keep original for resizing
            self.update_image_size()
            
        except (pygame.error, FileNotFoundError):
            # Use default avatar for users without photos
            try:
                default_avatar_path = "profiles/default_avatar.png"
                temp_image = pygame.image.load(default_avatar_path).convert_alpha()
                self.original_image = temp_image
                self.update_image_size()
                print(f"Using default avatar for {self.username}")
            except:
                # Final fallback if default avatar doesn't exist
                print(f"Warning: Could not load image for {self.username}. Using a fallback color.")
                random.seed(self.username)
                self.fallback_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
                self.original_image = None
                self.update_image_size()

        # Create the rect for positioning and collision
        self.rect = self.image.get_rect()
        self.radius = self.current_size // 2  # For circular collision

        # Physics properties using floating-point vectors for smooth movement
        self.pos = pygame.math.Vector2(
            random.randint(SPRITE_SIZE, SCREEN_WIDTH - SPRITE_SIZE),
            random.randint(SPRITE_SIZE, SCREEN_HEIGHT - SPRITE_SIZE)
        )
        
        # Random initial velocity
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 4)  # Increased base speed
        self.velocity = pygame.math.Vector2(
            speed * math.cos(angle),
            speed * math.sin(angle)
        )

        self.rect.center = self.pos

        # Combat attributes - Check JSON file for bonuses
        bonuses = {'hp': 0, 'forca': 0, 'armadura': 0, 'sorte': 0}
        try:
            with open('atributos.json', 'r') as f:
                all_attributes = json.load(f)
                if self.username in all_attributes:
                    bonuses = all_attributes[self.username]
        except:
            pass  # Use default values if file doesn't exist
        
        # Base values
        base_hp = 100
        base_damage = 5
        
        # Each attribute point = 1% bonus
        hp_bonus = bonuses.get('hp', 0)
        damage_bonus = bonuses.get('forca', 0)
        armor_bonus = bonuses.get('armadura', 0)
        luck_bonus = bonuses.get('sorte', 0)
        
        # Apply percentage bonuses
        self.hp = int(base_hp * (1 + hp_bonus / 100))  # +1% per point
        self.max_hp = self.hp
        self.damage = base_damage * (1 + damage_bonus / 100)  # +1% per point
        
        # Armor reduces incoming damage by percentage (max 50% reduction)
        self.armor_reduction = min(0.5, armor_bonus / 100)  # 1% reduction per point, max 50%
        
        # Luck is chance for critical hit (max 50% chance)
        self.luck = min(0.5, luck_bonus / 100)  # 1% crit chance per point, max 50%
        
        # Show balanced stats
        if hp_bonus > 0 or damage_bonus > 0 or armor_bonus > 0 or luck_bonus > 0:
            print(f"{self.username}: HP={self.hp} (+{hp_bonus}%), DMG={self.damage:.1f} (+{damage_bonus}%), ARM={self.armor_reduction*100:.0f}%, LUCK={self.luck*100:.0f}%")

        # Cooldown to prevent instant multiple hits
        self.last_hit_time = 0
        self.hit_cooldown = 500  # milliseconds
    
    def update_image_size(self):
        """Update the sprite image based on current size"""
        radius = self.current_size // 2
        
        if self.original_image:
            # Scale the original image to new size
            temp_image = pygame.transform.scale(self.original_image, (self.current_size, self.current_size))
            
            # Create circular mask
            self.image = pygame.Surface((self.current_size, self.current_size), pygame.SRCALPHA)
            self.image.fill((0, 0, 0, 0))  # Transparent background
            
            # Draw circular mask
            pygame.draw.circle(self.image, (255, 255, 255, 255), (radius, radius), radius)
            self.image.blit(temp_image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            
            # NO BORDER - removed the white border line
        else:
            # Fallback colored circle
            self.image = pygame.Surface((self.current_size, self.current_size), pygame.SRCALPHA)
            self.image.fill((0, 0, 0, 0))  # Transparent background
            
            # Draw colored circle without border
            pygame.draw.circle(self.image, self.fallback_color, (radius, radius), radius)
        
        # Update rect and radius
        old_center = self.rect.center if hasattr(self, 'rect') else (0, 0)
        self.rect = self.image.get_rect(center=old_center)
        self.radius = radius
    
    def update_size_and_speed(self, total_deaths):
        """Update size based on deaths, then speed if at max size"""
        # Logarithmic growth for smoother progression
        if total_deaths == 0:
            self.current_size = INITIAL_SIZE
        else:
            # Use logarithmic scale for smoother growth
            growth_factor = math.log(total_deaths + 1) * 8  # Adjust multiplier for desired growth rate
            new_size = INITIAL_SIZE + growth_factor
            
            if new_size <= MAX_SIZE:
                # Still growing in size
                self.current_size = int(new_size)
                self.update_image_size()
            else:
                # Max size reached, increase speed instead
                self.current_size = MAX_SIZE
                self.update_image_size()
                
                # Calculate extra deaths beyond size limit
                extra_deaths = total_deaths - 30  # Approximate deaths to reach max size
                if extra_deaths > 0:
                    self.speed_multiplier = 1.0 + (extra_deaths * SPEED_INCREMENT)
                    
                    # Cap speed multiplier
                    if self.speed_multiplier > 3.0:
                        self.speed_multiplier = 3.0

    def update(self):
        # --- Simple Movement and Physics with speed multiplier ---
        actual_velocity = self.velocity * self.speed_multiplier
        self.pos += actual_velocity
        self.rect.center = self.pos

        # Wall collision detection - perfect elastic collision
        hit_wall = False
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.velocity.x = -self.velocity.x
            hit_wall = True
            # Keep sprite in bounds
            if self.rect.left <= 0:
                self.rect.left = 0
            else:
                self.rect.right = SCREEN_WIDTH
            self.pos.x = self.rect.centerx
            
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.velocity.y = -self.velocity.y
            hit_wall = True
            # Keep sprite in bounds
            if self.rect.top <= 0:
                self.rect.top = 0
            else:
                self.rect.bottom = SCREEN_HEIGHT
            self.pos.y = self.rect.centery
        
        # Speed boost on wall hit after max size
        if hit_wall and self.current_size >= MAX_SIZE:
            self.speed_multiplier *= 1.01
            if self.speed_multiplier > 3.0:
                self.speed_multiplier = 3.0
        
        # Keep minimum speed to prevent stopping
        if self.velocity.length() < 2.0:  # Increased minimum
            # If too slow, give it a stronger push
            angle = random.uniform(0, 2 * math.pi)
            speed = 3.0  # Good base speed
            self.velocity = pygame.math.Vector2(
                speed * math.cos(angle),
                speed * math.sin(angle)
            )
        
        # Cap maximum velocity (before multiplier) - increased for better gameplay
        if self.velocity.length() > 10:
            self.velocity.scale_to_length(10)

    def collide_with(self, other_sprite):
        """Handle collision with another sprite"""
        # Calculate distance between centers
        distance = self.pos.distance_to(other_sprite.pos)
        
        # Check if actually colliding (circles touching)
        if distance < (self.radius + other_sprite.radius) and distance > 0:
            # Perfect elastic collision for circles
            # Calculate collision normal
            normal = (other_sprite.pos - self.pos).normalize()
            
            # Relative velocity
            relative_velocity = self.velocity - other_sprite.velocity
            
            # Speed along collision normal
            speed = relative_velocity.dot(normal)
            
            # Do not resolve if velocities are separating
            if speed < 0:
                return
            
            # Calculate new velocities (elastic collision)
            self.velocity -= normal * speed
            other_sprite.velocity += normal * speed
            
            # Ensure minimum speed after collision (higher minimum for endgame)
            min_speed = 3.0 if hasattr(self, 'current_size') and self.current_size > MAX_SIZE else 2.0
            if self.velocity.length() < min_speed:
                self.velocity.scale_to_length(min_speed)
            if other_sprite.velocity.length() < min_speed:
                other_sprite.velocity.scale_to_length(min_speed)
            
            # Speed boost on collision after max size
            if self.current_size >= MAX_SIZE:
                self.speed_multiplier *= 1.005
                if self.speed_multiplier > 3.0:
                    self.speed_multiplier = 3.0
            
            # Separate circles to prevent overlap
            overlap = (self.radius + other_sprite.radius) - distance
            separation = normal * (overlap / 2 + 1)
            self.pos -= separation
            other_sprite.pos += separation
            
            # Update rect positions
            self.rect.center = self.pos
            other_sprite.rect.center = other_sprite.pos

    def deal_damage(self, other_sprite, is_final_two=False):
        """Deal damage during collision - returns True if target dies"""
        now = pygame.time.get_ticks()
        if now - self.last_hit_time > self.hit_cooldown:
            self.last_hit_time = now
            
            # Start with calculated damage
            damage = self.damage
            
            # Apply luck for critical hits (based on new percentage system)
            if self.luck > 0 and random.random() < self.luck:
                damage = damage * 2
                print(f"CRITICAL HIT by {self.username}!")
            
            # Apply armor reduction (percentage-based, not flat reduction)
            if hasattr(other_sprite, 'armor_reduction') and other_sprite.armor_reduction > 0:
                damage = damage * (1 - other_sprite.armor_reduction)
            
            # Ensure minimum damage of 1
            damage = max(1, damage)
            
            # ANTI-DRAW SYSTEM: In final 2, ensure no draws
            if is_final_two:
                # If both would die from normal damage, the one with more HP wins
                if self.hp <= damage and other_sprite.hp <= damage:
                    # Prevent double death - higher HP survives
                    if self.hp > other_sprite.hp:
                        # I have more HP, kill the other
                        damage = other_sprite.hp + 1
                    else:
                        # Other has more HP, don't kill them but deal some damage
                        damage = max(1, min(damage, other_sprite.hp - 1))
                elif other_sprite.hp <= damage:
                    # Ensure they die
                    damage = other_sprite.hp + 1
            
            # Apply damage
            other_sprite.hp -= damage
            print(f"{self.username} hits {other_sprite.username} for {damage} damage. {other_sprite.username} HP: {other_sprite.hp}")
            
            # Log damage to database
            game_logger.log_damage(self.username, other_sprite.username, damage)

            # Elimination check
            if other_sprite.hp <= 0:
                print(f"--- {other_sprite.username} has been eliminated by {self.username}! ---")
                # Log kill to database
                game_logger.log_kill(self.username, other_sprite.username)
                return True  # Signal that someone died
        return False

    def draw_pixelated_heart(self, surface, x, y, size):
        """Draw a pixelated heart"""
        pixel_size = max(1, size // 8)
        heart_pattern = [
            [0,1,1,0,0,1,1,0],
            [1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1],
            [0,1,1,1,1,1,1,0],
            [0,0,1,1,1,1,0,0],
            [0,0,0,1,1,0,0,0],
            [0,0,0,0,0,0,0,0]
        ]
        for row in range(8):
            for col in range(8):
                if heart_pattern[row][col]:
                    px = x - (size//2) + col * pixel_size
                    py = y - (size//2) + row * pixel_size
                    pygame.draw.rect(surface, (255, 80, 120), (px, py, pixel_size, pixel_size))
    
    def draw_pixelated_sword(self, surface, x, y, size):
        """Draw a pixelated sword"""
        pixel_size = max(1, size // 8)
        sword_pattern = [
            [0,0,0,0,0,0,1,0],
            [0,0,0,0,0,1,1,1],
            [0,0,0,0,1,1,1,0],
            [0,0,0,1,1,1,0,0],
            [0,0,1,1,1,0,0,0],
            [0,1,1,1,0,0,0,0],
            [1,1,1,0,0,0,0,0],
            [1,1,0,0,0,0,0,0]
        ]
        for row in range(8):
            for col in range(8):
                if sword_pattern[row][col]:
                    px = x - (size//2) + col * pixel_size
                    py = y - (size//2) + row * pixel_size
                    if row < 2 or col < 2:  # Handle
                        pygame.draw.rect(surface, (139, 69, 19), (px, py, pixel_size, pixel_size))
                    else:  # Blade
                        pygame.draw.rect(surface, (192, 192, 192), (px, py, pixel_size, pixel_size))
    
    def draw_pixelated_shield(self, surface, x, y, size):
        """Draw a pixelated shield"""
        pixel_size = max(1, size // 8)
        shield_pattern = [
            [0,1,1,1,1,1,1,0],
            [1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1],
            [0,1,1,1,1,1,1,0],
            [0,0,1,1,1,1,0,0],
            [0,0,0,1,1,0,0,0]
        ]
        for row in range(8):
            for col in range(8):
                if shield_pattern[row][col]:
                    px = x - (size//2) + col * pixel_size
                    py = y - (size//2) + row * pixel_size
                    # Blue shield with silver trim
                    if (row == 0 or row == 7 or col == 0 or col == 7) and shield_pattern[row][col]:
                        pygame.draw.rect(surface, (192, 192, 192), (px, py, pixel_size, pixel_size))
                    else:
                        pygame.draw.rect(surface, (64, 128, 255), (px, py, pixel_size, pixel_size))
    
    def draw_pixelated_clover(self, surface, x, y, size):
        """Draw a pixelated four-leaf clover"""
        pixel_size = max(1, size // 8)
        clover_pattern = [
            [0,1,1,0,0,1,1,0],
            [1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1],
            [0,1,1,1,1,1,1,0],
            [0,0,0,1,1,0,0,0],
            [0,0,0,1,1,0,0,0],
            [0,0,0,1,1,0,0,0],
            [0,0,1,1,1,1,0,0]
        ]
        for row in range(8):
            for col in range(8):
                if clover_pattern[row][col]:
                    px = x - (size//2) + col * pixel_size
                    py = y - (size//2) + row * pixel_size
                    # Green clover
                    pygame.draw.rect(surface, (34, 177, 76), (px, py, pixel_size, pixel_size))
    
    def draw_attribute_icons(self, surface):
        """Draw pixelated attribute icons around the sprite"""
        if self.hp <= 0:
            return
        
        icons_to_draw = []
        
        # Check what bonuses the player has (any bonus above 0%)
        if hasattr(self, 'max_hp') and self.max_hp > 100:
            icons_to_draw.append('heart')
        
        if hasattr(self, 'damage') and self.damage > 5.0:
            icons_to_draw.append('sword')
        
        if hasattr(self, 'armor_reduction') and self.armor_reduction > 0:
            icons_to_draw.append('shield')
        
        if hasattr(self, 'luck') and self.luck > 0:
            icons_to_draw.append('clover')
        
        if not icons_to_draw:
            return
        
        # Calculate icon positions
        icon_size = min(24, max(16, self.current_size // 3))
        center_x, center_y = self.rect.center
        radius = self.current_size // 2 + icon_size
        
        for i, icon_type in enumerate(icons_to_draw):
            # Position icons evenly around the sprite
            angle = (360 / len(icons_to_draw)) * i - 90
            x = center_x + radius * math.cos(math.radians(angle))
            y = center_y + radius * math.sin(math.radians(angle))
            
            # Draw black background circle
            pygame.draw.circle(surface, (0, 0, 0), (int(x), int(y)), icon_size // 2 + 1)
            
            # Draw the pixelated icon
            if icon_type == 'heart':
                self.draw_pixelated_heart(surface, int(x), int(y), icon_size)
            elif icon_type == 'sword':
                self.draw_pixelated_sword(surface, int(x), int(y), icon_size)
            elif icon_type == 'shield':
                self.draw_pixelated_shield(surface, int(x), int(y), icon_size)
            elif icon_type == 'clover':
                self.draw_pixelated_clover(surface, int(x), int(y), icon_size)
    
    def draw_health_bar(self, surface):
        if self.hp > 0:
            bar_length = self.current_size  # Scale bar with sprite size
            bar_height = 5
            fill = (self.hp / self.max_hp) * bar_length
            outline_rect = pygame.Rect(self.rect.centerx - bar_length//2, self.rect.top - bar_height - 2, bar_length, bar_height)
            fill_rect = pygame.Rect(self.rect.centerx - bar_length//2, self.rect.top - bar_height - 2, fill, bar_height)
            pygame.draw.rect(surface, GREEN, fill_rect)
            pygame.draw.rect(surface, WHITE, outline_rect, 1)

def draw_crown(surface, x, y, size):
    """Draw an improved crown with better quality"""
    crown_width = size
    crown_height = int(size * 0.6)
    
    # Create a surface with per-pixel alpha for smoother rendering
    crown_surface = pygame.Surface((crown_width + 10, crown_height + 10), pygame.SRCALPHA)
    
    # Draw base rectangle
    base_rect = pygame.Rect(5, crown_height//2 + 5, crown_width, crown_height//3)
    pygame.draw.rect(crown_surface, GOLD, base_rect)
    pygame.draw.rect(crown_surface, (255, 200, 0), base_rect, 2)  # Darker gold border
    
    # Draw crown peaks with anti-aliasing
    peak_width = crown_width // 5
    peak_positions = [0.1, 0.3, 0.5, 0.7, 0.9]  # Relative positions
    
    for i, pos in enumerate(peak_positions):
        peak_x = int(5 + crown_width * pos)
        peak_height_mult = 1.2 if i == 2 else 1.0  # Center peak taller
        
        # Draw triangular peaks
        peak_points = [
            (peak_x - peak_width//2, crown_height//2 + 5),
            (peak_x, int(5 + (crown_height//4) / peak_height_mult)),
            (peak_x + peak_width//2, crown_height//2 + 5)
        ]
        pygame.draw.polygon(crown_surface, GOLD, peak_points)
        pygame.draw.polygon(crown_surface, (255, 200, 0), peak_points, 2)
    
    # Draw jewels with glow effect
    # Center jewel (red)
    center_x = crown_width//2 + 5
    center_y = crown_height//2 + 5
    pygame.draw.circle(crown_surface, (255, 100, 100), (center_x, center_y), size//8)  # Glow
    pygame.draw.circle(crown_surface, RED, (center_x, center_y), size//10)
    pygame.draw.circle(crown_surface, WHITE, (center_x - size//20, center_y - size//20), size//30)  # Shine
    
    # Side jewels (blue)
    for offset in [-crown_width//3, crown_width//3]:
        jewel_x = center_x + offset
        jewel_y = center_y
        pygame.draw.circle(crown_surface, (100, 100, 255), (jewel_x, jewel_y), size//10)  # Glow
        pygame.draw.circle(crown_surface, (0, 100, 255), (jewel_x, jewel_y), size//12)
        pygame.draw.circle(crown_surface, WHITE, (jewel_x - size//30, jewel_y - size//30), size//40)  # Shine
    
    # Blit the crown to the main surface
    crown_rect = crown_surface.get_rect(center=(x, y - crown_height//4))
    surface.blit(crown_surface, crown_rect)

# --- Main Game Function ---
def game_loop():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Clube da Luta - Battle Royale")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    winner_font = pygame.font.Font(None, 74)
    stats_font = pygame.font.Font(None, 36)

    # Load follower data from users.json
    try:
        with open("users.json", "r") as f:
            users_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading users.json: {e}")
        return

    # Create a sprite group and populate it
    all_sprites = pygame.sprite.Group()
    active_followers = [u for u in users_data if u.get("is_active_follower")]
    
    for user in active_followers:
        follower = Follower(user)
        all_sprites.add(follower)
    
    # Start logging the game
    game_logger.start_game(active_followers)

    running = True
    winner = None
    winner_display_size = 0
    total_deaths = 0
    initial_count = len(all_sprites)

    # Main game loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update all sprites
        all_sprites.update()

        # Collision Detection - Check every pair once
        sprites_list = list(all_sprites.sprites())
        to_remove = []  # Track sprites to remove
        survivors = len(all_sprites)
        is_final_two = (survivors == 2)  # Check if we're down to final 2
        
        # Boost growth and speed when few survivors remain
        if survivors <= 5 and survivors > 1:
            for sprite in sprites_list:
                # Extra growth for final survivors
                if sprite.current_size < MAX_SIZE + 20:  # Allow extra growth in endgame
                    sprite.current_size = min(sprite.current_size + 0.5, MAX_SIZE + 20)
                    sprite.radius = sprite.current_size // 2
                    sprite.update_image_size()
                
                # Speed boost for final survivors
                if survivors <= 3:
                    sprite.speed_multiplier = min(sprite.speed_multiplier * 1.002, 4.0)
                    # Ensure minimum velocity to prevent getting stuck
                    if sprite.velocity.length() < 3.0:
                        sprite.velocity.scale_to_length(3.0)
                    
                    # Push away from corners to prevent getting stuck
                    corner_threshold = 150
                    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
                    
                    # If too close to corners, apply force toward center
                    if (sprite.pos.x < corner_threshold or sprite.pos.x > SCREEN_WIDTH - corner_threshold) and \
                       (sprite.pos.y < corner_threshold or sprite.pos.y > SCREEN_HEIGHT - corner_threshold):
                        # Create vector pointing to center
                        to_center = pygame.math.Vector2(center_x - sprite.pos.x, center_y - sprite.pos.y)
                        if to_center.length() > 0:
                            to_center.normalize_ip()
                            # Add gentle push toward center
                            sprite.velocity += to_center * 0.5
        
        for i in range(len(sprites_list)):
            for j in range(i + 1, len(sprites_list)):
                sprite1 = sprites_list[i]
                sprite2 = sprites_list[j]
                
                # Check circular collision
                distance = sprite1.pos.distance_to(sprite2.pos)
                if distance < (sprite1.radius + sprite2.radius):
                    # Handle physics collision
                    sprite1.collide_with(sprite2)
                    
                    # Handle combat - check for simultaneous death prevention
                    if is_final_two:
                        # In final 2, only one can die per collision
                        sprite1_kills = sprite1.deal_damage(sprite2, is_final_two)
                        if sprite1_kills:
                            to_remove.append(sprite2)
                        elif not sprite1_kills:  # Only check sprite2 damage if sprite1 didn't kill
                            sprite2_kills = sprite2.deal_damage(sprite1, is_final_two)
                            if sprite2_kills:
                                to_remove.append(sprite1)
                    else:
                        # Normal combat for more than 2 players
                        if sprite1.deal_damage(sprite2, is_final_two):
                            to_remove.append(sprite2)
                        if sprite2.deal_damage(sprite1, is_final_two):
                            to_remove.append(sprite1)
        
        # Remove dead sprites and update all survivors
        if to_remove:
            for sprite in to_remove:
                if sprite in all_sprites:
                    sprite.kill()
                    total_deaths += 1
            
            # Update size and speed for all remaining sprites
            for sprite in all_sprites:
                sprite.update_size_and_speed(total_deaths)
            
            # Calculate actual size for logging
            if total_deaths > 0:
                growth_factor = math.log(total_deaths + 1) * 8
                current_size = min(int(INITIAL_SIZE + growth_factor), MAX_SIZE)
            else:
                current_size = INITIAL_SIZE
            print(f"Deaths: {total_deaths}, Size: {current_size}px")

        # --- Draw / Render ---
        screen.fill(BLACK)
        
        # Check for winner
        survivors = len(all_sprites)
        if survivors == 1 and not winner:
            winner = all_sprites.sprites()[0]
            winner_display_size = 0  # Start animation
            # Log game end
            game_logger.end_game(winner.username)
        elif survivors == 0 and not winner:
            winner = "Nobody"  # Everyone died
            # Log game end with no winner
            game_logger.end_game("DRAW")

        # Normal game display
        if not winner:
            all_sprites.draw(screen)

            for sprite in all_sprites:
                sprite.draw_health_bar(screen)
                sprite.draw_attribute_icons(screen)
                user_text = font.render(sprite.username, True, WHITE)
                text_rect = user_text.get_rect(center=(sprite.rect.centerx, sprite.rect.bottom + 8))
                screen.blit(user_text, text_rect)

            # Counter display
            counter_text = stats_font.render(f"Survivors: {survivors}/{initial_count}", True, WHITE)
            screen.blit(counter_text, (10, 10))
            
            # Final showdown indicator
            if survivors == 2:
                final_text = stats_font.render("FINAL SHOWDOWN!", True, RED)
                final_rect = final_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
                screen.blit(final_text, final_rect)
        
        # Winner display
        else:
            if isinstance(winner, str):
                win_text = winner_font.render("DRAW - Nobody survived!", True, GREEN)
                win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(win_text, win_rect)
            else:
                # Animate winner growing
                if winner_display_size < 200:
                    winner_display_size += 2
                
                # Draw winner big in center
                center_x = SCREEN_WIDTH // 2
                center_y = SCREEN_HEIGHT // 2
                
                if winner.original_image:
                    # Scale winner image
                    big_image = pygame.transform.scale(winner.original_image, 
                                                      (winner_display_size, winner_display_size))
                    
                    # Create circular mask
                    masked_image = pygame.Surface((winner_display_size, winner_display_size), pygame.SRCALPHA)
                    masked_image.fill((0, 0, 0, 0))
                    radius = winner_display_size // 2
                    pygame.draw.circle(masked_image, (255, 255, 255, 255), (radius, radius), radius)
                    masked_image.blit(big_image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                    
                    # Draw winner
                    image_rect = masked_image.get_rect(center=(center_x, center_y))
                    screen.blit(masked_image, image_rect)
                else:
                    # Fallback circle
                    pygame.draw.circle(screen, winner.fallback_color, 
                                     (center_x, center_y), winner_display_size // 2)
                
                # Draw crown (try PNG first, fallback to drawn)
                if winner_display_size >= 200:
                    crown_y = center_y - winner_display_size // 2 - 30
                    try:
                        # Try to load crown PNG
                        crown_img = pygame.image.load(r"C:\Users\Gabriel.Glock\Desktop\fightclubgame-main\pngwing.com.png").convert_alpha()
                        crown_img = pygame.transform.scale(crown_img, (80, 60))
                        crown_rect = crown_img.get_rect(center=(center_x, crown_y))
                        screen.blit(crown_img, crown_rect)
                    except:
                        # Fallback to drawn crown if PNG not found
                        draw_crown(screen, center_x, crown_y + 10, 60)
                
                # Draw winner text
                win_text = winner_font.render(f"{winner.username}", True, GOLD)
                win_rect = win_text.get_rect(center=(center_x, center_y + winner_display_size // 2 + 50))
                screen.blit(win_text, win_rect)
                
                wins_text = stats_font.render("WINS!", True, GREEN)
                wins_rect = wins_text.get_rect(center=(center_x, center_y + winner_display_size // 2 + 90))
                screen.blit(wins_text, wins_rect)
                
                # Final stats
                stats_text = font.render(f"Defeated {initial_count - 1} opponents", True, WHITE)
                stats_rect = stats_text.get_rect(center=(center_x, center_y + winner_display_size // 2 + 120))
                screen.blit(stats_text, stats_rect)

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    game_loop()