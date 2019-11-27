from enum import Enum

DomainAction = Enum(
    'DomainAction', 'ALLOW DENY CLOAK'
)
DomainCategory = Enum(
    'DomainCategory', 'Porn Other Uncategorized'
)
