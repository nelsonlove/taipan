from enums import Goods


def goods_str(goods_obj, string='Taipan, present prices per unit here are:'):
    goods = [good for good in Goods]
    goods_tuples = tuple(goods[x:x + 2] for x in range(0, len(Goods), 2))

    price_str = ''
    for gt in goods_tuples:
        for good in gt:
            price_str += '{g:<8}: {p:<11}'.format(g=good.shortname, p=goods_obj[good])
        price_str += '\n'
    return str(string + '\n' if string else '') + price_str
