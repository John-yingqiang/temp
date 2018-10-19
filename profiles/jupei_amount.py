import random
from scipy import integrate


def fun(x):
    return 1 / (2 * (1 + x ** 1.3))


def get_amount(n, amount_now):
    """
    n = 1，返回19元
    n = 200次 返回2分钱
    n = 2000次 总额达到90元
    :param n: 次数
    :param amount_now: 用户当前总额
    :return:
    """
    if amount_now > 9500:
        return 0

    amount = integrate.quad(fun, n, n + 1)[0] * 5000
    if amount > 50:
        a = random.randint(0, 20)
        amount -= a

    if amount < 1:
        amount = 1

    return int(amount)
