#  #######           NARESH-(11022015)             ######## #
from Common import *
import GlobalVaria
import MOD
import SER
import MDM
import MDM2
import sys

global UartDataIn
global 	SMSCount
global OutfileHandler

OutfileHandler = -1
mycase = {'!':'' ,'"':'' ,'@':'' ,'#':'' ,'%':'' }
VALID   	= {'0':'\x06'};
INVALID 	= {'0':'\x15'};
STX     	= {'0':'\x02','1':'\x03'};
END     	= {'0':'\x0d','1':'\x0a'};
DEFAULT_APN_SERVER			 = "airtelgprs.com                "
DEFAULT_HTTPURL				 = "http://cpdclcollservice.atil.info/service.asmx/                                 "
UartDataIn = 0
def FileSize(FileName):
	size = 0
	file = 0
	exist = 0
	try:
		file = open(FileName, "r")
	except IOError:
		##print "There was an error reading file"
		return 0
	file_text = file.seek(0,2)
	size = file.tell()
	##print 'value',size
	file.close()
	return size
# ########################################################### #
# ###############        Write INFO.INF            #########
# ########################################################### #

def WriteInformationfile():
	infofileHandler = -1
	#print 'Writing in to the Information File'
	clen = 0
	GlobalVaria.Infodata = GlobalVaria.Info['HttpUrl']+ GlobalVaria.Info['ApnServer'] + ' '
	##print 'INFORMATION File Data-',Infodata
	try:
		infofileHandler = open(GlobalVaria.INFORMATION_FILE, 'w')
	except IOError:
		#print 'INFORMATION_FILE open failed'
		return 0
	infofileHandler.write(GlobalVaria.Infodata)
	##print 'INFORMATION_FILE is writen'
	infofileHandler.close()
	return 1

# ########################################################### #
# ###############        ReadINFO.INF            #########
# ########################################################### #

def ReadInformationFile():
	ret = -1
	infofileHandler = 0
	##print 'In Read Information File'
	try:
		infofileHandler = open(GlobalVaria.INFORMATION_FILE, 'r')
	except IOError:
		##print '%s open Failed',GlobalVaria.INFORMATION_FILE
		GlobalVaria.Info['HttpUrl'] = DEFAULT_HTTPURL
		GlobalVaria.Info['ApnServer'] = DEFAULT_APN_SERVER
		if(WriteInformationfile() == 1):
			##print 'write info file success\n'
			try:
				infofileHandler = open(GlobalVaria.INFORMATION_FILE, 'r')
			except IOError:
				#print '%s open Failed',GlobalVaria.INFORMATION_FILE
				return 0
	GlobalVaria.Infodata = infofileHandler.read(110)
	##print 'INFO.INF is read',len(Infodata)
	if(len(GlobalVaria.Infodata) != 110):
		#print 'file reading failed number of bytes',len(GlobalVaria.Infodata)
		infofileHandler.close()
		return
	for index in range(len(GlobalVaria.Infodata),111):
		GlobalVaria.Infodata = GlobalVaria.Infodata + ' '
	infofileHandler.close()
	##print 'In Read Information File:'
	GlobalVaria.Info['HttpUrl'] = "%.80s" % GlobalVaria.Infodata[0:80]
	##print 'read HttpUrl',GlobalVaria.Info['HttpUrl']
	GlobalVaria.Info['ApnServer'] = "%.30s" % GlobalVaria.Infodata[80:110]
	##print 'read apn name',GlobalVaria.Info['ApnServer']
	#print 'ReadInformationfile Over'
	return 1


# ########################################################### #
# #####   Function for Checking File exist(1) or Not(-1)   ### #
# ########################################################### #
def Wait4Datainsbm():
	data = ''
	##print '\n-------------Mdm command--------------'
	timeout = MOD.secCounter() + 5
	while((len(data) == 0) and (MOD.secCounter() < timeout)):
		data = data + MDM.receive(1)
	return data
def Wait4DataInMdm2():
	data = ''
	##print '\n-------------Mdm2 command--------------'
	timeout = MOD.secCounter() + 5
	while((len(data) == 0) and (MOD.secCounter() < timeout)):
		data = data + MDM2.receive(1)
	return data

def FileCheck(filename):
	CheckHandler = -1
	##print 'In Check File',filename
	try:
		CheckHandler = open(filename,'r')
	except IOError:
		#print 'filename open Failed',filename
		return -1
	##print 'File open succes',filename
	CheckHandler.close()
	return 1

def WriteDataInfile():
	##print 'Writing data in File'
	InfileHandler = -1
	GlobalVaria.sbmInFileLength1 = 0
	GlobalVaria.SBMBuffer = GlobalVaria.SBMBuffer[2:-1]
	GlobalVaria.SBMBuffer = GlobalVaria.SBMBuffer + '\0'
	GlobalVaria.SBMBuffer = GlobalVaria.SBMBuffer + END['0']
	GlobalVaria.SBMBuffer = GlobalVaria.SBMBuffer + END['1']
	##print 'Latest SBMBuffer %s-%d'%(GlobalVaria.SBMBuffer,len(GlobalVaria.SBMBuffer))
	##print 'GlobalVaria.SBM_DATA_INFILE-1',GlobalVaria.SBM_DATA_INFILE1
	GlobalVaria.sbmInFileLength1 = FileSize(GlobalVaria.SBM_DATA_INFILE1)
	##print 'sbmInFileLength file length = %d:',GlobalVaria.sbmInFileLength1
	if(GlobalVaria.sbmInFileLength1 > 49000):
		##print 'sbmInFileLength file length is Greater that n 49k'
		if((FileCheck(GlobalVaria.SBM_DATA_INFILE2)== -1) and (FileCheck(GlobalVaria.SBM_DATA_OUTFILE)== 1)):
			#print 'Sbm Infile2 is not there so renaming Infile2 to Infile2'
			rename(GlobalVaria.SBM_DATA_INFILE1,GlobalVaria.SBM_DATA_INFILE2)
			GlobalVaria.sbmInFileLength1 = 0
			GlobalVaria.sbmInFileLength2 = FileSize(GlobalVaria.SBM_DATA_INFILE2)
		else:
			#print 'SBM canot store more data '
			GlobalVaria.InFileLenExceededflag = '1';
			SER.send("%s" %INVALID['0'])
			return
	##print 'Appending in to INFILE-1'
	try:
		InfileHandler = open(GlobalVaria.SBM_DATA_INFILE1,'a')
	except IOError:
		##print 'GlobalVaria.SBM_DATA_INFILE-1 open Failed'
		SER.send("%s" %INVALID['0'])
		return 0
	InfileHandler.write(GlobalVaria.SBMBuffer)
	writeedlen = len(GlobalVaria.SBMBuffer)
	##print 'File Write Success',writeedlen
	GlobalVaria.sbmInFileLength1 = FileSize(GlobalVaria.SBM_DATA_INFILE1)
	GlobalVaria.sbmInFileLength2 = 0
	InfileHandler.close()
	InfileHandler = -1

def SendCmd(cmd,value):
	res = ''
	MDM.receive(1)
	MDM.receive(1)
	#print 'cmd-%s,value-%s'%(cmd,value)
	if (len(cmd) != 0):
		##print 'asigng ='
		cmd = cmd + '='
	else:
		cmd = cmd + '\r'
	res = MDM.send(cmd, 0)
	##print 'cmd sending '
	if (len(value) != 0):
		res = MDM.send(value, 0)	
		res = MDM.send('\r', 0)
		##print 'value sending'
		res = Wait4Datainsbm()
	#print '\n in sendcmd res',res
	return res
def SendCmdMdm2(cmd,value):
	res = ''
	MDM2.receive(10)
	MDM2.receive(2)
	#print 'cmd-%s,value-%s'%(cmd,value)
	if (len(cmd) != 0):
		##print 'asigng ='
		cmd = cmd + '='
	else:
		cmd = cmd + '\r'
	res = MDM2.send(cmd, 0)
	##print 'cmd sending '
	if (len(value) != 0):
		res = MDM2.send(value, 0)	
		res = MDM2.send('\r', 0)
		##print 'value sending'
		res = MDM2.receive(5)
	#print '\n in sendcmd res',res
	return res

def WriteDataOutFile():
	##print 'Renaming the Outfile \n'
	##print 'File size of SBM_DATA_OUTFILE Before Renaming ',FileSize(GlobalVaria.SBM_DATA_OUTFILE)
	if(FileCheck(GlobalVaria.SBM_DATA_OUTFILE)== -1):
		#print 'Outfile is not there so checking for  infile-2'
		if(FileCheck(GlobalVaria.SBM_DATA_INFILE2)== 1):
			rename(GlobalVaria.SBM_DATA_INFILE2,GlobalVaria.SBM_DATA_OUTFILE)
			GlobalVaria.sbmInFileLength2 = 0
			##print 'File size of SBM_DATA_OUTFILE After Renaming ',FileSize(GlobalVaria.SBM_DATA_OUTFILE)
		else:
			rename(GlobalVaria.SBM_DATA_INFILE1,GlobalVaria.SBM_DATA_OUTFILE)
			GlobalVaria.sbmInFileLength1 = 0
			GlobalVaria.sbmInFileLength2 = 0
		GlobalVaria.DataAvailable2Upload = 1
		GlobalVaria.sbmOutFileLength = FileSize(GlobalVaria.SBM_DATA_OUTFILE)
	else:
		print ''
		##print 'SBM_DATA_OUTFILE Contains data so cant be renamed \n'
def DeleteFiles():
	# data will be- \x02\x25 ''''''''''''''''''''''''''''\x03
	response = ""
	SER.send("%s" %VALID['0'])
	tempbuf = ''
	if(GlobalVaria.uploadSBMData==0):
		if(FileCheck(GlobalVaria.SBM_DATA_INFILE1)== 1):
			response = SendCmd('AT#DSCRIPT',GlobalVaria.SBM_DATA_INFILE1)
			#print 'response',response
			if(response.find('OK') != 0):
				print ''
				#print 'GlobalVaria.SBM_DATA_INFILE1  Available, Now Removed'
			else:
				print ''
				#print 'GlobalVaria.GlobalVaria.SBM_DATA_INFILE1  Not Available'
		response = ""
		if(FileCheck(GlobalVaria.SBM_DATA_INFILE2)== 1):
			response = SendCmd('AT#DSCRIPT',GlobalVaria.SBM_DATA_INFILE2)
			#print 'response',response
			if(response.find('OK') != 0):
				print ''
				#print 'GlobalVaria.SBM_DATA_INFILE2  Available, Now Removed'
			else:
				print ''
				#print 'GlobalVaria.GlobalVaria.SBM_DATA_INFILE2  Not Available'
		response = ""
		if(FileCheck(GlobalVaria.SBM_DATA_OUTFILE)== 1):
			response = SendCmd('AT#DSCRIPT',GlobalVaria.SBM_DATA_OUTFILE)
			#print 'response',response
			if(response.find('OK') != 0):
				print ''
				#print 'GlobalVaria.SBM_DATA_OUTFILE  Available, Now Removed'
			else:
				print ''
				#print 'GlobalVaria.SBM_DATA_OUTFILE  Not Available'
		tempbuf = "Files Deleted"
		GlobalVaria.sbmInFileLength = 0
		GlobalVaria.InFileLenExceededflag = '0';
		GlobalVaria.OutFileLenExceededflag = '0';
		GlobalVaria.sbmInFileLength2 = 0
		GlobalVaria.sbmOutFileLength = 0
		SER.send('%s' %tempbuf)
	else:
		tempbuf = "Data Upload In Progress"
		SER.send('%s' %tempbuf)
def GetRtc():
	#          yy/MM/dd,hh:mm:ss±zz
	# AT+CCLK="02/09/07,22:30:00+00"
	# data will be- \x02\x29 ''''''''''''''''''''''''''''\x03
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
	#print 'tempbuff',tempbuff
	if(SendCmdMdm2('AT+CCLK',tempbuff) != -1):
		SER.send("%s" %VALID['0'])
		return 1
	else:
		SER.send("%s" %INVALID['0'])
		return -1
	
def GetInfoData():
	# data will be- \x02\x21 ''''''''''''''''''''''''''''\x03
	#print 'In GetInfoData File'
	SER.send("%s" %VALID['0'])
	ReadInformationFile()
	GlobalVaria.Info['HttpUrl'] = "%.80s" % GlobalVaria.SBMBuffer[2:82]
	#print '\nread HttpUrl',GlobalVaria.Info['HttpUrl']
	GlobalVaria.Info['ApnServer'] = "%.30s" % GlobalVaria.SBMBuffer[82:112]
	#print '\nread apn name',GlobalVaria.Info['ApnServer']
	WriteInformationfile()
	#print 'Completed GetInfoData'
	MDM.send('AT#REBOOT\r', 0)  								#modem rebooting
def SendInformationFile():
	# data will be- \x02\x24 ''''''''''''''''''''''''''''\x03
	tempbuff = ''
	ReadInformationFile()
	#print 'in Send Info File'
	tempbuff = '@'+ GlobalVaria.Info['HttpUrl'] + GlobalVaria.Info['ApnServer'] + '#'
	# Ql_SendToUart(ql_uart_port1,(u8*)tempbuff,113);
	SER.send("\n%s" %tempbuff)
def SendHealthStatus():    # Need To be write the code
	# data will be- \x02\x23 ''''''''''''''''''''''''''''\x03
	tempbuff =  ''
	length = 0
	StrLeng = ''
	infilelength1 = 0
	infilelength2 = 0
	outfilelength = 0
	#print 'In Send Health Status Function'
	infilelength1 = FileSize(GlobalVaria.SBM_DATA_INFILE1)
	infilelength2 = FileSize(GlobalVaria.SBM_DATA_INFILE2)
	length = GlobalVaria.sbmOutFileLength + infilelength1 + infilelength2
	if(length > 99990):
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
	#print '\nHealth status',tempbuff
	if(len(tempbuff) != 0):
		SER.send("%s" %tempbuff)
def VersionInfo():
	#print 'SBM VERSION IS',GlobalVaria.SBM_SW_VERSION
	SER.send("%s" %GlobalVaria.SBM_SW_VERSION)
def ModemResponse():
	MdemString = ''
	DATA = ' '
	#print 'In modem response is performing'
	MdemString = GlobalVaria.SBMBuffer[2:-1]
	res = MDM2.send(MdemString,5)
	res = MDM2.send('\r',1)
	response = ' '
	response = Wait4DataInMdm2()
	#print 'response',response
	if(len(response) != 1):
		#print 'Response Came'
		if(response.find('#') != -1):# #KEPT BECZ WE GET RESPONSE OF IMEI IN # BUT IN M10E WE WONT 
			response = response[3:]
			DATA = '@\x0A'+response+'#'
		else:
			DATA = '@'+response+'#'
		SER.send("%s" %DATA)
	else:
		#print 'Response Not Came'
		SER.send("%s" %INVALID['0'])
		return

def FindSbmCmnd(sbmcmd):
	#print 'sbmcmd',sbmcmd
	mycase = {'!': GetInfoData,'"': WriteDataInfile,'#': SendHealthStatus,'$': SendInformationFile,
				'%': DeleteFiles,'&': '','\'': '','(': ReadQuery,
				')': GetRtc,'*': '','+': '',',': ModemResponse,'-': VersionInfo
			 }#start from (!)x21 to (-)x2D
	myfunc = mycase[sbmcmd]
	myfunc()
def ReadQuery():
	# data will be- \x02\x28 ''''''''''''''''''''''''''''\x03
	GlobalVaria.ServiceNo = ''
	k = 0
	i = 0
	Bufcnt = 0
	GlobalVaria.SBM_FLAG = 1
	#print 'In ReadQuery Function'
	Bufcnt = len(GlobalVaria.SBMBuffer)
	GlobalVaria.SBMBuffer = GlobalVaria.SBMBuffer[2:-1]
	##print 'In Read Query Function',GlobalVaria.SBMBuffer
	GlobalVaria.ServiceNo = GlobalVaria.ServiceNo + GlobalVaria.SBMBuffer
	print 'ServiceNo',GlobalVaria.ServiceNo
	GlobalVaria.getReq = 1


def SBMmetReading():
	GlobalVaria.UartData = ""
	i = 0
	UartDataIn = 0
	GlobalVaria.SBM_FLAG=0
	SBMTrial = 0
	Bufcnt = 0
	##print '\n-------SBM Reading entry ------\n'
	GlobalVaria.SBMBuffer = ""
	UartData = ""
	GlobalVaria.UartData = SER.read()
	#print'\n------Reading Uart Data------\n',GlobalVaria.UartData
	while(SBMTrial < 3):
		##print '\n In SBM Mode \n',SBMTrial
		#MOD.sleep(5)
		if( len(GlobalVaria.UartData) != 0):
			##print'\n------Reading Uart Data------\n'
			GlobalVaria.UartData = GlobalVaria.UartData + SER.read()
		SBMTrial = SBMTrial + 1
	##print 'GlobalVaria.UartData',GlobalVaria.UartData
	if(len(GlobalVaria.UartData) != 0):
		##print '\n----Uart Data Received--------\n'
		##print 'len(UartData)-',len(GlobalVaria.UartData)
		if((GlobalVaria.UartData[0] == STX['0']) and (GlobalVaria.UartData[-1] == STX['1'])):
			##print 'uartdata matched \n',GlobalVaria.UartData
			index = 0
			GlobalVaria.SBMBuffer = GlobalVaria.SBMBuffer + GlobalVaria.UartData
			##print ' -------SBMBuffer------- \n',GlobalVaria.SBMBuffer
			UartDataIn = 1
			if((GlobalVaria.SBMBuffer[1] == '\x22') and (GlobalVaria.InFileLenExceededflag == '0')):
				SER.send("%s" %VALID['0'])
				#print '-------------- ACK SENT --------------- '
		else:
			#print '------  Data Mismatched --------'
			UartDataIn = 0
			SER.send("%s" %INVALID['0'])
		if(UartDataIn == 1):
			print 'Data matched .......Bufcount ',GlobalVaria.SBMBuffer
			if((GlobalVaria.SBMBuffer[1] == '\x21')or(GlobalVaria.SBMBuffer[1] == '\x22') or(GlobalVaria.SBMBuffer[1] == '\x23') or(GlobalVaria.SBMBuffer[1] == '\x24') or (GlobalVaria.SBMBuffer[1] == '\x25') or (GlobalVaria.SBMBuffer[1] == '\x28') or (GlobalVaria.SBMBuffer[1] == '\x29') or (GlobalVaria.SBMBuffer[1] == '\x2D') or (GlobalVaria.SBMBuffer[1] == '\x2C')):
				FindSbmCmnd(GlobalVaria.SBMBuffer[1])
		Bufcnt = 0
		UartDataIn = 0
		GlobalVaria.SBMBuffer = ""
		GlobalVaria.UartData = 0
	if((UartDataIn == 0) and (GlobalVaria.uploadSBMData == 0)):
		GlobalVaria.sbmInFileLength1 = FileSize(GlobalVaria.SBM_DATA_INFILE1)
		GlobalVaria.sbmInFileLength2 = FileSize(GlobalVaria.SBM_DATA_INFILE2)
		##print 'GlobalVaria.SBM_DATA_INFILE1  size is \n',GlobalVaria.sbmInFileLength1
		if(((GlobalVaria.sbmInFileLength1 > 0) or(GlobalVaria.sbmInFileLength2 > 0)) and (OutfileHandler == -1)):
			WriteDataOutFile()
			#return 1 this is commented becz when outfile is exced and infile has some data then data wont be upload to server when reboot modem
		else:
			GlobalVaria.InFileLenExceededflag = '0';
		#elif(FileCheck(GlobalVaria.SBM_DATA_OUTFILE)== 1):
		#	#print 'GlobalVaria.SBM_DATA_OUTFILE  exist \n'
		GlobalVaria.sbmOutFileLength = FileSize(GlobalVaria.SBM_DATA_OUTFILE)
		##print 'GlobalVaria.SBM_DATA_OUTFILE  size is \n',GlobalVaria.sbmOutFileLength
		if(GlobalVaria.sbmOutFileLength > 0):
			GlobalVaria.DataAvailable2Upload = 1
		else:
			GlobalVaria.OutFileLenExceededflag = '0';
		#print 'len(GlobalVaria.ServiceNo)-[%d],GlobalVaria.ServiceNo-[%s]'%(len(GlobalVaria.ServiceNo),GlobalVaria.ServiceNo)
		if(len(GlobalVaria.ServiceNo)>6):
			GlobalVaria.getReq = 1
		return 1
		#return 1
	##print ' Enter Command While Modem is in SBM Mode \n'
