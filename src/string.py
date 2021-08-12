import random
from datetime import date

from enums import Goods


def comma_list(str_list, conjunction='or'):
    return ', '.join(str_list[:-1]) + f', {conjunction} ' + str_list[-1]


def goods_str(goods_obj, string='Taipan, present prices per unit here are:'):
    good_str = '{g:<8}: {p:<11}'
    goods = [good for good in Goods]
    goods_tuples = tuple(goods[x:x + 2] for x in range(0, len(Goods), 2))

    price_str = ''
    for gt in goods_tuples:
        for good in gt:
            price_str += good_str.format(g=good.shortname, p=goods_obj[good])
        price_str += '\n'
    return str(string + '\n' if string else '') + price_str


def date_str(months):
    years = months // 12
    months = months % 12
    current_date = date(1860 + years, 1 + months, 15)
    return current_date.strftime('%d %b %Y')
