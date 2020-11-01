import time
import glob
import curses
import asyncio
import random

from itertools import cycle
from physics import update_speed
from space_garbage import fly_garbage
from curses_tools import (
    draw_frame,
    read_controls,
    get_frame_size
)


TIC_TIMEOUT = 0.1
MAX_PAUSE_BEFORE_BLINK = 20
OFFSET_FROM_EDGE_OF_SCREEN = 1
FRAME_OFFSET = 2
KINDS_OF_STARS = ['+', '*', '.', ':']

coroutines = []


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def fill_orbit_with_garbage(canvas, rows, columns, frames):
    screen_side_ratio = round(rows / columns * 100)
    while True:
        coroutines.append(
            fly_garbage(
                canvas,
                random.randint(
                    OFFSET_FROM_EDGE_OF_SCREEN,
                    columns - OFFSET_FROM_EDGE_OF_SCREEN
                ),
                random.choice(frames)
            )
        )
        await sleep(random.randint(0, screen_side_ratio * 2))


async def animate_spaceship(canvas, row, column, frames):
    row_speed = column_speed = 0
    screen_rows, screen_columns = canvas.getmaxyx()
    max_row, max_column = screen_rows - OFFSET_FROM_EDGE_OF_SCREEN, screen_columns - OFFSET_FROM_EDGE_OF_SCREEN
    for frame in cycle(frames):
        frame_rows, frame_columns = get_frame_size(frame)
        for _ in range(2):
            rows_direction, columns_direction, space_pressed = read_controls(canvas)
            row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction, columns_direction)
            row += row_speed
            column += column_speed

            row = max(
                OFFSET_FROM_EDGE_OF_SCREEN,
                min(row + rows_direction, max_row - frame_rows)
            )
            column = max(
                OFFSET_FROM_EDGE_OF_SCREEN,
                min(column + columns_direction, max_column - frame_columns)
            )
            coroutines.append(
                fire(canvas, row, column + round(frame_columns / 2))
            ) if space_pressed else True
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
    await sleep(pause)
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(15)

        canvas.addstr(row, column, symbol, curses.A_NORMAL)
        await sleep(2)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_NORMAL)
        await sleep(2)


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
    for rocket_frame_file_path in glob.glob('frames/rocket*.txt'):
        with open(rocket_frame_file_path, 'r') as file_handler:
            rocket_frames.append(file_handler.read())
    return rocket_frames


def load_garbage_frames():
    garbage_frames = []
    for garbage_frame_file_path in glob.glob('frames/trash*.txt'):
        with open(garbage_frame_file_path, 'r') as file_handler:
            garbage_frames.append(file_handler.read())
    return garbage_frames


def draw(canvas):
    global coroutines
    canvas.border()
    curses.curs_set(0)
    canvas.nodelay(True)
    rows, columns = canvas.getmaxyx()
    middle_row, middle_column = int(rows / 2), int(columns / 2)
    rocket_frames = load_rocket_frames()
    garbage_frames = load_garbage_frames()
    coroutines = [
        *get_stars(canvas, rows - OFFSET_FROM_EDGE_OF_SCREEN, columns - OFFSET_FROM_EDGE_OF_SCREEN),
        animate_spaceship(canvas, middle_row - FRAME_OFFSET, middle_column - FRAME_OFFSET, rocket_frames),
        fill_orbit_with_garbage(canvas, rows, columns, garbage_frames)
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
