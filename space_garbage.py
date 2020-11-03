import asyncio
from obstacles import Obstacle
from explosion import explode
from curses_tools import draw_frame, get_frame_size


async def fly_garbage(canvas, column, garbage_frame, obstacles, knocked_down_garbages, garbage_id, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""

    rows_number, columns_number = canvas.getmaxyx()
    frame_rows, frame_columns = get_frame_size(garbage_frame)

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0
    while row < rows_number and garbage_id not in knocked_down_garbages:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        obstacles.append(
            Obstacle(row, column, frame_rows, frame_columns, uid=garbage_id)
        )
    else:
        for obstacle in [obstacle for obstacle in obstacles if obstacle.uid == garbage_id]:
            obstacles.remove(obstacle)
        if garbage_id in knocked_down_garbages:
            knocked_down_garbages.remove(garbage_id)
            await explode(canvas, row, column)
