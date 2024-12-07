# import kivy                     # base template from https://kivy.org/doc/stable/guide/basic.html#quickstart
# kivy.require('2.3.0') 

# from kivy.app import App
# from kivy.uix.label import Label


# class MyApp(App):

#     def build(self):
#         return Label(text='Hello world')


# if __name__ == '__main__':
#     MyApp().run()

from kivy_config_helper import config_kivy                                  # reference: https://github.gatech.edu/IMTC/CS6456_ClassResources/blob/main/kivy_config_sim_demo.py

scr_w, scr_h = config_kivy(window_width=400, window_height=500,
            simulate_device=False, simulate_dpi=1000, simulate_density=5.0)

import os
from kivy.graphics import Rectangle, Color
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.properties import AliasProperty, BooleanProperty
from kivy.core.image import Image as CoreImage

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.metrics import dp, sp                                         
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
import re

# class ScalableLabel(Label):                                             # reference for responsive design across simulated resolutions: 
#     def __init__(self, **kwargs):                                   # https://stackoverflow.com/questions/62498639/python-kivy-how-to-optimize-screen-resolution-for-all-devices
#         super(ScalableLabel, self).__init__(**kwargs)                # commented out because this wasnt scaling very well, instead used dp() where font sizes are explicity specified for each widget
#         self.bind(size=self.update_text_size)

#     def update_text_size(self, *args):
#         self.text_size = self.size                                # maybe window.size ?

IMG_FOLDER = "./images/"
IMG_CHECKBOX_ON = os.path.join(IMG_FOLDER, "checkbox_on.png")
IMG_CHECKBOX_OFF = os.path.join(IMG_FOLDER, "checkbox_off.png")

class AltCheckBox(ToggleButtonBehavior, Widget):                            # Entire class copied from class resources
    keep_ratio = BooleanProperty(True)                                      # Reference: https://github.gatech.edu/IMTC/CS6456_ClassResources/blob/main/alt_checkbox.py

    def __init__(self, **kwargs):
        super(AltCheckBox, self).__init__(**kwargs)
        self.bind(size=self.update_texture, pos=self.update_texture, state=self.update_texture)
        self.texture = None
        self.update_texture()

    def get_widget_screen_size(self):
        x1, y1 = self.to_window(0, 0)
        x2, y2 = self.to_window(self.width, self.height)
        return abs(x2 - x1), abs(y2 - y1)

    def update_texture(self, *args):
        img_file = IMG_CHECKBOX_ON if self.state == 'down' else IMG_CHECKBOX_OFF
        img = CoreImage(img_file).texture
        widget_width, widget_height = self.get_widget_screen_size()
        img_width, img_height = img.size
        img_aspect = img_width / img_height
        offset_x, offset_y = 0, 0

        if self.keep_ratio:
            widget_aspect = widget_width / widget_height
            if img_aspect > widget_aspect:
                scaled_width = widget_width
                scaled_height = widget_width / img_aspect
                offset_y = (widget_height - scaled_height) / 2
            else:
                scaled_height = widget_height
                scaled_width = widget_height * img_aspect
                offset_x = (widget_width - scaled_width) / 2
        else:
            scaled_width, scaled_height = widget_width, widget_height

        self.texture = img
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1, 1)
            Rectangle(texture=self.texture, pos=[self.pos[0] + offset_x, self.pos[1] + offset_y], size=[scaled_width, scaled_height])

    def _get_active(self):
        return self.state == 'down'

    def _set_active(self, value):
        self.state = 'down' if value else 'normal'

    active = AliasProperty(_get_active, _set_active, bind=('state',), cache=True)

class ListViewScreen(Screen):                                           # Kivy Screenmanager tutorials: https://www.youtube.com/watch?v=Prt_SKkZji8
    def __init__(self, **kwargs):
        super(ListViewScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        # Setting same color scheme as form - dull white with blue highlights/widgets
        with self.canvas.before:
            Color(0.92,0.92,0.92,1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Title of window/GUI
        self.layout.add_widget(Label(text='Demographics Form', font_size=dp(24), size_hint_y=None, height=dp(40), color=(0.2, 0.6, 0.8, 1)))
        
        # Button layout
        button_layout = BoxLayout(size_hint_y=None, height=dp(50))
        button_layout.add_widget(Widget())                                          # This pushes the button to the right
        self.add_button = Button(text='+', size_hint=(None, None), font_size=dp(20), background_color=(0.5, 0.7, 0.9, 1), color=(1, 1, 1, 1), size=(dp(40), dp(40)))
        self.add_button.bind(on_press=self.add_new_entry)
        button_layout.add_widget(self.add_button)
        self.layout.add_widget(button_layout)

        # Entries layout
        self.entries_layout = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.entries_layout.bind(minimum_height=self.entries_layout.setter('height'))

        self.scroll_view = ScrollView(size_hint=(1, 1))             # https://www.tutorialspoint.com/kivy/kivy-scrollview.htm
        self.scroll_view.add_widget(self.entries_layout)            # Simple scrollview same as documentation
        self.layout.add_widget(self.scroll_view)
        
        self.add_widget(self.layout)


    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def add_new_entry(self, instance):
        App.get_running_app().switch_to_form(new_entry=True)

    def update_entries(self, entries):
        self.entries_layout.clear_widgets()
        for index, entry in enumerate(entries):
            btn = Button(text=entry['name'], size_hint_y=None, font_size=14, background_color=(0.5, 0.7, 0.9, 1), height=dp(40))
            btn.bind(on_press=self.on_entry_press)
            btn.index = index  # Store the index as an attribute of the button
            self.entries_layout.add_widget(btn)

    def on_entry_press(self, instance):
        self.edit_entry(instance.index)

    def edit_entry(self, index):
        App.get_running_app().edit_entry(index)

class CustomSpinnerOption(SpinnerOption):                                         # form inspiration and QoL changes from: https://github.com/kivy/kivy/wiki/Forms
    def __init__(self, **kwargs):
        super(CustomSpinnerOption, self).__init__(**kwargs)                 # ensure parent class's __init__ method is called before we add our own initialization. (superclass inheritance)
        self.height = dp(30)                                                # super() is like python's custom forced OOP which I like to use since my strongest language is C++
        self.font_size = dp(14)                                             # why? - avoid rewriting. reference used: https://realpython.com/python-super/. Check super() deep dive.
                                                                            # So, in addition to kivy's built-in SpinnerOption, I add my own height and font size
                                                                            # also used in kivy documentation during filtering: https://kivy.org/doc/stable/api-kivy.uix.textinput.html
        self.background_color = (0.4, 0.5, 0.8, 1)
        self.color = (1,1,1, 1)
        

class DemographicForm(Screen):                                           # inheriting from BoxLayout: https://kivy.org/doc/stable/api-kivy.uix.boxlayout.html
    def __init__(self, **kwargs):
        super(DemographicForm, self).__init__(**kwargs)                     # for python3, super().__init__(**kwargs) also works. But I like to keep it verbose
        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.orientation = 'vertical'                                       # specify since default is horizontal
        self.padding = dp(20)
        self.spacing = dp(15)                                               # dp() used from metrics page: https://kivy.org/doc/stable/api-kivy.metrics.html

        with self.canvas.before:                                            # reference: https://kivy.org/doc/stable/api-kivy.graphics.html
            Color(0.92,0.92,0.92,1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)            # ensures updated positioning of rectangle when size changes. ref: https://stackoverflow.com/questions/20872598/kivy-change-background-color-to-white


        

        # Rest widget content layout
        # content_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=1)       # I did this myself to apply size_hint_y=1 to selected components.
                                                                                                # later changed to individually apply size_hint_y = 1 to all widgets to scale with whitespace

        # Name
        self.layout.add_widget(Label(text='Full Name:', size_hint_y=1, height=dp(20), font_size=dp(15), color=(0.2, 0.2, 0.2, 1)))                  # widget additions, Input and GUI Layouts inspired and tested from:
        self.name_input = TextInput(multiline=False, size_hint_y=0.9, height=dp(33), font_size=dp(15), background_color=(1, 1, 1, 0.8))                # https://www.youtube.com/watch?v=QUHnJrFouv8
        self.name_input.bind(text=self.on_name_change)                                                      
        self.layout.add_widget(self.name_input)

        # Age Range
        self.layout.add_widget(Label(text='Age Range:', size_hint_y=1, height=dp(20), font_size=dp(15), color=(0.2, 0.2, 0.2, 1)))
        self.age_spinner = Spinner(                                                                         # Creating and adding spinners: https://kivy.org/doc/stable/api-kivy.uix.spinner.html
            text='Select Age Range',
            values=('Below 18','18-25', '26-33', '34-41', '42-50', '50+'),
            size_hint_y=1,
            height=dp(40),
            font_size=dp(15),
            background_color=(0.5, 0.7, 0.9, 1),
            option_cls=CustomSpinnerOption,
            # background_color=(0.5,0.5,0.5,1),
            # color=(1,1,1,1)
        )
        self.age_spinner.bind(text=self.validate_form)
        self.layout.add_widget(self.age_spinner)

        # Gender
        self.layout.add_widget(Label(text='Gender:', size_hint_y=1, height=dp(30), font_size=dp(15), color=(0.2, 0.2, 0.2, 1)))
        # gender_layout = GridLayout(cols=3, size_hint_y=0.95, height=dp(40))                                     # Using Grid Layouts https://www.techwithtim.net/tutorials/kivy-tutorial/gui-layouts
        gender_layout = BoxLayout(size_hint_y=0.9, height=dp(40))
        gender_layout.bind(minimum_height=gender_layout.setter('height'))               # binding layout object's to setter, inspired from scrollview.

        with gender_layout.canvas.before:                                               # Lines 219-222 were implemented in the very beginning and do not do much. probably dont need
            Color(0.92, 0.92, 0.92, 1)                                                  # but I'll keep it in to avoid anything from breaking last minute.
            self.gender_rect = Rectangle(size=gender_layout.size, pos=gender_layout.pos)
        gender_layout.bind(size=self._update_gender_rect, pos=self._update_gender_rect)

        self.gender_checkboxes = {}
        self.gender_order = ['Male', 'Female', 'Other']
        for gender in self.gender_order:
            box = BoxLayout(size_hint_x=1)
            cb = AltCheckBox(size_hint=(None, None), size=(dp(30), dp(30)), keep_ratio=True)
            cb.bind(active=self.validate_form)
            box.add_widget(cb)
            box.add_widget(Label(text=gender, font_size=dp(15), color=(0.2, 0.65, 0.85, 1)))
            gender_layout.add_widget(box)
            self.gender_checkboxes[gender] = cb
        self.layout.add_widget(gender_layout)

        # Phone Number
        self.layout.add_widget(Label(text='Phone Number:', size_hint_y=1, height=dp(20), font_size=dp(15), color=(0.2, 0.2, 0.2, 1)))
        self.phone_input = TextInput(multiline=False, size_hint_y=0.9, height=dp(33), font_size=dp(15), background_color=(1, 1, 1, 0.8))
        self.phone_input.bind(text=self.on_phone_change, focus=self.on_phone_focus)
        self.layout.add_widget(self.phone_input)

        # Buttons
        button_layout = BoxLayout(size_hint_y=1.4, height=dp(60), spacing=dp(25))
        self.submit_button = Button(text='Submit', disabled=True, font_size=dp(15), background_color=(0.5, 0.7, 0.9, 1), color=(1, 1, 1, 1))              # adding buttons and event triggers: https://youtu.be/fGWHQA3LhJ8
        self.submit_button.bind(on_press=self.submit_form)                                                                              # Button Binding same video timestamp 6:45
        self.cancel_button = Button(text='Cancel', font_size=dp(15), background_color=(0.5, 0.7, 0.9, 1), color=(1, 1, 1, 1))
        self.cancel_button.bind(on_press=self.cancel_form)
        button_layout.add_widget(self.submit_button)
        button_layout.add_widget(self.cancel_button)
        self.layout.add_widget(button_layout)

        self.add_widget(self.layout)

        # root = ScrollView(
        #     size_hint=(1,None),                               # Tried to apply scrollview to formView to account for weird screen lengths, but errors abound
        #     size=(Window.width, Window.height)
        # )
        # root.add_widget(self.layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_gender_rect(self, instance, value):
        self.gender_rect.pos = instance.pos
        self.gender_rect.size = instance.size

        # Filtering inspired from: https://kivy.org/doc/stable/api-kivy.uix.textinput.html#filtering. But implemented by self - simpler.
    def on_name_change(self, instance, value):
        # Allow only letters, spaces, and hyphens (special char exception - example: ward-prowse is a valid name. Unrelated - He has excellent freekicks, check YouTube)
        instance.text = re.sub(r'[^a-zA-Z \-]', '', value)          # regular expression (regex) matching - standard python parsing https://docs.python.org/3/library/re.html
        self.validate_form()                                        # here, I am using re.sub() which replaces all un-permitted characters with empty strings (removes them)
                                                                    # all permitted characters shown using Caret (^), i.e: a to z, A to Z, space and special character (-)
                                                                    # [^ ] with Caret inside represents all characters except the ones shown are replaced.
                                                                    # same method used by kivy filtering, refer above URL (line 96)

    def on_phone_change(self, instance, value):
        # Allow only numbers, spaces, hyphens, and parentheses (as described in format (555) 555-5555 has both parenthesis and hyphen)
        instance.text = re.sub(r'[^\d\s\-()]', '', value)               # only \d = digits, \s = whitespaces and hyphen and parenthesis are allowed
        self.validate_form()

    def on_phone_focus(self, instance, value):
        if not value:                                               # If focus is lost
            digits = re.sub(r'\D', '', instance.text)                    # Remove all non-digit characters
            if len(digits) == 10:
                # Format as (555) 555-5555 - first 3 digits in parenthesis, next 3 before hyphen, rest all after hyphen. Max 10 digits allowed for reformatting
                instance.text = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            self.validate_form()

    def validate_form(self, *args):
        name_valid = len(self.name_input.text.strip()) > 7
        age_valid = self.age_spinner.text != 'Select Age Range'
        gender_valid = any(cb.active for cb in self.gender_checkboxes.values())
        phone_valid = len(re.sub(r'\D', '', self.phone_input.text)) == 10

        self.submit_button.disabled = not (name_valid and age_valid and gender_valid and phone_valid)

    def submit_form(self, instance):
        # Collect and print form data
        selected_gender = [g for g, cb in self.gender_checkboxes.items() if cb.active]
        digits = re.sub(r'\D', '', self.phone_input.text)
        self.phone_input.text = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"        # lines 172 and 173 are added to avoid direct focussed submit click unformat.

        data = {
            'name': self.name_input.text,
            'age_range': self.age_spinner.text,
            'gender': selected_gender,
            'phone': self.phone_input.text
        }
        App.get_running_app().add_entry(data)           # add entry to listview - so now app does not close.
        print(data)                                     # console print (obvious, but): https://youtu.be/fGWHQA3LhJ8 (timestamp: 8:25)
        # App.get_running_app().stop()

    def cancel_form(self, instance):
        # App.get_running_app().stop()
        App.get_running_app().switch_to_list_view()         # cancel form does not close app, just takes back to listview
    
    def populate_form(self, data):
        self.name_input.text = data['name']                         # stores all created entries in listview - to restore on clicking existing entry button.
        self.age_spinner.text = data['age_range']
        for gender, cb in self.gender_checkboxes.items():
            cb.active = gender in data['gender']
        self.phone_input.text = data['phone']

    def clear_form(self):
        self.name_input.text = ''
        self.age_spinner.text = 'Select Age Range'
        for cb in self.gender_checkboxes.values():
            cb.active = False
        self.phone_input.text = ''
        self.validate_form()

class DemographicFormApp(App):
    def build(self):
        self.entries = []
        self.sm = ScreenManager()
        self.list_view_screen = ListViewScreen(name='list_view')
        self.form_screen = DemographicForm(name='form')
        self.sm.add_widget(self.list_view_screen)
        self.sm.add_widget(self.form_screen)
        self.sm.current = 'list_view'
        return self.sm

    def switch_to_form(self, new_entry=True, edit_index=None):
        if new_entry:
            self.form_screen.clear_form()
        else:
            self.form_screen.populate_form(self.entries[edit_index])
        self.sm.current = 'form'

    def switch_to_list_view(self):
        self.sm.current = 'list_view'
        self.list_view_screen.update_entries(self.entries)

    def add_entry(self, data):
        self.entries.append(data)
        self.switch_to_list_view()

    def edit_entry(self, index):
        self.switch_to_form(new_entry=False, edit_index=index)

if __name__ == '__main__':
    DemographicFormApp().run()