import re
import time
from datetime import datetime

from dateutil.parser import parse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

from core.base_processor import BaseProcessor
from utils.common import _time_print, TIME_FORMAT
from .constants import TRAIN_TYPE_MAP, TICKET_MAP, SEAT_MAP, TIME_RANGE_MAP


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



    def _login(self) -> None:
        _time_print("开始登录")
        self._driver.get(self._conf.get('login_url'))
        # 填写账号和密码
        WebDriverWait(timeout=self.TIME_OUT, driver=self._driver).until(
            ec.presence_of_all_elements_located((By.ID, "J-userName")))
        self._driver.find_element(value="J-userName").send_keys(self._conf.get("username"))
        self._driver.find_element(value="J-password").send_keys(self._conf.get("password"))
        # 点击登录
        self._driver.find_element(value="J-login").click()

        try:
            # 如果隐藏了浏览器则不处理不用用户自己输入, 身份验证信息需要在终端填写
            # 填入身份证后四位
            time.sleep(self.MIDDLE_INTERVAL)
            id_card_input = self._driver.find_element(value="id_card")
            id_card_input.clear()
            id_card_last_four_number = self._conf.get("id_card_last_four_number")
            if not id_card_last_four_number:
                id_card_last_four_number = input("请输入身份证后4位：")
            id_card_input.send_keys(id_card_last_four_number)
            self._driver.find_element(value="verification_code").click()
            verification_code = input("请输入验证码：")
            code_input = self._driver.find_element(value="code")
            code_input.clear()
            code_input.send_keys(verification_code)
            self._driver.find_element(value="sureClick").click()
        except (NoSuchElementException, ElementNotInteractableException) as _:
            # 代表此时不需要输入验证码
            pass
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
        start_date_input.send_keys(self._conf.get("start_date", datetime.now().strftime(TIME_FORMAT)))

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
        def _select_time() -> None:
            # 选择列出出发时间点
            start_time_range = self._conf.get("start_time_range", "00:00--24:00")
            if start_time_range:
                ranges = self._driver.find_elements(value="cc_start_time")
                for range_ in ranges:
                    range_dropdown = Select(range_)
                    range_dropdown.select_by_value(TIME_RANGE_MAP.get(start_time_range))

        _select_time()
        wait_times = 0
        # 等待1.2亿次大概需要1分钟
        one_minute_times = 120000000
        fetch_start_time = self._conf.get("fetch_start_time")
        if fetch_start_time:
            fetch_start_time = parse(fetch_start_time)
            if datetime.now() < fetch_start_time:
                _time_print(f"将在{fetch_start_time.strftime(TIME_FORMAT)}开启预订余票")
            while datetime.now() < fetch_start_time:
                wait_times += 1
                # 每三分钟刷新一次页面，防止跳转到登录页面
                if wait_times % (one_minute_times * 3) == 0:
                    self._driver.refresh()
                    self._pre_start()
                    _select_time()
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
        _time_print("开始选择乘客")
        passenger_labels = self._driver.find_elements(by=By.XPATH, value=self.PASSENGER_PATTERN)
        select_passengers = re.split(self.SEP_PATTERN, self._conf.get("users"))
        for passenger_label in passenger_labels:
            if any(passenger_label.text.startswith(p) for p in select_passengers):
                passenger_label.click()
                retry_times = 0
                # 学生票需要点击确认按钮
                while self._conf.get("ticket_type", "成人票") == "学生票":
                    try:
                        confirm_student = ec.visibility_of_element_located((By.ID, "dialog_xsertcj_ok"))
                        if confirm_student(self._driver):
                            confirm_student(self._driver).click()
                        break
                    except NoSuchElementException as _:
                        if retry_times > 100:
                            break
                        retry_times += 1
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

        def _click_confirm_button() -> None:
            while True:
                try:
                    self._driver.find_element(value="qr_submit_id").click()
                    if self._driver.current_url != self._conf.get('buy_url'):
                        break
                except Exception as _:
                    if self._driver.current_url.startswith(self._conf.get('pay_url')):
                        break

        self._driver.find_element(value="submitOrder_id").click()
        WebDriverWait(timeout=self.TIME_OUT, driver=self._driver).until(
            ec.element_to_be_clickable((By.ID, "qr_submit_id")))
        _time_print("开始选座")
        if self._driver.find_element(by=By.XPATH, value="//*[@id='sy_ticket_num_id']/strong").text.strip() == '0':
            _click_confirm_button()
        else:
            is_allowed_empty_seat = int(self._conf.get("no_seat_allow", '1')) == 1
            if is_allowed_empty_seat:
                self._driver.find_element(value="back_edit_id").click()
            else:
                _click_confirm_button()
        _time_print("成功选座")
        time.sleep(self.BIG_INTERVAL)

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
                _time_print(str(_))
                time.sleep(self.BIG_INTERVAL)
        _time_print(f"订票成功，请在10分钟之内支付车票费用，支付网址：{self._conf.get('pay_url')}")
