import Tkinter
import time
import PIL
from PIL import Image, ImageTk, ImageSequence
from multiprocessing import Process, Queue, Lock
import serial
from flask import Flask, render_template, request
import datetime
gif_queue = Queue()
state_queue = Queue()
serial_queue = Queue()

class Animator:
	def __init__(self, parent, gif_queue):
		self.parent = parent

		self.gif_queue = gif_queue

		#self.entry = Tkinter.Entry(parent)
		self.button = Tkinter.Button(parent, text="Test Dispense!", command=self.on_button)
		self.button.pack()
		#self.entry.pack()

		self.canvas = Tkinter.Canvas(parent, width = 548, height = 300)
		self.canvas.pack()

		self.cat_im   = Image.open(r'/home/pi/Desktop/FinalProject/cat.gif')
		self.cat_sequence = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(self.cat_im)]

		self.hedge_im = Image.open(r'/home/pi/Desktop/FinalProject/hedge.gif')
		self.hedge_sequence = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(self.hedge_im)]

		self.dog_im   = Image.open(r'/home/pi/Desktop/FinalProject/dog.gif')
		self.dog_sequence = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(self.dog_im)]

		self.ack_im   = Image.open(r'/home/pi/Desktop/FinalProject/acknowledge.gif')
		self.ack_sequence = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(self.ack_im)]

		self.done_im   = Image.open(r'/home/pi/Desktop/FinalProject/done.gif')
		self.done_sequence = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(self.done_im)]

		self.alarm_im   = Image.open(r'/home/pi/Desktop/FinalProject/alarm.gif')
		self.alarm_sequence = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(self.alarm_im)]

		self.jam_im   = Image.open(r'/home/pi/Desktop/FinalProject/jam.gif')
		self.jam_sequence = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(self.jam_im)]

		self.play_gif()

	def animate(self, counter, counter_max):
		self.canvas.itemconfig(self.image, image = self.sequence[counter])
		if not self.animating:
			return
		self.parent.after(33, lambda:self.animate((counter+1) % len(self.sequence), counter_max))
		if counter == counter_max:
			print("Done Animating!")
			self.canvas.delete("all")
			self.animating = False
			self.play_gif()
			return
		#print("Counter is: " + str(counter))

	def on_button(self):
		serial_queue.put("Dispense")
	
	def play_gif(self):
		#print("Play_Gif called")
		incoming_data = "NO_GIF"
		play_flag = False
		gif_wait_time = 5000
		nframes = 0
		if not self.gif_queue.empty():
			incoming_data = self.gif_queue.get()
			#print("Incoming Data: " + incoming_data)
			play_flag = True
		else:
			self.parent.after(100, self.play_gif)
			return

		if play_flag and ("Left Ear" in incoming_data):
			print("Playing Left Ear!")
			self.sequence = self.cat_sequence
			nframes = self.cat_im.n_frames-1
			gif_wait_time = 2000

		elif play_flag and ("Right Ear" in incoming_data):
			print("Playing Right Ear!")
			self.sequence = self.hedge_sequence
			nframes = self.hedge_im.n_frames-1
			gif_wait_time = 8000

		elif play_flag and ("Petting" in incoming_data):
			print("Playing Petting!")
			self.sequence = self.dog_sequence
			nframes = self.dog_im.n_frames-1
			gif_wait_time = 4000

		elif play_flag and ("Ack Disp" in incoming_data):
			print("Playing Ack Disp!")
			self.sequence = self.ack_sequence
			nframes = self.ack_im.n_frames-1
			gif_wait_time = 4000

		elif play_flag and ("Alarm Disp" in incoming_data):
			print("Playing Alarm Disp!")
			self.sequence = self.alarm_sequence
			nframes = self.alarm_im.n_frames-1
			gif_wait_time = 4000

		elif play_flag and ("Jam" in incoming_data):
			print("Playing Done Disp!")
			self.sequence = self.jam_sequence
			nframes = self.jam_im.n_frames-1
			gif_wait_time = 4000

		elif play_flag and ("Done Disp" in incoming_data):
			print("Playing Done Disp!")
			self.sequence = self.done_sequence
			nframes = self.done_im.n_frames-1
			gif_wait_time = 4000

		self.image = self.canvas.create_image(270, 100, image = self.sequence[0])
		self.animating = True
		self.animate(0, nframes)        
		#self.parent.after(gif_wait_time, self.play_gif)

def animatorProcess(gif_queue):
	animator_root = Tkinter.Tk()
	animator_app = Animator(animator_root, gif_queue)
	animator_root.mainloop()

app = Flask(__name__)
# Create a dictionary called pins to store the pin number, name, and pin state:
pills = {
	1 : {'name' : 'Asparin', 'time' : '7:00PM', 'level' : 100, 'amt' : 1},
	2 : {'name' : 'Mucinex', 'time' : '8:30PM', 'level' : 100, 'amt' : 1}
	}

class Top_Controller:
	def __init__(self, state_queue):
		self.ser = serial.Serial('/dev/ttyUSB0', 9600)
		self.state_queue = state_queue
		self.pills = pills

	def timeToDispense(self):
		try:
			for pillNum in self.pills:
				temp1 = self.pills[pillNum]['time']
				temp2 = ''.join(ch for ch in temp1 if not ch.isalpha())
				hours = int(temp2.split(':')[0])
				minutes = int(temp2.split(':')[1])
				if temp1.endswith('PM'):
					hours += 12
				now = datetime.datetime.now()
				if (hours == now.hour ) and (minutes == now.minute):
					return pillNum
			return -1
		except:
			print("INVALID TIME :(")
			return -1

	def validString(self, incoming_data):
		if ("Left Ear" in incoming_data) or ("Right Ear" in incoming_data) or ("Petting" in incoming_data) or ("Ack Disp" in incoming_data) or ("Alarm Disp" in incoming_data) or ("Done Disp" in incoming_data) or ("Jam" in incoming_data):
			return True
		else:
			return False


	def mainloop(self):
		try:
			dispenseFlag = True
			while True:
				if self.ser.in_waiting > 0:
					incoming_data = self.ser.readline()
					print("Got: " + incoming_data)
					if self.validString(incoming_data):
						gif_queue.put(incoming_data)

				if not self.state_queue.empty():
					self.pills = self.state_queue.get()
					# print("Got New State!")
					# print("Name: " + self.pills[1]["name"])
					# print("Time: " + self.pills[1]["time"])
					# print("Name: " + self.pills[2]["name"])
					# print("Time: " + self.pills[2]["time"])

				pillN = self.timeToDispense()
				if pillN != -1 and dispenseFlag:
					print("*******************************Dispensing**************************************")
					self.pills[pillN]["level"] -= 1
					lvl = self.pills[pillN]["level"]
					ch = 'H'
					if lvl < 75 and lvl > 25:
						ch = 'M'
					if lvl <= 25 and lvl >= 0:
						ch = 'L'
					self.ser.write("Dispense " + ch + " 1\n")
					dispenseFlag = False

				elif pillN == -1:
					dispenseFlag = True

				if not serial_queue.empty():
					answer = serial_queue.get()
					print("*******************************Dispensing Test**************************************")
					self.pills[1]["level"] -= 1
					lvl = self.pills[1]["level"]
					ch = 'H'
					if lvl < 75 and lvl > 25:
						ch = 'M'
					if lvl <= 25 and lvl >= 0:
						ch = 'L'
					self.ser.write("Dispense " + ch + " 1")
		except:
			print("Closing Serial")
			self.ser.close()

def serialProcess(state_queue):
	controller = Top_Controller(state_queue);
	controller.mainloop()

@app.route("/")
def main():
	# For each pin, read the pin state and store it in the pins dictionary:
	templateData = {
		'pills' : pills
	}
	# Pass the template data into the template main.html and return it to the user
	return render_template('main.html', **templateData)

@app.route("/schedule")
def schedule():
	templateData = {
		'pills' : pills
	}
	return render_template('schedule.html', **templateData)

# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<pillNum>/<action>", methods = ['GET', 'POST'])
def action(pillNum, action):
	# Convert the pin from the URL into an integer:
	pillNum = int(pillNum)

	# If the action part of the URL is "on," execute the code indented below:
	if action == "on":
		# Set the pin high:
		print("Test Dispensing Pill " + str(pillNum))
		# Save the status message to be passed into the template:
		message = "Dispensed " + pillName
	elif action == "off":
		print("Pressed off?")
		message = "Dispensed " + pillName
	elif action == 'change':
		# Update Pill Dispension Stuff
		print(request.form['pillname'])
		print(request.form['time'])
		if request.form['pillname'].strip():
			pills[pillNum]['name'] = request.form['pillname']
		if request.form['time'].strip():
			pills[pillNum]['time'] = request.form['time']
		if request.form['level'].strip():
			pills[pillNum]['level'] = request.form['level']
		
		state_queue.put(pills)


	# Along with the pin dictionary, put the message into the template data dictionary:
	templateData = {
	  'pills' : pills,
	}

	return render_template('schedule.html', **templateData)

if __name__ == "__main__":
	p1 = Process(target=animatorProcess, args=(gif_queue,))
	p2 = Process(target=serialProcess, args=(state_queue,))
	p1.start()
	time.sleep(5)
	p2.start()
	try:
		app.run(host='0.0.0.0', port=1234, debug=False)
		p1.join()
		p2.join()
	except:
		p1.close()
		p1.join()
		p2.kill()
		p2.join()
		print("Closed")


