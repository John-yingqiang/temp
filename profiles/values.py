from common.functions import DictEnum


credit_cases_dict = {
    'identification': 'identification',
    'number': 'number',
    'zhima': 'zhima',
    'shebao': 'shebao',
    'gongjijin': 'gongjijin',
    'xuexin': 'xuexin',
}

credit_cases = DictEnum(credit_cases_dict)


credit_result = {
    'AAA': {
        'rank': 8,
        'level': 'AAA',
        'limit': '任性',
        'desc': '一览众山小'
    },
    'AA': {
        'rank': 7,
        'level': 'AA',
        'limit': '50万',
        'desc': '信用极好'
    },
    'A': {
        'rank': 6,
        'level': 'A',
        'limit': '20万',
        'desc': '优秀'
    },
    'BBB': {
        'rank': 5,
        'level': 'BBB',
        'limit': '50000',
        'desc': '哎呦不错哦'
    },
    'BB': {
        'rank': 4,
        'level': 'BB',
        'limit': '10000',
        'desc': '中规中矩'
    },
    'B': {
        'rank': 3,
        'level': 'B',
        'limit': '3000',
        'desc': '继续加油'
    },
    'C': {
        'rank': 2,
        'level': 'C',
        'limit': '500',
        'desc': '仍需努力'
    },
    'D': {
        'rank': 1,
        'level': 'D',
        'limit': '暂无额度',
        'desc': '有待提升'
    },
}

"""
auth status

1   已提交
10  已认证
11  认证失败
13  认证过期

"""

# 信用币
coin_num_cases = {
    # 信用认证
    'identification': 20,
    'number': 20,
    'zhima': 50,
    'shebao': 50,
    'gongjijin': 50,
    'xuexin': 50,
    # 邀请好友
    'share_register': 10,  # A邀请B，给A增加，可以无限次
    'share_register_from': 10,  # A邀请B，给B增加，一个 id 只能加一次
    'share_loan': 50,   # 好友成功借款，仅第一次生效
    'share_creditCard': 50,  # 好友成功申请信用卡，仅第一次生效
    # 社区
    'shequ_hot': 10,  # 设为热门
    'shequ_jinghua': 20,  # 设为精华
    'shequ_shang': 100,  # 悬赏、打赏
    # 签到
    'sign': 3,  # 签到单独处理，随机1-5个
    'birthday': 100,  # 生日当天签到
    # 业务,对接api申请
    'loan': 100,  # 成功借款
    'creditCard': 200,  # 成功申请信用卡
    'add_id': 1  # 通过红包奖励获得，动态
}

# 存储用过的 redis key

# 签到
sign_history_key = 'sign_history_key'  # 用户签到redis存储key

# 3.6
# 信用分
auth_scores = {
            'identification': 100,
            'jie_profile': 100,
            'bank': 100,
            'number': 150,
            'gps': 30,
            'contacts': 50
        }

auth_uids = {
            'identification': 150,
            'profile':  100,
            'number': 200,
            'gps': 10,
            'contacts': 10,
            'download_product': 50,
            'share_day': 1,
        }
