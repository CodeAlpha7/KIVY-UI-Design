from kivy_config_helper import config_kivy

scr_w, scr_h = config_kivy(window_width=800, window_height=800,
                          simulate_device=False, simulate_dpi=300, simulate_density=1.0)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
import json
from kivy.uix.spinner import Spinner
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.properties import ListProperty, ObjectProperty
from kivy.animation import Animation
from kivy.core.audio import SoundLoader
from math import sqrt, pi, sin, cos
from kivy.clock import Clock
from datetime import datetime, timedelta
from functools import partial

class GameOverScreen(Screen):
    def __init__(self, winner, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        
        title = Label(text='Game Over!',
                     font_size=dp(50),
                     pos_hint={'center_x': 0.5, 'center_y': 0.7})

        winner_label = Label(text=winner,
                           font_size=dp(30),
                           pos_hint={'center_x': 0.5, 'center_y': 0.5})

        menu_btn = Button(text='Return to Menu',
                         size_hint=(0.3, 0.1),
                         pos_hint={'center_x': 0.5, 'center_y': 0.3})
        menu_btn.bind(on_press=self.return_to_menu)

        layout.add_widget(title)
        layout.add_widget(winner_label)
        layout.add_widget(menu_btn)
        self.add_widget(layout)
    
    def return_to_menu(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = 'start'

class GamePiece(Button):
    def __init__(self, team, **kwargs):
        super().__init__(**kwargs)
        self.team = team
        self.size_hint = (None, None)
        self.selected = False
        self.background_color = (0, 0, 0, 0)
        self.glow_color = (1, 1, 1, 0.5)

    def update_piece(self, *args):
        if not self.parent:
            return
        
        self.canvas.before.clear()
        with self.canvas.before:
            if self.selected:
                Color(*self.glow_color)
                piece_size = min(self.parent.width, self.parent.height) * 0.9
                glow_pos = (
                    self.parent.x + (self.parent.width - piece_size) / 2,
                    self.parent.y + (self.parent.height - piece_size) / 2
                )
                Ellipse(pos=glow_pos, size=(piece_size, piece_size))

            if self.team == 1:
                Color(0.9, 0.2, 0.2, 1)
            else:
                Color(0.2, 0.2, 0.9, 1)
            Ellipse(pos=self.pos, size=self.size)

    def on_size(self, *args):
        self.update_piece()

    def on_pos(self, *args):
        self.update_piece()
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.parent:
                self.parent.dispatch('on_press')
            return True
        return super().on_touch_down(touch)


class GameCell(Button):
    def __init__(self, row, col, cell_type, **kwargs):
        super().__init__(**kwargs)
        self.row = row
        self.col = col
        self.cell_type = cell_type
        self.piece = None
        self.highlight_color = (0.3, 0.8, 0.3, 0.4)
        self.background_color = (0, 0, 0, 0)
        self.bind(size=self.update_cell, pos=self.update_cell)

    def update_cell(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.cell_type == 9:
                Color(0.25, 0.25, 0.25, 1)
            else:
                Color(0.1, 0.4, 0.1, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            Color(0.9, 0.9, 0.9, 0.7)
            line_width = dp(1.5)
            Rectangle(pos=self.pos, size=(self.width, line_width))
            Rectangle(pos=self.pos, size=(line_width, self.height))
            Rectangle(pos=(self.pos[0], self.pos[1] + self.height - line_width), 
                     size=(self.width, line_width))
            Rectangle(pos=(self.pos[0] + self.width - line_width, self.pos[1]), 
                     size=(line_width, self.height))

        # Update piece position if exists - else dont.

        if self.piece:
            piece_size = min(self.width, self.height) * 0.8
            self.piece.size = (piece_size, piece_size)
            self.piece.pos = (
                self.x + (self.width - piece_size) / 2,
                self.y + (self.height - piece_size) / 2
            )

class GameScreen(Screen):
    board_state = ListProperty([[0]*7 for _ in range(7)])
    selected_piece = ObjectProperty(None, allownone=True)

    def __init__(self, level_data, time_limit=None, **kwargs):
        super().__init__(**kwargs)
        self.level_data = level_data
        self.time_limit = time_limit
        self.current_team = 1                                                   # Team A starts
        
        main_layout = FloatLayout()

        if time_limit:
            self.time_remaining = {
                1: timedelta(minutes=time_limit),
                2: timedelta(minutes=time_limit)
            }
            
            self.timer_a = Label(
                text=self.format_time(self.time_remaining[1]) if time_limit else "Unlimited",
                pos_hint={'x': 0.05, 'top': 0.935},
                size_hint=(None, None),
                size=(dp(150), dp(50)),
                font_size=dp(20),
                bold=True
            )
            self.timer_b = Label(
                text=self.format_time(self.time_remaining[2]) if time_limit else "Unlimited",
                pos_hint={'right': 0.95, 'top': 0.935},
                size_hint=(None, None),
                size=(dp(150), dp(50)),
                font_size=dp(20),
                bold=True
            )

            self.center_timer = Label(
                text="",
                pos_hint={'center_x': 0.5, 'y': 0.94},
                size_hint=(None, None),
                size=(dp(200), dp(50)),
                font_size=dp(20),
                bold=True
            )
            main_layout.add_widget(self.center_timer)
            main_layout.add_widget(self.timer_a)
            main_layout.add_widget(self.timer_b)
            
            Clock.schedule_interval(self.update_timer, 1.0)

        self.init_sounds()
        
        self.board_layout = GridLayout(
            cols=7,
            spacing=dp(2),
            padding=dp(20),
            size_hint=(0.8, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        self.board_state = [[0]*7 for _ in range(7)]
        self.board_state[0][0] = self.board_state[0][6] = 1
        self.board_state[6][0] = self.board_state[6][6] = 2

        self.cells = {}
        for row in range(7):
            for col in range(7):
                cell_type = level_data['board'][row][col]
                cell = GameCell(row=row, col=col, cell_type=cell_type)
                cell.bind(on_press=self.on_cell_press)
                self.cells[(row, col)] = cell
                self.board_layout.add_widget(cell)

                if cell_type in (1, 2):
                    piece = GamePiece(team=cell_type)
                    cell.piece = piece
                    cell.add_widget(piece)
                    piece.update_piece()

        main_layout.add_widget(self.board_layout)
        
        self.team_a_score = Label(
            text="Team A: 2",
            pos_hint={'x': 0.05, 'y': 0.92},
            size_hint=(None, None),
            size=(dp(150), dp(50)),
            font_size=dp(24),
            bold=True
        )
        self.team_b_score = Label(
            text="Team B: 2",
            pos_hint={'right': 0.95, 'y': 0.92},
            size_hint=(None, None),
            size=(dp(150), dp(50)),
            font_size=dp(24),
            bold=True
        )
        main_layout.add_widget(self.team_a_score)
        main_layout.add_widget(self.team_b_score)

        self.turn_indicator = Label(
            text="Current Turn: Team A",
            pos_hint={'center_x': 0.5, 'y': 0.9},
            size_hint=(None, None),
            size=(dp(200), dp(50)),
            font_size=dp(20)
        )
        main_layout.add_widget(self.turn_indicator)

        self.add_widget(main_layout)
        self.update_scores()

    def on_cell_press(self, cell):
        if cell.cell_type == 9:
            return
        
        for c in self.cells.values():
            if c.piece:
                c.piece.disabled = (c.piece.team != self.current_team)
        
        if self.selected_piece:
            if self.is_valid_move(self.selected_piece.parent, cell):
                self.make_move(self.selected_piece.parent, cell)
            self.clear_selection()
        elif cell.piece and cell.piece.team == self.current_team:
            self.select_piece(cell.piece)
            self.highlight_valid_moves(cell)

    def select_piece(self, piece):
        self.clear_selection()
        piece.selected = True
        piece.update_piece()
        self.selected_piece = piece
        self.highlight_valid_moves(piece.parent)
        self.play_sound('select')

    def clear_selection(self):
        if self.selected_piece:
            self.selected_piece.selected = False
            self.selected_piece.update_piece()
            self.selected_piece = None
        self.clear_highlights()

    def update_scores(self):
        team_a_count = sum(1 for cell in self.cells.values() 
                          if cell.piece and cell.piece.team == 1)
        team_b_count = sum(1 for cell in self.cells.values() 
                          if cell.piece and cell.piece.team == 2)
        self.team_a_score.text = f'Team A: {team_a_count}'
        self.team_b_score.text = f'Team B: {team_b_count}'

    def is_valid_move(self, from_cell, to_cell):
        if to_cell.piece is not None or to_cell.cell_type == 9:
            return False
        
        dx = abs(from_cell.row - to_cell.row)
        dy = abs(from_cell.col - to_cell.col)
        
        return dx <= 2 and dy <= 2 and (dx > 0 or dy > 0)

    def highlight_valid_moves(self, from_cell):
        self.clear_highlights()
        for cell in self.cells.values():
            if self.is_valid_move(from_cell, cell):
                with cell.canvas.before:
                    Color(*cell.highlight_color)
                    size = cell.size[0] * 0.95
                    pos_x = cell.pos[0] + (cell.size[0] - size) / 2
                    pos_y = cell.pos[1] + (cell.size[1] - size) / 2
                    Rectangle(pos=(pos_x, pos_y), size=(size, size))
                    
                    Color(1, 1, 1, 0.3)
                    line_width = dp(2)
                    Rectangle(pos=cell.pos, size=(cell.width, line_width))
                    Rectangle(pos=cell.pos, size=(line_width, cell.height))
                    Rectangle(pos=(cell.x, cell.y + cell.height - line_width), 
                             size=(cell.width, line_width))
                    Rectangle(pos=(cell.x + cell.width - line_width, cell.y), 
                             size=(line_width, cell.height))

    def clear_highlights(self):
        for cell in self.cells.values():
            cell.canvas.before.clear()
            cell.update_cell()

    def make_move(self, from_cell, to_cell):
        dx = abs(from_cell.row - to_cell.row)
        dy = abs(from_cell.col - to_cell.col)
        is_jump = max(dx, dy) == 2

        piece_size = min(to_cell.width, to_cell.height) * 0.8
        new_piece = GamePiece(team=self.current_team)
        new_piece.size = (piece_size, piece_size)
        
        # Set initial position
        start_pos = (
            from_cell.x + (from_cell.width - piece_size) / 2,
            from_cell.y + (from_cell.height - piece_size) / 2
        )
        end_pos = (
            to_cell.x + (to_cell.width - piece_size) / 2,
            to_cell.y + (to_cell.height - piece_size) / 2
        )
        
        to_cell.piece = new_piece
        to_cell.add_widget(new_piece)
        
        if is_jump:
            from_cell.remove_widget(self.selected_piece)
            from_cell.piece = None
            self.board_state[from_cell.row][from_cell.col] = 0
            
            new_piece.pos = start_pos
            
            # Jump animation - a small arc from behind
            anim = Animation(pos=end_pos, duration=0.3, t='out_quad')
            self.play_sound('jump')
        else:
            # Clone animation - just zooms/resizings
            new_piece.pos = (
                to_cell.x + (to_cell.width - piece_size) / 2,
                to_cell.y + (to_cell.height - piece_size) / 2
            )
            
            # Simple scale animation for clone
            new_piece.size = (0, 0)
            anim = Animation(size=(piece_size, piece_size), duration=0.3, t='out_quad')
            self.play_sound('clone')

        self.board_state[to_cell.row][to_cell.col] = self.current_team
        
        def after_move_complete(animation, widget):
            self.convert_adjacent_pieces(to_cell)
            Clock.schedule_once(self.finish_turn, 0.3)
        
        anim.bind(on_complete=after_move_complete)
        anim.start(new_piece)

    def convert_adjacent_pieces(self, cell):
        converted = False
        animations = []                         # Track all animations
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                    
                adj_row = cell.row + dx
                adj_col = cell.col + dy
                
                if (adj_row, adj_col) in self.cells:
                    adj_cell = self.cells[(adj_row, adj_col)]
                    if (adj_cell.piece and adj_cell.piece.team != self.current_team):
                        # Store the original team for the animation
                        piece = adj_cell.piece
                        piece.team = self.current_team
                        
                        # Get the piece's current size and position
                        original_size = piece.size[0]
                        center_x = piece.pos[0] + original_size/2
                        center_y = piece.pos[1] + original_size/2

                        # Creating grow animation
                        grow = Animation(
                            size=(original_size * 1.2, original_size * 1.2),
                            duration=0.15,
                            t='out_quad'
                        )
                        
                        # Creating shrink animation
                        shrink = Animation(
                            size=(original_size, original_size),
                            duration=0.15,
                            t='in_quad'
                        )
                        
                        # Combine animations - to produce that wavy motion
                        anim = grow + shrink

                        # Keep piece centered and visible during animation
                        def create_update_pos(piece_center_x, piece_center_y):
                            def update_pos(animation, widget, progress):
                                current_size = widget.size[0]
                                widget.pos = (
                                    piece_center_x - current_size/2,
                                    piece_center_y - current_size/2
                                )
                                widget.update_piece()
                            return update_pos

                        # Bind position update to this specific piece's animation - make sure during all that movement the piece itself moves relative to center point of cell and stays there.
                        anim.bind(on_progress=create_update_pos(center_x, center_y))
                        
                        # Start the animation
                        anim.start(piece)
                        animations.append(anim)
                        converted = True
        
        if converted:
            self.play_sound('convert')

    def animate_conversion(self, piece):
        original_size = piece.size[0]
        original_pos = piece.pos
        
        anim1 = Animation(
            size=(original_size * 1.2, original_size * 1.2),
            duration=0.1,
            t='out_quad'
        )
        
        anim2 = Animation(
            size=(original_size * 0.8, original_size * 0.8),
            duration=0.1,
            t='in_quad'
        )
        
        anim3 = Animation(
            size=(original_size, original_size),
            duration=0.1,
            t='out_quad'
        )
        
        anim = anim1 + anim2 + anim3
        
        def update_pos(animation, widget, progress):
            current_size = widget.size[0]
            widget.pos = (
                original_pos[0] - (current_size - original_size)/2,
                original_pos[1] - (current_size - original_size)/2
            )
            widget.update_piece()
        
        anim.bind(on_progress=update_pos)
        anim.start(piece)

    def finish_turn(self, dt=None):
        self.current_team = 3 - self.current_team
        self.turn_indicator.text = f"Current Turn: Team {'A' if self.current_team == 1 else 'B'}"
        self.update_scores()
        self.check_game_end()

    def init_sounds(self):
        self.sounds = {}
        for sound_name in ['jump', 'clone', 'convert', 'game_end', 'select']:
            sound = SoundLoader.load(f'sounds/{sound_name}.wav')
            if sound:
                self.sounds[sound_name] = sound
            else:
                print(f"Warning: Sound file '{sound_name}' not found.")

    def play_sound(self, sound_type):
        if sound_type in self.sounds and self.sounds[sound_type]:
            try:
                self.sounds[sound_type].play()
            except Exception as e:
                print(f"Error playing {sound_type} sound: {e}")

    def format_time(self, td):
        minutes = int(td.total_seconds() // 60)
        seconds = int(td.total_seconds() % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def update_timer(self, dt):
        if not self.time_limit:
            return

        self.time_remaining[self.current_team] -= timedelta(seconds=1)          #reference: https://www.geeksforgeeks.org/python-datetime-timedelta-function/
        current_time = self.time_remaining[self.current_team]

        if current_time.total_seconds() <= 0:
            self.time_out()
            return

        time_str = self.format_time(current_time)
        if self.current_team == 1:
            self.timer_a.text = time_str
            if self.center_timer:
                self.center_timer.text = f"Team A: {time_str}"
        else:
            self.timer_b.text = time_str
            if self.center_timer:
                self.center_timer.text = f"Team B: {time_str}"

    def time_out(self):
        Clock.unschedule(self.update_timer)
        winner = 3 - self.current_team
        self.play_sound('game_end')
        self.show_game_over(winner)

    def check_game_end(self):
        team_a_count = sum(1 for cell in self.cells.values() 
                          if cell.piece and cell.piece.team == 1)
        team_b_count = sum(1 for cell in self.cells.values() 
                          if cell.piece and cell.piece.team == 2)
        
        if team_a_count == 0 or team_b_count == 0:
            self.game_over()
            return

        empty_spaces = sum(1 for cell in self.cells.values() 
                          if cell.cell_type != 9 and not cell.piece)

        if empty_spaces < 5:
            has_moves = False
            for cell in self.cells.values():
                if cell.piece and cell.piece.team == self.current_team:
                    for target in self.cells.values():
                        if self.is_valid_move(cell, target):
                            has_moves = True
                            break
                if has_moves:
                    break

            if not has_moves:
                self.game_over()

    def game_over(self):
        Clock.unschedule(self.update_timer)
        team_a_count = sum(1 for cell in self.cells.values() 
                        if cell.piece and cell.piece.team == 1)
        team_b_count = sum(1 for cell in self.cells.values() 
                        if cell.piece and cell.piece.team == 2)
        
        if team_a_count > team_b_count:
            winner = 1
        elif team_b_count > team_a_count:
            winner = 2
        else:
            winner = None
            
        self.play_sound('game_end')
        self.show_game_over(winner)

    def show_game_over(self, winner):
        if winner is None:
            message = "It's a draw!"
        else:
            message = f"Winner: Team {'A' if winner == 1 else 'B'}"

        self.manager.add_widget(GameOverScreen(winner=message, name='gameover'))
        self.manager.transition.direction = 'left'
        self.manager.current = 'gameover'

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = FloatLayout()
        
        title = Label(text='Ataxx', 
                     size_hint=(None, None),
                     pos_hint={'center_x': 0.5, 'center_y': 0.9},
                     font_size=dp(40))
        main_layout.add_widget(title)
        
        options_layout = BoxLayout(orientation='vertical', 
                                 spacing=dp(20),
                                 size_hint=(0.8, 0.6),
                                 pos_hint={'center_x': 0.5, 'center_y': 0.5})
        
        self.level_spinner = Spinner(text='Select Level',
                                   values=self.load_level_names(),
                                   size_hint_y=None,
                                   height=dp(50))
        
        self.mode_spinner = Spinner(text='Player vs Player',
                                  values=('Player vs Player', 'Player vs Computer'),
                                  size_hint_y=None,
                                  height=dp(50))
        
        self.time_spinner = Spinner(text='Unlimited Time',
                                  values=('Unlimited Time', '3 Minutes', '5 Minutes', '10 Minutes'),
                                  size_hint_y=None,
                                  height=dp(50))
        
        start_button = Button(text='Start Game',
                            size_hint_y=None,
                            height=dp(50))
        start_button.bind(on_press=self.start_game)
        
        options_layout.add_widget(self.level_spinner)
        options_layout.add_widget(self.time_spinner)
        options_layout.add_widget(self.mode_spinner)
        options_layout.add_widget(start_button)
        
        main_layout.add_widget(options_layout)
        self.add_widget(main_layout)

    def load_level_names(self):
        try:
            with open('levels-1.txt', 'r') as f:
                levels = json.load(f)
                return [level['name'] for level in levels]
        except Exception as e:
            print(f"Error loading levels: {e}")
            return ['Level 1']

    def start_game(self, instance):
        if self.level_spinner.text == 'Select Level':
            print("Please select a level first")
            return 

        try:
            with open('levels-1.txt', 'r') as f:
                levels = json.load(f)
                selected_level = self.level_spinner.text
                level_data = next(level for level in levels if level['name'] == selected_level)
            
            time_mode = self.time_spinner.text
            time_limit = None if time_mode == 'Unlimited Time' else int(time_mode.split()[0])
            
            app = App.get_running_app()
            app.start_game(level_data, time_limit)
        
        except Exception as e:
            print(f"Error starting game: {e}")

class AtaxxApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(StartScreen(name='start'))
        return self.sm

    def start_game(self, level_data, time_limit=None):
        if 'game' in self.sm.screen_names:
            self.sm.remove_widget(self.sm.get_screen('game'))
        
        game_screen = GameScreen(level_data=level_data, 
                               time_limit=time_limit,
                               name='game')
        self.sm.add_widget(game_screen)
        self.sm.transition.direction = 'left'
        self.sm.current = 'game'

if __name__ == '__main__':
    AtaxxApp().run()