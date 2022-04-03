import time
import asyncio

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from threading import Thread


MAIN_THREAD = None
MENU_CYCLE_INTERVAL = 10.0
COUNTY_CYCLE_INTERVAL = 7.5
REFRESH_INTERVAL = 70.0

EXT_PATH = r'C:\Users\csino\OneDrive\Asztali gép\Portfolio\3.12_0'


class MainThread(Thread):

    COUNTIES = ['06-01', '06-02', '06-03', '06-04']

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
                if self.index == 0:
                    self.cycleCounties()
                elif self.index == 3:
                    driver.find_elements(By.CSS_SELECTOR, 'span.hasResult[data-time]')[::-1][0].click()
            except selenium.common.exceptions.StaleElementReferenceException:
                continue

            self.index += 1
            time.sleep(MENU_CYCLE_INTERVAL)

    def cycleCounties(self):
        for area in self.COUNTIES:
            driver.execute_script(f"showCounty('{area}')")
            time.sleep(COUNTY_CYCLE_INTERVAL)
        driver.execute_script('hideCounty()')

    async def reset(self):
        self._get_menu_items()
        self.index = 0


async def onRefresh():
    driver.refresh()
    driver.execute_script("window.scrollTo(0, 475)")
    driver.fullscreen_window()
    driver.find_element(By.CSS_SELECTOR, 'div.el-menu>div.el-menu-item[data-index="1"]').click()

    try:
        sticky = driver.find_element(By.CSS_SELECTOR, 'div.sticky-news')
        driver.execute_script('arguments[0].parentNode.removeChild(arguments[0])', sticky)
    except selenium.common.exceptions.NoSuchElementException as e:
        pass

    driver.execute_script('arguments[0].parentNode.removeChild(arguments[0])',
                          driver.find_element(By.CSS_SELECTOR, 'div.mf_inner'))


async def refreshPage():
    await asyncio.sleep(REFRESH_INTERVAL)
    await onRefresh()
    await MAIN_THREAD.reset()


async def mainLoop():
    task = asyncio.create_task(refreshPage())
    await task
    await mainLoop()


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument('load-extension=' + EXT_PATH)

    driver = webdriver.Chrome(options=chrome_options)
    driver.create_options()

    driver.implicitly_wait(0)
    driver.get('https://www.portfolio.hu/valasztas')

    time.sleep(10)
    asyncio.run(onRefresh())

    MAIN_THREAD = MainThread()
    MAIN_THREAD.start()
    asyncio.run(mainLoop())
