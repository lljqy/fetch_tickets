import re
import time
import base64
from pathlib import Path
from http import cookiejar

import requests
import pandas as pd
from urllib.parse import urljoin
from fake_useragent import UserAgent

from utils.common import BASE_DIR, time_print
from core.base_processor import BaseCrawlPackageProcessor
from .constants import TRAIN_TYPE_MAP, TICKET_MAP, SEAT_MAP, TIME_RANGE_MAP, DEFAULTS_CONF, REQUIRES, DEFAULT_VALUE, \
    SITE_MAP

UINT8_BLOCK = 16
SITE_MAP_REVERSE = {site_en_name: site_cn_name for site_cn_name, site_en_name in SITE_MAP.items()}


class QuickSpider:

    def __init__(self) -> None:
        self._base_url = "https://kyfw.12306.cn"
        self._session = requests.Session()
        self._init_cookies()
        try:
            self._load_cookies()
        except cookiejar.LoadError as _:
            ...

    def _init_cookies(self) -> None:
        cookies_dir = Path(BASE_DIR) / "apps" / "_12306" / "preserve"
        cookies_dir.mkdir(exist_ok=True)
        cookie_file_path = cookies_dir / "cookies.txt"
        cookie_file_path.touch(exist_ok=True)
        self._session.cookies = cookiejar.MozillaCookieJar(filename=str(cookie_file_path.absolute()))

    def _save_cookies(self) -> None:
        self._session.save(ignore_discard=True, ignore_expires=True)

    def _load_cookies(self) -> None:
        cookies_dir = Path(BASE_DIR) / "apps" / "_12306" / "preserve"
        cookies_dir.mkdir(exist_ok=True)
        cookie_file_path = cookies_dir / "cookies.txt"
        cookie_file_path.touch(exist_ok=True)
        load_cookiejar = cookiejar.MozillaCookieJar()
        load_cookiejar.load(str(cookie_file_path.absolute()), ignore_discard=True, ignore_expires=True)
        load_cookies = requests.utils.dict_from_cookiejar(load_cookiejar)
        cookies = requests.utils.cookiejar_from_dict(load_cookies)
        # 只需将读取出的cookies赋值给session.cookies，即可在后续的请求中带上之前保存的cookies啦
        self._session.cookies = cookies

    def _get_sms_code(self, user_name: str, cast_num: str, headers: dict[str, str]) -> str:
        """
        :param user_name: 登录用户名
        :param cast_num:  身份证后四位
        :return:
        """
        data = {
            "appid": "otn",
            "username": user_name,
            "castNum": cast_num
        }
        self._session.post(url=urljoin(self._base_url, "passport/web/getMessageCode"), headers=headers, data=data,
                           verify=False)
        sms_code = input("请输入手机验证码")
        return sms_code

    def _check(self, user_name: str, headers: dict[str, str]) -> None:
        data = {"appid": "otn", "username": user_name}
        self._session.post(
            url=urljoin(self._base_url, "passport/web/checkLoginVerify"), headers=headers, data=data, verify=False)

    def _login(self, user_name: str, password: str, cast_num: str, headers: dict[str, str]) -> None:
        self._check(user_name, headers)
        # 1. 获取验证码
        sms_code = self._get_sms_code(user_name, cast_num, headers)
        # 2. 登录获取cookie
        data = {
            'sessionId': '',
            'sig': '',
            'if_check_slide_passcode_token': '',
            'scene': '',
            'checkMode': '0',
            'randCode': sms_code,
            'username': user_name,
            'password': self.encrypt_password(password),
            'appid': 'otn',
        }
        # {
        # 	"result_message": "登录成功",
        # 	"uamtk": "cCuKQKnUcxB37xtQzk5Ws6Gh8EFVxuzJ5HLe-Qozl1l0",
        # 	"result_code": 0
        # }
        response = self._session.post(url=urljoin(self._base_url, "passport/web/login"), headers=headers, data=data,
                                      verify=False)
        self._session.get(url=urljoin(self._base_url, "otn/login/userLogin"), headers=headers, verify=False)
        self._session.get(url=urljoin(self._base_url, "otn/passport?redirect=/otn/login/userLogin"), headers=headers,
                          verify=False)
        self._session.cookies.set("uamtk", response.json().get("uamtk"))
        # {
        # 	"apptk": null,
        # 	"result_message": "验证通过",
        # 	"result_code": 0,
        # 	"newapptk": "B6P-HFaDHdzCH7wNPpJLDv0hNjb9pwIUfLPaVg09l1l0"
        # }
        response = self._session.post(
            url=urljoin(self._base_url, "passport/web/auth/uamtk"), headers=headers, data={'appid': 'otn'},
            verify=False)

        # {
        # 	"result_code": 0,
        # 	"result_message": "验证通过",
        # 	"username": "刘伦杰",
        # 	"apptk": "B6P-HFaDHdzCH7wNPpJLDv0hNjb9pwIUfLPaVg09l1l0"}
        data = {'tk': response.json().get("newapptk")}
        self._session.post(url=urljoin(self._base_url, "otn/uamauthclient"), headers=headers, data=data, verify=False)
        self._session.get(url=urljoin(self._base_url, "otn/login/userLogin"), headers=headers, verify=False)
        # {
        # 	"validateMessagesShowId": "_validatorMessage",
        # 	"status": true,
        # 	"httpstatus": 200,
        # 	"data": {
        # 		"is_open_updateHBTime": "Y",
        # 		"isstudentDate": false,
        # 		"is_message_passCode": "N",
        # 		"born_date": "1992-09-30",
        # 		"is_phone_check": "N",
        # 		"ei_email": "78*****52@qq.com",
        # 		"studentDate": ["2020-04-01", "2020-11-30", "2020-12-01", "2020-12-31", "2021-01-01", "2025-09-30"],
        # 		"is_uam_login": "Y",
        # 		"is_login_passCode": "Y",
        # 		"user_name": "lxpztgllj",
        # 		"is_sweep_login": "Y",
        # 		"queryUrl": "leftTicket/queryG",
        # 		"nowStr": "20240419223341",
        # 		"psr_qr_code_result": "N",
        # 		"now": 1713537221090,
        # 		"name": "刘伦杰",
        # 		"login_url": "resources/login.html",
        # 		"stu_control": 15,
        # 		"is_login": "Y",
        # 		"is_olympicLogin": "N",
        # 		"other_control": 15
        # 	},
        # 	"messages": [],
        # 	"validateMessages": {}
        # }
        self._session.post(url=urljoin(self._base_url, "otn/login/conf"), headers=headers, verify=False)
        # {
        # 	"validateMessagesShowId": "_validatorMessage",
        # 	"status": true,
        # 	"httpstatus": 200,
        # 	"data": {
        # 		"notify_way": "6",
        # 		"if_show_ali_qr_code": false,
        # 		"isSuperUser": "N",
        # 		"_email": "78*****52@qq.com",
        # 		"user_status": "1",
        # 		"_is_needModifyPassword": null,
        # 		"needEdit": false,
        # 		"member_status": "2",
        # 		"control_code": null,
        # 		"id_type_code": "1",
        # 		"user_name": "刘伦杰",
        # 		"member_level": "2",
        # 		"isCanRegistMember": false,
        # 		"user_regard": "先生,下午好！",
        # 		"resetMemberPwd": "N",
        # 		"_is_active": "Y"
        # 	},
        # 	"messages": [],
        # 	"validateMessages": {}
        # }
        self._session.post(url=urljoin(self._base_url, "otn/index/initMy12306Api"), headers=headers,
                           verify=False)
        self._save_cookies()

    def _query_left_tickets(
            self,
            from_: str,
            to: str,
            start_date: str,
            headers: dict[str, str],
            purpose_code: str = "ADULT"
    ) -> pd.DataFrame:
        if from_ not in SITE_MAP or to not in SITE_MAP:
            raise ValueError(f"‘出发地’({from_})或者‘目的地’({to})有误")
        params = {
            "leftTicketDTO.train_date": start_date,
            "leftTicketDTO.from_station": SEAT_MAP.get(from_),
            "leftTicketDTO.to_station": SEAT_MAP.get(to),
            "purpose_codes": purpose_code,
        }
        response = self._session.get(
            url=urljoin(self._base_url, "otn/leftTicket/queryG"),
            params=params,
            headers=headers)
        r = response.json()
        if r != requests.status_codes.codes.ok:
            raise RuntimeError("无法查询车次信息")
        results = r.get("data", dict()).get("result", list())
        columns = [
            "secret_str",
            "button_text_info",
            "train_no",
            "train_code",
            "start_station_telecode",
            "end_station_telecode",
            "from_station_telecode",
            "to_station_telecode",
            "start_time",
            "arrive_time",
            "time_consuming"
            "can_web_by",
            "yp_info",
            "start_train_date",
            "train_seat_feature",
            "location_code",
            "from_station_no",
            "to_station_no",
            "is_support_card",
            "controlled_train_flag",
            "gg_num",
            "gr_num",
            "qt_num",
            "rw_num",
            "rz_num",
            "tz_num",
            "wz_num",
            "yb_num",
            "yw_num",
            "yz_num",
            "ze_num",
            "zy_num",
            "swz_num",
            "srrb_num",
            "yp_ex",
            "seat_types",
            "exchange_train_flag",
            "houbu_train_flag",
            "houbu_seat_limit",
            "yp_info_new",
            "dw_flag",
            "stop_check_time",
            "country_flag",
            "local_arrive_time",
            "local_start_time",
            "bed_level_info",
            "seat_discount_info",
            "sale_time",
            "from_station_name",
            "to_station_name",
        ]
        data = [result.split("|") for result in results]
        df = pd.DataFrame(data=data, columns=columns)
        df["from_station_name"] = df["from_station_telecode"].map(SITE_MAP_REVERSE)
        df["to_station_name"] = df["to_station_telecode"].map(SITE_MAP_REVERSE)
        return df

    def _choose_train(self, headers: dict[str, str], train_info: dict[str, str]) -> None:
        # 检查用户信息
        self._session.post(urljoin(self._base_url, "otn/login/checkUser"), headers=headers, data={'_json_att': ''})
        # 选择车次对应页面提交预订按钮
        data = 'secretStr=sh4HUuBB1zEjlWbTXqkp5HtzkLW37QzFJWFBJ0u5XQYxguYi2NJ8Re3WXxI06oAXgYrXx%2BQ4xN9D%0AQXINKWISm6qyw7lAk0Uvth3nCT6RZEFu0KM6nZB4KlOm%2FgjYNesNwqZ24KXUFmOnHbOcfq1ZZrwj%0Ah5aTEunyG1luS3w%2FJJdZoidBJ2Wh98POGQrVcxt0saxBbl6wuNQfiZqH9ADYwaFO0kG3oIED8mTO%0AXISl1mh5BKtnMaAWvCxiHAGGsr8CsMtRjIzZl%2FcLfnwFtvAganpmofLdpojDZNZyxWuQuZcUPlSD%0An62XyXVvpyuVPwGlzINWZUPAkvGpdVmIOBfJnBtR4t5D5sjP&train_date=2024-04-22&back_train_date=2024-04-21&tour_flag=dc&purpose_codes=ADULT&query_from_station_name=深圳北&query_to_station_name=武汉&bed_level_info=33025453102725320263543047354104945&seat_discount_info=&undefined'.encode()
        self._session.post(urljoin(self._base_url, "otn/leftTicket/submitOrderRequest"), headers=headers, data=data)

    def _get_passengers(self, headers: dict[str, str]) -> list[dict[str, str]]:
        response = self._session.post(urljoin(self._base_url, "otn/confirmPassenger/initDc"), headers=headers,
                                      data={'_json_att': ''})
        token = re.search(r"var globalRepeatSubmitToken\s=\s\'(\w+)\'", response.text).group(1)
        data = {
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token,
        }
        response = self._session.post(
            urljoin(self._base_url, "otn/confirmPassenger/getPassengerDTOs"),
            headers=headers,
            data=data,
        )
        result = response.json()
        return result.get("data", dict()).get("normal_passengers", list())

    def _submit(self, headers: dict[str, str]) -> None:
        response = self._session.post(urljoin(self._base_url, "otn/confirmPassenger/initDc"), headers=headers,
                                      data={'_json_att': ''})
        token = re.search(r"var globalRepeatSubmitToken\s=\s\'(\w+)\'", response.text).group(1)
        data = {
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token,
        }
        response = self._session.post(
            urljoin(self._base_url, "otn/confirmPassenger/getPassengerDTOs"),
            headers=headers,
            data=data,
        )
        passengers = response.json().get("data", dict()).get("normal_passengers", list())

        data = 'cancel_flag=2&bed_level_order_num=000000000000000000000000000000&passengerTicketStr=M%2C0%2C1%2C%E5%90%B4%E7%82%80%2C1%2C4409***********112%2C158****1159%2CN%2Cfd0c5e0f2da3aff2d2804eadc99622c3371d5248e9a29e8d29d93bb5d17579daec372b0a3937f533daa808a12c14af3972694f9b735758b33d1845bb0797b64b812b20e9abcb7b8b2f8243ad2b4b3615&oldPassengerStr=%E5%90%B4%E7%82%80%2C1%2C4409***********112%2C1_&tour_flag=dc&whatsSelect=1&sessionId=&sig=&scene=nc_login&_json_att=&REPEAT_SUBMIT_TOKEN=f8c2bddedb919f67c693600053b181dc'
        response = self._session.post(urljoin(self._base_url, "otn/confirmPassenger/checkOrderInfo"), headers=headers,
                                      data=data)

        data = 'train_date=Mon+Apr+22+2024+00%3A00%3A00+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&train_no=6i000G119203&stationTrainCode=G1192&seatType=M&fromStationTelecode=IOQ&toStationTelecode=WHN&leftTicket=TV6WggpPZoyKnkpUvFgKWYANONqXMN5MKtf04aygzT%252FR8Cik&purpose_codes=00&train_location=Q6&_json_att=&REPEAT_SUBMIT_TOKEN=f8c2bddedb919f67c693600053b181dc'
        response = self._session.post(urljoin(self._base_url, "otn/confirmPassenger/getQueueCount"), headers=headers,
                                      data=data)

        data = 'passengerTicketStr=O%2C0%2C1%2C%E5%90%B4%E7%82%80%2C1%2C4409***********112%2C158****1159%2CN%2Cfd0c5e0f2da3aff2d2804eadc99622c3371d5248e9a29e8d29d93bb5d17579daec372b0a3937f533daa808a12c14af3972694f9b735758b33d1845bb0797b64b812b20e9abcb7b8b2f8243ad2b4b3615&oldPassengerStr=%E5%90%B4%E7%82%80%2C1%2C4409***********112%2C1_&purpose_codes=00&key_check_isChange=E24C1DD104C01C5246EB3A4C39D5FB8105CB256FDA0C9DE98BF5697B&leftTicketStr=dIXqS9mAxqP9Ivm%252BVus93BQgJqbOZuIKfaIrklxBf9jBzkd%252F&train_location=Q7&choose_seats=&seatDetailType=000&is_jy=N&is_cj=Y&encryptedData=H24NHlCkhz8qcS.zGF8Jqj.SMs4uMLPV0_vfrIRKn1bZPqyvPl3l4R0MdlieNAgODBhWMGPnd2dNGRfhduLhmM3CAbKcFrOsojOaNBEHsjpBpBz.zMrYI_8PITih3S8v2PbYT_TJAcQq2x.KCwbOCXLTcyTi8IC242OXhi_Q5f_lfIQ24WqKvJd1HrcLuRErnCCRGQuOilKVn.nhQCpCAVPJNS8LX63kUWnLLEHJ7ZT9U.Vu5Z0HHOFsGquNEv9jjh2ldwHR0RdBlEwfn2VgRe757jhdPpztMEQczBdlSD7eRBhSVAWrxEAHRJGdCtI4xvzx_DP6o1_K0DhOnMn_QybiSaAAuQngfnXCexZs1ngE2IZi3CGv7Cq.337CBSrJu.Xgdpqu5w.vk8fu1WmEcxuGjoTcMrFTP3dhECL7oT9.ncmYBqlo3_u7mo3hoMS_iRn6nFMoD3HvxXC5gv88TiFv.TCfJxzC3XzK84Z8HhrcsGhfll6YcCuCTk.HmNOJ3D7asVMAxY11DfU2s5fyagZHSkhCXxmXFHJdtj5QBkR9_Dm1Gx7c7vBb9EHPvR4u8EmU9xSTl_qCQykvr2AZBXu01MHHK70KwpHYmtXeKE_gBD6fWKgmVFbsOSvP5XRJPqSA.GQTBQ3sB4xIZSkSKQLAY0kua01OA2k.VhpdQ_mwR9drioOYEIDyF_7873Yxe.xW_RS6GUxGNwiUUEcA6CmQFzCycGBpPCGhpR_4l4zprZXboVlMWO.rCg9VNSbWiOOcv5RwAe_JJNHUptABrQ0ZJajRRow4K4LqWS0tl6Ll.jjaVs.sBIskHHuXFeJnfhwxS4K6hfsYwiI98UO_vGljxoNpYp87..hhAgKJon1pKiyB2Du4QXhoCTzB4MtrxAXy8gVfJGFJU2jUHj7cHJgYYEh6HP8WfUYpwbOfvGQ94JBxJZoAKb8fQTDJPV6HveXckl4MpIyKURGfOOfmvhyELDFsjyNATwRk0wiBh69lJobpNg7XAykmM0NNvYFnp5YB4vwfEdAaXBwacyuvPLuWtM2kB3164AQYulKeMaP2kWauXGNvSQ71ux_.1XWWyUGQ4_Mw79s.qcCzHgyDx7xl4zYjFTAzS4YPFT5rcQI4EBZRB10GwsPRTLp1KtZm5ff7bIFOL8HingGrVAh1wWv0gEuFPz5RORvNb6pnrovEcRV7lX6Ku3CUMc6nlg8Si3m2zLgYf6Nq3WKHZjkNwRhXJyLNaNHQmjfBdmCQcEHp1HzlSFaNDXEXkTM5MNc75beCDCLAaoJUVhFq7fcfg7Z0DBtubeBv8W81MJMsZcVGW2SMdXKIcqiNRyiLI.jgHRljcDJuKNzF6tajvSHL9aaVqIxba.xXH.aL5vshUMylaKRds8PRNxV2ZWtcQfGDetAfizCfuEgR_IKmMQ5sdJ6Qt1s8iSTijeIEviUbPfDIry1DHo1kUmNEPawndFgzFAGe1AYhGy1hxPvVId2LPQzFooGH30BupNbdDuNh7M4zam.CEtwYrKQ653.nqIWFCs5cLp8Js.nmQFz5Y5WNgqbawHTCW1xqYO.0Oxd2Ao10Lpnc1UbuKPqEBxIXCQYjddzb_gvqbWgJafsyL4IO_Ln.1gwgU13GeTaqXkkRsg3SG2CSczLV2MIL0yhuD2I92Eagba1pFWKN1MkZjfJSsCalpdr1jebSTPB4izsnMQf7rJFvoWcmwjf5sFhHXDsNJBdswc1cG0tjl_FAvJs3RCpCMdhlu5jeTX7RlVGO0hG4RhIjROc7wpRdwrMskuCJKJYnEAewRYxmj8ePSi3G2fD.8z2YIQgzD31vqNsjVDV9U2mD5EZfDtrkZL8N1HNLY85DpBd7bH_itZ7bLYxts8U6AhFz0CzXKIeU1r5gpIP7LwkFzf7EByQrHE7yEG4nfPvlDWFuWGTJtcffcB4AkGPJzdURGE_x5NAqNjd3J1Qb6LFceqHtbgvSDOqc2pO03bzbsfdjftvGoG9Syc_RTaEPwro5nkiz4ssgDadXuNKGX2BU72iJFPr_i29Z7VnIMWIr12UCIHnimTB1tPCZlxgtypTNMRfqm30mb7iFVtfR0nwa1W_Z.NVSPVVJUOcIO.UMGulgR.zM0YiT8o.92x1vnwZP5ZzppSW.Ky2FHAjGJ3QkkfGfnyYjjhMhkwQvJu9VDLd2ikWrvDuvsPDrw1lHX.VuLzhWOa0nm9AashC0iawCp8XduxPFMLAx81nh1RKyvzx30CJOR1x._3b1PulhiIgudOZpoZ.AQJiYWpH0UhQlkBW0bBNYiwOO_tUo01P_ZbL8c19Ha7Cbq_Iy8bqQ45uYulfYIrDHQmQ0100_AkRaMF.jhVJpR20mJYztYus9mEetX83i94adRDG8k3aL1U3X7Oq6e1HdQaBEts1tmWpWW2aQGFYQi_q95YTuL87e1ETi1L8VmgNkbnaPfY2WdDpPLyv0HJ5g66KPAhq9lkCAklHT3qieL6vGm3Qvd3jX1ymYWk9aUUEP5EtR3O.C.v1S1CPtftm_EW6XvnhwrL4sdDfiXkaWggaZ_9nSkPXQbZifxQG1NwRBHwNxapAo1OGlE3YKYA7XHgkglCTjPlUCbzWrDZidp7Bc_TOEcwR50uFvngs55IgS19jzQtkebtqmzih9kLfkg1e4jHV9PEynD_HL9guLk0YPg_ggQiGEFzqAPym64lGtpweATF9pA0CWrL8cLp0AAzbtvixNvnJL0FHjdODkAzkIGjdsu2THByFliIczFDQT4eRlFFs1l6CfNw1rL1cDtISNS9l&whatsSelect=1&roomType=00&dwAll=N&_json_att=&REPEAT_SUBMIT_TOKEN=649a63bb2fa8d05cd9a009fa1ef6d5f3'
        response = self._session.post(
            urljoin(self._base_url, "otn/confirmPassenger/confirmSingleForQueue"),
            headers=headers,
            data=data,
        )
        params = {
            # 当前时间戳
            # 'random': '1713714595217',
            'random': round(time.time() * 1000),
            'tourFlag': 'dc',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token,
        }
        while True:
            response = self._session.get(
                urljoin(self._base_url, "otn/confirmPassenger/queryOrderWaitTime"),
                params=params,
                headers=headers,
            )
            # {
            # 	"validateMessagesShowId": "_validatorMessage",
            # 	"status": true,
            # 	"httpstatus": 200,
            # 	"data": {
            # 		"queryOrderWaitTimeStatus": true,
            # 		"count": 0,
            # 		"waitTime": -1,
            # 		"requestId": 7187839780614394060,
            # 		"waitCount": 0,
            # 		"tourFlag": "dc",
            # 		"orderId": "E411857572"
            # 	},
            # 	"messages": [],
            # 	"validateMessages": {}
            # }
            order_id = response.json().get("data", dict()).get("orderId")
            if order_id:
                break
        data = {
            'orderSequence_no': order_id,
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token,
        }
        # {
        # 	"validateMessagesShowId": "_validatorMessage",
        # 	"status": true,
        # 	"httpstatus": 200,
        # 	"data": {
        # 		"submitStatus": true
        # 	},
        # 	"messages": [],
        # 	"validateMessages": {}
        # }
        response = self._session.post(
            urljoin(self._base_url, "otn/confirmPassenger/resultOrderForDcQueue"),
            headers=headers,
            data=data,
        )
        if response.json().get("data", dict()).get("submitStatus"):
            time_print("抢票成功")

    @staticmethod
    def _unsigned_right_shift(num: int, shift: int) -> int:
        # 先转换为正数
        positive_num = num + (1 << 32) if num < 0 else num
        # 右移
        shifted = positive_num >> shift
        # 转换回32位无符号整数
        return (shifted - (1 << 31)) if shifted > (1 << 31) - 1 else shifted

    @staticmethod
    def _js_bit_xor(a: int, b: int) -> int:
        bit_limit = 32
        bit_length_a, bit_length_b = a.bit_length(), b.bit_length()
        value = a ^ b
        if bit_length_a < bit_limit and bit_length_b < bit_limit:
            return value
        compensate_code = format(value, "064b")
        coe = 1 if value > 0 else -1
        bit_code = compensate_code[-32:]
        if bit_code[0] == "0":
            return int(bit_code, base=2) * coe
        bit_code = "".join(["0" if bit == "1" else "1" for bit in bit_code])
        return -(int(bit_code, base=2) + 1) * coe

    @staticmethod
    def _js_right_bit(num: int, steps: int) -> int:
        if num > 0:
            compensate_code = format(num, "032b")
        else:
            bit_code = format(-num, "032b")
            reversed_bit_code = "".join(["0" if bit == "1" else "1" for bit in bit_code])
            reversed_compensate_value = int(reversed_bit_code, base=2)
            reversed_compensate_value += 1
            bit_code = format(reversed_compensate_value, "032b")
            compensate_code = "1" + bit_code[1:]
        code = (compensate_code + "0" * steps)[-32:]
        if code[0] == "0":
            return int(code, base=2)
        code = "".join(["0" if bit == "1" else "1" for bit in code])
        return -(int(code, base=2) + 1)

    def _tau_transform(self, a: int) -> int:
        s_box = [214, 144, 233, 254, 204, 225, 61, 183, 22, 182, 20, 194, 40, 251, 44, 5, 43, 103, 154, 118, 42, 190, 4,
                 195,
                 170, 68, 19, 38, 73, 134, 6, 153, 156, 66, 80, 244, 145, 239, 152, 122, 51, 84, 11, 67, 237, 207, 172,
                 98, 228,
                 179, 28, 169, 201, 8, 232, 149, 128, 223, 148, 250, 117, 143, 63, 166, 71, 7, 167, 252, 243, 115, 23,
                 186, 131,
                 89, 60, 25, 230, 133, 79, 168, 104, 107, 129, 178, 113, 100, 218, 139, 248, 235, 15, 75, 112, 86, 157,
                 53, 30,
                 36, 14, 94, 99, 88, 209, 162, 37, 34, 124, 59, 1, 33, 120, 135, 212, 0, 70, 87, 159, 211, 39, 82, 76,
                 54, 2,
                 231, 160, 196, 200, 158, 234, 191, 138, 210, 64, 199, 56, 181, 163, 247, 242, 206, 249, 97, 21, 161,
                 224, 174,
                 93, 164, 155, 52, 26, 85, 173, 147, 50, 48, 245, 140, 177, 227, 29, 246, 226, 46, 130, 102, 202, 96,
                 192, 41,
                 35, 171, 13, 83, 78, 111, 213, 219, 55, 69, 222, 253, 142, 47, 3, 255, 106, 114, 109, 108, 91, 81, 141,
                 27,
                 175, 146, 187, 221, 188, 127, 17, 217, 92, 65, 31, 16, 90, 216, 10, 193, 49, 136, 165, 205, 123, 189,
                 45, 116,
                 208, 18, 184, 229, 180, 176, 137, 105, 151, 74, 12, 150, 119, 126, 101, 185, 241, 9, 197, 110, 198,
                 132, 24,
                 240, 125, 236, 58, 220, 77, 32, 121, 238, 95, 62, 215, 203, 57, 72]
        return (self._js_right_bit(s_box[a >> 24 & 0xff], 24) | self._js_right_bit(s_box[a >> 16 & 0xff], 16)
                | self._js_right_bit(s_box[a >> 8 & 0xff], 8) | s_box[a & 0xff])

    def _rotate_left(self, x: int, y: int) -> int:
        return self._js_right_bit(x, y) | self._unsigned_right_shift(x, 32 - y)

    def _t_transform1(self, a: int) -> int:
        b = self._tau_transform(a)
        ans = b
        for y in (2, 10, 18, 24):
            ans = self._js_bit_xor(ans, self._rotate_left(b, y))
        return ans

    def _t_transform2(self, a: int) -> int:
        b = self._tau_transform(a)
        ans = b
        for y in (13, 23):
            ans = self._js_bit_xor(ans, self._rotate_left(b, y))
        return ans

    def _encrypt_round_keys(self, key: list[int]) -> list[int]:
        keys = list()
        mk = [self._js_right_bit(key[0], 24) | self._js_right_bit(key[1], 16) |
              self._js_right_bit(key[2], 8) | key[3],
              self._js_right_bit(key[4], 24) | self._js_right_bit(key[5], 16) |
              self._js_right_bit(key[6], 8) | key[7],
              self._js_right_bit(key[8], 24) | self._js_right_bit(key[9], 16) |
              self._js_right_bit(key[10], 8) | key[11],
              self._js_right_bit(key[12], 24) | self._js_right_bit(key[13], 16) |
              self._js_right_bit(key[14], 8) | key[15]]
        before, after = 4, 32
        k = [0] * (before + after)
        fk = [2746333894, 1453994832, 1736282519, 2993693404]
        ck = [462357, 472066609, 943670861, 1415275113, 1886879365, 2358483617, 2830087869, 3301692121, 3773296373,
              4228057617, 404694573, 876298825, 1347903077, 1819507329, 2291111581, 2762715833, 3234320085, 3705924337,
              4177462797, 337322537, 808926789, 1280531041, 1752135293, 2223739545, 2695343797, 3166948049, 3638552301,
              4110090761, 269950501, 741554753, 1213159005, 1684763257]
        for index in range(before):
            # k[index] = self._py_num_to_js_num(mk[index] ^ fk[index])
            k[index] = self._js_bit_xor(mk[index], fk[index])
        for index in range(after):
            params = 0
            for value in (k[index + 1], k[index + 2], k[index + 3], ck[index]):
                params = self._js_bit_xor(params, value)
            k[index + 4] = self._js_bit_xor(k[index], self._t_transform2(params))
            keys.append(k[index + 4])
        return keys

    def _padding(self, original_buffer: list[int]) -> list[int]:
        if not original_buffer:
            return list()

        padding_length = 16 - len(original_buffer) % UINT8_BLOCK
        original_buffer.extend([padding_length] * padding_length)
        padded_buffer = original_buffer
        return padded_buffer

    def _get_chain_block(self, arr: list[int], base_index: int = 0) -> list[int]:
        return [self._js_right_bit(arr[base_index], 24) | self._js_right_bit(arr[base_index + 1], 16) |
                self._js_right_bit(arr[base_index + 2], 8) | arr[base_index + 3],
                self._js_right_bit(arr[base_index + 4], 24) | self._js_right_bit(arr[base_index + 5], 16) |
                self._js_right_bit(arr[base_index + 6], 8) | arr[base_index + 7],
                self._js_right_bit(arr[base_index + 8], 24) | self._js_right_bit(arr[base_index + 9], 16) |
                self._js_right_bit(arr[base_index + 10], 8) | arr[base_index + 11],
                self._js_right_bit(arr[base_index + 12], 24) | self._js_right_bit(arr[base_index + 13], 16) |
                self._js_right_bit(arr[base_index + 14], 8) | arr[base_index + 15]]

    def _do_block_crypt(self, block_data: list[int], round_keys: list[int]) -> list[int]:
        x_block = [0] * 36
        for index, val in enumerate(block_data):
            x_block[index] = val
        for index in range(32):
            params = 0
            for value in (x_block[index + 1], x_block[index + 2], x_block[index + 3], round_keys[index]):
                params = self._js_bit_xor(params, value)
            x_block[index + 4] = self._js_bit_xor(x_block[index], self._t_transform1(params))
        y_block = [x_block[35], x_block[34], x_block[33], x_block[32]]
        return y_block

    def encrypt_password(self, password: str, key: str = "tiekeyuankp12306", mode: str = "base64") -> str:
        key_array = list(map(lambda x: ord(x), key))
        encrypt_round_keys = self._encrypt_round_keys(key_array)
        plain_byte_array = list(map(lambda x: ord(x), password))
        padded = self._padding(plain_byte_array)
        block_times = (len(padded) + UINT8_BLOCK - 1) // UINT8_BLOCK
        out_array = list()
        for index in range(block_times):
            round_index = index * UINT8_BLOCK
            block = self._get_chain_block(padded, round_index)
            cipher_block = self._do_block_crypt(block, encrypt_round_keys)
            for l in range(UINT8_BLOCK):
                out_array.append(cipher_block[int(l / 4)] >> (3 - l) % 4 * 8 & 0xff)
        if mode == "base64":
            byte_array = bytearray(out_array)
            return "@" + base64.b64encode(byte_array).decode("utf-8")
        return "@" + "".join(map(lambda x: chr(x), out_array))

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Host": "kyfw.12306.cn",
            "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": UserAgent().chrome,
            "sec-ch-ua-platform": "\"Windows\"",
            "Origin": "https://kyfw.12306.cn",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://kyfw.12306.cn/otn/resources/login.html",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }

    def run(self):
        headers = self.headers
        self._login("", "", "", headers)
        df_train_infos = self._query_left_tickets("深圳北", "武汉", "2024-04-26", headers)
        self._choose_train(headers, df_train_infos.to_dict(orient="records")[0])
        self._submit(headers)
