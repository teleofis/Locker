import MOD, GPIO, SER2

def pack(command, type, data):
    """Упаковка команды в транспортный протокол

    Args:
        command: Команда
            RESET - процессорный Watchdog
            COUNT - счетный вход
            INPUT - логический вход
            OUTPUT - логический выход
        type: Операция
            R - чтение параметра
            W - запить параметра
        data: Данные
    Returns:
        Строка в формате транспортного протокола
    """
    if (data != ''):
        message = '%s,%s,%s' % (command, type, data)
    else:
        message = '%s,%s' % (command, type)
    crc = calcCrc(0, message)
    frame = '$%s*%0.2X\r\n' % (message, crc)
    return frame

def unpack(m):
    """Распаковка команды из транспортного протокола

    Args:
        m: строка в формате транспортного протокола
    Returns:
        Массив данных
    """
    try:
        m = m.strip()
        if m.startswith('$'):
            m = m[1:]
        messageParts = m.split('*')
        crc1 = int(messageParts[1], 16)
        crc2 = calcCrc(0, messageParts[0])
        if(crc1 == crc2):
            parsedData = messageParts[0].split(',')
            return parsedData
    except Exception, e:
        return []
    return []
    
def calcCrc(crc, data):
    """Алгоритм подсчета контрольной суммы

    Args:
        crc: Начальное значение контрольной суммы
        data: Данные
    Returns:
        Контрольная сумма
    """
    for d in data:
        crc = crc ^ ord(d)
    return crc

def send(cmd, type, data):
    """Отправить команду для процессора

    Args:
        cmd: Команда
        type: Операция
        data: Данные
    """
    req = pack(cmd, type, data)
    SER2.send(req)
    
def receive(timeout = 2):
    """Получить ответ от процессора

    Args:
        timeout: Время ожидания ответа в сек
    Returns:
        Сырые принятые данные
    """
    data = ''
    timer = MOD.secCounter() + timeout
    while(1):
        rcv = SER2.read()
        if(len(rcv) > 0):
            data = data + rcv
            if(data.endswith('\r') or data.endswith('\n')):
                return data
        if(MOD.secCounter() > timer):
            return ''
    
def resetWDT():
    """Сброс сторожевого таймера процессора

    Returns:
        0 - ошибка
        1 - успешно
    """
    send('RESET', 'W', '')
    res = receive()
    ans = unpack(res)
    if(len(ans) > 1):
        if(ans[0] == 'RESET' and ans[1] == 'A'):
            return 0
    return -1

def readCounter(num):
    """Чтение значения счетчика импульсов

    Args:
        num: Номер входа 1-2
    Returns:
        0-... - значение счетчика
        -1 - ошибка
    """
    send('COUNT', 'R', str(num))
    res = receive()
    ans = unpack(res)
    if(len(ans) > 3):
        if(ans[0] == 'COUNT' and ans[1] == 'A' and ans[2] == str(num)):
            return int(ans[3])
    return -1

def writeCounter(num, value):
    """Запись значения счетчика импульсов

    Args:
        num: Номер входа 1-2
        value: Значение счетчика
    Returns:
        
    """
    send('COUNT', 'W', str(num) + ',' + str(value))
    res = receive()
    ans = unpack(res)
    if(len(ans) > 2):
        if(ans[0] == 'COUNT' and ans[1] == 'A' and ans[2] == str(num)):
            return 0
    return -1

def writeOutput(num, state):
    """Установка состояния цифрового выхода

    Args:
        num: номер выхода
        state: состояние
    Returns:
        0 - ОК
        -1 - ошибка
    """
    send('OUTPUT', 'W', str(num) + ',' + str(state))
    res = receive()
    ans = unpack(res)
    if(len(ans) > 2):
        if(ans[0] == 'OUTPUT' and ans[1] == 'A'):
            return 0
    return -1

def readInput(num):
    """Чтение состояния цифрового входа

    Args:
        num: номер цифрового входа
    Returns:
        -1 - ошибка
        0 - низкий уровень
        1 - высокий уровень
    """
    send('INPUT', 'R', str(num))
    res = receive()
    ans = unpack(res)
    if(len(ans) > 3):
        if(ans[0] == 'INPUT' and ans[1] == 'A' and ans[2] == str(num)):
            return int(ans[3])
    return -1

def getCounter1():
    """Чтение состояния цифрового входа Counter 1

    Returns:
        -1 - ошибка
        0 - низкий уровень
        1 - высокий уровень
    """
    return readInput(17)
    
def getCounter2():
    """Чтение состояния цифрового входа Counter 2

    Returns:
        -1 - ошибка
        0 - низкий уровень
        1 - высокий уровень
    """
    return readInput(18)
    
def set75V(state):
    """Установка состояния выхода 7.5 V

    Args:
        state: состояние
    Returns:
        0 - ОК
        -1 - ошибка
    """
    return writeOutput(25, state)

def get75V():
    """Чтение состояния выхода 7.5 V
    
    Returns:
        состояние выхода
    """
    return readInput(25)

def setVCC(state):
    """Установка состояния выхода 12 V

    Args:
        state: состояние
    Returns:
        0 - ОК
        -1 - ошибка
    """
    return writeOutput(29, state)

def getVCC():
    """Чтение состояния выхода 12 V
    
    Returns:
        состояние выхода
    """
    return readInput(29)

def getSimInsert1():
    """Чтение состояния сигнала установки SIM карты 1

    Returns:
        0 - не установлена
        1 - установлена
    """
    return readInput(32)

def getSimInsert2():
    """Чтение состояния сигнала установки SIM карты 2

    Returns:
        0 - не установлена
        1 - установлена
    """
    return readInput(46)

def initIO():
    """Инициализация линий ввода-вывода
    """
    SER2.set_speed('115200')
    # 0 - input, 1 - output, 2 - alt
    GPIO.setIOdir(4, 0, 0) # SK1
    GPIO.setIOdir(3, 0, 0) # SK2
    GPIO.setIOdir(6, 0, 1) # RELE1
    GPIO.setIOdir(1, 0, 1) # RELE2
    GPIO.setIOdir(5, 0, 1) # SIM_SELECT
    GPIO.setIOdir(2, 0, 2) # JDR

def getADC():
    """Чтение значения АЦП
    
    Returns:
        Значение АЦП
    """
    mV = GPIO.getADC(1)
    return mV

def getSK1():
    """Чтение состояния сухого контакта 1

    Returns:
        Состояние
    """
    state = GPIO.getIOvalue(4)
    return state

def getSK2():
    """Чтение состояния сухого контакта 2

    Returns:
        Состояние
    """
    state = GPIO.getIOvalue(3)
    return state

def getOUT1():
    """Чтение состояния реле 1

    Returns:
        Состояние
    """
    state = GPIO.getIOvalue(6)
    return state

def setOUT1(state):
    """Установка состояния реле 1
    
    Args:
        state: требуемое состояние

    """
    GPIO.setIOvalue(6, state)
    
def getOUT2():
    """Чтение состояния реле 2

    Returns:
        Состояние
    """
    state = GPIO.getIOvalue(1)
    return state

def setOUT2(state):
    """Установка состояния реле 2

    Args:
        state: требуемое состояние

    """
    GPIO.setIOvalue(1, state)
    
def getSIMSELECT():
    """Чтение состояния выхода SIMSELECT

    Returns:
        Состояние
    """
    state = GPIO.getIOvalue(5)
    return state

def setSIMSELECT(state):
    """Установка состояния выхода SIMSELECT

    Args:
        state: требуемое состояние

    """
    GPIO.setIOvalue(5, state)

def getJDR():
    """Чтение состояния входа JD

    Returns:
        Состояние
    """
    state = GPIO.getIOvalue(2)
    return state

    