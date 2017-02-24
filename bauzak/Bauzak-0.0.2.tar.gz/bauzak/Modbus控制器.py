from fatek.target import FatekTarget
from pymodbus3.client.sync import ModbusTcpClient


class Modbus控制器:

    def __init__(self, ip, port):
        self.連線 = ModbusTcpClient(host=ip, port=port)

    def 開始(self):
        self.連線.connect()

    def 停止(self):
        self.連線.close()

    def 讀一个(self, 所在):
        return FatekTarget(self.連線, 所在).read()

    def 讀32位元的資料(self, 表):
        位置名對應表 = {}
        for 位, 名 in 表.items():
            位置名對應表[int(位.strip('R'))] = 名
#             檢查攏愛雙數
        開始, *_, 結束 = sorted(位置名對應表.keys())
        位址數量 = (結束 + 2 - 開始)
# 檢查袂使超過125
        result = self.連線.read_holding_registers(開始, 位址數量)
        原始資料 = result.registers

        上尾資料 = {}
        for 第幾个, (細, 大) in enumerate(zip(原始資料[::2], 原始資料[1::2])):
            對應位址 = 開始 + 第幾个 + 第幾个
            try:
                名 = 位置名對應表[對應位址]
            except:
                pass
            else:
                上尾資料[名] = 細 + 大 * 65536
        return 上尾資料

    def 讀16位元的資料(self, 表):
        位置名對應表 = {}
        for 位, 名 in 表.items():
            位置名對應表[int(位.strip('R'))] = 名
#             檢查攏愛雙數
        開始, *_, 結束 = sorted(位置名對應表.keys())
        位址數量 = (結束 + 1 - 開始)
# 檢查袂使超過125
        result = self.連線.read_holding_registers(開始, 位址數量)
        原始資料 = result.registers

        上尾資料 = {}
        for 第幾个, 數值 in enumerate(原始資料):
            對應位址 = 開始 + 第幾个
            try:
                名 = 位置名對應表[對應位址]
            except:
                pass
            else:
                上尾資料[名] = 數值
        return 上尾資料

    def sia2_32位元的資料(self):
        result = self.連線.read_holding_registers(4128, 6)
        print(result.registers)
        self.連線.write_registers(
            2020, [8, 0, 17, 0, 19, 0, 4, 0, 0, 0, 0, 0])

    def tui2si5(self):
        self.連線.write_registers(2010, [13, 36, 14, 29, 12, 16, 1])
