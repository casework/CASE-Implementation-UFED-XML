import codecs

#---	class ParserDebug.py
class ParserDebug:
	def __init__(self, debugFile):
		self.dFileName = debugFile
		self.dFileHandle = codecs.open(self.dFileName, 'w', encoding='utf8')

	def writeDebugCALL(self, data):    
		line = "\n*---\nTotal CALL (deleted)  " + str(data.CALLtotal)
		line += ' (' + str(data.CALLdeleted) + ')'
		line += '\n*---'		
		self.dFileHandle.write(line)
		for i in range(data.CALLtotal):
			line = '\n[id] ' + data.CALLid[i]
			line += '\n\t[status] ' + data.CALLstatus[i] 
			line += '\n\t[source] ' + data.CALLsource[i]
			line += '\n\t[direction] ' + data.CALLdirection[i]
			line += '\n\t[outcome] ' + data.CALLoutcome[i]
			line += '\n\t[time] ' + data.CALLtimeStamp[i]
			line += '\n\t[duration]' + data.CALLduration[i] 
			if (len(data.CALLrolesTO[i]) > 0):
				line += '\n\t[roleTO] ' + data.CALLrolesTO[i][0] 
			else:
				line += '\n\t[roleTO] ' + '_NOT_PROVIDED_' 
			
			if (len(data.CALLrolesFROM[i]) > 0):
				line += '\n\t[roleFROM] ' + data.CALLrolesFROM[i][0]
			else:
				line += '\n\t[roleFROM] ' + '_NOT_PROVIDED_'

			if (len(data.CALLnamesTO[i]) > 0):
				line += '\n\t[nameTO] ' + data.CALLnamesTO[i][0] 
			else:
				line += '\n\t[nameTO] ' + '_NOT_PROVIDED_'

			if (len(data.CALLnamesFROM[i]) > 0):
				line += '\n\t[nameFROM] ' + data.CALLnamesFROM[i][0]
			else:		
				line += '\n\t[nameFROM] ' + '_NOT_PROVIDED_'
			
			if (len(data.CALLidentifiersTO[i]) > 0):
				line += '\n\t[identifierTO] ' + data.CALLidentifiersTO[i][0]
			else:
			 	line += '\n\t[identifierTO] ' + '_NOT_PROVIDED_'

			if (len(data.CALLidentifiersFROM[i]) > 0):
				line += '\n\t[identifierFROM] ' + data.CALLidentifiersFROM[i][0]
			else:
				line += '\n\t[identifierFROM] ' + '_NOT_PROVIDED_'
				
			self.dFileHandle.write(line)

	def writeDebugCHAT(self, data):    
		line = "\n*---\nTotal CHAT (deleted)  " + str(data.CHATtotal)
		line += ' (' + str(data.CHATdeleted) + ')'
		line += '\n*---'		
		self.dFileHandle.write(line)
		for i in range(data.CHATtotal):
			line = '\n* [CHATid] ' + data.CHATid[i]
			line += '\n\t[source] ' + data.CHATsource[i]
			for j in range(len(data.CHATpartyIdentifiers[i])):
				line +=  '\n\t[particpantIdentifier] ' + data.CHATpartyIdentifiers[i][j] 
				line +=  '\n\t[particpantName] ' + data.CHATpartyNames[i][j]
			for j in range(len(data.CHATmsgBodies[i])):
				line += '\n\t[msg n.] ' + str(j + 1)
				line += '\n\t\t[IdentifierFROM] ' + data.CHATmsgIdentifiersFrom[i][j]
				line += '\n\t\t[NameFROM] ' + data.CHATmsgNamesFrom[i][j]
				line += '\n\t\t[msgIdentifierTO] ' + data.CHATmsgIdentifiersTo[i][j]
				line += '\n\t\t[msgNameTO] ' + data.CHATmsgNamesTo[i][j]
				line += '\n\t\t[msgBody] ' + data.CHATmsgBodies[i][j]
				line += '\n\t\t[Status] ' + data.CHATmsgStatuses[i][j]
				line += '\n\t\t[msgTimeStamp] ' + data.CHATmsgTimeStamps[i][j]
				line += '\n\t\t[Attachment (File/Url)] ' + data.CHATmsgAttachmentFilenames[i][j]
				line += ' @@@ ' + data.CHATmsgAttachmentUrls[i][j]
			self.dFileHandle.write(line)

	def writeDebugCONTACT(self, data):		    	
		line = "\n*---\nTotal CONTACT (deleted)  " + str(data.CONTACTtotal)
		line += ' (' + str(data.CONTACTdeleted) + ')'
		line += '\n*---'		
		self.dFileHandle.write(line + '\n')
		for i in range(data.CONTACTtotal):
			line = '[CONTACTid] ' + data.CONTACTid[i]  + '\n'        
			line +=  ' [Name] ' + data.CONTACTname[i] 
			for j in range(len(data.CONTACTphoneNums[i])):
				line +=  ' [PhoneNums] ' + data.CONTACTphoneNums[i][j] + ' '
			line += '\n'
			self.dFileHandle.write(line)
        
	def writeDebugCONTEXT(self, data):    
		line = "\n*---\nCONTEXT"
		line += '\n*---'		
		line += '\n\t[Ufed version] ' + data.CONTEXTufedVersionText
		line += '\n\t[Device Extraction start date/time] '
		line += data.CONTEXTdeviceCreationTimeText + '\n'
		line += '\n\t[Device Acquisition Start/End date/time] '
		line += data.CONTEXTdeviceExtractionStartText + ' / '
		line += data.CONTEXTdeviceExtractionEndText + '\n'
		line += '\n\t[Examiner name] '
		line += data.CONTEXTexaminerNameText + '\n'
		line += '\n\t[Bluetooth MAC] ' + data.CONTEXTdeviceBluetoothAddressText
		line += '\n\t[DeviceID] ' + data.CONTEXTdeviceIdText
		line += '\n\t[PhoneModel] ' + data.CONTEXTdevicePhoneModelText
		line += '\n\t[OS type] ' + data.CONTEXTdeviceOsTypeText
		line += '\n\t[OS version] ' + data.CONTEXTdeviceOsVersionText
		line += '\n\t[PhoneVendor] ' + data.CONTEXTdevicePhoneVendorText
		line += '\n\t[MAC] ' + data.CONTEXTdeviceMacAddressText
		line += '\n\t[ICCID] ' + data.CONTEXTdeviceIccidText
		line += '\n\t[IMSI] ' + data.CONTEXTdeviceImsiText
		line += '\n\t[IMEI] ' + data.CONTEXTdeviceImeiText
		line += '\n\t[Files]'
		for i in range (len(data.CONTEXTimagePath)):
			line += '\n\t\t[path]' + data.CONTEXTimagePath[i]
			line += '\n\t\t[size]' + data.CONTEXTimageSize[i]
			line += '\n\t\t[hash SHA256 / MD5]' + data.CONTEXTimageMetadataHashSHA[i] + ' / '
			line += data.CONTEXTimageMetadataHashMD5[i]
		self.dFileHandle.write(line)

	def writeDebugEMAIL(self, data):
		line = "\n*---\nTotal EMAIL (deleted)  " + str(data.EMAILtotal)
		line += ' (' + str(data.EMAILdeleted) + ')'
		line += '\n*---'		
		self.dFileHandle.write(line)
		for i in range(data.EMAILtotal):
			line = '\n[EMAILid] ' + data.EMAILid[i]
			line += '\n\t[status] ' + data.EMAILstatus[i]
			line += '\n\t[Source] ' + data.EMAILsource[i]
			line += '\n\t[FROM] ' + data.EMAILidentifierFROM[i] 
			line += '\n\t[TO] '
			for j in range(len(data.EMAILidentifiersTO[i])):
				line += '\n\t\t' + data.EMAILidentifiersTO[i][j] 				
			line += '\n\t[CC] '
			for j in range(len(data.EMAILidentifiersCC[i])):
				line += '\n\t\t' + data.EMAILidentifiersCC[i][j]
			line += '\n\t[BCC] ' 
			for j in range(len(data.EMAILidentifiersBCC[i])):
				line += '\n\t\t' + data.EMAILidentifiersBCC[i][j]
	        
			line += '\n\t[Body] ' + data.EMAILbody[i]
			line += '\n\t[Subject] ' + data.EMAILsubject[i] 
			line += '\n\t[TimeStamp] ' + data.EMAILtimeStamp[i]
			line += '\n\t[Attachments]'
			for j in range(len(data.EMAILattachmentsFilename[i])):
				line += '\n\t\t' + data.EMAILattachmentsFilename[i][j]
			self.dFileHandle.write(line)        

	def writeDebugEXTRA_INFO(self, data):
		line = '\n*---\nTotal EXTRA_INFO ' + str(len(data.EXTRA_INFOdictPath))
		line += '\n*---'
		self.dFileHandle.write(line)
		for key in data.EXTRA_INFOdictPath:
			line = '\n[extraInofId] ' + key 
			line += '\n\t[path] ' + data.EXTRA_INFOdictPath[key]
			line += '\n\t[size] ' + data.EXTRA_INFOdictSize[key]
			line += '\n\t[tableName] ' + data.EXTRA_INFOdictTableName[key] 
			line += '\n\t[offset] ' + data.EXTRA_INFOdictOffset[key]
			line += '\n\t[nodeInfoId] ' + data.EXTRA_INFOdictNodeInfoId[key]
			self.dFileHandle.write(line)

	def writeDebugFILES(self, data):
		line = "\n*---\nTotal FILE " + str(len(data.FILEid))
		line += '\n*---'
		self.dFileHandle.write(line)
		for i in range(len(data.FILEid)):
			line = '\n[id]=' + data.FILEid[i]
			line += '\n\t[path] ' + data.FILEpath[i]
			line += '\n\t[size] ' + data.FILEsize[i]
			line += '\n\t[MD5] ' + data.FILEmd5[i] 
			line += '\n\t[Tags] ' + data.FILEtags[i] 
			line += '\n\t[Ctime] ' + data.FILEtimeCreate[i]  
			line += '\n\t[Mtime] ' + data.FILEtimeModify[i]  
			line += '\n\t[Atime] ' + data.FILEtimeAccess[i]  
			line += '\n\t[localPath] ' +  data.FILElocalPath[i] 
			line += '\n\t[iNodeNumber] ' + data.FILEiNodeNumber[i] 
			line += '\n\t[OwnerGID] ' + data.FILEownerGID[i] 
			line += '\n\t[OwnerUID] ' + data.FILEownerUID[i]
			self.dFileHandle.write(line)

	def writeDebugSMS(self, data):
		line = "\n*---\nTotal SMS (deleted)  " + str(data.SMStotal)
		line += ' (' + str(data.SMSdeleted) + ')'
		line += '\n*---'		
		self.dFileHandle.write(line)
		for i in range(len(data.SMSbody)):
			line = '\n[SMSid] ' + data.SMSid[i]
			line += '\n\t[status] ' + data.SMSstatus[i]
			line += '\n\t[source] ' + data.SMSsource[i]
			line += '\n\t[parties]'
			for j in range(len(data.SMSpartyRoles[i])):
				line += '\n\t\t[role] ' + data.SMSpartyRoles[i][j]
				line += '\n\t\t[identifier] ' + data.SMSpartyIdentifiers[i][j] 
				line += '\n\t\t[name] ' + data.SMSpartyNames[i][j] 
       			
			line += '\n\t[time] ' + data.SMStimeStamp[i]
			line += '\n\t[body] ' + data.SMSbody[i]      
			self.dFileHandle.write(line)
    		    	
	def writeDebugU_ACCOUNT(self, data): 
		line = "\n*---\nTotal U_ACCOUNT " + str(data.U_ACCOUNTtotal)
		line += '\n*---'				
		self.dFileHandle.write(line)
		for i in range(len(data.U_ACCOUNTsource)):
			line = '\n\t[Source] ' + data.U_ACCOUNTsource[i] 
			line += '\n\t[Name] ' + data.U_ACCOUNTname[i] 
			line += '\n\t[User Name] ' + data.U_ACCOUNTusername[i] 
			self.dFileHandle.write(line)           


	def writeDebugWEB_PAGE(self, data):    
		line = "\n*---\nTotal WEB_PAGE (deleted)  " + str(data.WEB_PAGEtotal)
		line += ' (' + str(data.WEB_PAGEdeleted) + ')'
		line += '\n*---'		
		self.dFileHandle.write(line)
		for i in range(data.WEB_PAGEtotal):
			line = '\n[id] ' + data.WEB_PAGEid[i]
			line += '\n\t[source] ' + data.WEB_PAGEsource[i]
			line += '\n\t[url] ' + data.WEB_PAGEurl[i]
			line += '\n\t[title] ' + data.WEB_PAGEtitle[i]
			line += '\n\t[visitCount] ' + data.WEB_PAGEvisitCount[i]
			line += '\n\t[lastVisited] ' + data.WEB_PAGElastVisited[i]
			self.dFileHandle.write(line)

	def closeDebug(self):
		self.dFileHandle.close()

