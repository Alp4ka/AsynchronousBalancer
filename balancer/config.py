from abc import abstractmethod
import xml.etree.ElementTree as ElementTree
from typing import Optional, List


class Config:
    @staticmethod
    @abstractmethod
    def from_xml(xml_path: str) -> Optional['Config'] | List['Config']: pass

    @staticmethod
    @abstractmethod
    def from_xml_element(element: ElementTree.Element) -> 'Config': pass


class WorkerConfig(Config):
    address: str

    def __init__(self, address: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.address = address

    @staticmethod
    def from_xml(xml_path: str) -> List['WorkerConfig']:
        if xml_path is None:
            raise ValueError("Arguments were None!")
        root = ElementTree.parse(xml_path).getroot()
        workers_xml_element = root.find('workers')
        if workers_xml_element is None:
            return []

        workers_configs = []
        for worker_xml_element in workers_xml_element.iterfind('worker'):
            workers_configs.append(WorkerConfig.from_xml_element(worker_xml_element))

        return workers_configs

    @staticmethod
    def from_xml_element(element: ElementTree.Element) -> 'WorkerConfig':
        if element is None:
            raise ValueError("Element was None!")
        address_element = element.find('address')
        if address_element is None:
            return WorkerConfig(address="")
        address = address_element.text.strip()
        return WorkerConfig(address=address)


class BalancerConfig(Config):
    workers: List[WorkerConfig]

    def __init__(self, workers: Optional[List[WorkerConfig]] = None, *args, **kwargs):
        if workers is None:
            workers = []
        self.workers = workers
        super().__init__()

    @staticmethod
    def from_xml(xml_path: str) -> 'BalancerConfig':
        if xml_path is None:
            return BalancerConfig()
        return BalancerConfig.from_xml_element(ElementTree.parse(xml_path).getroot())

    @staticmethod
    def from_xml_element(element: ElementTree.Element) -> 'BalancerConfig':
        if element is None:
            return BalancerConfig()
        workers_xml_element = element.find('workers')
        if workers_xml_element is None:
            return BalancerConfig()

        workers_configs = []
        for worker_xml_element in workers_xml_element.iterfind('worker'):
            workers_configs.append(WorkerConfig.from_xml_element(worker_xml_element))

        return BalancerConfig(workers=workers_configs)
