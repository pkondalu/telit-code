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
		
def ParseRTC(res):
	global SBM_RTC_BUFFER
	cclkfound = 0
	SBM_RTC_BUFFER = ''
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
	SBM_RTC_BUFFER = day+month+year+'&'+Time+''
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
	#print 'DateTime[sec] \n',DateTime['sec']


# ########################################################### #
# #####          Function for Getting RTC Date          ########
# ########################################################### #
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
	print 'In Signal Strength'
	MDM.receive(1)
	MDM.receive(1)
	MDM.receive(1)
	signal = MDM.send('AT+CSQ\r', 3)
	##MOD.sleep(5)
	signal = Wait4Data()
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
	print 'SignalStrength--',GlobalVaria.SignalStrength
	return GlobalVaria.SignalStrength
def prepareConnectionPacket(uploadFileSize):
	index = 0
	sizestring = ""
	#print 'In prepareConnectionPacket'
	sizestring = "%06d"%(uploadFileSize)
	ConnectionPacket = "UNITID:SBMM1012345" + sizestring
	try:
		fo = open('CNCTPKT.REC','w')
	except IOError:
		#print 'prepareconection packet failed'
		return 0
	fo.write(ConnectionPacket)
	fo.close()
	#print 'ConnectionPacket',ConnectionPacket

def modemInitialization():
	#print '\n In modem initialisation \n'
	First = 1
	count = 0
	TrailCnt = 0
	MdmCmd = ''
	MdmRes = ''
	while(First == 1):
		SBMmetReading()
		##print '\n DEBUG_INFO : AT command Sending\n'		#                       DEBUG_INFO : AT
		MdmRes = ''
		SBMmetReading()
		#a = SER.send(MdmRes)		# debug info
		TrailCnt = 0
		MdmCmd = ''
		MdmRes = ''
		#print '\rDEBUG_INFO : AT+CPIN command Sending - \r',TrailCnt		#         DEBUG_INFO : AT+CPIN
		MDM.receive(1)
		while (MdmRes.find('+CPIN')==-1) :
			MDM.send('AT+CPIN?\r', 2)
			MdmRes = Wait4Data()
			#print '\n AT+CPIN? - \n',MdmRes
			if(TrailCnt > 3):
				GlobalVaria.simavailable = 0
				GlobalVaria.Gprs_Flag = 0
				GlobalVaria.HttpCon = 0
				return 0
			##MOD.sleep(5)
			TrailCnt = TrailCnt + 1
		GlobalVaria.simavailable = 1
		#a = SER.send(MdmRes)		# debug info
		TrailCnt = 0
		MdmCmd = ''
		MdmRes = ''
		#print '\rDEBUG_INFO : AT+CREG command Sending - \r',TrailCnt		#       DEBUG_INFO : AT+CREG
		MDM.receive(1)
		while (MdmRes.find('OK')==-1) :
			MdmRes = verifyREG()
			#print '\n AT+CREG? - \n',MdmRes
			if(TrailCnt > 3):
				#print 'Registration Failed'
				GlobalVaria.Gprs_Flag = 0
				GlobalVaria.HttpCon = 0
				return 0
			##MOD.sleep(5)
			TrailCnt = TrailCnt + 1
		#a = SER.send(MdmRes)		# debug info
		#print 'Registration Success'
		TrailCnt = 0
		MdmCmd = ''
		MdmRes = ''
		#print '\rDEBUG_INFO : "AT#CCID" command Sending\r'		#                DEBUG_INFO : "CCID"
		MDM.receive(1)
		while (MdmRes.find('OK')==-1) :
			MdmCmd = MDM.send('"AT#CCID\r', 2)     # AT context
			MdmRes = Wait4Data()
			#print '\n SIM CIMI NUM AT#CCID - \n',MdmRes
			print ']SIM CIMI NUM Len - \n',len(MdmRes)
			if(TrailCnt > 3):
				return 0
			##MOD.sleep(5)
			TrailCnt = TrailCnt + 1
		##MOD.sleep(5)
		GlobalVaria.CIMINumber = ''#CCID: 89917310657203858031<CR><LF>OK
		count = MdmRes.find('D:')
		if (count == -1 ):
			#print 'not found #CCID'
			GlobalVaria.CIMINumber = ''
		#GlobalVaria.CIMINumber = MdmRes[count+2:count+23]
		GlobalVaria.CIMINumber = MdmRes[count+2:count + len(MdmRes) - 14]
		print '\n GlobalVaria.CIMINumber -[',GlobalVaria.CIMINumber
		print ']GlobalVaria.CIMINumber - \n',GlobalVaria.CIMINumber
		return 1

def ReadRTC():
	MDM.receive(1)
	print '\n reading rtc \n'
	DT = MDM.send('AT+CCLK?\r', 3)
	DT = Wait4Data()
	#print 'Date & Time',DT
	if(DT.find('+CCLK') != -1):
		ParseRTC(DT)
	print '\n reading rtc completed\n'
def Wait4Data():
	data = ''
	#print '\n-------------Mdm command--------------'
	timeout = MOD.secCounter() + TIMEOUT_ATTESA
	while((len(data) == 0) and (MOD.secCounter() < timeout)):
		SBMmetReading()
		data = MDM.receive(15)
	#print 'data in Wait4Data ',data
	return data

# ########################################################### #
# ########    Function for Checking GPRS Connction    ####### #
# ########################################################### #
		
def checkGPRSConnection():
	PdpTraicnt = 0
	APN = ''
	s=''
	SBMmetReading()
	APN = GlobalVaria.Info['ApnServer'].strip()
	#print 'NEW APN IS',APN
	MDM.receive(1)
	while (s.find('OK')==-1) :
		a = MDM.send('AT+CGDCONT=1,"IP","',0)
		a = MDM.send(APN,0)			# insert APN of the operator in use (e.g.TIM)  'IBOX.TIM.IT'
		a = MDM.send('"\r',0)
		s = Wait4Data()
		#print 'In CGDCONT'
		if(PdpTraicnt > 3):
			GlobalVaria.Gprs_Flag = 0
			return 0	
		##MOD.sleep(10)
		PdpTraicnt = PdpTraicnt + 1
	##MOD.sleep(10)
	#print 'Passed CGDCONT'
	s=''
	GprsTraicnt = 0
	while (s.find('OK')==-1) :
		#a = SER.send('\rDEBUG_INFO : GPRS Deactivation\r')# debug info
		a = MDM.send('AT#SGACT=1,0\r', 3)     # GPRS context activation
		##MOD.sleep(10)
		s = Wait4Data()
		#a = SER.send(s)		# debug info
		##MOD.sleep(10)
		if(GprsTraicnt > 5):
			GlobalVaria.Gprs_Flag = 0
			return 0
		##MOD.sleep(10)
		GprsTraicnt = GprsTraicnt + 1
	#print 'GPRS DEACTIVATED'
	s=''
	GprsTraicnt = 0
	while (s.find('#SGACT')==-1) :
		#a = SER.send('\rDEBUG_INFO : GPRS context\r')# debug info
		a = MDM.send('AT#SGACT=1,1\r', 5)     # GPRS context activation
		##MOD.sleep(20)
		s = Wait4Data()
		#a = SER.send(s)		# debug info
		if(GprsTraicnt > 5):
			GlobalVaria.Gprs_Flag = 0
			return 0	
		##MOD.sleep(10)
		GprsTraicnt = GprsTraicnt + 1
	print 'GPRS OK'
	return 1

# ########################################################### #
# #####   Function for Verifying Registration       ##########
# ########################################################### #

def verifyREG():
	REG = 0
	MDM.receive(1)
	res = MDM.send('AT+COPS?\r', 3)
	res = Wait4Data()
	#print res
	res = MDM.send('AT+CREG?\r', 3)
	res = Wait4Data()
	#print res
	SBMmetReading()
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
