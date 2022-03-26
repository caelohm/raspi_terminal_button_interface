import os, re, time, subprocess, random, socket, math
import RPi.GPIO as GPIO


def print_normal(list):
	i = 1
	length = len(list)
	# newline
	print()

	while(i <= length):
		if (i < 10):
			pad = ' '
		else:
			pad = ''

		# no tabs & newline
		print(pad + str(i) + '. ' + list[i-1])
		i += 1




def printdir(list):
	i = 1
	length = len(list)
	# newline
	print()

	while(i <= length):
		if (i < 10):
			pad = ' '
		else:
			pad = ''
		
		if ((i-1) % 2 == 0):
			tabs = ''
			n_tabs = math.floor((len(list[i-1]) + 4) / 8)
			while (n_tabs < 6):
				tabs += '\t'
				n_tabs += 1
			
			# print no newline
			print(pad + str(i) + '. ' + list[i-1] + tabs, end = '')

		else:
			# no tabs & newline
			print(pad + str(i) + '. ' + list[i-1])
		i += 1

	if (length % 2 == 1):
		print()



def input_single_pin():
	temp = 'N'
	while (temp == 'N'):
		if (GPIO.input(16) == 0):
			temp = 'B'
		if (GPIO.input(22) == 0):
			temp = 'Y'
		if (GPIO.input(29) == 0):
			temp = 'R'
		if (GPIO.input(31) == 0):
			temp = 'G'
		time.sleep(0.05)
	time.sleep(0.2)
	return temp
	
	


def dirHandle(current_dir, direct, R_Sel_Dir):
	final = False

	select = 0
	
	print('\nStarting at: \n1. ' + direct[0] + '\n')

	while (not final):

		while (GPIO.input(16) == 0): # Blue
			if (GPIO.input(29) == 0): # Red
				if (select - 5 < 0):
					select = len(direct) - 1
				else:
					select -= 5
					time.sleep(0.2)
			elif (GPIO.input(22) == 0):
				printdir(direct)
			elif (select == 0):
				select = len(direct) - 1
			else:
				select -= 1
			print('\n' + str(select + 1) + '. ' + direct[select])
			time.sleep(0.3)


		while (GPIO.input(22) == 0): # Yellow
			if (GPIO.input(31) == 0): # Green
				if (select + 5 > len(direct) - 1):
					select = 0
				else:
					select += 5
					time.sleep(0.2)
			elif (GPIO.input(16) == 0):
				printdir(direct)
			elif (select == len(direct) - 1):
				select = 0
			else:
				select += 1
			print('\n' + str(select + 1) + '. ' + direct[select])
			time.sleep(0.3)

		# reset
		if (GPIO.input(29) == 0):
			if (R_Sel_Dir):
				final = True
			else:
				return 'Reset'
			time.sleep(0.2)

		# Green
		elif (GPIO.input(31) == 0):
			if (not os.path.isdir(current_dir + '/' + direct[select])):
				final = True
			else:
				current_dir += '/' + direct[select]
				direct = os.listdir(current_dir)
				direct.sort()

			if (not final):
				select = 0

				printdir(direct)

				print('\nStarting at: \n1. ' + direct[0])
			time.sleep(0.2)

		time.sleep(0.025)
	
	episodes = []

	if (R_Sel_Dir):
		for (dirpath, dirnames, filenames) in os.walk(current_dir):
			episodes += [os.path.join(dirpath, file) for file in filenames]
	else:
		for elem in direct:
			episodes.append(current_dir + '/' + elem)

	episodes.sort()
	return [episodes, select, current_dir]






def player(sode):
	time.sleep(0.5)
	'''
	temp = None
	print('\nPick size of subtitles:' +
		'\nBlue = Small, Yellow = Medium, Green = Large\n')
	while (temp == None):
		if (GPIO.input(16) == 0):
			temp = '50'
		if (GPIO.input(22) == 0):
			temp = '75'
		if (GPIO.input(31) == 0):
			temp = '100'
		time.sleep(0.1)

		add '--sub-text-scale=' + temp, to Popen to launch
			with subtitle scaling
	'''
	subprocess.Popen(['vlc', '--no-video-title-show', 
		'--rc-host', '127.0.0.1:1080', '--freetype-shadow-opacity=255', sode])
		#'--video-filter', '"adjust{brightness=0.8}"', sode])
		# stdout=subprocess.PIPE, stdin=subprocess.PIPE) if using p.poll()

	# Wait for VLC to launch.
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	while (sock.connect_ex(('127.0.0.1', 1080)) != 0):
		time.sleep(1)


	# type of jump
	dist = [15, 60, 300, 1200]
	index = 0
	paused = False
	ctr = 1
	subtrack = '-1'
	trigger = True
	timer = 0
	length = 40000

	# stream still needs more time to launch
	time.sleep(3)

	sock.send('get_length\n'.encode())
	# need to give time for vlc to return time
	time.sleep(1)

	# Starts out with hogwash VLC greeting
	temp = sock.recv(1024).decode()
	temp = temp.split()
	temp = temp[len(temp)-3:]
	temp = ' '.join(temp)
	print(temp)

	length = int(re.search('\d+', temp).group())


	# while video player is running
	while (trigger):

		# Red Pressed
		if (GPIO.input(29) == 0):
			if (paused):
				sock.send(('key vol-mute\n').encode())
			else:
				if (index == 3):
					index = 0
					# mp3 must be in current directory
					os.system('mpg321 -g 25 bumper.mp3')
				else:
					index += 1

			while (GPIO.input(29) == 0):
				if (GPIO.input(16) == 0):
					sock.send('shutdown\n'.encode())

					sock.shutdown(socket.SHUT_RDWR)
					sock.close()

					return 'Previous'

				time.sleep(0.1)
			time.sleep(0.1)




		# Blue Pressed
		elif (GPIO.input(16) == 0):
			if (not paused):
				timer = timer - dist[index]
				sock.send(('seek ' + str(timer) + '\n').encode())
				time.sleep(2)
			
			while (GPIO.input(16) == 0):
				if (paused):
					sock.send(('key vol-down\n').encode())
					time.sleep(0.2)
					
				if (GPIO.input(29) == 0):
					sock.send('shutdown\n'.encode())

					sock.shutdown(socket.SHUT_RDWR)
					sock.close()

					return 'Previous'

				if (GPIO.input(22) == 0):
					sock.send('shutdown\n'.encode())

					sock.shutdown(socket.SHUT_RDWR)
					sock.close()

					return 'Stop'




		# Yellow Pressed
		elif (GPIO.input(22) == 0):

			if (timer + dist[index] < length and not paused):
				timer = timer + dist[index]
				sock.send(('seek ' + str(timer) + '\n').encode())
				time.sleep(2)

			while (GPIO.input(22) == 0):
				if (paused):
					sock.send(('key vol-up\n').encode())
					time.sleep(0.1)
				
				if (GPIO.input(16) == 0):
					sock.send('shutdown\n'.encode())

					sock.shutdown(socket.SHUT_RDWR)
					sock.close()

					return 'Stop'

				if (GPIO.input(31) == 0):
					sock.send('shutdown\n'.encode())

					sock.shutdown(socket.SHUT_RDWR)
					sock.close()

					return 'Next'

				time.sleep(0.1)




		# Green Pressed
		elif (GPIO.input(31) == 0):
			sock.send('pause\n'.encode())
			paused = not paused

			ctrSub = 0
			while (GPIO.input(31) == 0):
				if (GPIO.input(22) == 0):
					sock.send('shutdown\n'.encode())

					sock.shutdown(socket.SHUT_RDWR)
					sock.close()

					return 'Next'

				# held for 1 second
				if (ctrSub == 10):
					if (subtrack == '-1'):
						sock.send('strack\n'.encode())
						# need to give time for vlc to return subtitles
						time.sleep(0.05)

						temp = sock.recv(1024).decode()
						print(temp)

						temp = temp.split('\n')
						for i in range(0, len(temp)):
							if (re.search('\*', temp[i]) != None and i != 1):
								subtrack = re.search('\d+', temp[i]).group()
				
						sock.send('strack -1\n'.encode())
						os.system('mpg321 -g 60 bumper.mp3')
						ctrSub = 0
					else:
						sock.send(('strack ' + subtrack + '\n').encode())
						os.system('mpg321 -g 60 bumper.mp3')
						subtrack = '-1'
						ctrSub = 0
					

				time.sleep(0.1)
				ctrSub += 1
			time.sleep(0.25)


		time.sleep(0.1)

		if (ctr % 50 == 0):

			sock.send('get_time\n'.encode())
			# need to give time for vlc to return time
			time.sleep(0.02)

			temp = sock.recv(1024).decode()
			if (re.search('\d+\r\n', temp) != None):
				timer = int(re.search('\d+', temp).group())

			sock.send('is_playing\n'.encode())

			if (re.search('0\r\n', sock.recv(1024).decode()) != None):
				trigger = False
				sock.send('shutdown\n'.encode())
			# print(sock.recv(1024).decode())

			ctr = 0
		ctr += 1

	sock.shutdown(socket.SHUT_RDWR)
	sock.close()
	return True




def createDir(dir):
	if (not os.path.exists(dir)):
		os.mkdir(dir)




def readfile(path, Files):
	file = open(path, 'r', encoding='utf8')

	Files[1] = int(file.readline().replace('\n', ''))
	Files[2] = file.readline().replace('\n', '')
	Files[0] = []
	for line in file:
		Files[0].append(line.replace('\n', ''))
	file.close()
	return Files




def session_name(sode):
	last3 = sode.split('/')
	last3 = last3[len(last3)-3:]
	last3 = ' '.join(last3)
	last3 = last3.replace('.mkv', '')
	last3 = last3.replace('.mp4', '')
	return last3






def main(vidpath):
	'''
	BOARD 16 = Blue
	BOARD 22 = Yellow
	BOARD 29 = Red
	BOARD 31 = Green
	'''
	GPIO.setmode(GPIO.BOARD)
	GPIO.setwarnings(False)

	GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(29, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(31, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	# GPIO.input(BOARD NUM) to check pin value. 0 = on, 1 = off

	type = 'N'
	print('\n\n\nPress Blue: play one or multiple\n' +
			'Press Yellow: play Favorites\n' +
			'Press Red: play a random range\n' +
			'Press Green: play previous session\n')
	
	type = input_single_pin()


	'''
	Determine if no directories are in current directory
	using folders_in method.

	Write files in episodes list to playlist
	'''


	if (type == 'R'):
		print('\nBlue: decrement\n' +
			'Red: randomize current directory\n' +
			'Yellow: increment\n' +
			'Green: confirm\n')

		# lists folders in vidpath
		current_dir = vidpath
		direct = os.listdir(current_dir)
		direct.sort()
		printdir(direct)

		Files = dirHandle(current_dir, direct, True)

		Files[1] = random.randint(0, len(Files[0]) - 1)

	else:
		print('\nBlue: decrement\n' +
			'Red: terminate/reset\n' +
			'Yellow: increment\n' +
			'Green: confirm\n')
	



	if (type == 'B'):
		current_dir = vidpath
		direct = os.listdir(current_dir)
		direct.sort()
		printdir(direct)

		# returns 
		Files = dirHandle(current_dir, direct, False)

		# back to beginning
		if (Files == 'Reset'):
			return True





	while (type == 'G' or type == 'Y'):
		if (type == 'Y'):
			current_dir = 'Favorites/'
		else:
			current_dir = 'Sessions/'
		createDir(current_dir)
		Sessions = os.listdir(current_dir)

		if (len(Sessions) == 0):
			if (type == 'Y'):
				print('No favorites currently stored')
			else:
				print('No sessions currently stored')
			return True

		if (type == 'Y'):
			Sessions.sort()
		else:
			# Sorts in order of creation
			Sessions = [os.path.join(current_dir, s) for s in Sessions]
			Sessions.sort(key=lambda x: os.path.getmtime(x), reverse=True)
			Sessions = [s.replace(current_dir, '') for s in Sessions]

		print_normal(Sessions)

		Files = dirHandle(current_dir, Sessions, False)

		if (Files == 'Reset'):
			return True

		print('\nRed for delete, otherwise play\n')

		if (input_single_pin() == 'R'):
			os.remove(current_dir + Sessions[Files[1]])

		else:
			temp = type
			type = 'N'

			if (re.search('Random', Sessions[Files[1]]) != None):
				type = 'R'

			if (temp == 'Y'):
				print('\nRandomize? Red for random, otherwise no\n')
				if (input_single_pin() == 'R'):
					type = 'R'

			Files = readfile(current_dir + Sessions[Files[1]], Files)

			if (type == 'R'):
				Files[1] = random.randint(0, len(Files[0]) - 1)



	'''
	# runs video player, -t subtitles on
	print('\nSubtitles on? Green for yes, otherwise no\n')
	if (re.search('G', input_single_pin()) != None):
		sub = True
	else:
		sub = False
	'''

	#Same as code in while loop. initialize variables.
	end_close = ''
	prev_index = Files[1]

	while (end_close != 'Stop' and Files[1] <= len(Files[0]) - 1
		and Files[1] >= 0):

		sode = Files[0][Files[1]]
		prev_index = Files[1]

		end_close = player(sode)
		time.sleep(1)

		if (type == 'R'):
			while (Files[1] == prev_index):
				Files[1] = random.randint(0, len(Files[0]) - 1)
		elif (end_close == 'Previous'):
			Files[1] -= 1
		else:
			Files[1] += 1

	if (Files[1] < 0):
		Files[1] = 0
	elif (Files[1] > len(Files[0]) - 1):
		Files[1] = len(Files[0]) - 1
	# set to endings of episodes

	#'''



	time.sleep(1)
	print('\nYellow: save episode to favorites\n' +
			'Green: save session\n' +
			'Otherwise, reset\n')
	temp = input_single_pin()
	if (temp == 'Y'):
		type = 'Y'
	elif (temp != 'G'):
		return True
	

	if (type == 'R'):
		createDir('Sessions/')

		last3 = session_name(Files[2])

		file = open('Sessions/Random_' + last3, 'w', encoding='utf8')
		print('Saved Sessions/Random_' + last3)
	


	elif (type == 'Y'):
		print('\nBlue: decrement\n' +
			'Red: terminate/reset\n' +
			'Yellow: increment\n' +
			'Green: confirm\n')

		current_dir = 'Favorites/'
		createDir(current_dir)

		Sessions = os.listdir(current_dir)
		Sessions.sort()

		Sessions.insert(0, 'Add new Favorites file')

		print_normal(Sessions)

		Files = dirHandle(current_dir, Sessions, False)

		if (Files == 'Reset'):
			return True

		if (Files[1] != 0):
			temp = Files[0][Files[1] - 1]
			
			Files = readfile(temp, Files)

			file = open(temp, 'w', encoding='utf8')

			# make sure not adding duplicates
			No_file = True
			for line in Files[0]:
				if (re.search(sode, line) != None):
					No_file = False
			if (No_file):
				Files[0].append(sode)
			
		else:
			prev_index = 0
			temp = len(Sessions)
			if (temp < 10):
				file = open('Favorites/Favorite_0' + str(temp), 'w', encoding='utf8')
				print('Saved to Favorites/Favorite_0' + str(temp))
			else:
				file = open('Favorites/Favorite_' + str(temp), 'w', encoding='utf8')
				print('Saved to Favorites/Favorite_' + str(temp))

			Files[0] = [sode]
	


	else:
		createDir('Sessions/')

		last3 = session_name(sode)

		file = open('Sessions/Session_' + last3, 'w', encoding='utf8')
		print('Saved Sessions/Session_' + last3)

	file.write(str(prev_index) + '\n')
	file.write(Files[2] + '\n')
	for episode in Files[0]:
		file.write(episode + '\n')

	file.close()

	return True
	




if __name__ == "__main__":

	vidpath = '/home/pi/Videos'

	reset = True
	while (reset == True):
		reset = main(vidpath)
		time.sleep(0.5)
