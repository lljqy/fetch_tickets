# 配置文件动态加载项
CONF_ITEMS = {
    "12306": {
        "login": ("username", "password", "is_show_browser", "id_card_last_four_number"),
        "cookie_info": ("from", "to", "start_date"),
        "scheduler": ("fetch_start_time",),
        "order_item": ("order",),
        "user_info": ("users",),
        "train_info": ("train_types", "start_time_range"),
        "ticket_info": ("ticket_type",),
        "confirm_info": ("seat_type", "no_seat_allow"),
        "url_info": ("ticket_url", "login_url", "init_url", "buy_url", "pay_url"),
        "path_info": ("driver_name",),
    },
}
