import asyncio
import datetime

from models import Task, TaskStatus
import random

BASE_COMPUTATION_TIME = 15
LOWER_RANDOM_CONSTRAINTS = 0
UPPER_RANDOM_CONSTRAINTS = 100


async def simulate_computation(task: Task, seconds: int = BASE_COMPUTATION_TIME):
    """
    Симулирует какие-то расчеты с таской.

    :param task: Task, Таска, с которой надо работать
    :param seconds: int, Сколько времени будет выполняться симуляция
    :return: None
    """
    task.status = TaskStatus.IN_PROGRESS

    await asyncio.sleep(seconds)

    task.result = random.randint(LOWER_RANDOM_CONSTRAINTS, UPPER_RANDOM_CONSTRAINTS) + random.random()

    task.date = datetime.datetime.now()
    task.status = TaskStatus.DONE
