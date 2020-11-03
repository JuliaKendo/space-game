SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def draw_frame_border(canvas, start_row, start_column, text, frame, offset_from_edge_of_screen):
    rows, columns = canvas.getmaxyx()
    frame_rows, frame_columns = get_frame_size(frame)
    for offset_column in range(frame_columns):
        next_column = min(round(start_column) + offset_column, columns - offset_from_edge_of_screen)
        max_row = min(round(start_row) + frame_rows, rows - offset_from_edge_of_screen)
        if next_column >= columns - offset_from_edge_of_screen or round(start_row) >= rows:
            break
        canvas.addstr(round(start_row), next_column, text)
        canvas.addstr(max_row, next_column, text)
    for offset_row in range(frame_rows):
        next_row = min(round(start_row) + offset_row, rows - offset_from_edge_of_screen)
        max_column = min(round(start_column) + frame_columns, columns - offset_from_edge_of_screen)
        if next_row >= rows - offset_from_edge_of_screen or round(start_column) >= columns:
            break
        canvas.addstr(round(next_row), start_column, text)
        canvas.addstr(next_row, max_column, text)
