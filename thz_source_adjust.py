import serial

# COM port for the source
COM_port = 'COM3'


serialPort = serial.Serial( port=COM_port, baudrate=115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
print(f'{COM_port} is open', serialPort.isOpen())

serialPort.write(b'*IDN?\r')     
res = serialPort.read(100)    

# adjust the source power to :OUTPL:ATT {} dB
serialPort.write(b':OUTP:ATT 6\r')              

res = serialPort.read(100)            ###   always read a response after the write even if the command does not return anything.      

if res==b'\r':                                  ### empty string is returned if there should be no response and everything is OK
    print('OK')
else:
    print("Error code: "+ res.decode().strip())     ### error code is returned if something is wrong

serialPort.close()