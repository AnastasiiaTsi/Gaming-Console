from machine import Pin, PWM
from LCD_ST7789VW import LCD_ST7789VW
import utime
import random

# 1. Ініціалізація Кнопок 
keyA = Pin(15, Pin.IN, Pin.PULL_UP)
keyB = Pin(17, Pin.IN, Pin.PULL_UP)
keyX = Pin(19, Pin.IN, Pin.PULL_UP)
keyY = Pin(21, Pin.IN, Pin.PULL_UP)
ctrl = Pin(3, Pin.IN, Pin.PULL_UP)

# 2. Налаштування підсвітки та Дисплея 
lcd_bl = PWM(Pin(13))
lcd_bl.freq(1000)
# статична яскравість  
lcd_bl.duty_u16(65535)

lcd = LCD_ST7789VW()
width, height = 240, 240 

current_screen = "MENU"
menu_selection = 0
games = ["Ping-Pong", "Snake", "Space", "Maze", "Dino"]

# 3. Система Меню 
def draw_menu():
    lcd.fill(0) 
    lcd.text("MAIN MENU", 80, 20, lcd.white)
    for i, game in enumerate(games):
        color = lcd.red if i == menu_selection else lcd.white
        label = "> " + game if i == menu_selection else game
        lcd.text(label, 40, 60 + (i * 30), color)
    lcd.text("Press CTRL to Start", 40, 210, lcd.green)
    lcd.show()

def menu_loop():
    global menu_selection, current_screen
    while current_screen == "MENU":
        if keyA.value() == 0:
            menu_selection = (menu_selection - 1) % len(games)
            utime.sleep(0.2)
        elif keyB.value() == 0:
            menu_selection = (menu_selection + 1) % len(games)
            utime.sleep(0.2)
        elif ctrl.value() == 0:
            current_screen = games[menu_selection]
            utime.sleep(0.4) 
        draw_menu()

# 4. Ігрові модулі

# гра №1 - ping-pong
def play_ping_pong():
    global current_screen
    bx, by = 120, 20
    bvx, bvy = 3, 3 
    px = 100; pw, ph = 60, 10 
    
    while current_screen == "Ping-Pong":
        lcd.fill(0) 
        if keyX.value() == 0 and px > 0: px -= 6 
        if keyY.value() == 0 and px < (width - pw): px += 6 
        
        if ctrl.value() == 0: 
            current_screen = "MENU"
            utime.sleep(0.4)
            break

        bx += bvx; by += bvy 
        if bx <= 5 or bx >= width-5: bvx = -bvx 
        if by <= 5: bvy = -bvy # [cite: 72]
        
        if by >= 220 and px < bx < px + pw: 
            bvy = -random.randint(3, 6) 
            bvx = random.choice([-4, -2, 2, 4])
            
        if by > height: current_screen = "MENU" 

        lcd.ellipse(int(bx), int(by), 5, 5, lcd.green, 1) 
        lcd.rect(int(px), 230, pw, ph, lcd.red, 1) 
        lcd.show()
        utime.sleep(0.01)

# гра №2 snake
def play_snake():
    global current_screen
    snake = [[100, 100], [90, 100], [80, 100]] 
    dx, dy = 10, 0
    food = [random.randrange(1, 23) * 10, random.randrange(1, 23) * 10]
    
    while current_screen == "Snake":
        if keyA.value() == 0 and dy == 0: dx, dy = 0, -10
        if keyB.value() == 0 and dy == 0: dx, dy = 0, 10
        if keyX.value() == 0 and dx == 0: dx, dy = -10, 0
        if keyY.value() == 0 and dx == 0: dx, dy = 10, 0
        
        if ctrl.value() == 0:
            current_screen = "MENU"
            utime.sleep(0.4)
            break

        new_head = [snake[0][0] + dx, snake[0][1] + dy]
        if new_head[0] < 0 or new_head[0] >= width or new_head[1] < 0 or new_head[1] >= height or new_head in snake:
            current_screen = "MENU"
            
        snake.insert(0, new_head)
        if new_head == food:
            food = [random.randrange(1, 23) * 10, random.randrange(1, 23) * 10]
        else:
            snake.pop()

        lcd.fill(0)
        lcd.rect(food[0], food[1], 10, 10, lcd.red, 1)
        for p in snake:
            lcd.rect(p[0], p[1], 10, 10, lcd.green, 1)
        lcd.show()
        utime.sleep(0.12)

# гра №3 space invaders 
def play_space_invaders():
    global current_screen
    ship_x = 110
    bullets = []
    enemies = [[random.randint(10, 220), 0] for _ in range(3)]

    while current_screen == "Space":
        lcd.fill(0)
        if keyX.value() == 0 and ship_x > 0: ship_x -= 5
        if keyY.value() == 0 and ship_x < 220: ship_x += 5
        if keyA.value() == 0: bullets.append([ship_x + 10, 220])
        
        if ctrl.value() == 0:
            current_screen = "MENU"
            utime.sleep(0.4)
            break

        for b in bullets:
            b[1] -= 8
            lcd.rect(b[0], b[1], 2, 6, lcd.white, 1)
        bullets = [b for b in bullets if b[1] > 0]

        for e in enemies:
            e[1] += 2
            lcd.rect(e[0], e[1], 16, 16, lcd.red, 1)
            if e[1] > 230: current_screen = "MENU"
            
            for b in bullets:
                if e[0] < b[0] < e[0] + 16 and e[1] < b[1] < e[1] + 16:
                    e[1] = 0; e[0] = random.randint(10, 220)
                    bullets.remove(b)

        lcd.rect(int(ship_x), 225, 20, 10, lcd.green, 1)
        lcd.show()
        utime.sleep(0.04)

# гра №4 maze 
def play_maze():
    global current_screen
    px, py = 15, 15
    walls = [[50, 0, 10, 170], [110, 70, 10, 170], [170, 0, 10, 170]]
    finish = [210, 210, 20, 20]

    while current_screen == "Maze":
        lcd.fill(0)
        if keyA.value() == 0: py -= 3
        if keyB.value() == 0: py += 3
        if keyX.value() == 0: px -= 3
        if keyY.value() == 0: px += 3
        
        if ctrl.value() == 0:
            current_screen = "MENU"
            utime.sleep(0.4)
            break

        for w in walls:
            lcd.rect(w[0], w[1], w[2], w[3], lcd.white, 1)
            if w[0] < px < w[0]+w[2] and w[1] < py < w[1]+w[3]:
                px, py = 15, 15 

        lcd.rect(finish[0], finish[1], finish[2], finish[3], lcd.green, 1)
        if px > finish[0] and py > finish[1]: current_screen = "MENU"

        lcd.ellipse(int(px), int(py), 4, 4, lcd.red, 1)
        lcd.show()
        utime.sleep(0.02)
        
# гра №5 dino
def play_dino():
    global current_screen
    dy = 200; jumping = False; jump_v = 10
    cx = 240

    while current_screen == "Dino":
        lcd.fill(0)
        if not jumping and keyA.value() == 0: jumping = True
        
        if jumping:
            dy -= jump_v * 2
            jump_v -= 1
            if dy >= 200: dy = 200; jumping = False; jump_v = 10

        cx -= 6
        if cx < -20: cx = 240

        if cx < 40 and dy > 175: current_screen = "MENU"
        
        if ctrl.value() == 0:
            current_screen = "MENU"
            utime.sleep(0.4)
            break

        lcd.rect(0, 220, 240, 2, lcd.white, 1)
        lcd.rect(20, int(dy), 20, 20, lcd.green, 1)
        lcd.rect(int(cx), 195, 15, 25, lcd.red, 1)
        lcd.show()
        utime.sleep(0.03)

# 5. Головний цикл 
while True:
    if current_screen == "MENU":
        menu_loop()
    elif current_screen == "Ping-Pong":
        play_ping_pong()
    elif current_screen == "Snake":
        play_snake()
    elif current_screen == "Space":
        play_space_invaders()
    elif current_screen == "Maze":
        play_maze()
    elif current_screen == "Dino":
        play_dino()