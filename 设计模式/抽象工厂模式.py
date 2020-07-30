# _*_coding:utf-8_*_
__author__ = 'Alex Li'


class AbstractFactory(object):
    computer_name = ''

    def createCpu(self):
        pass

    def createMainboard(self):
        pass


class IntelFactory(AbstractFactory):
    computer_name = 'Intel I7-series computer '

    def createCpu(self):
        return IntelCpu('I7-6500')

    def createMainboard(self):
        return IntelMainBoard('Intel-6000')


class AmdFactory(AbstractFactory):
    computer_name = 'Amd 4 computer '

    def createCpu(self):
        return AmdCpu('amd444')

    def createMainboard(self):
        return AmdMainBoard('AMD-4000')


class AbstractCpu(object):
    series_name = ''
    instructions = ''
    arch = ''


class IntelCpu(AbstractCpu):
    def __init__(self, series):
        self.series_name = series


class AmdCpu(AbstractCpu):
    def __init__(self, series):
        self.series_name = series


class AbstractMainboard(object):
    series_name = ''


class IntelMainBoard(AbstractMainboard):
    def __init__(self, series):
        self.series_name = series


class AmdMainBoard(AbstractMainboard):
    def __init__(self, series):
        self.series_name = series


class ComputerEngineer(object):
    def makeComputer(self, computer_obj):
        self.prepareHardwares(computer_obj)

    def prepareHardwares(self, computer_obj):
        self.cpu = computer_obj.createCpu()
        self.mainboard = computer_obj.createMainboard()

        info = '''
            ------- computer [%s] info:
            cpu: %s
            mainboard: %s
        
            -------- End --------
        ''' % (computer_obj.computer_name, self.cpu.series_name, self.mainboard.series_name)
        print(info)


if __name__ == "__main__":
    engineer = ComputerEngineer()

    computer_factory = IntelFactory()
    engineer.makeComputer(computer_factory)

    computer_factory2 = AmdFactory()
    engineer.makeComputer(computer_factory2)