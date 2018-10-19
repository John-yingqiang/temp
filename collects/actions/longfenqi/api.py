import json
from django.utils import timezone
import requests
from .utils import createSign, RSAEncrypt, RSADecrypt
import bson

# test
# PUHUI_PUBLIC_KEY = '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvnVB6yXhsYZiP5L9DcYQ\nGtcHJu9SofJPaZDifcqVYcWBFxiT8mYWJMysG95OViQ37nQDg8XwFFMUqGmgJaPh\nz0Wm8OfN3tyiaETCobYS0UyL2qLd0sLLaKnB0BAePfGBLbnNlyhhSj8aTEv8GUfJ\nziViy1C+5H9ItT1yR/TGbXgH2gtZAhW2YYcwS3Ko3/UZLC2xq/jY88UOr86ccBwt\n2A98XppcWtGMr4+0CcqPGISH1438MSI07f1NGUYUc+AgcbzJy61ZSMtdw3pFOuXd\niVAuHgsCUisDCIOfBmpsDbR5QBwv48b6mivirns/rgDnNuThmREhm0L8L7+m3QMK\nEwIDAQAB\n-----END PUBLIC KEY-----\n'
# APP_PRIVATE_KEY = '-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC6aXnKAmpwR1kF\nBRMAMyeAyTt4C28AmKQQnUCeYJ7oMAeDUGBgQ5EGs0ilAO2pIeUDHQoy6ciMNw8R\nuGRjxgmCNi585JzdFZnGbIhgFRxymBfiNQxc6A7bqXdMML9HtxpzoRbVRIUS28v6\nWI1xf761TKsurQfP2tglD3QmQQFrL7zWwlRo40MrkNXIPWiTUaQ4PVwobV1Ev4bM\neQ8Eb1MEObnVODuUCHSg2VpIVdp4tmY2bOd5AYcYZTesVBaoyZSmYr22Jvk8yJU7\nCJHlUEFBKqVzOKRro5H+mzK1fWk8tl6CyCA2rU3CDmMOQSTMXwWtmkPH5snS6qW2\np2BxSvcxAgMBAAECggEAS8zB+jO7Rkas2w6yKD2kzYiGRw0XKP3okNzwvrX5R97n\n3yya0+oFmdzjKD1VZpXiwr5XPFa19tYYqZL6N1v619jiVGS9qGS1L+tIFRHgjHRu\nGcyKZ2jxSb8CRJf539aDygrx9uyy0/VOX1EMyt8wFBbF8OfpKksJ4yACkd+TDRsd\nV1C/KEjnGieg/MR8kUBCvjy079VhsBeGjI0YLOdSq3ypCQ5mZaJ6c7uLqKCr3sLm\nBXUt8EqELKLIxEe3pI3ED10XXy3JBkHCr0zlKDtjzypF7oE1NJzAOeOys6cDq46l\nDKj+Z0q89IpQh+XySaB4cH66cwuaa+JYfilTeCFNcQKBgQDm3aQ2PXS788zPP9+N\nvWVsaWu7ovOFDjD1ywM6sAxC+zjuDGvJ4ezprnKUI/7DcAVV3tsN4VWJ9UfdkWy5\n9b1Yxg8gOCXz+m/4ymeebrdxZMWCuT8XPLMufReG6FSCBwWpyH0M25c0ySb0r8Mx\n0IRSzD1u4Bg0BQYYHucJraiE/QKBgQDOtOH/JoDLuGNOqb6CxtBF7KlYi5oMuf+s\n2pO/Cr1iweTE7Zsj0Q0G1o/u+hkMG3vilWJ/E6gkTQScmYe7QwidslbpqJF6pgYa\nQ3awME1JTJswkkU2yRLUPXQ36CgJFfx5otMSgfi1lQie1Me5aEidN+KyZs/s8tJn\nLoF4BF1LRQKBgQCdio4ufU2VnM8cdmflX2NA0ce0qYQoPgDnGfxAJjaX1ruIpm0/\nvK5g4KxLryyAzYa2jHdLR4OJuxmpdz2MwMbPN4jG4cn0befPDMAc+0yvUqb9h9An\n2UIk7TQK2awhdw1ESQ4cohTS7plozDAVZEeIANvDN6UMiokYGK5sila/OQKBgCcp\nHae5I610wVulzPH5uHuG2o5r5EOE+WtF/bez0S1kjnLAkSO39z/UZnBf8V7Z1h6X\nLpHkp3Y5ISaJ760KhhdaMh0SUn1p9r4DCflXLU01tjD9hR9b+LU870eoM+2EvNBO\niK548SV1lqyAo1X868TdUZV65Ol/F1108hJKwWIBAoGAOI/8SWVsuNOwbIcj6Kz7\nacrWTMvvyqtowzKlR1LrEC3PmEx91jjjAGhv94wNn+DYR/9E58Y2rF3dsaUqbhac\nNfXvQU6dHrNW0+p/M/+3xfQhS7zvDfdirQitzPZZiDA3G9DDFve+E+hO2bLmDdXW\nailtDAUPbBLUI0+3nqnNELI=\n-----END PRIVATE KEY-----\n'
# capitalSideId = "3341876"
# productId = "200000004"
# url = 'http://tapi.xiaoshushidai.cn/partner-push_deal'

# pro
PUHUI_PUBLIC_KEY = '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAskdWipKKlcHz7s4Wpfuq\nyDT1C+1sh7o30ykwqBwlC/XhSHu3cImOfu3TMdLFjF1WNWV3yDEzlwmk3e/yIL0N\nLjAcRJi4qDpNg7zJlVsSGQZKOFSpnEIG0FJUe871I/YScvuN5xKxjSyRIcd1/q8J\n+go9ZTxMuKb/obd1ivQnWZjYmcbtKsLCvV1pk/gHJ7oCiKH5402owGVgIu1Q9zy7\nzAiN9gvVbx//qgOs3m0fDIdQW5bl0yfjRW6Z7p/U5kQcSQAJUtW2ui6uFR/wF/Kk\n4iVgcqH4tGnowAKQeXINGmXNZSWLH84cnhE/AcI6M5qqqmF7+/zXijTKJd+b5qAz\n3QIDAQAB\n-----END PUBLIC KEY-----\n'
APP_PRIVATE_KEY = '-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC9TsfE73mUdljC\niQ35h3sMf0UQf3SKWYDBD9nFGIJT7+TlnO/rGjXEmDxrau0bK5TNpAy4qBhEv/YQ\nAgrZilXvXvi+zas9CP1FZP+zfpWVY2dlK1LYqVy6jHumnHWjjnMEEKcGHsAt4nGV\nzQ/CBvJRmQIGR4bbhPHkUdLZk77F+RyCpQMasNDTAoDeDB3oRkSwK7IyLuEyeikq\ndRoI1OaYe0T4X0ALKBlyKa99jR8BJjQ07L14jTz5tnPOBg3rxMhy54avWPVW1fFs\nzzEVnyUI3nTwc80wgFwIxqHYmxCOmiQzSS9aHZaOVKb0iPagd9Jd6sPzgaZethkI\nkZRIwIlJAgMBAAECggEAO4NXxC6w3x5xev7ROOABrAUatjwLbC8FDiyofpDc7/xb\nzl+PAS8lNh/R5scfsUn7JsbrBOY7cumSNqgdtxQJPg5yTrGjorV/weAljs09w1AT\nwjdjfR+JOlBN0ywew4NV3zJI/+CM9B/bK4fi61F5vnNGsqir2bkqvmeGzMXo1J2X\niyi8AEK11FBssfOaiVJkHD7SdbJ1lLk0V3p3/YkUL+PNj6Fa8t1+SN+7u9eeCEkM\n93SHwLP2ez5tRatiJ4WRkHjI6q84Q88/+lwSTMQA+vBCPPwIyaXTNaubpuwpd3+K\nYZ0GlDfx4h1AJEe6zcb1g9AaEEog4MImWhMopCG2AQKBgQD4nSciMcEqcGnepB+O\nL+P20G+7VAGR93QnsxOa4gpH2reTu5tl03Dqi+q0aI6LnViuItPLcdaCaqGrd2jd\nYN9c9p/sENMGBkZvtl3ggc/TIIjFejn71TbB62SqUfHDX9rvxrTydNvDye1oE3/k\nmo/X+Js+/Uqsfxtm3FOVKwjXCQKBgQDC7pI6tUmVbJhye7mi2zNnzD1aecS/GzrG\nhjgW6j3ky8Fpsvf7al5KSvQV44l+NK9NVIRvS8PfXDzZFifL/2Mza/LLxKerm8PV\nJDhfnTZKzQute7CLitgfcgBy1C+AzUUNa0HErU/DaKC4477qKykO//YriA+44+DV\n+t6sL35wQQKBgEJyXj85ZRNesC0dWIG8MwWIeBRtQ24r4ROrPRYsS+sgfegyQDpa\n5NcLRlOpjk+qYkVIcaryZg69STB23cQtXAWQtPV3Ga+GhdTdvQGAMHeRPnzpSg4Q\n0m3J6EHNXPyG5hEn3rzels4hbh5e99O1q7RhcbzIHek0n7JCOOSpd9dhAoGARJVP\nmZxDAXGtyUnCrIvW8EQpqfWBxYM9ELAUd+t+T0tpB1lSaoCoIBdy/WiK7X531wtP\ndSEBD0sSlYZ4BgwayPLH/+122Kf7JLiTpQBZI8Q0wZrtKIt3MskXY09IT1bpXqlI\nAHzBvYzIT4TBnP4GeiKQaAx9C54RcvfK9GXZZIECgYAcTaOUaHPESBL4NJMofOM4\n44x5fr/SAdH5GrgxvGQnedv3fi/+9GswQHwZoxB0MrQlyn+Gcsqbpq4+qpL6oFMD\ndbMRWcmFhR9xC92x1rVY9sVWA0dw0lgoihhvUfs7crqWkYcmsdzf/ig6AdyxdFdx\npDe/ofogtTYLsna5IhTXFQ==\n-----END PRIVATE KEY-----\n'
capitalSideId = "200952233"
productId = "200000004"
url = 'https://t-mapi.xiaoshushidai.com/partner-push_deal'

headers = {
    "Content-Type": "application/json;charset=utf-8",
    "rft-key": capitalSideId,
    "rft-token": productId,
}

MD5_KEY = capitalSideId + productId


def send_long_fen_qi(number, username, identification, amount, period):
    loan_data = {}
    loan_data['capitalSideId'] = capitalSideId
    loan_data['productId'] = productId
    loan_data['loanId'] = str(bson.ObjectId())

    loan_data['customerName'] = username
    loan_data['mobilePhone'] = number
    loan_data['identifier'] = identification
    loan_data['applyAmount'] = amount
    loan_data['applyPeriod'] = period
    sign = createSign(loan_data, MD5_KEY)
    loan_data['sign'] = sign
    en_data = RSAEncrypt(loan_data, PUHUI_PUBLIC_KEY)
    response = requests.post(url, data=en_data, headers=headers)
    res_data = response.text

    decrypted = RSADecrypt(res_data, APP_PRIVATE_KEY)
    url_res = json.loads(decrypted)

    # print('sign', createSign(url_res, MD5_KEY), url_res['sign'])
    if str(url_res['retData']['orderStatus']) == '1':  # 保存成功
        return {'ios': url_res['retData']['iosUrl'], 'android': url_res['retData']['appDownloadUrl']}
    else:
        return {}
