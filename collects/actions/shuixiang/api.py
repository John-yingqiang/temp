import requests
import json
from utils import AESENCRYPT

appid = "HFKFHKH423412KLK"
aeskey = 'AmCILBEADCgkHhDK'

class SendShuiXiangAPI(object):
    '''
    水象接口
    '''


    def __init__(self, appid, aeskey):
        self.base_url = "http://106.15.126.217:8092/beadwalletloanapp/sxyDrainage/jqks"
        self.headers = {"Content-Type": "application/json;charset=utf-8"}
        self.app_id = appid
        self.encrypt = AESENCRYPT(aeskey)

    def send(self, url, data):
        json_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        encontent = self.encrypt.encrypt(json_data)

        body = {"appId": self.app_id, "request": encontent}
        response = json.loads(requests.post(url, json.dumps(body), headers=self.headers).text)
        #response = json.loads(self.encrypt.decrypt(requests.post(url, json.dumps(body), headers=self.headers).text))

        return response

    # 准入
    def send_zhunru(self, name, id_card, phone):
        url=self.base_url + "/checkUser.do"
        data = {
            "name": name,
            "idCard":id_card,
            "phone":phone
        }

        #测试数据
        data = {
            "idCard": "510121199401011122",
            "name": "张三一",
            "phone": "18888888889"
            }
        return self.send(url, data)

    # 预绑卡
    def send_preband_card(self, phone, id_card, name, bank_card_no, bank_code, bank_phone):
        url = self.base_url + "/saveBindCard.do"
        data = {
                "phone":phone,
                "idCard":id_card,
                "name":name,
                "bankCardNo":bank_card_no,
                "bankCode":bank_code,
                "bankPhone":bank_phone
            }

        #测试数据
        data={
            "phone": "15727150000",
            "name": "王子杰",
            "id_card": "421127199510211517",
            "bankcardNO": "6215581818002985950",
            "bankPhone":"15727150000",
            "bankCode":"ICBC"
        }

        return self.send(url, data)

    # 确认绑卡
    def send_ensure_card(self, phone, verify_code):
        url = self.base_url + "/saveBindCardCode.do"
        data = {
            "phone":phone,
            "verifyCode": verify_code
        }

        #测试数据
        data = {
            "phone": "15727150000",
            "verifyCode": "123456"
        }
        return self.send(url, data)

    # 进件推送
    def send_push_file(self, basic, company, identify, operator, device, contacts=None, extend=None):
        data = {}
        url = self.base_url + "/saveOrder.do"
        if isinstance(basic, dict):
            data["basicInfo"] = basic
        if isinstance(company, dict):
            data["company"] = company
        if isinstance(identify, dict):
            data["identifyInfo"] = identify
        if isinstance(operator, dict):
            data["operator"] = operator
        if isinstance(device, dict):
            data["deviceInfo"] = device
        if isinstance(contacts, list):
            data["contacts"] = contacts
        if isinstance(extend, dict):
            data["extendInfo"] = extend

        #测试数据
        data = {
                "orderNo": "2235646124",
                "basicInfo": {
                    "applyDate": "2018-03-01 08:06:05",
                    "colleagueName": "xx",
                    "colleaguePhone": "13888888888",
                    "desc": "消费",
                    "email": "123456@163.com",
                    "firstName": "xx",
                    "firstPhone": "13888888881",
                    "friend1Name": "xxx",
                    "friend1Phone": "13888888882",
                    "friend2Name": "xxx",
                    "friend2Phone": "13888888883",
                    "haveCar": 1,
                    "haveHouse": 1,
                    "houseAddress": "xxxxxx",
                    "idCard": "232638198509188762",
                    "loanAmount": 1000000,
                    "marriage": 1,
                    "name": "王五一",
                    "phone": "18888888888",
                    "qqchat": "1231461",
                    "secondName": "xxx",
                    "secondPhone": "13888888884",
                    "wechat": "461321321a"
                },
                "companyInfo": {
                    "companyName": "xxxx",
                    "income": "1234",
                    "industry": "A",
                    "jobTime": "2"
                },
                "contacts": [
                    {
                        "name": "xxx",
                        "phone": "13888888884"
                    },
                    {
                        "name": "xxx",
                        "phone": "13888888882"
                    }
                ],
                "deviceInfo": {
                    "devicetype": "",
                    "idfa": "",
                    "imei": "",
                    "ip": "",
                    "isroot": "",
                    "latitude": "",
                    "applist": "",
                    "longitude": "",
                    "mac": ""
                },
                "identifyInfo": {
                    "address": "武汉xxx",
                    "backFile": "base64处理身份证反面",
                    "frontFile": "base64处理身份证正面",
                    "issuedBy": "武汉",
                    "nation": "汉",
                    "natureFile": "base64处理人脸照",
                    "validDate": "2012.10.1-2022.10.1"
                },
                "operator":{
                    "identity_code": "321323199909093919",
                    "created_time": "2017-03-07 15:30:20",
                    "channel_src": "中国联通",
                    "user_mobile": "18162033789",
                    "task_data": {
                        "bill_info": [
                                      {
                                          "bill_discount": "4120",
                                          "bill_fee": None,
                                          "usage_detail": [
                                                           {
                                                               "item_package_amount": None,
                                                               "item_usage": "0",
                                                               "item_name": "月固定费",
                                                               "item_last_balance": None
                                                           },
                                                           {
                                                               "item_package_amount": None,
                                                               "item_usage": "0",
                                                               "item_name": "基本套餐费",
                                                               "item_last_balance": None
                                                           },
                                                           {
                                                               "item_package_amount": None,
                                                               "item_usage": "0",
                                                               "item_name": "增值业务费",
                                                               "item_last_balance": None
                                                           },
                                                           {
                                                               "item_package_amount": None,
                                                               "item_usage": "0",
                                                               "item_name": "增值业务-绿色邮箱",
                                                               "item_last_balance": None
                                                           },
                                                           {
                                                               "item_package_amount": None,
                                                               "item_usage": "0",
                                                               "item_name": "联通在信",
                                                               "item_last_balance": None
                                                           },
                                                           {
                                                               "item_package_amount": None,
                                                               "item_usage": "0",
                                                               "item_name": "语音通话费",
                                                               "item_last_balance": None
                                                           },
                                                           {
                                                               "item_package_amount": None,
                                                               "item_usage": "0",
                                                               "item_name": "国内通话费",
                                                               "item_last_balance": None
                                                           },
                                                           {
                                                               "item_package_amount": None,
                                                               "item_usage": "0",
                                                               "item_name": "上网费",
                                                               "item_last_balance": None
                                                           },
                                                           {
                                                               "item_package_amount": None,
                                                               "item_usage": "0",
                                                               "item_name": "手机上网流量费",
                                                               "item_last_balance": None
                                                           }
                                                           ],
                                          "bill_record": [
                                                          {
                                                              "fee_name": "月固定费",
                                                              "fee_amount": "3600",
                                                              "fee_category": None,
                                                              "user_number": None
                                                          },
                                                          {
                                                              "fee_name": "基本套餐费",
                                                              "fee_amount": "3600",
                                                              "fee_category": None,
                                                              "user_number": None
                                                          },
                                                          {
                                                              "fee_name": "增值业务费",
                                                              "fee_amount": "10",
                                                              "fee_category": None,
                                                              "user_number": None
                                                          },
                                                          {
                                                              "fee_name": "增值业务-绿色邮箱",
                                                              "fee_amount": "0",
                                                              "fee_category": None,
                                                              "user_number": None
                                                          },
                                                          {
                                                              "fee_name": "联通在信",
                                                              "fee_amount": "10",
                                                              "fee_category": None,
                                                              "user_number": None
                                                          },
                                                          {
                                                              "fee_name": "语音通话费",
                                                              "fee_amount": "60",
                                                              "fee_category": None,
                                                              "user_number": None
                                                          },
                                                          {
                                                              "fee_name": "国内通话费",
                                                              "fee_amount": "60",
                                                              "fee_category": None,
                                                              "user_number": None
                                                          },
                                                          {
                                                              "fee_name": "上网费",
                                                              "fee_amount": "450",
                                                              "fee_category": None,
                                                              "user_number": None
                                                          },
                                                          {
                                                              "fee_name": "手机上网流量费",
                                                              "fee_amount": "450",
                                                              "fee_category": None,
                                                              "user_number": None
                                                          }
                                                          ],
                                          "bill_cycle": "2017-02",
                                          "paid_amount": None,
                                          "unpaid_amount": None,
                                          "breach_amount": None,
                                          "bill_total": "0"
                                      },
                                      {
                                          "bill_discount": "5460",
                                          "bill_fee": None,
                                          "usage_detail": [],
                                          "bill_record": [],
                                          "bill_cycle": "2017-01",
                                          "paid_amount": None,
                                          "unpaid_amount": None,
                                          "breach_amount": None,
                                          "bill_total": "0"
                                      },
                                      {
                                          "bill_discount": "3620",
                                          "bill_fee": None,
                                          "usage_detail": [],
                                          "bill_record": [],
                                          "bill_cycle": "2016-12",
                                          "paid_amount": None,
                                          "unpaid_amount": None,
                                          "breach_amount": None,
                                          "bill_total": "0"
                                      },
                                      {
                                          "bill_discount": "4535",
                                          "bill_fee": None,
                                          "usage_detail": [],
                                          "bill_record": [],
                                          "bill_cycle": "2016-11",
                                          "paid_amount": None,
                                          "unpaid_amount": None,
                                          "breach_amount": None,
                                          "bill_total": "0"
                                      },
                                      {
                                          "bill_discount": "3880",
                                          "bill_fee": None,
                                          "usage_detail": [],
                                          "bill_record": [],
                                          "bill_cycle": "2016-10",
                                          "paid_amount": None,
                                          "unpaid_amount": None,
                                          "breach_amount": None,
                                          "bill_total": "0"
                                      }
                                      ],
                        "family_info": [],
                        "sms_info": [
                                     {
                                         "total_msg_cost": "0",
                                         "total_msg_count": "14",
                                         "sms_record": [
                                                        {
                                                            "msg_cost": "10",
                                                            "msg_channel": None,
                                                            "msg_fee": None,
                                                            "msg_biz_name": None,
                                                            "msg_start_time": "2017-02-28 08:53:17",
                                                            "msg_discount": None,
                                                            "msg_remark": None,
                                                            "msg_type": "2",
                                                            "msg_address": None,
                                                            "msg_other_num": "18616105695"
                                                        },
                                                        {
                                                            "msg_cost": "10",
                                                            "msg_channel": None,
                                                            "msg_fee": None,
                                                            "msg_biz_name": None,
                                                            "msg_start_time": "2017-02-28 08:47:39",
                                                            "msg_discount": None,
                                                            "msg_remark": None,
                                                            "msg_type": "2",
                                                            "msg_address": None,
                                                            "msg_other_num": "18616105695"
                                                        }
                                                        ],
                                         "msg_cycle": "2017-02"
                                     },
                                     {
                                         "total_msg_cost": "0",
                                         "total_msg_count": "10",
                                         "sms_record": [],
                                         "msg_cycle": "2017-01"
                                     },
                                     {
                                         "total_msg_cost": "0",
                                         "total_msg_count": "12",
                                         "sms_record": [],
                                         "msg_cycle": "2016-12"
                                     },
                                     {
                                         "total_msg_cost": "30",
                                         "total_msg_count": "11",
                                         "sms_record": [],
                                         "msg_cycle": "2016-11"
                                     },
                                     {
                                         "total_msg_cost": "0",
                                         "total_msg_count": "9",
                                         "sms_record": [],
                                         "msg_cycle": "2016-10"
                                     }
                                     ],
                        "account_info": {
                            "mobile_status": "开通",
                            "prom_available": "0",
                            "credit_score": None,
                            "credit_point": "2215",
                            "balance_unavailable": None,
                            "account_balance": "15022",
                            "balance_available": "15022",
                            "sim_card": "89860116831000879346",
                            "land_level": "国内通话",
                            "prepay_unavailable": "0",
                            "net_age": "35",
                            "real_info": None,
                            "prepay_available": "15022",
                            "prom_unavailable": "0",
                            "credit_effective_time": None,
                            "credit_level": "二星用户",
                            "net_time": "2014年04月22日",
                            "puk_code": "09004314",
                            "current_fee": "3600",
                            "roam_state": "国内漫游"
                        },
                        "point_info": {
                            "point_record": [],
                            "point_detail": []
                        },
                        "base_info": {
                            "user_sex": "男",
                            "cert_addr": "江苏省泗阳县三庄乡黄徐村一组19号",
                            "user_email": "未绑定",
                            "user_name": "王小明",
                            "post_code": None,
                            "cert_num": "3213****3918",
                            "user_number": "18162033789",
                            "user_contact_no": None
                        },
                        "payment_info": [
                                         {
                                             "pay_date": "2017-02-08",
                                             "pay_channel": "银行代收",
                                             "pay_fee": "1000",
                                             "pay_type": None
                                         },
                                         {
                                             "pay_date": "2016-12-12",
                                             "pay_channel": "银行代收",
                                             "pay_fee": "10000",
                                             "pay_type": None
                                         },
                                         {
                                             "pay_date": "2016-11-11",
                                             "pay_channel": "银行代收",
                                             "pay_fee": "10000",
                                             "pay_type": None
                                         },
                                         {
                                             "pay_date": "2016-10-07",
                                             "pay_channel": "银行代收",
                                             "pay_fee": "10000",
                                             "pay_type": None
                                         }
                                         ],
                        "package_info": {
                            "brand_name": "沃4G后付费",
                            "pay_type": "后付费",
                            "package_detail": [
                                               {
                                                   "fee_cycle": None,
                                                   "package_name": "4G本地套餐-36元套餐",
                                                   "invalid_time": None,
                                                   "category": None,
                                                   "package_fee": None,
                                                   "effect_time": None
                                               }
                                               ]
                        },
                        "call_info": [
                                      {
                                          "total_call_count": "18",
                                          "total_call_time": "5327",
                                          "total_fee": "0",
                                          "call_cycle": "2017-03",
                                          "call_record": [
                                                          {
                                                              "call_cost": "0",
                                                              "call_land_type": "国内通话",
                                                              "call_long_distance": None,
                                                              "call_type_name": "被叫",
                                                              "call_time": "9",
                                                              "call_roam_cost": None,
                                                              "call_other_number": "13761836627",
                                                              "call_start_time": "2017-03-07 14:35:55",
                                                              "call_discount": None,
                                                              "call_address": "上海"
                                                          },
                                                          {
                                                              "call_cost": "0",
                                                              "call_land_type": "国内通话",
                                                              "call_long_distance": None,
                                                              "call_type_name": "被叫",
                                                              "call_time": "13",
                                                              "call_roam_cost": None,
                                                              "call_other_number": "02867732837",
                                                              "call_start_time": "2017-03-06 18:05:36",
                                                              "call_discount": None,
                                                              "call_address": "上海"
                                                          },
                                                          {
                                                              "call_cost": "0",
                                                              "call_land_type": "国内通话",
                                                              "call_long_distance": None,
                                                              "call_type_name": "被叫",
                                                              "call_time": "846",
                                                              "call_roam_cost": None,
                                                              "call_other_number": "15905150326",
                                                              "call_start_time": "2017-03-06 17:34:02",
                                                              "call_discount": None,
                                                              "call_address": "上海"
                                                          },
                                                          {
                                                              "call_cost": "0",
                                                              "call_land_type": "国内通话",
                                                              "call_long_distance": None,
                                                              "call_type_name": "被叫",
                                                              "call_time": "11",
                                                              "call_roam_cost": None,
                                                              "call_other_number": "10101888",
                                                              "call_start_time": "2017-03-01 15:26:56",
                                                              "call_discount": None,
                                                              "call_address": "上海"
                                                          },
                                                          {
                                                              "call_cost": "0",
                                                              "call_land_type": "国内通话",
                                                              "call_long_distance": None,
                                                              "call_type_name": "被叫",
                                                              "call_time": "15",
                                                              "call_roam_cost": None,
                                                              "call_other_number": "18137588985",
                                                              "call_start_time": "2017-03-01 15:00:31",
                                                              "call_discount": None,
                                                              "call_address": "上海"
                                                          }
                                                          ]
                                      },
                                      {
                                          "total_call_count": "71",
                                          "total_call_time": "10049",
                                          "total_fee": "60",
                                          "call_cycle": "2017-02",
                                          "call_record": [
                                                         ]
                                      },
                                      {
                                          "total_call_count": "72",
                                          "total_call_time": "15662",
                                          "total_fee": "540",
                                          "call_cycle": "2017-01",
                                          "call_record": []
                                      },
                                      {
                                          "total_call_count": "44",
                                          "total_call_time": "17068",
                                          "total_fee": "0",
                                          "call_cycle": "2016-12",
                                          "call_record": []
                                      },
                                      {
                                          "total_call_count": "68",
                                          "total_call_time": "14557",
                                          "total_fee": "885",
                                          "call_cycle": "2016-11",
                                          "call_record": []
                                      },
                                      {
                                          "total_call_count": "60",
                                          "total_call_time": "13318",
                                          "total_fee": "270",
                                          "call_cycle": "2016-10",
                                          "call_record": []
                                      }
                                      ]
                    },
                    "user_name": "18162033789",
                    "real_name": "王小明",
                    "channel_code": "100000",
                    "channel_type": "YYS",
                    "channel_attr": "上海",
                    "lost_data": None
                },
            }

        return self.send(url, data)

    #签名（提现）H5
    def send_sign_h5(self, phone, order_no, platform, return_url):
        import hashlib
        url = "http://106.15.126.217:8081/loanapp-api-web/v4/app/order/a1/login.do"
        md5 = hashlib.md5()
        md5.update("phone={}&order_no={}".format(phone, order_no).encode('utf-8'))
        data = "?phone={}&order_no={}&paltform={}&params={}&returnUrl={}".format(
            phone,
            order_no,
            platform,
            md5.hexdigest(),
            return_url)


        return url+data

    #签名（提现）API
    def send_sign_api(self, order_no):
        url = self.base_url + "/withDraw.do"
        data = {"orderNo": order_no}

        return self.send(url, data)

    #主动还款
    def send_repay(self, order_no):
        url = self.base_url + "/activeRepay.do"
        data = {"orderNo":order_no}

        return self.send(url, data)

    #拉取订单状态接口
    def send_get_order_status(self, order_no):
        url = self.base_url + "/getOrderStatus.do"
        data = {"orderNo": order_no}

        return self.send(url, data)

    #还款试算接口
    def send_count_repay(self, order_no, repay_num):
        url = self.base_url + "/"
        data = {"orderNo":order_no, "repayNum":repay_num}

        return self.send(url, data)

    #试算接口
    def send_get_count_pay(self, order_no, loan_amount):
        url = self.base_url + "/getCaculate.do"
        data = {"orderNo": order_no, "loanAmount": loan_amount}

        return self.send(url, data)

    #获取合同信息接口
    def send_get_contract(self, iurl, order_no):
        url = self.base_url + iurl
        data = {"orderNo": order_no}

        return self.send(url, data)

    #绑卡结果通知
    def send_band_result(self, iurl, result, order_no=None, phone=None):
        url = self.base_url + iurl
        if order_no:
            data = {"orderNo": order_no, "resultcode": result}
        if phone:
            data = {"phone":phone, "resultcode": result}

        return self.send(url, data)

    def send_order_status(self, iurl, order_num, status, approve_amount, approve_data,total_principal,
                          total_interest, total_repay_money, total_already_paid, total_overdue_fee, repay_plans_dict):
        pass

if __name__ == "__main__":
    api = SendShuiXiangAPI(appid, aeskey)

    #准入接口
    #print(api.send_zhunru(1,1,1))
    #print(api.send_preband_card(1,1,1,1,1,1))
    #print(api.send_ensure_card(1,2))
    #print(api.send_push_file(1,1,1,1,1,1,1))
    print(api.send_sign_api("15727158711_jqks"))
    #print(api.send_get_order_status("15727158711_jqks"))
    #print(api.send_repay("15727158711_jqks"))
    #print(api.send_sign_h5("15727150000", "15727158711_jqks", 4, "wwww.baidu.com"))
    #print(api.send_get_count_pay("15727158711_jqks", 5000000))