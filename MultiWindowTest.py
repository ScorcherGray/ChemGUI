from PyQt5.QtWidgets import *
#from sys import stderr, stdout
import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

outputList = []
fileList = []
dirList = []
currentDirectory = ''
uName = ''

class MainWindow(QWidget):
	global uName
	global currentDirectory
	def __init__(self):
		print('MainWindow\n')
		super().__init__()
		self.initMain()

	def logOut(self):
		self.coordFileSelect.clear()
		self.inputFileSelect.clear()
		self.outputFileSelect.clear()
		self.topFileSelect.clear()
		self.refFileSelect.clear()
		self.rstFileSelect.clear()
		self.outputWindow.clear()
		self.dirSelect.clear()
		client.close()

	def newLocation(self):
		self.coordFileLabel.clear()
		self.inputFileSelect.clear()
		self.outputFileSelect.clear()
		self.topFileSelect.clear()
		self.refFileSelect.clear()
		self.rstFileSelect.clear()
		self.outputWindow.clear()
		newLoc = self.dirSelect.currentText()
		print('new location: ', str(newLoc).rstrip('\n\r'), '\n')
		self.changeDirectory(newLoc)

	def initMain(self):
		print('creating window\n')
		grid = QGridLayout()
		
		self.windowTitle=str(uName) + " Remote File Access"

		self.outButton = QPushButton('Log Out')
		grid.addWidget(self.outButton, 3, 3, 1, 1)
		self.outButton.clicked.connect(self.logOut)

		self.changeButton = QPushButton('GO!')
		grid.addWidget(self.changeButton, 8, 3, 1, 2)
		self.changeButton.clicked.connect(self.newLocation)

		self.outputWindow = QTextEdit()
		grid.addWidget(self.outputWindow, 9, 0, 3, 2)

		self.inputFileSelect = QComboBox()
		grid.addWidget(self.inputFileSelect, 2, 1, 1, 2)

		self.inputFileLabel = QLabel('Input File (.in)')
		grid.addWidget(self.inputFileLabel, 2, 0, 1, 1)

		self.outputFileSelect = QComboBox()
		grid.addWidget(self.outputFileSelect, 3, 1, 1, 2)

		self.topFileSelect = QComboBox()
		grid.addWidget(self.topFileSelect, 4, 1, 1, 2)

		self.topFileLabel = QLabel('Topology File (.prmtop)')
		grid.addWidget(self.topFileLabel, 4, 0, 1, 1)

		self.coordFileSelect = QComboBox()
		grid.addWidget(self.coordFileSelect, 5, 1, 1, 2)

		self.coordFileLabel = QLabel('Coord File (.inpcrd)')
		grid.addWidget(self.coordFileLabel, 5, 0, 1, 1)

		self.rstFileSelect = QComboBox()
		grid.addWidget(self.rstFileSelect, 6, 1, 1, 2)

		self.rstFileLabel = QLabel('Restart File (.rst)')
		grid.addWidget(self.rstFileLabel, 6, 0, 1, 1)

		self.refFileSelect = QComboBox()
		grid.addWidget(self.refFileSelect, 7, 1, 1, 2)

		self.refFileLabel = QLabel('Reference File (.inpcrd)')
		grid.addWidget(self.refFileLabel, 7, 0, 1, 1)

		self.dirLabel = QLabel('Current working directory: ')
		grid.addWidget(self.dirLabel, 0, 2, 1, 1)

		self.changeLabel = QLabel('Change directory: ')
		grid.addWidget(self.changeLabel, 8, 0, 1, 1)

		self.dirSelect = QComboBox()
		grid.addWidget(self.dirSelect, 8, 1, 1, 2)

		self.currentDirLabel = QLabel()
		grid.addWidget(self.currentDirLabel, 1, 2, 1, 1)

		self.show()
		self.listFiles()

	def organizeFiles(self, outputList):
		print('organize files\n')
		global currentDirectory
		print('Current directory: ', currentDirectory)
		fileList.clear()
		dirList.clear()
		for item in outputList:
			if '.' in item:
				fileList.append(str(item).rstrip('\n\r'))
			else:
				toTest = str(currentDirectory).rstrip('\n\r') + '/' + str(item).rstrip('\n\r')
				self.testDirectory(toTest)
		for item in fileList:
			if item.endswith('.in'):
				self.inputFileSelect.addItem(str(item).rstrip('\n\r'))
		for item in fileList:
			if item.endswith('.out'):
				self.outputFileSelect.addItem(str(item).rstrip('\n\r'))
		for item in fileList:
			if item.endswith('.prmtop'):
				self.topFileSelect.addItem(str(item).rstrip('\n\r'))
		for item in fileList:
			if item.endswith('.inpcrd'):
				self.coordFileSelect.addItem(str(item).rstrip('\n\r'))
				self.refFileSelect.addItem(str(item).rstrip('\n\r'))
		for item in fileList:
			if item.endswith('.rst'):
				self.rstFileSelect.addItem(str(item).rstrip('\n\r'))

	def populateDirSelect(self, workingDir):
		print('populateDirSelect\n')
		global currentDirectory
		self.dirSelect.clear()
		fullDir = ''
		for word in workingDir.split('/'):
			if len(word) > 1:
				fullDir = fullDir.rstrip('\n\r') + "/" + word
				self.dirSelect.addItem(fullDir.rstrip('\n\r'))
				#print("fullDir = {}".format(fullDir))
		currentDirectory = fullDir
		self.currentDirLabel.setText(fullDir)
		for item in dirList:
			newDir = fullDir.rstrip('\n\r') + '/' + str(item)
			newDir.rstrip('\n\r')
			print(newDir)
			self.dirSelect.addItem(newDir)

	def testDirectory(self, dir):
		print('testDirectory called \n')
		response = ''
		print(dir) #this should be the full file path: /home/dgray/Practice/mdinfo
		stdin, stdout, stderr = client.exec_command('file ' + str(dir))
		for line in stdout:
			response = line
			print(response)
		if 'directory' in response:
			print('Is a directory!')
			self.dirSelect.addItem(dir)
		
	def getDirectory(self):
		global currentDirectory
		print('get directory \n')
		stdin, stdout, stderr = client.exec_command('pwd')
		for line in stdout:
			workingDir = line
			#print(workingDir)
		currentDirectory = workingDir
		print(currentDirectory)
		self.populateDirSelect(workingDir)

	def listFiles(self):
		print('list files\n')
		outputList.clear()
		self.outputWindow.clear()
		stdin, stdout, stderr = client.exec_command('ls')
		for line in stdout:
			outputList.append(line)
			self.outputWindow.append(" {} ".format(line.strip('\n')))	
		self.getDirectory()
		self.organizeFiles(outputList)

	def changeDirectory(newLoc):
		global currentDirectory
		currentDirectory = newLoc
		print('changing directory to: ', str(currentDirectory).rstrip('\n\r'), '\n')
		stdin, stdout, stderr = client.exec_command('cd ' + str(newLoc).rstrip('\n\r') + '; ls')
		#Populate new directory list
		self.populateDirSelect(currentDirectory)
		#populate list of files of 'new directory'
		outputList.clear()
		self.outputWindow.clear()
		for line in stdout:
			outputList.append(line)
			self.outputWindow.append(" {} ".format(line.strip('\n')))
		#Call organize files passing in new list of files
		self.organizeFiles(outputList)
	
	def newLocation():
		self.coordFileLabel.clear()
		self.inputFileSelect.clear()
		self.outputFileSelect.clear()
		self.topFileSelect.clear()
		self.refFileSelect.clear()
		self.rstFileSelect.clear()
		self.outputWindow.clear()
		newLoc = self.dirSelect.currentText()
		print('new location: ', str(newLoc).rstrip('\n\r'), '\n')
		self.changeDirectory(self.newLoc)


class LoginWindow(QWidget):
	global uName
	
	def get_user_name(self):
		return self.userInput.text()

	def get_password(self):
		return self.passwordInput.text()

	def __init__(self):
		super().__init__()
		self.initUI()
	
	def callConnect(self):
		uName = self.get_user_name()
		self.pWord = self.get_password()
		self.sshConnect(uName, self.pWord)

	def initUI(self):		
		grid = QGridLayout()
		
		self.nameLabel = QLabel('User Name')
		grid.addWidget(self.nameLabel, 0, 0, 1, 1)

		self.userInput = QLineEdit()
		grid.addWidget(self.userInput, 0, 1, 1, 1)

		self.pwLabel = QLabel('Password')
		grid.addWidget(self.pwLabel, 1, 0, 1, 1)

		self.passwordInput = QLineEdit()
		grid.addWidget(self.passwordInput, 1, 1, 1, 1)
		self.passwordInput.returnPressed.connect(self.callConnect)
		self.passwordInput.setEchoMode(QLineEdit.Password)

		self.logButton = QPushButton('Log In')
		grid.addWidget(self.logButton, 2, 3, 1, 1)
		self.logButton.clicked.connect(self.callConnect)

		self.setLayout(grid)
		self.setWindowTitle('Log In')
		self.show()

	def sshConnect(self, uName, pWord):
		print('sshConnect\n')
		client.connect('cos-d226275a.static.uvu.edu', username=uName, password=pWord)
		time.sleep(1)
		#listFiles()
		#passwordInput.clear()
		print('attempt close\n')
		self.close()
		print('Close success, calling next\n')
		next=MainWindow()

if __name__ == '__main__':
	#outButton.clicked.connect(logOut)
	#changeButton.clicked.connect(newLocation)

	app = QApplication([])
	app.setStyle('GTK+')
	login = LoginWindow()
	#window.setLayout(grid)
	#window.show()
	app.exec_()
