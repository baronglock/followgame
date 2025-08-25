#!/usr/bin/env python3
"""
Create a default avatar image like social media platforms use
"""

import pygame
import os

def create_default_avatar():
    """Create a default avatar similar to Instagram's default profile picture"""
    
    # Initialize pygame
    pygame.init()
    
    # Create surface
    size = 150
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))  # Transparent background
    
    # Colors (Instagram-like gray)
    bg_color = (219, 219, 219)  # Light gray background
    icon_color = (142, 142, 142)  # Darker gray for icon
    
    # Draw background circle
    center = (size // 2, size // 2)
    radius = size // 2
    pygame.draw.circle(surface, bg_color, center, radius)
    
    # Draw person icon (simplified)
    # Head
    head_radius = size // 6
    head_center = (size // 2, size // 2 - size // 8)
    pygame.draw.circle(surface, icon_color, head_center, head_radius)
    
    # Body (shoulders)
    body_width = size // 2
    body_height = size // 3
    body_top = head_center[1] + head_radius + 5
    
    # Create a curved body shape
    body_rect = pygame.Rect(
        center[0] - body_width // 2,
        body_top,
        body_width,
        body_height
    )
    
    # Draw body as an arc/ellipse for shoulders
    pygame.draw.ellipse(surface, icon_color, body_rect, 0)
    
    # Clip the bottom part (outside the circle)
    # Create a mask surface
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))
    pygame.draw.circle(mask, (255, 255, 255, 255), center, radius)
    
    # Apply mask
    final_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    final_surface.fill((0, 0, 0, 0))
    final_surface.blit(surface, (0, 0))
    final_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    
    # Save the image
    os.makedirs("profiles", exist_ok=True)
    pygame.image.save(final_surface, "profiles/default_avatar.png")
    print("Created default_avatar.png in profiles folder")

if __name__ == "__main__":
    create_default_avatar()