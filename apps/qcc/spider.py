import re
import time
import secrets
from typing import Dict
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from core.base_processor import BaseProcessor
from utils.common import time_print, BASE_DIR, engine


class QCC(BaseProcessor):

    def __init__(self):
        super().__init__()
        self._login_url = "https://www.qcc.com/"

    def _read_config(self, config_file_path: str = str(Path(BASE_DIR) / "configs" / "qcc.ini")) -> Dict[str, str]:
        return super()._read_config(config_file_path)

    def _login(self) -> None:
        self._driver.get(self._login_url)
        self._driver.find_element(by=By.XPATH, value="//a[@class='navi-btn login-nav-btn']").click()
        time.sleep(1)
        self._driver.find_element(by=By.XPATH, value="//div[@class='login-change']").click()
        time.sleep(1)
        elements = self._driver.find_elements(by=By.XPATH, value="//div[@class='login-tab']")
        for element in elements:
            if element.text == '密码登录':
                element.click()
                break
        time.sleep(1)
        self._driver.find_element(
            by=By.XPATH,
            value="//div[@class='password-login_wrapper']//input[@class='form-control']"
        ).send_keys(self._conf.get('login.username'))
        self._driver.find_element(
            by=By.XPATH,
            value="//div[@class='password-login_wrapper']//input[@class='form-control password-input']"
        ).send_keys(self._conf.get('login.password'))
        self._driver.find_element(
            by=By.XPATH,
            value="//div[@class='password-login_wrapper']//button[@class='btn btn-primary login-btn']"
        ).click()
        while True:
            try:
                if self._driver.find_element(by=By.ID, value='loginModal'):
                    continue
            except NoSuchElementException as _:
                break
        time_print("登录完毕")

    def _crawl_then_save(self) -> None:
        df_enterprise_names = pd.read_sql("SELECT DISTINCT enterprise_name FROM t_company", con=engine)
        enterprise_names = df_enterprise_names.enterprise_name.values.tolist()
        df_exists_enterprise_names = pd.read_sql(
            "SELECT DISTINCT enterprise_name FROM t_qcc_company",
            con=engine,
            columns=['columns']
        )
        exists_enterprise_names = [item.split('\n')[0] for item in df_exists_enterprise_names.enterprise_name.to_list()]
        enterprise_names = sorted(set(enterprise_names).difference(exists_enterprise_names))
        sep = '：'
        for enterprise_name in enterprise_names:
            time.sleep(secrets.choice(range(5, 10)))
            while True:
                try:
                    time_print(f"开始爬取{enterprise_name}的数据")
                    # 放到里面是为了动态的添加列
                    df_comment = pd.read_sql(
                        "SELECT COLUMN_NAME, COLUMN_COMMENT FROM information_schema.COLUMNS WHERE TABLE_NAME = 't_qcc_company' AND COLUMN_NAME != 'id'",
                        con=engine
                    )
                    comment_map = dict(zip(df_comment['COLUMN_COMMENT'], df_comment['COLUMN_NAME']))
                    value = dict()
                    # 1. 爬取基本信息
                    url = urljoin(self._login_url, f"web/search?key={enterprise_name}")
                    self._driver.get(url)

                    detail_url = self._driver.find_element(
                        by=By.XPATH, value="//span[@class='copy-title']/a").get_attribute('href')
                    self._driver.get(detail_url)
                    elements = self._driver.find_elements(
                        by=By.XPATH,
                        value="//div[@class='main-part']//div[@class='rline']//span"
                    )
                    for index, el in enumerate(elements):
                        text = el.text
                        if sep in text:
                            comment, val = text.replace('\n', '').split(sep)
                            val = val.strip()
                            if not val:
                                continue
                            val = val.split(' ')[0]
                            # 电话和邮箱数据需要清洗
                            if comment in ('电话', '邮箱'):
                                matched = re.match('^[\d\.\@a-z]+', val)
                                val = matched.group() if matched is not None else val
                            value.__setitem__(comment, val)
                    person_in_legal = value.get('法定代表人')
                    # 2. 爬取工商信息
                    elements = self._driver.find_elements(
                        By.XPATH, "//section[@id='cominfo']//table[@class='ntable']//td")
                    start = 0
                    while start < len(elements):
                        if elements[start].get_attribute('class') == 'tb':
                            value.__setitem__(elements[start].text.strip(), elements[start + 1].text.strip())
                            start += 1
                        start += 1
                    value.__setitem__('法定代表人', person_in_legal)
                    df_to_db = pd.DataFrame([value]).rename(columns=comment_map).fillna('')
                    df_to_db.to_sql(name='t_qcc_company', con=engine, if_exists='append', index=False)
                    time_print(f"成功爬取{enterprise_name}的数据")
                    break
                except Exception as _:
                    print(_.args)
                    time_print("爬虫被封，稍等...")
                    time.sleep(10)
                    continue

    def run(self) -> None:
        self._login()
        self._crawl_then_save()


if __name__ == '__main__':
    qcc = QCC()
    qcc.run()
