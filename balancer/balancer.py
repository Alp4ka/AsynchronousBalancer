import asyncio
import json
from typing import List, Optional, Sequence
import aiohttp
from aiohttp import ClientConnectionError

from models import TaskRequest, WorkerStatus, Task
from config import BalancerConfig, WorkerConfig


class Worker:
    """Класс Worker взаимодействует с частью API
    Воркеров, необходимой для работы балансера. Для распределения задач
    Балансеру необходимо проверять состояние своих воркеров
    и иметь возможность пересылать им запросы, выполняя роль прокси.

    Attributes
    ----------
    _TIMEOUT : int
        Таймаут для вызова /compute у endpoint'а. Ввиду того, что мы симулируем процесс расчета,
        выставляем значение больше worker.utils.BASE_COMPUTATION_TIME
    _HEALTHCHECK_TIMEOUT: int
        Таймаут для проверки состояния воркера. Если воркер не отвечает в течение заданного времени -
        выставляем ему статус DEAD
    address : str
        Адрес endpoint'а
    number_of_connections : int
        Число единовременных подключений к воркеру
    protocol : str
        По умолчанию - http://

    Methods
    -------
    compute(self, task_request: TaskRequest) -> Optional[Task]
        Переслать task_request на расчет. Вернет Task в случае успеха, None
        в случае ошибки или таймаута. Вызов этого метода мы считаем за активное подключение!
    status(self) -> WorkerStatus
        Возвращает статус воркера, отсылая запрос к соответствующему endpoint.
        В случае возврата со стороны endpoint BUSY и IDLE возвращает их же, иначе -
        DEAD(как и в случае отсутствия ответа).
    from_config(config: WorkerConfig) -> Worker
        Создает воркера с конфигурацией, указанной в экземпляре WorkerConfig.
    """
    _TIMEOUT: int = 50
    _HEALTHCHECK_TIMEOUT: int = 1
    address: str
    number_of_connections: int
    protocol: str = "http://"  # noqa

    def __init__(self, address: str):
        self.address = address
        self.number_of_connections = 0

    async def compute(self, task_request: TaskRequest) -> Optional[Task]:
        """
        Переслать task_request на расчет. Вернет Task в случае успеха, None
        в случае ошибки или таймаута. Вызов этого метода мы считаем за активное подключение!

        :param task_request: TaskRequest, исходные данные для расчета.
        :return: экземпляр Task в случае успешного расчета, None - в случае таймаута или ошибки со стороны Worker
        """
        self.number_of_connections += 1
        result: Optional[Task] = None
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self._TIMEOUT)) as client:
                async with client.post(f"{self.protocol}{self.address}/compute",
                                       json=json.loads(task_request.json())) as response:
                    if response.status == 200:
                        response_json = await response.json()
                        result = Task(**response_json)
        except ClientConnectionError: pass  # noqa
        except asyncio.TimeoutError: pass  # noqa
        finally:
            self.number_of_connections -= 1
            return result

    async def status(self) -> WorkerStatus:
        """
        Возвращает статус воркера, отсылая запрос к соответствующему endpoint.
        В случае возврата со стороны endpoint BUSY и IDLE возвращает их же, иначе -
        DEAD(как и в случае отсутствия ответа).

        :return: статус воркера (WorkerStatus).
        """
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self._HEALTHCHECK_TIMEOUT)) as client:
                async with client.get(f"{self.protocol}{self.address}/status") as response:
                    if response.status == 200:
                        response_json = await response.json()
                        return WorkerStatus(response_json["status"])
            return WorkerStatus.DEAD
        except ClientConnectionError:
            return WorkerStatus.DEAD
        except asyncio.TimeoutError:
            return WorkerStatus.DEAD

    @staticmethod
    def from_config(config: WorkerConfig) -> 'Worker':
        """
        Создает воркера с конфигурацией, указанной в экземпляре WorkerConfig.

        :param config: WorkerConfig, конфигурация.
        :return: Worker, экземпляр класса Worker с заданной конфигурацией.
        """
        return Worker(address=config.address)


class Balancer:
    """Класс Worker взаимодействует с частью API
    Воркеров, необходимой для работы балансера. Для распределения задач
    Балансеру необходимо проверять состояние своих воркеров
    и иметь возможность пересылать им запросы, выполняя роль прокси.

    Attributes
    ----------
    workers : List[Worker]
        Список воркеров (и живых, и мертвых, за статус отвечает Worker.status()).

    Methods
    -------
    compute(self, task_request: TaskRequest) -> Optional[Task]
        Отправляет запрос самому незагруженному живому воркеру.
    _get_alive_workers(workers: Sequence[Worker]) -> Sequence[Worker]
        Получить живых воркеров. Живыми считаются все воркеры со статусом неравным DEAD.
    _get_least_loaded(workers: Sequence[Worker]) -> Optional[Worker]
        Получить из переданного списка самого незагруженного воркера.
    _get_workers_statuses(workers: Sequence[Worker]) -> Sequence[WorkerStatus]
        Асинхронно узнать статусы воркеров.
    from_config(config: BalancerConfig) -> Balancer
        Создает балансер с конфигурацией, указанной в экземпляре BalancerConfig.
    """
    workers: List[Worker]

    def __init__(self, workers: Optional[List[Worker]] = None):
        if workers is None:
            workers = []
        self.workers = workers

    async def compute(self, task_request: TaskRequest) -> Optional[Task]:
        """
        Передает запрос на расчет самому незагруженному живому воркеру.

        :param task_request: TaskRequest, запрос на расчет.
        :return: экземпляр Task в случае успешного расчета, None - в случае таймаута или ошибки со стороны Worker.
        """
        least_loaded_worker = self._get_least_loaded(await self._get_alive_workers(self.workers))
        if least_loaded_worker is not None:
            return await least_loaded_worker.compute(task_request)
        return None

    @staticmethod
    async def _get_alive_workers(workers: Sequence[Worker]) -> List[Worker]:
        """
        Получить живых воркеров. Живыми считаются все воркеры со статусом неравным DEAD.

        :param workers: Sequence[Worker], список воркеров, из которых следует отобрать живых.
        :return: List[Worker], список живых воркеров.
        """
        status_list = await Balancer._get_workers_statuses(workers)
        return [worker for worker, status in
                filter(lambda pair: pair[1] != WorkerStatus.DEAD, zip(workers, status_list))]

    @staticmethod
    def _get_least_loaded(workers: Sequence[Worker]) -> Optional[Worker]:
        """
        Получить самого незагруженного воркера из списка.

        :param workers: Sequence[Worker], список воркеров, из которых следует отобрать самого незагруженного.
        :return: Worker, если workers не пустой и не равен None, None - иначе.
        """
        if workers is None or not workers:
            return None
        return min(workers, key=lambda worker: worker.number_of_connections)

    @staticmethod
    def from_config(config: BalancerConfig) -> 'Balancer':
        """
        Создает балансер с конфигурацией, указанной в экземпляре BalancerConfig.

        :param config: BalancerConfig, конфигурация.
        :return: Balancer, экземпляр класса Balancer с заданной конфигурацией.
        """
        return Balancer(workers=[Worker.from_config(worker_config) for worker_config in config.workers])

    @staticmethod
    async def _get_workers_statuses(workers: Sequence[Worker]) -> Sequence[WorkerStatus]:
        """
        Узнать статусы воркеров.

        :param workers: Sequence[Worker], список воркеров, статусы которых нужно узнать.
        :return: Sequence[WorkerStatus], статусы воркеров.
        """
        gather_tasks = []
        for worker in workers:
            gather_tasks.append(asyncio.create_task(worker.status()))
        status_list = await asyncio.gather(*gather_tasks)
        return status_list
