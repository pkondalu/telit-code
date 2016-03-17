# #######           NARESH-(11022015)            ######## #
import GlobalVaria
from SBMReading import *
import MOD
import SER
import MDM
import sys
global 	TIMEOUT_ATTESA
global SignStre
TIMEOUT_ATTESA  = 40
SignStre = 0

def PrintDebug(message):
	SER.send("\n"+message+'\n')

def ExecuteATCommand(command, exceptedResponse, modemSleep, timeout, trailCount):
	trialIndex = 0
	response = ''
	msg = ''
	while (response.find(exceptedResponse)==-1):
		MDM.send(command,timeout)
		MOD.sleep(modemSleep)
		response = WaitForModemResponse(timeout)
		GlobalVaria.gAtResponse = response
		if(trialIndex > trailCount):
			msg = "Command : " + command + "Response:" + response  +" - FAILED"
			msg = msg.replace('\r','')
			msg = msg.replace('\n','')
			PrintDebug(msg)
			return 0	
		trialIndex = trialIndex + 1
	#PrintDebug("Command : " + command  + "- SUCCESS")
	return 1

def UrlSpliter(Type):
	PortNum = ''
	serviceAdd = ''
	url1 = ''
	TelitUrl = ''
	tempbuff = ''
	slash =0
	Colon = 0
	tempbuff = GlobalVaria.Info['HttpUrl'].strip()#Just like Trimstring http://cpdclcollservice.atil.info/service.asmx/
	#print 'tempbuff',tempbuff
	slash = tempbuff.find("/")#cpdclcollservice.atil.info/service.asmx/
	url1 = url1 + tempbuff[slash+2:]#cpdclcollservice.atil.info/service.asmx/
	#print 'url1',url1
	slash = 0
	slash = url1.find("/")#cpdclcollservice.atil.info/
	TelitUrl = TelitUrl + url1[:slash]
	#print 'TelitUrl',TelitUrl
	if(Type == 1):
		Colon = TelitUrl.find(":")
		if(Colon !=  -1):
			PortNum = TelitUrl[Colon+1:]
			#print '\nPort number with colon is',TelitUrl
			return PortNum
		else:
			#print '\nPort number is without colon 80\n'
			return '80'
	elif(Type == 2):
		#print '\nService in post method to be sent is \n'
		tempbuff = ''
		url1 = ''
		tempbuff = GlobalVaria.Info['HttpUrl'].strip()#
			#print 'tempbuff',tempbuff
		slash = tempbuff.find("/")
		url1 = url1 + tempbuff[slash+2:]#cpdclcollservice.atil.info/service.asmx/
		#print 'url1',url1
		slash = 0
		slash = url1.find("/")
		serviceAdd = url1[slash:]#service.asmx/
		#print '\serviceAdd \n',serviceAdd
		return serviceAdd
	elif(Type == 3):
		#print '\n TelitUrl \n',TelitUrl
		Colon = TelitUrl.find(":")
		if(Colon ==  -1):
			#print '\n TelitUrl Type 3 without colon is\n',TelitUrl
			return TelitUrl
		else:
			TelitUrl = TelitUrl[:Colon]
			#print '\n TelitUrl Type 3 with colon is\n',TelitUrl
			return TelitUrl
			
def HttpGet(resource):
	res = ''
	MdmRes = ''
	httpGetCommand = "%s%s,%s,0\r" % ('AT#HTTPQRY=1,0,', httpUrl, str(len(httpData)))
	PrintDebug(resource)
	res = MDM.send(resource, 5)
	MOD.sleep(5)
	MdmRes = Wait4Data()

def ParseRTC(res):
	PrintDebug("ParseRTC")
	cclkfound = 0
	GlobalVaria.SBM_RTC_BUFFER = ''
	Time1 = ''
	date =''
	date1 = ''
	hour1 = ''
	day = ''
	month = ''
	year = ''
	year1 = ''
	Time = ''
	#print 'before res',res
	cclkfound = res.find('+CCLK')
	res = res[cclkfound+1 : ]
	#print 'after res',res
	date = date + res[7:15]
	#print 'date',date
	for index in date:
		if(index == '/'):
			index = ''
		date1 = date1 + index
	#print 'date1',date1
	day = date1[4:]
	#print 'day',day
	day = "%02d" % int(day)
	#print 'day',day
	month = date1[2:4]
	month ="%02d" % int(month)
	#print 'month',month
	year1 = date1[0:2]
	#year1 = "%02d" % int(year)
	#year = ''
	year = "20%02d" % int(year1)
	#print 'year',year
	Time1 = res[16:24]
	for index in Time1:
		if(index == ':'):
			index = ''
		Time = Time + index
	GlobalVaria.SBM_RTC_BUFFER = day+month+year+'&'+Time+''
	GlobalVaria.DateTime['day'] = day
	#print 'DateTime[day]',DateTime['day']
	GlobalVaria.DateTime['month'] = month
	#print 'DateTime[month] \n',DateTime['month']
	GlobalVaria.DateTime['year'] = year
	#print 'DateTime[year] \n',DateTime['year']
	GlobalVaria.DateTime['hour'] = Time[0:2]
	#print 'DateTime[hour] \n',DateTime['hour']
	GlobalVaria.DateTime['min'] = Time[2:4]
	#print 'DateTime[min] \n',DateTime['min']
	GlobalVaria.DateTime['sec'] = Time[4:6]
	
def isdigitof(Splitstr):
	Numbers = "0123456789"
	copysig = ""
	for index in Splitstr:
		if(Numbers.find(index) != -1):
			if((index.find('0x20') != -1)):
				continue
			copysig = copysig + index
	#print 'copysig',copysig
	return copysig

def GetSignalStrength():
	signal = ''
	value = ''
	SignStre = '00'
	#PrintDebug('In Signal Strength')
	MDM.receive(1)
	MDM.receive(1)
	MDM.receive(1)
	signal = MDM.send('AT+CSQ\r', 3)
	signal = WaitForModemResponse(120)
	print 'signal',signal
	IdUpdCsq = signal.find('Q: ')
	if (IdUpdCsq == -1 ):
		#print 'no find CSQ'
		SignStre = '%.02s' %(SignStre)
		GlobalVaria.SignalStrength = '%02s' %(SignStre)
		return GlobalVaria.SignalStrength
	CSQfind = signal.find(',')
	if(CSQfind == -1):
		#print 'no find Cama'
		SignStre = '%.02s' %(SignStre)
		GlobalVaria.SignalStrength = '%02s' %(SignStre)
		return GlobalVaria.SignalStrength
	SignStre = signal[IdUpdCsq+3 : CSQfind]
	GlobalVaria.SignalStrength = '%02d' %int(SignStre)
	GlobalVaria.SignalStrength = '%02s'%(GlobalVaria.SignalStrength)
	PrintDebug('SignalStrength: ' + str(GlobalVaria.SignalStrength))
	return GlobalVaria.SignalStrength

def Wait4Data():
	data = ''
	#print '\n-------------Mdm command--------------'
	timeout = MOD.secCounter() + TIMEOUT_ATTESA
	while((len(data) == 0) and (MOD.secCounter() < timeout)):
		#SBMmetReading()
		data = MDM.receive(15)
	#print 'data in Wait4Data ',data
	return data
	
def WaitForModemResponse(timeoutInSec):
	data = ''
	timeout = MOD.secCounter() + TIMEOUT_ATTESA
	while((len(data) == 0) and (MOD.secCounter() < timeout)):
		data = MDM.receive(timeoutInSec)
	return data
	
def Http_Cfg():
	PrintDebug("In Http Configuration")
	PORT = ''
	TrailCount = 0
	ConnTrailcnt = 0
	GlobalVaria.HTML_ADDR = UrlSpliter(3)
	PORT = UrlSpliter(1)
	command = 'AT#HTTPCFG=1,"' + GlobalVaria.HTML_ADDR + '",' + PORT + ',0,,,0,120\r'
	result = ExecuteATCommand(command,"OK",1,120,3)
	Http_Cfg_Flag = 0
	if(result == 1):
		Http_Cfg_Flag = 1
	return result;
		
def SetGprsInitilization():
	PrintDebug("SetGprsInitilization")
	trialCount = 0
	response = ''
	command = 'AT+CGDCONT=1,"IP","' + GlobalVaria.APN.strip() + '"\r' 
	result = ExecuteATCommand(command,"OK",1,120,1)
	GlobalVaria.Gprs_Flag = 0
	if(result == 1):
		GlobalVaria.Gprs_Flag = 1
	command = 'AT#SGACT=1,0\r' 					  # GRPS Context Activation
	result = ExecuteATCommand(command,"OK",1,120,1)
	GlobalVaria.Gprs_Flag = 0
	if(result == 1):
		GlobalVaria.Gprs_Flag = 1
	MOD.sleep(10)
	command = 'AT#SGACT=1,1\r' 					  # GRPS Context Activation
	result = ExecuteATCommand(command,"#SGACT",20,120,3)
	GlobalVaria.Gprs_Flag = 0
	if(result == 1 or GlobalVaria.gAtResponse.find('context already activated') != -1):
		GlobalVaria.Gprs_Flag = 1
		#PrintDebug(GlobalVaria.gAtResponse)
	if(GlobalVaria.Gprs_Flag == 1):
		Http_Cfg()
	else:
		return 0
	return 1

def GetHttpResponse(httpRingMessage):
	PROFILE_ID = 0
	STATUS_CODE = 1
	CONTENT_TYPE = 2
	CONTENT_LENGTH = 3
	response = httpRingMessage
	response = response.replace('#HTTPRING:','')
	resposeCodes = response.split(',')
	PrintDebug('PROFILE_ID Code: '+ resposeCodes[PROFILE_ID])
	PrintDebug('STATUS_CODE Code: '+ resposeCodes[STATUS_CODE])
	PrintDebug('CONTENT_TYPE Code: '+ resposeCodes[CONTENT_TYPE])
	PrintDebug('CONTENT_LENGTH Code: '+ resposeCodes[CONTENT_LENGTH])
	if(len(resposeCodes) == 4):
		# if(resposeCodes[STATUS_CODE].find("200") == -1):
			# PrintDebug('Response Code: '+ resposeCodes[STATUS_CODE])
			# return "Error - No Success Code in HTTPRING"
		# contentLength = resposeCodes[CONTENT_LENGTH].strip()
		# if(isnumeric(contentLength) == False or contentLength == "0"):
			# PrintDebug('Content - Length:'+resposeCodes[CONTENT_LENGTH])
			# return "Error - Zero Content Length in HTTPRING"
		command = "AT#HTTPRCV="+resposeCodes[PROFILE_ID].strip() + '\r'
		result = ExecuteATCommand(command,"<<<",50,120,1)
		if(result == 1):
			response = GlobalVaria.gAtResponse
			response = response.replace('<<<','')
			response = response.replace('\r','')
			response = response.replace('\n','')
			return response;
		else:
			return 'Error - Error in HTTPRCV '
	else:
		return "Error - in HTTPRING"
		
def verifyREG():
	PrintDebug("Verify Registration")
	REG = 0
	MDM.receive(1)
	res = MDM.send('AT+COPS?\r', 3)
	res = WaitForModemResponse(10)
	result = ExecuteATCommand('AT+CREG?\r','+CREG:',1,120,3)
	res = GlobalVaria.gAtResponse
	if (res.find('+CREG: 0,0')!=-1) or (res.find('+CREG: 1,0')!=-1)or (res.find('+CREG: 2,0')!=-1):
		# not registred
		#print 'not REGISTRED'
		GlobalVaria.Gprs_Flag = 0
		GlobalVaria.HttpCon = 0
		res = ''
		REG = 0
	if (res.find('+CREG: 0,1')!=-1) or (res.find('+CREG: 1,1')!=-1)or (res.find('+CREG: 2,1')!=-1):
		# registred HOME
		#print 'Registred HOME'
		REG = 1
	if (res.find('+CREG: 0,2')!=-1) or (res.find('+CREG: 1,2')!=-1)or (res.find('+CREG: 2,2')!=-1):
		# SEARCHING
		#print 'SERCHING NETWORK'
		GlobalVaria.Gprs_Flag = 0
		GlobalVaria.HttpCon = 0
		res = ''
		REG = 0
	if (res.find('+CREG: 0,3')!=-1) or (res.find('+CREG: 1,3')!=-1)or (res.find('+CREG: 2,3')!=-1):
		# registred DENIED
		#print 'registred DENIED'
		GlobalVaria.Gprs_Flag = 0
		GlobalVaria.HttpCon = 0
		res = ''
		REG = 0
	if (res.find('+CREG: 0,5')!=-1) or (res.find('+CREG: 1,5')!=-1)or (res.find('+CREG: 2,5')!=-1):
		# registred ROAMING
		#print 'registred ROAMING'
		REG = 1
	return res			

def ReadRTC():
	PrintDebug("Read RTC")
	MDM.receive(1)
	PrintDebug('Reading RTC \n')
	DT = MDM.send('AT+CCLK?\r', 3)
	DT = WaitForModemResponse(120)
	if(DT.find('+CCLK') != -1):
		ParseRTC(DT)
	PrintDebug("Reading rtc completed\n")
	
def ModemSetup():
	PrintDebug("Modem Setup")
	First = 1
	count = 0
	TrailCnt = 0
	MdmCmd = ''
	MdmRes = ''
	GlobalVaria.simavailable = 0
	GlobalVaria.Gprs_Flag = 0
	GlobalVaria.HttpCon = 0
	GlobalVaria.simavailable = 0
	result = ExecuteATCommand('AT+CPIN?\r','+CPIN',1,120,3)
	if(result == 1):
		GlobalVaria.simavailable = 1
	else:
		PrintDebug("Error- AT+CPIN? ")
		return 0
	MdmRes = ''
	TrailCnt = 0
	#PrintDebug("Before Verify")
	while (MdmRes.find('OK')==-1) :
		MdmRes = verifyREG()
		if(TrailCnt > 3):
			GlobalVaria.Gprs_Flag = 0
			GlobalVaria.HttpCon = 0
			return 0
		TrailCnt = TrailCnt + 1
		TrailCnt = 0
	MdmRes = ''
	while (MdmRes.find('OK')==-1):
		result = ExecuteATCommand('AT#CCID\r','#CCID',1,120,3)
		MdmRes = GlobalVaria.gAtResponse
		#PrintDebug(MdmRes)
		if(TrailCnt > 3):
			return 0
		TrailCnt = TrailCnt + 1
		GlobalVaria.CIMINumber = ' ' #CCID: 89917310657203858031<CR><LF>OK
		count = MdmRes.find('D:')
		if (count == -1 ):
			PrintDebug('not found #CCID')
			GlobalVaria.CIMINumber = ' '
		else:
			MdmRes = MdmRes.replace("#CCID:",'').strip()
			endIndex = MdmRes.find('\r')
			if(endIndex > 0):
				GlobalVaria.CIMINumber = MdmRes[0:endIndex]
		PrintDebug('GlobalVaria.CIMINumber - [' + GlobalVaria.CIMINumber + ']')
		return 1			
	return 1

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

def GetFileSize(filename):	
	PrintDebug("Get File Size")
	fileSize = 0
	chunk = ''
	file1 = -1
	if(FileCheck(filename) == 1):
		try:
			file1 = open(filename, "r")
		except IOError:
			return -1
		file1.seek(0,0)
		while(1):
			chunk = file1.read(100)
			if(chunk != ''):
				fileSize = fileSize + len(chunk)
			else:
				break
		file1.close()
		PrintDebug("Total Length Size:"+ str(fileSize))
		return fileSize
	else:
		PrintDebug("File Not found :" + filename)
		return -1

def FileCheck(filename):
	CheckHandler = -1
	try:
		CheckHandler = open(filename,'r')
	except IOError:
		return -1
	CheckHandler.close()
	return 1

def PostData(postUrl, recordData):
	PrintDebug("Get Data From Server received!!!")
	httpData = recordData
	methodName = ""
	GlobalVaria.Info['HttpUrl'] = postUrl
	#GlobalVaria.Info['HttpUrl']  = "http://apepdclatmsbm.ctms.info/SBMDOWNLOAD.asmx/ReadRecord"
	PrintDebug(GlobalVaria.Info['HttpUrl'])
	if(SetGprsInitilization() != 1):
		PrintDebug("GprsInitialization Failed")
		return 0
	if(Http_Cfg() != 1):
		PrintDebug("Failed")
		return 0
	PrintDebug(GlobalVaria.Info['HttpUrl'])
	httpUrl = '"' + UrlSpliter(2) + '"'
	PrintDebug(httpUrl)
	GlobalVaria.COLL_DATA_LINK = "%s%s,%s,0\r" % ('AT#HTTPSND=1,0,', httpUrl, str(len(httpData)))
	PrintDebug(GlobalVaria.COLL_DATA_LINK)
	result = ExecuteATCommand(GlobalVaria.COLL_DATA_LINK,">>>",20,120,3)
	if(result == 1):
		PrintDebug("Connected!!!")
		recordData = recordData+'\r\n'
		PrintDebug(recordData)
		result = ExecuteATCommand(recordData,"OK",5,120,1)
		PrintDebug(GlobalVaria.gAtResponse)
		if(result == 1):
			PrintDebug("Data Sent and Waiting for Http Status")
			MOD.sleep(50)
			MdmRes = WaitForModemResponse(120)
			PrintDebug(MdmRes)
			gHttpRespone = GetHttpResponse(MdmRes)
			if(gHttpRespone.find("Error") == -1):
				PrintDebug("Success in receiving data")
				PrintDebug(gHttpRespone)
				return 1
			else:
				PrintDebug("Error in receiving the data")
				return 0
		else:
			PrintDebug("Error in sending the data")
			return 0
	else:
		PrintDebug("Not Connected!!!")
		return 0