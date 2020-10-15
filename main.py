import os
import time
import glob
import curses
import asyncio
from numpy import random
from curses_tools import draw_frame, read_controls, get_frame_size


TIC_TIMEOUT = 0.1
MAX_PAUSE_BEFORE_BLINK = 20
KINDS_OF_STARS = ['+', '*', '.', ':']
ROCKET_SPEED = os.getenv('ROCKET_SPEED', default='1')


async def animate_spaceship(canvas, row, column, frames):
    screen_rows, screen_columns = canvas.getmaxyx()
    while True:
        for frame in frames:
            frame_rows, frame_columns = get_frame_size(frame)
            draw_frame(canvas, row, column, frame)
            for i in range(2):
                await asyncio.sleep(0)
            draw_frame(canvas, row, column, frame, negative=True)

            rows_direction, columns_direction, space_pressed = read_controls(canvas)

            next_row = row + rows_direction * int(ROCKET_SPEED)
            max_row = screen_rows - frame_rows
            if 0 <= min(0 if next_row < 0 else next_row, max_row - 1) < max_row:
                row = min(0 if next_row < 0 else next_row, max_row - 1)
                row = row if row else 1

            next_column = column + columns_direction * int(ROCKET_SPEED)
            max_column = screen_columns - frame_columns
            if 0 <= min(0 if next_column < 0 else next_column, max_column - 1) < max_column:
                column = min(0 if next_column < 0 else next_column, max_column - 1)
                column = column if column else 1


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
    max_row, max_column = rows - 1, columns - 1

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
        for i in range(15):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_NORMAL)
        for i in range(2):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for i in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_NORMAL)
        for i in range(2):
            await asyncio.sleep(0)


def get_stars(canvas, rows, columns):
    coroutines = []
    array = random.randint(0, round(rows / columns * 100), (rows - 2, columns - 2))
    for number_of_row, row in enumerate(array):
        for number_of_column, value in enumerate(row):
            if not value == (round(rows / columns * 100)) - 1:
                continue
            coroutines.append(
                blink(
                    canvas,
                    number_of_row + 1,
                    number_of_column + 1,
                    random.choice(KINDS_OF_STARS),
                    random.randint(0, MAX_PAUSE_BEFORE_BLINK)
                )
            )
    return coroutines


def load_rocket_frames():
    rocket_frames = []
    for rocket_frame_file in glob.glob('frames/*.txt'):
        with open(rocket_frame_file, 'r') as file_handler:
            rocket_frames.append(file_handler.read())
    return rocket_frames


def draw(canvas):
    canvas.border()
    curses.curs_set(0)
    canvas.nodelay(True)
    rows, columns = canvas.getmaxyx()
    rocket_frames = load_rocket_frames()
    coroutines = [
        *get_stars(canvas, rows, columns),
        fire(canvas, int(rows / 2), int(columns / 2)),
        animate_spaceship(canvas, int(rows / 2) - 2, int(columns / 2) - 2, rocket_frames)
    ]
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
                continue
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.wrapper(draw)
