#!/usr/bin/python3

import tkinter 
from tkinter import *
import net
from tkinter import messagebox

import threading

import queue 
import time
import sys

inputQueue = queue.Queue()
outputQueue = queue.Queue()

FINISH_COMMAND = 3


def running():
	try:
		while True:
			try:
				command = inputQueue.get(True)
				if command['i'] == 0 :
					(time_res, weix_res) = net.sendTime(command['turn'], command['countDown'])
					outputQueue.put({"i":0,"time_res":time_res,"weix_res":weix_res})
				elif command['i'] == 1 :
					outputQueue.put({"i":1,"res":net.getConfig()})
				elif command['i'] == FINISH_COMMAND:
					sent =  command['sendPackage']
					outputQueue.put({"i":FINISH_COMMAND, "res":net.finishTurn(sent)})
			except queue.Empty:
				pass
	except (KeyboardInterrupt, SystemExit):
		print("before stop")
		bgThread.exit()
		sys.exit()


bgThread = threading.Thread(target=running)
bgThread.daemon = True
bgThread.start()



top = tkinter.Tk()


top.geometry('{}x{}'.format(800, 800))

f1 = Frame(top,height=50,width=800)

l1 = Label(f1, text="波数", fg="black", bg="white")
l2 = Label(f1,text="倒计时时间", fg="black", bg="white")

input1 = Entry(f1, fg="black", bg="white", width=20)
input2 = Entry(f1, fg="black", bg="white", width=20)

f2 = Frame(top, height = 100, width=800)

l3Text =StringVar()
l3Text.set("abc")
finishText = StringVar()
finishText.set("unsent")
l3 = Label(f2, fg="black", width=100,bg="white",textvariable=l3Text)
lfinish = Label(f2, fg="black", width=100,bg="white",textvariable=finishText)


f3 = Frame(top, height = 100)

l4Text = StringVar()
l4Text.set("undefined")
l4 = Label(top, fg="black", bg="white",width=100, height=20,textvariable=l4Text)

def clearTime():
	l3Text.set("waiting")
def sendTime():
	turn = input1.get()
	countDown = input2.get()
	inputQueue.put({'i':0,'turn':turn,'countDown':countDown})


	


def periodicCall():
		try:
			command = outputQueue.get(0)
			if command['i'] == 0 :
				l3Text .set( command['time_res'] + "\n" + command['weix_res'])
				top.after(5000, clearTime)
			elif command['i'] == 1 :
				strr = command['res']
				l4Text.set(strr)
				top.after(1000, timer)
			elif command['i'] == FINISH_COMMAND:
				strr = command['res']
				finishText.set(strr)
		except queue.Empty:
			pass
		top.after(200, periodicCall)
def finishTurn():
	inputQueue.put({'i':FINISH_COMMAND,"sendPackage":False})

def finishTurnAndSent():
	if tkinter.messagebox.askyesno("发放剩余红包", "确定要发放所有剩余红包吗?"):
		inputQueue.put({'i':FINISH_COMMAND,"sendPackage":True})
	

w = Button ( f1, text ="sendTime", command = sendTime)
w2 = Button (f1, text="结束", command = finishTurn)
w3 = Button (f1, text="结束并发放剩余红包", command = finishTurnAndSent)

f1.pack()
l1.pack(side="left")
input1.pack(side="left")
l2.pack(side="left")
input2.pack(side="left")
w.pack(side="left")
w2.pack(side="left")
w3.pack(side="left")
f1.pack(side="top")


f2.pack()
l3.pack(side="top")
lfinish.pack(side="top")

f3.pack()

l4.pack()


def timer():
	# get configs
	strr = inputQueue.put({"i":1})


timer()

top.after(200, periodicCall)




top.mainloop()


