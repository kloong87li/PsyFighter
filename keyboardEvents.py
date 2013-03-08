import kivy
from kivy.uix.widget import Widget
from kivy.core.window import Window

class KeyboardListener(Widget): #base code taken from Kivy API documentation
    def __init__(self, **kwargs):
        super(KeyboardListener, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.on_keyPress)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_keyPress)
        self._keyboard = None

    def on_keyPress(self, keyboard, keycode, text, modifiers):
        #print 'The key', keycode, 'have been pressed'
        #print ' - text is %r' % text
        #print ' - modifiers are %r' % modifiers

        # Keycode is composed of an integer + a string
        #if keycode[1] == 'escape':
        #    keyboard.release()
        return True