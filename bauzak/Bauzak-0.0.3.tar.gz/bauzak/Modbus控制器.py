from fatek.symbol import Symbol
from fatek.target import FatekTarget
from pymodbus3.client.sync import ModbusTcpClient


class Modbus控制器:
    # MODBUS Application Protocol Specification V1.1b
    # http://www.modbus.org/docs/Modbus_Application_Protocol_V1_1b.pdf
    # - page 12
    線圈一擺數量限制 = 2000
    # - page 15
    暫存器一擺數量限制 = 125

    def __init__(self, ip, port):
        self.連線 = ModbusTcpClient(host=ip, port=port)

    def 開始(self):
        self.連線.connect()

    def 停止(self):
        self.連線.close()

    def 讀一个(self, 所在):
        return FatekTarget(self.連線, 所在).read()

    def 讀線圈的資料(self, 表):
        位置名對應表 = {}
        for 位, 名 in 表.items():
            位置名對應表[Symbol(位, current_value=False).offset] = 名

        這段開始 = None
        這段結束 = None
        上尾資料 = {}
        for 位置 in sorted(位置名對應表.keys()):
            這个開始 = 位置
            這个結束 = 位置 + 1
            if 這段開始 is None:
                這段開始 = 這个開始
                這段結束 = 這个結束
            elif 這个結束 - 這段開始 <= self.線圈一擺數量限制:
                這段結束 = 這个結束
            else:
                self._讀線圈一段資料(位置名對應表, 上尾資料, 這段開始, 這段結束)
                這段開始 = 這个開始
                這段結束 = 這个結束
        if 這段開始 is not None:
            self._讀線圈一段資料(位置名對應表, 上尾資料, 這段開始, 這段結束)
        return 上尾資料

    def _讀線圈一段資料(self, 位置名對應表, 上尾資料, 這段開始, 這段結束):
        result = self.連線.read_coils(這段開始, 這段結束 - 這段開始)
        原始資料 = result.bits
        for 對應位址, 細 in enumerate(原始資料, start=這段開始):
            try:
                名 = 位置名對應表[對應位址]
            except:
                pass
            else:
                上尾資料[名] = 細

    def 讀16位元的資料(self, 表):
        位置名對應表 = {}
        for 位, 名 in 表.items():
            位置名對應表[Symbol(位, current_value=True).offset] = 名

        這段開始 = None
        這段結束 = None
        上尾資料 = {}
        for 位置 in sorted(位置名對應表.keys()):
            這个開始 = 位置
            這个結束 = 位置 + 1
            if 這段開始 is None:
                這段開始 = 這个開始
                這段結束 = 這个結束
            elif 這个結束 - 這段開始 <= self.暫存器一擺數量限制:
                這段結束 = 這个結束
            else:
                self._讀16位元一段資料(位置名對應表, 上尾資料, 這段開始, 這段結束)
                這段開始 = 這个開始
                這段結束 = 這个結束
        if 這段開始 is not None:
            self._讀16位元一段資料(位置名對應表, 上尾資料, 這段開始, 這段結束)
        return 上尾資料

    def _讀16位元一段資料(self, 位置名對應表, 上尾資料, 這段開始, 這段結束):
        result = self.連線.read_holding_registers(這段開始, 這段結束 - 這段開始)
        原始資料 = result.registers
        for 對應位址, 細 in enumerate(原始資料, start=這段開始):
            try:
                名 = 位置名對應表[對應位址]
            except:
                pass
            else:
                上尾資料[名] = 細

    def 讀32位元的資料(self, 表):
        位置名對應表 = {}
        for 位, 名 in 表.items():
            位置名對應表[Symbol(位, current_value=True).offset] = 名

        這段開始 = None
        這段結束 = None
        上尾資料 = {}
        for 位置 in sorted(位置名對應表.keys()):
            這个開始 = 位置
            這个結束 = 位置 + 2
            if 這段開始 is None:
                這段開始 = 這个開始
                這段結束 = 這个結束
            elif 這个結束 - 這段開始 <= self.暫存器一擺數量限制:
                這段結束 = 這个結束
            else:
                self._讀32位元一段資料(位置名對應表, 上尾資料, 這段開始, 這段結束)
                這段開始 = 這个開始
                這段結束 = 這个結束
        if 這段開始 is not None:
            self._讀32位元一段資料(位置名對應表, 上尾資料, 這段開始, 這段結束)
        return 上尾資料

    def _讀32位元一段資料(self, 位置名對應表, 上尾資料, 這段開始, 這段結束):
        result = self.連線.read_holding_registers(這段開始, 這段結束 - 這段開始)
        原始資料 = result.registers
        for 對應位址, (細, 大) in enumerate(zip(原始資料[:-1], 原始資料[1:]), start=這段開始):
            try:
                名 = 位置名對應表[對應位址]
            except:
                pass
            else:
                上尾資料[名] = 細 + 大 * 65536

    def sia2_32位元的資料(self):
        result = self.連線.read_holding_registers(4128, 6)
        print(result.registers)
        self.連線.write_registers(
            2020, [8, 0, 17, 0, 19, 0, 4, 0, 0, 0, 0, 0])

    def tui2si5(self):
        self.連線.write_registers(2010, [13, 36, 14, 29, 12, 16, 1])
