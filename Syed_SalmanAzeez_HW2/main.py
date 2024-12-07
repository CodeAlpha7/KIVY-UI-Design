from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.metrics import dp
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.scrollview import ScrollView
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy_config_helper import config_kivy
from kivy.core.window import Window
import random

# Configure Kivy
scr_w, scr_h = config_kivy(window_width=800, window_height=600,
                           simulate_device=False, simulate_dpi=300, simulate_density=3.0)

class FocusButton(FocusBehavior, Button):                                               # This code has mostly been copied from class resources:
    def __init__(self, **kwargs):                                                       # https://github.gatech.edu/IMTC/CS6456_ClassResources/blob/main/focus_demo.py
        super().__init__(**kwargs)
        self.bind(focus=self.on_focus)
        self.bind(pos=self.update_focus_border, size=self.update_focus_border)
        Window.bind(on_key_down=self.on_key_down)                                       # main issue causing keyboard commands to fail. Resolved when changing bind target to entire window
        self.border_line = None

    def on_focus(self, instance, value):
        if value:
            self.add_focus_border()
        else:
            self.remove_focus_border()

    def add_focus_border(self):
        self.remove_focus_border()  # Remove any existing border
        with self.canvas.after:
            Color(1, 0, 0)
            self.border_line = Line(rectangle=(self.x, self.y, self.width, self.height), width=2)

    def remove_focus_border(self):
        if self.border_line:
            self.canvas.after.remove(self.border_line)
            self.border_line = None

    def update_focus_border(self, *args):
        if self.focus:
            self.add_focus_border()

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        if self.focus and scancode in (40, 88):  # Enter or numpad Enter
            self.trigger_action(duration=0)  # Simulate mouse button press
            return True  # consume event
        return False

class CustomScaleWidget(FocusBehavior, Widget):
    value = NumericProperty(0)
    visited = BooleanProperty(False)
    low_text = StringProperty("Very Low")
    high_text = StringProperty("Very High")

    def __init__(self, **kwargs):
        super(CustomScaleWidget, self).__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas, value=self.update_canvas)
        self.bind(focus=self.on_focus)
        Window.bind(on_key_down=self.on_key_down)

        # Create the labels as part of the widget
        self.low_label = Label(text=self.low_text, font_size=dp(12), color=(1, 1, 1, 1))
        self.high_label = Label(text=self.high_text, font_size=dp(12), color=(1, 1, 1, 1))
        self.add_widget(self.low_label)
        self.add_widget(self.high_label)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Background
            Color(0, 0, 0, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            # Horizontal line
            Color(1, 1, 1, 1)
            Line(points=[self.x, self.y, self.x + self.width, self.y])

            # Scale Marks
            for i in range(21):
                x = self.x + i * self.width / 20
                height = dp(16) if i in [0,10,20] else dp(8)
                Line(points=[x, self.y, x, self.y + height])
            
            # Value bar
            Color(0.1, 0.3, 0.5, 1)
            Rectangle(pos=self.pos, size=(self.width * self.value / 100, self.height/1.5))

            if self.focus:
                Color(1, 0, 0)
                Line(rectangle=(self.x, self.y, self.width, self.height/1.4), width=2)

        # Update label positions
        self.low_label.pos = (self.x - self.low_label.width / 3, self.y - dp(65))
        self.high_label.pos = (self.right - self.high_label.width / 1.4, self.y - dp(65))

    def on_focus(self, instance, value):
        self.update_canvas()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.set_value_from_pos(touch.x)
            touch.grab(self)                                                    # this is to enable dragging functionality of value bar.
            return True                                                         # 3 touch functions inspired from: https://www.tutorialspoint.com/how-to-add-drag-behavior-in-kivy-widget
        return super(CustomScaleWidget, self).on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if touch.grab_current == self:
            self.set_value_from_pos(touch.x)
            return True
        return super(CustomScaleWidget, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            touch.ungrab(self)
            return True
        return super(CustomScaleWidget, self).on_touch_up(touch)

    def set_value_from_pos(self, x):
        self.value = max(0, min(100, int((x - self.x) / self.width * 100)))
        self.visited = True
        App.get_running_app().sm.get_screen('rating').check_completion()

    def on_key_down(self, window, key, scancode, codepoint, modifier):                  
        if self.focus:
            if scancode == 80:  # Left arrow 
                self.value = max(0, self.value - 5)
            elif scancode == 79:  # Right arrow
                self.value = min(100, self.value + 5)
            else:
                return False
            self.visited = True
            App.get_running_app().sm.get_screen('rating').check_completion()
            return True
        return False

    def on_value(self, instance, value):
        self.value = round(value / 5) * 5

class OpeningScreen(Screen):
    def __init__(self, **kwargs):
        super(OpeningScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        top_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120))
        title = Label(text='NASA TLX Workload Assessment', font_size=dp(24), size_hint_y=None, height=dp(60))
        intro = Label(text='Assess workload across six dimensions', font_size=dp(18), size_hint_y=None, height=dp(40))
        top_layout.add_widget(title)
        top_layout.add_widget(intro)
        
        button_layout = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=None, height=dp(80))
        self.start_button = FocusButton(text='Start Assessment', size_hint=(None, None), size=(dp(200), dp(60)), 
                                        font_size=dp(16))
        self.start_button.bind(on_press=self.start_assessment)
        button_layout.add_widget(self.start_button)

        layout.add_widget(top_layout)
        layout.add_widget(Widget())  # This will push the button to the bottom
        layout.add_widget(button_layout)
        self.add_widget(layout)

        Window.bind(on_key_down=self.on_key_down)

    def start_assessment(self, instance):
        self.manager.current = 'weight_0'

    def on_enter(self):
        self.start_button.focus = True

    def on_key_down(self, window, keycode, text, scancode, modifiers):
        if scancode == 43:  # Tab key
            self.start_button.focus = True
            return True
        elif scancode in (40, 88):  # Enter or numpad Enter
            if self.start_button.focus:
                self.start_assessment(None)
            return True
        return False

class ScaleWeightScreen(Screen):
    def __init__(self, factor1, factor2, **kwargs):
        super(ScaleWeightScreen, self).__init__(**kwargs)
        self.factor1 = factor1
        self.factor2 = factor2
        self.selected = None

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))

        top_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(140))
        
        instruction = Label(text='Which factor has a greater impact?', 
                            font_size=dp(19), size_hint_y=None, height=dp(60))
        layout.add_widget(instruction)

        self.button1 = FocusButton(text=factor1, on_press=self.select_factor, font_size=dp(16), 
                                   size_hint=(None, None), size=(dp(250), dp(60)), pos_hint={'center_x': 0.5})
        self.button2 = FocusButton(text=factor2, on_press=self.select_factor, font_size=dp(16), 
                                   size_hint=(None, None), size=(dp(250), dp(60)), pos_hint={'center_x': 0.5})
        layout.add_widget(self.button1)
        layout.add_widget(self.button2)

        layout.add_widget(top_layout)
        layout.add_widget(Widget())

        button_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(20))
        self.prev_button = FocusButton(text='Previous', on_press=self.go_previous, disabled=True, font_size=dp(16))
        self.next_button = FocusButton(text='Next', on_press=self.go_next, disabled=True, font_size=dp(16))
        button_layout.add_widget(self.prev_button)
        button_layout.add_widget(self.next_button)
        layout.add_widget(button_layout)

        self.add_widget(layout)

        self.focusable_widgets = [self.button1, self.button2, self.prev_button, self.next_button]
        self.current_focus = 0

        Window.bind(on_key_down=self.on_key_down)

    def select_factor(self, instance):
        self.selected = instance.text
        self.button1.background_color = (0.2, 0.6, 0.8, 1) if self.button1.text == self.selected else (1, 1, 1, 1)
        self.button2.background_color = (0.2, 0.6, 0.8, 1) if self.button2.text == self.selected else (1, 1, 1, 1)
        self.next_button.disabled = False

    def go_previous(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = self.manager.previous()

    def go_next(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = self.manager.next()

    def on_enter(self):
        self.prev_button.disabled = self.manager.current == 'weight_0'
        self.button1.focus = True
        self.current_focus = 0

    def on_key_down(self, window, keycode, text, scancode, modifiers):
        if scancode == 43:  # Tab key
            self.focus_next()
            return True
        return False

    def focus_next(self):
        self.focusable_widgets[self.current_focus].focus = False
        self.current_focus = (self.current_focus + 1) % len(self.focusable_widgets)
        self.focusable_widgets[self.current_focus].focus = True

class HighlightableLabel(Label):
    def on_focus(self, instance, value):
        self.color = (0.2, 0.5, 0.7, 1) if value else (1, 1, 1, 1)

class NumericalRatingScreen(Screen):
    def __init__(self, **kwargs):
        super(NumericalRatingScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(25))
       
        instruction = Label(text='Rate the following factors:', font_size=dp(18), size_hint_y=None, height=dp(25))
        self.layout.add_widget(instruction)
        
        self.scales = {}
        self.factor_labels = {}
        self.focusable_widgets = []                 # since many toggle objects, this will help organize the order of toggling
        
        for factor in App.get_running_app().factors:
            factor_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), padding=[0, dp(10), dp(10), 0])
            factor_label = Label(text=factor, size_hint_x=0.3, font_size=dp(16), halign='center', color=(0.1, 0.4, 0.8,1))
            factor_label.bind(size=factor_label.setter('text_size'))
            self.factor_labels[factor] = factor_label
            factor_layout.add_widget(factor_label)
            scale = CustomScaleWidget(size_hint_x=0.7)
            self.scales[factor] = scale
            factor_layout.add_widget(scale)
            self.layout.add_widget(factor_layout)
            self.focusable_widgets.append(scale)
        
        button_layout = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(20), padding=[0, dp(10), 0, 0])
        self.prev_button = FocusButton(text='Previous', on_press=self.go_previous, font_size=dp(16))
        self.next_button = FocusButton(text='View Results', on_press=self.go_next, disabled=True, font_size=dp(16))
        button_layout.add_widget(self.prev_button)
        button_layout.add_widget(self.next_button)
        self.layout.add_widget(button_layout)
        
        self.focusable_widgets.extend([self.prev_button, self.next_button])
        
        self.add_widget(self.layout)
        
        Window.bind(on_key_down=self.on_key_down)

    def on_enter(self):
        self.focusable_widgets[0].focus = True
        self.check_completion()

    def check_completion(self):
        self.next_button.disabled = not all(scale.visited for scale in self.scales.values())

    def on_key_down(self, window, keycode, text, scancode, modifiers):
        if scancode == 43:  # Tab key
            self.focus_next()
            return True
        elif scancode in (40, 88):  # Enter or numpad Enter
            if self.prev_button.focus:
                self.go_previous(None)
            elif self.next_button.focus and not self.next_button.disabled:
                self.go_next(None)
            return True
        return False

    def focus_next(self):
        current_focus = next((i for i, w in enumerate(self.focusable_widgets) if w.focus), -1)
        if current_focus != -1:
            self.focusable_widgets[current_focus].focus = False
        elif (current_focus + 1) == len(self.focusable_widgets):
            self.prev_button.focus = True
        elif self.prev_button.focus:
            self.next_button.focus = True
        next_focus = (current_focus + 1) % len(self.focusable_widgets)
        self.focusable_widgets[next_focus].focus = True
        self.update_factor_highlight(self.focusable_widgets[next_focus])


    def update_factor_highlight(self, focused_widget):
        for factor, scale in self.scales.items():
            if scale == focused_widget:
                self.factor_labels[factor].color = (0, 0.6, 0.8, 1)  # Highlight color
            else:
                self.factor_labels[factor].color = (1, 1, 1, 1)  # Normal color

    def go_previous(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = self.manager.previous()

    def go_next(self, instance):
        app = App.get_running_app()
        for factor, scale in self.scales.items():
            app.factor_ratings[factor] = scale.value
        self.manager.transition.direction = 'left'
        self.manager.current = 'results'

class ResultsScreen(Screen):
    def __init__(self, **kwargs):
        super(ResultsScreen, self).__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))

        # Title at the top
        title_label = Label(text='NASA TLX Results', font_size=dp(24), size_hint_y=None, height=dp(40))
        main_layout.add_widget(title_label)

        # Content in the center
        content_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        self.results_labels = []
        for _ in range(7):  # 6 factors + 1 overall score
            label = Label(font_size=dp(16), size_hint_y=None, height=dp(30))
            self.results_labels.append(label)
            content_layout.add_widget(label)

        # Wrap content in a ScrollView
        scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height * 0.6))
        scroll_view.add_widget(content_layout)

        # Center the ScrollView
        center_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        center_layout.add_widget(scroll_view)
        main_layout.add_widget(center_layout)

        # Restart button at the bottom
        self.restart_button = FocusButton(text="Restart Assessment", size_hint_y=None, height=dp(50), font_size=dp(18))
        self.restart_button.bind(on_press=self.restart_assessment)
        main_layout.add_widget(self.restart_button)

        self.add_widget(main_layout)

        Window.bind(on_key_down=self.on_key_down)

    def on_enter(self):
        app = App.get_running_app()
        
        # Calculate weights (tally)
        weights = {factor: 0 for factor in app.factors}
        for pair in app.pairs:
            selected = app.sm.get_screen(f'weight_{app.pairs.index(pair)}').selected
            weights[selected] += 1

        ratings = app.factor_ratings
        workload_score = sum(weights[factor] * ratings[factor] for factor in app.factors) / 15

        for i, factor in enumerate(app.factors):
            result_text = f"{factor}:       Tally: {weights[factor]};    Weight: {weights[factor]/15:.2f};  Rating: {ratings[factor]:.2f}/100"
            self.results_labels[i].text = result_text

        self.results_labels[-1].text = f"\nWorkload Score: {workload_score:.2f}"

        self.restart_button.focus = True

    def restart_assessment(self, instance):
        app = App.get_running_app()
        app.reset_assessment()

    def on_key_down(self, window, keycode, text, scancode, modifiers):
        if scancode in (40, 88):  # Enter or numpad Enter
            if self.restart_button.focus:
                self.restart_assessment(None)
            return True
        return False

class NASATLXApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.setup_assessment()
        return self.sm

    def setup_assessment(self):
        self.factors = ['Mental Demand', 'Physical Demand', 'Temporal Demand', 
                        'Performance', 'Effort', 'Frustration']
        self.factor_ratings = {factor: 0 for factor in self.factors}
        self.pairs = list(self.generate_pairs())
        random.shuffle(self.pairs)

        self.sm.clear_widgets()
        self.sm.add_widget(OpeningScreen(name='opening'))
        for i, pair in enumerate(self.pairs):
            self.sm.add_widget(ScaleWeightScreen(pair[0], pair[1], name=f'weight_{i}'))
        self.sm.add_widget(NumericalRatingScreen(name='rating'))
        self.sm.add_widget(ResultsScreen(name='results'))

        self.sm.current = 'opening'

    def reset_assessment(self):
        self.setup_assessment()
        self.sm.current = 'opening'

    def generate_pairs(self):
        return [(self.factors[i], self.factors[j]) 
                for i in range(len(self.factors)) 
                for j in range(i+1, len(self.factors))]

    def on_key_down(self, window, keycode, text, scancode, modifiers):
        if self.sm.current_screen:
            return self.sm.current_screen.on_key_down(window, keycode, text, scancode, modifiers)
        return False

if __name__ == '__main__':
    NASATLXApp().run()