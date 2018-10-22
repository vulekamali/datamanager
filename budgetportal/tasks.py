import logging
import time

logger = logging.getLogger(__name__)


def do_something(fred, john):
    logger.info("\nGOT TASK")
    time.sleep(10)
    logger.info("DOING SOMETHING fred=%r, john=%r\n", fred, john)
