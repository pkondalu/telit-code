# #######         NARESH-(21062014)             ######## #
# ######################## SBMMAIN  #####################
global SBM_SW_VERSION
global UartData
global simavailable
global SBMBuffer
global sbmInFileLength1
global sbmInFileLength2
global Gprs_Flag
global sbmOutFileLength
global ServiceNo
global getReq
global DataAvailable2Upload
global SBM_FLAG
global HTML_SERVICE
global HTML_ADDR
global Http_Cfg_Flag
global COLL_DATA_LINK
global 	ServerFileName
global 	Type
global 	StarRecNo
global ConnectionPacket
global uploadFileSize
global ContentLen
global HttpUploadFileName
global SEEK_PTR
global DATA_LEN
global recno
global RawUpldRecNo
global TxtUpldRecNo
global send_connection_packet
global TotRec2Upload
global loop1val
global loop2val
global rawseek
global DataServer
global ENCRYPTSBMOUTFILE
global LastRecord
global  data_length
global SmsFlag
# ##########################  MAINFUNC   #########################
global 	uploadSBMData
global 	getDataFrmServer
global 	DnldRespFile
global 	Infodata
global  CIMINumber
global  HttpCon
global  SignalStrength
global  SBM_DATA_INFILE1
global  SBM_DATA_INFILE2
global  SBM_DATA_OUTFILE
global  INFORMATION_FILE
global InFileLenExceededflag
global OutFileLenExceededflag
global Servertrial
global gAtResponse
global gHttpRespone
global gFileValidationMethod
global gUploadDataMethod
global gDownloadDataMethod
global 	APN
global exitFlag
global SBM_RTC_BUFFER
# ########################## SBMMAIN INITILAISATION #########################
SBM_RTC_BUFFER=''
exitFlag=0
APN=  "airtelgprs.com                "
gFileValidationMethod = "FileValidation"
gDownloadDataMethod = "ReadRecord"
gUploadDataMethod = "GetCollectionData"
UartData 			= ""
InFileLenExceededflag = '0'
Servertrial = 0
OutFileLenExceededflag = '0'
SBM_SW_VERSION 	= "@1.14T#"
Info = {'ApnServer':'','HttpUrl':''}
Gprs_Flag = 0
HttpCon = 0
COLL_DATA_LINK = ''
ENCRYPTSBMOUTFILE = "ENSBOUT.txt"
SEEK_PTR      = "SEEK_PTR.txt"
SBMBuffer 			= ""
Http_Cfg_Flag = 0
CIMINumber = ''
sbmInFileLength1 	= 0
sbmInFileLength2 	= 0
SBM_FLAG = 0
sbmOutFileLength 	= 0
ServiceNo 			= ' '
getReq 				= 0
simavailable = 0
DATA_LEN      = 2000
DataAvailable2Upload = 0
SignalStrength = '00'
SBM_DATA_INFILE1			 = "SBMZTIN1.txt"
SBM_DATA_INFILE2			 = "SBMZTIN2.txt"
SBM_DATA_OUTFILE			 = "SBMZTOUT.txt"
INFORMATION_FILE			 = "INFO.INF"
SmsFlag = 0
# ########################## MAINFUNC INITILAISATION #########################
uploadSBMData 		= 0
getDataFrmServer 	= 0
DnldRespFile 		= 0
Infodata = [' '] * 111#List Array Size
DateTime	= {'day':'','month':'','year':'','hour':'','min':'','sec':''}#Dictionary
# ############################################## #
