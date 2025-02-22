# -*- coding: utf-8 -*-
# Time       : 2021/12/22 9:05
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import asyncio
import os
from typing import Optional, List, Union

import aiohttp
import gevent
from gevent import queue


class CoroutineSpeedup:
    """轻量化的协程控件"""

    def __init__(self, docker: Optional[List] = None, power: Optional[int] = None):
        # 任务容器：queue
        self.worker, self.done = queue.Queue(), queue.Queue()

        # 任务容器
        self.docker = docker

        # 协程数
        self.power = max(os.cpu_count(), 2) if power is None else power

        # 任务队列满载时刻长度
        self.max_queue_size = 0

    def progress(self) -> str:
        """
        任务进度

        :return:
        """
        _progress = self.max_queue_size - self.worker.qsize()
        return (
            "__pending__"
            if _progress < self.power
            else f"{_progress}/{self.max_queue_size}"
        )

    def launcher(self, *args, **kwargs):
        """
        适配器实例生产

        :return:
        """
        while not self.worker.empty():
            task = self.worker.get_nowait()
            self.control_driver(task, *args, **kwargs)

    def control_driver(self, task, *args, **kwargs):
        """
        默认逻辑

        :param task:
        :return:
        """
        raise NotImplementedError

    def preload(self):
        """
        数据预处理

        :return:
        """

    def overload(self):
        """
        任务重载

        :return:
        """
        if self.docker:
            for task in self.docker:
                self.worker.put_nowait(task)
        self.max_queue_size = self.worker.qsize()

    def offload(self) -> list:
        """
        缓存卸载

        :return:
        """
        docker = []
        while not self.done.empty():
            docker.append(self.done.get())
        return docker

    def killer(self):
        """
        缓存回收

        :return:
        """

    def speedup(self, *args, **kwargs):
        """
        框架接口

        :return:
        """

        # 任务重载
        self.overload()

        # 弹出空载任务
        if self.max_queue_size == 0:
            return

        # 粘性功率
        power = kwargs.get("power")
        self.power = self.power if power is None else power
        self.power = (
            self.max_queue_size if self.power > self.max_queue_size else self.power
        )

        # 任务启动
        task_list = []
        for _ in range(self.power):
            task = gevent.spawn(self.launcher, *args, **kwargs)
            task_list.append(task)
        try:
            gevent.joinall(task_list)
        finally:
            self.killer()


class AshFramework:
    """轻量化的协程控件"""

    def __init__(self, docker: Optional[List] = None):
        # 任务容器：queue
        self.worker, self.done = asyncio.Queue(), asyncio.Queue()
        # 任务容器
        self.docker = docker
        # 任务队列满载时刻长度
        self.max_queue_size = 0

    def progress(self) -> str:
        """任务进度"""
        _progress = self.max_queue_size - self.worker.qsize()
        return f"{_progress}/{self.max_queue_size}"

    def preload(self):
        """预处理"""

    def overload(self):
        """任务重载"""
        if self.docker:
            for task in self.docker:
                self.worker.put_nowait(task)
        self.max_queue_size = self.worker.qsize()

    def offload(self) -> Optional[List]:
        """缓存卸载"""
        crash = []
        while not self.done.empty():
            crash.append(self.done.get())
        return crash

    async def control_driver(self, context, session=None):
        """需要并发执行的代码片段"""
        raise NotImplementedError

    async def launcher(self, session=None):
        """适配接口模式"""
        while not self.worker.empty():
            context = self.worker.get_nowait()
            await self.control_driver(context, session=session)

    async def subvert(self, workers: Union[str, int] = None):
        """
        框架接口

        loop = asyncio.get_event_loop()
        loop.run_until_complete(fl.go(workers))

        :param workers: ["fast", power]
        :return:
        """
        # 任务重载
        self.overload()

        # 弹出空载任务
        if self.max_queue_size == 0:
            return

        # 粘性功率
        workers = self.max_queue_size if workers in ["fast"] else workers
        workers = workers if workers <= self.max_queue_size else self.max_queue_size

        # 弹性分发
        task_list = []
        async with aiohttp.ClientSession() as session:
            for _ in range(workers):
                task = self.launcher(session=session)
                task_list.append(task)
            await asyncio.wait(task_list)
