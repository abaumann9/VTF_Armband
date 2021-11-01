import os
import pickle
from pathlib import Path

import tkinter
from tkinter import *
from tkinter import ttk
import tkinter.filedialog as filedialog

import bleak
import serial
import struct
import time
from PIL import ImageTk, Image
import threading

import asyncio
from bleak import BleakClient
from bleak import BleakScanner
from bleak import discover
import serial.tools.list_ports
from winrt import _winrt

import platform
import ast
import logging

#Lets tkinter.filedialog.askdirectory work (No Clue Why)
_winrt.uninit_apartment()

VTF_WRITE_UUID = 'd2411652-234a-11ec-9621-0242ac130002'
VTF_WRITE_SERVICE = 'b8aff320-234a-11ec-9621-0242ac130002'
ble_connected = False
ble_data_ready = False
ble_data = bytearray()

root = Tk()
root.geometry("1000x600")

serial_object = None
vibration_block_list = []
current_connections_list = []
pause_flag = 0
loop_flag = 0
go_flag = 0
real_time_flag = 0

current_directory = r'C:\Users\adamb\PycharmProjects\pythonProject'


def addGo():
    """Sets the go flag"""
    global go_flag
    go_flag = 1
    addVibrationBlock()


def addPause():
    """Sets the pause flag"""
    global pause_flag
    pause_flag = 1
    addVibrationBlock()


def addLoop():
    """Sets the loop flag"""
    global loop_flag
    loop_flag = 1
    addVibrationBlock()


def typeSelect():
    """Raises the programed or real"""
    global real_time_flag
    if input_type.get() == "Programed":
        control_frame.tkraise()
        real_time_flag = 0
        demo_list.configure(state=DISABLED)


    elif input_type.get() == "Real":
        demo_list.configure(state=DISABLED)
        real_time_frame.tkraise()
        real_time_flag = 1

    elif input_type.get() == "Demo":
        demo_frame.tkraise()
        demo_list.configure(state=NORMAL)


def programedType():
    """Switches listboxes from predefined to saved"""
    if programed_type.get() == "predef":
        predef_list.configure(state=NORMAL)
        saved_list.configure(state=DISABLED)

    elif programed_type.get() == "created":
        predef_list.configure(state=DISABLED)
        saved_list.configure(state=NORMAL)



def resetRealTimeScale():
    motor0_scale.set(0)
    motor1_scale.set(0)
    motor2_scale.set(0)
    motor3_scale.set(0)
    motor4_scale.set(0)
    motor5_scale.set(0)
    motor6_scale.set(0)
    motor7_scale.set(0)
    motor8_scale.set(0)
    motor9_scale.set(0)
    motor10_scale.set(0)
    motor11_scale.set(0)
    motor12_scale.set(0)


def clearVibrationBlock():
    """Clear the vibration boxes on the screen"""
    vibration_block_list.clear()
    drawBlocks()


def addVibrationBlock():
    """Will add a given vibration block command to the vib_dict"""
    global pause_flag
    global loop_flag
    global go_flag

    # Directory of all the commands to be displayed / executed
    vib_dict = {'Motors': [], 'Type': [], 'PredefName': [], 'PredefNum': [], 'SavedName': [], 'SavedNum': [], 'Pause': [],
                'Loops': [], 'labelnum': []}

    if pause_flag == 1:
        pause_flag = 0
        vib_dict['Type'].append('Pause')
        vib_dict['Pause'].append(pause_time.get())
        pause_time.set(0)
        pause_time_enter.delete(0, 'end')

    elif loop_flag == 1:
        loop_flag = 0
        vib_dict['Type'].append('Loop')
        vib_dict['Loops'].append(loop_time.get())
        loop_time.set(0)
        loop_time_enter.delete(0, 'end')

    elif go_flag == 1:
        go_flag = 0
        vib_dict['Type'].append('Go')


    else:
        for i in motor_select.curselection():
            vib_dict['Motors'].append(motor_select.get(i))

        vib_dict['Type'].append(programed_type.get())

        if programed_type.get() == 'predef':
            vib_dict['PredefName'].append(predef_list.get(predef_list.curselection()))
            vib_dict['PredefNum'].append(predef_list.curselection()[0])
        else:
            vib_dict['SavedName'].append(saved_list.get(saved_list.curselection()))
            vib_dict['SavedNum'].append(saved_list.curselection()[0])


    vibration_block_list.append(vib_dict)

    drawBlocks()

def deleteBlock(info):
    """Enables a block to be deleted by clicking on it twice"""
    for widget in block_frame.winfo_children():
        if widget is info.widget:
            i = len(vibration_block_list)-1
            while i >= 0:
                if vibration_block_list[i]['labelnum'] == widget.winfo_id():
                    vibration_block_list.pop(i)
                i = i - 1;

    drawBlocks()

def drawBlocks():
    """Will draw all the current commands on the screen """
    x_pos = 5
    y_pos = 5
    y_pos_max = 5
    i = 0

    for widget in block_frame.winfo_children():
        if isinstance(widget, tkinter.Label):
            widget.destroy()

    while i < len(vibration_block_list):

        if vibration_block_list[i]['Type'] == ['Pause']:
            block_info = "Pause for " + vibration_block_list[i]['Pause'][0] + " Second/s"

        elif vibration_block_list[i]['Type'] == ['Loop']:
            block_info = "Loop " + vibration_block_list[i]['Loops'][0] + " Time/s"

        elif vibration_block_list[i]['Type'] == ['Go']:
            block_info = "Execute\nPrevious Block/s"

        elif vibration_block_list[i]['Type'][0] == 'created':
            block_info = "Saved Block: "
            block_info += vibration_block_list[i]['SavedName'][0]

        else:
            # Get Motors

            block_info = "Motors: "
            for j in range(len(vibration_block_list[i]['Motors'])):
                block_info += vibration_block_list[i]['Motors'][j] + ' '

            block_info += '\n'

            if vibration_block_list[i]['Type'] == ['predef']:
                block_info += "Vibration Type: "
                block_info += vibration_block_list[i]['PredefName'][0]

        block_label = Label(block_frame, text=block_info, borderwidth=2, relief="solid", wraplength=400)

        block_label.place(x=x_pos, y=y_pos)
        block_label.bind("<Double-Button-1>", deleteBlock)
        vibration_block_list[i]['labelnum'] = block_label.winfo_id()
        block_frame.update()

        x_pos = x_pos + block_label.winfo_width() + 5

        if (block_label.winfo_height() > y_pos_max):
            y_pos_max = block_label.winfo_y()

        if x_pos > 790:
            block_label.destroy()
            x_pos = 5
            y_pos = y_pos_max + 50
            i = i - 1

        i = i + 1


def getMotorBinarySecond(motors):
    """Generates the binary information for the motors selected"""
    binary = 0
    for i in range(len(motors)):
        if motors[i] == "Motor 0":
            binary += (1 << 0)

        elif motors[i] == "Motor 1":
            binary += (1 << 1)

        elif motors[i] == "Motor 2":
            binary += (1 << 2)

        elif motors[i] == "Motor 3":
            binary += (1 << 3)

        elif motors[i] == "Motor 4":
            binary += (1 << 4)

        elif motors[i] == "Motor 5":
            binary += (1 << 5)

        elif motors[i] == "Motor 6":
            binary += (1 << 6)

        elif motors[i] == "Motor 7":
            binary += (1 << 7)

    return binary


def getMotorBinaryFirst(motors):
    binary = 0
    for i in range(len(motors)):
        if motors[i] == "Motor 8":
            binary += (1 << 0)

        elif motors[i] == "Motor 9":
            binary += (1 << 1)

        elif motors[i] == "Motor 10":
            binary += (1 << 2)

        elif motors[i] == "Motor 11":
            binary += (1 << 3)

        elif motors[i] == "Motor 12":
            binary += (1 << 4)

    return binary


def sendBlocks():
    """When the send data button is pushed this takes the data in the vib_dict
    Packages it appropriately and send is via serial com or BLE"""
    global ble_data_ready, ble_connected, ble_data
    data = bytearray()

    data.append(0x41)
    data.append(0x41)
    for i in range(len(vibration_block_list)):
        # Data Type
        vibe_type = vibration_block_list[i]['Type']

        if vibe_type == ['created']:

            saved_block = open(current_directory + '\\' + vibration_block_list[i]['SavedName'][0] + '.bin', 'rb')
            saved_data = saved_block.read()
            for byte in saved_data:
                data.append(byte)
            saved_block.close()

        else:
            data.append(0x73)
            data.append(0x73)

            if vibe_type == ['predef']:
                data.append(0x50)
                data.append((vibration_block_list[i]['PredefNum'][0]))
                data.append((getMotorBinaryFirst(vibration_block_list[i]['Motors'])))
                data.append((getMotorBinarySecond(vibration_block_list[i]['Motors'])))

            elif vibe_type == ['Go']:
                data.append(0x47)

            elif vibe_type == ['Pause']:
                data.append(0x53)
                pause_float = float(vibration_block_list[i]['Pause'][0])
                pause_int_ms = int(round(pause_float * 1000))
                pause_bytes = pause_int_ms.to_bytes(4, byteorder='little')
                data.append(pause_bytes[0])
                data.append(pause_bytes[1])
                data.append(pause_bytes[2])
                data.append(pause_bytes[3])

            elif vibe_type == ['Loop']:
                data.append(0x4C)
                data.append(int(vibration_block_list[i]['Loops'][0]))

            data.append(0x78)
            data.append(0x78)


    data.append(0x45)
    data.append(0x45)

    for byte in data:
        print(byte)

    if ble_connected:
        print("DATA SENT")
        for b in data:
            print(b)
            ble_data.append(b)
        ble_data_ready = True

    else:
        ser.write(data)

    data.clear()



def saveBlocks():
    """Will save the current displayed blocks as a binary file. No error checking exists"""
    file = tkinter.filedialog.asksaveasfile(mode='wb', defaultextension=".bin")
    data = bytearray()

    for i in range(len(vibration_block_list)):
        data.append(0x73)
        data.append(0x73)
        # Data Type
        vibe_type = vibration_block_list[i]['Type']
        if vibe_type == ['predef']:
            data.append(0x50)
            data.append((vibration_block_list[i]['PredefNum'][0]))
            data.append((getMotorBinaryFirst(vibration_block_list[i]['Motors'])))
            data.append((getMotorBinarySecond(vibration_block_list[i]['Motors'])))
        elif vibe_type == ['Go']:
            data.append(0x47)

        elif vibe_type == ['Pause']:
            data.append(0x53)
            pause_float = float(vibration_block_list[i]['Pause'][0])
            pause_int_ms = int(round(pause_float * 1000))
            pause_bytes = pause_int_ms.to_bytes(4, byteorder='little')
            data.append(pause_bytes[0])
            data.append(pause_bytes[1])
            data.append(pause_bytes[2])
            data.append(pause_bytes[3])

        elif vibe_type == ['Loop']:
            data.append(0x4C)
            data.append(int(vibration_block_list[i]['Loops'][0]))

        data.append(0x78)
        data.append(0x78)


    file.write(data)
    file.close()
    displaySavedBlocks()

def displaySavedBlocks():
    """Will display a saved blocks in the current directory"""
    saved_list.configure(state=NORMAL)
    for root, dirs, files in os.walk(current_directory):
        # select file name
        for file in files:
            # check the extension of files
            if file.endswith('.bin'):
                # print whole path of files
                #print(os.path.join(root, file))

                if Path(file).stem not in saved_choices:
                    saved_choices.append(Path(file).stem)
                    saved_list.insert(END, Path(file).stem)
    programedType()

serial_monitor_on = 0

def _on_mousewheel(event):
    """Allows the serial monitor to scroll no matter where is is"""
    global dataCanvas
    dataCanvas.yview_scroll(int(-1*(event.delta/120)), "units")

def startMonitor():
    """Creates a new frame that displays incoming serial data"""
    global serial_monitor_on
    global dataFrame, dataCanvas
    serial_monitor_on = 1
    monitor = tkinter.Toplevel()
    monitor.wm_title("Serial Monitor")
    monitor_frame = Frame(monitor)
    monitor_frame.pack(fill=BOTH, expand=YES)
    dataCanvas = Canvas(monitor_frame, width=850, height=400, bg="white", highlightthickness=0)
    dataCanvas.pack(fill=BOTH, expand=YES, side=LEFT)

    vsb = Scrollbar(monitor_frame, orient='vertical', command=dataCanvas.yview)
    vsb.pack(fill=BOTH, expand=NO, side=RIGHT)

    dataCanvas.config(yscrollcommand=vsb.set)
    dataCanvas.bind("<Enter>", lambda _: dataCanvas.bind_all('<MouseWheel>', _on_mousewheel))
    dataCanvas.bind("<Leave>", lambda _: dataCanvas.unbind_all('<MouseWheel>'))

    dataFrame = Frame(dataCanvas, bg='white')
    dataCanvas.create_window((10,0), window=dataFrame, anchor='nw')

def updateDataMonitor(data):
    """Updates the serial monitor with incoming data"""
    global dataFrame, dataCanvas
    Label(dataFrame, text=data, font=('Calibri', '13'), bg='white', justify='left').pack(anchor=NW)
    dataCanvas.config(scrollregion=dataCanvas.bbox('all'))



def changeWorkingDic():
    """Change The Working Directory"""
    global current_directory
    new_directory = filedialog.askdirectory(title='Select A New Working Directory', initialdir=current_directory)
    current_directory = new_directory
    displaySavedBlocks()



def sendRealTime(motor_num, percentage):
    """Sends the realtime data for a given motor each time a slider is changed"""
    global ble_data_ready, ble_connected, ble_data
    data = bytearray()

    data.append(0x41)
    data.append(0x41)
    data.append(0x73)
    data.append(0x73)

    data.append(0x52)

    motor_val = motor_num.to_bytes(1, byteorder='big')

    data.append(motor_val[0])

    value = round(((int(percentage) / 200) * 255))

    if value == 1:
        value = 0

    intensity = value.to_bytes(1, byteorder='big')
    # print(test[0])

    data.append(intensity[0])
    data.append(0x78)
    data.append(0x78)
    data.append(0x45)
    data.append(0x45)

    if ble_connected:
        print("DATA SENT")
        for b in data:
            print(b)
            ble_data.append(b)
        ble_data_ready = True

    else:
        ser.write(data)
    data.clear()

def send_demo():
    global ble_data_ready, ble_connected, ble_data
    data = bytearray()

    data.append(0x41)
    data.append(0x41)
    data.append(0x73)
    data.append(0x73)

    data.append(0x44)
    data.append(demo_list.curselection()[0])
    print(demo_list.curselection()[0])

    data.append(0x78)
    data.append(0x78)
    data.append(0x45)
    data.append(0x45)

    if ble_connected:
        for b in data:
            ble_data.append(b)
        ble_data_ready = True

    else:
        ser.write(data)
    data.clear()

def readData():
    """Reads any serial data sent and prints it"""
    global serial_object, ble_connected, serial_monitor_on
    while 1:
        try:
            serial_data = ser.readline()
            message = serial_data.decode('utf8')

            print(message)

            if serial_monitor_on == 1:
                updateDataMonitor(message.rstrip('\n'))

        except:
            status_bar_update_ser(0, ser.name)
            ser.close()


def startBLE():
    """Starts a thread for BLE"""
    threading.Thread(target=goBLE, daemon=True).start()


def goBLE():
    """Starts the asynchronous function connect_ble
    asynchronous must be used as per bleak"""
    ble_devices = asyncio.run(connect_ble())


async def connect_ble():
    """Finds & connects to the nano 33 BLE then writes information to BLE
    characteristic when prompted"""
    global ble_connected, ble_data_ready, ble_data
    print('Looking for Arduino Nano 33 BLE Sense Peripheral Device...')
    found = False
    devices = await discover()
    for d in devices:
        if 'Nano 33 BLE' in d.name:
            print('Found Arduino Nano 33 BLE Sense Peripheral')
            print(d.details)
            found = True
            async with BleakClient(d.address) as client:
                print(f'Connected to {d.address}')
                ble_connected = True
                status_bar_update_ble(1)
                while True:
                    if ble_data_ready:
                        try:
                            await client.write_gatt_char(VTF_WRITE_SERVICE, ble_data, True)
                            ble_data.clear()
                            ble_data_ready = False

                        except:
                            status_bar_update_ble(0)
                            ble_connected = False
                            break

    if not found:
        print('Could not find Arduino Nano 33 BLE Sense Peripheral')

    return devices


async def find_ble():
    """Find current BLE devices that can be connected to"""
    devices = await discover()
    return devices


def startSerial(com):
    """Start serial communications at a given port baud is set at 9600"""
    global ser
    ser = serial.Serial(port=com, baudrate=9600, timeout=10)
    if ser:
        status_bar_update_ser(1, com)
        threading.Thread(target=readData, daemon=True).start()


def refreshDevices():
    """Updates a list of current available ports and BLE devices"""
    ports = serial.tools.list_ports.comports()

    for com in ports:
        usb_menu.add_command(label=com[0], command=lambda: startSerial(com[0]))

    ble_ports = asyncio.run(find_ble())
    for d in ble_ports:
        if d.name != "":
            ble_menu.add_command(label=d.name, command=startBLE)


def status_bar_update_ble(connected):
    """Updates when a BLE devices is connected/disconnected"""
    if connected:
        menubar.add_command(label="Nano 33 BLE")
    else:
        menubar.delete("Nano 33 BLE")
    menubar.update()


def status_bar_update_ser(connected, com):
    """Updates when a serial devices is connected/disconnected"""
    if connected:
        menubar.add_command(label=com)
    else:
        menubar.delete(com)
    menubar.update()


# Setup Frames
block_frame = LabelFrame(root, text="Vibration Blocks", width=795, height=313)
arm_frame = LabelFrame(root, text="Armband", width=300, height=313)
type_frame = LabelFrame(root, text="Type", width=50, height=287)
control_frame = LabelFrame(root, text="Control", width=890, height=287)
real_time_frame = LabelFrame(root, text="Real Time", width=950, height=287)
demo_frame = LabelFrame(root, text="Demo", width=890, height=287)

# Place Frames
block_frame.grid(row=0, column=0, sticky="nw", padx=5)
block_frame.grid_propagate(False)
arm_frame.grid(row=0, column=1, sticky="ne", padx=5)
type_frame.grid(row=1, column=0, sticky="nw", padx=5)
control_frame.grid(row=1, columnspan=2, sticky="sne", padx=5)
real_time_frame.grid(row=1, columnspan=2, sticky="sne", padx=5)
demo_frame.grid(row=1, columnspan=2, sticky="sne", padx=5)
demo_frame.grid_propagate(False)

control_frame.tkraise()

# Add armband photo
arm_band_image = ImageTk.PhotoImage(Image.open("armband.jpg"))
arm_band_image_label = Label(arm_frame, image=arm_band_image)
arm_band_image_label.pack()

########################################################################################################################
# MENU
########################################################################################################################
menubar = Menu(root)
file_menu = Menu(menubar, tearoff=0)
file_menu.add_command(label="Change Working Directory", command=changeWorkingDic)
file_menu.add_command(label="Serial Monitor", command=startMonitor)

connect_menu = Menu(menubar, tearoff=0)
connect_menu.add_command(label="Refresh Devices", command=refreshDevices)
connect_menu.add_separator()
usb_menu = Menu(menubar, tearoff=0)
ble_menu = Menu(menubar, tearoff=0)

connect_menu.add_cascade(label="USB", menu=usb_menu)
connect_menu.add_cascade(label="BLE", menu=ble_menu)

menubar.add_cascade(label="File", menu=file_menu)
menubar.add_cascade(label="Connect", menu=connect_menu)
menubar.add_command(label="                  ")
menubar.add_command(label="Connected Devices:")


root.config(menu=menubar)

########################################################################################################################
# Block Frame
########################################################################################################################
send_data_button = Button(block_frame, text="Send Blocks", command=sendBlocks)
send_data_button.place(x=710, y=260)

clear_data_button = Button(block_frame, text="Clear Blocks", command=clearVibrationBlock)
clear_data_button.place(x=630, y=260)

save_data_button = Button(block_frame, text="Save Blocks", command=saveBlocks)
save_data_button.place(x=550, y=260)

########################################################################################################################
# Control Frame
########################################################################################################################

# RADIO BUTTONS #
# Define Radio Buttons
input_type = StringVar()
programed_radio_button = Radiobutton(type_frame, text="Programed", variable=input_type, value='Programed',
                                     command=typeSelect)
real_time_radio_button = Radiobutton(type_frame, text="Real Time", variable=input_type, value='Real',
                                     command=typeSelect)
demo_radio_button = Radiobutton(type_frame, text="Demo", variable=input_type, value='Demo', command=typeSelect)

# Place Radio buttons
programed_radio_button.grid(row=0, column=0, padx=2, pady=2, stick="w")
real_time_radio_button.grid(row=1, column=0, padx=2, pady=2, stick="w")
demo_radio_button.grid(row=3, column=0, padx=2, pady=2, stick="w")

# Motor select
choices = ["Motor 0", "Motor 1", "Motor 2", "Motor 3", "Motor 4", "Motor 5", "Motor 6", "Motor 7", "Motor 8", "Motor 9",
           "Motor 10", "Motor 11", "Motor 12"]
choicesvar = StringVar(value=choices)
motor_select = Listbox(control_frame, height=13, listvariable=choicesvar, selectmode="multiple", exportselection=False)
motor_select.grid(row=0, rowspan=13, column=1, stick="n", padx=2, pady=2)

# Define Type Buttons
programed_type = StringVar()
predefined_radio_button = Radiobutton(control_frame, text="Pre Defined", variable=programed_type, value='predef',
                                      command=programedType)
create_radio_button = Radiobutton(control_frame, text="Saved", variable=programed_type, value='created',
                                  command=programedType)
programed_type.set('predef')

predefined_radio_button.grid(row=0, column=2, padx=2, pady=2, stick="w")
create_radio_button.grid(row=1, column=2, padx=2, pady=2, stick="w")


# Predefined function
predef_choices = ["Strong Click - 100%", "Strong Click - 60%", "Strong Click - 30%", "Sharp Click - 100%",
                  "Sharp Click - 60% ", "Sharp Click - 30%", "Soft Bump - 100%", "Soft Bump - 60%", "Soft Bump - 30%",
                  "Double Click - 100%", "Double Click - 60%", "Triple Click - 100%", "Soft Fuzz - 60%",
                  "Strong Buzz - 100%", "750 ms Alert 100%", "1000 ms Alert 100%", "Strong Click 1 - 100% ",
                  "Strong Click 2 - 80%", "Strong Click 3 - 60%", "Strong Click 4 - 30%", "Medium Click 1 - 100%",
                  "Medium Click 2 - 80%", "Medium Click 3 - 60%", "Sharp Tick 1 - 100%", "Sharp Tick 2 - 80%",
                  "Sharp Tick 3 – 60%", "Short Double Click Strong 1 – 100%", "Short Double Click Strong 2 – 80%",
                  "Short Double Click Strong 3 – 60%", "Short Double Click Strong 4 – 30%",
                  "Short Double Click Medium 1 – 100%", "Short Double Click Medium 2 – 80%",
                  "Short Double Click Medium 3 – 60%", "Short Double Sharp Tick 1 – 100%",
                  "Short Double Sharp Tick 2 – 80%", "Short Double Sharp Tick 3 – 60%",
                  "Long Double Sharp Click Strong - 100%", "Long Double Sharp Click Strong 2 - 80%",
                  "Long Double Sharp Click Strong 3 – 60%", "Long Double Sharp Click Strong 4 – 30%",
                  "Long Double Sharp Click Medium 1 – 100%", "Short Double Click Medium 2 – 80%",
                  "Long Double Sharp Click Medium 3 – 60%", "Long Double Sharp Tick 1 – 100%",
                  "Long Double Sharp Tick 2 – 80%", "Long Double Sharp Tick 3 – 60%", "Buzz 1 – 100%",
                  "Buzz 2 – 80%", "Buzz 3 – 60%", "Buzz 4 – 40%", "Buzz 5 – 20%", "Pulsing Strong 1 – 100%",
                  "Pulsing Strong 2 – 60%", "Pulsing Medium 1 – 100%", "Pulsing Medium 2 – 60%",
                  "Pulsing Sharp 1 – 100%", "Pulsing Sharp 2 – 60%", "Transition Click 1 – 100%",
                  "Transition Click 2 – 80%", "Transition Click 3 – 60%", "Transition Click 4 – 40%",
                  "Transition Click 5 – 20%", "Transition Click 6 – 10%", "Transition Hum 1 – 100%",
                  "Transition Hum 2 – 80%", "Transition Hum 3 – 60% ", "Transition Hum 4 – 40%",
                  "Transition Hum 5 – 20%", "Transition Hum 6 – 10%", "Transition Ramp Down Long Smooth 1 – 100 to 0%",
                  "Transition Ramp Down Long Smooth 2 – 100 to 0%", "Transition Ramp Down Medium Smooth 1 – 100 to 0%",
                  "Transition Ramp Down Medium Smooth 2 – 100 to 0%", "Transition Ramp Down Short Smooth 1 – 100 to 0%",
                  "Transition Ramp Down Short Smooth 2 – 100 to 0%", "Transition Ramp Down Long Sharp 1 – 100 to 0%",
                  "Transition Ramp Down Long Sharp 2 – 100 to 0% ", "Transition Ramp Down Medium Sharp 1 – 100 to 0% ",
                  "Transition Ramp Down Medium Sharp 2 – 100 to 0%", "Transition Ramp Down Short Sharp 1 – 100 to 0%",
                  "Transition Ramp Down Short Sharp 2 – 100 to 0%", "Transition Ramp Up Long Smooth 1 – 0 to 100%",
                  "Transition Ramp Up Long Smooth 2 – 0 to 100%", "Transition Ramp Up Medium Smooth 1 – 0 to 100%",
                  "Transition Ramp Up Medium Smooth 2 – 0 to 100%", "Transition Ramp Up Short Smooth 1 – 0 to 100%",
                  "Transition Ramp Up Short Smooth 2 – 0 to 100%", "Transition Ramp Up Long Sharp 1 – 0 to 100%",
                  "Transition Ramp Up Long Sharp 2 – 0 to 100%", "Transition Ramp Up Medium Sharp 1 – 0 to 100%",
                  "Transition Ramp Up Medium Sharp 2 – 0 to 100%", "Transition Ramp Up Short Sharp 1 – 0 to 100%",
                  "Transition Ramp Up Short Sharp 2 – 0 to 100%", "Transition Ramp Down Long Smooth 1 – 50 to 0%",
                  "Transition Ramp Down Long Smooth 2 – 50 to 0%", "Transition Ramp Down Medium Smooth 1 – 50 to 0%",
                  "Transition Ramp Down Medium Smooth 2 – 50 to 0%", "Transition Ramp Down Short Smooth 1 – 50 to 0%",
                  "Transition Ramp Down Short Smooth 2 – 50 to 0%", "Transition Ramp Down Long Sharp 1 – 50 to 0%",
                  "Transition Ramp Down Long Sharp 2 – 50 to 0%", "Transition Ramp Down Medium Sharp 1 – 50 to 0%",
                  "Transition Ramp Down Medium Sharp 2 – 50 to 0%", "Transition Ramp Down Short Sharp 1 – 50 to 0%",
                  "Transition Ramp Down Short Sharp 2 – 50 to 0%", "Transition Ramp Up Long Smooth 1 – 0 to 50%",
                  "Transition Ramp Up Long Smooth 2 – 0 to 50%", "Transition Ramp Up Medium Smooth 1 – 0 to 50%",
                  "Transition Ramp Up Medium Smooth 2 – 0 to 50%", "Transition Ramp Up Short Smooth 1 – 0 to 50%",
                  "Transition Ramp Up Short Smooth 2 – 0 to 50%", "Transition Ramp Up Long Sharp 1 – 0 to 50%",
                  "Transition Ramp Up Long Sharp 2 – 0 to 50%", "Transition Ramp Up Medium Sharp 1 – 0 to 50%",
                  "Transition Ramp Up Medium Sharp 2 – 0 to 50%", "Transition Ramp Up Short Sharp 1 – 0 to 50%",
                  "Transition Ramp Up Short Sharp 2 – 0 to 50%", "Long buzz for programmatic stopping – 100%",
                  "Smooth Hum 1 (No kick or brake pulse) – 50%", "Smooth Hum 2 (No kick or brake pulse) – 40%",
                  "Smooth Hum 3 (No kick or brake pulse) – 30%", "Smooth Hum 4 (No kick or brake pulse) – 20%",
                  "Smooth Hum 5 (No kick or brake pulse) – 10%"]

predef_choicesvar = StringVar(value=predef_choices)
predef_list = Listbox(control_frame, height=15, width=40, listvariable=predef_choicesvar, exportselection=False)
predef_list.grid(row=0, rowspan=15, column=3, stick="n", padx=2, pady=2)

# scroll bar
predef_scrollbar = Scrollbar(control_frame, orient="vertical", command=predef_list.yview)
predef_scrollbar.grid(row=0, rowspan=15, column=4, stick="nsw")
predef_list.config(yscrollcommand=predef_scrollbar.set)

# Create scale bars

saved_choices = []
saved_choicesvar = StringVar(value=saved_choices)
saved_list = Listbox(control_frame, height=15, width=19, listvariable=saved_choicesvar, exportselection=False)
saved_list.grid(row=0, rowspan=15, column=5, stick="n", padx=5, pady=2)
displaySavedBlocks()

programedType()


# Add Created
add_created_button = Button(control_frame, text="Add Created \n Vibration to Que", command=addVibrationBlock)
add_created_button.grid(row=3, column=7, padx=2)


# loop go and pause buttons
pause_time = StringVar()
pause_time_enter = Entry(control_frame, textvariable=pause_time, width=10)
pause_time_add_button = Button(control_frame, text="Add Pause to Que", command=addPause)

loop_time = StringVar()
loop_time_enter = Entry(control_frame, textvariable=loop_time, width=10)
loop_time_add_button = Button(control_frame, text="Add Loop Number to Que", command=addLoop)

go_button = Button(control_frame, text="Execute\nPrevious Blocks", command=addGo)

pause_time_enter.grid(row=1, column=8, padx=10)
pause_time_add_button.grid(row=2, column=8, padx=10)

loop_time_enter.grid(row=3, column=8, padx=10)
loop_time_add_button.grid(row=4, column=8, padx=10)

go_button.grid(row=8, column=8, padx=10)


########################################################################################################################
# Real Time Frame
########################################################################################################################
def motor_0_change(percentage):
    sendRealTime(0, percentage)


def motor_1_change(percentage):
    sendRealTime(1, percentage)


def motor_2_change(percentage):
    sendRealTime(2, percentage)


def motor_3_change(percentage):
    sendRealTime(3, percentage)


def motor_4_change(percentage):
    sendRealTime(4, percentage)


def motor_5_change(percentage):
    sendRealTime(5, percentage)


def motor_6_change(percentage):
    sendRealTime(6, percentage)


def motor_7_change(percentage):
    sendRealTime(7, percentage)


def motor_8_change(percentage):
    sendRealTime(8, percentage)


def motor_9_change(percentage):
    sendRealTime(9, percentage)


def motor_10_change(percentage):
    sendRealTime(10, percentage)


def motor_11_change(percentage):
    sendRealTime(11, percentage)


def motor_12_change(percentage):
    sendRealTime(12, percentage)


# Create Scales & Lables
motor_0_percentage = IntVar(value=0)
motor0_scale = Scale(real_time_frame, orient=VERTICAL, length=200, from_=100, to=0, variable=motor_0_percentage,
                     command=motor_0_change)
motor0_scale_label = Label(real_time_frame, text="Motor 0 %")

motor_1_percentage = IntVar(value=0)
motor1_scale = Scale(real_time_frame, orient=VERTICAL, length=200, from_=100, to=0, variable=motor_1_percentage,
                     command=motor_1_change)
motor1_scale_label = Label(real_time_frame, text="Motor 1 %")

motor_2_percentage = IntVar(value=0)
motor2_scale = Scale(real_time_frame, orient=VERTICAL, length=200, from_=100, to=0, variable=motor_2_percentage,
                     command=motor_2_change)
motor2_scale_label = Label(real_time_frame, text="Motor 2 %")

motor_3_percentage = IntVar(value=0)
motor3_scale = Scale(real_time_frame, orient=VERTICAL, length=200, from_=100, to=0, variable=motor_3_percentage,
                     command=motor_3_change)
motor3_scale_label = Label(real_time_frame, text="Motor 3 %")

motor_4_percentage = IntVar(value=0)
motor4_scale = Scale(real_time_frame, orient=VERTICAL, length=200, from_=100, to=0, variable=motor_4_percentage,
                     command=motor_4_change)
motor4_scale_label = Label(real_time_frame, text="Motor 4 %")

motor_5_percentage = IntVar(value=0)
motor5_scale = Scale(real_time_frame, orient=VERTICAL, length=200, from_=100, to=0, variable=motor_5_percentage,
                     command=motor_5_change)
motor5_scale_label = Label(real_time_frame, text="Motor 5 %")

motor_6_percentage = IntVar(value=0)
motor6_scale = Scale(real_time_frame, orient=VERTICAL, length=200, from_=100, to=0, variable=motor_6_percentage,
                     command=motor_6_change)
motor6_scale_label = Label(real_time_frame, text="Motor 6 %")

motor_7_percentage = IntVar(value=0)
motor7_scale = Scale(real_time_frame, orient=VERTICAL, length=200, from_=100, to=0, variable=motor_7_percentage,
                     command=motor_7_change)
motor7_scale_label = Label(real_time_frame, text="Motor 7 %")

motor_8_percentage = IntVar(value=0)
motor8_scale = Scale(real_time_frame, orient=VERTICAL, length=200, from_=100, to=0, variable=motor_8_percentage,
                     command=motor_8_change)
motor8_scale_label = Label(real_time_frame, text="Motor 8 %")

motor_9_percentage = IntVar(value=0)
motor9_scale = Scale(real_time_frame, orient=VERTICAL, length=200, from_=100, to=0, variable=motor_9_percentage,
                     command=motor_9_change)
motor9_scale_label = Label(real_time_frame, text="Motor 9 %")

motor_10_percentage = IntVar(value=0)
motor10_scale = Scale(real_time_frame, orient=VERTICAL, length=200, from_=100, to=0, variable=motor_10_percentage,
                      command=motor_10_change)
motor10_scale_label = Label(real_time_frame, text="Motor 10 %")

motor_11_percentage = IntVar(value=0)
motor11_scale = Scale(real_time_frame, orient=VERTICAL, length=200, from_=100, to=0, variable=motor_11_percentage,
                      command=motor_11_change)
motor11_scale_label = Label(real_time_frame, text="Motor 11 %")

motor_12_percentage = IntVar(value=0)
motor12_scale = Scale(real_time_frame, orient=VERTICAL, length=200, from_=100, to=0, variable=motor_12_percentage,
                      command=motor_12_change)
motor12_scale_label = Label(real_time_frame, text="Motor 12 %")

# Place
motor0_scale.grid(row=1, rowspan=20, column=0, stick="nsw", padx=6, pady=5)
motor0_scale_label.grid(row=21, column=0, stick="sw", padx=6)

motor1_scale.grid(row=1, rowspan=20, column=1, stick="nsw", padx=2, pady=5)
motor1_scale_label.grid(row=21, column=1, stick="sw", padx=2)

motor2_scale.grid(row=1, rowspan=20, column=2, stick="nsw", padx=2, pady=5)
motor2_scale_label.grid(row=21, column=2, stick="sw", padx=2)

motor3_scale.grid(row=1, rowspan=20, column=3, stick="nsw", padx=2, pady=5)
motor3_scale_label.grid(row=21, column=3, stick="sw", padx=2)

motor4_scale.grid(row=1, rowspan=20, column=4, stick="nsw", padx=2, pady=5)
motor4_scale_label.grid(row=21, column=4, stick="sw", padx=2)

motor5_scale.grid(row=1, rowspan=20, column=5, stick="nsw", padx=2, pady=5)
motor5_scale_label.grid(row=21, column=5, stick="sw", padx=2)

motor6_scale.grid(row=1, rowspan=20, column=6, stick="nsw", padx=2, pady=5)
motor6_scale_label.grid(row=21, column=6, stick="sw", padx=2)

motor7_scale.grid(row=1, rowspan=20, column=7, stick="nsw", padx=2, pady=5)
motor7_scale_label.grid(row=21, column=7, stick="sw", padx=2)

motor8_scale.grid(row=1, rowspan=20, column=8, stick="nsw", padx=2, pady=5)
motor8_scale_label.grid(row=21, column=8, stick="sw", padx=2)

motor9_scale.grid(row=1, rowspan=20, column=9, stick="nsw", padx=2, pady=5)
motor9_scale_label.grid(row=21, column=9, stick="sw", padx=2)

motor10_scale.grid(row=1, rowspan=20, column=10, stick="nsw", padx=2, pady=5)
motor10_scale_label.grid(row=21, column=10, stick="sw", padx=2)

motor11_scale.grid(row=1, rowspan=20, column=11, stick="nsw", padx=2, pady=5)
motor11_scale_label.grid(row=21, column=11, stick="sw", padx=2)

motor12_scale.grid(row=1, rowspan=20, column=12, stick="nsw", padx=10, pady=5)
motor12_scale_label.grid(row=21, column=12, stick="se", padx=10)

# Reset Button
reset_button = Button(real_time_frame, text="Reset", command=resetRealTimeScale)
reset_button.grid(row=22, column=6, stick="s")

########################################################################################################################
# Demo Frame
########################################################################################################################
demo_choices = ["Demo 1: Rotation", "Demo 2: Up/Down", "Demo 3: Balance"]

demo_choicesvar = StringVar(value=demo_choices)
demo_list = Listbox(demo_frame, height=15, width=40, listvariable=demo_choicesvar, exportselection=False)
demo_list.grid(row=3, rowspan=15, column=2, stick="n", padx=2, pady=2)

send_demo_button = Button(demo_frame, text="Start Demo", command=send_demo)
send_demo_button.grid(row=3, column=6, stick="s", padx=10, pady=2)

refreshDevices()

root.title("VTF Driver Control")
root.iconbitmap(r'vtf.ico')
root.mainloop()
