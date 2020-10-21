import os
import time
import glob
import curses
import asyncio
import random

from itertools import cycle
from curses_tools import draw_frame, read_controls, get_frame_size


TIC_TIMEOUT = 0.1
MAX_PAUSE_BEFORE_BLINK = 20
OFFSET_FROM_EDGE_OF_SCREEN = 1
FRAME_OFFSET = 2
KINDS_OF_STARS = ['+', '*', '.', ':']
ROCKET_SPEED = os.getenv('ROCKET_SPEED', default='1')


async def animate_spaceship(canvas, row, column, frames):
    screen_rows, screen_columns = canvas.getmaxyx()
    max_row, max_column = screen_rows - OFFSET_FROM_EDGE_OF_SCREEN, screen_columns - OFFSET_FROM_EDGE_OF_SCREEN
    for frame in cycle(frames):
        frame_rows, frame_columns = get_frame_size(frame)
        for _ in range(2):
            rows_direction, columns_direction, space_pressed = read_controls(canvas)

            row = max(
                OFFSET_FROM_EDGE_OF_SCREEN,
                min(row + rows_direction * int(ROCKET_SPEED), max_row - frame_rows)
            )
            column = max(
                OFFSET_FROM_EDGE_OF_SCREEN,
                min(column + columns_direction * int(ROCKET_SPEED), max_column - frame_columns)
            )

            draw_frame(canvas, row, column, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, frame, negative=True)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - OFFSET_FROM_EDGE_OF_SCREEN, columns - OFFSET_FROM_EDGE_OF_SCREEN

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol='*', pause=0):
    for i in range(pause):
        await asyncio.sleep(0)
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(15):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_NORMAL)
        for _ in range(2):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_NORMAL)
        for _ in range(2):
            await asyncio.sleep(0)


def get_stars(canvas, rows, columns):
    coroutines = []
    screen_side_ratio = round(rows / columns * 100)
    for cell_number in range(1, (rows * columns) - columns):
        row_number = round(cell_number / columns + 0.5)
        column_number = cell_number - columns * (row_number - 1)
        if not random.randint(0, screen_side_ratio) == screen_side_ratio or column_number == 0:
            continue
        coroutines.append(
            blink(
                canvas,
                row_number,
                column_number,
                random.choice(KINDS_OF_STARS),
                random.randint(0, MAX_PAUSE_BEFORE_BLINK)
            )
        )
    return coroutines


def load_rocket_frames():
    rocket_frames = []
    for rocket_frame_file_path in glob.glob('frames/*.txt'):
        with open(rocket_frame_file_path, 'r') as file_handler:
            rocket_frames.append(file_handler.read())
    return rocket_frames


def draw(canvas):
    canvas.border()
    curses.curs_set(0)
    canvas.nodelay(True)
    rows, columns = canvas.getmaxyx()
    middle_row, middle_column = int(rows / 2), int(columns / 2)
    rocket_frames = load_rocket_frames()
    coroutines = [
        *get_stars(canvas, rows - OFFSET_FROM_EDGE_OF_SCREEN, columns - OFFSET_FROM_EDGE_OF_SCREEN),
        fire(canvas, middle_row, middle_column),
        animate_spaceship(canvas, middle_row - FRAME_OFFSET, middle_column - FRAME_OFFSET, rocket_frames)
    ]
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.wrapper(draw)
