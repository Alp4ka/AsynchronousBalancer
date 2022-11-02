import asyncio
import json
import os

from aiohttp import ClientSession


ADDRESS = "http://localhost:8000/compute"


async def send_compute_request(session: ClientSession, payload: str, delay: int):
    await asyncio.sleep(delay)
    message = f'{{"payload": "{payload}"}}'
    response = await session.post(f"{ADDRESS}", json=json.loads(message))
    return await response.text()


async def os_execute(command: str, delay: int):
    await asyncio.sleep(delay)
    print(f"Executing '{command}'")
    os.system(command)


async def main():
    """
    Достаточными условиями для успешного тестирования при заданных настройках
    (время выполнения задачи 15сек, 5 воркеров, 1 секунда задержки) будут:
        1) Ни в один из моментов времени количество подключений у каждого сервера не может быть больше 4
        2) Нагрузка распределяется линейно, относительно общего числа подключений в момент времени
        2.1) При отключении воркера, нагрузка перераспределяется между оставшимися
             (см. AsynchronousBalancer/test/proof3.png)
        2.2) При повторном подключении воркера, нагрузка распределяется между ним и всеми живыми воркерами
             (см. AsynchronousBalancer/test/proof4.png)

    P.S.
    Аргументацию пункта (1) см. в AsynchronousBalancer/test/proof1.png. Учитываем, что есть запросы посылаются
    и обрабатываются не точно каждую 1 секунду, в связи с чем картинка proof1.png является идеальным примером
    Least Connections при заданных настройках.

    Также на AsynchronousBalancer/test/proof2.png заметим, что после отключения крайних двух сессий воркер стал
    самым незагруженным, в связи с чем следующие два подключения отдали ему.

    Недостатком моего решения является то, что с появлением неактивного воркера время распределения задачи увеличивается
    с AVERAGE_RESPONSE_TIME до HEALTHCHECK_TIMEOUT. Решается это добавлением ручки /register в балансер
    (что лишает смысла писать для него конфиг), либо Scheduled проверкой воркеров на живучесть и хранением status
    как свойства balancer.Worker, что тоже имеет свои недостатки(например, некоторые запросы могут пятисотить
    просто потому, что мы распределили их в неработающий воркер до проверки на хелсчек).

    -----------------------------------------------------------------------------------------------------------
    В любом случае таймаут = 1 секунде, очевидно, не самое адекватное решение, но в целях демонстрации подойдет.
    """
    os.system("cd ../")
    async with ClientSession() as session:
        tasks = []
        for i in range(250):
            if i == 100:
                tasks.append(os_execute("docker-compose kill -s SIGKILL worker1", delay=i))
            elif i == 200:
                tasks.append(os_execute("docker-compose restart worker1", delay=i))
            else:
                tasks.append(send_compute_request(session=session, payload="test_payload", delay=i))
        results = await asyncio.gather(*tasks, return_exceptions=False)
        print(results)

if __name__ == "__main__":
    asyncio.run(main())
