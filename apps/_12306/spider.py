import re
import time
from typing import Dict
from pathlib import Path
from datetime import datetime
from itertools import zip_longest

from dateutil.parser import parse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, \
    StaleElementReferenceException

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

    def __init__(self, stealth_file_name: str = 'stealth.min.js', set_proxy: bool = False):
        super().__init__(stealth_file_name, set_proxy)
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


    def _login_by_qrcode(self) -> None:
        time_print("开始登录")
        cookies_dir = Path(BASE_DIR) / 'apps' / '_12306' / 'preserve'
        cookies_dir.mkdir(exist_ok=True)
        cookies_file_path = cookies_dir / 'cookies.json'
        self._driver.get(self._conf.get('url_info.init_url'))
        if cookies_file_path.exists():
            self.add_cookies(str(cookies_file_path))
        self._driver.get(self._conf.get('url_info.init_url'))
        if not self._driver.current_url.startswith(self._conf.get('url_info.init_url')):
            self._driver.delete_all_cookies()
            self._driver.find_element(by=By.XPATH, value='//a[text()="扫码登录"]').click()
            # 等待访问网页是否加载
            WebDriverWait(timeout=self.TIME_OUT, driver=self._driver).until(
                ec.url_to_be(self._conf.get("url_info.init_url")))
            cookies = self._driver.get_cookies()
            for cookie in cookies:
                # 修改domain防止再次登录的时候报错
                cookie.__setitem__('domain', '.12306.cn')
                cookie.pop('sameSite', self.EMPTY)
            self.save_cookies(cookies, str(cookies_file_path))
        time_print("登录成功")

    def _login(self) -> None:
        time_print("开始登录")
        cookies_dir = Path(BASE_DIR) / 'apps' / '_12306' / 'preserve'
        cookies_dir.mkdir(exist_ok=True)
        cookies_file_path = cookies_dir / 'cookies.json'
        self._driver.get(self._conf.get('url_info.init_url'))
        if cookies_file_path.exists():
            self.add_cookies(str(cookies_file_path))
        self._driver.get(self._conf.get('url_info.init_url'))
        if not self._driver.current_url.startswith(self._conf.get('url_info.init_url')):
            self._driver.delete_all_cookies()
            # 填写账号和密码
            WebDriverWait(timeout=self.TIME_OUT, driver=self._driver).until(
                ec.presence_of_all_elements_located((By.ID, "J-userName")))
            self._driver.find_element(value="J-userName").send_keys(self._conf.get("login.username"))
            self._driver.find_element(value="J-password").send_keys(self._conf.get("login.password"))
            # 点击登录
            while True:
                try:
                    self._driver.find_element(value="J-login").click()
                    break
                except Exception as _:
                    continue
            try:
                # 如果隐藏了浏览器则不处理不用用户自己输入, 身份验证信息需要在终端填写
                # 填入身份证后四位
                time.sleep(self.MIDDLE_INTERVAL * 2)
                id_card_input = self._driver.find_element(value="id_card")
                id_card_input.clear()
                id_card_last_four_number = self._conf.get("login.id_card_last_four_number")
                if not id_card_last_four_number:
                    id_card_last_four_number = input("请输入身份证后4位：").strip()
                id_card_input.send_keys(id_card_last_four_number)
                self._driver.find_element(value="verification_code").click()
                verification_code = input("请输入验证码：").strip()
                code_input = self._driver.find_element(value="code")
                code_input.clear()
                code_input.send_keys(verification_code)
                self._driver.find_element(value="sureClick").click()
            except (NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException) as _:
                # 代表此时不需要输入验证码
                time_print("报错了(请自行输入证件号和验证码):" + str(_))
            # 等待访问网页是否加载
            WebDriverWait(timeout=self.TIME_OUT, driver=self._driver).until(
                ec.url_to_be(self._conf.get("url_info.init_url")))
            cookies = self._driver.get_cookies()
            for cookie in cookies:
                # 修改domain防止再次登录的时候报错
                cookie.__setitem__('domain', '.12306.cn')
                cookie.pop('sameSite', self.EMPTY)
            self.save_cookies(cookies, str(cookies_file_path))
        time_print("登录成功")

    def _pre_start(self) -> None:
        """
        添加起止时间和地址
        :return:
        """
        for des in ("from", "to"):
            el = self._driver.find_element(value=f"{des}StationText")
            el.click()
            el.send_keys(self._conf.get(f"cookie_info.{des}"))
            self._driver.find_element(by=By.XPATH, value="//div[@id='panel_cities']/div/span[text()='{place}']".format(
                place=self._conf.get(f"cookie_info.{des}"))).click()
        start_date_input = self._driver.find_element(value="train_date")
        start_date_input.clear()
        start_date_input.send_keys(self._conf.get("cookie_info.start_date", datetime.now().strftime(TIME_FORMAT)))

    def _search(self) -> None:
        for train_type in re.split(self.SEP_PATTERN, self._conf.get("train_info.train_types", DEFAULT_VALUE)):
            train_type = train_type.strip()
            if train_type not in TRAIN_TYPE_MAP:
                time_print(f"车次类型异常或未选择!(train_type={train_type})")
                continue
            el = self._driver.find_element(
                by=By.XPATH,
                value=f"//label[text()='{TRAIN_TYPE_MAP.get(train_type)}']/../input")
            if not el.is_selected():
                el.click()

        if self._conf.get("cookie_info.start_date"):
            self._driver.find_element(value="query_ticket").click()
            time.sleep(self.MIDDLE_INTERVAL)
            # 等待车次列表是否加载进来
            WebDriverWait(timeout=self.TIME_OUT, driver=self._driver).until(
                ec.presence_of_all_elements_located((By.XPATH, "//tbody[@id='queryLeftTable']/tr")))
        else:
            time_print("未指定发车时间, 默认00:00-24:00")

    def _pre_book(self, order: int = 0) -> None:
        def _select_time() -> None:
            # 选择列出出发时间点
            start_time_range = self._conf.get("train_info.start_time_range")
            if start_time_range:
                ranges = self._driver.find_elements(value="cc_start_time")
                for range_ in ranges:
                    range_dropdown = Select(range_)
                    range_dropdown.select_by_value(TIME_RANGE_MAP.get(start_time_range))

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
                    self._driver.refresh()
                    self._pre_start()
                    _select_time()
        cnt = 0
        train_string =  self._conf.get("train_info.train_nos", DEFAULT_VALUE)
        train_nos = re.split(self.SEP_PATTERN, train_string) if train_string else list()
        while self._driver.current_url == self._conf.get("url_info.ticket_url"):
            self._search()
            cnt += 1
            time_print(f"持续抢票...第{cnt}次")
            try:
                book_items = self._driver.find_elements(by=By.XPATH, value="//a[text()='预订'] | //td[text()='预订']")
                if train_nos:
                    train_text = self._driver.find_elements(
                        by=By.XPATH,
                        value="//a[@title='点击查看停靠站信息']"
                    )
                    book_items = [
                        book_item for train, book_item in zip(train_text, book_items) if train.text in train_nos]
                if order > 0:
                    book_items[order - 1].click()
                    time.sleep(self.MIDDLE_INTERVAL)
                else:
                    for book_item in book_items:
                        try:
                            book_item.click()
                            time.sleep(self.MIDDLE_INTERVAL)
                        except Exception as _:
                            pass
            except Exception as _:
                time_print("还没开始预订")
                continue

    def _choose(self) -> None:
        time_print("开始预订票")
        self._driver.get(self._conf.get("url_info.ticket_url"))
        self._pre_start()
        self._pre_book(int(self._conf.get('order_item.order')))
        time_print("成功选择订票车次")


    def _select_by_name(self, xpath: str, name: str, map_relation: Dict[str, str]) -> bool:
        select_ = Select(self._driver.find_element(by=By.XPATH, value=xpath))
        for option in select_.options:
            if option.text.startswith(name):
                select_.select_by_value(map_relation.get(name))
                return True
        return False


    def _ensure_passengers_and_ticket_type_and_seat_type(self) -> None:
        time_print("开始选择乘客")
        passenger_labels = self._driver.find_elements(by=By.XPATH, value=self.PASSENGER_PATTERN)
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
                            confirm_student = ec.visibility_of_element_located((By.ID, "dialog_xsertcj_ok"))
                            if confirm_student(self._driver):
                                confirm_student(self._driver).click()
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
                    self._driver.find_element(value="qr_submit_id").click()
                    if self._driver.current_url != self._conf.get('url_info.buy_url'):
                        break
                except Exception as _:
                    if self._driver.current_url.startswith(self._conf.get('url_info.pay_url')):
                        break
                if time.perf_counter() - start > self.TIME_OUT:
                    time_print("抢票过程中出现异常, 马上开始重新抢票")
                    RuntimeError("抢票过程中出现异常, 马上开始重新抢票")

        self._driver.find_element(value="submitOrder_id").click()
        WebDriverWait(timeout=self.BIG_INTERVAL, driver=self._driver).until(
            ec.element_to_be_clickable((By.ID, "qr_submit_id")), message="没有票了")
        time_print("开始选座")
        if self._driver.find_element(by=By.XPATH, value="//*[@id='sy_ticket_num_id']/strong").text.strip() != '0':
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

    def run(self, debug: bool = False) -> None:
        """
        如果最终没有到达支付页面，循环执行订票操作，直到订票成功为止
        :return:
        """
        # self._login()
        self._login_by_qrcode()
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
