from codecs import encode, decode
from babel import dates


def create_rule_hash(src, dst):
    return decode(encode(encode('{}-{}'.format(src, dst), 'utf-8'), 'hex'), 'utf-8')


def convert_datetime(dt):
    return dates.format_datetime(dt)
