import pyglet
from pyglet import window, shapes
from pyglet.window import key

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

ICON_SIZE = 40
ICON_UNSELECTED_COLOR = (0, 0, 255)
ICON_SELECTED_COLOR = (255, 0, 0)
SPACE_SIZE = 5
ROWS = (WINDOW_HEIGHT - SPACE_SIZE) // (ICON_SIZE + SPACE_SIZE)
COLUMNS = (WINDOW_WIDTH - SPACE_SIZE) // (ICON_SIZE + SPACE_SIZE)

win = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

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
    init_icons()

icons = []
selected_icon = None

def init_icons():
    global icons
    for row in range(ROWS):
        row_icons = []
        for col in range(COLUMNS):
            icon = Icon(col, row)
            row_icons.append(icon)
        icons.append(row_icons)
    icons[0][0].select(True)

def update_selection(symbol):
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


@win.event
def on_draw():
    win.clear()
    for row in icons:
        for icon in row:
            icon.sprite.draw()

@win.event
def on_key_press(symbol, modifiers):
    update_selection(symbol)

if __name__ == "__main__":
    main()

pyglet.app.run()