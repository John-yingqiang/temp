
class InviteCode(object):
    """
    A 用来补位
    """

    static_string = 'E5FCDG3HQ4B1NOPIJ2RSTUV67MWX89KL0YZ'

    def uid_to_code(self, uid):
        code = ''
        while uid > 0:
            mod = int(uid % 35)
            uid = int((uid - mod) / 35)
            code = self.static_string[mod] + code
        if len(code) < 4:
            code = code.rjust(4, 'A')
        return code

    def code_to_uid(self, code):
        code = code.replace('A', '')
        len_code = len(code)
        code = code[::-1]
        uid = 0
        for i in range(len_code):
            uid += self.static_string.index(code[i]) * pow(35, i)
        return int(uid)
