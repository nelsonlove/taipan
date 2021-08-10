import goods

from abstract import Port


HONG_KONG = Port(1, "Hong Kong", {
    goods.OPIUM: 11,
    goods.SILK: 11,
    goods.ARMS: 12,
    goods.GENERAL: 10,
})

SHANGHAI = Port(2, "Shanghai", {
    goods.OPIUM: 16,
    goods.SILK: 14,
    goods.ARMS: 16,
    goods.GENERAL: 11,
})

NAGASAKI = Port(3, "Nagasaki", {
    goods.OPIUM: 15,
    goods.SILK: 15,
    goods.ARMS: 10,
    goods.GENERAL: 12,
})

SAIGON = Port(4, "Saigon", {
    goods.OPIUM: 14,
    goods.SILK: 16,
    goods.ARMS: 11,
    goods.GENERAL: 13,
})

MANILA = Port(5, "Manila", {
    goods.OPIUM: 12,
    goods.SILK: 10,
    goods.ARMS: 13,
    goods.GENERAL: 14,
})

SINGAPORE = Port(6, "Singapore", {
    goods.OPIUM: 10,
    goods.SILK: 13,
    goods.ARMS: 14,
    goods.GENERAL: 15,
})

BATAVIA = Port(7, "Batavia", {
    goods.OPIUM: 13,
    goods.SILK: 12,
    goods.ARMS: 15,
    goods.GENERAL: 16,
})
