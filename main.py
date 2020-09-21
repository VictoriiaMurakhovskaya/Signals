from tkinter import Tk, Button, Entry, StringVar, LEFT
from tkinter.ttk import Combobox
from tkinter import messagebox as mb
from tkinter import filedialog as fd
from tkinter import LabelFrame as lf
import re
from tic import Tic
import json
import os

file = None

json_dict = {'nom_sign': 8, 'n_fil': 8, 'n_dec': 8, 'n_dfm': 8, 'poly': 8, 'n_tay': 8, 'Drp': 8, 'dev':	8, 'Kpot': 8,
             'nsdv': 8, 'nstr':	8, 'ndnstr': 8, 'dlstr': 8, 'fg1': 8, 'r_phasepoint': 8, 'tips': 4, 'nvk': 4,'nhk':	4,
             'prUWB': 2, 'reserve':	4, 'nfaz': 2, 'input_switch': 2, 'trks': 2, 'reserve_1': 2, 'kdiv_x': 2,
             'kdiv_y': 2, 'npos': 2, 'mask_rec': 8, 'attamps': 2, 'fazkk': 2, 'fazopk':	2, 'mask_bc_ams': 2,
             'mode_cont_unit': 2, 'kpg': 2, 'align_1': 12, 'reserve_2':	12, 'por_blank': 4, 'abs_value': 8, 'kgd': 8,
             'shgd': 8, 'trace_ctrl': 8, 'fg2':	8, 'nfgd_fu': 8, 'nlgrs': 4, 'kgrs': 4, 'shgrs': 4, 'magnitude_rel': 4,
             'magnitude_fl': 4, 'win_size_R': 2, 'win_size_V': 2, 'thres_comb':	2, 'local_max':	2, 'mask_pol':	2,
             'prclb': 2, 'kolimp': 2, 'namplrs': 2, 'tippc': 2, 'union_pol': 2, 'comm_ent_stream': 2, 'mask232': 4,
             'hardw_model_mask': 2, 'sign_ea': 2, 'num_ad':	2, 'align_2': 12, 'nom_imob': 4, 'pr_imit':	2, 'nom_can': 2,
             'tip_z': 2, 'nom_bar': 2, 'align_3': 12}

to_float = ['n_tay', 'Drp', 'Kpot']

to_plusminus = ['nfgd_fu', 'n1grs']


def choose_file():
    """ обработчик кнопки выбора файла """
    global file
    file.set(fd.askopenfile().name)


def check_bit(item):
    """ проверка соответствия тика условиям
        в начальной задаче бит 0x0040 равен 0049 """
    try:
        bit = item['0x0040'][0]
        if bit == '0049':
            return True
        else:
            return False
    except:
        return False


def main_method(filename=None):
    """ основной метод обработки входного файла
        filename - имя обрабатываемого файла
        если не передано, читается напрямую текстовое поле в GUI"""
    main_dict = {}
    subdict = {}
    header = ' '
    if not filename:
        filename = file.get()

    # чтение файла
    with open(filename) as f:
        for line in f:
            match = re.search(r'[\d]{2}\:[\d]{2}\:[\d]{2}[\.]{1}[\d]*', line)
            if match:
                if header != '':
                    main_dict.update({header: subdict})
                header = match.group(0)
                subdict = {}
            else:
                match = re.search(r'0[Хx][0-9A-Fa-f]{4}', line)
                if match:
                    subheader = match.group(0)
                    subline = line[len(subheader)+2:]
                    data = subline.strip().split(' ')
                    subdict.update({subheader: data})
        main_dict.update({header: subdict})

    # создание списка объектов, при удовлетворении входному условию
    # условие может быть изменено в функции check_bit()
    res = []
    count = 0 # счетчик тиков, увеличивается всегда кроме случая, когда следующий тик есть продолжение предыдущего
    for item in main_dict.keys():
        if check_bit(main_dict[item]):
            res.append(Tic(count, item, main_dict[item]))
            count += 1
        else:
            if res:
                if not res[-1].setextention(main_dict[item]):
                    count += 1

    # формирование выходного файла
    # определение имени файла
    outputfilename = filename[:filename.index('.')]
    json_result = make_json(res)
    with open(outputfilename + '.json', 'w') as f:
        json.dump(json_result, f)

    # формирование данных для текстового файла
    textarray = []
    for key in json_result.keys():
        count = 1
        for subitem in json_result[key]:
            # номер тика, номер строба, нужное значение
            textarray.append((key, count, subitem['mask_pol']))
            count += 1

    with open(outputfilename + '.txt', 'w') as f:
        for item in textarray:
            f.write('Номер строба: %d\t Побитовая маска поляризаций (mask_pol): %d\t Номер такта: %d\n' % (item[1], item[2], item[0]))
    mb.showinfo(title='Сообщение', message='Формирование файлов завершено')


def make_json(ticlist):
    """ функция формирования JSON на основе списка тактов """
    s = 0
    write_dict = {}
    for item in json_dict.keys():
        s += json_dict[item]
    for item in ticlist:
        strobeslst = []
        for subitem in item.get_strobes():
            stringtoparse = ''.join(subitem)
            pointer = 0
            strobedict = {}
            for parametr in json_dict.keys():
                value = stringtoparse[pointer: pointer+json_dict[parametr]]
                # перевод параметра в другую систему счисления и запись в словарь
                if parametr in to_float:
                    # если параметр в списке float - параметров
                    strobedict.update({parametr: int('0x' + value, 16)})
                elif parametr in to_plusminus:
                    # если нужно анализировать положительный/отрицательный
                    # проверка знака
                    if (value[:4].lower() == '00ff') | (value[:4].lower() == 'ffff'):
                        sign = -1
                    else:
                        sign = 1
                    strobedict.update({parametr: sign * int('0x' + value[4:], 16)})
                else:
                    strobedict.update({parametr: int('0x' + value, 16)})
            strobeslst.append(strobedict)
        write_dict.update({item.number: strobeslst})
    return write_dict


def main():
    """ метод вызывается при запуске скрипта как основного модуля программы
        создание графического интефейса пользователя """
    global file
    window = Tk()
    file = StringVar()
    window.geometry("330x100")
    input1 = lf(window, text='Файл дампа')
    Entry(input1, textvariable=file, width=25).pack(side=LEFT, padx=10, pady=10)
    Button(input1, text='...', command=choose_file).pack(side=LEFT, padx=10, pady=10)
    input1.pack(side=LEFT, pady=10, padx=20)
    Button(window, text='Считать', command=main_method).pack(side=LEFT, pady=(15, 10), padx=(0,20))
    window.mainloop()


if __name__ == '__main__':
    main()



