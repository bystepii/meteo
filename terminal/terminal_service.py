import logging
from collections import deque
from multiprocessing import Process, Queue
from typing import Deque, Tuple

import matplotlib.animation as animation
import matplotlib.pyplot as plt

from common.log import format_proto_msg
from proto.services.terminal.terminal_service_pb2 import Results

logger = logging.getLogger(__name__)


class TerminalService:
    def __init__(self, max_results: int = 50):
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

    def plot_data(self, wellness_data: Queue, pollution_data: Queue):
        self._wellness_data = wellness_data
        self._pollution_data = pollution_data
        logger.debug("Plotting data")
        fig, (ax1, ax2) = plt.subplots(2)

        def animate(i):
            # clear the axes
            ax1.clear()
            ax2.clear()

            # wellness data
            w = self._wellness_data.get()
            logger.debug(f"Plotting wellness data: {w}")
            ax1.plot([x[0] for x in w], [x[1] for x in w])
            ax1.set_title("Wellness data")
            ax1.set_xlabel("Timestamp")
            ax1.set_ylabel("Wellness")

            # pollution data
            p = self._pollution_data.get()
            logger.debug(f"Plotting pollution data: {p}")
            ax2.plot([x[0] for x in p], [x[1] for x in p])
            ax2.set_title("Pollution data")
            ax2.set_xlabel("Timestamp")
            ax2.set_ylabel("Pollution")

            # format the plot
            ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
            ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
            plt.subplots_adjust(bottom=0.30)

            plt.tight_layout()

        self._animation = animation.FuncAnimation(fig, animate, interval=1000)
        plt.show()

    async def run(self):
        logger.info("Running TerminalService")

        self._plot_process = Process(target=self.plot_data, args=(self._wellness_data, self._pollution_data))
        self._plot_process.start()
