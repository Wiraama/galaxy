from kivy.config import Config
Config.set('kivy', 'window_icon', 'images/icon.png')
from kivy.uix.relativelayout import RelativeLayout
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy import platform
from kivy.lang import Builder
import random
from menu import MenuWidget

Builder.load_file("menu.kv")

class MainWidget(RelativeLayout):
    #perspective_point_x = NumericProperty(0)
    #perspective_point_y = NumericProperty(0)
    menu_widget = ObjectProperty()
    
    V_NUM_LINES = 11
    V_LINES_SPACING = .4
    v_line = []

    H_NUM_LINES = 9
    H_LINES_SPACING = .1
    h_line = []
    
    SPEED = 0.32
    SPEED_X = 2
    current_speed_x = 0
    current_offset_y = 0
    current_offset_x = 0
    
    NB_TILES = 20
    tiles = []
    tiles_points = []
    
    current_y_loop = 0
    
    SHIP_WIDTH = 0.1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None
    ship_points = [(0, 0), (0, 0), (0, 0)]
    
    game_over = False
    start_game = False
    
    menu_title = StringProperty("Wiriama\nG   A   L   A   X   Y")
    menu_btn_title = StringProperty("START")
    
    your_score = StringProperty()
    
    begin = None
    galaxy = None
    gameover_impact = None
    gameover_voice = None
    music1 = None
    restart = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_audio()
        self.initiate_v_line()
        self.initiate_h_line()
        self.init_tiles()
        self.init_ship()
        self.pre_fill_tile_points()
        self.generate_tile_points()
        
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)
            
        self.galaxy.play()
        
        Clock.schedule_interval(self.update, 1.0/60.0)
        
    def init_audio(self):
        self.begin = SoundLoader.load("audio/begin.wav")
        self.galaxy = SoundLoader.load("audio/galaxy.wav")
        self.gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.music1 = SoundLoader.load("audio/music1.wav")
        self.restart = SoundLoader.load("audio/restart.wav")
        
        self.begin.volume = .8
        self.galaxy.volume = .25
        self.gameover_impact.volume = .25
        self.gameover_voice.volume = .25
        self.music1.volume = .25
        self.restart.volume = .6
        
    def reset_game(self):
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
        
        self.your_score = f"SCORE: {str(self.current_y_loop)}"
        
        self.tiles_points = []
        self.pre_fill_tile_points()
        self.generate_tile_points()
        
        self.game_over = False

    def keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_keyboard_down)
        self._keyboard.unbind(on_key_up=self.on_keyboard_up)
        self._keyboard = None
        
    def is_desktop(Self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False
        
    def on_parent(self, widget, parent):
        pass

    def on_size(self, *args):
        # self.perspective_point_x = self.width/2
        # self.perspective_point_y = self.height * 0.75
        #self.update_v_line()
        #self.update_h_line()
        pass

    def on_perspective_point_x(self, widget, value):
        pass

    def on_perspective_point_y(self, widget, value):
        pass

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()
    
    def update_ship(self):
        center_x = self.width/2
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.SHIP_HEIGHT * self.height
        
        self.ship_points[0] = (center_x-ship_half_width, base_y)
        self.ship_points[1] = (center_x, base_y + ship_height)
        self.ship_points[2] = (center_x+ship_half_width, base_y)
        
        x1, y1 = self.transform(*self.ship_points[0])
        x2, y2 = self.transform(*self.ship_points[1])
        x3, y3 = self.transform(*self.ship_points[2])
        
        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_ship_collision(self):
        for i in range(0, len(self.tiles_points)):
            ti_x, ti_y = self.tiles_points[i]
            if ti_y > self.current_y_loop + 1:
                return False
            if self.chec_ship_collision_on_tile(ti_x, ti_y):
                return True
        return False

    def chec_ship_collision_on_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_points(ti_x, ti_y)
        xmax, ymax = self.get_tile_points(ti_x + 1, ti_y + 1)
        
        for i in range(0, 3):
            px, py = self.ship_points[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False

    def init_tiles(self):
        with self.canvas:
            Color(2, 5, 1)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())
    
    def pre_fill_tile_points(self):
        for i in range(0, 4):
            self.tiles_points.append((0, i))
    
    def generate_tile_points(self):
        last_x = 0
        last_y = 0
        for i in range(len(self.tiles_points)-1, -1, -1):
            if self.tiles_points[i][1] < self.current_y_loop:
                del self.tiles_points[i]
        
        if len(self.tiles_points) > 0:
            last_point = self.tiles_points[-1]
            last_x = last_point[0]
            last_y = last_point[1] + 1
        
        for i in range(len(self.tiles_points), self.NB_TILES):
            r = random.randint(0, 2)
            
            start_index = -int(self.V_NUM_LINES/2) + 1
            end_index = start_index + self.V_NUM_LINES
            
            if last_x <= start_index:
                r = 1
            if last_x >= end_index:
                r = 2
        
            self.tiles_points.append((last_x, last_y))

            if r == 1:
                last_x += 1
                self.tiles_points.append((last_x, last_y))
                last_y += 1
                self.tiles_points.append((last_x, last_y))
            if r == 2:
                last_x -= 1
                self.tiles_points.append((last_x, last_y))
                last_y += 1
                self.tiles_points.append((last_x, last_y))
        
    def initiate_v_line(self):
        with self.canvas:
            Color(1, 1, 1)
            # self.line = Line(points=[100, 0, 100, 100])
            for i in range(0, self.V_NUM_LINES):
                self.v_line.append(Line())

    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * self.width
        offset = index - 0.5
        line_x = central_line_x + offset * spacing + self.current_offset_x
        
        return line_x
        
    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING*self.height
        line_y = index * spacing_y - self.current_offset_y
        
        return line_y
    def get_tile_points(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        
        return x, y
    
    def update_tiles(self):
        for i in range(0, self.NB_TILES):
            tile = self.tiles[i]
            tile_points = self.tiles_points[i]
            xmin, ymin = self.get_tile_points(tile_points[0], tile_points[1])
            xmax, ymax = self.get_tile_points(tile_points[0]+1, tile_points[1]+1)
            
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)
            
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]
    
    def update_v_line(self):
        start_index = -int(self.V_NUM_LINES/2) + 1
        for i in range(start_index, start_index + self.V_NUM_LINES):
            line_x = self.get_line_x_from_index(i)
            
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)

            self.v_line[i].points = [x1, y1, x2, y2]
    
    def initiate_h_line(self):
        with self.canvas:
            Color(1, 1, 1)
            # self.line = Line(points=[100, 0, 100, 100])
            for i in range(0, self.H_NUM_LINES):
                self.h_line.append(Line())

    def update_h_line(self):
        start_index = -int(self.V_NUM_LINES/2) + 1
        end_index = start_index + self.V_NUM_LINES - 1
        
        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)

        for i in range(0, self.H_NUM_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)

            self.h_line[i].points = [x1, y1, x2, y2]

    def transform(self, x, y):
        #return self.transform_2D(x, y)
        return self.transform_perspective(x, y)

    def transform_2D(self, x, y):
        return int(x), int(y)

    def transform_perspective(self, x, y):
        lin_y = y * self.perspective_point_y / self.height
        if lin_y > self.perspective_point_y:
            lin_y = self.perspective_point_y

        diff_x = x - self.perspective_point_x
        diff_y = self.perspective_point_y - lin_y
        factor_y = diff_y/self.perspective_point_y
        factor_y = pow(factor_y, 4)

        tr_x = self.perspective_point_x + diff_x * factor_y
        tr_y = self.perspective_point_y - factor_y * self.perspective_point_y
        return int(tr_x), int(tr_y)

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'left':
            self.current_speed_x = self.SPEED_X
        elif keycode[1] == 'right':
            self.current_speed_x = -self.SPEED_X
        return True
    
    def on_keyboard_up(self, keyboard, keycode):
        self.current_speed_x = 0
        return True

    def on_touch_down(self, touch):
        if not self.game_over and self.start_game:
            if touch.x < self.width/2:
                self.current_speed_x = self.SPEED_X
            else:
                self.current_speed_x = -self.SPEED_X
        return super(RelativeLayout, self).on_touch_down(touch)
        
    def on_touch_up(self, touch):
        self.current_speed_x = 0

    def update(self, dt):
        #print("update called")
        time_factor = dt*60
        self.update_v_line()
        self.update_h_line()
        self.update_tiles()
        self.update_ship()
        
        if not self.game_over and self.start_game:
            speed_y = self.SPEED * self.height / 100
            self.current_offset_y += speed_y * time_factor
            
            spacing_y = self.H_LINES_SPACING*self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.your_score = f"SCORE: {str(self.current_y_loop)}"
                self.generate_tile_points()
                #print(f"loop {str(self.current_y_loop)}")
        
            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor
        
        if not self.check_ship_collision() and not self.game_over:
            self.game_over = True
            self.menu_title = "G  A  M  E   O  V  E  R"
            self.menu_btn_title = "RESTART"
            self.menu_widget.opacity = 1
            self.music1.stop()
            self.gameover_impact.play()
            Clock.schedule_once(self.play_game_over, 3)
            print("GAMEOVER")

    def play_game_over(self, dt):
        if self.game_over:
            self.gameover_voice.play()

    def on_menu_button_press(self):
        print("Game start")
        if self.game_over:
            self.restart.play()
        else:
            self.begin.play()
        
        self.music1.play()
        self.reset_game()
        self.start_game = True
        self.menu_widget.opacity = 0
    
class GalaxyApp(App):
    pass



GalaxyApp().run()
