

coupon_section_choices = (('C', '信用权益'), ('loan', '借款券'))

UI_conf_keys = [
  "news_coupon",
  "banner_coupon",
  "category_coupon_credit",
  "category_coupon_register",
  "category_coupon_birthday"
]

UI_conf = {
    "news_coupon": {
        "up": 0
    },
    "banner_coupon": {
        "up": 16
    },
    "category_coupon_credit": {
        "up": 16,
        "event_action": {
            "params": {
                "is_new_register": False
            },
            "name": "信用权益"
        },
        "desc": "更多",
        "num": 4,
        "section_title": "信用权益"
    },
    "category_coupon_register": {
        "up": 16,
        "event_action": {
            "params": {
                "is_new_register": True
            },
            "name": "新人专享"
        },
        "desc": "更多",
        "num": 2,
        "section_title": "新人专享"
    },
    "category_coupon_birthday": {
        "up": 16,
        "event_action": {
            "params": {
                "is_birthday": True
            },
            "name": "生日特权"
        },
        "desc": "更多",
        "num": 2,
        "section_title": "生日特权"
    }
}

coins_rules = {
    "pic": "https://platplat.oss-cn-shanghai.aliyuncs.com/coupons/image/1951516155605_.pic_hd.jpg",
    "rule_list": [
        "信用币是您的财富哦，可以兑换话费、节日礼品、免息券等许多福利！信用等级越高的用户，越有机会获取更多的信用币。",
        "登录 App 后，首先来领一下信用币，我们也会不断更新对应的礼品。新注册用户、在生日当天、还有特殊的日子里，更会有我们自己都想不到的重大活动！重要活动，只在那几天有效啊。",
        "怎么获取信用币呢？首先是签到，每天都能获取，信用等级越高的用户，获取的越多。然后是申请借款，申请信用卡，参与金融活动，还有在特殊活动里获取信用币大礼包！",
        "还有获取信用币的方法，就是系统会弹出信用币让你领取，看你的信用等级和在App里的活跃度啦！"
    ]
}
