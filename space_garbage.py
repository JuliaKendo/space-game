import asyncio
from obstacles import Obstacle
from explosion import explode
from curses_tools import draw_frame, get_frame_size


async def fly_garbage(
    canvas, column, garbage_frame, garbage_id,
    obstacles, obstacles_in_last_collisions, speed=0.5
):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""

    rows_number, columns_number = canvas.getmaxyx()
    frame_rows, frame_columns = get_frame_size(garbage_frame)

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0
    while row < rows_number and garbage_id not in obstacles_in_last_collisions:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        update_obstacle(obstacles, row, column, frame_rows, frame_columns, garbage_id)
    else:
        remove_obstacle(obstacles, garbage_id)
        if garbage_id in obstacles_in_last_collisions:
            obstacles_in_last_collisions.remove(garbage_id)
            await explode(canvas, row, column)


def update_obstacle(obstacles, row, column, frame_rows, frame_columns, garbage_id):
    obstacle_seq = set([obstacle for obstacle in obstacles if obstacle.uid == garbage_id])
    if obstacle_seq:
        obstacle, = obstacle_seq
        obstacle.row, obstacle.column, obstacle.rows_size, obstacle.columns_size =\
            row, column, frame_rows, frame_columns
    else:
        obstacles.append(
            Obstacle(row, column, frame_rows, frame_columns, uid=garbage_id)
        )


def remove_obstacle(obstacles, garbage_id):
    for obstacle in obstacles:
        obstacles.remove(obstacle) if obstacle.uid == garbage_id else True
