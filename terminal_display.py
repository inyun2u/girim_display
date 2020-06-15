import sys
from PyQt5 import QtWidgets, uic, QtSerialPort, QtCore
from PyQt5.QtCore import QByteArray, QDate, QDateTime, QTime, QTimer
import struct
from PyQt5.QtGui import QPalette, QColor


class Ui(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Ui, self).__init__(*args, **kwargs)
        uic.loadUi('terminal_display.ui', self)

        self.serialData = QByteArray().append("created ")
        self.receivedData = QByteArray()
        self.transmitData = QByteArray()
        self.serialPort = QtSerialPort.QSerialPort()
        self.serialPort.setPortName("COM10")
        self.serialPort.setBaudRate(115200)
        self.serialPort.setFlowControl(self.serialPort.NoFlowControl)
        self.serialPort.setStopBits(self.serialPort.OneStop)

        self.serialPort.readyRead.connect(self.onreadyread)
        self.serialPort.bytesWritten.connect(self.onbyteswritten)

        ports = QtSerialPort.QSerialPortInfo.availablePorts()
        print(ports)

        for eachPort in ports:
            print(eachPort.portName())

        print("open : ", self.serialPort.open(QtCore.QIODevice.ReadWrite), self.serialPort.portName())

        self.packet = b''
        self.packetCounter=0

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        app.setPalette(palette)

        ''' 
        self.testTimer = QTimer()
        self.testTimer.setInterval(10)
        self.testTimer.timeout.connect(self.timeToSend)
        self.i=0
        self.counter=0
        self.formattedi=""
        self.bytearrayToSend=QByteArray(4,'a')
        self.testTimer.start()
        '''

        self.show()

    def timeToSend(self):
        self.bytearrayToSend.clear()
        formattedi = '%04d' % self.i
        self.bytearrayToSend.append(formattedi)
        print("go ", self.formattedi)
        print(self.bytearrayToSend)
        self.serialPort.writeData(self.bytearrayToSend)
        self.i = (self.i + 1) % 256

    def onbyteswritten(self, bytes):
        # self.serialPort.flush()
        # print("onbyteswritten",bytes)
        # print("bytestowrite",self.serialPort.bytesToWrite())
        # print(self.serialPort.readBufferSize())
        # print()
        pass

    def onreadyread(self):
        # self.serialPort.flush()
        self.receivedData = self.serialPort.readAll()
        while len(self.receivedData) > 64:
            index = self.receivedData.indexOf(b'\x14', 0)
            print("index : ", index, "len : ", len(self.packet))

            self.packet = self.receivedData[index:index + 64]
            self.packetCounter += 1

            print(self.packetCounter, "th packet", self.packet)

            print("remaining stream : ", len(self.receivedData), self.receivedData)
            self.receivedData = self.receivedData[index + 64:]
            print("after strip : ", len(self.receivedData), self.receivedData)
            if len(self.packet) == 64:
                self.parse()
            else:
                print("packet size miss, skip.")
        print()

    def parse(self):
        year = int.from_bytes(self.packet[0], "big")
        month = int.from_bytes(self.packet[1], "big")
        day = int.from_bytes(self.packet[2], "big")
        hour = int.from_bytes(self.packet[3], "big")
        minute = int.from_bytes(self.packet[4], "big")
        second = int.from_bytes(self.packet[5], "big")
        print(year, month, day, hour, minute, second)

        date = QDate(year + 2000, month, day)
        time = QTime(hour, minute, second)

        self.dateTimeEdit.setDate(date)
        self.dateTimeEdit.setTime(time)

        [index,
         gyrox, gyroy, gyroz,
         accx, accy, accz,
         magx, magy, magz,
         ch1_volt, ch1_amp,
         ch2_volt, ch2_amp] = \
            struct.unpack("iiiiiiiiiififi", self.packet[8:64])

        print("stream index : ", index)
        print("gyro : ", gyrox, gyroy, gyroz)
        print("acc : ", accx, accy, accz)
        print("mag : ", magx, magy, magz)
        print("ch1 : ", ch1_volt, ch1_amp)
        print("ch2 : ", ch2_volt, ch2_amp)

        self.Index_lineEdit.setText(str(index))

        self.lineEdit_Status_gyrox.setText(str(gyrox))
        self.lineEdit_Status_gyroy.setText(str(gyroy))
        self.lineEdit_Status_gyroz.setText(str(gyroz))

        self.lineEdit_Status_accx.setText(str(accx))
        self.lineEdit_Status_accy.setText(str(accy))
        self.lineEdit_Status_accz.setText(str(accz))

        self.lineEdit_Status_magx.setText(str(magx))
        self.lineEdit_Status_magy.setText(str(magy))
        self.lineEdit_Status_magz.setText(str(magz))

        self.lineEdit_Ch1_vol.setText(str(ch1_volt))
        self.lineEdit_Ch1_amp.setText(str(ch1_amp))

        self.lineEdit_Ch2_vol.setText(str(ch2_volt))
        self.lineEdit_Ch2_amp.setText(str(ch2_amp))

    def commandstart(self):
        print("command start")
        self.serialPort.writeData(b'\x01\x00')

    def commandstop(self):
        print("command stop")
        self.serialPort.writeData(b'\x00\x00')

    def SingleModeClicked(self, On):
        if On:
            print("Single mode on")
            self.serialPort.writeData(b'\x02\x00')
        else:
            print("Single mode off")

    def MultiModeClicked(self, On):
        if On:
            print("Multimode on")
            self.serialPort.writeData(b'\x02\x01')
        else:
            print("Multimode off")

    def changeIntensityValue(self, value):
        print("intensity value ", value)
        self.receivedData.clear()

        print("data to append : ", QByteArray.number(value, 16))

        print("QByteArray after append")
        self.receivedData.append(QByteArray.fromHex(QByteArray.number(3, 16)))
        self.receivedData.append(QByteArray.fromHex(QByteArray.number(value, 16)))
        print(self.receivedData)

        self.serialPort.writeData(self.receivedData)

        self.receivedData.clear()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = Ui()
    app.exec_()
