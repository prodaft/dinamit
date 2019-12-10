from dinamit.feeds.base import TextFeed
from dinamit.core.constants import DomainCategory


class LehighEduMalware(TextFeed):
    NAME = 'LehighEduMalware'
    CATEGORY = DomainCategory.MALWARE
    SOURCE = 'http://malwaredomains.lehigh.edu/files/justdomains'
