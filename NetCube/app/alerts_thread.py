import time  
from threading import Timer 

def display():  
    print(str('Activando Timer Hora:' + ' ' + time.strftime('%H:%M:%S')).center(50,"*"))  
  
##Lets make our timer run in intervals  
class RepeatTimer(Timer):  
    def run(self):
        print('Thread de escaneo de alertas encendido'.center(50,"#"))    
       # self.function(*self.args) 
        while not self.finished.wait(self.interval):
            display()   
            self.function(*self.args) 
            print(' ')  
