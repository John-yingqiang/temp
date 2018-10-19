TOGET = 1
GOT = 5
            # INEFFECTIVE = 10
            # UNUSE = 15
EXPIRE = 20
USING = 25
USEFAILED = 30
USED = 35


status_str = {
TOGET: '去领取',
GOT: '已领取',
                # INEFFECTIVE: '待生效',  # 前端动态显示
                # UNUSE:  '去使用',
EXPIRE: '已失效',
USING: '使用中',
USEFAILED: '重新使用',  # 等效于未使用
USED: '使用成功',

    # PENDING: '未提交',
    # APPROVING: '审核中',
    # APPROVED: '审核通过',
    # REJECTED: '审核拒绝',
    # CANCELLED: '已取消',
    # SIGNING: '签约中',
    # SIGN_FAILED: '签约失败',
    # FUNDING: '放款中',
    # FUND_ERROR: '放款失败',
    # FUNDED: '待还款',
    # REPAYING: '还款中',
    # REPAID: '已还清'
}