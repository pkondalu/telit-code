# #######         NARESH-(11022015)             ######## #
from Common import *
from SBMReading import *
import GlobalVaria
import MOD
import SER
import MDM
import sys
global 	FILE_CREATE
global 	FILE_APPEND
global 	FILE_END
global 	FILE_ONE_RECORD
global 	NETWORK
global SmsFlag
global 	BILL_HTTP_LINK
GlobalVaria.HTML_ADDR = ''
SmsFlag = '0'
FILE_CREATE 	= '0'
FILE_APPEND 	= '1'
FILE_END 		= '2'
FILE_ONE_RECORD = '3'
GlobalVaria.ServerFileName	= ""
GlobalVaria.HTML_SERVICE = " "
GlobalVaria.Type			= 0
GlobalVaria.StarRecNo		= 0
GlobalVaria.Servertrial		= 0
GlobalVaria.HttpUploadFileName = ''
GlobalVaria.ConnectionPacket 	= ''
GlobalVaria.uploadFileSize		= 0
GlobalVaria.ContentLen 			= 0
GlobalVaria.TicketNo 			= ''
GlobalVaria.send_connection_packet = 0
GlobalVaria.TxtUpldRecNo=0
GlobalVaria.TotRec2Upload =0
GlobalVaria.rawseek =0;
GlobalVaria.data_length=0;
GlobalVaria.data_length_sz = 0
GlobalVaria.recno=0
GlobalVaria.recno_sz = 0
GlobalVaria.RawUpldRecNo = 0

def initializeseekFile():
	#print 'in initializeseekFile \n'
	try:
		SeekHandler = open(GlobalVaria.SEEK_PTR,'w')
	except IOError:
		#print 'SEEK_PTRopen Failed'
		return 0
	SeekHandler.write("000000")
	SeekHandler.close()
	return 1

def Digit_cnt(myNumber):
	num_digits=0;
	if(myNumber == 0):
		num_digits = 1
	while(myNumber > 0):
		num_digits = num_digits + 1
		myNumber = myNumber/10
	return num_digits;

def DayChange():
	smssendFileHandler = 0
	writeedlen = 0
	Position = 0
	k=0
	i=0
	tempbuff = "" 
	#print 'In day change Function \n',GlobalVaria.DataAvailable2Upload
	if((GlobalVaria.DataAvailable2Upload == 1)and(GlobalVaria.simavailable == 1)):#changed the code becz we need to enable the flag only when sim is there
		GlobalVaria.DataAvailable2Upload = 0
		#print 'in day change GlobalVaria.uploadSBMData',GlobalVaria.uploadSBMData
		GlobalVaria.uploadSBMData = 1

def SmsSetup():
	#PrintDebug("SmsSetup")
	MdmRes = ''
	result = ExecuteATCommand('AT+CNMI=2,1\r','OK',1,120,3)
	if(result == 0):
		GlobalVaria.SmsFlag = 0
		#PrintDebug('SMS not AVAILABLE' + MdmRes)
	else:
		result = ExecuteATCommand('AT+CMGF=1\r','OK',1,120,3)
		if(result == 0):
			GlobalVaria.SmsFlag = 0
			#PrintDebug('SMS not AVAILABLE' + MdmRes)
		else:
			GlobalVaria.SmsFlag = 1

def GprsSetup():
	TrailCnt = 0
	while(GlobalVaria.simavailable == 1 and GlobalVaria.Gprs_Flag == 0 and TrailCnt < 3):
		PrintDebug("GPRS Initialization"+ str(TrailCnt))
		GlobalVaria.Gprs_Flag = 0
		GlobalVaria.Http_Cfg_Flag = 0
		GlobalVaria.Gprs_Flag = SetGprsInitilization()
		TrailCnt = TrailCnt + 1

def RTCSetup():
	PrintDebug("RTC Setup")
	if(GlobalVaria.Gprs_Flag == 1):
		PrintDebug("EXecuting NTP command")
		result = ExecuteATCommand('at#ntp="ntp1.inrim.it",123,1,5\r','#NTP:',1,120,1)
		if(result == 1):
			PrintDebug('#NTP is found RTC IS SET')
			Rtc_Set_Flag = '1'
		else:
			PrintDebug('#NTP is found RTC IS NOT SET')
			Rtc_Set_Flag = '0'

def FindSbmCmnd(sbmcmd):
	#PrintDebug("in find SBM Command")
	commandFunctions = {'\x21': SetUrls,
						'\x22': WriteUploadDataToFile,
						'\x23': GetHealthStatus,
						'\x24': ReadUrls,
						'\x25': DeleteFiles,
						'\x28': ReadRecordFromServer,
						'\x29': SetRTC,
						'E': ExitProgram,
						'R': RTCCommand,
						'\x2D': GetCpuVersion}
	modemFunction = commandFunctions[sbmcmd]
	modemFunction()
	#SER.send("in find SBM Command- End")

def SetUrls():
	PrintDebug("SetUrls")
	GlobalVaria.Info['HttpUrl'] = "%.80s" % GlobalVaria.SBMBuffer[2:82]
	GlobalVaria.Info['ApnServer'] = "%.30s" % GlobalVaria.SBMBuffer[82:112]
	PrintDebug(GlobalVaria.Info['HttpUrl'])
	PrintDebug(GlobalVaria.Info['ApnServer'])

def WriteUploadDataToFile():
	PrintDebug("Writting Data to File")
	InfileHandler = -1
	GlobalVaria.sbmInFileLength1 = 0
	GlobalVaria.SBMBuffer = GlobalVaria.SBMBuffer[2:-1]
	GlobalVaria.SBMBuffer = GlobalVaria.SBMBuffer + '\0'
	GlobalVaria.sbmInFileLength1 = FileSize(GlobalVaria.SBM_DATA_INFILE1)
	if(GlobalVaria.sbmInFileLength1 > 49000):
		if((FileCheck(GlobalVaria.SBM_DATA_INFILE2)== -1) and (FileCheck(GlobalVaria.SBM_DATA_OUTFILE)== 1)):
			rename(GlobalVaria.SBM_DATA_INFILE1,GlobalVaria.SBM_DATA_INFILE2)
			GlobalVaria.sbmInFileLength1 = 0
			GlobalVaria.sbmInFileLength2 = FileSize(GlobalVaria.SBM_DATA_INFILE2)
		else:
			GlobalVaria.InFileLenExceededflag = '1';
			SER.send('\0x02')
			return
	try:
		InfileHandler = open(GlobalVaria.SBM_DATA_INFILE1,'a')
	except IOError:
		SER.send('\x03')
		return 0
	InfileHandler.write(GlobalVaria.SBMBuffer)
	writeedlen = len(GlobalVaria.SBMBuffer)
	GlobalVaria.sbmInFileLength1 = FileSize(GlobalVaria.SBM_DATA_INFILE1)
	GlobalVaria.sbmInFileLength2 = 0
	InfileHandler.close()
	InfileHandler = -1
	PrintDebug("Writting Complated")
	
def GetHealthStatus():
	PrintDebug("GetHealthStatus")
	length = 99999
	length = '%05d'%(length)
	StrLeng = '%.05s'%(str(length))
	if(GlobalVaria.simavailable == 0):
		GlobalVaria.SignalStrength = '00'
		GlobalVaria.SignalStrength = '%02s'%(GlobalVaria.SignalStrength)
		GlobalVaria.Gprs_Flag = 0
		GlobalVaria.HttpCon = 0
	GlobalVaria.SignalStrength = '%02s'%(GlobalVaria.SignalStrength)
	tempbuff = '@' + StrLeng + GlobalVaria.SignalStrength + str(GlobalVaria.simavailable) + str(GlobalVaria.Gprs_Flag) + str(GlobalVaria.HttpCon) +'T#' 
	if(len(tempbuff) != 0):
		SER.send("%s" %tempbuff)

def ReadUrls():
	PrintDebug("ReadUrls")
	tempbuff = '@'+ GlobalVaria.Info['HttpUrl'] + GlobalVaria.Info['ApnServer'] + '#'
	SER.send(tempbuff)

def ReadFile(filename, offset, numOfBytes):
	PrintDebug("Reading File")
	Datafile = -1
	fileData =''
	if(FileCheck(filename) == 1):
		try:
			Datafile = open(filename,'r')
		except IOError:
			PrintDebug("Error")
			return 0
		Datafile.seek(offset,0)
		fileData = Datafile.read(numOfBytes)
		Datafile.close()
		PrintDebug("File Data:" + fileData)
		return fileData
	else:
		PrintDebug("File Not found :"  +filename)
		return ''
		
def DeleteFile(filename):
	PrintDebug("fileName:" + filename)
	if(FileCheck(filename) == 1):
		command = 'AT#DSCRIPT="' + GlobalVaria.SBM_DATA_INFILE1 + '"\r'
		result = ExecuteATCommand(command,"OK",10,120,1)
		if(result== 1):
			PrintDebug("FileName:"+ filename + " Deleted")
			return 1
		else:
			PrintDebug("Error in deleting FileName:"+ filename)
			return 0
	else:
		PrintDebug("File :" + filename + " Not Found")	
	
def DeleteFiles():
	PrintDebug("DeleteFiles")
	DeleteFile(GlobalVaria.SBM_DATA_OUTFILE)
	DeleteFile(GlobalVaria.SBM_DATA_INFILE1)
	DeleteFile(GlobalVaria.SBM_DATA_INFILE2)

def ReadRecordFromServer():
	PrintDebug("ReadRecordFromServer")
	postUrl = "http://apepdclatmsbm.ctms.info/SBMDOWNLOAD.asmx/ReadRecord"
	PostData(postUrl, "filename=12345678&recno=1")

def SetRTC():
	PrintDebug("GetRTC")
	tempbuff = [0]* 30
	GlobalVaria.SBMBuffer = GlobalVaria.SBMBuffer[2:-1]
	GlobalVaria.SBMBuffer = GlobalVaria.SBMBuffer + '\0'
	GlobalVaria.DateTime['year'] = GlobalVaria.SBMBuffer[0:2]
	GlobalVaria.DateTime['month'] = GlobalVaria.SBMBuffer[2:4]
	GlobalVaria.DateTime['day'] = GlobalVaria.SBMBuffer[4:6]
	GlobalVaria.DateTime['hour'] = GlobalVaria.SBMBuffer[6:8]
	GlobalVaria.DateTime['min'] = GlobalVaria.SBMBuffer[8:10]
	GlobalVaria.DateTime['sec'] = GlobalVaria.SBMBuffer[10:12]
	tempbuff = "\"" + GlobalVaria.DateTime['day'] + "/"+GlobalVaria.DateTime['month'] + "/"+GlobalVaria.DateTime['year'] + ","+GlobalVaria.DateTime['hour'] + ":"+GlobalVaria.DateTime['min'] + ":"+GlobalVaria.DateTime['sec'] + "+" +"00" + "\""
	command = 'AT+CCLK=' + tempbuff + '\r'
	PrintDebug(command)
	result = ExecuteATCommand(command,"OK",1,120,2)
	if(result == 1):
		SER.send('\x02')
	else:
		SER.send('\x03')

def GetCpuVersion():
	PrintDebug("GetCpuVersion")	
	SER.send("%s" %GlobalVaria.SBM_SW_VERSION)

def RTCCommand():
	PrintDebug("Reading RTC Command")
	ReadRTC()
	PrintDebug("Current Date:" + str(GlobalVaria.SBM_RTC_BUFFER))
	SER.send(GlobalVaria.SBM_RTC_BUFFER)
	
def ExitProgram():
	PrintDebug("Exit Program")
	GlobalVaria.exitFlag = 1

def SendDataToServer(filename):
	PrintDebug("SendDataToServer" + filename)
	postUrl = "http://apepdclatmsbm.ctms.info/SBMDOWNLOAD.asmx/GetCollectionData"
	
def ProcessSBMCommand():
	while(1):
		PrintDebug("SBS Command Process")
		#PrintDebug("Waiting for command")
		# COMMAND_START = 0
		# COMMAND_END = 1
		#if(len(GlobalVaria.UartData) > DATA_LEN):
		#PrintDebug("Data is more than the defined limit")
		#PrintDebug("Wiating on seriel port")
		GlobalVaria.UartData = GlobalVaria.UartData + SER.read()
		PrintDebug(GlobalVaria.UartData)
		startIndex = GlobalVaria.UartData.find('\x02')
		endIndex = GlobalVaria.UartData.find('\x03')
		PrintDebug("Start Index:" + str(startIndex))
		PrintDebug("end Index:" + str(endIndex))
		if(startIndex != -1 and  endIndex!= -1):
			GlobalVaria.SBMBuffer = GlobalVaria.UartData[startIndex:endIndex+1]
			PrintDebug("Command: " + GlobalVaria.SBMBuffer)
			SER.send('\x02')
			FindSbmCmnd(GlobalVaria.SBMBuffer[1])
			GlobalVaria.UartData = GlobalVaria.UartData[endIndex+1:]
			PrintDebug("Remaining:" + GlobalVaria.UartData)
		else:
			SER.send('\0x03')
			break
			
def StartMethod():
	PrintDebug ('SBM READING © 2014 ENTRY Telit Communications')
	GlobalVaria.simavailable = ExecuteATCommand('AT+CPIN?\r','+CPIN',5,120,3)
	GlobalVaria.SignalStrength = '00'
	GlobalVaria.SignalStrength = GetSignalStrength()
	PrintDebug('Main Task -Version : ' + GlobalVaria.SBM_SW_VERSION)
	#ReadInformationFile()
	ModemSetup()
	loopIndex = 1
	TrailCnt = 0
	SmsSetup()
	GprsSetup()
	RTCSetup()
	
	while(1):
		MdmRes = ''
		res = ''
		Expired = ''
		PrintDebug('Running in the main Loop')
		ReadRTC()
		MDM.receive(1)
		MDM.receive(1)
		MDM.receive(1)
		GlobalVaria.SignalStrength = GetSignalStrength()
		if(int(GlobalVaria.SignalStrength) > 9):
			if(GlobalVaria.Gprs_Flag == 0 or GlobalVaria.Http_Cfg_Flag == 0):
				#PrintDebug("Preparing for GPRs/HTTP setup")
				SetGprsInitilization()
				if(GlobalVaria.Gprs_Flag != 1 or GlobalVaria.Http_Cfg_Flag != 1):
					GlobalVaria.Gprs_Flag = 0
					GlobalVaria.Http_Cfg_Flag = 0
					ModemSetup()
				else:
					PrintDebug("GPRS/HTTP Setup already done")
			else:
				PrintDebug('Gprs is Available')
		else:
			PrintDebug('GlobalVaria.SignalStrength is Low'+ str(GlobalVaria.SignalStrength))
			GlobalVaria.SignalStrength = '00';
		
		if(Rtc_Set_Flag == '0') and (GlobalVaria.Gprs_Flag == 1):
			PrintDebug('Setting Rtc_Set_Flag'+ str(Rtc_Set_Flag))
			RTCSetup()
		else:
			PrintDebug("RTC already set")
			
		if(GlobalVaria.SmsFlag == 0):
			PrintDebug('Sms Settuping')
			SmsSetup()
			MDM2.receive(10)
		else:
			PrintDebug("SMS Setup Already Done")
		#DayChange()
		GlobalVaria.exitFlag = 0
		ProcessSBMCommand()
		GetFileSize(GlobalVaria.SBM_DATA_OUTFILE)
		GetFileSize(GlobalVaria.SBM_DATA_INFILE1)
		GetFileSize(GlobalVaria.SBM_DATA_INFILE2)
		#ReadFile(GlobalVaria.SBM_DATA_INFILE1, 100,1000)
		SendDataToServer(GlobalVaria.SBM_DATA_INFILE1)
		if(GlobalVaria.exitFlag == 1):
			PrintDebug("Exit Program")
			return
		MOD.sleep(60)

led = 0
data = ''
GlobalVaria.UartData = ''
GlobalVaria.SBMBuffer = ''
SbmEntry = 0
Rtc_Set_Flag = '0'
TrailCnt  = 0
loopIndex = 1
MdmRes=''
SER.set_speed('115200','8N1')
PrintDebug("Starting")
MOD.sleep(5)
loopIndex = 1
GlobalVaria.Gprs_Flag = 0
GlobalVaria.simavailable = 0
GlobalVaria.Http_Cfg_Flag = 0
GlobalVaria.SmsFlag = 0
GlobalVaria.HttpCon = 0
GlobalVaria.gAtResponse = '0'
SendDataToServer(GlobalVaria.SBM_DATA_INFILE1)
PrintDebug("Program existed")
# while(loopIndex < 10):
	# PrintDebug("Starting")
	# StartMethod()
	# MOD.sleep(60)
	# loopIndex = loopIndex + 1
	

