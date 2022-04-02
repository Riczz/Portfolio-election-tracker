import time
import asyncio

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from threading import Thread


MAIN_THREAD = None
CYCLE_INTERVAL = 10.0
REFRESH_INTERVAL = 80.0

EXT_PATH = r'D:\PycharmProjects\Portfolio\3.12_0'


class MainThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._get_menu_items()
        self._index = 0

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = 0 if value >= 4 else value

    def _get_menu_items(self):
        self.menu_items = driver.find_elements(By.CSS_SELECTOR, 'div.el-menu>div.el-menu-item')

    def run(self) -> None:
        while True:
            try:
                self.menu_items[self.index].click()
                if self.index == 3:
                    driver.find_elements(By.CSS_SELECTOR, 'span.hasResult[data-time]')[::-1][0].click()
            except selenium.common.exceptions.StaleElementReferenceException:
                pass
            self.index += 1
            time.sleep(CYCLE_INTERVAL)

    def reset(self):
        self._get_menu_items()
        self.index = 0


def onRefresh():
    driver.refresh()
    driver.execute_script("window.scrollTo(0, 475)")
    driver.fullscreen_window()
    driver.find_element(By.CSS_SELECTOR, 'div.el-menu>div.el-menu-item[data-index="1"]').click()
    driver.execute_script('arguments[0].parentNode.removeChild(arguments[0])',
                          driver.find_element(By.CSS_SELECTOR, 'div.mf_inner'))


async def refreshPage():
    await asyncio.sleep(REFRESH_INTERVAL)
    onRefresh()


async def mainLoop():
    task = asyncio.create_task(refreshPage())
    task.add_done_callback(lambda result: MAIN_THREAD.reset())
    await task
    await mainLoop()


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument('load-extension=' + EXT_PATH)

    driver = webdriver.Chrome(options=chrome_options)
    driver.create_options()

    driver.implicitly_wait(10)
    driver.get('https://www.portfolio.hu/valasztas')

    time.sleep(10)
    onRefresh()

    MAIN_THREAD = MainThread()
    MAIN_THREAD.start()
    asyncio.run(mainLoop())
