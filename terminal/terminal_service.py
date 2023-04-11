import logging
from collections import deque
from multiprocessing import Process, Queue
from threading import Thread
from typing import Deque, Tuple

import matplotlib.pyplot as plt

from common.log import format_proto_msg
from proto.services.terminal.terminal_service_pb2 import Results

logger = logging.getLogger(__name__)


class TerminalService:
    def __init__(
            self,
            max_results: int = 50
    ):
        logger.info("Initializing TerminalService")
        self._max_results = max_results
        self._wellness_data: Queue[Deque[Tuple[str, float]]] = Queue(maxsize=max_results)
        self._wellness_data_deque: Deque[Tuple[str, float]] = deque(maxlen=max_results)
        self._pollution_data: Queue[Deque[Tuple[str, float]]] = Queue(maxsize=max_results)
        self._pollution_data_deque: Deque[Tuple[str, float]] = deque(maxlen=max_results)
        self._animation = None
        self._plot_process = None

    async def receive_results(self, results: Results):
        logger.debug(f"Received results: {format_proto_msg(results)}")
        if results.wellness_timestamp.ToNanoseconds() != 0:
            self._wellness_data_deque.append((
                results.wellness_timestamp.ToDatetime().strftime('%H:%M:%S.%f'),
                results.wellness_data
            ))
        if results.pollution_timestamp.ToNanoseconds() != 0:
            self._pollution_data_deque.append((
                results.pollution_timestamp.ToDatetime().strftime('%H:%M:%S.%f'),
                results.pollution_data
            ))

        if len(self._wellness_data_deque) > self._max_results:
            self._wellness_data_deque.popleft()
        if len(self._pollution_data_deque) > self._max_results:
            self._pollution_data_deque.popleft()

        self._wellness_data.put(self._wellness_data_deque)
        self._pollution_data.put(self._pollution_data_deque)

    def _update_plot(self, wellness_data: Deque[Tuple[str, float]], pollution_data: Deque[Tuple[str, float]]):
        # clear the plot
        self._ax1.clear()
        self._ax2.clear()

        # wellness data
        self._ax1.set_title("Wellness data")
        self._ax1.set_xlabel("Timestamp")
        self._ax1.set_ylabel("Wellness")

        w = wellness_data
        logger.debug(f"Plotting wellness data: {w}")
        self._ax1.plot([x[0] for x in w], [x[1] for x in w])

        # pollution data
        self._ax2.set_title("Pollution data")
        self._ax2.set_xlabel("Timestamp")
        self._ax2.set_ylabel("Pollution")

        p = pollution_data
        logger.debug(f"Plotting pollution data: {p}")
        self._ax2.plot([x[0] for x in p], [x[1] for x in p])

        # format the plot
        self._ax1.set_xticklabels(self._ax1.get_xticklabels(), rotation=45, ha='right')
        self._ax2.set_xticklabels(self._ax2.get_xticklabels(), rotation=45, ha='right')
        plt.subplots_adjust(bottom=0.30)
        plt.tight_layout()

        self._fig.canvas.draw()

    def _plot_data(self, wellness_data, pollution_data):
        logger.info("Starting plot process")
        self._fig, (self._ax1, self._ax2) = plt.subplots(2)

        self._wellness_data = wellness_data
        self._pollution_data = pollution_data

        Thread(target=self._animate).start()

        plt.show()

    def _animate(self):
        while True:
            self._update_plot(self._wellness_data.get(), self._pollution_data.get())

    def run(self):
        logger.info("Running TerminalService")

        self._plot_process = Process(target=self._plot_data, args=(self._wellness_data, self._pollution_data))
        self._plot_process.start()
