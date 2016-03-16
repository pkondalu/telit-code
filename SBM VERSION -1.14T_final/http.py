from Common import *
import GlobalVaria
import os
### Url for documentation: http://forum.arduino.cc/index.php?topic=287462.0

def Send2Modem1(atCommand, command, exceptedRes, timeout):
    response = "121212O12K"
    result = response.find(exceptedRes)
    return True if result >= 0 else False

def ConnectToServerMock():
    print(GlobalVaria.COLL_DATA_LINK)
    return 1

def ValidateDevie(methodName):
    GlobalVaria.SBMBuffer = "112345678-2.04 "
    GlobalVaria.Info['HttpUrl']  = "http://apepdclatmsbm.ctms.info/"
    FileName = GlobalVaria.SBMBuffer[1: len(GlobalVaria.SBMBuffer)-1]
    command  = "%s%s" % (GlobalVaria.Info['HttpUrl'],FileName)
    GlobalVaria.HTML_SERVICE = UrlSpliter(2)

    httpData = "fileName=%s" % FileName 
    httpUrl = "\"%s%s\"" % (GlobalVaria.HTML_SERVICE,methodName)
    GlobalVaria.COLL_DATA_LINK = "%s%s,%s,0\r" % ('AT#HTTPSND=1,0,', httpUrl, str(len(httpData)))
    if(ConnectToServer() == 1):
        res = MDM.send(httpData, 3)
		Receivedbuff = Wait4Data()
		if(Receivedbuff.find('#HTTPRING') != -1):
			MOD.sleep(5)
			MDM.send('AT#HTTPRCV=1\r', 2)
		else:
			print 'httpring not found '
			return 0
		return 1
	else:
		print("unable to connect to the Web Server method")
		return 0
def CreateFile(filename, data):
	os.system("touch %s" % filename)
	f = open(filename, "w")
	f.write(data)
	f.close()

def DownloadData(filename, recordNum):
	httpData = ""
	methodName = ""
	GlobalVaria.Info['HttpUrl']  = "http://apepdclatmsbm.ctms.info/"
	httpUrl = "\"%s%s\"" % (GlobalVaria.HTML_SERVICE,methodName)
	GlobalVaria.COLL_DATA_LINK = "%s%s,%s,0\r" % ('AT#HTTPSND=1,0,', httpUrl, str(len(httpData)))
    if(ConnectToServer() == 1):
		res = MDM.send(httpData, 3)
    	if(Receivedbuff.find('#HTTPRING') != -1):
			MOD.sleep(5)
			MDM.send('AT#HTTPRCV=1\r', 2)
		else:
			print 'httpring not found '
			return 0
		Receivedbuff = Wait4Data()
		print(Receivedbuff)	
		CreateFile(Receivedbuff)
		return 1
	else:
		print ("Unable to download the data from http Service")
		return 0


