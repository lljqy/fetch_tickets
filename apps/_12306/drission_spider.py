import re
import time
from typing import Dict
from pathlib import Path
from datetime import datetime
from itertools import zip_longest

from DrissionPage import ChromiumPage
from DrissionPage.errors import ElementNotFoundError, ElementLostError

from dateutil.parser import parse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException

from utils.exceptions import ConfigError
from core.base_processor import BaseProcessor
from utils.common import time_print, TIME_FORMAT, BASE_DIR
from .constants import TRAIN_TYPE_MAP, TICKET_MAP, SEAT_MAP, TIME_RANGE_MAP, DEFAULTS_CONF, REQUIRES, DEFAULT_VALUE


class TicketProcessor(BaseProcessor):
    """
    处理流程：
        1. 读取配置文件, 设置关键参数
        2. 进入登录页面（需要验证码登录），登录成功
        3. 进入火车票预订页面，选择火车信息
        4. 选择乘车人，确认订单
        5. 乘车人付款
    """
    APP_NAME = "12306"
    PASSENGER_PATTERN = "//ul[@id='normal_passenger_id']/li/label"

    def __init__(self):
        self._page = ChromiumPage()
        self._conf = self._read_config()
        self._cookies = dict()

    def _set_cookies(self) -> None:
        for elem in self._driver.get_cookies():
            self._cookies.__setitem__(elem['name'], elem['value'])

    def _read_config(self, config_file_path: str = str(Path(BASE_DIR) / "configs" / "12306.ini")) -> Dict[str, str]:
        conf = super()._read_config(config_file_path)
        for name, default_value in DEFAULTS_CONF.items():
            value = conf.get(name) or default_value
            if not value and name in REQUIRES:
                _, s = name.split('.')
                raise ConfigError(f"必须设置`{s}`的值")
            if value:
                conf.__setitem__(name, value)
        return conf

    def _login(self) -> None:
        time_print("开始登录")
        cookies_dir = Path(BASE_DIR) / 'apps' / '_12306' / 'preserve'
        cookies_dir.mkdir(exist_ok=True)
        cookies_file_path = cookies_dir / 'cookies.json'
        self._page.get(self._conf.get('url_info.init_url'))
        if cookies_file_path.exists():
            self._page.set.cookies.clear()
            self.add_cookies(str(cookies_file_path))
        self._page.get(self._conf.get('url_info.init_url'))
        if not self._page.url.startswith(self._conf.get('url_info.init_url')):
            # 填写账号和密码
            self._page.ele("#J-userName", timeout=self.TIME_OUT).input(self._conf.get("login.username"))
            self._page.ele("#J-password", timeout=self.TIME_OUT).input(self._conf.get("login.password"))
            # 点击登录
            while True:
                try:
                    self._page.ele("#J-login", timeout=self.TIME_OUT).click()
                    break
                except Exception as _:
                    continue
            try:
                # 如果隐藏了浏览器则不处理不用用户自己输入, 身份验证信息需要在终端填写
                # 填入身份证后四位
                id_card_input = self._page.ele("#id_card", timeout=self.TIME_OUT)
                id_card_input.clear()
                id_card_last_four_number = self._conf.get("login.id_card_last_four_number")
                if not id_card_last_four_number:
                    id_card_last_four_number = input("请输入身份证后4位：").strip()
                id_card_input.input(id_card_last_four_number)
                self._page.ele("#verification_code", timeout=self.TIME_OUT).click()
                verification_code = input("请输入验证码：").strip()
                code_input = self._page.ele("#code", timeout=self.TIME_OUT)
                code_input.clear()
                code_input.input(verification_code)
                self._page.ele("#sureClick", timeout=self.TIME_OUT).click()
            except (ElementNotFoundError, ElementLostError) as _:
                # 代表此时不需要输入验证码
                time_print("报错了(请自行输入证件号和验证码):" + str(_))
            cookies = self._page.cookies()
            # for cookie in cookies:
            #     # 修改domain防止再次登录的时候报错
            #     cookie.__setitem__('domain', '.12306.cn')
            #     cookie.pop('sameSite', self.EMPTY)
            # self.save_cookies(cookies, str(cookies_file_path))
        self._page.wait.url_change(self._conf.get('url_info.init_url'))
        time_print("登录成功")

    def _pre_start(self) -> None:
        """
        添加起止时间和地址
        :return:
        """
        for des in ("from", "to"):
            el = self._page.ele(f"#{des}StationText")
            el.click()
            el.input(vals=self._conf.get(f"cookie_info.{des}"), clear=True, by_js=True)
            # self._page.ele(("xpath", "//div[@id='panel_cities']/div/span[text()='{place}']".format(
            #     place=self._conf.get(f"cookie_info.{des}")))).click()
        start_date_input = self._page.ele("#train_date")
        start_date_input.clear()
        start_date_input.input(self._conf.get("cookie_info.start_date", datetime.now().strftime(TIME_FORMAT)))

    def _search(self) -> None:
        for train_type in re.split(self.SEP_PATTERN, self._conf.get("train_info.train_types", DEFAULT_VALUE)):
            train_type = train_type.strip()
            if train_type not in TRAIN_TYPE_MAP:
                time_print(f"车次类型异常或未选择!(train_type={train_type})")
                continue
            el = self._page.ele(("xpath", f"//label[text()='{TRAIN_TYPE_MAP.get(train_type)}']/../input"))
            if not el.states.is_selected:
                el.click()

        if self._conf.get("cookie_info.start_date"):
            self._page.ele("#query_ticket").click()
            self._page.wait.ele_displayed(("xpath", "//tbody[@id='queryLeftTable']/tr"))
        else:
            time_print("未指定发车时间, 默认00:00-24:00")

    def _pre_book(self, order: int = 0) -> None:
        def _select_time() -> None:
            # 选择列出出发时间点
            start_time_range = self._conf.get("train_info.start_time_range")
            if start_time_range:
                ranges = self._page.ele("#cc_start_time")
                ranges.select.by_value(TIME_RANGE_MAP.get(start_time_range))

        _select_time()
        wait_times = 0
        # 等待1.2亿次大概需要1分钟
        one_minute_times = 120000000
        fetch_start_time = self._conf.get("scheduler.fetch_start_time")
        if fetch_start_time:
            fetch_start_time = parse(fetch_start_time)
            if datetime.now() < fetch_start_time:
                time_print(f"将在{fetch_start_time.strftime(TIME_FORMAT)}开启预订余票")
            while datetime.now() < fetch_start_time:
                wait_times += 1
                # 每三分钟刷新一次页面，防止跳转到登录页面
                if wait_times % (one_minute_times * 3) == 0:
                    self._page.refresh()
                    self._pre_start()
                    _select_time()
        cnt = 0
        while self._page.url == self._conf.get("url_info.ticket_url"):
            self._search()
            cnt += 1
            time_print(f"持续抢票...第{cnt}次")
            try:
                book_items = self._page.eles(("xpath", "//a[text()='预订']"))
                if order > 0:
                    book_items[order - 1].click()
                else:
                    for book_item in book_items:
                        try:
                            book_item.click()
                        except Exception as _:
                            pass
            except Exception as _:
                time_print("还没开始预订")
                continue
        self._page.wait.url_change(self._conf.get("url_info.buy_url"))

    def _choose(self) -> None:
        time_print("开始预订票")
        self._page.get(self._conf.get("url_info.ticket_url"))
        self._pre_start()
        self._pre_book(int(self._conf.get('order_item.order')))
        time_print("成功选择订票车次")

    def _select_by_name(self, xpath: str, name: str, map_relation: Dict[str, str]) -> bool:
        select_ = self._page.ele(("xpath", xpath)).select
        for option in select_.options:
            if option.text.startswith(name):
                select_.by_value(map_relation.get(name))
                return True
        return False

    def _ensure_passengers_and_ticket_type_and_seat_type(self) -> None:
        time_print("开始选择乘客")
        passenger_labels = self._page.s_eles(("xpath", self.PASSENGER_PATTERN))
        select_passengers = re.split(self.SEP_PATTERN, self._conf.get("user_info.users"))
        ticket_types = re.split(self.SEP_PATTERN, self._conf.get("ticket_info.ticket_type"))
        seat_types = re.split(self.SEP_PATTERN, self._conf.get("confirm_info.seat_type"))
        student_suffix = "(学生)"
        for index, (passenger_name, ticket_type, seat_type) in enumerate(
                zip_longest(select_passengers, ticket_types, seat_types), start=1):
            if not passenger_name:
                continue
            ticket_type = ticket_type if ticket_type else "成人票"
            for passenger_label in passenger_labels:
                select_passenger_name = passenger_label.text
                if select_passenger_name.endswith(student_suffix):
                    select_passenger_name = select_passenger_name.replace(student_suffix, '')
                if select_passenger_name == passenger_name:
                    passenger_label.click()
                    # 消除系统弹出来的学生框模态
                    retry_times = 0
                    while retry_times <= 1000 and passenger_label.text.endswith(student_suffix):
                        try:
                            self._page.wait.ele_displayed("#dialog_xsertcj_ok", timeout=self.MIDDLE_INTERVAL)
                            self._page.ele("#dialog_xsertcj_ok").click()
                            break
                        except NoSuchElementException as _:
                            retry_times += 1
                    # 选择票种
                    self._select_by_name(f"//select[@id='ticketType_{index}']", ticket_type, TICKET_MAP)
                    # 选择系别
                    if seat_type:
                        self._select_by_name(f"//select[@id='seatType_{index}']", seat_type, SEAT_MAP)
                    break
        # 判断手机号绑定验证“qd_closeDefaultWarningWindowDialog_id”
        self.compatible(By.ID, "qd_closeDefaultWarningWindowDialog_id")
        time_print("成功选择乘客")

    def _ensure_seat_position(self) -> None:

        def _click_confirm_button() -> None:
            start = time.perf_counter()
            while True:
                try:
                    self._page.ele("#qr_submit_id").click()
                    if self._page.url != self._conf.get('url_info.buy_url'):
                        break
                except NoSuchElementException as _:
                    if self._page.url.startswith(self._conf.get('url_info.pay_url')):
                        break
                if time.perf_counter() - start > self.TIME_OUT:
                    time_print("抢票过程中出现异常, 马上开始重新抢票")
                    RuntimeError("抢票过程中出现异常, 马上开始重新抢票")

        self._page.ele("#submitOrder_id", timeout=self.BIG_INTERVAL).click()
        time_print("开始选座")
        if self._page.ele(("xpath", "//*[@id='sy_ticket_num_id']/strong")).text.strip() != '0':
            _click_confirm_button()
        else:
            is_allowed_empty_seat = int(self._conf.get("confirm_info.no_seat_allow")) == 1
            if is_allowed_empty_seat:
                _click_confirm_button()
            else:
                time_print("没有座位啦, 只剩下无座, 稍等片刻...")
                RuntimeError("没有座位啦, 只剩下无座, 稍等片刻...")
        time_print("成功选座")
        time.sleep(self.BIG_INTERVAL)

    def _ensure(self) -> None:
        self._ensure_passengers_and_ticket_type_and_seat_type()
        self._ensure_seat_position()
        self._page.wait.url_change(self._conf.get("url_info.pay_url"), timeout=self.BIG_INTERVAL)

    def compatible(self, by=By.ID, value: str = '') -> bool:
        """
        有些元素可能出现了，也有可能没有出现，兼容处理
        :param by:
        :param value:
        :return:
        """
        self._page.wait.ele_displayed((by, value), timeout=self.MIDDLE_INTERVAL)
        self._page.ele((by, value)).click()
        try:
            self._page.ele((by, value)).click()
            return True
        except NoSuchElementException as _:
            pass
        return False

    def add_cookies(self, path: str) -> None:
        cookies = self.load_cookies(path)
        self._page.set.cookies(cookies)

    def run(self, debug: bool = False) -> None:
        """
        如果最终没有到达支付页面，循环执行订票操作，直到订票成功为止
        :return:
        """
        self._login()
        if debug:
            self._choose()
            self._ensure()
        else:
            while True:
                try:
                    self._choose()
                    self._ensure()
                    if self._driver.current_url.startswith(self._conf.get("url_info.pay_url")):
                        break
                except Exception as _:
                    time_print(str(_))
                    time.sleep(self.BIG_INTERVAL)
        time_print(f"订票成功，请在10分钟之内支付车票费用，支付网址：{self._conf.get('url_info.pay_url')}")
