import os, keyboard, re, time
from sys import platform


def printdir(list):
	i = 0
	# newline
	print()

	for file in list:
		i += 1
		print(str(i) + '. ' + file)


def final_dir(folder_dirs, current_dir):
	for fname in folder_dirs:
		if os.path.isdir(os.path.join(current_dir, fname)):
			return False
	return True


def change_pins(GPIObin, GPIO):
	# set bits
	if (re.search('B', GPIO) != None):
		GPIObin[0] = '0'
	if (re.search('R', GPIO) != None):
		GPIObin[1] = '0'
	if (re.search('G', GPIO) != None):
		GPIObin[2] = '0'
	if (re.search('Y', GPIO) != None):
		GPIObin[3] = '0'
	return GPIObin




def main(vidpath):
	print('\nInput any button pressed\n' +
		'\tBlue means play one episode, range, or decrement\n' +
		'\tRed means randomize or terminate/reset\n' +
		'\tGreen means play previous session or confirm\n' +
		'\tYellow means edit playlists or increment\n')

	type = -1
	while (type == -1):
		GPIO = input('\nPress Blue: play 1 or multiple episodes\n' +
			'Press Yellow: edit playlists\n' +
			'Press Red: play a random range\n' +
			'Press Green: play previous session\n')

		# set bits
		if (re.search('B', GPIO) != None):
			type = 0
		if (re.search('R', GPIO) != None):
			type = 1
		if (re.search('Y', GPIO) != None):
			type = 2
		if (re.search('G', GPIO) != None):
			type = 3

	episodes = []
	for (dirpath, dirnames, filenames) in os.walk(vidpath):
		episodes += [os.path.join(dirpath, file) for file in filenames]

 
	'''
	Determine if no directories are in current directory
	using folders_in method.
	
	Write files in episodes list to playlist
	'''
	current_dir = vidpath
	folders = os.listdir(current_dir)

	while (True):

		GPIObin = ['1', '1', '1', '1']
		select = 0


		if (type == 0):
			printdir(folders)
			GPIO = input('\nStarting at \n1. ' + folders[0] + ',\n'
				'Blue: decrement\n' +
				'Yellow: increment\n' +
				'Red: terminate/reset\n' +
				'Green: confirm\n\n')
			GPIObin = change_pins(GPIObin, GPIO)

			while(GPIObin[2] == '1'):

				if (GPIObin[0] == '0'):
					if (select == 0):
						select = len(folders) - 1
					else:
						select -= 1
					print('\n' + str(select) + '. ' + folders[select])

				if (GPIObin[1] == '0'):
					if (re.search('R', input('Terminate? Red to terminate, otherwise no') != None)):
						return False
					else:
						return True
				
				if (GPIObin[3] == '0'):
					if (select == len(folders) - 1):
						select = 0
					else:
						select += 1
					print('\n' + str(select) + '. ' + folders[select])
				

				GPIObin = ['1', '1', '1', '1']
				GPIO = input()
				GPIObin = change_pins(GPIObin, GPIO)
				time.sleep(0.2)
		'''
		if (type == 1):

		if (type == 2):

		if (type == 3):
		'''

		if (platform == "win32"):
			current_dir += '\\' + folders[select]
		else:
			current_dir += '/' + folders[select]	
		
		folders = os.listdir(current_dir)



if __name__ == "__main__":
	
	if (platform == "win32"):
		vidpath = 'D:\Videos'
	else:
		vidpath = '/home/pi/Videos/TVShow/'
	
	reset = True
	while (reset == True):
		reset = main(vidpath)
