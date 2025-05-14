import pyglet
from pyglet import window, shapes
from pyglet.window import key
import numpy as np
import threading
from scipy.stats import linregress
from pynput.keyboard import Controller, Key
import audio_sample

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

ICON_SIZE = 20
ICON_UNSELECTED_COLOR = (0, 0, 255)
ICON_SELECTED_COLOR = (255, 0, 0)
SPACE_SIZE = 5
# Weil ich wohl etwas hohl bin und nicht bedacht habe, dass man nicht nach links oder rechts pfeifen kann, habe ich das "Menü" zweidimensional gemacht...
ROWS = (WINDOW_HEIGHT - SPACE_SIZE) // (ICON_SIZE + SPACE_SIZE)
COLUMNS = (WINDOW_WIDTH - SPACE_SIZE) // (ICON_SIZE + SPACE_SIZE)

MIN_NO_FREQUENCIES_IN_ARRAY = 8 # Mindestanzahl an erkannten Frequenzen in Folge, um eine Richtungsuaswertung durchzuführen
MAX_ZEROS_SINCE_SIGNAL_END = 10 # Maximale Anzahl Pausen/Stille (Frequenz = 0) bis das "zuhören" auf ein Signal beendet wird und ggf. Richtungsauswertung startet

win = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
keyboard = Controller()


class Icon:
    def __init__(self, col, row):
        self.column = col
        self.row = row
        self.x = SPACE_SIZE + self.column * (ICON_SIZE + SPACE_SIZE)
        self.y = SPACE_SIZE + self.row * (ICON_SIZE + SPACE_SIZE)
        self.selected = False
        self.sprite = shapes.Rectangle(self.x, self.y, ICON_SIZE, ICON_SIZE, color = ICON_UNSELECTED_COLOR) 

    def select(self, selected):
        global selected_icon
        if selected:
            self.selected = True
            self.sprite.color = ICON_SELECTED_COLOR
            selected_icon = self
        else:
            self.selected = False
            self.sprite.color = ICON_UNSELECTED_COLOR


def main():
    threading.Thread(target=set_current_frequency, daemon=True).start()
    init_icons()
    pyglet.app.run()


icons = []
selected_icon = None
frequencies = []


# Baut Icon-Raster
def init_icons():
    global icons
    for row in range(ROWS):
        row_icons = []
        for col in range(COLUMNS):
            icon = Icon(col, row)
            row_icons.append(icon)
        icons.append(row_icons)
    icons[0][0].select(True)


# Steuerung per Pfeiltasten zum Test (Vorsicht, ganz unten im Code ist das auslösende Event auskommentiert!)
def update_selection_manually(symbol):
    global selected_icon

    if symbol == key.UP:
        if selected_icon.row < (ROWS - 1):
            selected_icon.select(False)
            icons[selected_icon.row + 1][selected_icon.column].select(True)
    if symbol == key.DOWN:
        if selected_icon.row > 0:
            selected_icon.select(False)
            icons[selected_icon.row - 1][selected_icon.column].select(True)
    if symbol == key.RIGHT:
        if selected_icon.column < (COLUMNS - 1):
            selected_icon.select(False)
            icons[selected_icon.row][selected_icon.column + 1].select(True)
    if symbol == key.LEFT:
        if selected_icon.column > 0:
            selected_icon.select(False)
            icons[selected_icon.row][selected_icon.column - 1].select(True)

def update_selection_by_whistle(direction):
    if direction == 1:
        if selected_icon.row < (ROWS - 1):
            selected_icon.select(False)
            icons[selected_icon.row + 1][selected_icon.column].select(True)
    if direction == -1:
        if selected_icon.row > 0:
            selected_icon.select(False)
            icons[selected_icon.row - 1][selected_icon.column].select(True)


def set_current_frequency():
    global frequencies

    zero_counter = 0
    while True: # Hört dauerhaft auf Audio-Input
        freq = audio_sample.get_audio_signal()
        if freq == 0: # Falls Stille...
            zero_counter += 1
            if zero_counter >= MAX_ZEROS_SINCE_SIGNAL_END: # Falls lang genug schon still seit letztem Ton...
                zero_counter = 0
                analyze_tone_direction()
        else:
            zero_counter = 0 # Setze Pausen-Counter zurück, wenn ein Ton erkannt wird
            if frequencies:
                if frequencies[len(frequencies)-1] != freq: # Füge Frequenz nur hinzu, wenn es nicht auch schon die vorherige war (vermeidet Doppelte Registrierungen)
                    frequencies.append(freq)
            else:
                frequencies.append(freq)


# Lineare Regression zur Ermittlung der Steigung der Frequenzdaten über die gemessene Zeit
def analyze_tone_direction():
    global frequencies

    if len(frequencies) >= MIN_NO_FREQUENCIES_IN_ARRAY: # Nur auswerten, falls genug aufeinanderfolgende Frequenzen erkannt wurden
        x = np.arange(len(frequencies))
        slope, intercept, r, p, stderr = linregress(x, frequencies)

        if slope > 0:
            update_selection_by_whistle(1)
            print("up")
            keyboard.tap(Key.up)
        elif slope < 0:
            update_selection_by_whistle(-1)
            print("down")
            keyboard.tap(Key.down)
        else:
            print("weder noch")
    else:
        print("array gelöscht")
    frequencies.clear() # Frequenzaufzeichnung löschen, wenn sie zu wenige Frequenzen umfasst hat


@win.event
def on_draw():
    win.clear()
    for row in icons:
        for icon in row:
            icon.sprite.draw()


# Deaktiviert, sonst geht er immer um zwei Icons hoch/runter beim Pfiff
'''@win.event
def on_key_press(symbol, modifiers):
    update_selection_manually(symbol)'''


if __name__ == "__main__":
    main()