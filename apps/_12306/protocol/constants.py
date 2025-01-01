from enum import Enum
from urllib.parse import urljoin

BASE_URL = "https://kyfw.12306.cn"

# page url
LOGIN_PAGE_URL = urljoin(BASE_URL, "otn/resources/login.html")
INDEX_PAGE_URL = urljoin(BASE_URL, "otn/view/index.html")
REDIRECT_LOGIN_PAGE_URL = urljoin(BASE_URL, "otn/passport?redirect=/otn/login/userLogin")
LEFT_TICKETS_INIT_URL = urljoin(BASE_URL, "otn/leftTicket/init?linktypeid=dc")

# login references
# password login
CHECK_LOGIN_VERIFY_URL = urljoin(BASE_URL, "passport/web/checkLoginVerify")
MESSAGE_CODE_URL = urljoin(BASE_URL, "passport/web/getMessageCode")
PASSPORT_LOGIN_URL = urljoin(BASE_URL, "passport/web/login")
# ORCode login
PASSPORT_CREATE_QR64_URL = urljoin(BASE_URL, "passport/web/create-qr64")
PASSPORT_CHECK_QR_URL = urljoin(BASE_URL, "passport/web/checkqr")
# common login
USER_LOGIN_URL = urljoin(BASE_URL, "otn/login/userLogin")
OTN_PASSPORT_REDIRECT_URL = urljoin(BASE_URL, "otn/passport?redirect=/otn/login/userLogin")
PASSPORT_AUTH_UAMTK_URL = urljoin(BASE_URL, "passport/web/auth/uamtk")
UAM_AUTH_CLIENT_URL = urljoin(BASE_URL, "otn/uamauthclient")
OTN_CONF_URL = urljoin(BASE_URL, "otn/login/conf")
INIT_MY_12306_API_URL = urljoin(BASE_URL, "otn/index/initMy12306Api")

# query tickets references
LEFT_TICKET_URL = urljoin(BASE_URL, "otn/leftTicket/queryG")
LC_QUERY_URL = urljoin(BASE_URL, "lcquery/queryG")
CHECK_USER_URL = urljoin(BASE_URL, "otn/login/checkUser")
SUBMIT_ORDER_REQUEST_URL = urljoin(BASE_URL, "otn/leftTicket/submitOrderRequest")

# order tickets references
CONFIRM_PASSENGER_INIT_DC_URL = urljoin(BASE_URL, "otn/confirmPassenger/initDc")
CONFIRM_PASSENGER_GET_PASSENGER_DTOS_URL = urljoin(BASE_URL, "otn/confirmPassenger/getPassengerDTOs")
CONFIRM_PASSENGER_CHECK_ORDER_INFO_URL = urljoin(BASE_URL, "otn/confirmPassenger/checkOrderInfo")
CONFIRM_PASSENGER_GET_QUEUE_COUNT_URL = urljoin(BASE_URL, "otn/confirmPassenger/getQueueCount")
CONFIRM_PASSENGER_OTN_BASEDATA_LOG_URL = urljoin(BASE_URL, "otn/basedata/log")
CONFIRM_PASSENGER_CONFIRM_SINGLE_FOR_QUEUE_URL = urljoin(BASE_URL, "otn/confirmPassenger/confirmSingleForQueue")
CONFIRM_PASSENGER_CONFIRM_QUERY_ORDER_WAIT_TIME_URL = urljoin(BASE_URL, "otn/confirmPassenger/queryOrderWaitTime")
CONFIRM_PASSENGER_CONFIRM_RESULT_ORDER_FOR_DC_QUEUE_URL = urljoin(
    BASE_URL,
    "otn/confirmPassenger/resultOrderForDcQueue"
)

# tickets page
TICKETS_TABLE_COLUMNS = [
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
    "time_consuming",
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
    "sale_time"
]


class ResponseCodes(Enum):
    LOGIN_SUCCESS = "2"
    SUCCESS = 0
    FAIL = 1


class LoginMethods(Enum):
    PASSWD = "PASSWD"
    QR_CODE = "QR_CODE"
