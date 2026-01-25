#!/usr/bin/env python3
"""
🚀 Starship Falcon - Terminal Space Adventure
A beautiful ASCII rocket animation game for your terminal.
"""

import os
import sys
import time
import random
import signal

# Terminal dimensions
WIDTH = 80
HEIGHT = 30
FRAME_DELAY = 0.05  # 50ms delay

# ANSI color codes for enhanced visuals
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Rocket colors
    ROCKET_TIP = '\033[97m'      # Bright white
    ROCKET_BODY = '\033[37m'     # White
    ROCKET_FINS = '\033[94m'     # Blue
    ROCKET_ENGINE = '\033[93m'   # Yellow
    
    # Flame colors
    FLAME_INNER = '\033[93m'     # Yellow
    FLAME_OUTER = '\033[91m'     # Red
    FLAME_HOT = '\033[97m'       # Bright white
    
    # Star colors
    STAR_BRIGHT = '\033[97m'     # Bright white
    STAR_DIM = '\033[90m'        # Gray
    STAR_BLUE = '\033[96m'       # Cyan
    
    # UI colors
    TITLE = '\033[95m'           # Magenta
    INFO = '\033[92m'            # Green


def clear_screen():
    """Clear the terminal screen."""
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Unix/Linux/Mac
        print('\033[2J\033[H', end='', flush=True)


def hide_cursor():
    """Hide the terminal cursor."""
    print('\033[?25l', end='', flush=True)


def show_cursor():
    """Show the terminal cursor."""
    print('\033[?25h', end='', flush=True)


def create_star_field():
    """Create a random star field."""
    stars = {}
    for _ in range(150):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)
        star_type = random.choice(['bright', 'dim', 'blue'])
        stars[(x, y)] = star_type
    return stars


def draw_rocket(buffer, color_buffer, x, y, frame):
    """Draw the rocket with flames at position (x, y)."""
    # Rocket components
    rocket_parts = [
        # Tip (y offset, x offset, char, color)
        (0, 0, '^', Colors.ROCKET_TIP),
        
        # Upper body
        (1, -1, '/', Colors.ROCKET_BODY),
        (1, 0, '|', Colors.ROCKET_BODY),
        (1, 1, '\\', Colors.ROCKET_BODY),
        
        # Middle body
        (2, -2, '/', Colors.ROCKET_BODY),
        (2, -1, '█', Colors.ROCKET_ENGINE),
        (2, 0, '█', Colors.ROCKET_ENGINE),
        (2, 1, '█', Colors.ROCKET_ENGINE),
        (2, 2, '\\', Colors.ROCKET_BODY),
        
        # Lower body
        (3, -1, '█', Colors.ROCKET_BODY),
        (3, 0, '█', Colors.ROCKET_BODY),
        (3, 1, '█', Colors.ROCKET_BODY),
        
        # Engine section
        (4, -2, '[', Colors.ROCKET_ENGINE),
        (4, -1, '=', Colors.ROCKET_ENGINE),
        (4, 0, '=', Colors.ROCKET_ENGINE),
        (4, 1, '=', Colors.ROCKET_ENGINE),
        (4, 2, ']', Colors.ROCKET_ENGINE),
        
        # Fins
        (4, -3, '/', Colors.ROCKET_FINS),
        (5, -4, '/', Colors.ROCKET_FINS),
        (4, 3, '\\', Colors.ROCKET_FINS),
        (5, 4, '\\', Colors.ROCKET_FINS),
    ]
    
    # Draw rocket parts
    for dy, dx, char, color in rocket_parts:
        py, px = y + dy, x + dx
        if 0 <= py < HEIGHT and 0 <= px < WIDTH:
            buffer[py][px] = char
            color_buffer[py][px] = color
    
    # Animated flames (based on frame number)
    flame_offset = frame % 3
    
    # Inner flames
    flame_chars = ['|', '│', '║']
    flame_char = flame_chars[flame_offset]
    
    # Flame level 1
    for dx in [-1, 0, 1]:
        py, px = y + 5, x + dx
        if 0 <= py < HEIGHT and 0 <= px < WIDTH:
            buffer[py][px] = flame_char
            color_buffer[py][px] = Colors.FLAME_HOT
    
    # Flame level 2
    flame_parts_2 = [(-2, '\\'), (-1, flame_char), (0, flame_char), (1, flame_char), (2, '/')]
    for dx, char in flame_parts_2:
        py, px = y + 6, x + dx
        if 0 <= py < HEIGHT and 0 <= px < WIDTH:
            buffer[py][px] = char
            color_buffer[py][px] = Colors.FLAME_INNER
    
    # Flame level 3 (outer flames - animated)
    if flame_offset != 1:
        flame_parts_3 = [(-3, '\\'), (-2, flame_char), (-1, flame_char), 
                         (0, flame_char), (1, flame_char), (2, flame_char), (3, '/')]
        for dx, char in flame_parts_3:
            py, px = y + 7, x + dx
            if 0 <= py < HEIGHT and 0 <= px < WIDTH:
                buffer[py][px] = char
                color_buffer[py][px] = Colors.FLAME_OUTER


def render_frame(buffer, color_buffer, stars, rocket_x, rocket_y, frame):
    """Render a single frame."""
    # Clear buffers
    for y in range(HEIGHT):
        for x in range(WIDTH):
            buffer[y][x] = ' '
            color_buffer[y][x] = Colors.RESET
    
    # Draw stars (with slight animation)
    for (sx, sy), star_type in stars.items():
        # Stars twinkle
        if random.random() > 0.95:
            continue
        
        if star_type == 'bright':
            buffer[sy][sx] = '*'
            color_buffer[sy][sx] = Colors.STAR_BRIGHT
        elif star_type == 'dim':
            buffer[sy][sx] = '.'
            color_buffer[sy][sx] = Colors.STAR_DIM
        else:  # blue
            buffer[sy][sx] = '✦'
            color_buffer[sy][sx] = Colors.STAR_BLUE
    
    # Draw rocket
    draw_rocket(buffer, color_buffer, rocket_x, rocket_y, frame)
    
    # Build output string
    output = []
    output.append(f"\n{Colors.TITLE}{Colors.BOLD}  🚀 STARSHIP FALCON - LAUNCH SEQUENCE 🌟{Colors.RESET}\n")
    output.append(f"  {'─' * 50}\n")
    
    for y in range(HEIGHT):
        line = "  │"
        for x in range(WIDTH):
            line += f"{color_buffer[y][x]}{buffer[y][x]}{Colors.RESET}"
        line += "│"
        output.append(line + "\n")
    
    output.append(f"  {'─' * 50}\n")
    output.append(f"{Colors.INFO}  Frame: {frame:04d} │ Altitude: {HEIGHT - rocket_y:3d} units │ Press Ctrl+C to exit{Colors.RESET}\n")
    
    return ''.join(output)


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    show_cursor()
    clear_screen()
    print(f"\n{Colors.TITLE}🚀 Thanks for watching Starship Falcon!{Colors.RESET}")
    print(f"{Colors.INFO}   Safe travels through the cosmos! 🌟{Colors.RESET}\n")
    sys.exit(0)


def main():
    """Main game loop."""
    # Set up signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize buffers
    buffer = [[' ' for _ in range(WIDTH)] for _ in range(HEIGHT)]
    color_buffer = [[Colors.RESET for _ in range(WIDTH)] for _ in range(HEIGHT)]
    
    # Create star field
    stars = create_star_field()
    
    # Initial rocket position
    rocket_x = WIDTH // 2
    rocket_y = HEIGHT - 10
    rocket_speed = 0.3
    
    frame = 0
    
    try:
        hide_cursor()
        clear_screen()
        
        # Animation loop
        while True:
            # Render frame
            output = render_frame(buffer, color_buffer, stars, rocket_x, int(rocket_y), frame)
            
            # Move cursor to top and print frame
            print('\033[H' + output, end='', flush=True)
            
            # Update rocket position (ascend)
            rocket_y -= rocket_speed
            
            # Reset when rocket reaches top
            if rocket_y < -5:
                rocket_y = HEIGHT - 10
                # Regenerate stars for variety
                stars = create_star_field()
            
            # Increment frame counter
            frame += 1
            
            # Control frame rate
            time.sleep(FRAME_DELAY)
            
    except KeyboardInterrupt:
        signal_handler(None, None)
    finally:
        show_cursor()


if __name__ == "__main__":
    print(f"\n{Colors.TITLE}🚀 Starting Starship Falcon...{Colors.RESET}")
    print(f"{Colors.INFO}   Press Ctrl+C to exit at any time.{Colors.RESET}\n")
    time.sleep(1)
    main()
