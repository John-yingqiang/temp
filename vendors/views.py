from rest_framework.views import APIView
from rest_framework.response import Response
from common.permissions import WhiteListOnly
from .baidu_ocr import baidu_word_ocr
from common.logs import add_log_count
import traceback


class BaiDuWordOCRView(APIView):

    permission_classes = (WhiteListOnly,)

    def post(self, request):
        url = request.data.get('url')
        try:
            status, words = baidu_word_ocr(url)
            ret = {'success': status, 'words': words}
        except:
            ret = {'success': None, 'words': None}
            add_log_count('baidu_word_ocr')
            traceback.print_exc()

        return Response(ret)
