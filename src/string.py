from datetime import date

import goods


def comma_list(l):
    return ', '.join(l[:-1]) + ', or ' + l[-1]


def goods_str(goods_obj, string='Taipan, present prices per unit here are:'):
    price_str = ("{on:<8}: {o:<11}{sn:<8}: {s:<11}\n"
                 "{an:<8}: {a:<11}{gn:<8}: {g:<11}\n")
    return str(string + '\n' if string else '') + price_str.format(
        on='Opium',
        o=goods_obj[goods.OPIUM],
        sn='Silk',
        s=goods_obj[goods.SILK],
        an='Arms',
        a=goods_obj[goods.ARMS],
        gn='General',
        g=goods_obj[goods.GENERAL]
    )


def date_str(months):
    years = months // 12
    months = months % 12
    current_date = date(1860 + years, 1 + months, 15)
    return current_date.strftime('%d %b %Y')