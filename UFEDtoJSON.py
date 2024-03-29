#---	class UFEDtoJSON.py

import uuid
import os
import re
import sys
from UFED_case_generator import *
#from inspectrutils.case_builder import *
from datetime import datetime
#import logging

class UFEDtoJSON():
	'''
	It represents all attributes and methods to process the traces extracted from XML reports to generate
	the JSON-LD file complied with the last version of UCO/CASE ontologies.
	'''
	TAB = '\t'

# default value for string value not provided
#
	NP = ''  				

# default value for integer value not provided
#
	INT = '0'				

# default value for date value not provided
#
	DATE = '1900-01-01T08:00:00'				

# default value for Hash Method value not provided
#
	HASH_M = 'MD5' 	

# default value for Hash Method value not provided
#
	HASH_V = '1' * 76 	

# default value for the property referrerUrl of the URLHistoryFacet class
#
	REF_URL = 'http:www.empty.com/referrer_url'

# default value for the location where a forensic action was carried out
#
	LOC = 'Unknown location'


	def __init__(self, json_output=None, app_name=None, app_user_name=None, 
		app_user_account=None, case_bundle=None):
		
		# logging.basicConfig(filename='_jess.log', level=logging.INFO,
  #           filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

		self.bundle = case_bundle
		self.FileOut = json_output
		self.phoneNumberList = []
		self.phoneNameList = []
		self.phoneUuidList = []
		
		self.appNameList = []
		self.appObjectList = []
		self.domain_name_list = []
		self.domain_observable_list = []
		self.appAccountUsernameList = []
		self.appAccountNameList = []		
		self.accountName = []
		self.uuidaccountName = []

		self.CHATparticipantsNameList = []
		self.CHATparticipantsIdList = []
		self.CHATaccountIdList = []

		self.EMAILaccountObjectList = []
		self.EMAILaddressList = []
		self.phoneOwnerNumber = ''
		self.object_phone_owner = ''
		self.FILEuuid = {}
		self.FILEpath = {}
		self.FILEid = []

		self.EXTRA_INFOdictPath = {}
		self.EXTRA_INFOdictSize = {}
		self.EXTRA_INFOdictTableName = {}
		self.EXTRA_INFOdictOffset = {}
		self.EXTRA_INFOdictNodeInfoId = {}

		self.U_ACCOUNTapp = app_name
		self.U_ACCOUNTappUserName = app_user_name
		self.U_ACCOUNTappUserAccount = app_user_account

		self.DEVICE_object = None

		self.UrlList = {}

		self.LocationList = []
		self.LocationIDList = []

		self.CELL_SITE_gsm ={}

		self.WIRELESS_NET_ACCESS ={}

		self.LOCATION_lat_long_coordinate = {}
		self.SEARCHED_ITEMvalue_date = []


		self.SYS_MSG_ID = ''
				
		
	# static methods do not receive class or instance arguments
	# and usually operate on data that is not instance or class-specific
	@staticmethod
	def __createUUID():
		'''	
		Observables in CASE have a unique identification number, based on Globally Unique Identifier.  
		Each time a Trace is generated this static method in invoked, it doen't depends on any object
		'''
		return str(uuid.uuid4())

	def __checkAppName(self, name):
		"""It stores all the application connected with any Trace, in order to avoid duplications.
		    :param name: Tte name of the application (string)
			:return: observableApp.
		"""		
		if name in self.appNameList: 
			idx = self.appNameList.index(name)
			observable_app = self.appObjectList[idx]
		else:
			observable_app = self.__generateTraceAppName(name)
			self.appNameList.append(name)
			self.appObjectList.append(observable_app)
		
		return observable_app

	def __checkAccountName(self, account, name, uuidApp):
		self.accountName = []
		self.uuidaccountName = []
		id = account + '###' + name
		if id not in self.accountName: 
			uuid = self.__generateTraceApplicationAccount(account, name, uuidApp)
			self.accountName.append(id)
			self.uuidaccountName.append(uuid)

	def __checkGeoCoordinates(self, latitude, longitude, elevation, category):
		latitude = latitude.strip()
		longitude = longitude.strip()
		
		observable_location = None
		if latitude != '' and longitude != '':
			id_geo_loc = latitude + '@' + longitude
			if id_geo_loc in self.LOCATION_lat_long_coordinate.keys():
				observable_location = self.LOCATION_lat_long_coordinate[id_geo_loc]
			else:
				observable_location = self.__generateTraceLocationCoordinate(latitude, 
					longitude, elevation, category)
				self.LOCATION_lat_long_coordinate[id_geo_loc] = observable_location

		return observable_location

	def __checkSearchedItems(self, value):		
		itemFound = False
		if value not in self.SEARCHED_ITEMvalue_date:			
			self.SEARCHED_ITEMvalue_date.append(value)
			itemFound = True

		return itemFound

	def __checkUrlAddress(self, address):		
		if address in self.UrlList.keys(): 
			observable_url = self.UrlList.get(address)
		else:
			observable_url = self.__generateTraceURLFullValue(address)
			self.UrlList[address] = observable_url
	
		return observable_url

	def __checkChatParticipant(self, chat_id, chat_name, chat_source, id_app):
		if chat_id.strip() in self.CHATparticipantsIdList: 
			idx = self.CHATparticipantsIdList.index(chat_id.strip())
			observable_chat_account = self.CHATaccountIdList[idx]
		else:
			self.CHATparticipantsNameList.append(chat_name.strip())
			observable_chat_account = self.__generateTraceApplicationAccount(chat_id.strip(), 
				chat_name.strip(), id_app)
			self.CHATparticipantsIdList.append(chat_id.strip())
			self.CHATaccountIdList.append(observable_chat_account)
		
		return observable_chat_account
	
	def __checkPhoneNumber(self, contact_phone_num, contact_name):
		if contact_phone_num not in self.phoneNumberList:					
			self.phoneNumberList.append(contact_phone_num)
			self.phoneNameList.append(contact_name)
			mobileOperator = ""
			uuid = self.__generateTracePhoneAccount(mobileOperator, 
				contact_name, contact_phone_num)
			self.phoneUuidList.append(uuid)

	def __cleanDate(self, originalDate):
		aMonths = {
			'Jan': '01',
			'Feb': '02',
			'Mar': '03',
			'Apr': '04',
			'May': '05',
			'Jun': '06',
			'Jul': '07',
			'Aug': '08',
			'Sep': '09',
			'Oct': '10',
			'Nov': '11',
			'Dec': '12'
		}

		originalDate = originalDate.strip()
#---	the xsd:dateTime must have the format YYYY-MM-DDTHH:MM:SS (UTCxxx)
#		

		if 	originalDate == '':
			return None

		for k,v in aMonths.items():
			if originalDate.find(k) > -1:
				originalDate = originalDate.replace(k, v)
				break

		originalDate = originalDate.replace("/", "-")
		originalDate = originalDate.replace("(", "-")
		originalDate = originalDate.replace(")", "-")
		originalDate = originalDate.replace(' ', 'T', 1)
		originalDate = originalDate.replace('UTC', '')
		originalDate = originalDate.replace('AM', '')
		originalDate = originalDate.replace('PM', '')
		if re.search('^[0-9]{4}', originalDate):
			pass
		else:
			originalDate = re.sub('-([0-9][0-9])T', '-20\g<1>T', originalDate)
			originalDate = str(originalDate[6:10]) + originalDate[2:6] + originalDate[0:2] + \
				originalDate[10:] 

		startTZ = originalDate.find("+")
		if startTZ > -1:
			originalDate = originalDate[:startTZ]

		firstChars = originalDate[:10]
		firstChars = firstChars.replace(".", "-")
		originalDate = firstChars + originalDate[10:]

		originalDate = originalDate.strip()

		if originalDate[-1] == '-':
			originalDate = originalDate[0:-1]

		originalDate = originalDate.replace('.000', '')
		originalDate = originalDate.replace('.', ':')

		if re.search('T\d{2}\.', originalDate):
			originalDate = originalDate.replace('.', ':')

		if re.search('(\d{2}:\d{2}:\d{2})$', originalDate):
			pass
		else:
			originalDate = re.sub('(\d{2}:\d{2})$', '\g<1>:00', originalDate)

		if re.search('T(\d):', originalDate):
			originalDate = re.sub('T(\d):', 'T0\g<1>:', originalDate)

		if re.search(':(\d):', originalDate):
			originalDate = re.sub(':(\d):', ':0\g<1>:', originalDate)

		if re.search(':(\d)$', originalDate):
			originalDate = re.sub(':(\d)$', ':0\g<1>', originalDate)

		if re.search('T\d{2}:\d{2}:\d{2}(.+)$', originalDate):
			originalDate = re.sub('(T\d{2}:\d{2}:\d{2})(.+)$', '\g<1>', originalDate)

		
		if originalDate.find('+') > -1:
			originalDate = datetime.strptime(originalDate, 
				'%Y-%m-%dT%H:%M:%S.%f%z')
		else:
			originalDate = datetime.strptime(originalDate, 
				'%Y-%m-%dT%H:%M:%S')
		
		return originalDate

	def __cleanJSONtext(self, originalText):
		new_text = originalText.strip()
		if new_text == '':
			return ''
		else:
			new_text = new_text.replace('"', "").replace('\n', '').replace('\r', '')
			new_text = new_text.replace('\t', " ").replace("\\'", "'").replace("\\", "")
			return new_text

	def __generateContextUfed(self, ufedVersion, deviceReportCreateTime,
			deviceExtractionStartTime, deviceExtractionEndTime, examinerName, 
			imagePath, imageSize, imageMetadataHashSHA, imageMetadataHashMD5):

		# generate Trace/Tool for the Acquisition and Extraction Actions
		object_tool = self.__generateTraceTool('UFED PA', 'Acquisition', 
			'Cellebrite', ufedVersion, []);
		
		# generate Trace/Identity for the Performer, D.F. Expert, of the Actions
		object_identity = self.__generateTraceIdentity(examinerName, '', '')
		
		# generate Trace/Role for the Performer, D.F. Expert, of the Actions
		object_role = self.__generateTraceRole('Digital Forensic Expert')
		
		# generate Trace/Relation between the above Role and the Identity traces
		self.__generateTraceRelation(object_identity, object_role, 
			'has_role', '', '', None, None);		
		
#---	The XML report contains the attribute DeviceInfoExtractionStartDateTime 
#		that is the Acquisition Start Date and similarly for the Acquisition
#		End Date, The CreationReportDate is the Start and the End of the Extraction 
#		Forensic Action.
#

#---	Generate Trace/Provenance_Record for the mobile device
#
		object_device_list = []
		object_device_list.append(self.DEVICE_object)
		object_provenance_device = self.__generateTraceProvencance(object_device_list, 
			'Mobile device', '', deviceExtractionStartTime) 
		
#---	generate Trace/File for each file extracted by the Acuisition action
#			idFileList contains the uuid of these files and it is used for
#			creating the Provenance_Record of the Result/Output of the Acquisition 
# 		action. 
#			2021-08-02: actually the XML report doesn't include the Acquisition info
#		
		object_files_acquisition = []
		for i, img_path in enumerate(imagePath):
			if imageMetadataHashSHA[i].strip() == '':
				object_file_acquisition = self.__generateTraceFile(img_path, 
				imageSize[i], 'MD5', imageMetadataHashMD5[i], 'Uncategorized', '', '', '', '',
				'', '', '', '', '', '', '', '', '', '', '')  
				 
			else:
				object_file_acquisition = self.__generateTraceFile(img_path, 
				imageSize[i], 'SHA256', imageMetadataHashSHA[i], 'Uncategorized', 
				'', '', '', '', '', '', '', '', '', '', '', '', '', '', '') 				
			
			object_files_acquisition.append(object_file_acquisition)  	
		

		object_provenance_acquisition_files = \
			self.__generateTraceProvencance(object_files_acquisition, 
        	'Acquisition files', '', deviceExtractionStartTime)

		object_provenance_acquisition_files_list = []
		object_provenance_acquisition_files_list.append(object_provenance_acquisition_files)
		
		object_provencance_acquisition_action = \
		self.__generateTraceInvestigativeAction('acquisition', 
			'Forensic mobile device acquisition', deviceExtractionStartTime, 
			deviceExtractionEndTime, object_tool, '', object_identity, 
			object_provenance_device, object_provenance_acquisition_files_list);

		object_files_extraction = []
		for uuidFile in self.FILEuuid.values(): 
			object_files_extraction.append(uuidFile)

		object_provenance_extraction_files = \
		self.__generateTraceProvencance(object_files_extraction, 'Extraction',
			'', deviceReportCreateTime);
        
		object_provenance_extraction_files_list = []
		object_provenance_extraction_files_list.append(object_provenance_extraction_files)

		self.__generateTraceInvestigativeAction('extraction', 
			'Forensic mobile device extraction', deviceReportCreateTime,
			deviceReportCreateTime, object_tool, '', object_identity,
			object_provenance_acquisition_files, object_provenance_extraction_files_list);

	def __generateChainOfEvidence(self, IdTrace, uuidTrace):
#---	Search traceId in EXTRA_INFOdictNodeInfo a dictionary whose keys are the id
#			that represents the link between a Trace and its file(s)
#		
		table = self.EXTRA_INFOdictTableName.get(IdTrace, '_?TABLE')
		offset = self.EXTRA_INFOdictOffset.get(IdTrace, '_?OFFSET')

#---	This is the case where the infoNode sub element of extraInfo contains the id 
#		reference to the file. More then one infoNode can exist, the value of the key 
#		contains the id file separated by @@
#		
		if self.EXTRA_INFOdictNodeInfoId.get(IdTrace, '').strip() == '':
			path = self.EXTRA_INFOdictPath.get(IdTrace, '_?PATH')
			size = self.EXTRA_INFOdictSize.get(IdTrace, '_?SIZE')
			if path != '_?PATH':
				uuidFile = self.__generateTraceFile(path, size, '', 
						'', 'Uncategorized', '', '', '', '', '', 
						'', '', '', '', '', '', '', '', '', '')

				self.FILEuuid[IdTrace] = uuidFile
				self.__generateTraceRelation(uuidTrace, uuidFile, 'Contained_Within', 
					table, offset, None, None);
		else:
			nodeInfoIdList = self.EXTRA_INFOdictNodeInfoId.get(IdTrace, '@@@').split('@@@')
			for node in nodeInfoIdList:
				if node.strip() != '': 
					if node in self.FILEid: 
						uuidFile = self.FILEuuid.get(node, '_?UUID')
						self.__generateTraceRelation(uuidTrace, uuidFile, 'Contained_Within', 
							table, offset, None, None);	
					else:
						print ('nodeInfo ' + node + ' not found')		

	def writeDevice(self, deviceId, devicePhoneModel, deviceOsType, deviceOsVersion, 
            devicePhoneVendor, deviceMacAddress, deviceIccid, deviceImsi, 
            deviceImei, deviceBluetoothAddress, deviceBluetoothName):

#---	generate Trace/Device for the mobile phone
#	
		self.DEVICE_object = self.__generateTraceDevice(deviceMacAddress, deviceId, devicePhoneModel,
			deviceOsType, deviceOsVersion, devicePhoneVendor, deviceMacAddress,
			deviceIccid, deviceImsi, deviceImei, deviceBluetoothAddress, deviceBluetoothName)

	
	def __generateTraceAppName(self, app_name):
		
		observable = ObjectObservable()
		facet_application = Application(app_name=app_name)
		observable.append_facets(facet_application)
		self.bundle.append_to_uco_object(observable)
		return observable


	def __getMaxLenCallElement(self, CALLrolesTO, CALLrolesFROM, 
					CALLnamesTO, CALLnamesFROM, CALLidentifiersTO, 
					CALLidentifiersFROM):		
		maxLen = len(CALLrolesTO)
		
		if len(CALLrolesFROM) > maxLen:
			maxLen = len(CALLrolesFROM)
		if len(CALLnamesTO) > maxLen:
			maxLen = len(CALLnamesTO)
		if len(CALLnamesFROM) > maxLen:
			maxLen = len(CALLnamesFROM)
		if len(CALLidentifiersTO) > maxLen:
			maxLen = len(CALLidentifiersTO)
		if len(CALLidentifiersFROM) > maxLen:
			maxLen = len(CALLidentifiersFROM)
		return maxLen

	def writeCall(self, CALLid, CALLstatus, CALLsource, CALLtimeStamp, 
					CALLdirection, CALLduration, CALLrolesTO, CALLrolesFROM, 
					CALLnamesTO, CALLnamesFROM, CALLoutcome, CALLidentifiersTO, 
					CALLidentifiersFROM):
		
#---	each kind of phone call, further the traditional ones, are
#			processed, so the phonePattern is not necessary any more
#	
		phonePattern = '^\+?[0-9]+$'	# phone number pattern
		
		for i, call_id in enumerate(CALLid):
			
#---	there are two Parties, each of them with their own role
#						
			idPartyTO = ''
			idPartyFROM = ''
			idParty = ''
			
			maxLen = self.__getMaxLenCallElement(CALLrolesTO[i], CALLrolesFROM[i], 
					CALLnamesTO[i], CALLnamesFROM[i], CALLidentifiersTO[i], 
					CALLidentifiersFROM[i])
			
#---	all these arrays should have the same size, the check fill in the values.
#		if this is not the case, the loops make the size the same for all arrays
#
			for j in range(maxLen - len(CALLrolesTO[i])):
				CALLrolesTO[i].append('')
			
			for j in range(maxLen - len(CALLrolesFROM[i])):
				CALLrolesFROM[i].append('')
			
			for j in range(maxLen - len(CALLnamesTO[i])):
				CALLnamesTO[i].append('')
			
			for j in range(maxLen - len(CALLnamesFROM[i])):
				CALLnamesFROM[i].append('')
			
			for j in range(maxLen - len(CALLidentifiersTO[i])):
				CALLidentifiersTO[i].append('')
			
			for j in range(maxLen - len(CALLidentifiersFROM[i])):
				CALLidentifiersFROM[i].append('')
			
			if maxLen == 0:
				CALLrolesTO[i].append('')
				CALLrolesFROM[i].append('')
				CALLnamesTO[i].append('')
				CALLnamesFROM[i].append('')
				CALLidentifiersTO[i].append('')
				CALLidentifiersFROM[i].append('')

			if (len(CALLrolesFROM[i]) > 1):
				if CALLrolesFROM[i][0].strip() == '':					
					idPartyFROM = CALLidentifiersFROM[i][1]
					nameFROM = CALLnamesFROM[i][1]
					idPartyTO 	= CALLidentifiersTO[i][0]
					nameTO = CALLnamesTO[i][0]
				else:
					idPartyFROM = CALLidentifiersFROM[i][0]
					nameFROM = CALLnamesFROM[i][0]
					idPartyTO 	= CALLidentifiersTO[i][1]
					nameTO = CALLnamesTO[i][1]
			else:					
					if CALLrolesFROM[i][0].strip() == '':
						idPartyFROM = self.phoneOwnerNumber
						nameFROM = 'PHONE OWNER'
						idPartyTO		= CALLidentifiersTO[i][0]
						idParty = idPartyTO
						nameTO = CALLnamesTO[i][0]
					else:						
						idPartyFROM		= CALLidentifiersFROM[i][0]
						idParty = idPartyFROM
						idPartyTO = self.phoneOwnerNumber
						nameFROM = CALLnamesFROM[i][0]
						nameTO = 'PHONE OWNER'
						
			resPattern = re.match(phonePattern, idParty.strip())

			if resPattern:
				if idPartyTO in self.phoneNumberList:
					idx = self.phoneNumberList.index(idPartyTO)
					uuidPartyTO = self.phoneUuidList[idx]
				else:	
	# if the mobile operator is available in the XML report, an uco-identity:Identity 
	# will be defined as Organisation. 
					mobileOperator = "-"
					uuidPartyTO = self.__generateTracePhoneAccount(mobileOperator, 
						nameTO, idPartyTO)

				if idPartyFROM in self.phoneNumberList:
					idx = self.phoneNumberList.index(idPartyFROM)
					uuidPartyFROM = self.phoneUuidList[idx]
				else:	
	# see the above commment
					mobileOperator = "-"
					uuidPartyFROM = self.__generateTracePhoneAccount(mobileOperator, 
						nameFROM, idPartyFROM)

			else:
				idAppIdentity = self.__checkAppName(CALLsource[i].strip())	
				if idPartyFROM.strip() in self.CHATparticipantsIdList: 
					idx = self.CHATparticipantsIdList.index(idPartyFROM.strip())
					uuidPartyFROM = self.CHATaccountIdList[idx]
				else:
					self.CHATparticipantsNameList.append(nameFROM.strip())
					uuidPartyFROM = self.__generateTraceApplicationAccount(idPartyFROM.strip(), 
						nameFROM.strip(), idAppIdentity)
					self.CHATparticipantsIdList.append(idPartyFROM.strip())
					self.CHATaccountIdList.append(uuidPartyFROM)
				
				if idPartyTO.strip() in self.CHATparticipantsIdList: 
					idx = self.CHATparticipantsIdList.index(idPartyTO.strip())
					uuidPartyTO = self.CHATaccountIdList[idx]
				else:
					self.CHATparticipantsNameList.append(nameTO.strip())
					uuidPartyTO = self.__generateTraceApplicationAccount(idPartyTO.strip(), 
						nameTO.strip(), idAppIdentity)
					self.CHATparticipantsIdList.append(idPartyTO.strip())
					self.CHATaccountIdList.append(uuidPartyTO)
							
			object_phone_call = self.__generateTracePhoneCall(CALLdirection[i].lower(), 
				CALLtimeStamp[i], uuidPartyFROM, uuidPartyTO, CALLduration[i],
            	CALLstatus[i], CALLoutcome[i])
			self.__generateChainOfEvidence(call_id, object_phone_call)


	def __generateTraceWebBookmark(self, wb_id, wb_source, wb_timeStamp, wb_path, wb_url):
		    
		observable = ObjectObservable()		
		object_url = self.__checkUrlAddress(wb_url)
		objet_app = self.__checkAppName(wb_source)
		
		if wb_timeStamp.strip() == '':
			wb_timeStamp = None
		else:
			wb_timeStamp = self.__cleanDate(wb_timeStamp)
						
		facet_web_bookmark = BrowserBookmark(bookmark_source=objet_app, url=object_url, bookmark_path=wb_path, bookmark_accessed_time=wb_timeStamp)
		observable.append_facets(facet_web_bookmark)
		self.bundle.append_to_uco_object(observable)
		return observable
		
	def __generateTraceBluetooth(self, bt_id, bt_status, bt_value):
		
		if bt_value.strip() == '':
			return None
		
		observable = ObjectObservable()
		facet_bluetooth = BluetoothAddress(address=bt_value)
		observable.append_facets(facet_bluetooth)
		self.bundle.append_to_uco_object(observable)
		return observable
	
	def __generateTraceCalendar(self, calendar_id, status, group, subject, 
					details, startDate, endDate, repeatUntil, repeatInterval, 
					repeatRule):
		
		startDate = self.__cleanDate(startDate)
		endDate = self.__cleanDate(endDate)
		
		subject = self.__cleanJSONtext(subject)
		details = self.__cleanJSONtext(details)

		observable = ObjectObservable()
		facet_calendary = CalendarEntry(group=group, subject=subject, 
			details=details, start_time=startDate, end_time=endDate,
			repeat_interval=repeatInterval, status=status)

		observable.append_facets(facet_calendary)
		self.bundle.append_to_uco_object(observable)
		return observable
		

	def __generateTraceCell_Site(self, cell_id, cell_status, 
					cell_longitude, cell_latitude, cell_timeStamp, cell_mcc, 
					cell_mnc, cell_lac, cell_cid, cell_nid, cell_bid, cell_sid):
		
		cell_timeStamp = self.__cleanDate(cell_timeStamp)

		observableLocation = self.__checkGeoCoordinates(cell_latitude, cell_longitude, '', 'Cell Tower')
		
#--- the Cell Site Observbale is however generated even if its location is unknown (no GPS coordinates)
		#if observableLocation is None:
			#print(f"observableLocation is None, num={cell_num}")
			#return None

		cell_id = cell_mcc.strip() + '@' + cell_mnc.strip() +'@' + \
			cell_lac.strip() + '@' + cell_cid.strip()
		
#---	identifier of the Cell Tower cannot be empty
#			
		if cell_id == '@@@':
			#print(f"cell_mcc, cell_mncm, cell_lac and  cell_cid are empty,  num={cell_num}")
			return None

		if cell_id in self.CELL_SITE_gsm.keys():
#---	return the Cell Tower's uuid generated sometime before
			#print(f"cell id={cell_id}, already existing,  num={cell_num}")	
			return self.CELL_SITE_gsm.get(cell_id)
		
		else:				
			observable_cell_site = ObjectObservable()
			facet_cell_site = CellSite(country_code=cell_mcc, 
				network_code=cell_mnc, area_code=cell_lac, site_id=cell_cid)
			observable_cell_site.append_facets(facet_cell_site)
			self.bundle.append_to_uco_object(observable_cell_site)
			
			self.CELL_SITE_gsm[cell_id] = observable_cell_site

			if observableLocation:
				observable_relationship = Relationship(observable_cell_site, observableLocation, 
					start_time=cell_timeStamp, kind_of_relationship="Located_At", 
					directional=True)
				self.bundle.append_to_uco_object(observable_relationship)		
			
			return observable_cell_site
				
		
	def __generateTraceApplicationAccount(self, partyId, partyName, idApp):

		partyName = self.__cleanJSONtext(partyName)
		partyId = self.__cleanJSONtext(partyId)
		
		observable = ObjectObservable()
		facet_account = Account(partyId)
		facet_app_account = ApplicationAccount(application=idApp)		
		facet_digital_account = DigitalAccount(display_name=partyName)    	
		
		observable.append_facets(facet_account, facet_app_account, facet_digital_account)
		
		self.bundle.append_to_uco_object(observable)		
		return observable


	def __generateTraceChat(self, body, idApplication, timeStamp, idFrom,
		idToList, status, outcome, direction, attachmentNames, 
		attachmentUrls):
		
		TOlist = []
		for item in idToList:
#---	The idFROM shouldn't be part of the idTOlist unless there is only one 
#		Participant
#
			if item != idFrom:
				TOlist.append(item)

#---	if the TO list is empty, idFROM and idTOlist will contain the same
#		identifier
#						
		if TOlist == []:
			TOlist.append(idFrom)
		
		body = self.__cleanJSONtext(body)		

		observable_message = self.__generateTraceMessageFacet(body, idApplication, 
			idFrom, TOlist, timeStamp, status, 'CHAT Message')
		
#---	each Message, within a specific Chat can have more than one attachment,
#		both the Filenames and the Urls of the Attachment are separated by
# 		a triple hash tag # 
#		
		listFileNames = attachmentNames.split('###');
		listFileUrls = attachmentUrls.split('###');
		nName = len(listFileNames)
		nUrl = len(listFileUrls)
		if nName > nUrl:
			for i in range(nName - nUrl):
				listFileUrls.append('')
		if nName < nUrl:
			for i in range(nUrl - nName):
				listFileNames.append('')


		for i, file_name in enumerate(listFileNames):
			if (file_name.strip() != '') or \
			 	(listFileUrls[i].strip() != ''):
				fileUuid = self.__generateTraceFile(file_name, 
				'', '', '', 'Uncategorized', '', '', '', listFileUrls[i],
				'', '', '', '', '', '', '', '', '', '', '')
				
				if uuid != '':
					self.__generateTraceRelation(fileUuid, observable_message, 
						'Connected_To', '', '', None, None)
		
		return observable_message


	def __generateTraceDevice(self, deviceMAC, deviceSN, deviceModel,
		deviceOS, deviceOSVersion, deviceManufacturer, deviceWiFi, deviceICCID,
		deviceIMSI, deviceIMEI, deviceBluetoothAddress, deviceBluetoothName):
		
		observable = ObjectObservable()
		facet_device = Device(device_type="Mobile phone",
			model=deviceModel, serial=deviceSN)	
		facet_mobile = MobileDevice(IMSI=deviceIMSI, ICCID=deviceICCID,
			IMEI=deviceIMEI)
		manufacturer_object = self.__generateTraceIdentity(None, deviceManufacturer, None)
		facet_operating_system = OperatingSystem(os_name=deviceOS,
			os_version=deviceOSVersion, os_manufacturer=manufacturer_object)
		facet_bluetooth = BluetoothAddress(name=deviceBluetoothName,
			address=deviceBluetoothAddress)
		facet_wifi = WifiAddress(wifi_mac_address=deviceWiFi)

		observable.append_facets(facet_device, facet_mobile, facet_operating_system, 
    		facet_bluetooth,facet_wifi)
    	
		self.bundle.append_to_uco_object(observable)
		
		return observable
	
	def __generateTraceCookie(self, cookie_id, cookie_status, 
					cookie_source, cookie_name, cookie_path, cookie_domain, 
					cookie_creationTime, cookie_lastAccessedTime, cookie_expiry):
		
		cookie_creationTime = self.__cleanDate(cookie_creationTime)
		cookie_lastAccessedTime = self.__cleanDate(cookie_lastAccessedTime)
		cookie_expiry = self.__cleanDate(cookie_expiry)
		cookie_name = self.__cleanJSONtext(cookie_name)
		observable = ObjectObservable()
		
		observable_source = self.__checkAppName(cookie_source)
		observable_domain = self.__checkAppName(cookie_domain)
				
		facet_cookie = BrowserCookie(source=observable_source, 
			name=cookie_name, path=cookie_path, domain=observable_domain, 
			created_time=cookie_creationTime, last_access_time=cookie_lastAccessedTime, 
			expiration_time=cookie_expiry)

		observable.append_facets(facet_cookie)
		self.bundle.append_to_uco_object(observable)
		return observable


	def __generateTraceDeviceEvent(self, event_id, event_status, 
		event_timeStamp, event_type, event_text):

		event_timeStamp = self.__cleanDate(event_timeStamp)		
		event_text = self.__cleanJSONtext(event_text)
		
		observable = ObjectObservable()

		facet_event = Event(event_type=event_type, 
			event_text=event_text, created_time=event_timeStamp)
		observable.append_facets(facet_event)

		self.bundle.append_to_uco_object(observable)
		return observable


	def __generateTraceInstalledApp(self, INSTALLED_APPid, INSTALLED_APPstatus, INSTALLED_APPname,
	    INSTALLED_APPversion, INSTALLED_APPidentifier, INSTALLED_APPpurchaseDate):
		
		INSTALLED_APPtimeStamp = self.__cleanDate(INSTALLED_APPpurchaseDate)
#--- id installed_app_purchase_date is not empy a complete ApplicationFacet and ans ApplicationVerions are generated,
#    otherwise on a partial APplicatinFacet is generate and no Chain of Evidence is created (return None)
		observable = ObjectObservable()
		if INSTALLED_APPtimeStamp:			
			object_app_version =  ApplicationVersion(INSTALLED_APPtimeStamp)
			self.bundle.append_to_uco_object(object_app_version)
			facet_application = Application(app_name=INSTALLED_APPname, app_identifier=INSTALLED_APPidentifier,
			    version=INSTALLED_APPversion, installed_version_history=object_app_version)
			observable.append_facets(facet_application)
			self.bundle.append_to_uco_object(observable)
			return observable
		else:
			facet_application = Application(app_name=INSTALLED_APPname, version=INSTALLED_APPversion,
			    app_identifier=INSTALLED_APPidentifier)
			observable.append_facets(facet_application)
			self.bundle.append_to_uco_object(observable)
			return None			
								
	def __generateTraceEmail(self, EMAILid, EMAILstatus, EMAILsource, 
		EMAILidentifierFROM, EMAILidentifiersTO, EMAILidentifiersCC, 
		EMAILidentifiersBCC, EMAILbody, EMAILsubject, EMAILtimeStamp, 
		EMAILattachmentsFilename):
		#print(f'EMAILidentifierFROM={EMAILidentifierFROM}')
		if EMAILidentifierFROM.strip() in self.EMAILaddressList:
			idx = self.EMAILaddressList.index(EMAILidentifierFROM.strip())
			idFROM = self.EMAILaccountObjectList[idx]
		else:
			self.EMAILaddressList.append(EMAILidentifierFROM.strip())
			observable_email_account = self.__generateTraceEmailAccount(EMAILidentifierFROM.strip())
			self.EMAILaccountObjectList.append(observable_email_account)
			idFROM = observable_email_account

		itemsTO = []
		for i, email_identifier in enumerate(EMAILidentifiersTO):
			if email_identifier.strip() != '':
				if email_identifier.strip() in self.EMAILaddressList:
					idx = self.EMAILaddressList.index(email_identifier.strip())
					itemsTO.append(self.EMAILaccountObjectList[idx])
				else:
					self.EMAILaddressList.append(email_identifier.strip())
					observable_email = \
						self.__generateTraceEmailAccount(email_identifier.strip())
					self.EMAILaccountObjectList.append(observable_email)
					itemsTO.append(observable_email)

		itemsCC = []
		for i, email_identifier_cc in enumerate(EMAILidentifiersCC):
			if email_identifier_cc.strip() != '':
				if email_identifier_cc.strip() in self.EMAILaddressList:
					idx = self.EMAILaddressList.index(email_identifier_cc.strip())
					itemsCC.append(self.EMAILaccountObjectList[idx])
				else:
					self.EMAILaddressList.append(email_identifier_cc.strip())
					observable_email = self.__generateTraceEmailAccount(email_identifier_cc.strip())
					self.EMAILaccountObjectList.append(observable_email)
					itemsCC.append(observable_email)

		
		itemsBCC = []
		for i, email_identifier_bcc in enumerate(EMAILidentifiersBCC):
			if email_identifier_bcc.strip() != '':
				if email_identifier_bcc.strip() in self.EMAILaddressList:
					idx = self.EMAILaddressList.index(email_identifier_bcc.strip())
					itemsBCC.append(self.EMAILaccountObjectList[idx])
				else:
					self.EMAILaddressList.append(email_identifier_bcc.strip())
					observable_email = self.__generateTraceEmailAccount(email_identifier_bcc.strip())
					self.EMAILaccountObjectList.append(observable_email)
					itemsBCC.append(observable_email)

		body = self.__cleanJSONtext(EMAILbody)		
		subject = self.__cleanJSONtext(EMAILsubject)
		EMAILtimeStamp = self.__cleanDate(EMAILtimeStamp)
		
		observable = ObjectObservable()

		facet_email_message = EmailMessage(msg_to=itemsTO, 
			msg_from=idFROM, cc=itemsCC, bcc=itemsBCC, subject=subject, body=body, 
            sent_time=EMAILtimeStamp, allocation_status=EMAILstatus)


		observable.append_facets(facet_email_message)
		self.bundle.append_to_uco_object(observable)
		
		self.__generateChainOfEvidence(EMAILid, observable)

		for i, email_attachment in enumerate(EMAILattachmentsFilename):
			if email_attachment.strip() != '':
				fileUuid = self.__generateTraceFile(email_attachment, 
				'', '', '', 'Uncategorized', '', '', '', '',
  				'', '', '', '', '', '', '', '', '', '', '')
				self.__generateTraceRelation(fileUuid, observable, 'Attached_To', 
				'', '', None, None)
		
		return observable

	def __generateTraceEmailAccount(self, address):
		
		address = self.__cleanJSONtext(address) 
		observable_email_address = self.__generateTraceEmailAddress(address)

		observable_email_account = ObjectObservable()
		facet_email_account = EmailAccount(observable_email_address)
		facet_account = Account(identifier="-")
		observable_email_account.append_facets(facet_account, facet_email_account)
		
		self.bundle.append_to_uco_object(observable_email_account)
		
		return observable_email_account


	def __generateTraceEmailAddress(self, address):		
		address = self.__cleanJSONtext(address)

		observable = ObjectObservable()
		facet_email_address = EmailAddress(email_address_value=address)
		observable.append_facets(facet_email_address)
		
		self.bundle.append_to_uco_object(observable)
		return observable
		

	def __generateTraceFile(self, FILEpath, FILEsize, FILEhashType, 
		FILEHashValue, FILETag, FILEtimeC, FILEtimeM, FILEtimeA, FILElocalPath, 
		FILEiNode, FILEiNodeTimeM, FILEgid, FILEuid, FILEexifLatitudeRef, FILEexifLatitude, 
		FILEexifLongitudeRef, FILEexifLongitude, FILEexifAltitude, FILEexifMake, FILEexifModel):		
		head, tail = os.path.split(FILEpath)
		
		observable = ObjectObservable()

		tail = self.__cleanJSONtext(tail)
		path = FILEpath.replace('"', "").replace('\n', '').replace('\r', '')
		path = path.replace("\\", "/")
		
		dotPos = tail.find('.')
		if dotPos > -1:
			sExt = tail[dotPos:]
		else:
			sExt = ''
		
		if FILEHashValue.upper() == 'N/A':
			FILEHashValue = UFEDtoJSON.HASH_V

		if FILEHashValue.strip() == '':
				FILEHashValue = UFEDtoJSON.HASH_V

		if FILEhashType.strip() == '':
			FILEhashType = UFEDtoJSON.HASH_M

		if FILEhashType.upper() == '_NOT_PROVIDED_':
			FILEhashType = UFEDtoJSON.HASH_M	

		if FILETag.upper() == '_NOT_PROVIDED_':
			FILETag = 'Uncategorized';			
		
#--- Replace all not number occurrences with nothing
#		
		FILEsize = re.sub('[^0-9]','', FILEsize)
		if FILEsize.strip() == '':
			FILEsize = int(UFEDtoJSON.INT)
		else:
			FILEsize = int(FILEsize)
			
		if FILEHashValue != UFEDtoJSON.HASH_V: 
			facet_content = ContentData(hash_method=FILEhashType, hash_value=FILEHashValue)
			observable.append_facets(facet_content)

		FILEtimeC = self.__cleanDate(FILEtimeC)
		FILEtimeM = self.__cleanDate(FILEtimeM)
		FILEtimeA = self.__cleanDate(FILEtimeA)			
		FILEiNodeTimeM = self.__cleanDate(FILEiNodeTimeM)

		FILEiNode = FILEiNode.strip()
		if FILEiNode.strip() == '':
			FILEiNode = UFEDtoJSON.INT	
		
		if FILEiNode.find('0x') > - 1:
			FILEiNode = int(FILEiNode, 16)
		else:
			FILEiNode = int(FILEiNode)

		FILEuid = FILEuid.strip()
		if FILEuid.strip() == '':
			FILEuid = UFEDtoJSON.INT	

		if FILEuid.find('0x') > - 1:
			FILEuid = int(FILEuid, 16)
		else:
			FILEuid = int(FILEuid)

		FILEgid = FILEgid.strip()
		if FILEgid.strip() == '':
			FILEgid = UFEDtoJSON.INT

		if FILEgid.find('0x') > - 1:
			FILEgid = int(FILEgid, 16)
		else:
			FILEgid = int(FILEgid)
		
		localPath = FILElocalPath.replace('"', "").replace('\n', '').replace('\r', '')
		localPath = localPath.replace("\\", "/")
		
		if FILEexifLatitude.strip() != '':	
			exif_data = {"Make":FILEexifMake, 
				"Model":FILEexifModel, "LatitudeRef":FILEexifLatitudeRef,
				"Latitude":FILEexifLatitude, "LongitudeRef":FILEexifLongitudeRef,
				"Longitude":FILEexifLongitude, "Altitude":FILEexifAltitude}		
			facet_exif = EXIF(**exif_data)
			observable.append_facets(facet_exif)

		facet_ext_inode = ExtInode(inode_change_time=FILEiNodeTimeM, 
			inode_id=FILEiNode, sgid=FILEgid, suid=FILEuid)
		observable.append_facets(facet_ext_inode) 
		
		facet_file = File(tag=FILETag, file_name=tail, 
			file_path=path, file_local_path=localPath, file_extension=sExt,
                 size_bytes=FILEsize, accessed_time=FILEtimeA, created_time=FILEtimeC, 
                 modified_time=FILEtimeM)
		observable.append_facets(facet_file) 

		self.bundle.append_to_uco_object(observable)

		return observable


	def __generateTraceIdentity(self, name, family_name, birthDate):		
		
		if birthDate:
			birthDate = self.__cleanDate(birthDate)
		
		observable = ObjectObservable(object_class="uco-identity:Person")
		facet_identity = SimpleName(given_name=name, 
			family_name=family_name)
		observable.append_facets(facet_identity)
		self.bundle.append_to_uco_object(observable)
		return observable

	def __generateTraceLocationDevice(self, loc_id, loc_status, 
					loc_longitude, loc_latitude, loc_elevation,
					loc_timeStamp, loc_category, item):
		
		#location_timeStamp = self.__cleanDate(loc_timeStamp)
		uuidLocation = self.__checkGeoCoordinates(loc_latitude, loc_longitude, loc_elevation, loc_category)

		return uuidLocation

	def __generateTracePhoneAccount(self, source, name, phone_num):		
		
		observable_identity = None
		if source != "":
			observable_identity = ObjectObservable(object_class="uco-identity:Organization")
			facet_identity = SimpleName(given_name="-" + source)
			observable_identity.append_facets(facet_identity)
			self.bundle.append_to_uco_object(observable_identity)

		observable = ObjectObservable()
		facet_account = Account(identifier=name, issuer_id=observable_identity)
		facet_phone_account = PhoneAccount(phone_number=phone_num, 
			account_name=name)
		observable.append_facets(facet_account, facet_phone_account)
		self.bundle.append_to_uco_object(observable)

		return observable


	def __generateTraceInvestigativeAction(self, name, description, start_time, end_time, 
		object_instrument, str_location, object_performer, object_input, 
		object_list_result):

		start_time = self.__cleanDate(start_time)
		end_time = self.__cleanDate(end_time)
		
		object_location = self.__generateTraceLocation(str_location)
#---	to be deleted
#		
		investigation = InvestigativeAction(
			name=description, start_time=start_time, end_time=end_time,
			performer=object_performer, instrument=object_instrument, 
			location=object_location, objects=object_input, results=object_list_result)

		#investigation.append_facets(facet_action_ref)
		self.bundle.append_to_uco_object(investigation)

	
	def __generateTracePhoneCall(self, direction, startTime, idFROM, idTO, 
								duration, status, outcome):
		nTime = 0
		if duration != "":
			aTime = duration.split(":")
			if len(aTime) == 3:
				if aTime[2].find('.') > -1:
					aTime[2] = aTime[2][0:aTime[2].find('.')]
				if aTime[2].find(',') > -1:
					aTime[2] = aTime[2][0:aTime[2].find(',')]

				nTime = int(aTime[0])*3600 + int(aTime[1])*60 + int(aTime[2])
			if len(aTime) == 2:
				nTime = int(aTime[0])*60 + int(aTime[1]) 
			if len(aTime) == 1:
				nTime = int(aTime[0]) 
		duration = str(nTime)
		duration = duration.lstrip('0')
		if duration == "":
			duration = "0"
		
		point = duration.find('.') 
		if point > - 1:
			duration = duration[0:point]
		
		duration = int(duration)
		observable_app = self.__checkAppName("Native")
		observable = ObjectObservable()
		startTime = self.__cleanDate(startTime)
		facet_call = Call(call_type=direction,
			start_time=startTime, application=observable_app, call_from=idFROM, 
			call_to=idTO, call_duration=duration, allocation_status=status)		
		observable.append_facets(facet_call)

		self.bundle.append_to_uco_object(observable)
		return observable


	def __generateTracePhoneOwner(self, source, name, phone_num):
				
		observable_identity = None
		if source != '':
			observable_identity = ObjectObservable(object_class="uco-identity:Person")
			facet_identity = SimpleName(given_name="(Owner) " + source)
			observable_identity.append_facets(facet_identity)
			self.bundle.append_to_uco_object(observable_identity)


		observable = ObjectObservable()
		facet_account = Account(identifier=name, issuer_id=observable_identity)
		name += ' (Owner)'
		facet_phone_account = PhoneAccount(phone_number=phone_num, 
			account_name=name)
		observable.append_facets(facet_account, facet_phone_account)
		self.bundle.append_to_uco_object(observable)

		
		self.object_phone_owner = observable
		self.phoneNumberList.append(phone_num)
		self.phoneUuidList.append(self.object_phone_owner)

	def __generateTraceProvencance(self, uco_core_objects, description, 
		exhibitNumber, creationTime):
		
		case_provenance = ProvenanceRecord(exhibit_number=exhibitNumber, 
			uco_core_objects=uco_core_objects)
		
		self.bundle.append_to_uco_object(case_provenance)
		return case_provenance

	def __generateTraceRelation(self, source, target, relation, table, offset,
		start_date, end_date):
		
		if isinstance(start_date, str):
			start_date = self.__cleanDate(start_date)

		if isinstance(end_date, str):
			end_date = self.__cleanDate(end_date)
		
		observable_relationship = Relationship(source=source, target=target, 
			start_time=start_date, end_time=end_date, kind_of_relationship=relation, 
			directional=True)
		self.bundle.append_to_uco_object(observable_relationship)

		return observable_relationship

	def __generateTraceRole(self, role):
		
   
		object_role = Role(name=role)

		self.bundle.append_to_uco_object(object_role)
		return object_role

	def __generateTraceSocialMedia_Item(self, sm_item_id, sm_status, 
					sm_source, sm_timeStamp, sm_body,
					sm_title, sm_url, sm_identifier, sm_name, sm_reactionsCount, 
					sm_sharesCount, sm_activityType, sm_commentCount, sm_account):

		if sm_source.strip() != '': 
			observable_app = self.__checkAppName(sm_source.strip())
		else:
			observable_app = None		

		sm_timeStamp = self.__cleanDate(sm_timeStamp)
		sm_title = self.__cleanJSONtext(sm_title)
		sm_body = self.__cleanJSONtext(sm_body)
		sm_url = self.__cleanJSONtext(sm_url)
		
		if sm_url != '':
			observable_url = self.__checkUrlAddress(sm_url)
		else:
			observable_url = None

		if (sm_body == '' and sm_source.strip() == ''):
			return None

		observable = ObjectObservable()

		facet_social_media_activity = SocialMediaActivity(
			application=observable_app, created_time=sm_timeStamp, body=sm_body, 
			page_title=sm_title, url=observable_url, author_id=sm_identifier,
                 author_name=sm_name, reactions_count=sm_reactionsCount, 
                 shares_count=sm_sharesCount, activity_type=sm_activityType, 
                 comment_count=sm_commentCount, account_id=sm_account)
		observable.append_facets(facet_social_media_activity)

		self.bundle.append_to_uco_object(observable)
		return observable				

	def __generateTraceSearched_Item(self, search_id, search_status, 
					search_app, search_timestamp, search_value, search_result):
		
		search_value = self.__cleanJSONtext(search_value)		
		if search_value.strip() == '' and search_result.strip() == '':
			return None
		
		search_result = self.__cleanJSONtext(search_result)
		search_timestamp = self.__cleanDate(search_timestamp)
		if not self.__checkSearchedItems(search_value + str(search_timestamp)):
			return None		
		
		observable_app = self.__checkAppName(search_app)

		observable = ObjectObservable()
		
		facet_searched_item = SearchedItem(
		search_value=search_value, search_result=search_result, application=observable_app, 
		search_launch_time=search_timestamp)
		observable.append_facets(facet_searched_item)
		
		self.bundle.append_to_uco_object(observable)
		return observable

	def __generateTraceWireless_Net(self, wnet_id, wnet_status, wnet_ssid, wnet_bssid):
		wnet_id = wnet_bssid.strip() + '@' + wnet_ssid.strip()
		if wnet_id == '@':
			return None
		else:
			if wnet_id in self.WIRELESS_NET_ACCESS.keys():
				observable = self.WIRELESS_NET_ACCESS.get(wnet_id)
			else:									
				observable = ObjectObservable()
				facet_wnet_connection = WirelessNetworkConnection(
					ssid=wnet_ssid, base_station=wnet_bssid)
				observable.append_facets(facet_wnet_connection)
				self.bundle.append_to_uco_object(observable)
				self.WIRELESS_NET_ACCESS[wnet_id] = observable
			return observable


	def __generateTraceMessageFacet(self, body, id_app, phone_uuid_from, phone_uuid_to, 
			time_stamp, status, type):

		time_stamp = self.__cleanDate(time_stamp)
		body = self.__cleanJSONtext(body)

		if body.strip() == ''  	and \
			phone_uuid_to == '' and \
			phone_uuid_from == '' :
			return ''
		
		observable_message = ObjectObservable(object_class="uco-observable:Message")

		facet_message = Message(msg_to=phone_uuid_to, 
			msg_from=phone_uuid_from, message_text=body, sent_time=time_stamp,
	                 application=id_app, message_type=type)
		observable_message.append_facets(facet_message)
		
		self.bundle.append_to_uco_object(observable_message)
		return observable_message

	def __generateTraceSmsMessageFacet(self, body, id_app, phone_uuid_from, phone_uuid_to, 
			time_stamp, status):

		time_stamp = self.__cleanDate(time_stamp)
		body = self.__cleanJSONtext(body)

		if body.strip() == ''  	and \
			phone_uuid_to == '' and \
			phone_uuid_from == '' :
			return ''
		
		observable = ObjectObservable()

		facet_message = SmsMessage(msg_to=phone_uuid_to, 
			msg_from=phone_uuid_from, message_text=body, sent_time=time_stamp,
	                 application=id_app)
		observable.append_facets(facet_message)
		
		self.bundle.append_to_uco_object(observable)
		return observable		


	def __generateTraceSms(self, SMSid, SMSstatus, SMStimeStamp, 
							SMSpartyRoles, SMSpartyIdentifiers, 
							SMSsmsc, SMSpartyNames, SMSfolder, SMSbody, SMSsource):		
		
		for i, sms_id in enumerate(SMSid):
			phone_observable_to = []
			phone_observable_from = None
			for j, sms_party_identifier in enumerate(SMSpartyIdentifiers[i]):				
				if sms_party_identifier.strip() != '':
					if sms_party_identifier in self.phoneNumberList:						
						idx = self.phoneNumberList.index(sms_party_identifier)						
						#userId = self.phoneNumberList[idx]
						phone_party_observable = self.phoneUuidList[idx]
					else:
						self.phoneNumberList.append(sms_party_identifier)
						self.phoneNameList.append(SMSpartyNames[i][j])
						mobileOperator = ""
						phone_party_observable = self.__generateTracePhoneAccount(mobileOperator, 
							SMSpartyNames[i][j], sms_party_identifier)	
						self.phoneUuidList.append(phone_party_observable)
				
					if SMSpartyRoles[i][j] == 'To':
						phone_observable_from = self.object_phone_owner
						phone_observable_to.append(phone_party_observable)
					else:
						phone_observable_from = phone_party_observable
						phone_observable_to.append(self.object_phone_owner)
			
			phone_smsc_observable = None			
			if SMSsmsc[i].strip() != '':
				if SMSsmsc[i].strip() in self.phoneNumberList:						
					idx = self.phoneNumberList.index(SMSsmsc[i].strip())						
					#userId = self.phoneNumberList[idx]
					phone_smsc_observable = self.phoneUuidList[idx]
				else:
					self.phoneNumberList.append(SMSsmsc[i].strip())
					self.phoneNameList.append('SMSC')
					mobileOperator = ""
					phone_smsc_observable = self.__generateTracePhoneAccount(mobileOperator, 
						'SMSC', SMSsmsc[i].strip())	
					self.phoneUuidList.append(phone_smsc_observable)

			if SMSfolder[i] == 'Inbox':
				if phone_observable_from is None:
					phone_observable_from = phone_smsc_observable
			else:
				if phone_observable_to == []:
					phone_observable_to = phone_smsc_observable	

			# if self.object_phone_owner is not None:
			# 	if phone_observable_to is not self.object_phone_owner:
			# 		phoneUuidTo = phoneUuidTo[0:-1]

			body = self.__cleanJSONtext(SMSbody[i])
			
#---	the xsd:dateTime has the structure YYYY-MM-DDTHH:MM:SS (UTCxxx
#		the character "/" is not allowed
#		
			SMStimeStamp[i] = self.__cleanDate(SMStimeStamp[i])

			id_app_name = self.__checkAppName("Native")

			#direction = ''
			observable_message = self.__generateTraceSmsMessageFacet(body, id_app_name, 
				phone_observable_from, phone_observable_to, SMStimeStamp[i], SMSstatus[i])

			if observable_message is not None:
				self.__generateChainOfEvidence(sms_id, observable_message)

	def __generateThreadMessages(self, chatTraceId, chat_messages, chat_participants):		
		observable = ObjectObservable()		
		facet_message_thread = Messagethread(messages=chat_messages, 
			participants=chat_participants, display_name=str(chatTraceId))		
		observable.append_facets(facet_message_thread)
		self.bundle.append_to_uco_object(observable)
		return observable

	def __generateTraceTool(self, name, type, creator, version, confList):		
		observable_identity = ObjectObservable(object_class="uco-identity:Person")
		facet_identity = SimpleName(family_name=creator)
		observable_identity.append_facets(facet_identity)
		self.bundle.append_to_uco_object(observable_identity)		
		
		object_tool = Tool(name, version, tool_type=type, tool_creator=observable_identity)
		self.bundle.append_to_uco_object(object_tool)
		return object_tool

	def __generateTraceURLFullValue(self, URL_Value):
		
		observable = ObjectObservable()
		facet_url = Url(url_address=URL_Value)
		
		observable.append_facets(facet_url)
		self.bundle.append_to_uco_object(observable)
		return observable

	def __generateTraceURL(self, URL_Value):
		
		URL_Value = self.__cleanJSONtext(URL_Value)
		startHttp = URL_Value.strip().find('http')
		
		if startHttp > - 1:
			URL_Value = URL_Value[startHttp:]

		uuid = self.__checkUrlAddress(URL_Value)
				
		return uuid

	def __generateTraceLocation(self, Location):				
		"""
#---	to be included in case_builder classes
		Location = Location.strip()
		if Location in self.LocationList: 
					idx = self.LocationList.index(Location)
					uuid = self.LocationIDList[idx]
		else:
			uuid = "kb:" + UFEDtoJSON.__createUUID()
			self.LocationList.append(Location)
			self.LocationIDList.append(uuid)
			object_dict = {
				"@id":uuid,
				"@type":"uco-location:Location", 
				"uco-core:hasFacet":[
					{
						"@type":"uco-location:SimpleAddressFacet", 
						"uco-location:locality":Location
					}
				]
			}

			object_str = json.dumps(object_dict, indent = 4)
			self.FileOut.write(object_str + ',\n')
		
		return uuid
		"""		

	def __generateTraceLocationCoordinate (self, latitude, longitude, altitude, type):

		observable = ObjectObservable()
		id = latitude + '@' + longitude
		self.LOCATION_lat_long_coordinate[id] = observable

		latitude_decimal = float(latitude)
		longitude_decimal = float(longitude)
		
		if altitude != '':
			altitude_decimal = float(altitude)
		else:
			altitude_decimal = 0.00 

		facet_location = Location(latitude=latitude_decimal, 
			longitude=longitude_decimal, altitude=altitude_decimal)
		observable.append_facets(facet_location)
		
		self.bundle.append_to_uco_object(observable)
		return observable

	def __generateTraceWebPages(self, WEB_PAGEid, WEB_PAGEstatus, WEB_PAGEsource, WEB_PAGEurl, 
				WEB_PAGEtitle, WEB_PAGEvisitCount,  WEB_PAGElastVisited):
		"""
			URLHistoryFacet and urlHistoryEntry
		"""
		for i, web_page_id in enumerate(WEB_PAGEid):						
			WEB_PAGElastVisited[i] = self.__cleanDate(WEB_PAGElastVisited[i])
			observable_app = self.__checkAppName(WEB_PAGEsource[i].strip())
			observable_url = self.__generateTraceURL(WEB_PAGEurl[i])
			title = self.__cleanJSONtext(WEB_PAGEtitle[i])
			
			if WEB_PAGEvisitCount[i].strip() == '':
				visit_count = '0' 
			else:
				visit_count = WEB_PAGEvisitCount[i]

			visit_count = int(visit_count)

			observable = ObjectObservable()
			facet_url_history_entry = UrlHistoryEntry(
				last_visit=WEB_PAGElastVisited[i], url=observable_url, page_title=title, 
				visit_count=visit_count, allocation_status=WEB_PAGEstatus[i], browser=observable_app)			
			#facet_url_history = UrlHistory(browser=observable_app)
			observable.append_facets(facet_url_history_entry)
			
			self.bundle.append_to_uco_object(observable)			
			self.__generateChainOfEvidence(web_page_id, observable)

	def writeExtraInfo(self, EXTRA_INFOdictPath, EXTRA_INFOdictSize, EXTRA_INFOdictTableName, 
				EXTRA_INFOdictOffset, EXTRA_INFOdictNodeInfoId):
#---	this data are necessary, in some circumstances, to build up the Chain of Evidence		
#	
		self.EXTRA_INFOdictPath = EXTRA_INFOdictPath
		self.EXTRA_INFOdictSize = EXTRA_INFOdictSize
		self.EXTRA_INFOdictTableName = EXTRA_INFOdictTableName
		self.EXTRA_INFOdictOffset = EXTRA_INFOdictOffset
		self.EXTRA_INFOdictNodeInfoId = EXTRA_INFOdictNodeInfoId		

	def writeContact(self, CONTACTid, CONTACTstatus, CONTACTsource, 
            CONTACTname, CONTACTuserIds, CONTACTphoneNums, CONTACTaccount):
		for i, contact in enumerate(CONTACTid):
			for j, phoneNum in enumerate(CONTACTphoneNums[i]):
				if phoneNum.strip() != '':
					self.__checkPhoneNumber(phoneNum.strip(), CONTACTname[i])
			
			#if 	CONTACTaccount[i].strip() != '':				
				#self.__checkAccountName(CONTACTaccount[i], CONTACTname[i], idApp)
			if CONTACTuserIds[i][0].strip() != '':
				idApp = self.__checkAppName(CONTACTsource[i])
				self.__checkAccountName(CONTACTuserIds[i][0].strip(), CONTACTname[i], idApp)
					

	def writeHeader(self):
		if self.bundle is None:
			self.bundle = Bundle()
			observable_info=ObjectInfo(name="D.F. Expert", version="CASE 1.3.0", description="Extraction from UFED PA XML report")
			self.bundle.append_to_uco_object(observable_info)

	def writeLastLine(self):
#---	Save a reference to the original standard output			
		original_stdout = sys.stdout 

#--	Change the standard output to the file we created.    		
		sys.stdout = self.FileOut 
		
		print(self.bundle)

#--	Restore the standard output to its default value
		sys.stdout = original_stdout 

	def writePhoneOwner(self, phoneOwnerNumber):
		self.phoneOwnerNumber = phoneOwnerNumber
		mobileOperator = ""
		mobileOwnerName = ""
		self.__generateTracePhoneOwner(mobileOperator, mobileOwnerName, phoneOwnerNumber)

	def writeFiles(self, FILEid, FILEpath, FILEsize, FILEmd5, FILETag, 
					FILEtimeCreate, FILEtimeModify, FILEtimeAccess, FILElocalPath, 
                    FILEiNodeNumber, FILEiNodeTimeM, FILEownerGID, FILEownerUID,
                    FILEexifLatitudeRef, FILEexifLatitude, FILEexifLongitudeRef,
                    FILEexifLongitude, FILEexifAltitude, FILEexifMake, FILEexifModel):
			self.FILEid = FILEid
			for i, file_id in enumerate(FILEid):					
				object_file = self.__generateTraceFile(FILEpath[i], FILEsize[i], 
					'MD5', FILEmd5[i],	FILETag[i], FILEtimeCreate[i], FILEtimeModify[i], 
					FILEtimeAccess[i], FILElocalPath[i], FILEiNodeNumber[i], FILEiNodeTimeM[i],
					FILEownerGID[i], FILEownerUID[i], FILEexifLatitudeRef[i], 
					FILEexifLatitude[i], FILEexifLongitudeRef[i], FILEexifLongitude[i], 
					FILEexifAltitude[i], FILEexifMake[i], FILEexifModel[i])

				self.FILEuuid[file_id] = object_file
				self.FILEpath[file_id] = FILEpath[i]

				
	def writeWebBookmark(self, WEB_BOOKMARKid, WEB_BOOKMARKsource, WEB_BOOKMARKtimeStamp,
	    WEB_BOOKMARKpath, WEB_BOOKMARKurl):
		for i, wb_id in enumerate(WEB_BOOKMARKid):
			observable_web_bookmark = self.__generateTraceWebBookmark(wb_id, WEB_BOOKMARKsource[i],
			                            WEB_BOOKMARKtimeStamp[i], WEB_BOOKMARKpath[i], WEB_BOOKMARKurl[i])
			
			if observable_web_bookmark:
				pass
				#self.__generateTraceRelation(self.DEVICE_object, observable_bluetooth, 
				                     #'Connected_To', None, None, None, None)			
				#self.__generateChainOfEvidence(bt_id, observable_bluetooth)
		
	def writeBluetooth(self, BLUETOOTHid, BLUETOOTHstatus, BLUETOOTHvalues):
				
		for i, bt_id in enumerate(BLUETOOTHid):
			observable_bluetooth = self.__generateTraceBluetooth(bt_id, 
					BLUETOOTHstatus[i], BLUETOOTHvalues[i])
			
			if observable_bluetooth:
				self.__generateTraceRelation(self.DEVICE_object, observable_bluetooth, 
					                     'Connected_To', None, None, None, None)			
			self.__generateChainOfEvidence(bt_id, observable_bluetooth)
			
	def writeCalendar(self, CALENDARid, CALENDARstatus, CALENDARcategory, CALENDARsubject,
                    CALENDARdetails, CALENDARstartDate, CALENDARendDate, CALENDARrepeatUntil, 
                    CALENDARrepeatDay, CALENDARrepeatInterval):
		
		for i, calendar_id in enumerate(CALENDARid):
			observable_calendar = self.__generateTraceCalendar(calendar_id, 
					CALENDARstatus[i], CALENDARcategory[i], CALENDARsubject[i], 
					CALENDARdetails[i], CALENDARstartDate[i], CALENDARendDate[i], 
					CALENDARrepeatUntil[i], CALENDARrepeatDay[i], CALENDARrepeatInterval[i])
			
			self.__generateChainOfEvidence(calendar_id, observable_calendar)					

	def writeCell_Site(self, CELL_SITEid, CELL_SITEstatus, CELL_SITElongitude, 
					CELL_SITElatitude, CELL_SITEtimeStamp, CELL_SITEmcc,
                    CELL_SITEmnc, CELL_SITElac, CELL_SITEcid, CELL_SITEnid, 
                    CELL_SITEbid, CELL_SITEsid):
		
		for i, cell_site_id in enumerate(CELL_SITEid):
			observable_cell_site = self.__generateTraceCell_Site(cell_site_id, CELL_SITEstatus[i], 
					CELL_SITElongitude[i], CELL_SITElatitude[i], CELL_SITEtimeStamp[i], 
					CELL_SITEmcc[i], CELL_SITEmnc[i], CELL_SITElac[i], CELL_SITEcid[i], 
					CELL_SITEnid[i], CELL_SITEbid[i], CELL_SITEsid[i])
			
			if observable_cell_site is not None:				
				self.__generateTraceRelation(self.DEVICE_object, observable_cell_site, 
					'Connected_To', '', '', CELL_SITEtimeStamp[i], None)
				self.__generateChainOfEvidence(cell_site_id, observable_cell_site)							

	def writeChat(self, CHATid, CHATstatus, CHATsource, CHATpartyIdentifiers, CHATpartyNames, 
                CHATmsgIdentifiersFrom, CHATmsgNamesFrom, CHATmsgBodies, CHATmsgStatuses, CHATmsgOutcomes,
                CHATmsgTimeStamps, CHATmsgAttachmentFilenames, CHATmsgAttachmentUrls):		

		for i, chat_id in enumerate(CHATid):			
			appSource = CHATsource[i].strip().lower()
			idAppIdentity = self.__checkAppName(appSource)
			
			CHATid_account_to = []
			CHATid_account_from = ''
#---	if the CHAT doesn't have Participants, it is disregarded
#
			if  len(CHATpartyIdentifiers) <= i:
				continue
			
			if len(CHATpartyIdentifiers[i]) == 0:
				continue

			for j, chat_party_id in enumerate(CHATpartyIdentifiers[i]):	
				idChatAccount = self.__checkChatParticipant(chat_party_id, 
					CHATpartyNames[i][j], CHATsource[i], idAppIdentity)				
#---	in the account_to list, also the CHATmsgIdentifiersFrom is added 					
#						
				CHATid_account_to.append(idChatAccount)			
			
			CHATthread = []
#---	CHATmsgBodies[i] is the list of the messages of the same thread, 
#		the j index iterates over all the messages within the i-th CHAT 
#			
			for j, chat_msg_body in enumerate(CHATmsgBodies[i]):	

				CHATmsgFrom = CHATmsgIdentifiersFrom[i][j].strip()
				if len(CHATmsgIdentifiersFrom[i]) > 0:
					CHATid_account_from = self.__checkChatParticipant(CHATmsgFrom,
						CHATmsgNamesFrom[i][j], CHATsource[i], idAppIdentity)	
				else:
					CHATid_account_from = self.__checkChatParticipant('MSG_IDENTIFIER_EMPTY',
						'MSG_NAME_EMPTY', CHATsource[i], idAppIdentity)				

				chat_observable = self.__generateTraceChat(chat_msg_body, idAppIdentity, 
					CHATmsgTimeStamps[i][j], CHATid_account_from, CHATid_account_to, 
					CHATmsgStatuses[i][j], CHATmsgOutcomes[i][j],
					'', CHATmsgAttachmentFilenames[i][j], 
					CHATmsgAttachmentUrls[i][j])

				CHATthread.append(chat_observable)
				if CHATmsgAttachmentFilenames[i][j].strip() != '':
					CHATattachmentFiles = CHATmsgAttachmentFilenames[i][j].split('###')
					for idx, chat_attachment_file in enumerate(CHATattachmentFiles):
						for key in self.FILEpath:						
							if self.FILEpath[key].find(chat_attachment_file) > - 1:
								self.__generateTraceRelation(self.FILEuuid[key], 
									chat_observable, 'Attached_To', '', '', None, None);
								break			

#---	if there are not messages for this Chat or no ChatAccount has been generated, 
#		the ThreadMessage is skipped and the Chain of evidence is ignored 
#			
			if (len(CHATthread) == 0) or (len(CHATid_account_to) == 0):
				pass
			else:
				uuidThread = self.__generateThreadMessages(chat_id, CHATthread, 
								CHATid_account_to)
				self.__generateChainOfEvidence(chat_id, uuidThread)

	def writeCookie(self, COOKIEid, COOKIEstatus, COOKIEsource, COOKIEname,
                    COOKIEvalue, COOKIEdomain, COOKIEcreationTime, COOKIElastAccessTime, 
                    COOKIEexpiry):
		for i, cookie_id in enumerate(COOKIEid):
			observable_cookie = self.__generateTraceCookie(cookie_id, COOKIEstatus[i], 
					COOKIEsource[i], COOKIEname[i], COOKIEvalue[i], 
					COOKIEdomain[i], COOKIEcreationTime[i], COOKIElastAccessTime[i], 
					COOKIEexpiry[i])
			
			self.__generateChainOfEvidence(cookie_id, observable_cookie)

	def writeInstalledApp(self, INSTALLED_APPid, INSTALLED_APPstatus, 
            INSTALLED_APPname, INSTALLED_APPversion , INSTALLED_APPidentifier, INSTALLED_APPpurchaseDate):

		for i, app_id in enumerate(INSTALLED_APPid):
			observable_app = self.__generateTraceInstalledApp(app_id, 
			    INSTALLED_APPstatus[i], INSTALLED_APPname[i], 
		        INSTALLED_APPversion[i], INSTALLED_APPidentifier[i], INSTALLED_APPpurchaseDate[i])

			if observable_app:
				self.__generateChainOfEvidence(app_id, observable_app)
		
	def writeDeviceEvent(self, DEVICE_EVENTid, DEVICE_EVENTstatus, 
                    DEVICE_EVENTtimeStamp, DEVICE_EVENTeventType, DEVICE_EVENTvalue):

		for i, device_event_id in enumerate(DEVICE_EVENTid):
			observable_event = self.__generateTraceDeviceEvent(device_event_id, 
					DEVICE_EVENTstatus[i], DEVICE_EVENTtimeStamp[i], 
					DEVICE_EVENTeventType[i], DEVICE_EVENTvalue[i])
			
			self.__generateChainOfEvidence(device_event_id, observable_event)

	def writeEmail(self, EMAILid, EMAILstatus, EMAILsource, EMAILidentifierFROM, 
				EMAILidentifiersTO, EMAILidentifiersCC, EMAILidentifiersBCC, 
                EMAILbody, EMAILsubject, EMAILtimeStamp, EMAILattachmentsFilename):
		for i, email_id in enumerate(EMAILid):
			self.__generateTraceEmail(email_id, EMAILstatus[i], EMAILsource[i],
				EMAILidentifierFROM[i], EMAILidentifiersTO[i], 
				EMAILidentifiersCC[i], EMAILidentifiersBCC[i], EMAILbody[i], 
				EMAILsubject[i], EMAILtimeStamp[i], EMAILattachmentsFilename[i])


	def writeInstantMessage(self, INSTANT_MSGid, INSTANT_MSGstatus, INSTANT_MSGsource, 
			INSTANT_MSGtimeStamp, INSTANT_MSGfromIdentifier, INSTANT_MSGfromName,
            INSTANT_MSGtoIdentifier, INSTANT_MSGtoName, INSTANT_MSGsubject, INSTANT_MSGbody, 
            INSTANT_MSGfolder, INSTANT_MSGtype, INSTANT_MSGapplication):
		
		for i, i_msg_id in enumerate(INSTANT_MSGid):			
			if INSTANT_MSGsource[i].find('Native') > -1:
				idx = self.appNameList.index("Native")
				observable_app = self.appObjectList[idx]
			else:
				if INSTANT_MSGsource[i].strip() in self.appNameList: 
					idx = self.appNameList.index(INSTANT_MSGsource[i].strip())
					observable_app = self.appObjectList[idx]
				else:
					observable_app = self.__generateTraceAppName(INSTANT_MSGsource[i].strip())
					self.appNameList.append(INSTANT_MSGsource[i].strip())
					self.appObjectList.append(observable_app)	

			i_msg_from_identifier = INSTANT_MSGfromIdentifier[i].strip()
			
			observable_from = None
			if  i_msg_from_identifier != '' :
				if i_msg_from_identifier in self.phoneNumberList:						
					idx = self.phoneNumberList.index(i_msg_from_identifier)
					observable_from = self.phoneUuidList[idx]
				else:
					self.phoneNumberList.append(i_msg_from_identifier)
					self.phoneNameList.append(INSTANT_MSGfromName[i])
					mobileOperator = ""
					observable_from = self.__generateTracePhoneAccount(mobileOperator, 
							INSTANT_MSGfromName[i], i_msg_from_identifier)	
					self.phoneUuidList.append(observable_from)
			
			list_TO = INSTANT_MSGtoIdentifier[i].split('@@@')
			observables_msg_to = []
			for j, item in enumerate(list_TO):
				if item.strip() != '':
					if item in self.phoneNumberList:						
						idx = self.phoneNumberList.index(item.strip())
						observable_to = self.phoneUuidList[idx]												
					else:
						self.phoneNumberList.append(item.strip())
						self.phoneNameList.append(INSTANT_MSGtoName[i])
						mobileOperator = ""
						observable_to = self.__generateTracePhoneAccount(mobileOperator, 
						INSTANT_MSGtoName[i], item.strip())	
						self.phoneUuidList.append(observable_to)
					observables_msg_to.append(observable_to)
						
			observable_message = self.__generateTraceMessageFacet(INSTANT_MSGbody[i], 
				observable_app, observable_from, observables_msg_to, INSTANT_MSGtimeStamp[i], 
				INSTANT_MSGstatus[i], 'Instant Message')			
			
			if observable_message is not None:
				self.__generateChainOfEvidence(i_msg_id, observable_message)

	def writeLocationDevice(self, LOCATIONid, LOCATIONstatus, LOCATIONlongitude, 
					LOCATIONlatitude, LOCATIONaltitude, LOCATIONtimeStamp, 
					LOCATIONcategory):
		    
		for i, location_id in enumerate(LOCATIONid):
			observable_location= self.__generateTraceLocationDevice(location_id, LOCATIONstatus[i], 
					LOCATIONlongitude[i], LOCATIONlatitude[i], LOCATIONaltitude[i],
					LOCATIONtimeStamp[i], LOCATIONcategory[i], i)
			
			if observable_location is not None:
				self.__generateTraceRelation(self.DEVICE_object, observable_location, 
					'Mapped_By', '', '', LOCATIONtimeStamp[i], None)
				self.__generateChainOfEvidence(location_id, observable_location)


	def writeSocial_Media(self, SOCIAL_MEDIAid, SOCIAL_MEDIAstatus, 
            SOCIAL_MEDIAsource, SOCIAL_MEDIAtimeStamp, 
            SOCIAL_MEDIAbody, SOCIAL_MEDIAtitle, SOCIAL_MEDIAurl, SOCIAL_MEDIAidentifier, 
            SOCIAL_MEDIAname, SOCIAL_MEDIAreactionsCount, SOCIAL_MEDIAsharesCount,
            SOCIAL_MEDIAactivityType, SOCIAL_MEDIAcommentCount,
            SOCIAL_MEDIAaccount):

		for i, social_media_item_id in enumerate(SOCIAL_MEDIAid):
			observable_social= self.__generateTraceSocialMedia_Item(social_media_item_id, 
				SOCIAL_MEDIAstatus[i], SOCIAL_MEDIAsource[i], SOCIAL_MEDIAtimeStamp[i], 
				SOCIAL_MEDIAbody[i], SOCIAL_MEDIAtitle[i], SOCIAL_MEDIAurl[i], 
				SOCIAL_MEDIAidentifier[i], SOCIAL_MEDIAname[i], 
				SOCIAL_MEDIAreactionsCount[i], SOCIAL_MEDIAsharesCount[i],
				SOCIAL_MEDIAactivityType[i], SOCIAL_MEDIAcommentCount[i], 
				SOCIAL_MEDIAaccount[i])
			
			if observable_social is not None:
				self.__generateChainOfEvidence(social_media_item_id, observable_social)

	def writeSearched_Item(self, SEARCHED_ITEMid, SEARCHED_ITEMstatus, SEARCHED_ITEMsource, 
					SEARCHED_ITEMtimeStamp, SEARCHED_ITEMvalue, SEARCHED_ITEMsearchResult):
		
		for i, search_item_id in enumerate(SEARCHED_ITEMid):
			observable_searched_item = self.__generateTraceSearched_Item(search_item_id, 
				SEARCHED_ITEMstatus[i], SEARCHED_ITEMsource[i], SEARCHED_ITEMtimeStamp[i], 
				SEARCHED_ITEMvalue[i], SEARCHED_ITEMsearchResult[i])
			
			if observable_searched_item is not None:
				self.__generateChainOfEvidence(search_item_id, observable_searched_item)

	def writeWebPages(self, WEB_PAGEid, WEB_PAGEstatus, WEB_PAGEsource, WEB_PAGEurl, 
				WEB_PAGEtitle, WEB_PAGEvisitCount,  WEB_PAGlastVisited):
		self.__generateTraceWebPages(WEB_PAGEid, WEB_PAGEstatus, WEB_PAGEsource, WEB_PAGEurl, 
				WEB_PAGEtitle, WEB_PAGEvisitCount,  WEB_PAGlastVisited)

	def writeWireless_Net(self, WIRELESS_NETid, WIRELESS_NETstatus, WIRELESS_NETlongitude, 
					WIRELESS_NETlatitude, WIRELESS_NETtimeStamp, WIRELESS_NETlastConnection,
                    WIRELESS_NETbssid, WIRELESS_NETssid):
		
		for i, wireless_net_id in enumerate(WIRELESS_NETid):
			observable_wnet= self.__generateTraceWireless_Net(wireless_net_id, 
				WIRELESS_NETstatus[i], WIRELESS_NETbssid[i], WIRELESS_NETssid[i])
			
			if observable_wnet is not None:
				wnet_timeStamp = self.__cleanDate(WIRELESS_NETtimeStamp[i])
				wnet_last_connection = self.__cleanDate(WIRELESS_NETlastConnection[i])
				self.__generateTraceRelation(self.DEVICE_object, observable_wnet, 'Connected_To', 
					'', '', wnet_timeStamp, wnet_last_connection)				
				observable_location = self.__checkGeoCoordinates(WIRELESS_NETlatitude[i], WIRELESS_NETlongitude[i], '', 'Wireless Network')					
				if observable_location:
					self.__generateTraceRelation(observable_wnet, observable_location,
						'Mapped_To', '', '', None, None)								
				self.__generateChainOfEvidence(wireless_net_id, observable_wnet)

	def writeSms(self, SMSid, SMSstatus, SMStimeStamp, SMSpartyRoles,
					SMSpartyIdentifiers, SMSsmsc, SMSpartyNames, SMSfolder, SMSbody, SMSsource):
		self.__generateTraceSms(SMSid, SMSstatus, SMStimeStamp, SMSpartyRoles, 
					SMSpartyIdentifiers, SMSsmsc, SMSpartyNames, SMSfolder, SMSbody, SMSsource)

	def writeContextUfed(self, ufedVersionText, deviceReportCreateTime,
		deviceExtractionStartTime, deviceExtractionEndTime, examinerNameText,
		imagePath, imageSize, imageMetadataHashSHA, imageMetadataHashMD5):

		self.__generateContextUfed(ufedVersionText, deviceReportCreateTime,
			deviceExtractionStartTime, deviceExtractionEndTime, examinerNameText, 
			imagePath, imageSize, imageMetadataHashSHA, imageMetadataHashMD5)


