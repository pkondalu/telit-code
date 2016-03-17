#  #######           NARESH-(11022015)             ######## #
from Common import *
import GlobalVaria
import MOD
import SER
import MDM
import MDM2
import sys

global UartDataIn
global SMSCount
global OutfileHandler

OutfileHandler = -1
mycase = {'!':'' ,'"':'' ,'@':'' ,'#':'' ,'%':'' }
VALID   	= {'0':'\x06'};
INVALID 	= {'0':'\x15'};
STX     	= {'0':'\x02','1':'\x03'};
END     	= {'0':'\x0d','1':'\x0a'};
DEFAULT_APN_SERVER			 = "airtelgprs.com                "
DEFAULT_HTTPURL				 = "http://cpdclcollservice.atil.info/service.asmx/                                 "
CMD_DOWNLOAD_DATA  = '0x28'
CMD_DOWNLOAD_DATA  = '0x28'
UartDataIn = 0
