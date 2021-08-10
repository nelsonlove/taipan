from abstract import Orders


class PortOrders(Orders):
    BUY = 'Buy'
    SELL = 'Sell'
    VISIT_BANK = 'Visit bank'
    TRANSFER_CARGO = 'Transfer cargo'
    RETIRE = 'Retire'
    QUIT_TRADING = 'Quit trading'
    END_GAME = 'End game'


class GoodOrders(Orders):
    OPIUM = 'Opium'
    SILK = 'Silk'
    ARMS = 'Arms'
    GENERAL = 'General'


class SailOrders(Orders):
    HONG_KONG = 1
    SHANGHAI = 2
    NAGASAKI = 3
    SAIGON = 4
    MANILA = 5
    SINGAPORE = 6
    BATAVIA = 7

    @property
    def shortcut(self):
        return str(self.value)


class BattleOrders(Orders):
    FIGHT = "Fight"
    RUN = "Run"
    THROW_CARGO = "Throw Cargo"


class Decision(Orders):
    YES = 'Yes'
    NO = 'No'
