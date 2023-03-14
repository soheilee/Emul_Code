from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *    
import sys
import subprocess
import os
import time
import signal
import pika
from threading import Thread
from datetime import datetime


#from Consumer_Test import message_type
Flag_Status = 0
message_type=0
message_id=0


# -------------------------  Run the server program and wait for 500ms --------------------------------------------------
command = 'sudo python3 RunServer.py'
p = subprocess.Popen(['gnome-terminal', '--disable-factory', 'bash', '-e', command], stderr=subprocess.STDOUT, stdout=subprocess.PIPE, preexec_fn=os.setpgrp)
time.sleep(0.5)

# -------------------------  Establish the connection to the RabbitMQ and set the Routing key ---------------------------
cred = pika.PlainCredentials('genia', 'genia123')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/', cred))
channel = connection.channel()
routing_key = "NSCEServer"


# -------------------------  Defining the GUI --------------------------------------------------------------------------
class Dialog(QWidget):
    def __init__(self):
        super().__init__() 

        #Adding an icon and a title#Adding an icon and a title
        self.worker = WorkerThread()
        self.worker.start()
        self.worker.update_progress.connect(self.evt_update_progress)
        self.worker.LoadingSuccessful.connect(self.evt_LoadingSuccessful)
        self.setWindowIcon(QIcon('Roche.png'))
        self.setWindowTitle("NSCEServer")
        
        #Setting up the geometry of the GUI

        self.setGeometry(0, 0, 800, 600)
        dialogLayout = QVBoxLayout()   
    
        # Create the tab widget with two Main and Simulation labels

        tabs = QTabWidget()
        tabs.addTab(self.mainTabUI(), "Main")
        tabs.addTab(self.simulationTabUI(), "Simulation")
        dialogLayout.addWidget(tabs)    

        # Add a button box for OK or Cancel

        """btnBox = QDialogButtonBox()
        btnBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        dialogLayout.addWidget(btnBox)"""
        self.btnBox = QPushButton()
        self.btnBox.setIcon(QIcon('play.png'))
        self.btnBox.setGeometry(200, 150, 100, 40)
        self.btnBox.clicked.connect(self.buttonClicked_OK)
        dialogLayout.addWidget(self.btnBox, alignment=Qt.AlignRight)

        # Adding a progressbar  the layout on the dialog

        self.pbar = QProgressBar(self)
        dialogLayout.addWidget(self.pbar)
        self.setLayout(dialogLayout)
        
    
# -------------------------  Defining the the Main Tab --------------------------------------------------------------------------
    def mainTabUI(self):
        
        # Setting up the layout, size
        generalTab = QWidget()
        self.step = 0
        horizontalLayout = QHBoxLayout()

        # Setting up the label and the LineEdit for the FilePath
        self.label = QLabel()
        self.label.setText("Open File")
        self.label.setFixedWidth(70)
        self.label.setFont(QFont("Arial",weight=QFont.Bold))
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        horizontalLayout.addWidget(self.label)
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setFixedWidth(300)
        self.filter_name = '*.dat files (*.dat)'
        self.dirpath = QDir.currentPath()
        horizontalLayout.addWidget(self.lineEdit)

        
        self.button_search = QPushButton('Select Simulation File')
        self.button_search.clicked.connect(self.getFile)
        horizontalLayout.addWidget(self.button_search)

        self.button_load = QPushButton('Load Simulation File into RAM')
        self.button_load.clicked.connect(self.loadFile)
        horizontalLayout.addWidget(self.button_load)

        horizontalLayout.addStretch()
        verticalLayout = QVBoxLayout( self )
        verticalLayout.addLayout( horizontalLayout )
        # Creating a Text box
        LogBox_Spacer = QLabel( '' )
        LogBox_Label = QLabel( 'Console' )
        verticalLayout.addWidget( LogBox_Spacer )
        verticalLayout.addWidget( LogBox_Label )
        self.Logbox = QTextEdit(
            #lineWrapMode=QTextEdit.FixedColumnWidth,
            #lineWrapColumnOrWidth=200,
            placeholderText="Logs here",
            readOnly=True,
            )
        # Change font size of the textbox
        self.Logbox.setFont(QFont('Helvetica',9))
        
        #Put combobox on the screen
        verticalLayout.addWidget(self.Logbox)
        
        generalTab.setLayout(verticalLayout)
        return generalTab

# -------------------------  Defining the the Simulation Tab --------------------------------------------------------------------------
    def simulationTabUI(self):
        """To be designed"""
        networkTab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QCheckBox(" Option 1"))
        layout.addWidget(QCheckBox(" Option 2"))
        
        
        networkTab.setLayout(layout)
        return networkTab

# -------------------------  Defining the Dialog Funtion --------------------------------------------------------------------------

    def dialog():
        file , check = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()",
                                               "", ".dat Files (*.dat)")
        if check:
            print(file)

# -------------------------  Defining the GUI Ready Funtion --------------------------------------------------------------------------
#     
    def GUI_Ready(self):
        Message_1 = "{\"MessageType\":\"GUIReady\",\"ImmediateReplyTo\":\"nsp.reply1\",\"ContextId\":\"GUIReady\",\"ApiLevel\":\"R&D\"}"
        channel.basic_publish(exchange='ns3',routing_key=routing_key, body= Message_1, properties=pika.BasicProperties(
                                                                            type="GUIReady",
                                                                            message_id="GUIReady",
                                                                            delivery_mode = 1,))
        self.Logbox.setTextColor(QColor(100,150,100))
        self.Logbox.insertPlainText("\n")

        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        self.Logbox.insertPlainText(current_time)
        self.Logbox.insertPlainText("\t")
        self.Logbox.insertPlainText("GUIReady")

# -------------------------  Defining the GetFile Function --------------------------------------------------------------------------
    def getFile(self):
        self.filepaths = []
        self.filepaths.append(QFileDialog.getOpenFileName(self, caption='Choose File',
                                                    directory=self.dirpath,
                                                    filter=self.filter_name)[0]) 
        #print(self.filepaths)
        self.lineEdit.setText(self.filepaths[0])

        ###################-----------------------------UPDATING THE SERVER   "File is selected successfully" --------------------------------###################

        Message_2 = "{\"MessageType\":\"FileSelected\",\"ImmediateReplyTo\":\"nsp.reply1\",\"ContextId\":\"FileSelectedID\",\"ApiLevel\":\"R&D\"}"

        channel.basic_publish(exchange='ns3',routing_key=routing_key, body= Message_2, properties=pika.BasicProperties(
                                                                                type=self.filepaths[0],
                                                                                message_id="FileSelectedID",
                                                                                delivery_mode = 1,))
        self.Logbox.setTextColor(QColor(100,150,100))
        self.Logbox.insertPlainText("\n")
        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        self.Logbox.insertPlainText(current_time)
        self.Logbox.insertPlainText("\t")
        self.Logbox.insertPlainText("FileSelected")

# -------------------------  Defining the LoadFile Function --------------------------------------------------------------------------

    def loadFile(self):
            self.step = 0;
            self.button_load.setDisabled(True)
            self.button_search.setDisabled(True)
            self.lineEdit.setDisabled(True)
            """while self.step < 100:
                time.sleep(0.01)
                self.step +=1
                self.pbar.setValue(self.step)"""
            self.button_load.setEnabled(True)
            self.button_search.setEnabled(True)
            self.lineEdit.setEnabled(True)

            ###################-----------------------------UPDATING THE SERVER   "File is Loaded Successfully" --------------------------------###################

            Message_3 = "{\"MessageType\":\"LoadFile\",\"ImmediateReplyTo\":\"nsp.reply1\",\"ContextId\":\"LoadFileID\",\"ApiLevel\":\"R&D\"}"

            channel.basic_publish(exchange='ns3',routing_key=routing_key, body= Message_3, properties=pika.BasicProperties(
                                                                                type="LoadFile",
                                                                                message_id="LoadFileID",
                                                                                delivery_mode = 1,))
            self.Logbox.setTextColor(QColor(100,150,100))
            self.Logbox.insertPlainText("\n")
            now = datetime.now()
            current_time = now.strftime("%d/%m/%Y %H:%M:%S")
            self.Logbox.insertPlainText(current_time)
            self.Logbox.insertPlainText("\t")
            self.Logbox.insertPlainText("LoadFile")

    
                                                                    
# -------------------------  Defining the Cancel Button Function --------------------------------------------------------------------------
    def buttonClicked_Cancel(self):
        
        #QCoreApplication.instance().quit()
        ###################-----------------------------UPDATING THE SERVER   "Cancel Button is clicked" --------------------------------###################
        Message_4 = "{\"MessageType\":\"CancelButtonClicked\",\"ImmediateReplyTo\":\"nsp.reply1\",\"ContextId\":\"ProgramAborted\",\"ApiLevel\":\"R&D\"}"

        channel.basic_publish(exchange='ns3',routing_key=routing_key, body= Message_4, properties=pika.BasicProperties(
                                                                                type="CancelButtonClicked",
                                                                                message_id="ProgramAborted",
                                                                                delivery_mode = 1,))
        #os.killpg(p.pid, signal.SIGINT)    

# -------------------------  Defining the OK Button Function --------------------------------------------------------------------------

    def buttonClicked_OK(self):
        
        #QCoreApplication.instance().quit()
        ###################-----------------------------UPDATING THE SERVER   "OK Button is clicked" --------------------------------###################
        Message_5 = "{\"MessageType\":\"SimulationStarted\",\"ImmediateReplyTo\":\"nsp.reply1\",\"ContextId\":\"SimulationStartedID\",\"ApiLevel\":\"R&D\"}"

        channel.basic_publish(exchange='ns3',routing_key=routing_key, body= Message_5, properties=pika.BasicProperties(
                                                                                type="SimulationStarted",
                                                                                message_id="SimulationStarted",
                                                                                delivery_mode = 1,))
        self.Logbox.setTextColor(QColor(100,150,100))
        self.Logbox.insertPlainText("\n")
        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        self.Logbox.insertPlainText(current_time)
        self.Logbox.insertPlainText("\t")
        self.Logbox.insertPlainText("Simulation Started")
        self.Logbox.setDisabled(True)
        self.step = 0
        self.button_load.setDisabled(True)
        self.button_search.setDisabled(True)
        self.lineEdit.setDisabled(True)
        self.btnBox.setDisabled(True)
        self.pbar.setRange(0,0)
        '''self.button_load.setEnabled(True)
        self.button_search.setEnabled(True)
        self.lineEdit.setEnabled(True)
        self.Logbox.setEnabled(True)'''                                                                        
        #os.killpg(p.pid, signal.SIGINT)
    def evt_update_progress(self,val):
            self.pbar.setValue(val)
    def evt_LoadingSuccessful(self,val):
        if(val):
            self.button_load.setEnabled(True)
            self.button_search.setEnabled(True)
            self.lineEdit.setEnabled(True)
            self.Logbox.setTextColor(QColor(100,150,100))
            self.Logbox.insertPlainText("\n")
            now = datetime.now()
            current_time = now.strftime("%d/%m/%Y %H:%M:%S")
            self.Logbox.insertPlainText(current_time)
            self.Logbox.insertPlainText("\t") 
            self.Logbox.insertPlainText("Loading Successful")
        else:
            self.button_load.setDisabled(True)
            self.button_search.setDisabled(True)
            self.lineEdit.setDisabled(True)
    def closeEvent(self, event):
            reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?',QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                event.accept()
                global Flag_Status
                Flag_Status = 5
                QCoreApplication.instance().quit()
                os.killpg(p.pid, signal.SIGINT)    
            else:
	            event.ignore()

class WorkerThread(QThread):
    update_progress = pyqtSignal(int)
    LoadingSuccessful = pyqtSignal(bool)
    def receive_callback(self,ch, method, properties, body):
        global message_type, message_id
        global Flag_Status
        message_id = properties.message_id
        message_type = properties.type
        print(message_id)
        
        if(message_id=="ProgramFinishedID"):
            Flag_Status = 8
        elif(message_id=="ServerReadyID"):
            Flag_Status = 1
        elif(message_id=="PathReceivedSuccessfullyID"):
            Flag_Status = 2
        elif(message_id=="LoadInProgressID"):
            Flag_Status = 3
            Percent = int(message_type)
            self.update_progress.emit(Percent)
            self.LoadingSuccessful.emit(False)
        elif(message_type=="FileLoadedSuccessfully"):
            Flag_Status = 7    
            Percent = 100
            self.update_progress.emit(Percent)
            self.LoadingSuccessful.emit(True)
        else:
            Flage_Status = 0
    
    def RBMQ(self):
        global Flag_Status
        self.cred = pika.PlainCredentials('genia', 'genia123')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/', self.cred))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='GUI', durable=False)
        self.channel.queue_bind(queue='GUI', exchange='ns3', routing_key='GUI')
        self.channel.basic_consume(queue='GUI', auto_ack=True,
            on_message_callback=self.receive_callback)
        print("Starting Consuming") 
        self.channel.start_consuming()

    def run(self):
        self.RBMQ()
        
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = Dialog()
    dlg.show()
    dlg.GUI_Ready()
    sys.exit(app.exec_())