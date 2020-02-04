from rotating_proxies.policy import BanDetectionPolicy
from scrapy.exceptions import IgnoreRequest


class InstagramBanDetection(BanDetectionPolicy):
    NOT_BAN_STATUSES = {200, 301, 302, 404}
    NOT_BAN_EXCEPTIONS = (IgnoreRequest,)

    # Todo: Change rotating proxy behavior if item could not be retrieved
    def response_is_ban(self, request, response):
        if response.status not in self.NOT_BAN_STATUSES:
            return True
        if response.status == 200 and not len(response.body):
            return True
        if response.status == 200 and 'login' in response.url:
            return True
        if response.status == 302:
            return True
        return False

    def exception_is_ban(self, request, exception):
        return None