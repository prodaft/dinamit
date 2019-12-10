from enum import Enum

DomainAction = Enum(
    'DomainAction',
    'ALLOW DENY CLOAK'
)
DomainCategory = Enum(
    'DomainCategory',
    'ALCOHOL DATING GAMBLING PORNOGRAPHY STREAMING ADVERTISING MALICIOUS PHISHING MALWARE DRUG SPAM'
)
