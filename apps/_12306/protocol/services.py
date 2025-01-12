import base64
import urllib3
from urllib.parse import urlencode

from requests import utils as request_utils

from . import constants
from .util import Session, Encrypt
from apps._12306.constants import SITE_MAP

urllib3.disable_warnings()

OTN = "otn"
UUID = "uuid"
APPID = "appid"
REFER = "Refer"
UAMTK = "uamtk"
JSON_ATTR = "_json_att"
USERNAME = "username"
USE_AGENT = "User-Agent"
RESULT_MESSAGE = "result_message"

session = Session()
encrypt = Encrypt()


def _fill_cookie() -> None:
    # cookie_map = {
    #     "_uab_collina": "173177021080196427966096",
    #     "_jc_save_wfdc_flag": "dc",
    #     "guidesStatus": "off",
    #     "highContrastMode": "defaltMode",
    #     "cursorStatus": "off",
    # }
    # for k, v in cookie_map.items():
    #     request_utils.add_dict_to_cookiejar(session.cookies, cookie_dict={k: v})
    pass


class LoginAPI:

    @staticmethod
    def is_cookie_alive(headers: dict[str, str]) -> bool:
        response = session.post(
            url=constants.PASSPORT_AUTH_UAMTK_URL,
            headers={**headers, REFER: constants.LOGIN_PAGE_URL},
            data={APPID: OTN}
        )
        return response.json().get(RESULT_MESSAGE) == "验证通过"

    @staticmethod
    def check_login_verify(user_name: str, headers: dict[str, str]) -> dict[str, str]:
        """
        :param user_name: 用户名
        :param headers: 请求头信息
        :return:
        """
        data = {APPID: OTN, USERNAME: user_name}
        response = session.post(
            url=constants.CHECK_LOGIN_VERIFY_URL, headers={**headers, REFER: constants.LOGIN_PAGE_URL}, data=data)
        return response.json()

    @staticmethod
    def get_sms_code(user_name: str, cast_num: str, headers: dict[str, str]) -> str:
        """
        :param user_name: 用户名
        :param cast_num:  身份证后四位
        :param headers: 请求头信息
        :return:
        """
        data = {
            APPID: OTN,
            USERNAME: user_name,
            "castNum": cast_num
        }
        session.post(url=constants.MESSAGE_CODE_URL, headers={**headers, REFER: constants.LOGIN_PAGE_URL}, data=data)
        sms_code = input("请输入手机验证码")
        return sms_code

    @staticmethod
    def web_login(user_name: str, password: str, sms_code: str, headers: dict[str, str]) -> dict[str, str]:
        data = {
            'sessionId': '',
            'sig': '',
            'if_check_slide_passcode_token': '',
            'scene': '',
            'checkMode': '0',
            'randCode': sms_code,
            'username': user_name,
            'password': encrypt.encrypt_password(password),
            'appid': 'otn',
        }
        session.headers.update({USE_AGENT: headers.get(USE_AGENT)})
        response = session.post(
            constants.PASSPORT_LOGIN_URL, headers={**headers, REFER: constants.LOGIN_PAGE_URL}, data=data)
        results = response.json()
        request_utils.add_dict_to_cookiejar(session.cookies, cookie_dict={UAMTK: results.get(UAMTK)})
        _fill_cookie()
        return results

    @staticmethod
    def otn_user_login(headers: dict[str, str]) -> None:
        session.get(constants.USER_LOGIN_URL, headers={**headers, REFER: constants.LOGIN_PAGE_URL})

    @staticmethod
    def otn_redirect_login(headers: dict[str, str]) -> None:
        session.get(constants.OTN_PASSPORT_REDIRECT_URL, headers={**headers, REFER: constants.LOGIN_PAGE_URL})

    @staticmethod
    def auth_uamtk(headers: dict[str, str]) -> dict[str, str]:
        """
        :param headers:
        :return:
            {
                "apptk": null,
                "result_message": "验证通过",
                "result_code": 0,
                "newapptk": "lQQXuLoEQUPh6x0t951-6-vKZiMn7feE5oa6WQkol1l0"
            }
        """
        response = session.post(
            constants.PASSPORT_AUTH_UAMTK_URL,
            headers={**headers, REFER: constants.REDIRECT_LOGIN_PAGE_URL},
            data={APPID: OTN}
        )
        return response.json()

    @staticmethod
    def uam_auth_client(headers: dict[str, str], tk: str) -> dict:
        """
        :param headers:
        :param tk: auth_uamtk接口中返回的"newapptk"参数
        :return:
            {
                "result_code": 0,
                "result_message": "验证通过",
                "username": "刘伦杰",
                "apptk": "lQQXuLoEQUPh6x0t951-6-vKZiMn7feE5oa6WQkol1l0"
            }
        """
        response = session.post(
            constants.UAM_AUTH_CLIENT_URL,
            headers={**headers, REFER: constants.REDIRECT_LOGIN_PAGE_URL},
            data={"tk": tk}
        )
        return response.json()

    @staticmethod
    def otn_user_login2(headers: dict[str, str]) -> None:
        session.get(constants.USER_LOGIN_URL, headers={**headers, REFER: constants.REDIRECT_LOGIN_PAGE_URL})

    @staticmethod
    def otn_login_conf(headers: dict[str, str]) -> dict:
        """
        :param headers:
        :return:
            {
                "validateMessagesShowId": "_validatorMessage",
                "status": true,
                "httpstatus": 200,
                "data": {
                    "is_open_updateHBTime": "Y",
                    "isstudentDate": false,
                    "is_message_passCode": "N",
                    "born_date": "1992-09-30",
                    "is_phone_check": "N",
                    "ei_email": "78*********52@qq.com",
                    "studentDate": ["2020-04-01", "2020-11-30", "2020-12-01", "2020-12-31", "2021-01-01", "2025-09-30"],
                    "is_uam_login": "Y",
                    "is_login_passCode": "Y",
                    "user_name": "lxpztgllj",
                    "is_sweep_login": "Y",
                    "queryUrl": "leftTicket/queryG",
                    "nowStr": "20241231235059",
                    "psr_qr_code_result": "N",
                    "now": 1735660259739,
                    "yy_open_time": "20250114-20250222",
                    "name": "刘伦杰",
                    "login_url": "resources/login.html",
                    "stu_control": 15,
                    "is_login": "Y",
                    "is_olympicLogin": "N",
                    "yy_ticket_query": "reservationTicket/query",
                    "other_control": 15
                },
                "messages": [],
                "validateMessages": {}
            }
        """
        response = session.post(
            constants.OTN_CONF_URL,
            headers={
                **headers,
                REFER: constants.REDIRECT_LOGIN_PAGE_URL,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        return response.json()

    @staticmethod
    def init_my_12306(headers: dict[str, str]) -> dict:
        """
        :param headers:
        :return:
            {
                "validateMessagesShowId": "_validatorMessage",
                "status": true,
                "httpstatus": 200,
                "data": {
                    "notify_way": "6",
                    "if_show_ali_qr_code": false,
                    "isSuperUser": "N",
                    "_email": "78*****52@qq.com",
                    "user_status": "1",
                    "_is_needModifyPassword": null,
                    "needEdit": false,
                    "member_status": "2",
                    "control_code": null,
                    "id_type_code": "1",
                    "user_name": "刘伦杰",
                    "member_level": "2",
                    "isCanRegistMember": false,
                    "user_regard": "先生,下午好！",
                    "resetMemberPwd": "N",
                    "_is_active": "Y"
                },
                "messages": [],
                "validateMessages": {}
            }
        """
        response = session.post(
            constants.INIT_MY_12306_API_URL,
            headers={
                **headers,
                REFER: constants.INDEX_PAGE_URL,
                "Content-Type": "application/x-www-form-urlencoded",
            })
        return response.json()

    @staticmethod
    def create_qr64(headers: dict[str, str]) -> str:
        """
        :param headers:
        :return:
            {
                "image": "iVBORw0KGgoAAAANSUhEUgAAAMcAAADHCAIAAAAiZ9CRAAAHHElEQVR42u3dS7LbMAxEUe9/084wk6QkoS8gQb4a2n7Wh4cx2GBVPl8PD/r4+Ag8ulR9suPv11358D+u5v+fufQ9Z765dvFn/qp2YbUrpO699hD+dz2qUpWqVLVRFT5UZ96qPbVwyC+pCnXe6+zSW4gEValKVaparar2iGt3S41irby7dxQpnfijS4ZJVapSlap+UBVeiEyu//GHQL3V9+iaHoKqVKUqVf2gKqrI6FvJ98XKtwTx+OioSlWqUpWqatl6OEL4E6FGqO8G+1q/1DS+v2OjKlWpSlUjqnANvrL0lUSCqnxFVb6ySBV1hE3lgTYqVVtQ8QHVGv8+6VCVqlSlqkWqwj5ozRAVXuBj3xepUw3jPnnIpapKVapS1SJVA3UMHuxSDVr8XJOlUnguql9yuVpXlapUparHqMKbndQD7UsN8HNNdoUvnatvql/u2KhKVapS1SpVyT6bb3UXVJhchxut8AIrXK5TBPG06Gy2ripVqUpVD1ZFlQL4h2tl0L31GTUhL5091ED1MFSlKlWpap2qvvZwOIqUqr6CJsyyqfggDCbYToOqVKUqVa1WNblxJ3xYVEmBhyBhYB0WoGHZmkQnqlKVqlS1SBVV/fT9lofLbJwpdRkDjWe8oj0cQVWpSlWqWq0q7ETWipWBzUYDy/5aj/wd5Z2qVKUqVa1TheyqyeuzsHMcFk9UtUENJ17nhec6fxmqUpWqVLVIFbVyxg0hC13wwAs+ql4MmxlsAKQqValKVW9VRRUr+I4ivOgJK63QGe6DeuvwXKpSlapUtVEVtbmHWuhOLsX7erd4u5oK2ZsSHFWpSlWqWqRqoMdJ7a+iLhVvIVMzs6/g6zN9trusKlWpSlXLVU3eEsWL2uHUV2lR/Ql8Z1thJqhKVapS1WpV965v8UC/b9pQyX4Nbt+5kstQlapUpapFqvAmLj6ceOSBd6n7MgL8XN0Fn6pUpSpVLVKFG6r9Od4HDZvcYQjS12loqofK5wKqdVWpSlWqulsVDgUv1Kjqh9pjRC3pww9TjQokAFKVqlSlqo2qwiR9MkDva/2GFVJ377Yjo68NU33PgqpUpSpVPU8VNdKhPPxuKXDPz837Cj6yWleVqlSlqlWqJq+bSrepqi6MTvB6qC9wQaaWqlSlKlUtUlU78aXz9fWA8eX6p3T0laTUM6SOwyFQlapUpaqNqqi9OOHPc1+SjhdqAzulBs7FhheqUpWqVLVRVa2te4sGKizAY/fJchM/V+2fg7PVuqpUpSpVPU9VeLnUcOJt1NpnqDt9rDO8Vj7o2KhKVapS1U5VeOJcSxYoH9R9Ud98bx7RFLurSlWqUtVGVbXSpK9T25cCh2/1zY2BSUI1+A+ydVWpSlWqWqWqr7FKxe54e3ggEaAEh12N2r8ChQeuKlWpSlWLVOFiBsqpcCbgaUgfi7CUxAkeXqqqVKUqVS1SFRY9ocVwUV1bgVMIwgqyb4Dx/J2s1lWlKlWpaoMqakkfZtB9ATFV+eG5eV9YT81DMltXlapUpaqbVPVFz3hzGq/PJidAX7mJ31dCWVWqUpWqNqqirjtMrvFIvdaBxjvZ1MPsq72QcEdVqlKVqhaposLxeyPjvu4yVXdSNWVfaYtkOqpSlapUtUhVX7UxUP0MBPp4DEF1hcMJ2TS4qlKVqlS1URX+e4+sVL+P+c+l8Jx6MlkIK9rzT0NVqlKVqhapooa8rx3bF3zjcXm4kh9IwLuZqkpVqlLValXhz/zkEhrvsD4/f6dup2nSqkpVqlLVRlXUMOA1Ex464N+DB+hUgYWf/fAGVaUqVanqZapql0JVJH0pOf5X4cPEy7La6CSdBlWpSlWqWqSKSgSoCgmvh6hXKGdUSj45e1WlKlWp6pWqajl1XzMY70nXgonJvUrUZKOOhLKqVKUqVW1UNXlLVHaM1zrUMFCpAdVg6MOtKlWpSlUvUBUGsngZhIOjOgRhRtBXjVF96+QuVKUqVanq9arCgBjvUuNzI4y5wybuZIXEnl1VqlKVqhaposLovhZyH9PJQi20GNZnYwWfqlSlKlUtUoVvwaEWsVSyH/YD8IRiIKah5nMBt6pUpSpVLVKF//CHBQ1e2eBMw+Z03/TDu+aFh6AqValKVRtVhUdNzC27oMLedl/gcu9byJiqSlWqUtUiVcivKRh81yjXcoSB+J4qsKhWQfduAFWpSlWq2qgqrKLC2gJvkYbJQthOCDMUvP8dUj7/56pSlapUtVoVNZxUs7MvlaaydbyC7Mvowxb74SuqUpWqVPWDqsJQm9o7ReURYY5AtYfDL6S2Dlx4tqpSlapU9cOqwnGtNZVrGQGeoVBhQUgHz+jPf6GqVKUqVa1WVXvWVIHVV6MMxPdUeTcZVbDpjKpUpSpVbVSFp8l9G5so97VXJiN13Bk1gqpSlapU9QJVHh7goSoP/vgDK0D2N5nIrl0AAAAASUVORK5CYII=",
                "result_message": "生成二维码成功",
                "result_code": "0",
                "uuid": "zY-NlRMsfLdhTxQSsniiSR79mg5LD_2AjHKgvwO6lk10CTrIXltBMLEJ-_eZ4rPt1INo9qlOtm98rw1"
            } 中的image参数
        """
        response = session.post(
            constants.PASSPORT_CREATE_QR64_URL,
            headers={**headers, REFER: constants.LOGIN_PAGE_URL},
            data={APPID: OTN}
        )
        results = response.json()
        image_data = results.get("image")
        image = base64.b64decode(image_data)
        with open("qr_code.png", "wb") as f:
            f.write(image)
        return results.get(UUID)

    @staticmethod
    def check_qr(uuid_: str, headers: dict[str, str]) -> dict[str, str]:
        """
        :param uuid_: create_qr64接口中返回的uuid参数
        :param headers:
        :return:
        {
            "result_message": "二维码状态查询成功",
            "result_code": "0"
        }
        {
            "result_message": "二维码状态查询成功",
            "result_code": "1"
        }
        {
            "result_message": "扫码登录成功",
            "uamtk": "XFzDkM8DAdXJj0i1rsALxHIQKWGJ-LEvyEXHAQgal1l0",
            "result_code": "2"
        }
        """
        data = {UUID: uuid_, APPID: OTN}
        session.headers.update({USE_AGENT: headers.get(USE_AGENT)})
        response = session.post(
            constants.PASSPORT_CHECK_QR_URL,
            headers={**headers, REFER: constants.LOGIN_PAGE_URL},
            data=data
        )
        results = response.json()
        if results.get("result_code") == constants.ResponseCodes.LOGIN_SUCCESS.value:
            request_utils.add_dict_to_cookiejar(session.cookies, cookie_dict={UAMTK: results.get(UAMTK)})
            _fill_cookie()
        return results


class QueryAPI:
    @staticmethod
    def query_trains(
            train_date: str,
            from_station: str,
            to_station: str,
            headers: dict[str, str]
    ) -> dict[str, str]:
        """
        :param train_date:
        :param from_station:
        :param to_station:
        :param headers:
        :return:
            {
                "httpstatus": 200,
                "data": {
                    "result": ["po7iOf6GGmp7J4DN4c%2F2mzDXu45BFa63xBWYz5VvXLQOBtJr%2BVXZoqZKWDDW4F%2FWXyGO7aKOk287%0ABJn5LvY1bxXMaf0Hwu9RXveiFLxm944lifMAjDfjuxonovS%2FLTdMhGD2%2FXMp11heaKXt7XOUoIlb%0A5Rlbd5c1%2F91FJnQSu5OXm3kbCnEk2rlpIe%2FeV0JfzUPW3IhZ91dYBqwgeEc1k%2FqAmVIA54xACGcy%0ACfkjJisgBEznrtpB1CWbG5DSlRdt28LTsg7AzmA10lxVJ1vrL55%2BVJLtD1bKTkkCgwh5vgvILv9y%0AMmNytH5sio7LlL2sJp%2FHI%2FefVuJH6Z%2Be%2Fwb5X0pY4n%2FdbOEb7VWsWw%3D%3D|预订|330000K59822|K599|BTC|GZQ|FTP|GZQ|05:19|10:42|29:23|N|2oCrl3Zy7m0Z%2FAOA%2FkPYtu4mA0l9KW046f%2BHN7cA4FnIFUOB%2FfA10HGeCew%3D|20250109|3|C1|09|33|1|0||||无|||无||无|无|||||104030W0|1431|0|1||1025100000407500000030426000001025103000|0|||||1|0#0#0#0#z#0#43#z|||CHN,CHN|||N#N#|43075004107840330426031045603204410||202412270800|", "MrGnPTQCilQPImnl6933wxQfWs4SpJgbvLY1YPMGzqbKTzugovQHWdFM%2BUyZH6y1Xe8yvdiskUa2%0AP3vECVUJW%2B1zrTOiGVAhe7XgccfHaS%2FRlxegvshXam93WljtZrGaE2IQsdH6Esc5Fb5WnfsmgM7s%0ABCP0IXk%2FzUkQFCot9L8q%2BREGPPFykoC83wLt7sqC%2Bg4lBvC48t%2BWhzEqTKq3lprvL0yOSirx7%2B%2Bj%0A9IC8Pcl8xQep7MFUdS4OUUPWOiunhaMqW%2BcXr3wG5ORRsUABrFpjgdQc0%2BktuDQRBwMq89JsNXzM%0A6g64WO5ietLIS6x1hPnJjK%2Br67oO9HjxVQr4gxnFb4I%3D|预订|240000G33507|G335|BXP|NZQ|BXP|IZQ|07:26|17:49|10:23|Y|zqD2mZ%2FLQwYwVopMaEAcE2aahhj38ox42McOyCn4ivD1dwYO|20250110|3|P2|01|15|1|0|||||||||||有|无|无||90M0O0|9MO|0|1||9299000000M137900000O086200021|0|||||1|5#1#0#S#z#0#z#z|||CHN,CHN|||N#N#||90083M0084O0084|202412270800|", "geS8SUMxi40y2NxzyhAld79zYovIZmWWCNDt86dNcvq%2FbKDUd4O6dhRwoHa5D%2FdI7NJA6awXuQku%0APILzQgCVKdUPaX8v1xNEs3SyVqNMYq8NnW1QwNaSmUMCTtRHlJ47lzNfKegbCQA3JCauNbNrRqeG%0AWjg60giaz2ddBS5pPKZkgAv%2BuiJtZdLAtixtLY%2BYwHxSyl%2BLa8FFcvenYj%2BeHngRHzvT2FJsiVe3%0A4pfVUE8jBbEoCmNMtcj4g9Y%2BaLBe7j1m87V2j2%2F4yXDmc1RZHhKJuA4qT72u6nwnDjriIySOxDZK%0AayJwaa7ydU79Nobjv0tg%2F%2Ftvpn%2FFyM8JcpwP8w%3D%3D|预订|2400000G7710|G77|BJP|IZQ|BJP|IZQ|07:34|15:35|08:01|Y|laP7Ft%2FtUi%2BFpGvMiHVg7p%2F4QWyJkQ1gx%2BCeSiaeEtPT5a29|20250110|3|P3|01|09|1|0|||||||||||有|有|1||90M0O0|9MO|0|0||9325900001M165800021O103600021|0|||||1|5#1#0#S#z#0#z#z|||CHN,CHN|||N#N#||90090|202412271000|", "regu0TrsHTQvu1sIHuV10ZAYWOsFNCOcH1mu60gq4azYwmsSgIt2xw942cFhsSeqT2q32qdmllpW%0AQgPjJ4F5QyYryjScDCNSrc6bJDSEyzaBPkOVEVFQ8O8lzYcODpf%2FznFCo4BonZlX2roB72shCPBs%0A6seaO9eLJTaksLdES03tI6unhiSnulgUJl8C5pAV%2B7uOM3dt1HZC14%2BERD4fPBk9uObvz7U1GUcM%0AzNnoYrdPepzNzBpZsun75YmxUOuTh%2BbWaWJEeEMJpB%2BoOmKFzpgcf%2BeOn7XdodIlk536ArQWE2xd%0AsHoWwCCkksRnKQXqq1UTkdJnlX5Bib8ZB6QJaA%3D%3D|预订|2400000G7710|G77|BJP|IZQ|BXP|IZQ|08:00|15:35|07:35|Y|KF9YKJTV4IM%2FGERP1RBQnALInpmydCzZ5qNh2hFjO1nNSIZm|20250110|3|P3|02|09|1|0|||||||||||1|16|无||90M0O0|9MO|0|1||9325000000M165300016O103300001|0|||||1|5#1#0#S#z#0#z#z|||CHN,CHN|||N#N#||90090|202412270800|", "sj5f2SaEOe2XIPsycJ%2F2SzMBBYnFHbIdk46CMPGg5O6TTmwNKqHjiFXmtus8BI2mpD744Zuo1poi%0AF7RrzCCNAwPq%2Bb21q8QUprFlBk%2FbSRiahXOWq7LidpUn0bai80krgUbC6GHsR0DhbLt0bGb0n8sP%0A8WQydGw0pxf1vzhDMGKqlOzXnx%2BKjruZMpV8HprmZyum4ewm8FyB4T49kzRydQv9I7KfI7UhIx5%2F%0Au77q5SbqDyLRTbGUbnQ7a6tZBLJn9RwiH9c5MAipcSbqpfaD0ay33a7ap2Wblm2hisfsDFtyLYSg%0AkbMc5F1myDa2rGwYXQQghz4YdvKxBDinhIpT%2BzCfLPM%3D|预订|24000G15790B|G1579|BXP|IZQ|BXP|IZQ|08:32|19:12|10:40|Y|Bq4SNgEQKD2PeRvgmPgacf1nwrwjje9FT9Gm1ppBu61j1a8F|20250110|3|P4|01|17|1|0|||||||||||有|有|3||90M0O0|9MO|1|0||9299000003M137900021O086200021|0|||||1|0#1#0#0#z#0#z#z|||CHN,CHN|||N#N#||90083M0084O0084|202412270800|", "yZsCIyHjUrRGB1mpWXbR%2BdVIZpcYE4S6mkbe0gY%2B5uvgn7C4GiFVBPZTsCLDehneEG04PNngdOfi%0A%2Fnn44HyvRRHmxC3Sp17tGAzQc9cEsAnGLmaFecAOYxIkXzlzUcKZqDU6uLbkrtoj%2FCuHmPIpkQep%0AdwS%2Fgc7MEYidXCjIenxp6QVE1IjbwR6z5ugU5K8BrDCQyUoLvIp4Z22xrG%2F0WedI4WN9s0rmkJ1I%0AJKQG94MrmhHc6Uz%2Fuae%2FboEBaN0fcHL5G3I1gojIqVUCNFepL7SWUTw8hmPnTNaj5paIhuynXHp6%0AlCq81Gb0472vO8xXm0RE5oNZIRhCryeWKpOSXjInJcto%2BCD5IGE9Gbi3djg%3D|预订|2400000D3510|D35|BXP|GBA|BXP|GBA|09:17|06:39|21:22|Y|qLjklywvk2NX9x0V4j7DrjIOVTlKt6gxGqdP%2BDVg582MenMSQkVKvTNFKsE%3D|20250110|3|P4|01|05|1|0||||有|||有||有||有||||O0J0I0W0|OJIO|0|0||O032500021J052000021I087200021O032503034|0|||||1|0#1#0#0#z#0#JI#z|||CHN,CHN|||N#N#|J305200J106060J205540I308720I109870|O0046J3050J1049J2049I3065I1065W0046|202412270800|", "VljApJATEflveu3uX0FL1C5KSMUjUV2mnJ99YJI8PzgBBIG13NqvFmsG%2BWFXjWujLlWLskWegB5O%0AmviEfoSidyc6kW0oUD%2B4m8vl%2F5Rnjy8wcyCbdhdLPkGmY8rScWJAHfhCeVpmX0HOqzS0uUAqH3oT%0AlSu8CyoAXdw9ik8jlGV%2FVGZovO%2FaldoBgl2EBK2B%2Be8O5qCGrBzevSjU%2FPdHvii7lbbWL3gtomp9%0ANIdGazTe5Y7cs7HmFN6hOwcEmYsM59NoVHB54y2nRRA9noG%2FSyp6JVTtIJI7nZVCKnWTJ2MArsMh%0Aqm6Na6XIFPVp%2B5iO97g3NH56aQiEQ3BT24P55pEdmlA%3D|预订|2400000G790Q|G79|BXP|XJA|BXP|IZQ|10:00|17:17|07:17|Y|k%2F1a7j6qnQ8wLylmXj1nZl9EDS7fDvaK9Gnla5rgZ3y91nF8|20250110|3|X1|01|06|1|0|||||||||||无|无|2||90M0O0|9MO|0|1||9325000002M165300000O103300000|0|||||1|5#1#Q03#0#z#0#z#z|||CHN,CHN|||N#N#||90090|202412270800|", "hhDaIkXOVRjxpRRS1ObGWvo5EKbDdT2NpZn6PRUeUi1eNIrNxYzoNWVfccOIzO8Sl1O4RkwsDNxH%0ARTjzaXQ4Sl7xwVh3Ye37O1srBOhVhJrXp4wbSX4PwsP7FUzMJdiFsHMxs3p74r9f0hpHouqqTH64%0AW%2FU3K4ptW5aLJZZPAO2IEmZXYEOvcGLF9Rg9WzkMsc6vRvlkLH%2BFlfdwFMrlcjQrLO%2B7hOim0ugY%0AWgUS9xcJu3iIMuXWn6FAZQSk6QxfZ%2ByAyrcgcAn4pqPt7%2B78HYDp7AtPNAl%2FLrOs2qqLC6SR%2FVmD%0AC0SnGXFDbjAVsuFgNQjL4jQsrSgjylGT1lfiAzFPeZQ%3D|预订|240000G3370B|G337|BXP|ZHQ|BXP|IZQ|10:23|20:54|10:31|Y|D%2FeHei453yvtU8%2BGMdrNQYM%2FfdGop0zQmNCLeHgSgQtQBUvb|20250110|3|P3|01|19|1|0|||||||||||有|有|无||90M0O0|9MO|0|1||9299000000M137900021O086200021|0|||||1|0#1#0#0#z#0#z#z|||CHN,CHN|||N#N#||90083M0084O0084|202412270800|", "eTvhzYYo8p2Atrko2VF4NhfkZVBXIwJL6EwhGfGgK9RBybOJARULVQMqvBBy6%2BpLpZcnkgIQ%2FYE3%0AqxLFgkr0x9mPcjfE%2Byn%2FGP25q6vJupXwCd3%2FDSwUxKV1uRAuuO3XJh6vjgS1iq1KLtuKQY86hXgo%0AjG0Rn%2FHNSlsBVyIzZNQ1Lo0aqaS7vmcjE7YOxnYi4ILwB%2Fv%2FlbD%2B8W9pbcLgLpM%2Fd3Ch5mMe0xf2%0AlkvwgciUWdVAQwcaEOygGuxP2tcExZW9HlfV7gTYqXL8hAC0SlqaJFaNB%2BPqTpRDFauktrT59vi5%0ANZMBUOVDVBunTIoW0x6UZD5ynwfqhU79P8QYM%2FdV4xQ%3D|预订|240000G33922|G339|BXP|IZQ|BXP|IZQ|12:26|22:51|10:25|Y|XySaWDrgoKUTYXMXop2yTVfswtEPMrc4FFWPmpO2RDwinGzu|20250110|3|P4|01|17|1|0|||||||||||无|无|3||90M0O0|9MO|0|1||9299000003M137900000O086200000|0|||||1|5#1#0#S#z#0#z#z|||CHN,CHN|||N#N#||90083M0084O0084|202412270800|", "BBwp4f8KIFHPyCZV4Nm365DzyWkcoULMnO5cjrf7qS%2BlNm8xXd7vX%2BqMIdo1RmlVDmwTYhcsgN4y%0A54YRb3vg37xN4%2B6giGZAiU8I%2BRwNOV%2FTRSB2Z1qre%2BOgG5VtF9yPnToGD5CWxWefmmoMGmmIiUdZ%0AKQUNA18%2Br0sO6%2BcCmJ4uVR4EEp65j%2Biu%2FEB%2BZHfK67zD56wzrB85ZurFHXJXqAH513HG7iTvaMa4%0AgYwfJ%2FIJ%2FJZpP5ULi17cKh9db1urvQbskN8cY1GtXMAC6epRG4EeKkRvg0dJxL1%2FAOPEZDTBBaC4%0AEWrIyqzF225GhLGDtHjteyZoQRYYyElRoUIXUw%3D%3D|预订|2400000G8123|G81|BXP|IOQ|BXP|IZQ|14:00|21:43|07:43|Y|NOpGHklkqhpllWWo29sxIY93yMMBrC4NnSuyr85JO6pNA57K|20250110|3|P2|01|09|1|0|||||||||||有|有|无||90M0O0|9MO|0|1||9325000000M165300021O103300021|0|||||1|0#1#0#0#z#0#z#z|||CHN,CHN|||N#N#||90090|202412270800|", "ydJDM0DEa6F6xuapgNMcc6wAhrwoutm6ynzDRzKgGbkLc7%2BVuHjWWr4sYUSWFR8M%2B1eDafjwT%2B5V%0Auh6TEj81brI9Xdx4QtBGGXCk5Te0l%2B%2BHPtoQJ5KFBU%2FiTt6N2nF8MK%2BPk9HdDSelTJRDTq7bYQvX%0AH5C7tqHoCgJW76V0%2BOeda8UT4fZiG17cKXM12dEzL43keWlS620v07HUD4QHv%2FUTLjTpBdjKXYIx%0APPD%2Bywq%2BCvcRN0iAxmGWZKNCaI9a7miycOtteU1QDteN7VL7Tz09mrhhUY4VoI9dTu7d6%2FOaG3u5%0A8ObCxAIxxZ1uxNxoXDbqzGOtON5rInUsCue4ZbSXa42hYVg2mLeW3q%2BUbbrT72k0BM6uyQ%3D%3D|预订|1200000Z120H|Z13|SBT|GZQ|FTP|GZQ|14:24|12:41|22:17|Y|LOGaqt%2F%2Fq2AxoV3BttEiOj15QoR2UjqlupP%2Fm4bzHFYTl4nuf8zVB%2FDzhYlg2kjJhVSQf591GNE%3D|20250110|3|T2|08|15|1|0||无||无|||有||无|无|||||30406010W0|34611|0|1||30426000004075000000613830000010251000001025103030|0|||||1|0#0#0#0#z#0#346#z|||CHN,CHN|||N#N#|3304260310456032044104307500410784063138306114450||202412270800|", "4cUPYUpZgNTamoToDw2IZeeovcVbFUwEMmfT5iuztqDVM5%2FO1vAFYYIPLb6LwxH%2BWOm3qy5JdhSg%0AwuFjPNwQ7WMj51jiGiMzn5E5nY0D9dPNSKIGueL%2FW6LVEFDKXtUSRYS4ge46E%2FUWhMywLopONBim%0AIqI4nefegkVxr8FWwaScytqHDo7wkt1pqxcmuQIYnd9C%2B3mUi1bDRMGTNG3bwAwr%2Fdalz3WVMJ2g%0AJ6gq7ukkVHpiFgsGPV%2BTlamB%2FlU9uw7PpE0kMEhf0udSkzJC8pRqS0o48eH7i45mOjpcTOCd3aAC%0AvjhXkT%2BSADfMyYfZzDFRVjaiiX8%3D|预订|240000D9212S|D921|BXP|ZWQ|BXP|IZQ|19:36|06:37|11:01|N|EMekG4veh14pJxS5SxyN7OlSUD%2B4c601|20250110|3|P2|01|05|1|0||||无|||||||无||||F0O0|FO|0|1||F085000000O070900000|0|||||1|2#0#0#0#z#0#F#z|||CHN,CHN|||N#N#|F308500F109600|F3047F1047|202412270800|", "ZtYw3MQ0EpOinNQ5OvdgGMJDYqGJfmn4ucPufkgr%2BoWd2FWFh5mOlKl%2F9U48FZQ9yAip%2F1yBtz8O%0A9qK%2FnJL5a8jKIuMUIAmjU3YmOvTeFxTpRDmKfzOAVmLu%2BSnIHOkTF6vA%2FmuBmp71eMISk%2Fr1Y54t%0AiolfSZWMSOUyQb8zC9CmY%2FRN6g4rD%2Fi66DulqjnTC4jZ1sUWY%2Fje%2FKmE1X1KZW4r%2FU8gR3asIpzP%0AGxecsqf4Y8OxjxNcaaLUAiH0FIEVpwKJZmjs8LHrxK8rtuOk16ycyb1MKIHBSZ0put%2FUVsiZ0mhO%0AdqdNbss%2Fpcw%3D|预订|240000D9011M|D901|BXP|IOQ|BXP|GZQ|19:43|06:38|10:55|N|s8WiT9BwYAi6dkSKBhUOYw%3D%3D|20250110|3|P2|01|06|1|0||||无|||||||||||F0|F|0|1||F082000000|0|||||1|2#0#0#0#z#0#F#z|||CHN,CHN|||N#N#|F308200F109300|F3046F1046|202412270800|", "hwOY72Adm2mrGNcjUOUKojvx81LVm4BBoMjNcE1vwSnWbxwYdEywr59cQmzxNMkNS54ySp96aRgK%0AnFo0pTvRbOu61%2BU778Z%2FRM1SgKyECzpzCmj%2BkpabW7dJqc3ixdeaglKkc20UnqYK%2BRojet0TY3Zq%0Ancf6%2BTqolelQDeA0Jjye2fOr%2FP5%2BtwiWdsABr%2FMdY47gpAb1fomT7gum3cGW4P9klXPs1bdYs0vz%0AwJXi%2Fs%2FRlBsSRXIfPxyi9%2Bw%2BRs1glbsdO1Aidgpp%2B65Vt0lcka2eNMbgwBEZOy0Qnw0vqzNHsU0I%0APdwbbXsrvk7s42lSAXteQg%3D%3D|预订|240000D9031P|D903|BXP|IOQ|BXP|GZQ|20:05|06:33|10:28|N|U7p6uaZW1obYKeKPLUusoNWR8Y7liurx|20250110|3|P3|01|05|1|0||||无|||||||无||||O0F0|OF|0|1||O070300000F082000000|0|||||1|2#0#0#0#z#0#F#z|||CHN,CHN|||N#N#|F308200F109300|F3046F1046|202412270800|", "HVxBDHg7E5aztnkBqSkhj4fnjgyqW5y68dHzSoWGzvbHcB%2Bto2eyDJciATfTx74U3hpjdIJuTEKO%0Avy%2BunWPF6y9dz4nqzzvNIEHzQdCrPR2eRqahkNnezM%2FNwwptY9bRHeXPpyzeXAYEWEL9rdI2AKVN%0AVLTSmqcd9ZArIP7gBdwTaIsH0StlqCDeaat%2FCo3fF%2Fr7J1cHFrSV%2B%2F6RRs2eM5k9A3D5stFHESjg%0AeiJddlq9WJ2sacyS9nqVGEGEmuXI3JnGGLBsnOqTFiZGKiyvul7JmfFck2sk9gMQQLwI43hSPiar%0A8yVZROeMhxzKJVNbGCerMryjHNe0Et%2FXMvusDhAWRNU%3D|预订|240000G89702|G897|BXP|XJA|BXP|IZQ|20:13|06:07|09:54|N|JD4%2FFAzoUM2itXFOhPJ8MmOoS5qDdhwP9ietWyU0ty8EpH%2Fx|20250110|3|X1|01|05|1|0||||无||无|||||无||||F0O0P0|FOP|0|1||F095000000O077500000P083700000|0|||||1|5#1#0#0#z#0#F#z|||CHN,CHN|||N#N#|F309500F110700|F3036F1036O0075P0045|202412270800|", "80LZzk5D936amY9aCGVbgCyDEQGMNduG6sKGobEzd8g%2BfdlliMoH2jj33fqAtuuTJqdgQg4H08aC%0AtLsfGUbu2VctdQo1g3b73sBUPnqqpXg4K%2FAfVk%2F8o3%2B59IzMR1Dmf%2Bg2vv%2Bn5D6KHMAUsP%2FiseLF%0AtZhbXw4qsPCKxUNMYBFWm%2BicyFW8Nb2Ea1V2S2oAJqfjHYSirBmk9pExp4hAbpOWQsWcOznGgS04%0AXm9ZjNkXKpMyMLaZmNIH9qLIXXNDnwP3tOIysqN9nONiyNPnwnE48yBPHnMHif3xcMQrAgk0F6HX%0Ab8rUqWp8LYKVfBLoKPjAf%2BD6Pw8%3D|预订|240000D92720|D927|BXP|CBQ|BXP|IZQ|20:18|06:47|10:29|N|%2BjCWKOhdELw8cmRfhJ8fUVphal3iQccp|20250110|3|P3|01|05|1|0||||无|||||||无||||O0F0|OF|0|1||O070900000F092000000|0|||||1|0#0#0#0#z#0#F#z|||CHN,CHN|||N#N#|F309200F110400|F3051F1051|202412270800|", "M7K319PXYH6AX1gFIpULzBj3PE%2B75vmbTpy6B0meiUSdckZSI1aeCrN9ZlJmsmVQ1e8AQfcelO9v%0AnGjHBYVij81XWxm7hVyfFWBIeCasn5i6EhC2neQbg9YDM5ykQfne69cyGVyOau1ibnhWUThS7BCu%0AqlLVoowCN30zWsQZ05jM1PkRDL7cXoxaXVmsCatP3Hs4Nz6ywyg8dyWFdP7bgmYzdMFJxWIE0aDV%0AxYQnPfnYLwdUB7vJHLckZjXZSS%2FZn1%2FxpY3eaIDYpGtB9rCGCW0dnP1KF8%2FlSDx2SHHF4oi54y1J%0AM8XJQ7QIG9IhZcMMvbUe59uZZMHTdyQJhDNUfErmLXHqPFgXSvlsi3VIvrNvmseMnICQvbfOZEU%3D|预订|240000Z5010D|Z501|BXP|SEQ|BXP|GBA|20:24|18:03|21:39|Y|%2Fd5XxtgzKcBrk4H3mVNEosqFng93x5rDjv3rDkNcdz087vjT%2FyHmuoc1Yzi%2FhMMuz5zXzBeE1mg%3D|20250110|3|P2|01|08|1|0||无||无|||无||无|1|||||30406010W0|34611|0|1||30426000004075000000613830000010251000011025103000|0|||||1|0#0#0#0#z#0#346#z|||CHN,CHN|||N#N#|3304260310456032044104307500410784063138306114450||202412270800|", "Wl%2BpDKtwXmOQVh9bE3IxXlNxYcSo8R%2Bn4pv45ePu8sbz0HIUjC1xc39yP8LXFuIZG0ZHGmKrSyep%0AOTHbFV%2FTrQPIIosNBriGSDkxQzieWn%2BYn1ru5j5HswLlwRIWL7HrG%2BwUYTUhdzoZVpW5FFVCW3H2%0AIAI7%2BlCeFwjI%2FJU2NAx7n0J7TlM1AW0W9s%2BwUmqkGE%2Fvitj9cgJk3BedrWaV0qZil2Nlm6c%2Bh%2Bpt%0A17a1%2Bis9XwfVYM%2FM7DRtfrSdGKsQMNYw%2BhsG%2FQpCgiGxvQTo%2FZiD%2BfA5YlciLAvnpHFVViAu9gzl%0AVlOYfkvH2gPdZYA1aPZE2ZXoqAo%3D|预订|240000D9231L|D923|BXP|ZHQ|BXP|IZQ|20:27|06:42|10:15|N|Dqt1HTUdPnOSA24aTFdYQSxtwU9gCtz4|20250110|3|P3|01|05|1|0||||无|||||||无||||F0O0|FO|0|1||F109000000O070900000|0|||||1|2#0#0#0#z#0#F#z|||CHN,CHN|||N#N#|F310900F112300|F3061F1061|202412270800|", "mfFlJZmLsAAQxTKFgSj0v2A%2BuBDyWzDvBvYKIGZaeEsZ2bUAbCLqh8jtVgJJmGIKSQBdKaQ1y9AD%0AtBazhWkFZnLn09cuS7IP%2FZQxRIezVJh2oO51TPRoguc5Mcxyh93XL0moldkEUNL4UyRa5dcmEr4u%0A8q07x9kHPIq6I2xV17fjNoXk%2Fjr4Bcl2K44Zcj22XRPK3FoCy%2FSkqNENMx6h6hU2FOYtyStfANbA%0AFF5%2BkBv6B9SRV8YFUD80JCPAB1D0EMdZ9cExLqo4rOkNfS1yAXQ3MYJ7xsYcBTv9JEUTYVU%2F4Zv%2B%0AymJsbYOIH3LnpEW9qiCv%2BuJTd59cY7XFj%2BBK76ml1MumhpzO|预订|0h0000Z1140K|Z111|VAB|VUQ|FTP|GBA|23:06|20:57|21:51|N|vul8k6aqrxgcRNhWJtQzaAg5nNGgLjr%2FgwRgQaysse3F3Fa6|20250110|3|B3|09|19|1|0||||无|||||无|无|||||104030|143|0|1||102510000040723000003042600000|0|||||1|0#0#0#0#z#0#43#z|||CHN,CHN|||N#N#|43072304107540330426031045603204410||202412270800|"],
                    "flag": "1",
                    "level": "0",
                    "sametlc": "Y",
                    "map": {
                        "IZQ": "广州南",
                        "FTP": "北京丰台",
                        "GBA": "广州白云",
                        "BJP": "北京",
                        "BXP": "北京西",
                        "GZQ": "广州"
                    }
                },
                "messages": "",
                "status": true
            }
        """
        params = {
            "leftTicketDTO.train_date": train_date,
            "leftTicketDTO.from_station": SITE_MAP.get(from_station),
            "leftTicketDTO.to_station": SITE_MAP.get(to_station),
            "purpose_codes": "ADULT",
        }
        response = session.get(
            constants.LEFT_TICKET_URL,
            params=params,
            headers={**headers, REFER: constants.LEFT_TICKETS_INIT_URL}
        )
        return response.json()

    @staticmethod
    def lc_query_g(
            train_date: str,
            from_station: str,
            to_station: str,
            new_app_tk: str,
            headers: dict[str, str]
    ) -> dict:
        """
        :param train_date:
        :param from_station:
        :param to_station:
        :param new_app_tk:
        :param headers:
        :return:
            {
                "httpstatus": 200,
                "data": "",
                "status": true,
                "errorMsg": "没有查询到中转方案"
            }
        """
        params = {
            "train_date": train_date,
            "from_station_telecode": SITE_MAP.get(from_station),
            "to_station_telecode": SITE_MAP.get(to_station),
            "result_index": "0",
            "can_query": "Y",
            "isShowWZ": "Y",
            "sort_type": "2",
            "purpose_codes": "00",
            "is_loop_transfer": "S",
            "channel": "E",
            JSON_ATTR: '',
        }
        response = session.get(
            constants.LC_QUERY_URL,
            params=params,
            headers={**headers, REFER: constants.LEFT_TICKETS_INIT_URL, "tk": new_app_tk}
        )
        return response.json()

    @staticmethod
    def check_user(headers: dict[str, str]) -> dict:
        """
        :param headers:
        :return:
            {
                "validateMessagesShowId": "_validatorMessage",
                "status": true,
                "httpstatus": 200,
                "data": {
                    "flag": true
                },
                "messages": [],
                "validateMessages": {}
            }
        """
        response = session.post(
            constants.CHECK_USER_URL,
            headers={**headers, REFER: constants.LEFT_TICKETS_INIT_URL},
            data={JSON_ATTR: ""}
        )
        return response.json()

    @staticmethod
    def submit_order_request(data: dict[str, str], headers: dict[str, str]) -> None:
        """
        :param data:
        :param headers:
        :return:
            {
                "validateMessagesShowId": "_validatorMessage",
                "status": false,
                "httpstatus": 200,
                "messages": ["当前时间不可以订票"],
                "validateMessages": {}
            }
            {
                "validateMessagesShowId": "_validatorMessage",
                "status": true,
                "httpstatus": 200,
                "data": "0",
                "messages": [],
                "validateMessages": {}
            }
        """
        response = session.post(
            constants.SUBMIT_ORDER_REQUEST_URL,
            headers={**headers, REFER: constants.LEFT_TICKETS_INIT_URL},
            data=urlencode(data)
        )
        return response.json()


class OrderAPI:
    @staticmethod
    def confirm_passenger_init_dc(headers: dict[str, str]) -> str:
        headers = {
            'Host': 'kyfw.12306.cn',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Upgrade-Insecure-Requests': '1',
            'Origin': 'https://kyfw.12306.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = session.post(
            constants.CONFIRM_PASSENGER_INIT_DC_URL,
            headers={
                **headers,
                REFER: constants.LEFT_TICKETS_INIT_URL,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={JSON_ATTR: ""}
        )
        return response.text

    @staticmethod
    def get_passenger_dtos(headers: dict[str, str], repeat_submit_token: str) -> list[dict[str, str]]:
        """
                :param headers:
                :param repeat_submit_token:
                :return:
                    {
                        "validateMessagesShowId": "_validatorMessage",
                        "status": true,
                        "httpstatus": 200,
                        "data": {
                            "notify_for_gat": "",
                            "isExist": true,
                            "exMsg": "",
                            "two_isOpenClick": ["93", "95", "97", "99"],
                            "other_isOpenClick": ["91", "93", "98", "99", "95", "97"],
                            "normal_passengers": [{
                                "passenger_name": "刘伦杰",
                                "sex_code": "M",
                                "sex_name": "男",
                                "born_date": "1992-09-30 00:00:00",
                                "country_code": "CHN",
                                "passenger_id_type_code": "1",
                                "passenger_id_type_name": "居民身份证",
                                "passenger_id_no": "4290***********917",
                                "passenger_type": "1",
                                "passenger_type_name": "成人",
                                "mobile_no": "137****3873",
                                "phone_no": "",
                                "email": "78*****52@qq.com",
                                "address": "",
                                "postalcode": "",
                                "first_letter": "",
                                "recordCount": "14",
                                "isUserSelf": "Y",
                                "total_times": "99",
                                "index_id": "0",
                                "allEncStr": "b0fd258da6ace8c0d9a452caa2be495fe1e378c40ec28b0f3a655a43db6c68cc7a1d4a66b64dd5cbcbfd16b4a0f11ae0da9875b4174a4cdcb2ddb148deb707c5afeb7e6b2b6e55dee335798194bbfde7dee4af3f0947645264e03dea190d5e32",
                                "isAdult": "Y",
                                "isYongThan10": "N",
                                "isYongThan14": "N",
                                "isOldThan60": "N",
                                "if_receive": "Y",
                                "is_active": "Y",
                                "is_buy_ticket": "N",
                                "last_time": "20180114154653",
                                "passenger_uuid": "d1a6b5818b5f6561dadbd98dc698d988fddb2d0ca9c18de567c1935b1558839d",
                                "if_preferential": "",
                                "mobile_code": "86",
                                "temporay_age60": "N",
                                "gat_born_date": "19920930",
                                "gat_valid_date_start": "",
                                "gat_valid_date_end": "",
                                "gat_version": ""
                            }, {
                                "passenger_name": "白洁",
                                "sex_code": "F",
                                "sex_name": "女",
                                "born_date": "1974-02-10 00:00:00",
                                "country_code": "CHN",
                                "passenger_id_type_code": "1",
                                "passenger_id_type_name": "居民身份证",
                                "passenger_id_no": "2107***********040",
                                "passenger_type": "1",
                                "passenger_type_name": "成人",
                                "mobile_no": "137****3873",
                                "phone_no": "",
                                "email": "",
                                "address": "",
                                "postalcode": "",
                                "first_letter": "BJ",
                                "recordCount": "14",
                                "isUserSelf": "N",
                                "total_times": "99",
                                "index_id": "1",
                                "allEncStr": "d82f31f38fd52d7e303811c3e098d56850416775ad7d7af22b8d6356be1af9bb75be1954821954410db89c3b41471caf5571e48f893c05ee82dcfc77a57be75c821b7ff07379bad0bfe041e3ea1aeddf",
                                "isAdult": "Y",
                                "isYongThan10": "N",
                                "isYongThan14": "N",
                                "isOldThan60": "N",
                                "if_receive": "Y",
                                "is_active": "N",
                                "is_buy_ticket": "N",
                                "last_time": "20240416230956",
                                "passenger_uuid": "c27a537ae8a5cd344cf38cc3ea76dda80d487d2dc612c65de8f36b769663015b",
                                "if_preferential": "",
                                "mobile_code": "86",
                                "temporay_age60": "N",
                                "gat_born_date": "19740210",
                                "gat_valid_date_start": "",
                                "gat_valid_date_end": "",
                                "gat_version": ""
                            }, {
                                "passenger_name": "洪笛笙",
                                "sex_code": "M",
                                "sex_name": "男",
                                "born_date": "2004-06-28 00:00:00",
                                "country_code": "CHN",
                                "passenger_id_type_code": "1",
                                "passenger_id_type_name": "居民身份证",
                                "passenger_id_no": "3505***********515",
                                "passenger_type": "3",
                                "passenger_type_name": "学生",
                                "mobile_no": "150****7343",
                                "phone_no": "",
                                "email": "",
                                "address": "",
                                "postalcode": "",
                                "first_letter": "HDS",
                                "recordCount": "14",
                                "isUserSelf": "N",
                                "total_times": "99",
                                "index_id": "2",
                                "allEncStr": "c655c332e7f9d82a148e3716bdd2b56829417820ff6d16c012639a5577727303a8c3068c3f5bd68b475aa4a75583a555412dfd656b68f3fd51551ea9957d86c1dee4af3f0947645264e03dea190d5e32",
                                "isAdult": "Y",
                                "isYongThan10": "N",
                                "isYongThan14": "N",
                                "isOldThan60": "N",
                                "if_receive": "Y",
                                "is_active": "N",
                                "is_buy_ticket": "N",
                                "last_time": "20230922163651",
                                "passenger_uuid": "db90ad1d0acb05b18ce0f1827b4dea5e7c601e80f3cd5d92572436e6c8cccc1d",
                                "if_preferential": "",
                                "mobile_code": "86",
                                "temporay_age60": "N",
                                "gat_born_date": "20040628",
                                "gat_valid_date_start": "",
                                "gat_valid_date_end": "",
                                "gat_version": ""
                            }, {
                                "passenger_name": "洪法宝",
                                "sex_code": "M",
                                "sex_name": "男",
                                "born_date": "1975-04-14 00:00:00",
                                "country_code": "CHN",
                                "passenger_id_type_code": "1",
                                "passenger_id_type_name": "居民身份证",
                                "passenger_id_no": "3505***********039",
                                "passenger_type": "1",
                                "passenger_type_name": "成人",
                                "mobile_no": "159****0682",
                                "phone_no": "",
                                "email": "",
                                "address": "",
                                "postalcode": "",
                                "first_letter": "HFB",
                                "recordCount": "14",
                                "isUserSelf": "N",
                                "total_times": "99",
                                "index_id": "3",
                                "allEncStr": "f3f78e78c335e6d2bf726519727b592d1712f51650e673b6198aab62cfb9e2609fb7eb3c8e878592ffbfdaad0adb32f37c33b5cc288ba6de548e02218996bf3fdee4af3f0947645264e03dea190d5e32",
                                "isAdult": "Y",
                                "isYongThan10": "N",
                                "isYongThan14": "N",
                                "isOldThan60": "N",
                                "if_receive": "N",
                                "is_active": "N",
                                "is_buy_ticket": "N",
                                "last_time": "20240204092536",
                                "passenger_uuid": "d280e8d51c3e6f244f26ee1e0f8ebed8ea2ba6c048f8ddfe5c0725a59f26765d",
                                "if_preferential": "",
                                "mobile_code": "86",
                                "temporay_age60": "N",
                                "gat_born_date": "19750414",
                                "gat_valid_date_start": "",
                                "gat_valid_date_end": "",
                                "gat_version": ""
                            }, {
                                "passenger_name": "洪佳彦",
                                "sex_code": "M",
                                "sex_name": "男",
                                "born_date": "2017-10-10 00:00:00",
                                "country_code": "CHN",
                                "passenger_id_type_code": "1",
                                "passenger_id_type_name": "居民身份证",
                                "passenger_id_no": "3505***********336",
                                "passenger_type": "2",
                                "passenger_type_name": "儿童",
                                "mobile_no": "159****0682",
                                "phone_no": "",
                                "email": "",
                                "address": "",
                                "postalcode": "",
                                "first_letter": "HJY",
                                "recordCount": "14",
                                "isUserSelf": "N",
                                "total_times": "99",
                                "index_id": "4",
                                "allEncStr": "9c92edaf9a00af3d13a35865998f2ac291b1cf46180632cbd33e47f877b068aed181ff3ff7d1a54ffe6dbf8f994c74ae2c811bb04a5539790292aa29b9a0e61fdee4af3f0947645264e03dea190d5e32",
                                "isAdult": "N",
                                "isYongThan10": "Y",
                                "isYongThan14": "Y",
                                "isOldThan60": "N",
                                "if_receive": "Y",
                                "is_active": "N",
                                "is_buy_ticket": "N",
                                "last_time": "20240121150636",
                                "passenger_uuid": "5bf4247db8ae016b46ecbb6acb7c94bdd06fb3b60fc16192f62fd46927e0e610",
                                "if_preferential": "",
                                "mobile_code": "86",
                                "temporay_age60": "N",
                                "gat_born_date": "20171010",
                                "gat_valid_date_start": "",
                                "gat_valid_date_end": "",
                                "gat_version": ""
                            }, {
                                "passenger_name": "黄美凤",
                                "sex_code": "F",
                                "sex_name": "女",
                                "born_date": "1999-08-23 00:00:00",
                                "country_code": "CHN",
                                "passenger_id_type_code": "1",
                                "passenger_id_type_name": "居民身份证",
                                "passenger_id_no": "4412***********32X",
                                "passenger_type": "1",
                                "passenger_type_name": "成人",
                                "mobile_no": "178****7241",
                                "phone_no": "",
                                "email": "",
                                "address": "",
                                "postalcode": "",
                                "first_letter": "HMF",
                                "recordCount": "14",
                                "isUserSelf": "N",
                                "total_times": "99",
                                "index_id": "5",
                                "allEncStr": "ca5abda72e19ee588632052487d8e757e52cb4800d94a7ad6909c9735167b394d4686d363f7fe970e5dd9d14b570ef1e7df7dcafd6c0e71b6eca1fddda4e3037dee4af3f0947645264e03dea190d5e32",
                                "isAdult": "Y",
                                "isYongThan10": "N",
                                "isYongThan14": "N",
                                "isOldThan60": "N",
                                "if_receive": "Y",
                                "is_active": "N",
                                "is_buy_ticket": "N",
                                "last_time": "20230928100125",
                                "passenger_uuid": "b80dfd5ccb9719c137575cf7c08d1c2bb4e48a8dea92d0707ad21a26d9d45fff",
                                "if_preferential": "",
                                "mobile_code": "86",
                                "temporay_age60": "N",
                                "gat_born_date": "19990823",
                                "gat_valid_date_start": "",
                                "gat_valid_date_end": "",
                                "gat_version": ""
                            }, {
                                "passenger_name": "纪大为",
                                "sex_code": "M",
                                "sex_name": "男",
                                "born_date": "1974-03-05 00:00:00",
                                "country_code": "CHN",
                                "passenger_id_type_code": "1",
                                "passenger_id_type_name": "居民身份证",
                                "passenger_id_no": "2104***********519",
                                "passenger_type": "1",
                                "passenger_type_name": "成人",
                                "mobile_no": "137****3873",
                                "phone_no": "",
                                "email": "",
                                "address": "",
                                "postalcode": "",
                                "first_letter": "JDW",
                                "recordCount": "14",
                                "isUserSelf": "N",
                                "total_times": "99",
                                "index_id": "6",
                                "allEncStr": "3e394c0eeb4dbda42f436ab862cb2b55c0be71ddef54ef5ee02934d503ef911a00320d48bb872b0dec76f5b285f9d66dc92b3e02f9cde9ed1984624fc15bc118dee4af3f0947645264e03dea190d5e32",
                                "isAdult": "Y",
                                "isYongThan10": "N",
                                "isYongThan14": "N",
                                "isOldThan60": "N",
                                "if_receive": "Y",
                                "is_active": "N",
                                "is_buy_ticket": "N",
                                "last_time": "20240416230819",
                                "passenger_uuid": "deeb19deb83d3d8ad0cbc986670e6f39669565d099609cda0e0e1556d20aedaf",
                                "if_preferential": "",
                                "mobile_code": "86",
                                "temporay_age60": "N",
                                "gat_born_date": "19740305",
                                "gat_valid_date_start": "",
                                "gat_valid_date_end": "",
                                "gat_version": ""
                            }, {
                                "passenger_name": "纪思齐",
                                "sex_code": "F",
                                "sex_name": "女",
                                "born_date": "2015-07-21 00:00:00",
                                "country_code": "CHN",
                                "passenger_id_type_code": "1",
                                "passenger_id_type_name": "居民身份证",
                                "passenger_id_no": "2104***********349",
                                "passenger_type": "1",
                                "passenger_type_name": "成人",
                                "mobile_no": "137****3873",
                                "phone_no": "",
                                "email": "",
                                "address": "",
                                "postalcode": "",
                                "first_letter": "JSQ",
                                "recordCount": "14",
                                "isUserSelf": "N",
                                "total_times": "99",
                                "index_id": "7",
                                "allEncStr": "50d9a60be25fef4e1b39109eaa78604c39e969690626a092c763fe41dea44a3163ec598163fe815c3eaccc294e62b640883e8cdc9995c1f69f19ac81d31aa1dadee4af3f0947645264e03dea190d5e32",
                                "isAdult": "N",
                                "isYongThan10": "Y",
                                "isYongThan14": "Y",
                                "isOldThan60": "N",
                                "if_receive": "Y",
                                "is_active": "N",
                                "is_buy_ticket": "N",
                                "last_time": "20240416231055",
                                "passenger_uuid": "b43be5c297adcc0aa30129308ba8e0f9080f7913a85053db2afe7903f4c421d6",
                                "if_preferential": "",
                                "mobile_code": "86",
                                "temporay_age60": "N",
                                "gat_born_date": "20150721",
                                "gat_valid_date_start": "",
                                "gat_valid_date_end": "",
                                "gat_version": ""
                            }, {
                                "passenger_name": "李靖",
                                "sex_code": "M",
                                "sex_name": "男",
                                "born_date": "1993-05-15 00:00:00",
                                "country_code": "CHN",
                                "passenger_id_type_code": "1",
                                "passenger_id_type_name": "居民身份证",
                                "passenger_id_no": "1305***********51X",
                                "passenger_type": "1",
                                "passenger_type_name": "成人",
                                "mobile_no": "182****4171",
                                "phone_no": "",
                                "email": "",
                                "address": "",
                                "postalcode": "",
                                "first_letter": "LJ",
                                "recordCount": "14",
                                "isUserSelf": "N",
                                "total_times": "99",
                                "index_id": "8",
                                "allEncStr": "58e54e11c2173bd08e64d2947970b90770ac839d31fc5f9a72e403e78c05248b950f06996df5db89abe239cde3064de2abc57ed8d57fd969bd187d88284fa4b2821b7ff07379bad0bfe041e3ea1aeddf",
                                "isAdult": "Y",
                                "isYongThan10": "N",
                                "isYongThan14": "N",
                                "isOldThan60": "N",
                                "if_receive": "N",
                                "is_active": "N",
                                "is_buy_ticket": "N",
                                "last_time": "20141206184215",
                                "passenger_uuid": "a4183ea49377741b2328dc5c68dd8d4a6256f7d8b71149c9797a95e5f2ad6c24",
                                "if_preferential": "",
                                "mobile_code": "86",
                                "temporay_age60": "Y",
                                "gat_born_date": "19000101",
                                "gat_valid_date_start": "",
                                "gat_valid_date_end": "",
                                "gat_version": ""
                            }, {
                                "passenger_name": "吴炀",
                                "sex_code": "M",
                                "sex_name": "男",
                                "born_date": "1998-02-14 00:00:00",
                                "country_code": "CHN",
                                "passenger_id_type_code": "1",
                                "passenger_id_type_name": "居民身份证",
                                "passenger_id_no": "4409***********112",
                                "passenger_type": "1",
                                "passenger_type_name": "成人",
                                "mobile_no": "158****1159",
                                "phone_no": "",
                                "email": "",
                                "address": "",
                                "postalcode": "",
                                "first_letter": "WY",
                                "recordCount": "14",
                                "isUserSelf": "N",
                                "total_times": "99",
                                "index_id": "9",
                                "allEncStr": "fd0c5e0f2da3aff2d2804eadc99622c3371d5248e9a29e8d29d93bb5d17579daec372b0a3937f533daa808a12c14af395571e48f893c05ee82dcfc77a57be75c821b7ff07379bad0bfe041e3ea1aeddf",
                                "isAdult": "Y",
                                "isYongThan10": "N",
                                "isYongThan14": "N",
                                "isOldThan60": "N",
                                "if_receive": "Y",
                                "is_active": "N",
                                "is_buy_ticket": "N",
                                "last_time": "20230928095945",
                                "passenger_uuid": "5abeb802c3a77dde61e1eab21dd085b9e7752056979e08946578f23cbf1130f5",
                                "if_preferential": "",
                                "mobile_code": "86",
                                "temporay_age60": "N",
                                "gat_born_date": "19980214",
                                "gat_valid_date_start": "",
                                "gat_valid_date_end": "",
                                "gat_version": ""
                            }, {
                                "passenger_name": "王雨欢",
                                "sex_code": "F",
                                "sex_name": "女",
                                "born_date": "1994-03-08 00:00:00",
                                "country_code": "CHN",
                                "passenger_id_type_code": "1",
                                "passenger_id_type_name": "居民身份证",
                                "passenger_id_no": "4290***********046",
                                "passenger_type": "1",
                                "passenger_type_name": "成人",
                                "mobile_no": "188****7563",
                                "phone_no": "",
                                "email": "",
                                "address": "",
                                "postalcode": "",
                                "first_letter": "WYH",
                                "recordCount": "14",
                                "isUserSelf": "N",
                                "total_times": "99",
                                "index_id": "10",
                                "allEncStr": "15f1cb32f5b3abfa7e81699fcb2b789233be7290c07e7dc97ff9fa96aa847bb90d9d567b1a6c620bd6ea41c71ddd2067127edc46659484703762328ecadd25dddee4af3f0947645264e03dea190d5e32",
                                "isAdult": "Y",
                                "isYongThan10": "N",
                                "isYongThan14": "N",
                                "isOldThan60": "N",
                                "if_receive": "N",
                                "is_active": "N",
                                "is_buy_ticket": "N",
                                "last_time": "20141205124328",
                                "passenger_uuid": "bffb89cd1a11822ab2bac68c188ab93bee387001cc4eaa79b69225b41e92d8a0",
                                "if_preferential": "",
                                "mobile_code": "86",
                                "temporay_age60": "Y",
                                "gat_born_date": "19000101",
                                "gat_valid_date_start": "",
                                "gat_valid_date_end": "",
                                "gat_version": ""
                            }, {
                                "passenger_name": "张翠安",
                                "sex_code": "F",
                                "sex_name": "女",
                                "born_date": "1979-03-02 00:00:00",
                                "country_code": "CHN",
                                "passenger_id_type_code": "1",
                                "passenger_id_type_name": "居民身份证",
                                "passenger_id_no": "4201***********084",
                                "passenger_type": "1",
                                "passenger_type_name": "成人",
                                "mobile_no": "159****0682",
                                "phone_no": "",
                                "email": "",
                                "address": "",
                                "postalcode": "",
                                "first_letter": "ZCA",
                                "recordCount": "14",
                                "isUserSelf": "N",
                                "total_times": "99",
                                "index_id": "11",
                                "allEncStr": "3cd93492de57af004b0edee3e089a505f3316b95e9fbbbb61559db5c2918919d4007b3aecb27e30bb216c318c5977dbeb60517fc499ab4731e29afbec809a9b3dee4af3f0947645264e03dea190d5e32",
                                "isAdult": "Y",
                                "isYongThan10": "N",
                                "isYongThan14": "N",
                                "isOldThan60": "N",
                                "if_receive": "Y",
                                "is_active": "N",
                                "is_buy_ticket": "N",
                                "last_time": "20240121150438",
                                "passenger_uuid": "656e3df0ff3d0c721f3613a084af19dfaa44eecc62b8e428b41537c7c0d21f92",
                                "if_preferential": "",
                                "mobile_code": "86",
                                "temporay_age60": "N",
                                "gat_born_date": "19790302",
                                "gat_valid_date_start": "",
                                "gat_valid_date_end": "",
                                "gat_version": ""
                            }, {
                                "passenger_name": "朱浩然",
                                "sex_code": "M",
                                "sex_name": "男",
                                "born_date": "1999-06-08 00:00:00",
                                "country_code": "CHN",
                                "passenger_id_type_code": "1",
                                "passenger_id_type_name": "居民身份证",
                                "passenger_id_no": "3422***********018",
                                "passenger_type": "1",
                                "passenger_type_name": "成人",
                                "mobile_no": "181****6763",
                                "phone_no": "",
                                "email": "",
                                "address": "",
                                "postalcode": "",
                                "first_letter": "ZHR",
                                "recordCount": "14",
                                "isUserSelf": "N",
                                "total_times": "99",
                                "index_id": "12",
                                "allEncStr": "bb436e5180fdf4971ade7955bc3d8010d3b20c714952f3c179f19e614b154c2b85a873d21cb7f0d484db87ba17aab39d84fb7ed5c3f6e28b82cb46f45d6ce2a3dee4af3f0947645264e03dea190d5e32",
                                "isAdult": "Y",
                                "isYongThan10": "N",
                                "isYongThan14": "N",
                                "isOldThan60": "N",
                                "if_receive": "Y",
                                "is_active": "N",
                                "is_buy_ticket": "N",
                                "last_time": "20240202171716",
                                "passenger_uuid": "8e25128464aa24174b594de6d458363e222b0a0c31fc30e1815bcb0675a63d9a",
                                "if_preferential": "",
                                "mobile_code": "86",
                                "temporay_age60": "N",
                                "gat_born_date": "19990608",
                                "gat_valid_date_start": "",
                                "gat_valid_date_end": "",
                                "gat_version": ""
                            }, {
                                "passenger_name": "曾雪璨",
                                "sex_code": "F",
                                "sex_name": "女",
                                "born_date": "1993-08-26 00:00:00",
                                "country_code": "CHN",
                                "passenger_id_type_code": "1",
                                "passenger_id_type_name": "居民身份证",
                                "passenger_id_no": "4290***********203",
                                "passenger_type": "1",
                                "passenger_type_name": "成人",
                                "mobile_no": "137****6026",
                                "phone_no": "",
                                "email": "",
                                "address": "",
                                "postalcode": "",
                                "first_letter": "ZXC",
                                "recordCount": "14",
                                "isUserSelf": "N",
                                "total_times": "99",
                                "index_id": "13",
                                "allEncStr": "3adec4ec26ba5ecebbc341e704cb06c035e0a158d28cc7dc537d20e43d2239941f22c45cdb7c4ad41b02cafd3a0ce66a3a2f3cb7d031e3f45529be28182ea497dee4af3f0947645264e03dea190d5e32",
                                "isAdult": "Y",
                                "isYongThan10": "N",
                                "isYongThan14": "N",
                                "isOldThan60": "N",
                                "if_receive": "Y",
                                "is_active": "N",
                                "is_buy_ticket": "N",
                                "last_time": "20230928160552",
                                "passenger_uuid": "0393b0f8efbad5822a857994e021f502d1bf4317263cb9547bb47e491769222a",
                                "if_preferential": "",
                                "mobile_code": "86",
                                "temporay_age60": "N",
                                "gat_born_date": "19930826",
                                "gat_valid_date_start": "",
                                "gat_valid_date_end": "",
                                "gat_version": ""
                            }],
                            "dj_passengers": []
                        },
                        "messages": [],
                        "validateMessages": {}
                    }
                """
        data = {
            JSON_ATTR: '',
            'REPEAT_SUBMIT_TOKEN': repeat_submit_token,
        }
        response = session.post(
            constants.CONFIRM_PASSENGER_GET_PASSENGER_DTOS_URL,
            headers={**headers, REFER: constants.CONFIRM_PASSENGER_INIT_DC_URL},
            data=data,
        )
        return response.json().get("data", dict()).get("normal_passengers", list())

    @staticmethod
    def check_order_info(headers: dict[str, str], data: dict[str, str]) -> None:
        """
        :param headers:
        :param data:
        :return:
            {
                "validateMessagesShowId": "_validatorMessage",
                "status": true,
                "httpstatus": 200,
                "data": {
                    "canChooseBeds": "N",
                    "canChooseSeats": "Y",
                    "choose_Seats": "MO",
                    "isCanChooseMid": "N",
                    "ifShowPassCodeTime": "1",
                    "submitStatus": true,
                    "smokeStr": ""
                },
                "messages": [],
                "validateMessages": {}
            }
        """
        session.post(
            constants.CONFIRM_PASSENGER_CHECK_ORDER_INFO_URL,
            headers={**headers, REFER: constants.CONFIRM_PASSENGER_INIT_DC_URL},
            data=urlencode(data)
        )

    @staticmethod
    def get_queue_count(headers: dict[str, str], data: dict[str, str]) -> dict:
        """
        :param headers:
        :param data:
        :return:
            {
                "validateMessagesShowId": "_validatorMessage",
                "status": true,
                "httpstatus": 200,
                "data": {
                    "count": "19",
                    "ticket": "3",
                    "op_2": "false",
                    "countT": "0",
                    "op_1": "true"
                },
                "messages": [],
                "validateMessages": {}
            }
        """
        response = session.post(
            constants.CONFIRM_PASSENGER_GET_QUEUE_COUNT_URL,
            headers={**headers, REFER: constants.CONFIRM_PASSENGER_INIT_DC_URL},
            data=urlencode(data)
        )
        return response.json()

    @staticmethod
    def confirm_for_single_queue(headers: dict[str, str], data: dict[str, str]) -> dict:
        """
        :param headers:
        :param data:
        :return:
            {
                "validateMessagesShowId": "_validatorMessage",
                "status": true,
                "httpstatus": 200,
                "data": {
                    "isAsync": "1",
                    "submitStatus": true
                },
                "messages": [],
                "validateMessages": {}
            }
        """
        response = session.post(
            constants.CONFIRM_PASSENGER_CONFIRM_SINGLE_FOR_QUEUE_URL,
            headers={**headers, REFER: constants.CONFIRM_PASSENGER_INIT_DC_URL},
            data=urlencode(data),
        )
        return response.json()

    @staticmethod
    def otn_base_data_log(headers: dict[str, str], data: dict[str, str]) -> dict:
        """
        :param headers:
        :param data:
        :return:
            {
                "validateMessagesShowId": "_validatorMessage",
                "status": true,
                "httpstatus": 200,
                "data": true,
                "messages": [],
                "validateMessages": {}
            }
        """
        response = session.post(
            constants.CONFIRM_PASSENGER_OTN_BASEDATA_LOG_URL,
            headers={**headers, REFER: constants.CONFIRM_PASSENGER_INIT_DC_URL},
            data=urlencode(data))
        return response.json()

    @staticmethod
    def query_order_wait_time(headers: dict[str, str], params: dict[str, str]) -> dict:
        """
        :param headers:
        :param params:
        :return:
            {
                "validateMessagesShowId": "_validatorMessage",
                "status": true,
                "httpstatus": 200,
                "data": {
                    "queryOrderWaitTimeStatus": true,
                    "count": 0,
                    "waitTime": -100,
                    "requestId": 7279497878826995916,
                    "waitCount": 0,
                    "tourFlag": "dc",
                    "orderId": null
                },
                "messages": [],
                "validateMessages": {}
            }
        """
        response = session.get(
            constants.CONFIRM_PASSENGER_CONFIRM_QUERY_ORDER_WAIT_TIME_URL,
            params=params,
            headers={**headers, REFER: constants.CONFIRM_PASSENGER_INIT_DC_URL},
        )
        return response.json()
