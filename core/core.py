import re
import sys
import time
import codecs
from typing import Dict
from pathlib import Path
from datetime import datetime
from configparser import ConfigParser

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as ec

from .constants import CONF_ITEMS, TRAIN_TYPE_MAP, TICKET_MAP, SEAT_MAP, TIME_RANGE_MAP


def _time_print(msg: str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


class TicketProcessor:
    """
    处理流程：
        1. 读取配置文件, 设置关键参数
        2. 进入登录页面（需要验证码登录），登录成功
        3. 进入火车票预订页面，选择火车信息
        4. 选择乘车人，确认订单
        5. 乘车人付款
    """
    DRIVER_MAP = {'chrome': webdriver.Chrome, 'firefox': webdriver.Firefox, 'safari': webdriver.safari,
                  'edge': webdriver.Edge}
    TIME_OUT = 600
    SMALL_INTERVAL = 0.05
    MIDDLE_INTERVAL = 0.3
    BIG_INTERVAL = 5
    SEP_PATTERN = r'[,，]'
    PASSENGER_PATTERN = "//ul[@id='normal_passenger_id']/li/label"

    def __init__(self) -> None:
        self._load_driver_path()
        self._conf = self._read_config()
        self._driver = self.DRIVER_MAP.get(self._conf.get('driver_name'))()
        self._driver.maximize_window()

    @staticmethod
    def _load_driver_path() -> None:
        drivers_path = str(Path(__file__).absolute().parent.parent / "drivers")
        sys.path.append(drivers_path)

    def _read_config(self, config_file_path: str = "ticket.ini") -> Dict[str, str]:
        _time_print("开始加载配置文件")
        cp = ConfigParser()
        try:
            cp.read_file(codecs.open(config_file_path, 'r', 'utf-8-sig'))
        except IOError as _:
            config_file_name = Path(config_file_path).name
            _time_print(f"打开配置文件失败{config_file_name}失败，请先创建一份{config_file_name}")
            sys.exit()
        config_dictionary = dict()
        for title, infos in CONF_ITEMS.items():
            for info in infos:
                if cp.get(title, info).strip():
                    config_dictionary.__setitem__(info.strip(), cp.get(title, info).strip())
        return config_dictionary

    def _login(self) -> None:
        _time_print("开始登录")
        self._driver.get(self._conf.get('login_url'))
        # 填写账号和密码
        self._driver.find_element(value="J-userName").send_keys(self._conf.get("username"))
        self._driver.find_element(value="J-password").send_keys(self._conf.get("password"))
        # 点击登录
        self._driver.find_element(value="J-login").click()
        # 等待访问网页是否加载
        WebDriverWait(timeout=self.TIME_OUT, driver=self._driver).until(ec.url_to_be(self._conf.get("init_url")))
        _time_print("登录成功")

    def _pre_start(self) -> None:
        """
        添加起止时间和地址
        :return:
        """
        for des in ("from", "to"):
            el = self._driver.find_element(value=f"{des}StationText")
            el.click()
            el.send_keys(self._conf.get(des))
            el.send_keys(Keys.ENTER)
        start_date_input = self._driver.find_element(value="train_date")
        start_date_input.clear()
        start_date_input.send_keys(self._conf.get("start_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def _search(self) -> None:
        for train_type in re.split(self.SEP_PATTERN, self._conf.get("train_types", '')):
            train_type = train_type.strip()
            if train_type not in TRAIN_TYPE_MAP:
                _time_print(f"车次类型异常或未选择!(train_type={train_type})")
            else:
                self._driver.find_element(by=By.XPATH,
                                          value=f"//label[text()='{TRAIN_TYPE_MAP.get(train_type)}']").click()
        if self._conf.get("start_date"):
            self._driver.find_element(value="query_ticket").click()
            time.sleep(self.MIDDLE_INTERVAL)
            # 等待车次列表是否加载进来
            WebDriverWait(timeout=self.TIME_OUT, driver=self._driver).until(
                ec.presence_of_all_elements_located((By.XPATH, "//tbody[@id='queryLeftTable']/tr")))
        else:
            _time_print("未指定发车时间, 默认00:00-24:00")

    def _pre_book(self, order: int = 0) -> None:
        # 选择列出出发时间点
        start_time_range = self._conf.get("start_time_range", "00:00--24:00")
        if start_time_range:
            ranges = self._driver.find_elements(value="cc_start_time")
            for range_ in ranges:
                range_dropdown = Select(range_)
                range_dropdown.select_by_value(TIME_RANGE_MAP.get(start_time_range))
        cnt = 0
        while self._driver.current_url == self._conf.get("ticket_url"):
            self._search()
            cnt += 1
            _time_print(f"持续抢票...第{cnt}次")
            try:
                book_items = self._driver.find_elements(by=By.XPATH, value="//a[text()='预订']")
                if order > 0:
                    book_items[order - 1].click()
                    time.sleep(self.MIDDLE_INTERVAL)
                else:
                    for book_item in book_items:
                        book_item.click()
                        time.sleep(self.MIDDLE_INTERVAL)
            except Exception as _:
                _time_print("还没开始预订")
                continue

    def _choose(self) -> None:
        _time_print("开始预订票")
        self._driver.get(self._conf.get("ticket_url"))
        self._pre_start()
        self._pre_book(int(self._conf.get('order', 0)))
        _time_print("成功选择订票车次")

    def _ensure_passengers(self) -> None:
        # 等待是否进入提交订单页面
        # WebDriverWait(timeout=self.TIME_OUT, driver=self._driver).until(ec.url_to_be(self._conf.get('buy_url')))
        # 等待乘客按钮是否加载完毕

        # WebDriverWait(timeout=self.TIME_OUT, driver=self._driver).until(
        #     ec.presence_of_all_elements_located((By.XPATH, passenger_pattern)))
        _time_print("开始选择乘客")
        passenger_labels = self._driver.find_elements(by=By.XPATH, value=self.PASSENGER_PATTERN)
        select_passengers = re.split(self.SEP_PATTERN, self._conf.get("users"))
        for passenger_label in passenger_labels:
            if passenger_label.text in select_passengers:
                passenger_label.click()
        # 判断手机号绑定验证“qd_closeDefaultWarningWindowDialog_id”
        confirm_phone_func = ec.visibility_of_element_located((By.ID, "qd_closeDefaultWarningWindowDialog_id"))
        try:
            confirm_phone_func(self._driver).click()
        except NoSuchElementException as _:
            pass
        _time_print("成功选择乘客")

    def _ensure_ticket_type(self) -> None:
        _time_print("开始选择票种")
        ticket_type = self._conf.get("ticket_type", "成人票")
        if ticket_type:
            tickets = self._driver.find_elements(by=By.XPATH, value="//select[starts-with(@id,'ticketType')]")
            for ticket in tickets:
                ticket_type_dropdown = Select(ticket)
                ticket_type_dropdown.select_by_value(TICKET_MAP.get(ticket_type))
        _time_print("票种选择成功")

    def _ensure_seat_type(self) -> None:
        _time_print("开始选择席别")
        seat_type = self._conf.get("seat_type", "二等座")
        if seat_type:
            seats = self._driver.find_elements(by=By.XPATH, value="//select[starts-with(@id,'seatType')]")
            for seat in seats:
                seat_type_dropdown = Select(seat)
                seat_type_dropdown.select_by_value(SEAT_MAP.get(seat_type))
        _time_print("成功选择席别")

    def _ensure_seat_position(self) -> None:
        self._driver.find_element(value="submitOrder_id").click()
        time.sleep(self.MIDDLE_INTERVAL)
        WebDriverWait(timeout=self.TIME_OUT, driver=self._driver).until(
            ec.presence_of_all_elements_located((By.ID, "qr_submit_id")))
        _time_print("开始选座")
        if self._driver.find_element(by=By.XPATH, value="//*[@id='sy_ticket_num_id']/strong").text.strip() == '0':
            self._driver.find_element(value="qr_submit_id").click()
        else:
            is_allowed_empty_seat = int(self._conf.get("no_seat_allow", '1')) == 1
            if is_allowed_empty_seat:
                self._driver.find_element(value="back_edit_id").click()
            else:
                self._driver.find_element(value="qr_submit_id").click()
        _time_print("成功选座")

    def _ensure(self) -> None:
        self._ensure_passengers()
        self._ensure_ticket_type()
        self._ensure_seat_type()
        self._ensure_seat_position()

    def run(self) -> None:
        """
        如果最终没有到达支付页面，循环执行订票操作，直到订票成功为止
        :return:
        """
        self._login()
        while True:
            try:
                self._choose()
                self._ensure()
                if self._driver.current_url.startswith(self._conf.get("pay_url")):
                    break
            except Exception as _:
                time.sleep(self.BIG_INTERVAL)
        _time_print(f"订票成功，请在10分钟之内支付车票费用，支付网址：{self._conf.get('pay_url')}")
