import aioblescan as aiobs
from aioblescan.plugins import EddyStone
import asyncio
import paho.mqtt.client as mqtt
import time
import aioblescan as aiobs
from aioblescan.plugins import EddyStone
import asyncio
import paho.mqtt.client as mqtt
import time
import numpy as np
from numpy import genfromtxt
val=""
g1=""



def on_message(client, userdata, message):

  global val
  global g1
  print("message received ", str(message.payload.decode("utf-8")))
  print("message topic=", message.topic)
  print("message qos=", message.qos)
  print("message retain flag=", message.retain)
  #time.sleep(5)
  print("sending publication")
  
  a =  str(message.payload.decode("utf-8"))
  b = a.split()
  new_list = []
  for item in b:
      new_list.append(float(item))
  currmax = new_list[0]
  currmin = new_list[1]
  currhum = new_list[2]
  formax = new_list[3]
  formin = new_list[4]
  forhum = new_list[5]
  current_steps=calculate(currmax, currmin, currhum)
  print("Current steps are:",current_steps)
  forcast_steps=calculate(formax, formin, forhum)
  print("Forcast steps are:",forcast_steps)
  
  '''if int(val) < current_steps:
     g1="Goal not achieved!Try harder!"
     print("Goal not achieved!Try harder!")
  else:
      g1="Goal achieved!Keep the good work!"      
      print("Goal achieved!Keep the good work!" )'''

  a = genfromtxt('Fake_Data.csv', delimiter=',')
  X=a[:,:4]
  Y=a[:,4]
  Theta=np.array([1215.23927059,41.13028054,-11.34748777,28.91362573])
  j=2*len(X)
  for i in range(len(X)):
		#counter+=1
      yhat = np.matmul(X[i], Theta.T)
      Cost=(1/(len(X)))*(Y-yhat)
		
      gradient = np.dot(Theta, yhat) /j
		
      Theta1 = (Theta.T - 0.001 * gradient)
      Theta2=Theta1.T
		
      predicted_steps = Theta2[0] + Theta2[1]*(X[i][1]) + Theta2[2]* float(X[i][2]) + Theta2[3]* float(X[i][3])
      print(" Highest temp is %f | Lowest temp %f | Humidity is %f " % (X[i][1],X[i][2],X[i][3]))
      print(" The step is : " ,predicted_steps)
      print(" The actual step is : " ,Y[i])
    
    
    
  
  
  '''client.loop_start()
  client.subscribe(subscribetopic)
  client.publish(publishtopic, val)
  #time.sleep(10)
  client.loop_stop()'''
  

def calculate(max, min, hum):
    steps = 1215.23927059 + (max*41.13028054) + (min*-11.34748777) + (hum*28.91362573)
    return steps
	
def calories(val):
    global g1
    richa = val.split('*')
    val1 = richa[0]
    val2 = richa[1]
    cal= 0.25*int(val2)
    upcal= 0.5*int(val1)
    total=cal + upcal
    g1= str(total) + "," + str(cal) + "," + str(upcal)
    print(g1) 
   


def _process_packet(data):
    global val
    global g1
    ev = aiobs.HCI_Event()
    xx = ev.decode(data)
    xx = EddyStone().decode(ev)
    

    if xx is not None:
        check = xx['url']
        if 'werock' in str(xx['url']):
            val = xx['url'][18:]
            print("{}".format(xx['url'][18:]))
            cals=calories(val)
            client.on_message = on_message
            client.loop_start()
            client.subscribe(subscribetopic)
            client.publish(publishtopic, g1)
            #time.sleep(10)
            client.loop_stop()
            


if __name__ == '__main__':
    broker_address = "192.168.4.1" #enter your broker address here
    subscribetopic = "testTopic1"
    publishtopic = "testTopic2"
    client = mqtt.Client("P1")
    client.on_message = on_message
    client.connect(broker_address)
    mydev = 0
    event_loop = asyncio.get_event_loop()
    mysocket = aiobs.create_bt_socket(mydev)
    fac = event_loop._create_connection_transport(mysocket, aiobs.BLEScanRequester, None, None)
    conn, btctrl = event_loop.run_until_complete(fac)
    btctrl.process = _process_packet
    btctrl.send_scan_request()
    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        print('Keyboard interrupt')
    finally:
        print('closing event loop')
        btctrl.stop_scan_request()
        conn.close()
        event_loop.close()

