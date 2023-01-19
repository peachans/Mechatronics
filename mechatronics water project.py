import cv2
import mediapipe
from gpiozero import LED
import time
water = LED(14)
soap = LED(15)
wind = LED(18)

#call function api of mediapipe
drawingModule = mediapipe.solutions.drawing_utils
handsModule = mediapipe.solutions.hands
#select camera output
capture = cv2.VideoCapture(1)
  
#function calculation distance between finger and the point
def distance(a,b,x,y):
D = ((a - x)**2+(b - y)**2)**0.5
# ((rx - soap_center_x)**2+(ry - soap_center_y)**2)**0.5
return D
  
frameWidth = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
frameHeight = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(frameWidth,frameHeight)
  
#adjust point position of each button
soap_button = [frameWidth*0.9,frameHeight*0.2]
wind_button = [frameWidth*0.2,frameHeight*0.2]
on_button = [frameWidth*0.3,frameHeight*0.8]
off_button = [frameWidth*0.7,frameHeight*0.8]
  
#points = ['soap_button','wind_button','on_button','off_button']
  
#store value in dict
button_points = {'soap_button':soap_button,'wind_button':wind_button
,'on_button':on_button,'off_button':off_button}
dis_points = {'soap_button':[],'wind_button':[],'on_button':[],'off_button':[]}
  
#set the status of application
soap_test = False
wind_test = False
water_out = False
water_status = True
  
#setting value of function
with handsModule.Hands(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=2) as hands:

while (True):
water.off()
ret, frame = capture.read()
image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
image = cv2.flip(image, -1)
results = hands.process(image)
image.flags.writeable = True
image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
  
if results.multi_hand_landmarks != None:
start_all_time = time.time()
water_out = True
water.on()

while water_out:
current_all_time = time.time()
ret, frame = capture.read()
image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
image = cv2.flip(image, -1)
  
results = hands.process(image)
  
image.flags.writeable = True
image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
  
if results.multi_hand_landmarks != None:
dis_points = {'soap_button':[],'wind_button':[],'on_button':[],'off_button':[]}
for num_hand in range(len(results.multi_hand_landmarks)):
hand_position_x = results.multi_hand_landmarks[num_hand].landmark[8].x
hand_position_y = results.multi_hand_landmarks[num_hand].landmark[8].y
hand_position_x=round(hand_position_x*frameWidth,2)
hand_position_y=round(hand_position_y*frameHeight,2)
for p in dis_points.keys():
dis_points[p].append(distance(hand_position_x,hand_position_y,button_points[p][0],button_points[p][1]))
#Check what function is pointed
for p in dis_points.keys():
if min(dis_points[p]) < 50:
if p == 'soap_button':
soap_test =True
start_time = time.time()
elif p == 'wind_button':
wind_test =True
start_time = time.time()
elif p == 'off_button':
water_status = False
water.off()
else:
water_status = True
water.on()
#Draw points on hand
for handLandmarks in results.multi_hand_landmarks:
drawingModule.draw_landmarks(image, handLandmarks, handsModule.HAND_CONNECTIONS,
drawingModule.DrawingSpec(color = (121,22,50),thickness = 3,circle_radius = 4),
drawingModule.DrawingSpec(color = (50,255,50)))
  
#Soap loop
while soap_test == True:
water.off()
soap.on()
ret, frame = capture.read()
image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
image = cv2.flip(image, -1)
  
results = hands.process(image)
  
image.flags.writeable = True
image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
  
frame = cv2.flip(frame, -1)
#put text during soap loop
#cv2.rectangle(image,(120,300),(1000,628),(255,255,255),-1)
cv2.putText(image, 'Soap Out',(round(frameWidth*0.25), round(frameHeight*0.5)),cv2.FONT_HERSHEY_PLAIN,4,(255,0,255),5)
cv2.imshow('Test hand', image)
cv2.waitKey(1)
current_time =time.time()
if current_time - start_time >2:
soap_test = False
start_all_time = time.time()
soap.off()
water_status = True
water.on()

#Wind loop
while wind_test == True:
water.off()
wind.on()
ret, frame = capture.read()
image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
image = cv2.flip(image, -1)
  
results = hands.process(image)
  
image.flags.writeable = True
image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
  
frame = cv2.flip(frame, -1)
#put text during wind loop
cv2.putText(image, 'Wind Activate!',(round(frameWidth*0.15), round(frameHeight*0.5)),cv2.FONT_HERSHEY_PLAIN,4,(255,144,90),5)
cv2.imshow('Test hand', image)
cv2.waitKey(1)
current_time =time.time()
if current_time - start_time >5:
wind_test = False
water_status = False
water.off()
wind.off()
start_all_time = time.time()
  
#put text during water on
#Soap position
cv2.circle(image, (round(soap_button[0]),round(soap_button[1])), 50, (255,0,255), -1)
cv2.putText(image, 'SOAP',(round(soap_button[0]-40),round(soap_button[1])+10),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),3)
#Wind position
cv2.circle(image, (round(wind_button[0]), round(wind_button[1])), 50, (255,144,90), -1)
cv2.putText(image, 'WIND',(round(wind_button[0])-40, round(wind_button[1])+10),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),3)
  
#Check water on or off
if water_status == True:
cv2.putText(image, 'Water ON',(round(frameWidth*0.3), round(frameHeight*0.7)),cv2.FONT_HERSHEY_PLAIN,4,(0,255,0),5)
cv2.putText(image, f'{round(current_all_time-start_all_time,2)} sec',(round(frameWidth*0.3), round(frameHeight*0.6)),cv2.FONT_HERSHEY_PLAIN,2,(255,255,255),3)
cv2.circle(image, (round(on_button[0]), round(on_button[1])), 40, (0,255,82), -1)
cv2.putText(image, 'ON',(round(frameWidth*0.265), round(frameHeight*0.83)),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),3)
cv2.circle(image, (round(off_button[0]), round(off_button[1])), 40, (154,154,255), -1)
cv2.putText(image, 'OFF',(round(frameWidth*0.65), round(frameHeight*0.83)),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),3)
else:
cv2.putText(image, 'Water OFF',(round(frameWidth*0.25), round(frameHeight*0.7)),cv2.FONT_HERSHEY_PLAIN,4,(0,0,255),5)
cv2.circle(image, (round(on_button[0]), round(on_button[1])), 40, (158,245,186), -1)
cv2.putText(image, 'ON',(round(frameWidth*0.265), round(frameHeight*0.83)),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),3)
cv2.circle(image, (round(off_button[0]), round(off_button[1])), 40, (0,0,255), -1)
cv2.putText(image, 'OFF',(round(frameWidth*0.65), round(frameHeight*0.83)),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),3)

cv2.waitKey(1)
cv2.imshow('Test hand', image)
if (current_all_time-start_all_time >6) and (results.multi_hand_landmarks == None):
water_out = False
water_status = True
#Standby Mode 
cv2.putText(image, 'Ready to start',(round(frameWidth*0.1), round(frameHeight*0.5)),cv2.FONT_HERSHEY_COMPLEX,2,(255,255,255),3)
cv2.putText(image, 'Present your hand',(round(frameWidth*0.1), round(frameHeight*0.7)),cv2.FONT_HERSHEY_SCRIPT_COMPLEX,2,(255,255,255),3)
cv2.imshow('Test hand', image)
if cv2.waitKey(1) == 27:
break

cv2.destroyAllWindows()
capture.release()