START_BIT = 83
START_BIT_EXTENSION = 15
STROBE_LENGTH = 84
STROBE_SPACE = 48

class Tic:
    """ конструктор класса """
    def __init__(self, number, header, data):
        self.number = number
        self.header = header
        self.data = data
        self.extension = None

    def __str__(self):
        """ перезагрузка символьного представления класса """
        res = 'Header: ' + self.header + '\n'
        for item in self.data.keys():
            res = res + item + ' ' + ' '.join(self.data[item]) + '\n'
        return res

    def get_strobes(self):
        """ формирование стробов """
        # преобразование в длинную строку основного такта
        longdata = []
        for key in self.data.keys():
            longdata.extend(self.data[key])
        longdata = longdata[START_BIT:]

        # преобразование в длинную строку дополнительного такта
        if self.extension:
            longdataextension = []
            for key in self.extension.keys():
                longdataextension.extend(self.extension[key])
            longdataextension = longdataextension[START_BIT_EXTENSION:]
            longdata.extend(longdataextension)
        res = []
        while len(longdata) >= STROBE_LENGTH:
            res.append(longdata[0:STROBE_LENGTH])
            longdata = longdata[STROBE_LENGTH + STROBE_SPACE:]
        return res

    def setextention(self, extend_data):
        """ присоединение дополнения тика при соответствующем условии """
        bytes_tic = '0x' + self.data['0x0010'][4] + self.data['0x0010'][5]
        bytes_extend = '0x' + extend_data['0x0010'][4] + extend_data['0x0010'][5]
        if int(bytes_extend, 16) == (int(bytes_tic, 16) + 1):
            self.extension = extend_data
            return True
        return False



