from typing import List, Any, Optional, Type
import time
import sys
import threading

frames: List[str] = ["⠋ ", "⠙ ", "⠹ ", "⠸ ", "⠼ ", "⠴ ", "⠦ ", "⠧ ", "⠇ ", "⠏ "]


def _animate(stop_event: threading.Event, delay: float = 0.05) -> None:
    while not stop_event.is_set():
        for frame in frames:
            if stop_event.is_set():
                break
            sys.stdout.write("\r" + frame)
            sys.stdout.flush()
            time.sleep(delay)

    sys.stdout.write("\r    \r")
    sys.stdout.flush()


class LoadingAnimation:
    def __init__(self, delay: float = 0.05) -> None:
        self.delay = delay
        self.stop_event: threading.Event = threading.Event()
        self.thread: Optional[threading.Thread] = None

    def __enter__(self) -> "LoadingAnimation":
        self.start()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Any,
    ) -> None:
        self.stop()

    def start(self) -> None:
        self.stop_event.clear()
        self.thread = threading.Thread(
            target=_animate, args=(self.stop_event, self.delay)
        )
        self.thread.daemon = True
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread:
            self.thread.join()
