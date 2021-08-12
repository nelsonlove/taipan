from enum import Enum

from abstract import GoodEnum, PortEnum, SelectableEnum


class Goods(GoodEnum):
    OPIUM = 1000
    SILK = 100
    ARMS = 10
    GENERAL = 1, 'General Goods'


class Ports(PortEnum):
    HONG_KONG = 11, 11, 12, 10
    SHANGHAI = 16, 14, 16, 11
    NAGASAKI = 15, 15, 10, 12
    SAIGON = 14, 16, 11, 13
    MANILA = 12, 10, 13, 14
    SINGAPORE = 10, 13, 14, 15
    BATAVIA = 13, 12, 15, 16


class PortOrders(SelectableEnum):
    BUY = "Buy"
    SELL = "Sell"
    VISIT_BANK = "Visit Bank"
    TRANSFER_CARGO = "Transfer Cargo"
    RETIRE = "Retire"
    QUIT_TRADING = "Quit Trading"
    END_GAME = "End Game"


class BattleOrders(SelectableEnum):
    FIGHT = "Fight"
    RUN = "Run"
    THROW_CARGO = "Throw Cargo"


class Decisions(SelectableEnum):
    YES = 'Yes'
    NO = 'No'
