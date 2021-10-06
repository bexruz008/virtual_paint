from handTracker import *
import cv2
import mediapipe as mp
import numpy as np
import random

class ColorRect():
    def __init__(self, x, y, w, h, color, text=''):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.text=text
        
    
    def drawRect(self, img, text_color=(255,255,255), alpha=0.5, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8, thickness=2):
        #draw the box
        bg_rec = img[self.y : self.y + self.h, self.x : self.x + self.w]
        white_rect = np.ones(bg_rec.shape, dtype=np.uint8)
        white_rect[:] = self.color
        res = cv2.addWeighted(bg_rec, alpha, white_rect, 1-alpha, 1.0)
        
        # Putting the image back to its position
        img[self.y : self.y + self.h, self.x : self.x + self.w] = res

        #put the letter
        tetx_size = cv2.getTextSize(self.text, fontFace, fontScale, thickness)
        text_pos = (int(self.x + self.w/2 - tetx_size[0][0]/2), int(self.y + self.h/2 + tetx_size[0][1]/2))
        cv2.putText(img, self.text,text_pos , fontFace, fontScale,text_color, thickness)

    def isOver(self,x,y):
        if (self.x + self.w > x > self.x) and (self.y + self.h> y >self.y):
            return True
        return False


#initilize the habe detector
detector = HandTracker(detectionCon=0.8)

#initilize the camera 
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# creating canvas to draw on it
canvas = np.zeros((720,1280,3), np.uint8)

# define a previous point to be used with drawing a line
px,py = 0,0
#initial brush color
color = (255,0,0)
#####
brushSize = 5
eraserSize = 20
####
########### creating colors ########
colors = []
#random color
b = int(random.random()*255)-1
g = int(random.random()*255)
r = int(random.random()*255)
print(b,g,r)
colors.append(ColorRect(300,0,100,100, (b,g,r)))
#red
colors.append(ColorRect(400,0,100,100, (0,0,255)))
#blue
colors.append(ColorRect(500,0,100,100, (255,0,0)))
#green
colors.append(ColorRect(600,0,100,100, (0,255,0)))
#yellow
colors.append(ColorRect(700,0,100,100, (0,255,255)))
#erase (black)
colors.append(ColorRect(800,0,100,100, (0,0,0), "Eraser"))

#clear
clear = ColorRect(900,0,100,100, (100,100,100), "Clear")

########## pen sizes #######
pens = []
for i, penSize in enumerate(range(5,25,5)):
    pens.append(ColorRect(1100,50+100*i,100,100, (50,50,50), str(penSize)))

penLabel = ColorRect(1100, 0, 100, 50, color, 'Pen')


while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.resize(frame, (1280, 720))
    frame = cv2.flip(frame, 1)

    detector.findHands(frame)
    positions = detector.getPostion(frame, draw=False)
    upFingers = detector.getUpFingers(frame)
    if upFingers:
        x, y = positions[8][0], positions[8][1]
        if upFingers[1] and upFingers[2]:
            px, py = 0, 0
            ####### chose a color for drawing #######
            for cb in colors:
                if cb.isOver(x, y):
                    color = cb.color
            #Clear 
            if clear.isOver(x, y):
                canvas = np.zeros((720,1280,3), np.uint8)
            
            ##### pen sizes ######
            for pen in pens:
                if pen.isOver(x, y):
                    brushSize = int(pen.text)
            

        elif upFingers[1] and not upFingers[2]:
            #print('index finger is up')
            cv2.circle(frame, positions[8], brushSize, color,-1)
            #drawing on the canvas
            if px == 0 and py == 0:
                px, py = positions[8]
            if color == (0,0,0):
                cv2.line(canvas, (px,py), positions[8], color, eraserSize)
            else:
                cv2.line(canvas, (px,py), positions[8], color,brushSize)
            px, py = positions[8]

    ########### moving the draw to the main image #########
    canvasGray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(canvasGray, 20, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    frame = cv2.bitwise_and(frame, imgInv)
    frame = cv2.bitwise_or(frame, canvas)


    ########## pen colors' boxes #########
    for c in colors:
        c.drawRect(frame)
        cv2.rectangle(frame, (c.x, c.y), (c.x +c.w, c.y+c.h), (255,255,255), 2)

    clear.drawRect(frame)
    cv2.rectangle(frame, (clear.x, clear.y), (clear.x +clear.w, clear.y+clear.h), (255,255,255), 2)
    ########## brush size boxes ######
    penLabel.color = color
    penLabel.drawRect(frame)
    cv2.rectangle(frame, (penLabel.x, penLabel.y), (penLabel.x +penLabel.w, penLabel.y+penLabel.h), (255,255,255), 2)
    for pen in pens:
        pen.drawRect(frame)
        cv2.rectangle(frame, (pen.x, pen.y), (pen.x +pen.w, pen.y+pen.h), (255,255,255), 2)


    cv2.imshow('video', frame)
    #cv2.imshow('canvas', canvas)
    k= cv2.waitKey(1)
    if k == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()