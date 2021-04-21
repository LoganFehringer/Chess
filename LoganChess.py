
# initiate chessboard
from ChessBoard import ChessBoard
import subprocess, time
Board = ChessBoard()
import smbus
import math
from Adafruit_LED_Backpack import Matrix8x8
import I2C_LCD_Driver
from itertools import chain
# initiate stockfish chess engine

engine = subprocess.Popen(
    'stockfish',
    universal_newlines=True,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,shell=True)


I2C_address = 0x71# address of mux changed to avoid conflict with led driver
I2C_bus_number = 1
bus = smbus.SMBus(I2C_bus_number)
# this program scans 64 inputs on 4 MCP23017 port expanders and returns changes 
mbrd = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]   # mbrd is the 8 columns of the chess board this sets them to 11111111 : open w
chcol =["a","b","c","d","e","f","g","h",'x','y']
DEVICE = [0x21,0x22,0x23, 0x24]  # the 4 I2c Device address of the MCP23017s (A0-A2)
GPIOn = [0x12, 0x13]
IODIRA = 0x00 # APin direction register for first 8 ie 1 = input or 2= output
IODIRB = 0x01 # B Pin direction register
GPIOA  = 0x12 # Register for inputs
GPIOB  = 0x13 # B Register for inputs
GPPUA= 0x0C  # Register for Pull ups A
GPPUB= 0x0D  # Register for Pull ups B

for i in range(0,4):  
# Resets MCPs to begin program
  i2c_channel=2**(i+2) 
  bus.write_byte(I2C_address,i2c_channel)  # tell MUX to use this channel
  #for each of the 4 devices
  # Set all A 8 GPA pins as  input. ie set them to 1 oXFF = 11111111
  bus.write_byte_data(DEVICE[i],IODIRA,0xFF)
  # Set pull up on GPA pins .ie from default of 0 to 11111111
  bus.write_byte_data(DEVICE[i],GPPUA,0xFF)
  # Set all B 8 GPB pins as  input. ie set them to 1 oXFF = 11111111
  bus.write_byte_data(DEVICE[i],IODIRB,0xFF)
  # Set pull up on GPB pins .ie from default of 0 to 11111111
  bus.write_byte_data(DEVICE[i],GPPUB,0xFF)
#### End of Reed Setup
  
############################################################################ 
#initiate LED and LCD
############################################################################
display = Matrix8x8.Matrix8x8()
bus.write_byte(I2C_address,2)  
display.begin()
display.clear()
display.write_display()


lcd = I2C_LCD_Driver.lcd()
# Initialise the LCD display
lcd.lcd_clear()
lcd.lcd_display_string('Logan ChessBot Gen 1',1)
lcd.lcd_display_string('Welcome!',3,6)
time.sleep(6)


############################################################################
# defines LED funtions to turn on 1 LED or turn off all LED
############################################################################
def ledmx(x,y,z):
    if y == 8:
        y =0
    bus.write_byte(I2C_address,2)
    display.set_pixel(x, y, z)
    display.write_display()
def ledalloff():
    bus.write_byte(I2C_address,2)
    display.clear()
    display.write_display()
############################################################################
# turns int values into char to input into stockfish
############################################################################
def fixy(y):
    if y == 1:
        y ='1'
        return y
    elif y == 2:
        y = '2'
        return y
    elif y == 3:
        y = '3'
        return y
    elif y == 4:
        y = '4'
        return y
    elif y == 5:
        y = '5'
        return y
    elif y == 6:
        y = '6'
        return y
    elif y == 7:
        y = '7'
        return y
    elif y == 8:
        y = '8'
        return y
#############################################################################
#turns char values into Int for LEDs
#############################################################################
def ytoint(y):
    if y == '1':
        y =1
        return y
    elif y == '2':
        y = 2
        return y
    elif y == '3':
        y = 3
        return y
    elif y == '4':
        y = 4
        return y
    elif y == '5':
        y = 5
        return y
    elif y == '6':
        y = 6
        return y
    elif y == '7':
        y = 7
        return y
    elif y == '8':
        y = 8
        return y
##############################################################################
#Determines if the peice is taken for the computer
##############################################################################
def taken1():
 while True:
  # read the 8 registers
    for k in range(0,4):
      for l in range(2):  # for each MCP register A and B
          i2c_channel=2**(k+2) # calculates binary that gives channel pos, ie channel 0 is 0b00000001 and channel 4 is b0b00010000
          bus.write_byte(I2C_address,i2c_channel)  # tell MUX to use this channel

          a = bus.read_byte_data(DEVICE[k],GPIOn[l])
          if a != mbrd[(k*2)+l]: # there has been a change
            c = a ^ mbrd[(k*2)+l]  # bitwise operation copies the bit if it is set in one operand but not both.
            dirx = "Close"
            z=1
            
            if a > mbrd[(k*2)+l] :
              dirx = "Open"  # if the number gets bigger a 0 has changed to a 1
              z=0
            mbrd[(k*2)+l]=a 
            return dirx
###############################################################################
#Determines if the peice is taken for the player
###############################################################################
def Taken():
 while True:
  # read the 8 registers
    for k in range(0,4):
      for l in range(2):  # for each MCP register A and B
          i2c_channel=2**(k+2) # calculates binary that gives channel pos, ie channel 0 is 0b00000001 and channel 4 is b0b00010000
          bus.write_byte(I2C_address,i2c_channel)  # tell MUX to use this channel

          a = bus.read_byte_data(DEVICE[k],GPIOn[l])
          if a != mbrd[(k*2)+l]: # there has been a change
            c = a ^ mbrd[(k*2)+l]  # bitwise operation copies the bit if it is set in one operand but not both.
            dirx = "Close"
            z=1
            if a > mbrd[(k*2)+l] :
              dirx = "open"  # if the number gets bigger a 0 has changed to a 1
              z=0
              
            y = math.frexp(c)[1]  # calculates integer part of log base 2, which is binary bit position
            y = fixy(y)
            x= (k*2)+l
            ledmx(y,x,1)
            if dirx == 'open':
                move = [chcol[x]],[y]
                finishtake = ''.join(chain(*move))
                time.sleep(1)
                mbrd[(k*2)+l]=a
                return finishtake
###############################################################################
#Determines if the peice is placed by the player
###############################################################################
def Placed():
 while True:
  # read the 8 registers
    for k in range(0,4):
      for l in range(2):  # for each MCP register A and B
          i2c_channel=2**(k+2) # calculates binary that gives channel pos, ie channel 0 is 0b00000001 and channel 4 is b0b00010000
          bus.write_byte(I2C_address,i2c_channel)  # tell MUX to use this channel

          a = bus.read_byte_data(DEVICE[k],GPIOn[l])
          if a != mbrd[(k*2)+l]: # there has been a change
            if a > mbrd[(k*2)+l]:
                mbrd[(k*2)+l]=a
            if a < mbrd[(k*2)+l]:
                c = a ^ mbrd[(k*2)+l]  # bitwise operation copies the bit if it is set in one operand but not both.
                dirx = "Close"
                z=1
                y = math.frexp(c)[1]  # calculates integer part of log base 2, which is binary bit position
                x= (k*2)+l
                ledmx(y,x,1)
                time.sleep(1)
                y = fixy(y)
                if dirx == 'Close':
                    move = [chcol[x] , y]
                    finishplace = ''.join(chain(*move))
                    ledalloff()
                    mbrd[(k*2)+l]=a
                    lcd.lcd_display_string(finishplace, 3, 8)
                    time.sleep(1)
                    print finishplace
                    return finishplace
###############################################################################
#Determiens if the peice is properly placed for the computer
###############################################################################
def Placedforcomputer(finishplace):
 while True:
  # read the 8 registers
    for k in range(0,4):
      for l in range(2):  # for each MCP register A and B
          i2c_channel=2**(k+2) # calculates binary that gives channel pos, ie channel 0 is 0b00000001 and channel 4 is b0b00010000
          bus.write_byte(I2C_address,i2c_channel)  # tell MUX to use this channel
          a = bus.read_byte_data(DEVICE[k],GPIOn[l])
          if a != mbrd[(k*2)+l]: # there has been a change
            c = a ^ mbrd[(k*2)+l]  # bitwise operation copies the bit if it is set in one operand but not both.
            if a > mbrd[(k*2)+l]:
                mbrd[(k*2)+l]=a
            if a < mbrd[(k*2)+l]: 
                y = math.frexp(c)[1]  # calculates integer part of log base 2, which is binary bit position
                x= (k*2)+l
                dirx = "Close"
                y = fixy(y)
                move = [chcol[x] , y]
                finishplace1 = ''.join(chain(*move))
                if finishplace1 == finishplace:
                    mbrd[(k*2)+l]=a
                    return finishplace1
###############################################################################
#Turns on LED for column and row of piece to take for computer
###############################################################################            
def Astufftake(take_row):
    y= ytoint(take_row)
    for i in range(8):
        if y == 8:
            ledmx(0,0,1)
            if taken1() == 'Open':
                return 
        elif i == y:
            ledmx(i,0,1)
            if taken1() == 'Open':
                return
def Bstufftake(take_row):
    y= ytoint(take_row)
    for i in range(8):
        if y == 8:
            ledmx(0,1,1)
            if taken1() == 'Open':
                return 
        elif i == y:
            ledmx(i,1,1)
            if taken1() == 'Open':
                return
def Cstufftake(take_row):
    y= ytoint(take_row)
    for i in range(8):
        if y == 8:
            ledmx(0,2,1)
            if taken1() == 'Open':
                return 
        elif i == y:
            ledmx(i,2,1)
            if taken1() == 'Open':
                return 

def Dstufftake(take_row):
    y= ytoint(take_row)
    for i in range(8):
        if y == 8:
            ledmx(0,3,1)
            if taken1() == 'Open':
                return
        elif i == y:
            ledmx(i,3,1)
            if taken1() == 'Open':
                return
def Estufftake(take_row):
    y= ytoint(take_row)
    for i in range(8):
        if y == 8:
            ledmx(0,4,1)
            if taken1() == 'Open':
                return
        elif i == y:
            ledmx(i,4,1)
            if taken1() == 'Open':
                return
def Fstufftake(take_row):
    y= ytoint(take_row)
    for i in range(8):
        if y == 8:
            ledmx(0,5,1)
            if taken1() == 'Open':
                return
        elif i == y:
            ledmx(i,5,1)
            if taken1() == 'Open':
                return
def Gstufftake(take_row):
    y= ytoint(take_row)
    for i in range(8):
        if y == 8:
            ledmx(0,6,1)
            if taken1() == 'Open':
                return 
        elif i == y:
            ledmx(i,6,1)
            if taken1() == 'Open':
                return
def Hstufftake(take_row):
    y= ytoint(take_row)
    for i in range(8):
        if y == 8:
            ledmx(0,7,1)
            if taken1() == 'Open':
                return 
        elif i == y:
            ledmx(i,7,1)
            if taken1() == 'Open':
                return 
###############################################################################
#Turns off LED if piece is properly placed
###############################################################################

def Astuffplace(place_row):
    finishplace = ''.join(chain(['a',place_row]))
    y= ytoint(place_row)
    for i in range(8):
        if i == y:
            if i == 8:
                i = 0
            ledmx(i,0,1)
            z = Placedforcomputer(finishplace)
            if z == finishplace:
                time.sleep(1)
                ledalloff()
                return
def Bstuffplace(place_row):
    finishplace = ''.join(chain(['b',place_row]))
    y= ytoint(place_row)
    for i in range(8):
        if i == y:
            if i == 8:
                i = 0
            ledmx(i,1,1)
            z = Placedforcomputer(finishplace)
            if z == finishplace:
                time.sleep(1)
                ledalloff()
                return
def Cstuffplace(place_row):
    finishplace = ''.join(chain(['c',place_row]))
    y= ytoint(place_row)
    for i in range(8):
        if i == y:
            if i == 8:
                i = 0
            ledmx(i,2,1)
            z = Placedforcomputer(finishplace)
            if z == finishplace:
                time.sleep(1)
                ledalloff()
                return
def Dstuffplace(place_row):
    finishplace = ''.join(chain(['d',place_row]))
    y= ytoint(place_row)
    for i in range(8):
        if i == y:
            if i == 8:
                i = 0
            ledmx(i,3,1)
            z = Placedforcomputer(finishplace)
            if z == finishplace:
                time.sleep(1)
                ledalloff()
                return
def Estuffplace(place_row):
    finishplace = ''.join(chain(['e',place_row]))
    print finishplace
    y= ytoint(place_row)
    for i in range(8):
        if i == y:
            if i == 8:
                i = 0
            ledmx(i,4,1)
            z = Placedforcomputer(finishplace)
            if z == finishplace:
                time.sleep(1)
                ledalloff()
                return
def Fstuffplace(place_row):
    finishplace = ''.join(chain(['f',place_row]))
    y= ytoint(place_row)
    for i in range(8):
        if i == y:
            if i == 8:
                i = 0
            ledmx(i,5,1)
            z = Placedforcomputer(finishplace)
            if z == finishplace:
                time.sleep(1)
                ledalloff()
                return
def Gstuffplace(place_row):
    finishplace = ''.join(chain(['g',place_row]))
    y= ytoint(place_row)
    for i in range(8):
        if i == y:
            if i == 8:
                i = 0
            ledmx(i,6,1)
            z = Placedforcomputer(finishplace)
            if z == finishplace:
                time.sleep(1)
                ledalloff()
                return
def Hstuffplace(place_row):
    finishplace = ''.join(chain(['h',place_row]))
    y= ytoint(place_row)
    for i in range(8):
        if i == y:
            if i == 8:
                i = 0
            ledmx(i,7,1)
            z = Placedforcomputer(finishplace)
            if z == finishplace:
                time.sleep(1)
                ledalloff()
                return
###############################################################################
#takes the move from stockfish and tells player to pick up the peice
###############################################################################    

def EngineBoardTake(text):
    take_colume = text[0]
    take_row = text[1]
    if take_colume == 'a':
        Astufftake(take_row)
    elif take_colume == 'b':
        Bstufftake(take_row)
    elif take_colume == 'c':
        Cstufftake(take_row)
    elif take_colume == 'd':
        Dstufftake(take_row)
    elif take_colume == 'e':
        Estufftake(take_row)
    elif take_colume == 'f':
        Fstufftake(take_row)
    elif take_colume == 'g':
        Gstufftake(take_row)
    elif take_colume == 'h':
        Hstufftake(take_row)
###############################################################################
#takes move from stockfish and tells player to place the peice with LED
###############################################################################       
def EngineBoardPlace(text):
    Place_colume = text[2]
    Place_row = text[3]
    if Place_colume == 'a':
        Astuffplace(Place_row)
    elif Place_colume == 'b':
        Bstuffplace(Place_row)
    elif Place_colume == 'c':
        Cstuffplace(Place_row)
    elif Place_colume == 'd':
        Dstuffplace(Place_row)
    elif Place_colume == 'e':
        Estuffplace(Place_row)
    elif Place_colume == 'f':
        Fstuffplace(Place_row)
    elif Place_colume == 'g':
        Gstuffplace(Place_row)
    elif Place_colume == 'h':
        Hstuffplace(Place_row)  
        return True
    
###############################################################################
#gets the move from stockfish
###############################################################################
def get():
    
    # using the 'isready' command (engine has to answer 'readyok')
    # to indicate current last line of stdout
    stx=""
    engine.stdin.write('isready\n')
    print('\nengine:')
    while True :
        text = engine.stdout.readline().strip()
        if text == 'readyok':
            break
        if text !='':   
            print('\t'+text)
        if text[0:8] == 'bestmove':
        
            return text

def sget():
    
    # using the 'isready' command (engine has to answer 'readyok')
    # to indicate current last line of stdout
    stx=""
    engine.stdin.write('isready\n')
    print('\nengine:')
    while True :
        text = engine.stdout.readline().strip()
        #if text == 'readyok':
         #   break
        if text !='':   
            print('\t'+text)
        if text[0:8] == 'bestmove':
            mtext=text
            return mtext
###############################################################################
#sets matrix registars of current board placement
###############################################################################       
def getPhysB():
    for k in range(0,4):
      for l in range(2):
          i2c_channel=2**(k+2) # calculates binary that gives channel pos, ie channel 0 is 0b00000001 and channel 4 is b0b00010000
          bus.write_byte(I2C_address,i2c_channel) 
          a = bus.read_byte_data(DEVICE[k],GPIOn[l])
          mbrd[(k*2)+l]= a
    return mbrd
###############################################################################
#Gets move from player Firstmove = pick up Secondmove = placed
###############################################################################
def getboard():
    """ gets a text string from the board """
    lcd.lcd_clear()
    lcd.lcd_display_string("White's move...", 2, 4)
    if isCheck() == True:
        lcd.lcd_display_string("Check!" , 3,8)
        isGameOver()
    firstmove = Taken()
    lcd.lcd_display_string(firstmove, 3, 4)
    print(firstmove)
    secondmove = Placed()
    print(secondmove)
    command = 'm'+ firstmove+secondmove
    return command
    
def sendboard(stxt):
    """ sends a text string to the board """
    print("\n send to board: " +stxt)
###############################################################################
#Starts a new game with stockfish
###############################################################################
def newgame():
    setboard()
    skill = getSkill()
    get ()
    put('uci')
    get ()
    put('setoption name Skill Level value ' + skill)
    get ()
    put('setoption name Hash value 128')
    put('uci')
    get ()
    put('ucinewgame')
    Board.resetBoard()
    setboard()
    fmove=""
    return fmove

###############################################################################
#Resets the board registers and has player set the board up
###############################################################################
def setboard():
    global mbrd
    mbrd = [255,255,255,255,255,255,255,255]
    lcd.lcd_clear()
    lcd.lcd_display_string('Please set Board',2,2)
    while mbrd != [60,60,60,60,60,60,60,60]:
        # read the 8 registers
        for k in range(0,4):
           for l in range(2): # for each MCP register A and B
              i2c_channel=2**(k+2) # calculates binary that gives channel pos, ie channel 0 is 0b00000001 and channel 4 is b0b00010000
              bus.write_byte(I2C_address,i2c_channel)  # tell MUX to use this channel
              a = bus.read_byte_data(DEVICE[k],GPIOn[l])
              if a != mbrd[(k*2)+l]:
                c = a ^ mbrd[(k*2)+l]  # bitwise operation copies the bit if it is set in one operand but not both.
                dirx = "Close"
                z=1
                if a > mbrd[(k*2)+l] :
                  dirx = "open"  # if the number gets bigger a 0 has changed to a 1
                  z=0
                y = math.frexp(c)[1]  # calculates integer part of log base 2, which is binary bit position
                x= (k*2)+l
                if y == 8:
                    y = 0
                ledmx(y,x,z)
                mbrd[(k*2)+l]=a  # update the current state of the board
    ledalloff()
    lcd.lcd_clear()
    lcd.lcd_display_string('Thank you!', 2,4)
    time.sleep(2)
    

###############################################################################
#Gets computer move
###############################################################################
def bmove(fmove):
    global mbrd
    tempsave = getPhysB()
    lcd.lcd_clear()
    lcd.lcd_display_string("Black's Turn ...", 2,3)
    fmove=fmove
    # Get a move from the board
    brdmove = bmessage[1:5].lower()
    # now validate move
    # if invalid, get reason & send back to board
      #  Board.addTextMove(move)
    if Board.addTextMove(brdmove) == False :
                        etxt = "error"+ str(Board.getReason())+brdmove
                        lcd.lcd_display_string('Please return piece',2)
                        time.sleep(5)
                        mbrd = tempsave
                        Board.printBoard()
                        sendboard(etxt)
                        return fmove
                       
#  elif valid  make the move and send Fen to board
    else:
        Board.printBoard()
        print ("fmove")
        print(fmove)
        print ("brdmove")
        print(brdmove)
        fmove =fmove+" " +brdmove
        cmove = "position startpos moves"+fmove
        print (cmove)

        put(cmove)
        # send move to engine & get engines move
        
        put("go movetime " +movetime)
        text = sget()
        print (text)
        smove = text[9:13]
        hint = text[21:25]
        if Board.addTextMove(smove) != True :
                        stxt = "e"+ str(Board.getReason())+move
                        Board.printBoard()
                        sendboard(stxt)

        else:
                        temp=fmove
                        fmove =temp+" " +smove
                        stx = smove+hint      
                        sendboard(stx)
                        Board.printBoard()
                        EngineBoardTake(smove)
                        EngineBoardPlace(smove)
                        print ("computer move: " + smove)
                        return fmove
###############################################################################
#inputs PLayer move into 
###############################################################################        
def put(command):
    print('\nyou:\n\t'+command)
    engine.stdin.write(command+'\n')
###############################################################################
#Asks player to select level and sends back skill
###############################################################################
def getSkill():
    lcd.lcd_clear()
    lcd.lcd_display_string("Please select Level",1)
    lcd.lcd_display_string('Use King to select',2)
    lcd.lcd_display_string('a4=1 b4=2 c4=3 d4=4 ',3)
    lcd.lcd_display_string('e4=5 f4=6 g4=7 h4=8',4)
    skill = '10'
    while skill == '10':
        z =Placed()
        if z == 'a4':
            skill = '3'
            lcd.lcd_clear()
            lcd.lcd_display_string("Level 1")
            time.sleep(1)
        elif z== 'b4':
            skill = '6'
            lcd.lcd_clear()
            lcd.lcd_display_string("Level 2")
            time.sleep(1)
        elif z== 'c4':
            skill = '9'
            lcd.lcd_clear()
            lcd.lcd_display_string("Level 3")
            time.sleep(1)
        elif z == 'd4':
            skill = '11'
            lcd.lcd_clear()
            lcd.lcd_display_string("Level 4")
            time.sleep(1)
        elif z == 'e4':
            skill = '14'
            lcd.lcd_clear()
            lcd.lcd_display_string("Level 5")
            time.sleep(1)
        elif z == 'f4':
            skill = '17'
            lcd.lcd_clear()
            lcd.lcd_display_string("Level 6")
            time.sleep(1)
        elif z == 'g4':
            skill = '20'
            lcd.lcd_clear()
            lcd.lcd_display_string("Level 7")
            time.sleep(1)
        elif z == 'h4':
            skill = '20'
            lcd.lcd_clear()
            lcd.lcd_display_string("Level 8")
            time.sleep(1)
    return skill

###############################################################################
#Reset Function
###############################################################################
def Reset(finished):
    if finished == True:
        start()
    while True:
        lcd.lcd_clear()
        lcd.lcd_display_string('Restart game?',1,3)
        lcd.lcd_display_string('Yes = place a8',2,3)
        lcd.lcd_display_string('No = place h1',3,3)
        if Placed() == 'a8':
            start()
        if Placed() == 'h1':
            return
        
###############################################################################
#Determines Check
###############################################################################
def board_check_off():
  lcd.lcd_display_string("        ")

def isCheck():
  if (Board.isCheck()):
    return True
  else:
    board_check_off()   
###############################################################################
#Determines Game over and outputs results board
###############################################################################  
def isGameOver():
  if (Board.isGameOver()):
    Board.printBoard()
    result = Board.getGameResult()
    if   result == 1:
      board_mate_white()
      lcd.lcd_display_string('To restart move' ,1)
      lcd.lcd_display_string('peice from h1 to a8',2)
      while True:
          first = Taken()
          second = Placed()
          if first == 'h1':
              if second =='a8':
                  finished = True
                  Reset(finished)
    elif result == 2:
      board_mate_black()
      lcd.lcd_display_string('To restart move' ,1)
      lcd.lcd_display_string('peice from h1 to a8',2)
      while True:
          first = Taken()
          second = Placed()
          if first == 'h1':
              if second =='a8':
                  finished = True
                  Reset(finished)
    elif result == 3:
      board_draw_stalemate()
      lcd.lcd_display_string('To restart move' ,1)
      lcd.lcd_display_string('peice from h1 to a8',2)
      while True:
          first = Taken()
          second = Placed()
          if first == 'h1':
              if second =='a8':
                  finished = True
                  Reset(finished)
    elif result == 4:
      board_draw_fifty()
      lcd.lcd_display_string('To restart move' ,1)
      lcd.lcd_display_string('peice from h1 to a8',2)
      while True:
          first = Taken()
          second = Placed()
          if first == 'h1':
              if second =='a8':
                  finished = True
                  Reset(finished)
    elif result == 5:
      board_draw_repetition()
      lcd.lcd_display_string('To restart move' ,1)
      lcd.lcd_display_string('peice from h1 to a8',2)
      while True:
          first = Taken()
          second = Placed()
          if first == 'h1':
              if second =='a8':
                  finished = True
                  Reset(finished)
def board_mate_white():
  board_check_off()
  lcd.lcd_clear()
  lcd.lcd_display_string("CheckMate", 1 , 5)
  lcd.lcd_display_string("White Wins", 2 , 4)
  time.sleep(10)

def board_mate_black():
  board_check_off()
  lcd.lcd_clear()
  lcd.lcd_display_string("CheckMate", 1 , 5)
  lcd.lcd_display_string("Black Wins", 2 , 4)
  time.sleep(10)
def board_draw_stalemate():
  lcd.lcd_clear()
  lcd.lcd_display_string("Draw", 1 , 7)
  lcd.lcd_display_string("StaleMate", 2 , 5)
  time.sleep(10)
def board_draw_fifty():
  lcd.lcd_clear()
  lcd.lcd_display_string("Draw", 1 , 7)
  lcd.lcd_display_string("Fifty move rule ", 2 , 2)
  time.sleep(10)
def board_draw_repetition():
  lcd.lcd_clear()
  lcd.lcd_display_string("Draw", 1 , 7)
  lcd.lcd_display_string("3 repititions rule", 1 , 1)
  time.sleep(10)
###############################################################################
#Main 
###############################################################################
def start():
    global bmessage
    global movetime
    global move
    finished = False
    fmove = ''
    bmessage = ''
    movetime = "600"
    move = newgame()
    while True:
        # Get  message from board
        bmessage = getboard()  
        code = bmessage[0]
        restart = bmessage[1:5]
    
        fmove=fmove
        if restart == 'h1a8': Reset(finished)
        if code == 'm': fmove = bmove(fmove)
        else :  sendboard('error at option')


############################################################################
#Starts game
############################################################################
start()



#############################################################################\
#paosborne piChess github (ideas how to have the game run)
#mDobres MuxTesterly github (set up mux to use with board)
