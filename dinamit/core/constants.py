from enum import Enum

DomainAction = Enum(
    'DomainAction', 'ALLOW DENY CLOAK'
)
DomainCategory = Enum(
    'DomainCategory', 'ADS MALICIOUS MALWARE PHISHING PORN UNCATEGORIZED'
)
