import curses, curses.ascii
import traceback, logging

from datetime import datetime

from .content import Content

class LogHandler(logging.Handler):

    def __init__(self, write):
        super().__init__()
        self.write = write

    def emit(self, record):
        self.write(record)


class LogView(Content):

    def __init__(self, region, logger):

        super().__init__(region)

        logger.addHandler(LogHandler(self.write))
        self.styles = {
            'ERROR': curses.color_pair(9),
            'WARNING': curses.color_pair(11),
        }
        self.menu = ['[ESC] return to previous screen']

        self.previous_state = None

    def write(self, record):

        y, x = curses.getsyx()

        if record.exc_info is not None and record.levelno == 40:
            trace = traceback.format_exception(*record.exc_info)
        else:
            trace = []

        self.content_height += len(trace) + 1
        self.first_visible = max(0, self.content_height - self.region.height)
        self.resize()

        dt = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')
        message = f'{dt} [{record.name}:{record.levelname}] {record.msg}'
        self.screen.addstr(f'\n{message}', self.styles.get(record.levelname, 0))
        for line in trace:
            self.screen.addstr(f'\n{line}')

        self.screen.clrtoeol()
        self.screen.refresh(self.first_visible, 0, *self.region.box)

        curses.setsyx(y, x)

    def draw(self):
        curses.curs_set(1)

    def handle_key(self, ch, y, x):
        if ch == curses.KEY_UP:
            self.scroll_up(y)
        elif ch == curses.KEY_DOWN:
            self.scroll_down(y)
        elif ch == curses.KEY_PPAGE:
            self.page_up(y)
        elif ch == curses.KEY_NPAGE:
            self.page_down(y)
        self.screen.refresh(self.first_visible, 0, *self.region.box)

