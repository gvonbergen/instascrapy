from rotating_proxies.policy import BanDetectionPolicy
from scrapy.exceptions import IgnoreRequest


class InstagramBanDetection(BanDetectionPolicy):
    NOT_BAN_STATUSES = {200, 404}

    def response_is_ban(self, request, response):
        if response.status not in self.NOT_BAN_STATUSES:
            return True
        if 'login' in response.url:
            return True
        return False

    def exception_is_ban(self, request, exception):
        return None