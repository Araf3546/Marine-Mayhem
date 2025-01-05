from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

class SeaBattleGame:
    def __init__(self):
        self.grid_size = 10
        self.cell_size = 0.15
        self.window_size = (800, 600)
        self.current_player = 1
        self.scores = {1: 0, 2: 0}
        self.ships = []
        self.shots = []
        self.cannon_angle = 45
        self.cannon_pos = (0, -0.9)

        self.animating = False
        self.cannon_ball_pos = (0, -0.9)
        self.target_pos = (0, 0)
        self.animation_steps = 0
        self.max_steps = 30
        self.ball_radius = 0.02 

    def reset_game(self):
        self.current_player = 1
        self.scores = {1: 0, 2: 0}
        self.shots = []
        self.cannon_angle = 45
        self.animating = False
        self.cannon_ball_pos = (0, -0.9)
        self.animation_steps = 0
        self.ships = []
        self.create_ships()
        glutPostRedisplay()

    def midpoint_line(self, x1, y1, x2, y2):
        points = []
        scale = 1000
        x1, y1 = int(x1 * scale), int(y1 * scale)
        x2, y2 = int(x2 * scale), int(y2 * scale)
        
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        
        x_inc = 1 if x2 > x1 else -1
        y_inc = 1 if y2 > y1 else -1
        
        if dx >= dy:
            p = 2*dy - dx
            for _ in range(dx + 1):
                
                points.append((x/scale, y/scale))
                if p >= 0:
                    y += y_inc
                    p -= 2*dx
                x += x_inc
                p += 2*dy
        else:
            p = 2*dx - dy
            for _ in range(dy + 1):

                points.append((x/scale, y/scale))
                if p >= 0:
                    x += x_inc
                    p -= 2*dy
                y += y_inc
                p += 2*dx
        
        return points

    def midpoint_circle(self, xc, yc, radius):
        points = []
        scale = 1000
        xc, yc = int(xc * scale), int(yc * scale)
        radius = int(radius * scale)
        
        x, y = 0, radius
        p = 1 - radius
        
        def plot_points(x, y):
            points.extend([
                ((xc + x)/scale, (yc + y)/scale),
                ((xc - x)/scale, (yc + y)/scale),
                ((xc + x)/scale, (yc - y)/scale),
                ((xc - x)/scale, (yc - y)/scale),
                ((xc + y)/scale, (yc + x)/scale),
                ((xc - y)/scale, (yc + x)/scale),
                ((xc + y)/scale, (yc - x)/scale),
                ((xc - y)/scale, (yc - x)/scale)
            ])
        
        plot_points(x, y)
        while x < y:
            x += 1
            if p < 0:
                p += 2*x + 1
            else:
                y -= 1
                p += 2*(x - y) + 1
            plot_points(x, y)
        
        return points

    def create_ships(self):
        ship_shapes = [
            [(0,0), (1,0), (2,0), (3,0)],  # Long ship
            [(0,0), (1,0), (1,1), (2,0)],  # T-shaped
            [(0,0), (1,0), (2,0)],         # Medium ship
            [(0,0), (1,0)]                 # Small ship
        ]
        
        self.ships = []
        occupied_cells = set()
        
        for shape in ship_shapes:
            placed = False
            while not placed:
                x = random.randint(0, self.grid_size - 1)
                y = random.randint(0, self.grid_size - 1)
                rotation = random.choice([0, 90, 180, 270])
                
                rotated_ship = []
                can_place = True
                
                for dx, dy in shape:
                    if rotation == 0:
                        new_x, new_y = x + dx, y + dy
                    elif rotation == 90:
                        new_x, new_y = x - dy, y + dx
                    elif rotation == 180:
                        new_x, new_y = x - dx, y - dy
                    else:  # 270
                        new_x, new_y = x + dy, y - dx
                    
                    if (new_x < 0 or new_x >= self.grid_size or
                        new_y < 0 or new_y >= self.grid_size or
                        (new_x, new_y) in occupied_cells):
                        can_place = False
                        break
                    
                    rotated_ship.append((new_x, new_y))
                
                if can_place:
                    self.ships.append(rotated_ship)
                    occupied_cells.update(rotated_ship)
                    placed = True

    def draw_grid(self):
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_POINTS)
        for i in range(self.grid_size + 1):
            x = -0.75 + i * self.cell_size
            for point in self.midpoint_line(x, -0.75, x, 0.75):
                glVertex2f(*point)
            y = -0.75 + i * self.cell_size
            for point in self.midpoint_line(-0.75, y, 0.75, y):
                glVertex2f(*point)
        glEnd()

    def draw_cannon(self):
        glBegin(GL_POINTS)
        if self.current_player == 1:
            glColor3f(0.0, 0.0, 1.0)  # Blue for Player 1
        else:
            glColor3f(1.0, 0.0, 0.0)  # Red for Player 2
        for point in self.midpoint_circle(*self.cannon_pos, 0.08):
            glVertex2f(*point)
    
   
        angle_rad = math.radians(self.cannon_angle)
        barrel_length = 0.2  
        barrel_thickness = 0.04  
   
        end_x = self.cannon_pos[0] + barrel_length * math.cos(angle_rad)
        end_y = self.cannon_pos[1] + barrel_length * math.sin(angle_rad)
     
   
        for t in range(-5, 6):
            offset = t * barrel_thickness / 10
            dx = offset * math.sin(angle_rad)
            dy = offset * -math.cos(angle_rad)
            for point in self.midpoint_line(self.cannon_pos[0] + dx, self.cannon_pos[1] + dy, end_x + dx, end_y + dy):
                glVertex2f(*point)
    
        glEnd()
     
    def draw_reset_button(self):
        glBegin(GL_POINTS)
        glColor3f(1.0, 1.0, 1.0)
        points = []
    
    # Button box
        button_x = 0  
        button_y = 0.9  
        button_width = 0.2
        button_height = 0.08
    
    # button outline
        points.extend(self.midpoint_line(button_x - button_width/2, button_y - button_height, 
                                   button_x + button_width/2, button_y - button_height))
        points.extend(self.midpoint_line(button_x - button_width/2, button_y, 
                                   button_x + button_width/2, button_y))
        points.extend(self.midpoint_line(button_x - button_width/2, button_y - button_height, 
                                   button_x - button_width/2, button_y))
        points.extend(self.midpoint_line(button_x + button_width/2, button_y - button_height, 
                                   button_x + button_width/2, button_y))
    
    # "RESET" text
        text_scale = 0.001
        base_x = button_x - 0.09
        base_y = button_y - button_height/1.3
    
    # R
        points.extend(self.midpoint_line(base_x, base_y, base_x, base_y + 0.05))
        points.extend(self.midpoint_line(base_x, base_y + 0.05, base_x + 0.03, base_y + 0.05))
        points.extend(self.midpoint_line(base_x + 0.03, base_y + 0.05, base_x + 0.03, base_y + 0.025))
        points.extend(self.midpoint_line(base_x + 0.03, base_y + 0.025, base_x, base_y + 0.025))
        points.extend(self.midpoint_line(base_x, base_y + 0.025, base_x + 0.03, base_y))
    
    # E
        base_x += 0.04
        points.extend(self.midpoint_line(base_x, base_y, base_x, base_y + 0.05))
        points.extend(self.midpoint_line(base_x, base_y + 0.05, base_x + 0.03, base_y + 0.05))
        points.extend(self.midpoint_line(base_x, base_y + 0.025, base_x + 0.02, base_y + 0.025))
        points.extend(self.midpoint_line(base_x, base_y, base_x + 0.03, base_y))
    
    # S
        base_x += 0.04
        points.extend(self.midpoint_line(base_x + 0.03, base_y + 0.05, base_x, base_y + 0.05))
        points.extend(self.midpoint_line(base_x, base_y + 0.05, base_x, base_y + 0.025))
        points.extend(self.midpoint_line(base_x, base_y + 0.025, base_x + 0.03, base_y + 0.025))
        points.extend(self.midpoint_line(base_x + 0.03, base_y + 0.025, base_x + 0.03, base_y))
        points.extend(self.midpoint_line(base_x + 0.03, base_y, base_x, base_y))
    
    # E
        base_x += 0.04
        points.extend(self.midpoint_line(base_x, base_y, base_x, base_y + 0.05))
        points.extend(self.midpoint_line(base_x, base_y + 0.05, base_x + 0.03, base_y + 0.05))
        points.extend(self.midpoint_line(base_x, base_y + 0.025, base_x + 0.02, base_y + 0.025))
        points.extend(self.midpoint_line(base_x, base_y, base_x + 0.03, base_y))
    
    # T
        base_x += 0.04
        points.extend(self.midpoint_line(base_x, base_y + 0.05, base_x + 0.03, base_y + 0.05))
        points.extend(self.midpoint_line(base_x + 0.015, base_y + 0.05, base_x + 0.015, base_y))
    
        for point in points:
            glVertex2f(*point)
        glEnd()
    
    def animate_cannon_ball(self):
        if self.animating:
            if self.animation_steps < self.max_steps:
                t = self.animation_steps / self.max_steps
                self.cannon_ball_pos = (
                    self.cannon_pos[0] + (self.target_pos[0] - self.cannon_pos[0]) * t,
                    self.cannon_pos[1] + (self.target_pos[1] - self.cannon_pos[1]) * t
                )
                self.animation_steps += 1
                glutPostRedisplay()
            else:
                self.animating = False
                self.handle_shot_impact()

    def draw_cannon_ball(self):
        if self.animating:
            glBegin(GL_POINTS)
            glColor3f(1.0, 0.0, 0.0)  # Red cannon ball
            for point in self.midpoint_circle(self.cannon_ball_pos[0], self.cannon_ball_pos[1], self.ball_radius):
                glVertex2f(*point)
            glEnd()

    def handle_shot_impact(self):
        grid_x = int((self.target_pos[0] + 0.75) / self.cell_size)
        grid_y = int((self.target_pos[1] + 0.75) / self.cell_size)
        
        # Check if hit
        hit = False
        for ship in self.ships:
            if (grid_x, grid_y) in ship:
                hit = True
                self.scores[self.current_player] += 1
                
                # Check if ship is completely destroyed
                ship_cells = set(ship)
                shot_cells = {(s[0], s[1]) for s in self.shots if s[2]}
                if len(ship_cells - shot_cells) == 1:
                    self.scores[self.current_player] += 2
                break
        
        self.shots.append((grid_x, grid_y, hit))
        
        if not hit:
            self.current_player = 3 - self.current_player

    def fill_square(self, center_x, center_y, size):
        points = []
        half_size = size / 2
        density = 20
        step = size / density
        
        for x in range(density):
            for y in range(density):
                point_x = center_x - half_size + x * step
                point_y = center_y - half_size + y * step
                points.append((point_x, point_y))
        
        return points

    def draw_shots(self):
        glPointSize(2.0)  # Smaller point size for denser fill
        glBegin(GL_POINTS)
        for shot in self.shots:
            x, y, hit = shot
            if hit:
                glColor3f(1.0, 0.0, 0.0)  # Red for hits
            else:
                glColor3f(0.0, 0.0, 1.0)  # Blue for miss
                
            # Calculate center of the grid cell
            grid_x = -0.75 + x * self.cell_size + self.cell_size/2
            grid_y = -0.75 + y * self.cell_size + self.cell_size/2
            
            # Fill the entire square
            points = self.fill_square(grid_x, grid_y, self.cell_size * 0.9)  # fill 90% of cell 
            for point_x, point_y in points:
                glVertex2f(point_x, point_y)
        glEnd()
        
    def draw_digit(self, digit, base_x, base_y, scale=0.03):
        points = []
        segments = {
            0: [(0,1,1,1), (1,1,1,0), (1,0,1,-1), (1,-1,0,-1), (0,-1,0,0), (0,0,0,1)],  # 0
            1: [(1,1,1,-1)],  # 1
            2: [(0,1,1,1), (1,1,1,0), (1,0,0,0), (0,0,0,-1), (0,-1,1,-1)],  # 2
            3: [(0,1,1,1), (1,1,1,0), (1,0,0,0), (1,0,1,-1), (1,-1,0,-1)],  # 3
            4: [(0,1,0,0), (0,0,1,0), (1,1,1,-1)],  # 4
            5: [(1,1,0,1), (0,1,0,0), (0,0,1,0), (1,0,1,-1), (1,-1,0,-1)],  # 5
            6: [(1,1,0,1), (0,1,0,-1), (0,-1,1,-1), (1,-1,1,0), (1,0,0,0)],  # 6
            7: [(0,1,1,1), (1,1,1,-1)],  # 7
            8: [(0,1,1,1), (1,1,1,-1), (0,-1,1,-1), (0,-1,0,1), (0,0,1,0)],  # 8
            9: [(1,0,1,1), (1,1,0,1), (0,1,0,0), (0,0,1,0), (1,0,1,-1)]  # 9
            }
        
    
    # Draw segment for current digit
        if digit in segments:
            for seg in segments[digit]:
                x1, y1, x2, y2 = seg
                start_x = base_x + x1 * scale
                start_y = base_y + y1 * scale
                end_x = base_x + x2 * scale
                end_y = base_y + y2 * scale
                points.extend(self.midpoint_line(start_x, start_y, end_x, end_y))
    
            
        return points
    
    def draw_score(self):
        glBegin(GL_POINTS)
        glColor3f(1.0, 1.0, 1.0)
        points = []
        
        # Player 1 score 
        score1_str = str(self.scores[1])
        base_x = -0.95
        base_y = 0.1
        
        # P1 label
        points.extend(self.midpoint_line(base_x, base_y + 0.15, base_x, base_y + 0.2)) 
        points.extend(self.midpoint_line(base_x, base_y + 0.2, base_x + 0.05, base_y + 0.2)) 
        points.extend(self.midpoint_line(base_x + 0.05, base_y + 0.2, base_x + 0.05, base_y + 0.175))  
        points.extend(self.midpoint_line(base_x + 0.05, base_y + 0.175, base_x, base_y + 0.175)) 
        points.extend(self.midpoint_line(base_x + 0.1, base_y + 0.2, base_x + 0.1, base_y + 0.15))  # 1 vertical
        
        # score 
        digit_spacing = 0.06 
        for i, digit in enumerate(score1_str):
            points.extend(self.draw_digit(int(digit), base_x + i * digit_spacing, base_y))

        # Player 2 score 
        score2_str = str(self.scores[2])
        base_x = 0.8
        
        # P2 label
        points.extend(self.midpoint_line(base_x, base_y + 0.15, base_x, base_y + 0.2))  
        points.extend(self.midpoint_line(base_x, base_y + 0.2, base_x + 0.05, base_y + 0.2))  
        points.extend(self.midpoint_line(base_x + 0.05, base_y + 0.2, base_x + 0.05, base_y + 0.175))
        points.extend(self.midpoint_line(base_x + 0.05, base_y + 0.175, base_x, base_y + 0.175))  
        
        # Draw 2
        points.extend(self.midpoint_line(base_x + 0.1, base_y + 0.2, base_x + 0.15, base_y + 0.2))  
        points.extend(self.midpoint_line(base_x + 0.15, base_y + 0.2, base_x + 0.15, base_y + 0.175)) 
        points.extend(self.midpoint_line(base_x + 0.15, base_y + 0.175, base_x + 0.1, base_y + 0.175)) 
        points.extend(self.midpoint_line(base_x + 0.1, base_y + 0.175, base_x + 0.1, base_y + 0.15))  
        points.extend(self.midpoint_line(base_x + 0.1, base_y + 0.15, base_x + 0.15, base_y + 0.15))  
        
        for i, digit in enumerate(score2_str):
            points.extend(self.draw_digit(int(digit), base_x + i * digit_spacing, base_y))
        
        for point in points:
            glVertex2f(*point)
        glEnd()

    def is_game_over(self):
        all_ship_cells = set()
        for ship in self.ships:
            all_ship_cells.update(ship)
        
        hit_cells = {(s[0], s[1]) for s in self.shots if s[2]}
        return len(all_ship_cells) == len(hit_cells)

    def get_winner(self):
        if self.scores[1] > self.scores[2]:
            return 1
        elif self.scores[2] > self.scores[1]:
            return 2
        else:
            return 0  # draw

    def draw_game_over(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        glBegin(GL_POINTS)
        points = []
    
    # GAME OVER text
        base_x = -0.4
        base_y = 0.3
    
    # "GAME"
    # G
        points.extend(self.midpoint_line(base_x, base_y + 0.15, base_x + 0.1, base_y + 0.15))  # top horizontal
        points.extend(self.midpoint_line(base_x, base_y, base_x + 0.1, base_y))  # bottom horizontal
        points.extend(self.midpoint_line(base_x, base_y, base_x, base_y + 0.15))  # left vertical
        points.extend(self.midpoint_line(base_x + 0.1, base_y, base_x + 0.1, base_y + 0.07))  # right vertical
        points.extend(self.midpoint_line(base_x + 0.05, base_y + 0.07, base_x + 0.1, base_y + 0.07)) 
    
    # A
        base_x += 0.15
        points.extend(self.midpoint_line(base_x, base_y, base_x + 0.05, base_y + 0.15))
        points.extend(self.midpoint_line(base_x + 0.05, base_y + 0.15, base_x + 0.1, base_y))
        points.extend(self.midpoint_line(base_x + 0.02, base_y + 0.07, base_x + 0.08, base_y + 0.07))
    
    # M
        base_x += 0.15
        points.extend(self.midpoint_line(base_x, base_y, base_x, base_y + 0.15))
        points.extend(self.midpoint_line(base_x, base_y + 0.15, base_x + 0.05, base_y + 0.07))
        points.extend(self.midpoint_line(base_x + 0.05, base_y + 0.07, base_x + 0.1, base_y + 0.15))
        points.extend(self.midpoint_line(base_x + 0.1, base_y + 0.15, base_x + 0.1, base_y))
    
    # E
        base_x += 0.15
        points.extend(self.midpoint_line(base_x, base_y, base_x, base_y + 0.15))
        points.extend(self.midpoint_line(base_x, base_y + 0.15, base_x + 0.1, base_y + 0.15))
        points.extend(self.midpoint_line(base_x, base_y + 0.07, base_x + 0.08, base_y + 0.07))
        points.extend(self.midpoint_line(base_x, base_y, base_x + 0.1, base_y))
    
    # OVER
        base_x = -0.2
        base_y = 0.1
    
    # O
        points.extend(self.midpoint_line(base_x, base_y, base_x, base_y + 0.15))
        points.extend(self.midpoint_line(base_x, base_y + 0.15, base_x + 0.1, base_y + 0.15))
        points.extend(self.midpoint_line(base_x + 0.1, base_y + 0.15, base_x + 0.1, base_y))
        points.extend(self.midpoint_line(base_x, base_y, base_x + 0.1, base_y))
    
    # V
        base_x += 0.15
        points.extend(self.midpoint_line(base_x, base_y + 0.15, base_x + 0.05, base_y))
        points.extend(self.midpoint_line(base_x + 0.05, base_y, base_x + 0.1, base_y + 0.15))
    
    # E
        base_x += 0.15
        points.extend(self.midpoint_line(base_x, base_y, base_x, base_y + 0.15))
        points.extend(self.midpoint_line(base_x, base_y + 0.15, base_x + 0.1, base_y + 0.15))
        points.extend(self.midpoint_line(base_x, base_y + 0.07, base_x + 0.08, base_y + 0.07))
        points.extend(self.midpoint_line(base_x, base_y, base_x + 0.1, base_y))
    
    # R
        base_x += 0.15
        points.extend(self.midpoint_line(base_x, base_y, base_x, base_y + 0.15))
        points.extend(self.midpoint_line(base_x, base_y + 0.15, base_x + 0.1, base_y + 0.15))
        points.extend(self.midpoint_line(base_x + 0.1, base_y + 0.15, base_x + 0.1, base_y + 0.07))
        points.extend(self.midpoint_line(base_x + 0.1, base_y + 0.07, base_x, base_y + 0.07))
        points.extend(self.midpoint_line(base_x, base_y + 0.07, base_x + 0.1, base_y))
    
    # winner text
        winner = self.get_winner()
        if winner > 0:
            base_x = -0.3
            base_y = -0.2
        
        # P
            points.extend(self.midpoint_line(base_x, base_y, base_x, base_y + 0.15))  # P vertical
            points.extend(self.midpoint_line(base_x, base_y + 0.15, base_x + 0.1, base_y + 0.15))  # P top
            points.extend(self.midpoint_line(base_x + 0.1, base_y + 0.15, base_x + 0.1, base_y + 0.07))  # P right
            points.extend(self.midpoint_line(base_x + 0.1, base_y + 0.07, base_x, base_y + 0.07))  # P middle
        
        # winner number
            base_x += 0.15
            if winner == 1:
                points.extend(self.midpoint_line(base_x, base_y, base_x, base_y + 0.15))  # 1
            else:
                points.extend(self.midpoint_line(base_x, base_y + 0.15, base_x + 0.1, base_y + 0.15))  # 2 top
                points.extend(self.midpoint_line(base_x + 0.1, base_y + 0.15, base_x + 0.1, base_y + 0.07))  # 2 right
                points.extend(self.midpoint_line(base_x + 0.1, base_y + 0.07, base_x, base_y + 0.07))  # 2 middle
                points.extend(self.midpoint_line(base_x, base_y + 0.07, base_x, base_y))  # 2 left bottom
                points.extend(self.midpoint_line(base_x, base_y, base_x + 0.1, base_y))  # 2 bottom
        
        # WINS!
            base_x += 0.15
        # W
            points.extend(self.midpoint_line(base_x, base_y + 0.15, base_x + 0.03, base_y))
            points.extend(self.midpoint_line(base_x + 0.03, base_y, base_x + 0.06, base_y + 0.07))
            points.extend(self.midpoint_line(base_x + 0.06, base_y + 0.07, base_x + 0.09, base_y))
            points.extend(self.midpoint_line(base_x + 0.09, base_y, base_x + 0.12, base_y + 0.15))
        
        # I
            base_x += 0.13
            points.extend(self.midpoint_line(base_x, base_y, base_x, base_y + 0.15))
        
        # N
            base_x += 0.05
            points.extend(self.midpoint_line(base_x, base_y, base_x, base_y + 0.15))
            points.extend(self.midpoint_line(base_x, base_y + 0.15, base_x + 0.1, base_y))
            points.extend(self.midpoint_line(base_x + 0.1, base_y, base_x + 0.1, base_y + 0.15))
        
        # S
            base_x += 0.13
            points.extend(self.midpoint_line(base_x + 0.1, base_y + 0.15, base_x, base_y + 0.15))
            points.extend(self.midpoint_line(base_x, base_y + 0.15, base_x, base_y + 0.07))
            points.extend(self.midpoint_line(base_x, base_y + 0.07, base_x + 0.1, base_y + 0.07))
            points.extend(self.midpoint_line(base_x + 0.1, base_y + 0.07, base_x + 0.1, base_y))
            points.extend(self.midpoint_line(base_x + 0.1, base_y, base_x, base_y))
        
        # !
            base_x += 0.13
            points.extend(self.midpoint_line(base_x, base_y + 0.15, base_x, base_y + 0.05))
            points.extend(self.midpoint_line(base_x, base_y + 0.02, base_x, base_y))
    
        for point in points:
            glVertex2f(*point)
        glEnd()
        
    def handle_click(self, x, y):
        if self.is_game_over() or self.animating:
            return

        grid_x = int((x + 0.75) / self.cell_size)
        grid_y = int((y + 0.75) / self.cell_size)
        
        if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
            # Chk box condition
            for shot in self.shots:
                if shot[0] == grid_x and shot[1] == grid_y:
                    return
            
            # Start animation
            self.animating = True
            self.animation_steps = 0
            self.target_pos = (x, y)
            
            # Calculate initial cannon ball position 
            angle_rad = math.radians(self.cannon_angle)
            barrel_length = 0.15
            self.cannon_ball_pos = (
                self.cannon_pos[0] + barrel_length * math.cos(angle_rad),
                self.cannon_pos[1] + barrel_length * math.sin(angle_rad)
            )
    
    def display(self):
        if self.is_game_over():
            self.draw_game_over()
            self.draw_reset_button()  
        else:
            glClear(GL_COLOR_BUFFER_BIT)
            glLoadIdentity()
        
            self.draw_grid()
            self.draw_cannon()
            self.draw_shots()
            self.draw_score()
            self.draw_cannon_ball()
            self.draw_reset_button() 
            self.animate_cannon_ball()
    
        glutSwapBuffers()

    def idle_func(self):
        if self.animating:
            self.animate_cannon_ball()
            
    def calculate_angle_to_mouse(self, mouse_x, mouse_y):
        dx = mouse_x - self.cannon_pos[0]
        dy = mouse_y - self.cannon_pos[1]
        angle = math.degrees(math.atan2(dy, dx)) #degrees
        
        return angle % 360   
    
    def mouse_motion_func(self, x, y):
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        gl_x = (2.0 * x / window_width) - 1.0
        gl_y = 1.0 - (2.0 * y / window_height)
    
        self.cannon_angle = self.calculate_angle_to_mouse(gl_x, gl_y)
    
        glutPostRedisplay()

    def mouse_func(self, button, state, x, y):
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        gl_x = (2.0 * x / window_width) - 1.0
        gl_y = 1.0 - (2.0 * y / window_height)
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            if self.is_inside_reset_button(gl_x, gl_y):
                self.reset_game()
            else:
                self.handle_click(gl_x, gl_y)
            glutPostRedisplay()

    def is_inside_reset_button(self, x, y):
        button_x = 0
        button_y = 0.9
        button_width = 0.2
        button_height = 0.08
        return (button_x - button_width/2 <= x <= button_x + button_width/2 and
            button_y - button_height <= y <= button_y)

    def run(self):
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
        glutInitWindowSize(*self.window_size)
        glutCreateWindow(b"Marine Mayhem")
    
        glClearColor(0.0, 0.0, 0.0, 0.0)
        gluOrtho2D(-1, 1, -1, 1)
        glPointSize(2.0)
    
        self.create_ships()
    
        glutDisplayFunc(self.display)
        glutMouseFunc(self.mouse_func)
        glutMotionFunc(self.mouse_motion_func)   
        glutPassiveMotionFunc(self.mouse_motion_func) 
        glutIdleFunc(self.idle_func)
    
        glutMainLoop()

if __name__ == "__main__":
    game = SeaBattleGame()
    game.run()