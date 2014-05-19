#Importing Python Libraries
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import re
import ConfigParser

#Importing Paramiko
try:
    import paramiko
    paramiko_error = False
except ImportError as e:
    paramiko_error = True

#Importing Ui files
from ui import mainwindow

#Impporting Own libraries
from libs import monitoring_gui as mnt
from libs import misc_gui as misc


class configReplicator(QMainWindow, mainwindow.Ui_MainWindow):
    """
    Main Window Class
    """
    def __init__(self, parent=None):
        """
        Initialization Function
        """
        super(configReplicator, self).__init__(parent)
        self.setupUi(self)
        self.scriptTextEdit.setPlainText('Load the .src file with the configuration to send to the Devices ...')
        self.listTextEdit.setPlainText('Load the .lst file with the list of Devices to connect to and send the configuration ...')
        self.scriptTextEdit.setEnabled(False)
        self.listTextEdit.setEnabled(False)
        self.saveScriptPushButton.setEnabled(False)
        self.saveListPushButton.setEnabled(False)
        self.script_selected = False
        self.list_selected = False
        self.scriptNameLabel.setText('')
        self.listNameLabel.setText('')
        self.username = ''
        self.password = ''
        self.enable_password = ''
        self.commands = []
        self.destinations = []
        self.output = False
        self.summaryReport = ''
        self.outputReport = ''
        if paramiko_error:
            self.alertLabel.setText('Alert: Ssh is Disabled!!!')
        else:
            self.alertLabel.hide()
        self.updateUi()

    @pyqtSignature("")
    def on_actionClear_triggered(self):
        """
        Function to run when the Clear Button in the toolbar is pressed
        """
        self.threadsHorizontalSlider.setValue(1)
        self.scriptTextEdit.setPlainText('Load the .src file with the configuration to send to the Devices ...')
        self.listTextEdit.setPlainText('Load the .lst file with the list of Devices to connect to and send the configuration ...')
        self.scriptTextEdit.setEnabled(False)
        self.listTextEdit.setEnabled(False)
        self.script_selected = False
        self.list_selected = False
        self.saveScriptPushButton.setEnabled(False)
        self.saveListPushButton.setEnabled(False)
        self.scriptNameLabel.setText('')
        self.listNameLabel.setText('')
        self.username = ''
        self.password = ''
        self.enable_password = ''
        self.commands = []
        self.destinations = []
        self.output = False
        self.summaryReport = ''
        self. outputReport = ''
        self.updateUi()
        self.statusbar.showMessage('Al Values Cleared ...', 2000)

    @pyqtSignature("")
    def on_scriptPushButton_clicked(self):
        """
        Function to run when the Load Script button is clicked
        """
        fname = QFileDialog.getOpenFileName(self, 'Open File', directory='scripts/', filter='Script (*.src)')
        if fname != '':
            self.scriptTextEdit.setEnabled(True)
            filename = re.search('(.*)[\\|\/](.+\.src)', fname).group(2)
            f = open(fname, 'r')
            self.scriptTextEdit.setPlainText(f.read())
            f.close()
            self.script_selected = True
            self.scriptNameLabel.setText(filename)
            self.statusbar.showMessage('Selected script %s' % fname, 2000)
            self.commands = self.getCommands(fname)

        self.saveScriptPushButton.setEnabled(False)
        self.updateUi()

    @pyqtSignature("")
    def on_saveScriptPushButton_clicked(self):
        """
        Function to run when the Save Script is clicked
        """
        fname = QFileDialog.getSaveFileName(self, 'Save File', directory='scripts/', filter='Script (*.src)')
        if fname != '':
            f = open(fname, 'w')
            f.write(self.scriptTextEdit.toPlainText())
            f.close()
            filename = re.search('(.*)[\\|\/](.+\.src)', fname).group(2)
            self.scriptNameLabel.setText(filename)
            self.saveScriptPushButton.setEnabled(False)
            self.statusbar.showMessage('Saved script %s' % fname, 2000)
            self.commands = self.getCommands(fname)

    @pyqtSignature("")
    def on_listPushButton_clicked(self):
        """
        Function to run when the Load Destination List is clicked
        """
        fname = QFileDialog.getOpenFileName(self, 'Open File', directory='lists/', filter='List (*.lst)')
        if fname != '':
            self.listTextEdit.setEnabled(True)
            filename = re.search('(.*)[\\|\/](.+\.lst)', fname).group(2)
            f = open(fname, 'r')
            self.listTextEdit.setPlainText(f.read())
            f.close()
            self.list_selected = True
            self.listNameLabel.setText(filename)
            self.statusbar.showMessage('Selected List %s' % fname, 2000)
            self.destinations = self.getDevices(fname)

        self.saveListPushButton.setEnabled(False)
        self.updateUi()

    @pyqtSignature("")
    def on_saveListPushButton_clicked(self):
        """
        Function to run when the Save Destination List is clicked
        """
        fname = QFileDialog.getSaveFileName(self, 'Save File', directory='lists/', filter='List (*.lst)')
        if fname != '':
            f = open(fname, 'w')
            f.write(self.listTextEdit.toPlainText())
            f.close()
            filename = re.search('(.*)[\\|\/](.+\.lst)', fname).group(2)
            self.listNameLabel.setText(filename)
            self.saveListPushButton.setEnabled(False)
            self.statusbar.showMessage('Saved Destination List %s' % fname, 2000)
            self.destinations = self.getDevices(fname)

    @pyqtSignature("")
    def on_actionSettings_triggered(self):
        """
        Function to run when the Settings button on the toolbar is pressed
        """
        settings = misc.settingsWindow(self)
        settings.show()

    @pyqtSignature("")
    def on_actionHelp_triggered(self):
        """
        Function to run when the Help button on the toolbar is pressed
        """
        helpbrw = misc.helpWindow(self)
        helpbrw.show()

    @pyqtSignature("")
    def on_actionReports_triggered(self):
        """
        Function to run when the Reports button on the toolbar is pressed
        """
        reports = misc.reportsWindow(self.summaryReport, self.outputReport, self)
        reports.show()

    @pyqtSignature("")
    def on_actionConnect_triggered(self):
        """
        Function to run when the Connect button on the toolbar is pressed
        """
        #Launching Dialog to get the credentials
        credentials = misc.credentialDlg(self)
        credentials.connect(credentials, SIGNAL("credentials(QString, QString)"), self.get_credentials)
        credentials.exec_()

        #Use Enable?
        configure = ConfigParser.ConfigParser()
        configure.read('config.cfg')
        use_enable = configure.get('enable', 'enable').replace("\'", "").lower()

        if use_enable == 'yes':
            #Launching Dialog to get the credentials
            enable_dialog = misc.enableDlg(self)
            enable_dialog.connect(enable_dialog, SIGNAL("enable(QString)"), self.get_enable)
            enable_dialog.exec_()

        warning_msg = 'After this screen you will use the credentials entered to send the script \"%s\" to each device saved on the destination list \"%s\", using %i threads.\nDo you Want to Continue?' % (self.scriptNameLabel.text(), self.listNameLabel.text(), self.threadsHorizontalSlider.value())
        resp = QMessageBox.warning(self, 'Warning', warning_msg, QMessageBox.Yes | QMessageBox.No)

        if resp == QMessageBox.Yes:
            #Launching Monitoring Dialog
            monit = mnt.monitoringDlg(self.scriptNameLabel.text(),
                                  self.listNameLabel.text(),
                                  self.threadsHorizontalSlider.value(),
                                  self.commands,
                                  self.destinations,
                                  self.username,
                                  self.password,
                                  self.enable_password,
                                  self.output,
                                  self)
            monit.connect(monit, SIGNAL("summary_report(QString)"), self.getSummaryReport)
            monit.connect(monit, SIGNAL("output_report(QString)"), self.getOutputReport)
            monit.show()
            monit.exec_()

        self.username = ''
        self.password = ''
        self.enable_password = ''

    @pyqtSignature("")
    def on_scriptTextEdit_textChanged(self):
        """
        Function to run when the script is changed
        """
        self.saveScriptPushButton.setEnabled(True)

    @pyqtSignature("")
    def on_listTextEdit_textChanged(self):
        """
        Function to run when the destination list is changed
        """
        self.saveListPushButton.setEnabled(True)

    def getCommands(self, fname):
        """
        Function to process the commands on the script
        """
        #Creating list with commands to send and output directive
        fd = open(fname, 'r')
        output_pattern = re.compile('(^![Oo][Uu][Tt][Pp][Uu][Tt])(.*)\n')
        commands = []
        self.output = False
        for line in fd:
            if not re.search('^!', line):
                commands.append(line)
            elif re.search(output_pattern, line):
                self.output = True
        fd.close()
        return commands

    def getDevices(self, fname):
        """
        Function to process the destination list
        """
        fd = open(fname, 'r')
        ip_regex = re.compile('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')
        destinations = []
        for line in fd:
            if re.match(ip_regex, line):
                param = line.split(' ')
                #Processing IP Address
                ip_addr = param[0].strip('\n')
                #Processing Device name
                try:
                    dev_name = param[1].strip('\n')
                except IndexError:
                    dev_name = 'N/A'
                #processing Connection Mode
                try:
                    conn_mode = param[2].lower().strip('\n')
                    if conn_mode not in ['telnet', 'ssh']:
                        conn_mode = 'telnet'
                except IndexError:
                    conn_mode = 'telnet'
                destinations.append((ip_addr, dev_name, conn_mode))
        fd.close()
        return destinations

    def updateUi(self):
        """
        Function to refresh the interface
        """
        if self.script_selected and self.list_selected:
            self.actionConnect.setEnabled(True)
        else:
            self.actionConnect.setEnabled(False)

    def get_credentials(self, user, pwd):
        """
        Function to save the credentials entered
        """
        self.username = str(user)
        self.password = str(pwd)

    def get_enable(self, en):
        """
        Function to save the enable password entered
        """
        self.enable_password = str(en)

    def getSummaryReport(self, summary):
        self.summaryReport = str(summary)

    def getOutputReport(self, output):
        self.outputReport = str(output)


def welcome():
    """
    Function to print the Welcome Screen
    """
    welcome_string = """Welcome to the Config Replicator
======================

All the scripts should be saved with an \".src\" extension on the \"scripts\" directory, read the README file on the directory to know more about this files.

All the destination lists should be saved with a \".lst\" extension on the \"lists\" directory, read the README file on the directory to know more about this files.

You could find the reports on the \"reports\" directory with a format \"SummaryReportMMDDYYYYHHMM.txt\" and if your script needs output then it will be generated another report with the format \"OutputReportMMDDYYYYHHMM.txt\"

This program uses multithreading to speed up the process when the destination list is big, you could select the number of threads to spawn on the main window, please use a reasonable number here you could have undesirable results if this number is too big.

The flow of the program could be resumed as:
    - Select the script to send to each device
    - Select the destination list where to send the script selected
    - Select the number of threads to use
    - Enter the Username and Password to use to connect to the devices
    - Enter the Enable password if requested"""
    if paramiko_error:
        welcome_string = welcome_string + "\n\n######## THERE WAS A PROBLEM LOADING PARAMIKO ########\n######## SSH CONNECTIONS WILL NOT BE POSSIBLE ########"

    mb = QMessageBox()
    mb.setInformativeText(welcome_string)
    mb.setIcon(QMessageBox.Information)
    mb.setWindowFlags(Qt.WindowStaysOnTopHint)
    mb.show()
    mb.raise_()
    mb.exec_()


if __name__ == "__main__":
    import sys
    #Creating Qt application
    app = QApplication(sys.argv)

    #Calling Welcome Windows
    welcome()

    #Creating MainWindow
    form = configReplicator()

    form.show()
    app.exec_()

__author__ = 'Miguel Ercolino'