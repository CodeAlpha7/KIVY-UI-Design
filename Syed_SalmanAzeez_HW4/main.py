# main.py
from kivy_config_helper import config_kivy

scr_w, scr_h = config_kivy(window_width=800, window_height=600,
                           simulate_device=False, simulate_dpi=300, simulate_density=1.0)

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy_text_metrics import TextMetrics
from kivy.uix.settings import SettingsWithSidebar
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty, ObjectProperty
from kivy.graphics import Color, Rectangle, Line
from kivy.core.text import Label as CoreLabel
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.settings import SettingItem
from kivy.gesture import Gesture, GestureDatabase
from kivy.graphics import Color, Line, Ellipse
from math import cos, sin, radians
import math
from functools import partial
import os
import os.path
import re
import json
import vlc
from typing import List, Tuple

def parse_timecoded_text(text) -> List[Tuple[str, float, float]]:
    segments = re.split(r'(\[t\d+\.\d+\])|(\\\[t\d+\.\d+\])', text)         # regular python regex as explained in HW1
    segments = [seg for seg in segments if seg]
    
    parsed_output = []
    current_words = []
    last_timestamp = 0.0
    
    for segment in segments:
        if segment.startswith('\\[t'):
            current_words.append(segment.replace('\\', ''))
        elif segment.startswith('[t'):
            current_time = float(segment[2:-1])
            if current_words:
                word_count = len(current_words)
                time_interval = current_time - last_timestamp
                parsed_output.extend([(word, last_timestamp + i*time_interval/word_count, 
                                       last_timestamp + (i+1)*time_interval/word_count) 
                                      for i, word in enumerate(current_words)])
                current_words = []
            last_timestamp = current_time
        else:
            current_words.extend(segment.split())
    
    if current_words:
        average_time_per_word = 60 / 300                                            # Default to 300 WPM if no timestamps
        final_time = last_timestamp + average_time_per_word * len(current_words)
        parsed_output.extend([(word, last_timestamp + i*average_time_per_word, 
                               last_timestamp + (i+1)*average_time_per_word) 
                              for i, word in enumerate(current_words)])
    
    return parsed_output

def euclidean_distance(p1, p2):                                                         # Copied from HW4 description TIPS section. 
    """Compute Euclidean distance between two points."""                                # Will keep comment format similar for future function descriptions for consistency
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def better_unistroke_normalizer(pts, total_pts=32):
    """Normalize a unistroke to have exactly total_pts points."""
    if len(pts) < 2:
        raise ValueError("At least two distinct points are required.")

    total_length = sum(euclidean_distance(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
    if total_length == 0:
        raise ValueError("Total length of stroke is zero. Invalid input.")

    segment_length = total_length / (total_pts - 1)
    new_pts = [pts[0]]
    accumulated_dist = 0.0

    for i in range(1, len(pts)):
        p1, p2 = pts[i - 1], pts[i]
        dist = euclidean_distance(p1, p2)
        if dist == 0:
            continue

        while accumulated_dist + dist >= segment_length:
            t = (segment_length - accumulated_dist) / dist
            new_x = p1[0] + t * (p2[0] - p1[0])
            new_y = p1[1] + t * (p2[1] - p1[1])
            new_pts.append((new_x, new_y))
            accumulated_dist = 0.0
            p1 = (new_x, new_y)
            dist = euclidean_distance(p1, p2)
        accumulated_dist += dist

    if len(new_pts) < total_pts:
        new_pts.append(pts[-1])

    return new_pts[:total_pts]

def simplegesture(name, point_list):
    g = Gesture()
    g.add_stroke(point_list)
    g.normalize()
    g.name = name
    return g

def create_l_shape():
    pts = [(0.3, 0.8), (0.3, 0.2), (0.8, 0.2)]  
    pts = better_unistroke_normalizer(pts)
    g = Gesture()
    g.add_stroke(pts)
    g.normalize()
    g.name = 'l_shape'  
    return g

def create_reverse_l():
    pts = [(0.7, 0.8), (0.7, 0.2), (0.2, 0.2)] 
    pts = better_unistroke_normalizer(pts)
    g = Gesture()
    g.add_stroke(pts)
    g.normalize()
    g.name = 'reverse_l'
    return g

# def create_horizontal_swipe():
#     pts = [(0.3, 0.5), (0.7, 0.5)] 
#     pts = better_unistroke_normalizer(pts)
#     g = Gesture()
#     g.add_stroke(pts)
#     g.normalize()
#     g.name = 'horizontal_swipe'
#     return g

# def create_vertical_swipe():
#     pts = [(0.5, 0.3), (0.5, 0.7)] 
#     pts = better_unistroke_normalizer(pts)
#     g = Gesture()
#     g.add_stroke(pts)
#     g.normalize()
#     g.name = 'vertical_swipe'
#     return g

def create_left_swipe():
    pts = [(0.7, 0.5), (0.3, 0.5)]              # Right to left motion - Seek forward 5 words
    pts = better_unistroke_normalizer(pts)
    g = Gesture()
    g.add_stroke(pts)
    g.normalize()
    g.name = 'left_swipe'
    return g

def create_right_swipe():
    pts = [(0.3, 0.5), (0.7, 0.5)]              # Left to right motion - Seek backward 5 words
    pts = better_unistroke_normalizer(pts)
    g = Gesture()
    g.add_stroke(pts)
    g.normalize()
    g.name = 'right_swipe'
    return g

def create_up_swipe():
    pts = [(0.5, 0.3), (0.5, 0.7)]              # Bottom to top motion - Increase speed
    pts = better_unistroke_normalizer(pts)
    g = Gesture()
    g.add_stroke(pts)
    g.normalize()
    g.name = 'up_swipe'
    return g

def create_down_swipe():
    pts = [(0.5, 0.7), (0.5, 0.3)]              # Top to bottom motion - Decrease Speed
    pts = better_unistroke_normalizer(pts)
    g = Gesture()
    g.add_stroke(pts)
    g.normalize()
    g.name = 'down_swipe'
    return g

def create_diagonal_swipe():
    pts = [(0.2, 0.2), (0.8, 0.8)]              # Bottom-left to top-right diagonal - Toggle Play/Pause
    pts = better_unistroke_normalizer(pts)
    g = Gesture()
    g.add_stroke(pts)
    g.normalize()
    g.name = 'diagonal_swipe'
    return g

class ScaledButton(Button):                                             # Implemented this before the updated kivy_config file was posted which caused a lot of issues with text scaling
    def __init__(self, **kwargs):                                       # Later when kivy_config was updated, I imported the new code in and left these in just cause why not.
        super(ScaledButton, self).__init__(**kwargs)
        self.font_size = dp(14)  

class ScaledLabel(Label):
    def __init__(self, **kwargs):
        super(ScaledLabel, self).__init__(**kwargs)
        self.font_size = dp(14)  

class RSVPReader(BoxLayout):
    current_word = StringProperty('')
    is_playing = BooleanProperty(False)
    wpm = NumericProperty(150)                              # Default WPM of 300. EDIT: changed to 150 to normalize audio and sync
    font_name = StringProperty('Helvetica-Bold.ttf')
    font_size = NumericProperty(dp(40))                     # Default font size of 40

    def __init__(self, **kwargs):
        super(RSVPReader, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(20)

        # Adding gesture recognition
        self.gdb = GestureDatabase()                                    # reference: https://kivy.org/doc/stable/api-kivy.gesture.html

        # Create and store each gesture separately
        self.left_swipe = create_left_swipe()
        self.right_swipe = create_right_swipe()
        self.up_swipe = create_up_swipe()
        self.down_swipe = create_down_swipe()
        self.l_shape = create_l_shape()
        self.reverse_l = create_reverse_l()
        self.diagonal_swipe = create_diagonal_swipe()
        
        # Add all gestures to database
        self.gdb.add_gesture(self.left_swipe)
        self.gdb.add_gesture(self.right_swipe)
        self.gdb.add_gesture(self.up_swipe)
        self.gdb.add_gesture(self.down_swipe)
        self.gdb.add_gesture(self.l_shape)
        self.gdb.add_gesture(self.reverse_l)
        self.gdb.add_gesture(self.diagonal_swipe)

        # Add VLC instance                                      # references: https://www.geeksforgeeks.org/vlc-module-in-python-an-introduction/ AND https://pypi.org/project/python-vlc/
        self.vlc_instance = vlc.Instance('--quiet')                     # Add quiet tag to avoid console clutter and allow debugging to check correct gesture recognition.
        self.player = self.vlc_instance.media_player_new()
        self.has_audio = False
        self.base_wpm = 300                                 # Will be calculated from timecode
        
        # Adding keyboard binding
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        
        # Configuring audio player
        # self.player = None                
        self.has_audio = False

        # Add title label
        title_label = Label(
            text="RSVP Text Reader",
            size_hint_y=None,
            height=dp(40),
            font_size=dp(30),
            color=(1, 1, 1, 1)
        )
        self.add_widget(title_label)

        self.words = []
        self.current_word_index = 0

        # Top layout for word display and settings button
        top_layout = BoxLayout(size_hint_y=0.7)
        self.word_container = BoxLayout(size_hint=(0.8, 0.6), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        with self.word_container.canvas.before:
            Color(0.1, 0.1, 0.1, 1)  
            self.word_container.rect = Rectangle(size=self.word_container.size, pos=self.word_container.pos)
        self.word_container.bind(size=self._update_rect, pos=self._update_rect)
        top_layout.add_widget(self.word_container)
        
        settings_btn = Button(text='Settings', size_hint=(None, None), size=(dp(80), dp(50)), pos_hint={'right': 1, 'top': 1})
        settings_btn.bind(on_press=self.open_settings)
        top_layout.add_widget(settings_btn)
        
        self.add_widget(top_layout)

        # File chooser and play/pause buttons
        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(20), padding=[dp(20), 0, dp(20), 0])
        self.file_button = Button(text='Choose File', size_hint_x=0.4)
        self.file_button.bind(on_press=self.show_file_chooser)
        button_layout.add_widget(self.file_button)

        self.play_pause_btn = Button(text='Play', disabled=True, size_hint_x=0.4)
        self.play_pause_btn.bind(on_press=self.toggle_play_pause)
        button_layout.add_widget(self.play_pause_btn)

        self.add_widget(button_layout)

        Clock.schedule_interval(self.update_word_display, 1/60)

    def _update_rect(self, instance, value):
        self.word_container.rect.pos = instance.pos
        self.word_container.rect.size = instance.size

    def show_file_chooser(self, instance):                                  # Updated to handle audio files too
        content = BoxLayout(orientation='vertical')
        self.file_chooser = FileChooserListView(filters=['*.txt', '*.timecode', '*.wav', '*.mp3'])
        content.add_widget(self.file_chooser)
        
        select_button = ScaledButton(text='Select', size_hint_y=None, height=dp(50))
        select_button.bind(on_press=self.load_file)
        content.add_widget(select_button)
        
        self.popup = Popup(title='Choose a file', content=content, size_hint=(0.9, 0.9))
        self.popup.open()

    def load_file(self, instance):
        if self.file_chooser.selection:
            filepath = self.file_chooser.selection[0]
            try:
                # Get directory and base filename
                file_dir = os.path.dirname(filepath)
                base_name = os.path.splitext(os.path.basename(filepath))[0]
                
                # Handle audio files                                                                
                if filepath.endswith(('.wav', '.mp3')):
                    # Look for matching timecode file in same directory
                    timecode_path = os.path.join(file_dir, base_name + '.timecode')
                    
                    if not os.path.exists(timecode_path):
                        print(f"Error: No matching .timecode file found for {base_name}")
                        return
                        
                    # Load timecode file first
                    with open(timecode_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        self.words = parse_timecoded_text(content)
                        if self.words:
                            self.base_wpm = self.calculate_base_wpm(self.words)
                    
                    # Then setup audio                                                    # this will create vlc player object AFTER text which causes a small delay addressed later
                    self.setup_audio(filepath)
                    print(f"Audio file loaded: {filepath}")
                    print(f"Timecode file loaded: {timecode_path}")
                    
                # Handle timecode files
                elif filepath.endswith('.timecode'):
                    # Look for matching audio file in same directory
                    audio_path = None
                    for ext in ['.wav', '.mp3']:
                        potential_audio = os.path.join(file_dir, base_name + ext)
                        if os.path.exists(potential_audio):
                            audio_path = potential_audio
                            break
                            
                    # Load timecode content
                    with open(filepath, 'r', encoding='utf-8') as file:
                        content = file.read()
                        self.words = parse_timecoded_text(content)
                        if self.words:
                            self.base_wpm = self.calculate_base_wpm(self.words)
                    print(f"Timecode file loaded: {filepath}")
                    
                    # Setup audio if found
                    if audio_path:
                        self.setup_audio(audio_path)
                        print(f"Matching audio file loaded: {audio_path}")
                    else:
                        self.has_audio = False
                        if self.player:
                            self.player.stop()
                        print("No matching audio file found")
                        
                # Handle regular text files
                else:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        content = file.read()
                        self.words = [(word, i/self.wpm*60, (i+1)/self.wpm*60) 
                                    for i, word in enumerate(content.split())]
                    self.has_audio = False
                    if self.player:
                        self.player.stop()
                    print(f"Text file loaded: {filepath}")

                # Common setup after successful load
                self.current_word_index = 0
                self.play_pause_btn.disabled = False
                self.popup.dismiss()
                
            except UnicodeDecodeError:                                                  # this was added to avoid audio file loading errors or handle them gracefully.
                print(f"Error: Cannot read {filepath} - file appears to be binary or uses unsupported encoding")
            except Exception as e:
                print(f"Error loading file: {str(e)}")
                print(f"File path: {filepath}")
                import traceback
                traceback.print_exc()

    def calculate_base_wpm(self, words):
        """Calculate base WPM from timecoded text"""
        if not words:
            return 300
        
        total_words = len(words)
        last_word = words[-1]
        total_time_minutes = last_word[2] / 60              # Convert seconds to minutes
        return int(total_words / total_time_minutes)

    def setup_audio(self, audio_path):
        """Initialize audio player with the given file"""
        try:
            if self.player:
                self.player.stop()              # Stop any existing playback
                
            media = self.vlc_instance.media_new(str(audio_path))        # Convert path to string
            self.player.set_media(media)
            self.has_audio = True
            self.sync_audio_speed()
            print(f"Audio setup successful: {audio_path}")
        except Exception as e:
            print(f"Error setting up audio: {e}")
            self.has_audio = False

    def sync_audio_speed(self):
        """Synchronize audio playback speed with current WPM"""
        if not self.has_audio:
            return
        try:
            speed_ratio = self.wpm / self.base_wpm
            self.player.set_rate(float(speed_ratio))
            print(f"Audio speed set to {speed_ratio:.2f}x")
        except Exception as e:
            print(f"Error setting audio speed: {e}")

    def sync_audio_position(self):
        """Synchronize audio position with current word"""
        if not self.has_audio or not self.words or self.current_word_index >= len(self.words):
            return
        
        try:
            current_word = self.words[self.current_word_index]
            time_ms = int(current_word[1] * 1000)
            offset_ms = 550                                             # delay to handle vlc player instance creation delay - different coordinated start unintentionally, but it worked well, so left it in.
            self.player.set_time(max(0, time_ms + offset_ms))
            print(f"Audio synced to position: {time_ms + offset_ms}ms")
        except Exception as e:
            print(f"Error syncing audio position: {e}")
    
    def start_playback(self):
        """Helper method for synchronized start"""
        self.player.play()
        self.schedule_next_word()

    def toggle_play_pause(self, instance):
        self.is_playing = not self.is_playing
        if instance is not None:
            instance.text = 'Pause' if self.is_playing else 'Play'
        else:
            self.play_pause_btn.text = 'Pause' if self.is_playing else 'Play'
            
        if self.is_playing:
            if self.has_audio:
                # Reset and pre-buffer audio
                self.player.stop()
                self.player.play()
                self.player.set_time(int(self.words[self.current_word_index][1] * 1000))
                self.player.pause()
                # Small delay then coordinated start
                Clock.schedule_once(self.coordinated_start, 0.1)
            else:
                self.schedule_next_word()
        else:
            if self.has_audio:
                self.player.pause()
            Clock.unschedule(self.schedule_next_word)

    def coordinated_start(self, dt):
        """Ensure coordinated start of audio and text"""
        current_word = self.words[self.current_word_index]
        time_ms = int(current_word[1] * 1000)
        
        # Add a small negative offset (500ms = 0.5 seconds) - efforts to sync audio with text due to vlc initialization delays
        offset_ms = 1000
        self.player.set_time(max(0, time_ms + offset_ms))
        self.player.play()
        Clock.schedule_once(self.schedule_next_word, 0)



    def schedule_next_word(self, dt=0):
        if self.current_word_index < len(self.words):
            word, start_time, end_time = self.words[self.current_word_index]
            self.current_word = word
            
            # Calculate duration
            if self.has_audio:
                # Use actual time differences from timecode
                duration = end_time - start_time
                # Scale duration based on WPM ratio
                duration = duration * (self.base_wpm / self.wpm)
            else:
                # For non-audio files, use WPM-based timing
                duration = (end_time - start_time) * (300 / self.wpm)
            
            self.current_word_index += 1
            Clock.schedule_once(self.schedule_next_word, duration)
        else:
            self.is_playing = False
            self.play_pause_btn.text = 'Play'
            if self.has_audio:
                self.player.stop()


    def speed_up(self):
        old_wpm = self.wpm
        self.wpm = min(1000, self.wpm + 50)
        if self.wpm != old_wpm and self.has_audio:
            try:
                self.sync_audio_speed()
                # Re-sync position after speed change
                self.sync_audio_position()
            except Exception as e:
                print(f"Error adjusting speed: {e}")

    def speed_down(self):
        old_wpm = self.wpm
        self.wpm = max(50, self.wpm - 50)
        if self.wpm != old_wpm and self.has_audio:
            try:
                self.sync_audio_speed()
                # Re-sync position after speed change
                self.sync_audio_position()
            except Exception as e:
                print(f"Error adjusting speed: {e}")


    def update_word_display(self, *args):
        self.word_container.canvas.clear()
        if not self.words or self.current_word_index >= len(self.words):
            return

        word = self.words[self.current_word_index][0]
        focus_char_index = self.get_focus_character(word)
        
        try:
            font_path = os.path.join('Fonts', self.font_name)
            metrics = TextMetrics(font_path, int(self.font_size))
            glyph_attribs, ascender, descender = metrics.get_text_extents(word, (int(self.word_container.width), int(self.word_container.height)))

            # Calculate font size scaling factor (base font size is 40)
            font_scale = self.font_size / 40.0

            # Base spacing factors for font size 40             (same as HW3)
            word_length = len(word)
            if word_length <= 3:
                base_spacing = 0.105
                scale_rate = 0.6
            elif word_length == 4:
                base_spacing = 0.13
                scale_rate = 0.6
            elif word_length == 5:
                base_spacing = 0.17
                scale_rate = 0.6
            elif word_length <= 7:                                              # here, 0.6 is the scaling factor which determines how aggressive the scaling works.
                base_spacing = 0.215                                            # as font becomes bigger, characters overlap. So, we need to scale with font size.
                scale_rate = 0.7                                                # Greater the value, the more aggressive spacing becomes.
            elif word_length <= 9:                                              # longer words overlap more, so more aggressive spacing for words 7 characters or longer
                base_spacing = 0.28
                scale_rate = 0.7
            elif word_length == 10:
                base_spacing = 0.35
                scale_rate = 0.7
            else:
                base_spacing = 0.37
                scale_rate = 0.7

            # Scale spacing factor based on font size with appropriate scaling rate
            spacing_factor = base_spacing * (1 + (font_scale - 1) * scale_rate)                 

            # Calculate positions using x_advance
            total_advance = sum(glyph[6] * spacing_factor for glyph in glyph_attribs)
            focus_position = sum(glyph[6] * spacing_factor for glyph in glyph_attribs[:focus_char_index])               # referenced from kivy_text_metrices.py
            
            # Calculate the position to keep the focus character centered
            center_x = self.word_container.width / 2
            start_x = center_x - focus_position - (glyph_attribs[focus_char_index][6] * spacing_factor) / 2

            # Calculate baseline and line positions
            baseline_y = self.word_container.height * 1
            ascender_line = baseline_y + ascender * 2.5
            descender_line = baseline_y + descender * 2.5

            with self.word_container.canvas:
                # top and bottom baselines
                Color(0.5, 0.5, 0.5)
                Line(points=[35, ascender_line, self.word_container.width, ascender_line], width=1.2)
                Line(points=[35, descender_line, self.word_container.width, descender_line], width=1.2)

                # RED focus character indicator
                Color(1, 0, 0)
                top_mark_y = ascender_line - (dp(5) * (self.font_size*0.1))                             # scaling size of focus marker based on font size. 
                bottom_mark_y = descender_line + (dp(5) * (self.font_size*0.1))                         # We want it to increase in size along with baseline.
                Line(points=[center_x, top_mark_y, center_x, ascender_line], width=1.2)
                Line(points=[center_x, bottom_mark_y, center_x, descender_line], width=1.2)

                # Draw word
                x_offset = start_x
                y_offset = baseline_y

                for i, glyph in enumerate(glyph_attribs):
                    rect_x, rect_y, rect_w, rect_h, glyph_ascent, glyph_descent, x_advance = glyph
                    label = CoreLabel(text=word[i], font_size=int(self.font_size), font_name=font_path)
                    label.refresh()
                    texture = label.texture
                    if i == focus_char_index:
                        Color(1, 0, 0)                                                                  # Red color for focus character
                    else:
                        Color(1, 1, 1)                                                                  # White color for normal characters
                    Rectangle(pos=(x_offset, y_offset - descender), size=texture.size, texture=texture)
                    x_offset += x_advance * spacing_factor

        except Exception as e:
            print(f"Error in update_word_display: {e}")
            print(f"Current font: {self.font_name}")
            print(f"Current font path: {os.path.abspath(os.path.join('Fonts', self.font_name))}")


    def on_stop(self):                                      # Clean up the application when it's closed
        
        if self.has_audio:
            self.player.stop()
        self.vlc_instance.release()

        Clock.unschedule(self.update_word_display)
        try:
            # Clean up any remaining widget references
            self.word_container.canvas.clear()
            self.word_container.clear_widgets()
            self.clear_widgets()
        except:
            pass

    def get_focus_character(self, word):                   # simple heuristic to select focus character
        word_length = len(word)
        if word_length <= 2:
            return 0
        elif word_length <= 5:
            return 1
        elif word_length <= 9:
            return 2
        elif word_length <= 13:
            return 3
        else:
            return min(3, word_length // 3)

    def open_settings(self, instance):                      # default kivy settings menu: https://kivy.org/doc/stable/api-kivy.uix.settings.html
        app = App.get_running_app()
        app.open_settings()

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):                         # reference: https://stackoverflow.com/questions/17280341/how-do-you-check-for-keyboard-events-with-kivy
        if keycode[1] == 'spacebar':
            self.toggle_play_pause(None)
        elif keycode[1] == 'left':
            self.jump_back()
        elif keycode[1] == 'right':
            self.jump_forward()
        elif keycode[1] == 'up':
            self.speed_up()
        elif keycode[1] == 'down':
            self.speed_down()
        elif keycode[1] in "=": 
            self.font_bigger()
        elif keycode[1] in "-":  
            self.font_smaller()
        return True

    def on_touch_down(self, touch):
        if not self.word_container.collide_point(*touch.pos):
            return super(RSVPReader, self).on_touch_down(touch)
        
        touch.ud['line'] = Line(points=(touch.x, touch.y))
        with self.word_container.canvas:
            Color(1, 0, 0, 0.5)
            touch.ud['line'] = Line(points=(touch.x, touch.y))
        return True
    
    def on_touch_move(self, touch):
        if 'line' not in touch.ud:
            return super(RSVPReader, self).on_touch_move(touch)
        touch.ud['line'].points += [touch.x, touch.y]
        return True

    def on_touch_up(self, touch):
        if 'line' not in touch.ud:
            return super(RSVPReader, self).on_touch_up(touch)
                
        points = list(zip(touch.ud['line'].points[::2], touch.ud['line'].points[1::2]))
        
        # Clear gesture line - after single stroke (UNISTROKE ONLY)
        try:
            if hasattr(self.word_container.canvas, 'remove'):
                self.word_container.canvas.remove(touch.ud['line'])
        except:
            self.word_container.canvas.clear()

        try:
            points = better_unistroke_normalizer(points)
            gesture = Gesture()
            gesture.add_stroke(points)
            gesture.normalize()
            
            matched = self.gdb.find(gesture, minscore=0.6)
            
            if matched:
                print(f"Gesture matched: {matched[1].name} with score: {matched[0]:.2f}")
                
                if matched[1] == self.left_swipe:
                    print("Left swipe detected")
                    self.jump_back()
                elif matched[1] == self.right_swipe:
                    print("Right swipe detected")
                    self.jump_forward()
                elif matched[1] == self.up_swipe:
                    print("Up swipe detected")
                    self.speed_up()
                elif matched[1] == self.down_swipe:
                    print("Down swipe detected")
                    self.speed_down()
                elif matched[1] == self.l_shape:
                    print("L-shape detected")
                    self.font_bigger()
                elif matched[1] == self.reverse_l:
                    print("Reverse L-shape detected")
                    self.font_smaller()
                elif matched[1] == self.diagonal_swipe:
                    print("Diagonal swipe detected")
                    self.toggle_play_pause(None)
            else:
                print("No gesture matched")
                
        except Exception as e:
            print(f"Error in gesture recognition: {e}")
    
    def jump_back(self):
        if not self.words:
            return
        new_index = max(0, self.current_word_index - 5)
        self.current_word_index = new_index
        if self.has_audio:
            self.sync_audio_position()

    def jump_forward(self):
        if not self.words:
            return
        new_index = min(len(self.words) - 1, self.current_word_index + 5)
        self.current_word_index = new_index
        if self.has_audio:
            self.sync_audio_position()

    # def speed_up(self):
    #     self.wpm = min(1000, self.wpm + 50)
    #     if self.has_audio:
    #         self.update_audio_speed()

    # def speed_down(self):
    #     self.wpm = max(50, self.wpm - 50)
    #     if self.has_audio:
    #         self.update_audio_speed()

    def font_bigger(self):
        self.font_size = dp(min(100, self.font_size + 5))

    def font_smaller(self):
        self.font_size = dp(max(10, self.font_size - 5))

class SettingFontSpinner(SettingItem):                      # creating a simple spinner element for font selection
    options = ListProperty([])

    def __init__(self, **kwargs):
        # Extract options before super call
        options = kwargs.get('options', [])
        if isinstance(options, str):
            import json
            try:
                options = json.loads(options)
            except:
                options = []
        kwargs.pop('options', None)
        
        super(SettingFontSpinner, self).__init__(**kwargs)
        self.options = options
        
        # Create spinner widget
        self.spinner = Spinner(
            text=self.value,
            values=self.options,
            size_hint=(0.8, None),
            # size=(dp(220), dp(42)),
            # pos=(dp(10), dp(5)),  
            # size_hint_max_x=0.5,  
            height=dp(44),
            pos_hint={'x': 0.1},
        )
        
        # Bind spinner
        self.spinner.bind(text=self.on_spinner_value)
        self.add_widget(self.spinner)

    def on_spinner_value(self, spinner, text):
        self.value = text

    def set_value(self, value):
        self.value = value
        self.spinner.text = value

class RSVPReaderApp(App):
    def build(self):
        try:
            self.settings_cls = SettingsWithSidebar
            self.rsvp_reader = RSVPReader()
            self.apply_settings()
            return self.rsvp_reader
        except Exception as e:
            print(f"Error in build method: {e}")
            import traceback
            traceback.print_exc()
            return Label(text=f"An error occurred: {e}")

    def build_config(self, config):
        config.setdefaults('rsvp', {
            'wpm': 150,
            'font_size': 40,
            'font_name': 'Helvetica-Bold.ttf'
        })

    def build_settings(self, settings):
    
        font_options = [
            'AGaramondPro-Bold.otf', 'AGaramondPro-BoldItalic.otf', 'AGaramondPro-Italic.otf',
            'AGaramondPro-Regular.otf', 'APHont-BoldItalic_q15c.ttf', 'APHont-Bold_q15c.ttf',
            'APHont-Italic_q15c.ttf', 'APHont-Regular_q15c.ttf', 'Anonymous Pro B.ttf',
            'Anonymous Pro BI.ttf', 'Anonymous Pro I.ttf', 'Anonymous Pro.ttf', 'FreeSerif.otf',
            'FreeSerif.ttf', 'FreeSerifBold.otf', 'FreeSerifBold.ttf', 'FreeSerifBoldItalic.otf',
            'FreeSerifBoldItalic.ttf', 'FreeSerifItalic.otf', 'FreeSerifItalic.ttf',
            'Helvetica-Bold.ttf', 'Helvetica-BoldOblique.ttf', 'Helvetica-Oblique.ttf',
            'Helvetica.ttf', 'OpenDyslexic-Bold.otf', 'OpenDyslexic-Bold.ttf',
            'OpenDyslexic-BoldItalic.otf', 'OpenDyslexic-BoldItalic.ttf', 'OpenDyslexic-Italic.otf',
            'OpenDyslexic-Italic.ttf', 'OpenDyslexic-Regular.otf', 'OpenDyslexic-Regular.ttf',
            'OpenDyslexicAlta-Bold.otf', 'OpenDyslexicAlta-Bold.ttf', 'OpenDyslexicAlta-BoldItalic.otf',
            'OpenDyslexicAlta-BoldItalic.ttf', 'OpenDyslexicAlta-Italic.otf', 'OpenDyslexicAlta-Italic.ttf',
            'OpenDyslexicAlta-Regular.otf', 'OpenDyslexicAlta-Regular.ttf', 'OpenDyslexicMono-Regular.otf',
            'OpenDyslexicMono-Regular.ttf', 'PTC55F.ttf', 'PTC75F.ttf', 'PTN57F.ttf', 'PTN77F.ttf',
            'PTS55F.ttf', 'PTS56F.ttf', 'PTS75F.ttf', 'PTS76F.ttf', 'Times New Roman Bold Italic.ttf',
            'Times New Roman Bold.ttf', 'Times New Roman Italic.ttf', 'Times New Roman.ttf',
            'helvetica-compressed.otf', 'helvetica-light.ttf',
            'helvetica-rounded-bold.otf', 'tahoma.ttf'
        ]
        
        # Register the custom spinner setting type
        settings.register_type('font_spinner', SettingFontSpinner)
    
        # Create settings panel data
        panel_data = [
            {
                "type": "numeric",
                "title": "Words per Minute",
                "desc": "Set the reading speed",
                "section": "rsvp",
                "key": "wpm"
            },
            {
                "type": "numeric",
                "title": "Font Size",
                "desc": "Set the font size",
                "section": "rsvp",
                "key": "font_size"
            },
            {
                "type": "font_spinner",
                "title": "Font Name",
                "desc": "Set the font name",
                "section": "rsvp",
                "key": "font_name",
                "options": font_options
            }
        ]
        
        # Convert to JSON string
        settings.add_json_panel('RSVP Reader Settings', self.config, data=json.dumps(panel_data))

    def on_config_change(self, config, section, key, value):
        if config is self.config and section == 'rsvp':
            if key == 'wpm':
                self.rsvp_reader.wpm = int(value)
            elif key == 'font_size':
                self.rsvp_reader.font_size = dp(int(float(value)))
                config.set('rsvp', 'font_size', str(int(float(value))))
            elif key == 'font_name':
                self.rsvp_reader.font_name = value
            self.rsvp_reader.update_word_display()
            self.config.write()

    def apply_settings(self):
        self.rsvp_reader.wpm = self.config.getint('rsvp', 'wpm')
        self.rsvp_reader.font_size = dp(float(self.config.get('rsvp', 'font_size')))
        self.rsvp_reader.font_name = self.config.get('rsvp', 'font_name')

if __name__ == '__main__':
    try:
        RSVPReaderApp().run()
    except Exception as e:
        print(f"Error running the app: {e}")
        import traceback
        traceback.print_exc()