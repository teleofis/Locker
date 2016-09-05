'''
Copyright (c) 2013, ОАО "ТЕЛЕОФИС"

Разрешается повторное распространение и использование как в виде исходного кода, так и в двоичной форме, 
с изменениями или без, при соблюдении следующих условий:

- При повторном распространении исходного кода должно оставаться указанное выше уведомление об авторском праве, 
  этот список условий и последующий отказ от гарантий.
- При повторном распространении двоичного кода должна сохраняться указанная выше информация об авторском праве, 
  этот список условий и последующий отказ от гарантий в документации и/или в других материалах, поставляемых 
  при распространении.
- Ни название ОАО "ТЕЛЕОФИС", ни имена ее сотрудников не могут быть использованы в качестве поддержки или 
  продвижения продуктов, основанных на этом ПО без предварительного письменного разрешения.

ЭТА ПРОГРАММА ПРЕДОСТАВЛЕНА ВЛАДЕЛЬЦАМИ АВТОРСКИХ ПРАВ И/ИЛИ ДРУГИМИ СТОРОНАМИ «КАК ОНА ЕСТЬ» БЕЗ КАКОГО-ЛИБО 
ВИДА ГАРАНТИЙ, ВЫРАЖЕННЫХ ЯВНО ИЛИ ПОДРАЗУМЕВАЕМЫХ, ВКЛЮЧАЯ, НО НЕ ОГРАНИЧИВАЯСЬ ИМИ, ПОДРАЗУМЕВАЕМЫЕ ГАРАНТИИ 
КОММЕРЧЕСКОЙ ЦЕННОСТИ И ПРИГОДНОСТИ ДЛЯ КОНКРЕТНОЙ ЦЕЛИ. НИ В КОЕМ СЛУЧАЕ НИ ОДИН ВЛАДЕЛЕЦ АВТОРСКИХ ПРАВ И НИ 
ОДНО ДРУГОЕ ЛИЦО, КОТОРОЕ МОЖЕТ ИЗМЕНЯТЬ И/ИЛИ ПОВТОРНО РАСПРОСТРАНЯТЬ ПРОГРАММУ, КАК БЫЛО СКАЗАНО ВЫШЕ, НЕ 
НЕСЁТ ОТВЕТСТВЕННОСТИ, ВКЛЮЧАЯ ЛЮБЫЕ ОБЩИЕ, СЛУЧАЙНЫЕ, СПЕЦИАЛЬНЫЕ ИЛИ ПОСЛЕДОВАВШИЕ УБЫТКИ, ВСЛЕДСТВИЕ 
ИСПОЛЬЗОВАНИЯ ИЛИ НЕВОЗМОЖНОСТИ ИСПОЛЬЗОВАНИЯ ПРОГРАММЫ (ВКЛЮЧАЯ, НО НЕ ОГРАНИЧИВАЯСЬ ПОТЕРЕЙ ДАННЫХ, ИЛИ 
ДАННЫМИ, СТАВШИМИ НЕПРАВИЛЬНЫМИ, ИЛИ ПОТЕРЯМИ ПРИНЕСЕННЫМИ ИЗ-ЗА ВАС ИЛИ ТРЕТЬИХ ЛИЦ, ИЛИ ОТКАЗОМ ПРОГРАММЫ 
РАБОТАТЬ СОВМЕСТНО С ДРУГИМИ ПРОГРАММАМИ), ДАЖЕ ЕСЛИ ТАКОЙ ВЛАДЕЛЕЦ ИЛИ ДРУГОЕ ЛИЦО БЫЛИ ИЗВЕЩЕНЫ О 
ВОЗМОЖНОСТИ ТАКИХ УБЫТКОВ.
'''

import MOD
import SER
import sms
import sms_prot
import sms_msg
import command
import config
import calendar
import gsm
import RX_API

#
# Defines
#
CFG = config.Config('settings.ini')
INPUTS = config.Config('inputs.ini')

#
# Variables
#
OUT1_OFF_TIME = 0;
OUT2_OFF_TIME = 0;

OUT1_STATE = 0
OUT2_STATE = 0

IN1_STATE = 0
IN2_STATE = 0
IN3_STATE = 0
IN4_STATE = 0
ADC_STATE = 0

ADC_LAST_VALUE = 0

IN1_DELAY = 0
IN2_DELAY = 0
IN3_DELAY = 0
IN4_DELAY = 0
ADC_DELAY = 0

REBOOT_COUNTER = 0
CALENDAR = 0

def executeCommand(command):
    global OUT1_STATE
    global OUT1_OFF_TIME
    global OUT2_STATE
    global OUT2_OFF_TIME
    ok = 0
    if(command.getCommand() == 'OUT1'):
        if(command.getParameter() == '0'):
            RX_API.setOUT1(0)
            OUT1_STATE = 0
            ok = 1
        if(command.getParameter() == '1'):
            RX_API.setOUT1(1)
            OUT1_STATE = 1
            OUT1_OFF_TIME = MOD.secCounter() + int(CFG.get('OUT1TIME'))
            ok = 1
        SER.send('Set OUT1 to %s\r' % (command.getParameter()))
    elif(command.getCommand() == 'OUT2'):
        if(command.getParameter() == '0'):
            RX_API.setOUT2(0)
            OUT2_STATE = 0
            ok = 1
        if(command.getParameter() == '1'):
            RX_API.setOUT2(1)
            OUT2_STATE = 1
            OUT2_OFF_TIME = MOD.secCounter() + int(CFG.get('OUT2TIME'))
            ok = 1
        SER.send('Set OUT2 to %s\r' % (command.getParameter()))
    elif(command.getCommand() == 'DEBUG'):
        CFG.set('DEBUG', command.getParameter())
        CFG.write()
        SER.send('DEBUG is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'REBOOTPERIOD'):
        CFG.set('REBOOTPERIOD', command.getParameter())
        CFG.write()
        SER.send('REBOOTPERIOD is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'ALIVESMS'):
        CFG.set('ALIVESMS', command.getParameter())
        CFG.write()
        SER.send('ALIVESMS is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'SAVEINPUTS'):
        CFG.set('SAVEINPUTS', command.getParameter())
        CFG.write()
        SER.send('SAVEINPUTS is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'ADC'):
        ADC_VALUE_NEW = RX_API.getADC() * 11
        SER.send('Current ADC value: %d\r' % (ADC_VALUE_NEW))
        return 'ADC=%d mV;' % (ADC_VALUE_NEW)
    elif(command.getCommand() == 'INPUTS'):
        ADC_VALUE = RX_API.getADC() * 11
        IN1_VALUE = RX_API.getSK1()
        IN2_VALUE = RX_API.getSK2()
        IN3_VALUE = RX_API.getCounter1()
        IN4_VALUE = RX_API.getCounter2()
        SER.send('Current IN1: %d, IN2: %d, IN3: %d, IN4: %d, ADC: %d\r' % (IN1_VALUE, IN2_VALUE, IN3_VALUE, IN4_VALUE, ADC_VALUE))
        return 'IN1=%d,IN2=%d,IN3=%d,IN4=%d,ADC=%d;' % (IN1_VALUE, IN2_VALUE, IN3_VALUE, IN4_VALUE, ADC_VALUE)
    elif(command.getCommand() == 'ADCTXTOVR'):
        CFG.set('ADCTXTOVR', command.getParameter())
        CFG.write()
        SER.send('ADCTXTOVR is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'ADCTXTUND'):
        CFG.set('ADCTXTUND', command.getParameter())
        CFG.write()
        SER.send('ADCTXTUND is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'ADCVAL'):
        CFG.set('ADCVAL', command.getParameter())
        CFG.write()
        SER.send('ADCVAL is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'ADCHYST'):
        CFG.set('ADCHYST', command.getParameter())
        CFG.write()
        SER.send('ADCHYST is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'ADCFRONT'):
        CFG.set('ADCFRONT', command.getParameter())
        CFG.write()
        SER.send('ADCFRONT is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'ADCDELAY'):
        CFG.set('ADCDELAY', command.getParameter())
        CFG.write()
        SER.send('ADCDELAY is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'PASS'):
        CFG.set('PASS', command.getParameter())
        CFG.write()
        SER.send('PASS is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'IN1ONTXT'):
        CFG.set('IN1ONTXT', command.getParameter())
        CFG.write()
        SER.send('IN1ONTXT is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'IN1OFFTXT'):
        CFG.set('IN1OFFTXT', command.getParameter())
        CFG.write()
        SER.send('IN1OFFTXT is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'IN2ONTXT'):
        CFG.set('IN2ONTXT', command.getParameter())
        CFG.write()
        SER.send('IN2ONTXT is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'IN2OFFTXT'):
        CFG.set('IN2OFFTXT', command.getParameter())
        CFG.write()
        SER.send('IN2OFFTXT is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'IN3ONTXT'):
        CFG.set('IN3ONTXT', command.getParameter())
        CFG.write()
        SER.send('IN3ONTXT is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'IN3OFFTXT'):
        CFG.set('IN3OFFTXT', command.getParameter())
        CFG.write()
        SER.send('IN3OFFTXT is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'IN4ONTXT'):
        CFG.set('IN4ONTXT', command.getParameter())
        CFG.write()
        SER.send('IN4ONTXT is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'IN4OFFTXT'):
        CFG.set('IN4OFFTXT', command.getParameter())
        CFG.write()
        SER.send('IN4OFFTXT is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'SMS_ACK'):
        CFG.set('SMS_ACK', command.getParameter())
        CFG.write()
        SER.send('SMS_ACK is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'IN1FRONT'):
        CFG.set('IN1FRONT', command.getParameter())
        CFG.write()
        SER.send('IN1FRONT is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'IN2FRONT'):
        CFG.set('IN2FRONT', command.getParameter())
        CFG.write()
        SER.send('IN2FRONT is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'IN3FRONT'):
        CFG.set('IN3FRONT', command.getParameter())
        CFG.write()
        SER.send('IN3FRONT is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'IN4FRONT'):
        CFG.set('IN4FRONT', command.getParameter())
        CFG.write()
        SER.send('IN4FRONT is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'IN1DELAY'):
        CFG.set('IN1DELAY', command.getParameter())
        CFG.write()
        SER.send('IN1DELAY is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'IN2DELAY'):
        CFG.set('IN2DELAY', command.getParameter())
        CFG.write()
        SER.send('IN2DELAY is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'IN3DELAY'):
        CFG.set('IN3DELAY', command.getParameter())
        CFG.write()
        SER.send('IN3DELAY is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'IN4DELAY'):
        CFG.set('IN4DELAY', command.getParameter())
        CFG.write()
        SER.send('IN4DELAY is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'OUT1TIME'):
        CFG.set('OUT1TIME', command.getParameter())
        CFG.write()
        SER.send('OUT1TIME is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'OUT2TIME'):
        CFG.set('OUT2TIME', command.getParameter())
        CFG.write()
        SER.send('OUT2TIME is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'WHITE'):
        CFG.set('WHITE', command.getParameter())
        CFG.write()
        SER.send('WHITE is set to: %s\r' % (command.getParameter()))
        ok = 1
    elif(command.getCommand() == 'ALERT'):
        CFG.set('ALERT', command.getParameter())
        CFG.write()
        SER.send('ALERT is set to: %s\r' % (command.getParameter()))
        ok = 1
    if(ok == 1):
        return 'CMD %s OK;' % (command.getCommand())
    else:
        return 'CMD %s ERR;' % (command.getCommand())

def sendAlert(text):
    for num in CFG.getList('ALERT'):
        RX_API.resetWDT()
        SER.send('Send alert to: %s\r' % (num))
        sms.sendSms(sms_msg.SmsMessage('0', num, '', text))

def initInputs():
    global IN1_STATE
    global IN2_STATE
    global IN3_STATE
    global IN4_STATE
    global ADC_STATE
    
    if(int(CFG.get('SAVEINPUTS')) > 0):
        IN1_STATE = int(INPUTS.get('IN1'))
        IN2_STATE = int(INPUTS.get('IN2'))
        IN3_STATE = int(INPUTS.get('IN3'))
        IN4_STATE = int(INPUTS.get('IN4'))
        ADC_STATE = int(INPUTS.get('ADC'))
    else:
        IN1_STATE = RX_API.getSK1()
        IN2_STATE = RX_API.getSK2()
        IN3_STATE = RX_API.getCounter1()
        if(IN3_STATE < 0):
            IN3_STATE = RX_API.getCounter1()
        IN4_STATE = RX_API.getCounter2()
        if(IN4_STATE < 0):
            IN4_STATE = RX_API.getCounter2()
        ADC_VALUE_NEW = RX_API.getADC() * 11
        if(ADC_VALUE_NEW > int(CFG.get('ADCVAL'))):
            ADC_STATE = 1
        else:
            ADC_STATE = 0

def ioProcessing():
    if((int(CFG.get('OUT1TIME')) > 0) and (MOD.secCounter() > OUT1_OFF_TIME) and (OUT1_STATE == 1)):
        executeCommand(command.Command('OUT1', '0'))
    if((int(CFG.get('OUT2TIME')) > 0) and (MOD.secCounter() > OUT2_OFF_TIME) and (OUT2_STATE == 1)):
        executeCommand(command.Command('OUT2', '0'))
        
    global IN1_STATE
    global IN2_STATE
    global IN3_STATE
    global IN4_STATE
    global ADC_STATE
    
    global IN1_DELAY
    global IN2_DELAY
    global IN3_DELAY
    global IN4_DELAY
    global ADC_DELAY

    if(MOD.secCounter() > IN1_DELAY):
        IN1_STATE_NEW = RX_API.getSK1()
        if((IN1_STATE_NEW != IN1_STATE) and (IN1_STATE_NEW >= 0)):
            MOD.sleep(20)
            IN1_STATE_NEW_CHECK = RX_API.getSK1()
            if(IN1_STATE_NEW == IN1_STATE_NEW_CHECK):
                IN1_STATE = IN1_STATE_NEW
                if((IN1_STATE_NEW == 1) and (int(CFG.get('IN1FRONT')) in [1, 3])):
                    IN1_DELAY = MOD.secCounter() + int(CFG.get('IN1DELAY'))
                    if(int(CFG.get('SAVEINPUTS')) > 0):
                        INPUTS.set('IN1', '1')
                        INPUTS.write()
                    SER.send('IN1 ON\r')
                    sendAlert(CFG.get('IN1ONTXT'))
                if((IN1_STATE_NEW == 0) and (int(CFG.get('IN1FRONT')) in [2, 3])):
                    IN1_DELAY = MOD.secCounter() + int(CFG.get('IN1DELAY'))
                    if(int(CFG.get('SAVEINPUTS')) > 0):
                        INPUTS.set('IN1', '0')
                        INPUTS.write()
                    SER.send('IN1 OFF\r')
                    sendAlert(CFG.get('IN1OFFTXT'))
    
    if(MOD.secCounter() > IN2_DELAY):
        IN2_STATE_NEW = RX_API.getSK2()
        if((IN2_STATE_NEW != IN2_STATE) and (IN2_STATE_NEW >= 0)):
            MOD.sleep(20)
            IN2_STATE_NEW_CHECK = RX_API.getSK2()
            if(IN2_STATE_NEW == IN2_STATE_NEW_CHECK):
                IN2_STATE = IN2_STATE_NEW
                if((IN2_STATE_NEW == 1) and (int(CFG.get('IN2FRONT')) in [1, 3])):
                    IN2_DELAY = MOD.secCounter() + int(CFG.get('IN2DELAY'))
                    if(int(CFG.get('SAVEINPUTS')) > 0):
                        INPUTS.set('IN2', '1')
                        INPUTS.write()
                    SER.send('IN2 ON\r')
                    sendAlert(CFG.get('IN2ONTXT'))
                if((IN2_STATE_NEW == 0) and (int(CFG.get('IN2FRONT')) in [2, 3])):
                    IN2_DELAY = MOD.secCounter() + int(CFG.get('IN2DELAY'))
                    if(int(CFG.get('SAVEINPUTS')) > 0):
                        INPUTS.set('IN2', '0')
                        INPUTS.write()
                    SER.send('IN2 OFF\r')
                    sendAlert(CFG.get('IN2OFFTXT'))
                
    if(MOD.secCounter() > IN3_DELAY):
        IN3_STATE_NEW = RX_API.getCounter1()
        if((IN3_STATE_NEW != IN3_STATE) and (IN3_STATE_NEW >= 0)):
            MOD.sleep(20)
            IN3_STATE_NEW_CHECK = RX_API.getCounter1()
            if(IN3_STATE_NEW == IN3_STATE_NEW_CHECK):
                IN3_STATE = IN3_STATE_NEW
                if((IN3_STATE_NEW == 1) and (int(CFG.get('IN3FRONT')) in [1, 3])):
                    IN3_DELAY = MOD.secCounter() + int(CFG.get('IN3DELAY'))
                    if(int(CFG.get('SAVEINPUTS')) > 0):
                        INPUTS.set('IN3', '1')
                        INPUTS.write()
                    SER.send('IN3 ON\r')
                    sendAlert(CFG.get('IN3ONTXT'))
                if((IN3_STATE_NEW == 0) and (int(CFG.get('IN3FRONT')) in [2, 3])):
                    IN3_DELAY = MOD.secCounter() + int(CFG.get('IN3DELAY'))
                    if(int(CFG.get('SAVEINPUTS')) > 0):
                        INPUTS.set('IN3', '0')
                        INPUTS.write()
                    SER.send('IN3 OFF\r')
                    sendAlert(CFG.get('IN3OFFTXT'))
                
    if(MOD.secCounter() > IN4_DELAY):
        IN4_STATE_NEW = RX_API.getCounter2()
        if((IN4_STATE_NEW != IN4_STATE) and (IN4_STATE_NEW >= 0)):
            MOD.sleep(20)
            IN4_STATE_NEW_CHECK = RX_API.getCounter2()
            if(IN4_STATE_NEW == IN4_STATE_NEW_CHECK):
                IN4_STATE = IN4_STATE_NEW
                if((IN4_STATE_NEW == 1) and (int(CFG.get('IN4FRONT')) in [1, 3])):
                    IN4_DELAY = MOD.secCounter() + int(CFG.get('IN4DELAY'))
                    if(int(CFG.get('SAVEINPUTS')) > 0):
                        INPUTS.set('IN4', '1')
                        INPUTS.write()
                    SER.send('IN4 ON\r')
                    sendAlert(CFG.get('IN4ONTXT'))
                if((IN4_STATE_NEW == 0) and (int(CFG.get('IN4FRONT')) in [2, 3])):
                    IN4_DELAY = MOD.secCounter() + int(CFG.get('IN4DELAY'))
                    if(int(CFG.get('SAVEINPUTS')) > 0):
                        INPUTS.set('IN4', '0')
                        INPUTS.write()
                    SER.send('IN4 OFF\r')
                    sendAlert(CFG.get('IN4OFFTXT'))
    
    if(MOD.secCounter() > ADC_DELAY):
        ADC_VALUE_NEW = RX_API.getADC() * 11
        if(ADC_VALUE_NEW > (int(CFG.get('ADCVAL')) + int(CFG.get('ADCHYST')))):
            ADC_STATE_NEW = 1
        elif(ADC_VALUE_NEW < (int(CFG.get('ADCVAL')) - int(CFG.get('ADCHYST')))):
            ADC_STATE_NEW = 0
        else:
            ADC_STATE_NEW = ADC_STATE
        if(ADC_STATE_NEW != ADC_STATE):
            ADC_STATE = ADC_STATE_NEW
            if((ADC_STATE_NEW == 1) and (int(CFG.get('ADCFRONT')) in [1, 3])):
                ADC_DELAY = MOD.secCounter() + int(CFG.get('ADCDELAY'))
                if(int(CFG.get('SAVEINPUTS')) > 0):
                    INPUTS.set('ADC', '1')
                    INPUTS.write()
                SER.send('ADC > VALUE + HYST\r')
                sendAlert(CFG.get('ADCTXTOVR'))
            if((ADC_STATE_NEW == 0) and (int(CFG.get('ADCFRONT')) in [2, 3])):
                ADC_DELAY = MOD.secCounter() + int(CFG.get('ADCDELAY'))
                if(int(CFG.get('SAVEINPUTS')) > 0):
                    INPUTS.set('ADC', '0')
                    INPUTS.write()
                SER.send('ADC < VALUE - HYST\r')
                sendAlert(CFG.get('ADCTXTUND'))

def smsProcessing():
    RX_API.resetWDT()
    message = sms.receiveSms()
    if message is not None:
        commands = sms_prot.parseCommand(CFG.get('PASS'), message.getText())
        if(len(commands) > 0):
            if(commands[0].getCommand() == 'WRONG_PASSWORD'):
                sms.sendSms(sms_msg.SmsMessage('0', message.getNumber(), '', 'WRONG PASSWORD'))
            else:
                result = ''
                for c in commands:
                    result = result + executeCommand(c)
                if(int(CFG.get('SMS_ACK')) > 0):
                    sms.sendSms(sms_msg.SmsMessage('0', message.getNumber(), '', result))
        sms.deleteSms(message.getId())

def ringProcessing():
    ring = gsm.checkRing()
    if(ring != ''):
        SER.send('Ringing with number: %s\r' % (ring))
        if(ring in CFG.getList('WHITE')):
            executeCommand(command.Command('OUT1', '1'))
        else:
            SER.send('Phone is not in Whitelist\r')
#         MOD.sleep(40)
        gsm.hangUp()
        
def rebootCounterProcessing(delta):
    global REBOOT_COUNTER
    global CALENDAR
    if((delta < 0) or (delta > 100)):
        delta = 5
    REBOOT_COUNTER = REBOOT_COUNTER + delta
    SER.send('Current reboot counter: %d\r' % REBOOT_COUNTER)
    if(REBOOT_COUNTER > int(CFG.get('REBOOTPERIOD'))):
        SER.send('Terminal reboot.\r')
        if(int(CFG.get('ALIVESMS')) > 0):
            CALENDAR = CALENDAR + 1
            calendar.writeCalendar(CALENDAR)
        MOD.sleep(30)
        gsm.reboot()
        
def calendarProcessing():
    global CALENDAR
    if(CALENDAR > (int(CFG.get('ALIVESMS')) - 1)):
        calendar.writeCalendar(0)
        CALENDAR = 0
        SER.send('Send heartbeat SMS\r')
        sendAlert('Device is alive.')
    
if __name__ == "__main__":
    try:
        RX_API.resetWDT()
        SER.set_speed('115200')
        
        CFG.read()
        CFG.dump()
        
        INPUTS.read()
        INPUTS.dump()
        
        SER.send('Start GSM init\r')
        gsm.init()
        
        SER.send('Start SMS init\r')
        sms.init()
        
        SER.send('IO init\r')
        RX_API.initIO()
        
        SER.send('Read init IO\r')
        initInputs()
        
        RX_API.resetWDT()
        
        if(int(CFG.get('ALIVESMS')) > 0):
            SER.send('Read calendar\r')
            global CALENDAR
            CALENDAR = calendar.readCalendar()
            
        SER.send('Wait for network registration\r')
        gsm.waitRegister()
        
        if(int(CFG.get('ALIVESMS')) > 0):
            SER.send('Calendar processing\r')
            calendarProcessing()
            
        SER.send('Start main loop\r')
        while(1):
            start = MOD.secCounter()
            RX_API.resetWDT()
            
            smsProcessing()
            RX_API.resetWDT()
            
            ringProcessing()
            ioProcessing()
            RX_API.resetWDT()
            
            if(int(CFG.get('REBOOTPERIOD')) > 0):
                rebootCounterProcessing(MOD.secCounter() - start)
    except Exception, e:
        SER.send('Unhandled exception, reboot: %s\r' % e)
        MOD.sleep(20)
        gsm.reboot()
        
        
