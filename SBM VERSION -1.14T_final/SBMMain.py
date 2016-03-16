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
global 	APN
global SmsFlag
global 	BILL_HTTP_LINK
GlobalVaria.HTML_ADDR = ''
SmsFlag = '0'
FILE_CREATE 	= '0'
FILE_APPEND 	= '1'
FILE_END 		= '2'
FILE_ONE_RECORD = '3'
APN				=  "airtelgprs.com                "
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
# #######################################
# ######### files initialisation #
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
 ########################################################### #
# ###################  uploadTextDataFiles   ################ #
# ########################################################### #

def Htpp_Send():

	res = ''
	MdmRes = ''
	PrintDebug("In http Send function")
	res = MDM.send(GlobalVaria.COLL_DATA_LINK, 5)
	MOD.sleep(5)
	MdmRes = Wait4Data()
	PrintDebug(MdmRes)
	if(MdmRes.find('>>>') != -1):
		PrintDebug('server conection success'+MdmRes)
		return 1
	else:
		PrintDebug('Server sending failed'+MdmRes)
		return 0
def ConnectToServer():
	TrilCnt = 0
	#print '\n In connecting to server \n'
	PrintDebug("Connect to Server")
	while(1):
		if(Htpp_Send() == 1):
			PrintDebug('\n connecting to server Success \n')
			GlobalVaria.HttpCon = 1
			return 1
		else:
			TrilCnt = TrilCnt + 1
			if(checkGPRSConnection() == 1):
				GlobalVaria.Gprs_Flag = 1 #ravi
				PrintDebug('GPRS connection success')
				if(TrilCnt > 2):
					#print ' \n TrilCnt exceeded so conection to server failure\n'
					return 0
			else:
				PrintDebug('GPRS Connection Failed\n')
				GlobalVaria.Gprs_Flag = 0
				return 0

def uploadDataFiles():
	GlobalVaria.Servertrial = 0
	GlobalVaria.loop1val = 0;
	GlobalVaria.loop2val = 0;	
	GlobalVaria.recno = 0;
	GlobalVaria.LastRecord = '0';
	Hour = ""
	i = 0
	print '\n In processing uploadTextDataFiles \n'
	ReadRTC()
	RandValue= ""
	Hour = Hour + GlobalVaria.DateTime['hour']
	RandValue = RandValue + Hour[1:]+ GlobalVaria.DateTime['min'] + GlobalVaria.DateTime['sec']
	#print 'RandValue-%s,GlobalVaria.CIMINumber-%s' %(RandValue,GlobalVaria.CIMINumber)
	GlobalVaria.ServerFileName = "C_" + GlobalVaria.DateTime['year'] + GlobalVaria.DateTime['month'] + GlobalVaria.DateTime['day'] + GlobalVaria.DateTime['hour'] + GlobalVaria.DateTime['min'] + GlobalVaria.DateTime['sec'] + RandValue + GlobalVaria.CIMINumber[15:]+".txt"
	print 'Server file name:%s',GlobalVaria.ServerFileName
	Type = '1'
	GlobalVaria.HTML_SERVICE = UrlSpliter(2)
	while(1):
		#print '\n In uploadDataFiles to server \n',GlobalVaria.Info['HttpUrl']
		if(UploadFiles2Server() == 1):
			print 'UploadFiles2Server to success'
			return 1
		else:
			GlobalVaria.HttpCon = 0
			GlobalVaria.Servertrial = GlobalVaria.Servertrial + 1
			if(GlobalVaria.Servertrial  > 3):
				return 0
def Digit_cnt(myNumber):
	num_digits=0;
	if(myNumber == 0):
		num_digits = 1
	while(myNumber > 0):
		num_digits = num_digits + 1
		myNumber = myNumber/10
	return num_digits;
def UploadFiles2Server():
	Sbm_Out_Length = 0
	Sbm_Out_Length = FileSize(GlobalVaria.SBM_DATA_OUTFILE)
	if(Sbm_Out_Length == 0):
		#print 'Encryption is failed \n'
		return 0
	#print '\n In Sbm_Out_Length -',Sbm_Out_Length
	if(Sbm_Out_Length < 0):
		return 1
	GlobalVaria.loop1val = Sbm_Out_Length/GlobalVaria.DATA_LEN;
	GlobalVaria.loop2val = Sbm_Out_Length%GlobalVaria.DATA_LEN;
	GlobalVaria.TotRec2Upload  = GlobalVaria.loop1val;
	if(GlobalVaria.loop2val != 0 ):
		GlobalVaria.TotRec2Upload = GlobalVaria.TotRec2Upload + 1;
	GlobalVaria.recno = GlobalVaria.TxtUpldRecNo;
	if(GlobalVaria.recno == 0):
		GlobalVaria.rawseek = 0;
		initializeseekFile();
	#print '\n loop1val ',GlobalVaria.loop1val
	#print '\n loop2val ',GlobalVaria.loop2val
	print 'TotRec2Upload = %d\n',GlobalVaria.TotRec2Upload
	print 'recno = ',GlobalVaria.recno
	while(1):
		if(GlobalVaria.recno == 0):
			GlobalVaria.send_connection_packet = 1;
			prepareConnectionPacket(Sbm_Out_Length)
			try:
				fo = open("CNCTPKT.REC", "r")
			except IOError:
				GlobalVaria.HttpCon = 0
				return 0
			Data = fo.read(GlobalVaria.DATA_LEN)
			fo.close()
			#print 'TXT-DATA',Data
			if(len(Data) != 0):
				dataCoded = MOD.encBase64(Data)
			##print 'dataCoded',dataCoded
			if(len(dataCoded) != 0):
				GlobalVaria.DataServer = dataCoded.replace('\r\n',"")
			else:
				GlobalVaria.HttpCon = 0
				return '0000'
			##MOD.sleep(10)
			GlobalVaria.recno = 0;
			GlobalVaria.recno_sz = Digit_cnt(GlobalVaria.recno);
			#print 'recno_sz',GlobalVaria.recno_sz
			GlobalVaria.data_length = len(GlobalVaria.DataServer)
			#print 'data_length ',GlobalVaria.data_length 
			GlobalVaria.data_length_sz = Digit_cnt(GlobalVaria.data_length)
			#print 'data_length_sz',GlobalVaria.data_length_sz
			GlobalVaria.FileMode = FILE_CREATE
			if(Upload_File() != 1):
				return 0
			GlobalVaria.recno = GlobalVaria.recno + 1
			GlobalVaria.TxtUpldRecNo = GlobalVaria.recno
			#print 'TxtUpldRecNo',GlobalVaria.TxtUpldRecNo
			Receivedbuff = ''
		else:
			print 'AFTER CONCETION PKT SENDING DATA RECORDS \n'
			while(GlobalVaria.LastRecord == '0' ):
				#print '\n in uploading pkts recno =[%d],FileMode =[%c]'%(GlobalVaria.recno,GlobalVaria.FileMode)
				if(Upload_File() != 1):
					return 0
				GlobalVaria.recno = GlobalVaria.recno + 1
				GlobalVaria.TxtUpldRecNo = GlobalVaria.recno;
			GlobalVaria.TxtUpldRecNo =0;
			#Socret = SocketClose()
			#SocDwn = SocketDown()
			#GprsClose()
			return 1
# ########################################################### #
# ########      Function for Connecting to Server     ####### #
# ########################################################### #
def Upload_File():
	USize = 0;
	loopCnt = 0
	seekptrfile = ''
	Datafile = ''
	print '\n in Upload_File function \n'
	if(GlobalVaria.send_connection_packet == 0):
		try:
			SeekFileptr = open(GlobalVaria.SEEK_PTR, 'r')
		except IOError:
			GlobalVaria.HttpCon = 0
			return 0
		
		SeekFileptr.read(6)
		SeekFileptr.close()
		SeekFileptr= -1
		try:
			Datafile = open(GlobalVaria.SBM_DATA_OUTFILE,'r')
		except IOError:
			#print 'failed to open file in upload',GlobalVaria.SBM_DATA_OUTFILE
			GlobalVaria.HttpCon = 0
			return 0
		#print 'GlobalVaria.rawseek',GlobalVaria.rawseek
		Datafile.seek(GlobalVaria.rawseek,1)
		#print 'TotRec2Upload',GlobalVaria.TotRec2Upload
		GlobalVaria.DataServer = ''
		GlobalVaria.DataServer = Datafile.read(GlobalVaria.DATA_LEN)
		if(len(GlobalVaria.DataServer) != 0):
			dataCoded = MOD.encBase64(GlobalVaria.DataServer)
		#print 'dataCoded',dataCoded
		GlobalVaria.DataServer = ''
		if(len(dataCoded) != 0):
			GlobalVaria.DataServer = dataCoded.replace('\r\n',"")
		else:
			#print 'Failed to read Connection Packet\n'
			GlobalVaria.HttpCon = 0
			Datafile.close()
			return '0000'
		if(GlobalVaria.TotRec2Upload == 1):
			GlobalVaria.FileMode = FILE_ONE_RECORD
			GlobalVaria.data_length = len(GlobalVaria.DataServer)
		elif(GlobalVaria.recno == GlobalVaria.TotRec2Upload):
			GlobalVaria.FileMode = FILE_END;
			if(GlobalVaria.loop2val != 0):
				GlobalVaria.data_length = len(GlobalVaria.DataServer)
		else:
			GlobalVaria.FileMode = FILE_APPEND
			GlobalVaria.data_length = len(GlobalVaria.DataServer)
		GlobalVaria.data_length_sz = Digit_cnt(GlobalVaria.data_length);
		GlobalVaria.recno_sz = Digit_cnt(GlobalVaria.recno);
		USize = 39+GlobalVaria.data_length_sz + GlobalVaria.recno_sz + GlobalVaria.data_length + len(GlobalVaria.ServerFileName)
		GlobalVaria.COLL_DATA_LINK =  'AT#HTTPSND=1,0,"'+ GlobalVaria.HTML_SERVICE+ 'GetCollectionData"'+','+str(USize)+',0\r'
		print 'COLL_DATA_LINK-USize',GlobalVaria.COLL_DATA_LINK,USize
		#COLL_DATA_LINK	= 'POST '+GlobalVaria.HTML_SERVICE+'GetCollectionData HTTP/1.1\r\nHost: '+GlobalVaria.HTML_ADDR+'\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: '+str(USize)+'\r\n\r\n'
		TempBuffer = 'filename='+GlobalVaria.ServerFileName+'&' + 'type=' + GlobalVaria.FileMode + '&' +  'recno=' + str(GlobalVaria.recno) + '&' + 'length=' + str(GlobalVaria.data_length) + '&' + 'buffer='
		TrailCnt = 0
		MdmCmd = ''
		MdmRes = ''
		#print '\rDEBUG_INFO : AT+CPIN command Sending - \r',TrailCnt		#         DEBUG_INFO : AT+CPIN
		MDM.receive(10)
		if(ConnectToServer() == 1):
			#res = MDM.send(GlobalVaria.COLL_DATA_LINK, 5)
			res = MDM.send(TempBuffer+GlobalVaria.DataServer, 3)
			print ' in TempBuffer ',TempBuffer,len(GlobalVaria.DataServer)
			Receivedbuff = Wait4Data()
			print 'In Receivedbuff GlobalVaria.DataServer',Receivedbuff
			Receivedbuff = Wait4Data()
			print 'In Receivedbuff GlobalVaria.DataServer',Receivedbuff
			if(Receivedbuff.find('#HTTPRING') != -1):
				MOD.sleep(5)
				MDM.send('AT#HTTPRCV=1\r', 2)
			else:
				print 'httpring not found '
				return 0
		else:
			print 'Connect to server fail'
			return 0
			#print '%s%s'%(COLL_DATA_LINK,TempBuffer)
			#print 'DataServer-,len(DataServer)',GlobalVaria.DataServer,len(GlobalVaria.DataServer)
	else:
		USize = 39+GlobalVaria.data_length_sz + GlobalVaria.recno_sz + GlobalVaria.data_length + len(GlobalVaria.ServerFileName)
		GlobalVaria.COLL_DATA_LINK =  'AT#HTTPSND=1,0,"'+ GlobalVaria.HTML_SERVICE+ 'GetCollectionData"'+','+str(USize)+',0\r'
		print 'COLL_DATA_LINK-USize',GlobalVaria.COLL_DATA_LINK,USize
		#COLL_DATA_LINK	= 'POST '+GlobalVaria.HTML_SERVICE+'GetCollectionData HTTP/1.1\r\nHost: '+GlobalVaria.HTML_ADDR+'\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: '+str(USize)+'\r\n\r\n'
		TempBuffer = 'filename='+GlobalVaria.ServerFileName+'&' + 'type=' + str(GlobalVaria.FileMode) + '&' +  'recno=' + str(GlobalVaria.recno) + '&' + 'length=' + str(GlobalVaria.data_length) + '&' + 'buffer='
		TrailCnt = 0
		MdmCmd = ''
		MdmRes = ''
		#print '\rDEBUG_INFO : AT+CPIN command Sending - \r',TrailCnt		#         DEBUG_INFO : AT+CPIN
		MDM.receive(10)
		if(ConnectToServer() == 1) :
			#res = MDM.send(COLL_DATA_LINK, 5)
			res = MDM.send(TempBuffer+GlobalVaria.DataServer, 3)
			print ' in TempBuffer ',TempBuffer,len(GlobalVaria.DataServer)
			Receivedbuff = Wait4Data()
			print 'In Receivedbuff GlobalVaria.DataServer',Receivedbuff
			Receivedbuff = Wait4Data()
			print 'In Receivedbuff GlobalVaria.DataServer',Receivedbuff
			if(Receivedbuff.find('#HTTPRING') != -1):
				MOD.sleep(5)
				MDM.send('AT#HTTPRCV=1\r', 2)
			else:
				print 'httpring not found'
				return 0
		else:
			print 'Connect to server fail '
			return 0
	while(loopCnt < 2):
		Receivedbuff = Wait4Data()
		print 'Receivedbuff',Receivedbuff
		if(Receivedbuff.find('ACK') != -1):
			print 'ACK RECEIVED'
			Receivedbuff = Wait4Data()
			print 'Receivedbuff afte ACK',Receivedbuff
			if((GlobalVaria.FileMode == '2') or (GlobalVaria.FileMode =='3')):
				GlobalVaria.LastRecord = '1'
			GlobalVaria.Servertrial  = 0
			if(GlobalVaria.send_connection_packet == 0):
				GlobalVaria.rawseek = Datafile.tell()
				#print 'GlobalVaria.rawseek',GlobalVaria.rawseek
				try:
					SeekFileptr = open(GlobalVaria.SEEK_PTR, 'w')
				except IOError:
					#print 'failed to open file in upload',GlobalVaria.SEEK_PTR
					GlobalVaria.HttpCon = 0
					Datafile.close()
					return 0
				SeekFileptr.write(str(GlobalVaria.rawseek))
				SeekFileptr.close()
				SeekFileptr= -1
				Datafile.close()
				print 'file is closed'
				#print 'GlobalVaria.rawseek write in seek file\n'
				return 1
			else:
				GlobalVaria.send_connection_packet = 0
				#print 'SUCCES SENDING CONNECTION PKT\n'
				return 1
		elif(Receivedbuff.find('NCK') != -1):
			print 'NCK RECEIVED'
			Datafile.close()
			return 0
		elif(Receivedbuff.find('NO CAR') != -1):
			print ' I GOT NO  CARRIER\n'
			Datafile.close()
			return 0
		loopCnt = loopCnt + 1
	return 0


# ########################################################### #
# #####  GetServResponse for sending bililng data  ############## #
# ########################################################### #
def GetServResponse():
	tempbuff = ''
	loopCnt = 0
	Trail_cfg = 0
	HashCnt = 0
	atfound = 0
	trailFlag = 0
	ModemBuff = ''
	GlobalVaria.Servertrial = 0
	#print '\n  In GetServResponse Function \n  '
	GlobalVaria.HTML_SERVICE = UrlSpliter(2)
	while(1):
		#print '\n In GetServResponse to server \n',GlobalVaria.Info['HttpUrl']
		print '\n connecting to server -in getreq\n'
		trailFlag = getService()
		if(trailFlag == 1):
			return 1
		elif(trailFlag == 3):
			GlobalVaria.Servertrial = GlobalVaria.Servertrial + 1
			if(GlobalVaria.Servertrial  > 1):
				print 'get service is failed'
				return 0
		else:
			return 0
def getService():
	TempBuffer = ''
	loopCnt = 0
	HashCnt = -1
	atfound = 0
	ModemBuff = ''
	getResponse_Addr = ''
	Get_Service = ''
	print '\n  In getResponse Function \n  '
	USize = ContentLength = len(GlobalVaria.ServiceNo)  + 6		# 'ScrNo=' is 6digits
	GlobalVaria.COLL_DATA_LINK =  'AT#HTTPSND=1,0,"'+ GlobalVaria.HTML_SERVICE+ 'GetRequest"'+','+str(USize)+',0\r'
	print 'COLL_DATA_LINK-USize',GlobalVaria.COLL_DATA_LINK,USize
	#COLL_DATA_LINK	= 'POST '+GlobalVaria.HTML_SERVICE+'GetCollectionData HTTP/1.1\r\nHost: '+GlobalVaria.HTML_ADDR+'\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: '+str(USize)+'\r\n\r\n'
	TempBuffer = 'ScrNo='+ str(GlobalVaria.ServiceNo)
	TrailCnt = 0
	MdmCmd = ''
	MdmRes = ''
	#print '\rDEBUG_INFO : AT+CPIN command Sending - \r',TrailCnt		#         DEBUG_INFO : AT+CPIN
	if(ConnectToServer() == 1) :
		#res = MDM.send(COLL_DATA_LINK, 5)
		res = MDM.send(TempBuffer, 3)
		print ' in TempBuffer ',TempBuffer
		Receivedbuff = Wait4Data()
		#print 'In Receivedbuff GlobalVaria.DataServer',Receivedbuff
		Receivedbuff = Wait4Data()
		print 'In Receivedbuff GlobalVaria.DataServer',Receivedbuff
		if(Receivedbuff.find('#HTTPRING') != -1):
			MOD.sleep(5)
			MDM.send('AT#HTTPRCV=1\r', 2)
			ModemBuff = Wait4Data()
			print 'Receivedbuff',ModemBuff
		while(HashCnt == -1):
			ModemBuff = ModemBuff + Wait4Data()
			HashCnt = ModemBuff.find('#')
			print 'ModemBuff-%s,loopCnt-%d'%(ModemBuff,loopCnt)
			if((ModemBuff.find('NCK') != -1) or (ModemBuff.find('NO CARRI') != -1) or (ModemBuff.find('not registered') != -1)):
				GlobalVaria.getReq = 0
				GlobalVaria.ServiceNo = ''
				return 0
			elif(HashCnt != -1):
				#print ' HASH FOUND \n'
				atfound = ModemBuff.find('@')
				if((atfound != -1) and (HashCnt != -1)):
					tempbuff = ModemBuff[atfound : ]
					#print '\n DATA SENDING TO SERIAL PORT\n',tempbuff
					SER.send("%s" %tempbuff)
					GlobalVaria.getReq = 0
					GlobalVaria.ServiceNo = ''
					ModemBuff = Wait4Data()
					return 1
				else:
					SER.send("%s" %INVALID['0'])
					GlobalVaria.getReq = 0
					GlobalVaria.ServiceNo = ''
					return 0
			else:
				loopCnt = loopCnt + 1
				if(loopCnt > 1):
					return 0
	else:
		return 3
# ########################################################### #
# ########     Function for Closing the Socket        ####### #
# ########################################################### #

def HttpTask():
	Ans = ''
	GlobalVaria.HttpCon = 0
	i=0
	GlobalVaria.recno = 0
	GlobalVaria.send_connection_packet = 0
	#print '\n ---------In Http Task ----------- \n'
	#print '\n GlobalVaria.getReq -%d,GlobalVaria.uploadSBMData-%d ,\n'%(GlobalVaria.getReq,GlobalVaria.uploadSBMData)
	if(GlobalVaria.getReq == 1):
		ReadInformationFile()
		#print '\n ------ ReadInformationFile Over------- \n'
		if(GetServResponse()== 1):
			print '\n Get Query Response from Server Success \n'
			GlobalVaria.getReq = 0
			GlobalVaria.HttpCon = 0
		else:
			print '\n Get Query Response from Server Failed \n'
			GlobalVaria.getReq = 0
			GlobalVaria.HttpCon = 0
	elif(GlobalVaria.uploadSBMData == 1):
		print '\n ----- TextFile Upload Start ----- \n'
		if(uploadDataFiles() == 1):
			Ans = ' '
			for i in range(0,2):
				MDM.receive(5)
				MDM.send('AT#DSCRIPT="'+GlobalVaria.SBM_DATA_OUTFILE+'"\r',3)
				Ans = Wait4Data()
				print 'Ans',Ans
				print 'Ans',Ans.find('OK')
				if(Ans.find('OK') != -1):
					print 'HttpUploadFileName  Available, Now Removed-'
					GlobalVaria.OutFileLenExceededflag = '0'
					break
				else:
					print 'file is not removed',Ans
			GlobalVaria.OutFileLenExceededflag = '0'
			GlobalVaria.uploadSBMData = 0
			GlobalVaria.HttpCon = 0
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
	MdmRes = ''
	MDM2.send('AT+CNMI=2,1\r', 3)
	MdmRes = Wait4DataInMdm2()
	if(MdmRes.find('OK')==-1):
		GlobalVaria.SmsFlag = 0
		print 'SMS not AVAILABLE',MdmRes
	else:
		MdmRes = ''
		MDM2.send('AT+CMGF=1\r', 3)		
		MdmRes = Wait4DataInMdm2()
		if(MdmRes.find('OK') == -1):
			GlobalVaria.SmsFlag = 0
			print 'SMS not AVAILABLE',MdmRes
		else:
			GlobalVaria.SmsFlag = 1;
			MdmRes = ''
			print 'SMS AVAILABLE',MdmRes
			MDM2.receive(10)

		

# *********************************************************** #	
# **********       MAIN PROGRAM START FROM HEAR     ********* #
# *********************************************************** #

led = 0
data = ''
SbmEntry = 0
Rtc_Set_Flag = '0'
print ('   SBM READING © 2014 ENTRY Telit Communications\r ')
a = SER.set_speed('115200','8N1')
TrailCnt  = 0
MDM.send('AT+CPIN?\r', 2)
MdmRes = Wait4Data()
#PrintDebug('\n AT+CPIN? - \n' + MdmRes)
if(MdmRes.find('+CPIN')==-1):
	GlobalVaria.simavailable = 0
	#PrintDebug('SIM NOT AVAILABLE'+MdmRes)
else:
	GlobalVaria.simavailable = 1
	#PrintDebug('SIM AVAILABLE'+MdmRes)
GlobalVaria.SignalStrength = '00'
GlobalVaria.SignalStrength = GetSignalStrength()
#PrintDebug('Main Task -Version : ' + GlobalVaria.SBM_SW_VERSION)
#ReadInformationFile()
modemInitialization()
loopIndex = 1
while(loopIndex < 5):
	PrintDebug("2")
	PostData("filename=12345678&recno=1")
	MOD.sleep(30)
	loopIndex = loopIndex + 1
	
TrailCnt = 0
SmsSetup()
while((GlobalVaria.simavailable == 1) and (GlobalVaria.Gprs_Flag == 0) and (TrailCnt < 3)):
	print 'Checking Gprs Connection - \n',TrailCnt
	if(checkGPRSConnection() == 1):
		GlobalVaria.Gprs_Flag = 1
		if(Http_Cfg() == 1):
			GlobalVaria.Http_Cfg_Flag = 1
	else:
		GlobalVaria.Gprs_Flag = 0
		GlobalVaria.Http_Cfg_Flag = 0
	TrailCnt = TrailCnt + 1
# #####    MAIN PROGRAM WHILE LOOP START HEAR ########## #

if(GlobalVaria.Gprs_Flag == 1):
	MDM.send('at#ntp="ntp1.inrim.it",123,1,5\r',3)
	MdmRes = Wait4Data()
	if(MdmRes.find('#NTP:') != -1):
		print '#NTP is found RTC IS SET'
		Rtc_Set_Flag = '1'
	else:
		Rtc_Set_Flag = '0'
while(1):
	MdmRes = ''
	res = ''
	Expired = ''
	#PrintDebug('\n ---------  Running in the main Loop  -------------\n')
	#ReadRTC()
	MDM.receive(1)
	MDM.receive(1)
	MDM.receive(1)
	GlobalVaria.SignalStrength = GetSignalStrength()
	if(int(GlobalVaria.SignalStrength) > 9):
		if(GlobalVaria.Gprs_Flag == 0):
			print 'GlobalVaria.Gprs_Flag is-',GlobalVaria.Gprs_Flag
			if(checkGPRSConnection() == 1):
				GlobalVaria.Gprs_Flag = 1 #ravi
				if(GlobalVaria.Http_Cfg_Flag == 0):
					Http_Cfg()
			else:
				GlobalVaria.Gprs_Flag = 0
				modemInitialization()
		else:
			print 'Gprs is Available'
	else:
		print 'GlobalVaria.SignalStrength is Low',GlobalVaria.SignalStrength
		GlobalVaria.SignalStrength = '00';
	if(Rtc_Set_Flag == '0') and (GlobalVaria.Gprs_Flag == 1):
		print 'Setting Rtc_Set_Flag',Rtc_Set_Flag
		MDM.send('at#ntp="ntp1.inrim.it",123,1,3\r',3)
		MdmRes = Wait4Data()
		if(MdmRes.find('#NTP:') != -1):
			print '#NTP is found RTC IS SET'
			Rtc_Set_Flag = '1'
		else:
			print '#NTP is Not found'
			Rtc_Set_Flag = '0'
	if(GlobalVaria.SmsFlag == 0):
		print '\n Sms Settuping'
		SmsSetup()
		MDM2.receive(10)
	DayChange()
	SBMmetReading()
	#print 'GlobalVaria.SBM_FLAG-%d,GlobalVaria.uploadSBMData-%d'%(GlobalVaria.SBM_FLAG,GlobalVaria.uploadSBMData)
	if(((GlobalVaria.SBM_FLAG == 1 or GlobalVaria.uploadSBMData == 1 or GlobalVaria.getReq == 1)) and (GlobalVaria.simavailable == 1) and (GlobalVaria.SignalStrength != '00')):
		print'\n  Http task started  \n'
		HttpTask()
		print 'http task completed \n'