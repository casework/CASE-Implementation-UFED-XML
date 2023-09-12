#!/usr/bin/env python3
#---
#       parser_UFEDtoCASE:    
#               SAX parser for extracrtiong the main Artifacts from a UFED XML report
#

import xml.sax
import argparse
import os
import codecs
import UFEDtoJSON as CJ
import re
import timeit
from time import localtime, strftime
#import logging


class UFEDparser():
    '''
    It represents all attributes and methods to process the traces extracted from XML reports by using
    the SAX parser.
    '''    
    def __init__(self, report_xml=None, json_output=None, 
        base_local_path="", case_bundle=None, mode_verbose=False):
        '''
        It initialises the main attributes for processing the XML report.
            :param report_xml: The filename of the XML report, provided as argumnent in the command line (string).
            :param json_output: The filename of the JSO-LD to be generated, provided as argumnent in the command line (string).
            :param case_bundle: The container of all Objects in the JSON-LF file (list).
            :param mode_verbose: True if the processing progress will be shown in the standard output (boolean).
        '''        
        self.xmlReport = report_xml
        self.jsonCASE = json_output
        self.baseLocalPath = os.path.join(base_local_path, '') 
        # logging.basicConfig(filename='_ufed_chat.txt', level=logging.INFO,
        #     filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
        # #logging.basicConfig(filename='_ufed_log.txt', level=logging.INFO,
        #    filemode='w', format='%(message)s')
        self.bundle = case_bundle
        # it stores the start time of the processing
        self.tic_start = timeit.default_timer()
        self.verbose = mode_verbose

    def show_elapsed_time(self, tic, message):
        '''
        It shows the processing time gone.
            :param tic: The initial time for calculating the processing time passed (float).
            :param message: The message to be shown (string).
            :return: None.
        '''        
        toc = timeit.default_timer()
        C_CYAN = '\033[36m'
        C_BLACK = '\033[0m'
        elapsed_seconds = round(toc - tic, 2)
        (ss, ms) = divmod(elapsed_seconds, 1)
        elapsedMm = str(int(ss) // 60)
        elapsedSs = str(int(ss) % 60)
        elapsedMs = str(round(ms, 2))[2:]
        elapsed_time = "".join([elapsedMm, ' min. ', elapsedSs, ' sec. and ',  elapsedMs, ' hundredths'])
        if self.verbose:
            print("".join(['\n', C_CYAN, 'elapsed time - ', message, ': ', elapsed_time, '\n', C_BLACK]))

    def processXmlReport(self):
        '''
        It implements the SAX parser overriding the default ContextHandler method.
            :return: None.
        '''         
        SAXparser = xml.sax.make_parser()
        Handler = ExtractTraces(self.baseLocalPath, self.verbose)        
        Handler.createOutFile(self.jsonCASE)
        SAXparser.setContentHandler(Handler)
        SAXparser.parse(self.xmlReport)

        self.show_elapsed_time(self.tic_start, 'Extraction Traces')

        if self.verbose:
            print('\n\n\nCASE JSON-LD file is being generated ...')
        
        tic_case_start = timeit.default_timer()
        
        phoneNumber = Handler.findOwnerPhone(Handler.U_ACCOUNTusername).replace(' ', '')

        if phoneNumber == '':
            phoneNumber = Handler.CONTEXTdeviceMsisdnText.replace(' ', '')

        if self.verbose:
            print("".join([Handler.C_CYAN, "owner's phone number: ", phoneNumber, '\n', Handler.C_BLACK]))

        caseTrace = CJ.UFEDtoJSON(json_output=Handler.fOut, app_name=Handler.U_ACCOUNTsource, 
            app_user_name=Handler.U_ACCOUNTname, app_user_account=Handler.U_ACCOUNTusername, 
            case_bundle=self.bundle)

#---    caseTrace.storeUserAccount(Handler.U_ACCOUNTsource, Handler.U_ACCOUNTname,
#       Handler.U_ACCOUNTusername)        

        caseTrace.writeHeader()

        #tic_write = timeit.default_timer()
        caseTrace.writeDevice(Handler.CONTEXTdeviceIdText, Handler.CONTEXTdevicePhoneModelText,            
            Handler.CONTEXTdeviceOsTypeText, Handler.CONTEXTdeviceOsVersionText, 
            Handler.CONTEXTdevicePhoneVendorText, Handler.CONTEXTdeviceMacAddressText, 
            Handler.CONTEXTdeviceIccidText, Handler.CONTEXTdeviceImsiText, 
            Handler.CONTEXTdeviceImeiText, Handler.CONTEXTdeviceBluetoothAddressText, 
            Handler.CONTEXTdeviceBluetoothNameText)
        #self.show_elapsed_time(tic_write, 'Write DEVICE')

        caseTrace.writePhoneOwner(phoneNumber)

        caseTrace.writeExtraInfo(Handler.EXTRA_INFOdictPath, Handler.EXTRA_INFOdictSize,
                        Handler.EXTRA_INFOdictTableName, Handler.EXTRA_INFOdictOffset,
                        Handler.EXTRA_INFOdictNodeInfoId)

        #tic_write = timeit.default_timer()
        caseTrace.writeFiles(Handler.FILEid, Handler.FILEpath, Handler.FILEsize,
                        Handler.FILEmd5, Handler.FILEtags, Handler.FILEtimeCreate, 
                        Handler.FILEtimeModify, Handler.FILEtimeAccess, Handler.FILElocalPath, 
                        Handler.FILEiNodeNumber, Handler.FILEiNodeTimeModify, 
                        Handler.FILEownerGID, Handler.FILEownerUID, Handler.FILEexifLatitudeRef,
                        Handler.FILEexifLatitude, Handler.FILEexifLongitudeRef,
                        Handler.FILEexifLongitude, Handler.FILEexifAltitude, Handler.FILEexifMake,
                        Handler.FILEexifModel)        
        #self.show_elapsed_time(tic_write, 'Write FILES')


        #tic_write = timeit.default_timer()        
        caseTrace.writeContact(Handler.CONTACTid, Handler.CONTACTstatus, Handler.CONTACTsource, 
            Handler.CONTACTname, Handler.CONTACTuserIds, Handler.CONTACTphoneNums, 
            Handler.CONTACTaccount)       
        #self.show_elapsed_time(tic_write, 'Write CONTACT')
            
        #tic_write = timeit.default_timer()
        caseTrace.writeSms(Handler.SMSid, Handler.SMSstatus, Handler.SMStimeStamp, 
            Handler.SMSpartyRoles, Handler.SMSpartyIdentifiers, 
            Handler.SMSsmsc, Handler.SMSpartyNames, Handler.SMSfolder, 
            Handler.SMSbody, Handler.SMSsource)        
        #self.show_elapsed_time(tic_write, 'Write SMS')

        caseTrace.writeCall(Handler.CALLid, Handler.CALLstatus, Handler.CALLsource, 
            Handler.CALLtimeStamp, Handler.CALLdirection, Handler.CALLduration,
            Handler.CALLrolesTO, Handler.CALLrolesFROM, Handler.CALLnamesTO, 
            Handler.CALLnamesFROM, Handler.CALLoutcome, Handler.CALLidentifiersTO, 
            Handler.CALLidentifiersFROM)        
        #self.show_elapsed_time(tic_write, 'Write CALL')

        #tic_write = timeit.default_timer()
        caseTrace.writeBluetooth(Handler.BLUETOOTHid, Handler.BLUETOOTHstatus, Handler.BLUETOOTHvalues)
        #self.show_elapsed_time(tic_write, 'Write CALENDAR')
        
        #tic_write = timeit.default_timer()
        caseTrace.writeCalendar(Handler.CALENDARid, Handler.CALENDARstatus, 
            Handler.CALENDARcategory, Handler.CALENDARsubject,
            Handler.CALENDARdetails, Handler.CALENDARstartDate,
            Handler.CALENDARendDate, Handler.CALENDARrepeatUntil, 
            Handler.CALENDARrepeatDay, Handler.CALENDARrepeatInterval)        
        #self.show_elapsed_time(tic_write, 'Write CALENDAR')

        #tic_write = timeit.default_timer()
        caseTrace.writeCell_Site(Handler.CELL_SITEid, Handler.CELL_SITEstatus, 
            Handler.CELL_SITElongitude, Handler.CELL_SITElatitude,
            Handler.CELL_SITEtimeStamp, Handler.CELL_SITEmcc,
            Handler.CELL_SITEmnc, Handler.CELL_SITElac, Handler.CELL_SITEcid,
            Handler.CELL_SITEnid, Handler.CELL_SITEbid, Handler.CELL_SITEsid)                
        #self.show_elapsed_time(tic_write, 'Write CELL TOWER')

        #tic_write = timeit.default_timer()        
        caseTrace.writeChat(Handler.CHATid, Handler.CHATstatus, Handler.CHATsource, 
            Handler.CHATpartyIdentifiers, Handler.CHATpartyNames, 
            Handler.CHATmsgIdentifiersFrom, Handler.CHATmsgNamesFrom, 
            Handler.CHATmsgBodies, Handler.CHATmsgStatuses,
            Handler.CHATmsgOutcomes, Handler.CHATmsgTimeStamps, 
            Handler.CHATmsgAttachmentFilenames, Handler.CHATmsgAttachmentUrls)        
        #self.show_elapsed_time(tic_write, 'Write CHAT')

        #tic_write = timeit.default_timer()
        caseTrace.writeCookie(Handler.COOKIEid, Handler.COOKIEstatus, 
            Handler.COOKIEsource, Handler.COOKIEname,
            Handler.COOKIEvalue, Handler.COOKIEdomain,
            Handler.COOKIEcreationTime, Handler.COOKIElastAccessTime, 
            Handler.COOKIEexpiry)        
        #self.show_elapsed_time(tic_write, 'Write COOKIE')

        #tic_write = timeit.default_timer()
        caseTrace.writeDeviceEvent(Handler.DEVICE_EVENTid, Handler.DEVICE_EVENTstatus, 
            Handler.DEVICE_EVENTtimeStamp, Handler.DEVICE_EVENTeventType,
            Handler.DEVICE_EVENTvalue)        
        #self.show_elapsed_time(tic_write, 'Write DEVICE EVENT')

        #tic_write = timeit.default_timer()
        caseTrace.writeEmail(Handler.EMAILid, Handler.EMAILstatus, Handler.EMAILsource, 
            Handler.EMAILidentifierFROM, Handler.EMAILidentifiersTO, 
            Handler.EMAILidentifiersCC, Handler.EMAILidentifiersBCC, 
            Handler.EMAILbody, Handler.EMAILsubject, Handler.EMAILtimeStamp, 
            Handler.EMAILattachmentsFilename)        
        #self.show_elapsed_time(tic_write, 'Write EMAIL')

        #tic_write = timeit.default_timer()
        caseTrace.writeInstantMessage(Handler.INSTANT_MSGid, Handler.INSTANT_MSGstatus, 
            Handler.INSTANT_MSGsource, Handler.INSTANT_MSGtimeStamp, 
            Handler.INSTANT_MSGfromIdentifier, Handler.INSTANT_MSGfromName,
            Handler.INSTANT_MSGtoIdentifier, Handler.INSTANT_MSGtoName, 
            Handler.INSTANT_MSGsubject, Handler.INSTANT_MSGbody, Handler.INSTANT_MSGfolder, 
            Handler.INSTANT_MSGtype, Handler.INSTANT_MSGapplication)        
        #self.show_elapsed_time(tic_write, 'Write INSTANT MESSAGE')

        #tic_write = timeit.default_timer()
        caseTrace.writeLocationDevice(Handler.LOCATIONid, Handler.LOCATIONstatus, 
            Handler.LOCATIONlongitude, Handler.LOCATIONlatitude,
            Handler.LOCATIONaltitude, Handler.LOCATIONtimeStamp, 
            Handler.LOCATIONcategory)        
        #self.show_elapsed_time(tic_write, 'Write LOCATION DEVICE')

        #tic_write = timeit.default_timer()
        caseTrace.writeSearched_Item(Handler.SEARCHED_ITEMid, Handler.SEARCHED_ITEMstatus, 
            Handler.SEARCHED_ITEMsource, Handler.SEARCHED_ITEMtimeStamp,
            Handler.SEARCHED_ITEMvalue, Handler.SEARCHED_ITEMsearchResult)        
        #self.show_elapsed_time(tic_write, 'Write SEARCHED ITEM')

        #tic_write = timeit.default_timer()            
        caseTrace.writeSocial_Media(Handler.SOCIAL_MEDIAid, Handler.SOCIAL_MEDIAstatus, 
            Handler.SOCIAL_MEDIAsource, Handler.SOCIAL_MEDIAtimeStamp, 
            Handler.SOCIAL_MEDIAbody, Handler.SOCIAL_MEDIAtitle, 
            Handler.SOCIAL_MEDIAurl, Handler.SOCIAL_MEDIAidentifier, Handler.SOCIAL_MEDIAname, 
            Handler.SOCIAL_MEDIAreactionsCount, Handler.SOCIAL_MEDIAsharesCount,
            Handler.SOCIAL_MEDIAactivityType, Handler.SOCIAL_MEDIAcommentCount,
            Handler.SOCIAL_MEDIAaccount)        
        #self.show_elapsed_time(tic_write, 'Write SOCIAL MEDIA')

        #tic_write = timeit.default_timer()
        caseTrace.writeWebPages(Handler.WEB_PAGEid, Handler.WEB_PAGEstatus, Handler.WEB_PAGEsource, 
            Handler.WEB_PAGEurl, Handler.WEB_PAGEtitle, Handler.WEB_PAGEvisitCount,
            Handler.WEB_PAGElastVisited)        
        #self.show_elapsed_time(tic_write, 'Write WEB PAGES')

        #tic_write = timeit.default_timer()
        caseTrace.writeWireless_Net(Handler.WIRELESS_NETid, Handler.WIRELESS_NETstatus, 
            Handler.WIRELESS_NETlongitude, Handler.WIRELESS_NETlatitude,
            Handler.WIRELESS_NETtimeStamp, Handler.WIRELESS_NETlastConnection,
            Handler.WIRELESS_NETbssid, Handler.WIRELESS_NETssid)        
        #self.show_elapsed_time(tic_write, 'Write WIRELESS NET')

        #tic_write = timeit.default_timer()
        caseTrace.writeContextUfed(Handler.CONTEXTufedVersionText, 
            Handler.CONTEXTdeviceCreationTimeText, Handler.CONTEXTdeviceExtractionStartText,
            Handler.CONTEXTdeviceExtractionEndText, Handler.CONTEXTexaminerNameText,
            Handler.CONTEXTimagePath, Handler.CONTEXTimageSize, 
            Handler.CONTEXTimageMetadataHashSHA, Handler.CONTEXTimageMetadataHashMD5)        
        #self.show_elapsed_time(tic_write, 'Write CONTEXT UFED')

#---    it writes a single line to complete the JSON output file
        caseTrace.writeLastLine()  
        self.show_elapsed_time(tic_case_start, 'Generation CASE JSON-LD file')

        Handler.fOut.close()  
        return Handler


class ExtractTraces(xml.sax.ContentHandler):
    '''
    Used to extract the Traces from the XML reports and fill in the appropriate structure before generatign the JSON-LD file.
    '''     
    def __init__(self, baseLocalPath, verbose):
        '''
        It initialises the attributes for the processing phase.
            :param baseLocalPath: The local path of the physical files extracted duting the acquisition process (string)
            :param verbose: True if the processing progress will be shonw on the standard output (boolean).
        '''         
        self.fOut = ''
        self.lineXML = 0
        self.skipLine = False
        self.Observable = False
        self.verbose = verbose

        self.C_GREEN  = '\033[32m'
        self.C_GREY  = '\033[37m'
        self.C_RED = '\033[31m'
        self.C_CYAN = '\033[36m'
        self.C_BLACK = '\033[0m'

# FILE section for the Chain of Evidence
        self.TAGGED_FILESin = False
        self.TAGGED_FILESsystem = False
        self.TAGGED_FILESinFile = False
        self.TAGGED_FILESinAccessInfo = False
        self.TAGGED_FILESinTimeStampCreation = False
        self.TAGGED_FILESinTimeStampModify = False
        self.TAGGED_FILESinTimeStampAccess = False
        self.TAGGED_FILESinAccessInfo = False
        self.TAGGED_FILESCreateText = ''
        self.TAGGED_FILESModifyText = ''
        self.TAGGED_FILESAccessText = ''
        self.TAGGED_FILESinAccessInfoCreate = False
        self.TAGGED_FILESinAccessInfoModify = False
        self.TAGGED_FILESinAccessInfoAccess = False
        self.TAGGED_FILESinMetadata = False
        self.TAGGED_FILESinMD5 = False
        self.TAGGED_FILESmd5Text = ''
        self.TAGGED_FILESinTags = False
        self.TAGGED_FILEStagsText = ''
        self.TAGGED_FILESinExifLatitudeRef = False
        self.TAGGED_FILESexifLatitudeRef = ''
        self.TAGGED_FILESinExifLatitude = False
        self.TAGGED_FILESexifLatitude = ''
        self.TAGGED_FILESinExifLongitudeRef = False
        self.TAGGED_FILESexifLongitudeRef = ''
        self.TAGGED_FILESinExifLongitude = False
        self.TAGGED_FILESexifLongitude = ''
        self.TAGGED_FILESinExifAltitude = False
        self.TAGGED_FILESexifAltitude = ''
        self.TAGGED_FILESinExifMake = False
        self.TAGGED_FILESexifMake = ''
        self.TAGGED_FILESinExifModel = False
        self.TAGGED_FILESexifModel = ''

        self.TAGGED_FILESinLocalPath  = False  
        self.TAGGED_FILESbaseLocalPath = baseLocalPath
        self.TAGGED_FILESlocalPathText = '' 
        self.TAGGED_FILESinInodeNumber = False
        self.TAGGED_FILESiNodeNumberText = ''
        self.TAGGED_FILESinOwnerGID = False
        self.TAGGED_FILESownerGIDText = ''
        self.TAGGED_FILESinInodeTimeModify = False
        self.TAGGED_FILESiNodeTimeModifyText = ''
        self.TAGGED_FILESinOwnerUID = False
        self.TAGGED_FILESownerUIDText = ''
        self.FILEidx = -1
        
        self.FILEid = []
        self.FILEpath = []
        self.FILEsize = []
        self.FILEtimeCreate = []
        self.FILEtimeModify = []
        self.FILEtimeAccess = []
        self.FILEmd5 = []
        self.FILEtags = []
        self.FILElocalPath = []
        self.FILEiNodeNumber = []
        self.FILEiNodeTimeModify = []
        self.FILEownerGID =[]
        self.FILEownerUID = []
        self.FILEexifLatitudeRef = []
        self.FILEexifLatitude = []
        self.FILEexifLongitudeRef = []
        self.FILEexifLongitude = []
        self.FILEexifAltitude = []
        self.FILEexifMake = []
        self.FILEexifModel = []

        self.EXTRA_INFOin = False 
        self.EXTRA_INFOnodeInfoin = False
        self.EXTRA_INFOid = ''
        self.EXTRA_INFOlistId = []
        self.EXTRA_INFOdictPath = {}
        self.EXTRA_INFOdictSize = {}
        self.EXTRA_INFOdictTableName = {}
        self.EXTRA_INFOdictOffset = {}
        self.EXTRA_INFOdictNodeInfoId = {}

#--     Bluetooh connection
        self.BLUETOOTHinModelType = False
        self.BLUETOOTHin = False
        self.BLUETOOTHinDeviceIdentifiers = False
        self.BLUETOOTHinKeyValueModel = False
        self.BLUETOOTHinKey = False
        self.BLUETOOTHinKeyValue = False        
        self.BLUETOOTHinValue = False
        self.BLUETOOTHinValueValue = False
        self.BLUETOOTHtotal = 0
        self.BLUETOOTHkeyText = ''
        self.BLUETOOTHvalueText = ''

        self.BLUETOOTHdeleted = 0
        self.BLUETOOTHid = []
        self.BLUETOOTHkeys = []
        self.BLUETOOTHvalues = []
        self.BLUETOOTHstatus = []  
                
#-- CALENDAR  section    
        self.CALENDARinModelType = False
        self.CALENDARin = False
        self.CALENDARinCategory = False
        self.CALENDARinCategoryValue = False
        self.CALENDARinSubject = False
        self.CALENDARinSubjectValue = False
        self.CALENDARinDetails = False
        self.CALENDARinDetailsValue = False
        self.CALENDARinStartDate = False
        self.CALENDARinStartDateValue = False
        self.CALENDARinEndDate = False
        self.CALENDARinEndDateValue = False
        self.CALENDARinRepeatUntil = False
        self.CALENDARinRepeatUntilValue = False
        self.CALENDARinRepeatDay = False
        self.CALENDARinRepeatDayValue = False
        self.CALENDARinRepeatInterval = False
        self.CALENDARinRepeatIntervalValue = False
        self.CALENDARinAttendees = False
        self.CALENDARinAttachments = False

        self.CALENDARtotal = 0
        self.CALENDARcategoryText = ''
        self.CALENDARsubjectText = ''
        self.CALENDARdetailsText = ''
        self.CALENDARstartDateText = ''
        self.CALENDARendDateText = ''
        self.CALENDARrepeatUntilText = ''
        self.CALENDARrepeatDayText = ''
        self.CALENDARrepeatIntervalText = ''

        self.CALENDARdeleted = 0
        self.CALENDARid = []
        self.CALENDARcategory = []
        self.CALENDARsubject = []
        self.CALENDARdetails = []
        self.CALENDARstartDate = []
        self.CALENDARendDate = []
        self.CALENDARrepeatUntil = []
        self.CALENDARrepeatDay = []
        self.CALENDARrepeatInterval = []
        self.CALENDARstatus = []            

#--     CALL  section
        self.CALLinModelType = False
        self.CALLin = False
        self.CALLinSource = False
        self.CALLinSourceValue = False
        self.CALLinDirection = False
        self.CALLinDirectionValue = False        
        self.CALLinOutcomeValue = False        
        self.CALLinDuration = False
        self.CALLinTimeStamp = False
        self.CALLinTimeStampValue = False
        self.CALLinType = False
        self.CALLinTypeValue = False        
        self.CALLinOutcome = False        
        self.CALLinDurationValue = False
        self.CALLinParty = False
        self.CALLinIdentifier = False
        self.CALLinIdentifierValue = False
        self.CALLinRole = False
        self.CALLinRoleValue = False
        self.CALLinName = False
        self.CALLinNameValue = False        

        self.CALLtotal = 0
        self.CALLsourceText = ''
        self.CALLdirectionText = ''
        self.CALLtypeText = ''
        self.CALLdurationText = ''
        self.CALLoutcomeText = ''
        self.CALLtimeStampText = ''
        self.CALLroleTextTO = ''        
        self.CALLroleTextFROM = ''        
        self.CALLidentifierText = ''
        self.CALLidentifierTextTO = ''
        self.CALLidentifierTextFROM = ''
        self.CALLnameTextTO = ''
        self.CALLnameTextFROM = ''
        self.CALLroleText = ''
        self.CALLnameText = ''
        self.CALLidentifierText = ''
        self.CALLdeleted = 0
        self.CALLid = []
        self.CALLsource = []
        self.CALLtimeStamp = []
        self.CALLdirection = []
        self.CALLtype = []
        self.CALLduration = []
        self.CALLstatus = []
        self.CALLoutcome = []
        self.CALLnameTO = []
        self.CALLnameFROM = []
        self.CALLroleTO = []
        self.CALLroleFROM = []
        self.CALLidentifierTO = []
        self.CALLidentifierFROM = []

        self.CALLnamesTO = []
        self.CALLnamesFROM = []
        self.CALLrolesTO = []
        self.CALLrolesFROM = []
        self.CALLidentifiersTO = []
        self.CALLidentifiersFROM = []

#-- CELL_SITE  section     
        self.CELL_SITEinModelType = False
        self.CELL_SITEin = False
        self.CELL_SITEinPosition = False
        self.CELL_SITEinLongitude = False
        self.CELL_SITEinLongitudeValue = False
        self.CELL_SITEinLatitude = False
        self.CELL_SITEinLatitudeValue = False
        self.CELL_SITEinTimeStamp = False
        self.CELL_SITEinTimeStampValue = False
        self.CELL_SITEinMCC = False
        self.CELL_SITEinMCCValue = False
        self.CELL_SITEinMNC = False
        self.CELL_SITEinMNCValue = False
        self.CELL_SITEinLAC = False
        self.CELL_SITEinLACValue = False
        self.CELL_SITEinCID = False
        self.CELL_SITEinCIDValue = False
        self.CELL_SITEinNID = False
        self.CELL_SITEinNIDValue = False
        self.CELL_SITEinBID = False
        self.CELL_SITEinBIDValue = False
        self.CELL_SITEinSID = False
        self.CELL_SITEinSIDValue = False

        self.CELL_SITEtotal = 0
        self.CELL_SITElongitudeText = ''
        self.CELL_SITElatitudeText = ''
        self.CELL_SITEtimeStampText = ''
        self.CELL_SITEmccText = ''
        self.CELL_SITEmncText = ''
        self.CELL_SITElacText = ''
        self.CELL_SITEcidText = ''
        self.CELL_SITEnidText = ''
        self.CELL_SITEbidText = ''
        self.CELL_SITEsidText = ''

        self.CELL_SITEdeleted = 0
        self.CELL_SITEid = []
        self.CELL_SITElongitude = []
        self.CELL_SITElatitude = []
        self.CELL_SITEtimeStamp = []
        self.CELL_SITEmcc = []
        self.CELL_SITEmnc = []
        self.CELL_SITElac = []
        self.CELL_SITEcid = []
        self.CELL_SITEnid = []
        self.CELL_SITEbid = []
        self.CELL_SITEsid = []
        self.CELL_SITEstatus = []

#---    CHAT section
        self.CHATinModelType = False
        self.CHATin = False
        self.CHATinSource = False
        self.CHATinSourceValue = False
        self.CHATinParty = False
        self.CHATinPartyIdentifier = False
        self.CHATinPartyIdentifierValue = False
        self.CHATinPartyName = False        
        self.CHATinPartyNameValue = False 
        self.CHATinInstantMessage = False                
        self.CHATinMultiModelFieldParticipants = False
        self.CHATinMsgFrom = False
        self.CHATinMultiModelFieldTo = False
        self.CHATinMsgIdentifierFrom = False
        self.CHATinMsgIdentifierFromValue = False
        self.CHATinMsgNameFrom = False
        self.CHATinMsgNameFromValue = False
        self.CHATinMultiModelFieldAttachments = False
        self.CHATinModelFieldAttachment = False
        self.CHATinMsgAttachment = False
        self.CHATinMultiModelFieldPhotos = False
        self.CHATinMsgContactPhoto = False
        self.CHATinMsgExtraData = False
        self.CHATinMsgSharedContacts = False
        self.CHATinMultiModelFieldSharedContacts = False
        self.CHATinMultiModelFieldMessageExtraData = False
        self.CHATinMsgBody = False
        self.CHATinMsgBodyValue = False
        self.CHATinMsgOutcome = False
        self.CHATinMsgOutcomeValue = False
        self.CHATinMsgTimeStamp = False
        self.CHATinMsgTimeStampValue = False
        self.CHATinMsgAttachmentFilename = False
        self.CHATinMsgAttachmentFilenameValue = False
        self.CHATinMsgAttachmentUrl = False
        self.CHATinMsgAttachmentUrlValue = False

        self.CHATnumber = 0
        self.CHATtotal = 0
        self.CHATdeleted = 0
        self.CHATmsgNum = -1
        self.CHATsourceText = ''
        self.CHATpartyIdentifierText = ''
        self.CHATpartyNameText = ''
        self.CHATmsgIdentifierFromText = ''
        self.CHATmsgNameFromText = ''
        self.CHATmsgIdentifierToText = ''
        self.CHATmsgNameToText = ''
        self.CHATmsgBodyText = ''
        self.CHATmsgOutcomeText = ''
        self.CHATmsgTimeStampText = ''
        self.CHATmsgAttachmentFilenameText = ''
        self.CHATmsgAttachmentUrlText = ''

        self.CHATid = []
        self.CHATstatus = []
        self.CHATsource = []
        # These lists contain the Identifier and Name below the model (type="Party")
        # element. For each Chat there is one PartyIdentifier and one NameIdentifier
        self.CHATpartyIdentifier = []
        self.CHATpartyName = []
        self.CHATmsgIdentifierFrom = []
        self.CHATmsgNameFrom = []
        self.CHATmsgAttachmentFilename = []
        self.CHATmsgAttachmentUrl = []
        self.CHATmsgBody = []
        self.CHATmsgStatus = []
        self.CHATmsgOutcome = []

        
#---    These are list of list: each item contains a list with all the data relating 
#       to the messages of a single Chat (they are grouped in the same thread). 
#       Therefore the item i (Chat[i]) contains many message bodies and each of them is
#       stored in the item CHATmsgBodies[i] that, actually, is a list. For instance, if
#       the Chat[0] contains three messages whose body are "How are you?", "I',m fine, and you?"
#       "So far so good", then the  CHATmsgBodies[0] is the the following list
#       ["How are you?", "I',m fine, and you?", "So far so good"]
        self.CHATpartyIdentifiers = []
        self.CHATpartyNames = []
        self.CHATmsgIdentifiersFrom = []
        self.CHATmsgNamesFrom = []
        self.CHATmsgBodies = []
        self.CHATmsgStatuses = []
        self.CHATmsgOutcomes = []
        self.CHATmsgTimeStamp = []
        self.CHATmsgTimeStamps = []
        self.CHATmsgAttachmentFilenames = []
        self.CHATmsgAttachmentUrls = [] 

#-- COOKIE  section
        self.COOKIEin = False
        self.COOKIEinModelType = False
        self.COOKIEinSource = False
        self.COOKIEinSourceValue = False
        self.COOKIEinName = False
        self.COOKIEinNameValue = False
        self.COOKIEinValue = False
        self.COOKIEinValueValue = False
        self.COOKIEinDomain = False
        self.COOKIEinDomainValue = False
        self.COOKIEinCreationTime = False
        self.COOKIEinCreationTimeValue = False
        self.COOKIEinLastAccessTime = False
        self.COOKIEinLastAccessTimeValue = False
        self.COOKIEinExpiry = False
        self.COOKIEinExpiryValue = False

        self.COOKIEtotal = 0
        self.COOKIEsourceText = ''
        self.COOKIEnameText = ''
        self.COOKIEvalueText = ''
        self.COOKIEdomainText = ''
        self.COOKIEcreationTimeText = ''
        self.COOKIElastAccessTimeText = ''
        self.COOKIEexpiryText = ''

        self.COOKIEdeleted = 0
        self.COOKIEid = []
        self.COOKIEsource = []
        self.COOKIEname = []
        self.COOKIEvalue = []
        self.COOKIEdomain = []
        self.COOKIEcreationTime = []
        self.COOKIElastAccessTime = []
        self.COOKIEexpiry = []
        self.COOKIEstatus = []        

#-- DEVICE_EVENT  section
        self.DEVICE_EVENTinModelType = False
        self.DEVICE_EVENTin = False
        self.DEVICE_EVENTinTimeStamp = False
        self.DEVICE_EVENTinTimeStampValue = False
        self.DEVICE_EVENTinEventType = False
        self.DEVICE_EVENTinEventTypeValue = False
        self.DEVICE_EVENTinValue = False
        self.DEVICE_EVENTinValueValue = False
        
        self.DEVICE_EVENTtotal = 0
        self.DEVICE_EVENTtimeStampText = ''
        self.DEVICE_EVENTeventTypeText = ''
        self.DEVICE_EVENTvalueText = ''

        self.DEVICE_EVENTdeleted = 0
        self.DEVICE_EVENTid = []
        self.DEVICE_EVENTtimeStamp = []
        self.DEVICE_EVENTeventType = []
        self.DEVICE_EVENTvalue = []
        self.DEVICE_EVENTstatus = []
        
#-- EMAIL section
        self.EMAILinModelType = False
        self.EMAILin = False
        self.EMAILinSource = False
        self.EMAILinSourceValue = False
        self.EMAILinModelFieldFROM = False
        self.EMAILinIdentifierFROM = False
        self.EMAILinIdentifierFROMvalue = False
        self.EMAILinMultiModelFieldTO = False
        self.EMAILinIdentifierTO = False
        self.EMAILinIdentifierTOvalue = False
        self.EMAILinMultiModelFieldCC= False
        self.EMAILinIdentifierCC = False
        self.EMAILinIdentifierCCvalue = False
        self.EMAILinMultiModelFieldBCC = False
        self.EMAILinIdentifierBCC = False
        self.EMAILinIdentifierBCCvalue = False
        self.EMAILinMultiModelFieldAttachments = False
        self.EMAILinAttachmentFilename = False
        self.EMAILinAttachmentFilenameValue = False
        self.EMAILinSubject = False
        self.EMAILinSubjectValue = False
        self.EMAILinBody = False
        self.EMAILinBodyValue = False
        self.EMAILinTimeStamp = False
        self.EMAILinTimeStampValue = False

        self.EMAILsourceText = ''
        self.EMAILidentifierFROMtext = ''
        self.EMAILidentifierTOtext = ''
        self.EMAILidentifierCCtext = ''
        self.EMAILidentifierBCCtext = ''
        self.EMAILattachmentFilenameText = ''
        self.EMAILbodyText = ''
        self.EMAILsubjectText = ''
        self.EMAILtimeStampText = ''

        self.EMAILnumber = 0
        self.EMAILtotal = 0
        self.EMAILdeleted = 0

        self.EMAILid = []
        self.EMAILstatus = []
        self.EMAILsource = []
        self.EMAILidentifierFROM = []
        self.EMAILidentifierTO = []
        self.EMAILidentifierCC = []
        self.EMAILidentifierBCC = []
        self.EMAILattachmentFilename = []
        self.EMAILbody = []
        self.EMAILsubject = []
        self.EMAILtimeStamp = []

        self.EMAILidentifiersTO = []
        self.EMAILidentifiersCC = []
        self.EMAILidentifiersBCC = []
        self.EMAILattachmentsFilename = []

# SMS section 
        self.SMSinModelType = False
        self.SMSin = False
        self.SMSinSource = False
        self.SMSinSourceValue = False        
        self.SMSinTimeStamp = False
        self.SMSinTimeStampValue = False
        self.SMSinBody = False
        self.SMSinBodyValue = False
        self.SMSinFolder = False
        self.SMSinFolderValue = False

#---    Short Message Service Center, part of the mdelType type="SMS"
        self.SMSinSmsc = False
        self.SMSinSmscValue = False

        self.SMSinParty = False
        self.SMSinAllTimeStamps = False
        self.SMSinPartyIdentifier = False
        self.SMSinPartyIdentifierValue = False
        self.SMSinPartyName = False
        self.SMSinPartyNameValue = False
        self.SMSinPartyRole = False
        self.SMSinPartyRoleValue = False
        
        self.SMSnumber = 0
        self.SMSdeleted = 0
        self.SMStimeStampText = ''
        self.SMSsourceText = ''
        self.SMSbodyText = ''
        self.SMSfolderText = ''
        self.SMSsmscText = ''
        self.SMSpartyRoleText = ''        
        self.SMSpartyIdentifierText = ''        
        self.SMSpartyNameText = ''
        
        self.SMStotal = 0
        
        self.SMSid = []
        self.SMSsource = []
        self.SMStimeStamp =[]
        self.SMSbody = []
        self.SMSfolder = []
        self.SMSsmsc = []
        self.SMSpartyIdentifier = []
        self.SMSpartyName = []        
        self.SMSpartyRole = []
        self.SMSstatus = []
        
        self.SMSpartyIdentifiers = []
        self.SMSpartyRoles = []
        self.SMSpartyNames = []

#-- INSTANT_MSG  section
        self.INSTANT_MSGinModelType = False
        self.INSTANT_MSGin = False
        self.INSTANT_MSGinSource = False
        self.INSTANT_MSGinSourceValue = False
        self.INSTANT_MSGinPartyFrom = False
        self.INSTANT_MSGinFromIdentifier = False 
        self.INSTANT_MSGinFromIdentifierValue = False 
        self.INSTANT_MSGinFromName = False 
        self.INSTANT_MSGinFromNameValue = False 
        self.INSTANT_MSGinPartyTo = False
        self.INSTANT_MSGinToIdentifier = False 
        self.INSTANT_MSGinToIdentifierValue = False 
        self.INSTANT_MSGinToName = False 
        self.INSTANT_MSGinToNameValue = False 
        self.INSTANT_MSGinSubject = False
        self.INSTANT_MSGinSubjectValue = False
        self.INSTANT_MSGinBody = False
        self.INSTANT_MSGinBodyValue = False
        self.INSTANT_MSGinTimeStamp= False
        self.INSTANT_MSGinTimeStampValue = False
        self.INSTANT_MSGinAttachment = False
        self.INSTANT_MSGinStatusMsg= False
        self.INSTANT_MSGinStatusMsgValue = False
        self.INSTANT_MSGinAttachments = False
        self.INSTANT_MSGinSharedContacts = False
        self.INSTANT_MSGinType = False
        self.INSTANT_MSGinTypeValue = False
        self.INSTANT_MSGinFolder = False
        self.INSTANT_MSGinFolderValue = False
        self.INSTANT_MSGinApplication = False
        self.INSTANT_MSGinApplicationValue = False

        self.INSTANT_MSGtotal = 0
        self.INSTANT_MSGdeleted = 0
        self.INSTANT_MSGsourceText = ''
        self.INSTANT_MSGfromIdentifierText = ''
        self.INSTANT_MSGfromNameText = ''
        self.INSTANT_MSGtoIdentifierText = ''
        self.INSTANT_MSGtoNameText = ''
        self.INSTANT_MSGsubjectText = ''
        self.INSTANT_MSGbodyText = ''
        self.INSTANT_MSGtimeStampText = ''
        self.INSTANT_MSGstatusMsgText  = ''        
        self.INSTANT_MSGtypeText = ''
        self.INSTANT_MSGfolderText = ''
        self.INSTANT_MSGapplicationText = ''

        self.INSTANT_MSGid = []
        self.INSTANT_MSGstatus = []
        self.INSTANT_MSGsource = []
        self.INSTANT_MSGfromIdentifier = []
        self.INSTANT_MSGfromName = []
        self.INSTANT_MSGtoIdentifier = []   # it contains values separated by @@@
        self.INSTANT_MSGtoName = []         # it contains values separated by @@@
        self.INSTANT_MSGsubject = []
        self.INSTANT_MSGbody = []
        self.INSTANT_MSGtimeStamp = []
        self.INSTANT_MSGtype = []
        self.INSTANT_MSGstatusMsg = []
        self.INSTANT_MSGfolder = []
        self.INSTANT_MSGapplication = []

#-- LOCATION (Device Location) section
        self.LOCATIONinModelType = False
        self.LOCATIONin = False
        self.LOCATIONinPosition = False
        self.LOCATIONinLongitude = False
        self.LOCATIONinLongitudeValue = False
        self.LOCATIONinLatitude = False
        self.LOCATIONinLatitudeValue = False
        self.LOCATIONinAltitude = False
        self.LOCATIONinAltitudeValue = False
        self.LOCATIONinTimeStamp = False
        self.LOCATIONinTimeStampValue = False
        self.LOCATIONinCategory = False
        self.LOCATIONinCategoryValue = False
        self.LOCATIONtic = 0 
        self.LOCATIONtoc = 0 

        self.LOCATIONtotal = 0        
        self.LOCATIONrun = 0
        self.LOCATIONlongitudeText = ''
        self.LOCATIONlatitudeText = ''
        self.LOCATIONaltitudeText = ''
        self.LOCATIONtimeStampText = ''
        self.LOCATIONcategoryText = ''

        self.LOCATIONdeleted = 0
        self.LOCATIONid = []
        self.LOCATIONlongitude = []
        self.LOCATIONlatitude = []
        self.LOCATIONaltitude = []
        self.LOCATIONtimeStamp =[]
        self.LOCATIONcategory = []
        self.LOCATIONstatus = []

# CONTACT section
        self.CONTACTin = False
        self.CONTACTinModelType = False
        self.CONTACTinSource = False
        self.CONTACTinSourceValue = False
        self.CONTACTinName = False
        self.CONTACTinNameValue = False
        self.CONTACTinMultiModelFieldPhotos = False
        self.CONTACTinMultiModelFieldEntries = False
        self.CONTACTinModelPhoneNumber = False
        self.CONTACTinModelUserId = False
        self.CONTACTinUserId = False
        self.CONTACTinUserIdValue = False
        self.CONTACTinPhoneNum = False
        self.CONTACTinPhoneNumValue = False
        self.CONTACTinModelProfilePicture = False
        self.CONTACTinAccount = False
        self.CONTACTinAccountValue = False
        self.CONTACTinMultiFieldInteractionStatuses = False

        self.CONTACTtotal = 0
        self.CONTACTdeleted = 0
        self.CONTACTsourceText = ''
        self.CONTACTnameText = ''        
        self.CONTACTphoneNumText = ''
        self.CONTACTuserIdText = ''
        self.CONTACTaccountText = ''
        
        self.CONTACTid = []
        self.CONTACTstatus = []
        self.CONTACTname = []
        self.CONTACTsource = []
        self.CONTACTuserId = []
        self.CONTACTphoneNum = []
        self.CONTACTaccount = []

        self.CONTACTphoneNums = []
        self.CONTACTuserIds = []

#-- SEARCHED ITEM  section     
        self.SEARCHED_ITEMin = False
        self.SEARCHED_ITEMinModelType = False
        self.SEARCHED_ITEMinSource = False
        self.SEARCHED_ITEMinSourceValue = False
        self.SEARCHED_ITEMinTimeStamp = False
        self.SEARCHED_ITEMinTimeStampValue = False
        self.SEARCHED_ITEMinValue = False
        self.SEARCHED_ITEMinValueValue = False
        self.SEARCHED_ITEMinSearchResult = False
        self.SEARCHED_ITEMinSearchResultValue = False

        self.SEARCHED_ITEMtotal = 0
        self.SEARCHED_ITEMsourceText = ''
        self.SEARCHED_ITEMtimeStampText = ''
        self.SEARCHED_ITEMvalueText = ''
        self.SEARCHED_ITEMsearchResultText = ''

        self.SEARCHED_ITEMdeleted = 0
        self.SEARCHED_ITEMid = []
        self.SEARCHED_ITEMsource = []
        self.SEARCHED_ITEMtimeStamp = []
        self.SEARCHED_ITEMvalue = []
        self.SEARCHED_ITEMstatus = []  
        self.SEARCHED_ITEMsearchResult = []  

#-- SOCIAL MEDIA ACTIVITY (direct interactions with the social media platform)            
        self.SOCIAL_MEDIAinModelType = False
        self.SOCIAL_MEDIAin = False
        self.SOCIAL_MEDIAinSource = False
        self.SOCIAL_MEDIAinSourceValue = False
        self.SOCIAL_MEDIAinAttachments = False
        self.SOCIAL_MEDIAinTimeStamp = False
        self.SOCIAL_MEDIAinTimeStampValue = False
        self.SOCIAL_MEDIAinBody = False
        self.SOCIAL_MEDIAinBodyValue = False
        self.SOCIAL_MEDIAinTitle = False
        self.SOCIAL_MEDIAinTitleValue = False
        self.SOCIAL_MEDIAinUrl = False
        self.SOCIAL_MEDIAinUrlValue = False
        self.SOCIAL_MEDIAinAuthor = False
        self.SOCIAL_MEDIAinIdentifier = False
        self.SOCIAL_MEDIAinIdentifierValue = False
        self.SOCIAL_MEDIAinName = False
        self.SOCIAL_MEDIAinNameValue = False
        self.SOCIAL_MEDIAinTaggedParties = False
        self.SOCIAL_MEDIAinReactionsCount = False
        self.SOCIAL_MEDIAinReactionsCountValue = False
        self.SOCIAL_MEDIAinSharesCount = False
        self.SOCIAL_MEDIAinSharesCountValue = False
        self.SOCIAL_MEDIAinActivityType = False
        self.SOCIAL_MEDIAinActivityTypeValue = False
        self.SOCIAL_MEDIAinCommentCount = False
        self.SOCIAL_MEDIAinCommentCountValue = False
        self.SOCIAL_MEDIAinAccount = False
        self.SOCIAL_MEDIAinAccountValue = False

        self.SOCIAL_MEDIAtotal = 0        
        self.SOCIAL_MEDIAsourceText = ''
        self.SOCIAL_MEDIAtimeStampText = ''
        self.SOCIAL_MEDIAbodyText = ''
        self.SOCIAL_MEDIAtitleText = ''
        self.SOCIAL_MEDIAurlText = ''
        self.SOCIAL_MEDIAidentifierText = ''
        self.SOCIAL_MEDIAnameText = ''
        self.SOCIAL_MEDIAreactionsCountText = ''
        self.SOCIAL_MEDIAsharesCountText = ''
        self.SOCIAL_MEDIAactivityTypeText = ''
        self.SOCIAL_MEDIAcommentCountText = ''
        self.SOCIAL_MEDIAaccountText = ''

        self.SOCIAL_MEDIAdeleted = 0
        self.SOCIAL_MEDIAid = []
        self.SOCIAL_MEDIAsource = []
        self.SOCIAL_MEDIAtimeStamp = []
        self.SOCIAL_MEDIAbody = []
        self.SOCIAL_MEDIAtitle = []
        self.SOCIAL_MEDIAurl = []
        self.SOCIAL_MEDIAidentifier = []
        self.SOCIAL_MEDIAname = []
        self.SOCIAL_MEDIAreactionsCount = []
        self.SOCIAL_MEDIAsharesCount = []
        self.SOCIAL_MEDIAactivityType = []
        self.SOCIAL_MEDIAcommentCount = []
        self.SOCIAL_MEDIAaccount = []

        self.SOCIAL_MEDIAstatus = []

#---    WEB HISTORY section
        self.WEB_PAGEinModelType = False
        self.WEB_PAGEin = False
        self.WEB_PAGEinSource = False
        self.WEB_PAGEinSourceValue = False
        self.WEB_PAGEinUrl = False
        self.WEB_PAGEinUrlValue = False
        self.WEB_PAGEinTitle = False
        self.WEB_PAGEinTitleValue = False
        self.WEB_PAGEinVisitCount = False
        self.WEB_PAGEinVisitCountValue = False
        self.WEB_PAGEinLastVisited = False        
        self.WEB_PAGEinLastVisitedValue = False        
        
        self.WEB_PAGEtotal = 0
        self.WEB_PAGEdeleted = 0
        self.WEB_PAGEsourceText = ''
        self.WEB_PAGEurlText = ''  
        self.WEB_PAGEtitleText = ''  
        self.WEB_PAGEvisitCountText = ''  
        self.WEB_PAGElastVisitedText = ''  
        self.WEB_PAGEid = []
        self.WEB_PAGEstatus = []
        self.WEB_PAGEsource = []
        self.WEB_PAGEurl = []
        self.WEB_PAGEtitle = []
        self.WEB_PAGEvisitCount = []
        self.WEB_PAGElastVisited = []
        
#-- WIRELESS_NET  section
        self.WIRELESS_NETin = False
        self.WIRELESS_NETinModelType = False
        self.WIRELESS_NETinPosition = False
        self.WIRELESS_NETinLongitude = False
        self.WIRELESS_NETinLongitudeValue = False
        self.WIRELESS_NETinLatitude = False
        self.WIRELESS_NETinLatitudeValue = False
        self.WIRELESS_NETinTimeStamp = False
        self.WIRELESS_NETinTimeStampValue = False
        self.WIRELESS_NETinLastConnection = False
        self.WIRELESS_NETinLastConnectionValue = False
        self.WIRELESS_NETinBssid = False
        self.WIRELESS_NETinBssidValue = False
        self.WIRELESS_NETinSsid = False
        self.WIRELESS_NETinSsidValue = False

        self.WIRELESS_NETtotal = 0
        self.WIRELESS_NETlongitudeText = ''
        self.WIRELESS_NETlatitudeText = ''
        self.WIRELESS_NETtimeStampText = ''
        self.WIRELESS_NETlastConnectionText = ''
        self.WIRELESS_NETbssidText = ''
        self.WIRELESS_NETssidText = ''

        self.WIRELESS_NETdeleted = 0
        self.WIRELESS_NETid = []
        self.WIRELESS_NETlongitude = []
        self.WIRELESS_NETlatitude = []
        self.WIRELESS_NETtimeStamp = []
        self.WIRELESS_NETlastConnection = []
        self.WIRELESS_NETbssid = []
        self.WIRELESS_NETssid = []
        self.WIRELESS_NETstatus = []        

#---    USER ACCOUNT section, it is for detecting username account of the owner's phone number 
#       for all application installed on the device (i.e. account Whatsapp that includes the 
#       phone number, Skype, Telegram, Snapchat, etc.)
        self.U_ACCOUNTin = False
        self.U_ACCOUNTinUsername = False
        self.U_ACCOUNTinUsernameValue = False
        self.U_ACCOUNTusernameValueText = ''
        self.U_ACCOUNTusername = []

        self.U_ACCOUNTinContactEntry = False
        self.U_ACCOUNTinContactPhoto = False
        self.U_ACCOUNTinEmailAddress = False
        self.U_ACCOUNTinUserID = False
        
        self.U_ACCOUNTinSource = False
        self.U_ACCOUNTinSourceValue = False
        self.U_ACCOUNTsourceValueText = ''
        self.U_ACCOUNTsource = []
        
        self.U_ACCOUNTinName = False
        self.U_ACCOUNTinNameValue = False
        self.U_ACCOUNTnameValueText = ''
        self.U_ACCOUNTname = []

        self.U_ACCOUNTtotal = 0

#---    Data for the context: tool, mobile device info, acquisition and 
#       extraction investigative action
        self.CONTEXTinAdditionalFields = False
        self.CONTEXTinUfedVersionValue  = False
        self.CONTEXTufedVersionText = ''
        self.CONTEXTinDeviceCreationTimeValue  = False
        self.CONTEXTdeviceCreationTimeText  = ''

        self.CONTEXTinCaseInfo  = False
        self.CONTEXTinExaminerNameValue  = False
        self.CONTEXTexaminerNameText = ''

        self.CONTEXTinExtractionData  = False
        self.CONTEXTinDeviceExtractionStart  = False
        self.CONTEXTdeviceExtractionStartText  = ''
        self.CONTEXTinDeviceExtractionEnd  = False
        self.CONTEXTdeviceExtractionEndText  = ''
        
        self.CONTEXTinDeviceInfo = False
        self.CONTEXTinDeviceBluetoothAddressValue = False
        self.CONTEXTdeviceBluetoothAddressText = ''
        self.CONTEXTinDeviceBluetoothName = False
        self.CONTEXTdeviceBluetoothNameText = ''
        self.CONTEXTinDeviceIdValue = False
        self.CONTEXTdeviceIdText = ''
        self.CONTEXTinDevicePhoneModelValue = False
        self.CONTEXTdevicePhoneModelText = ''
        self.CONTEXTinDeviceOsTypeValue = False
        self.CONTEXTdeviceOsTypeText = ''
        self.CONTEXTinDeviceOsVersionValue = False
        self.CONTEXTdeviceOsVersionText = ''
        self.CONTEXTinDevicePhoneVendorValue = False
        self.CONTEXTdevicePhoneVendorText = ''
        self.CONTEXTinDeviceMacAddressValue = False
        self.CONTEXTdeviceMacAddressText = ''
        self.CONTEXTinDeviceIccidValue = False
        self.CONTEXTdeviceIccidText = ''
        self.CONTEXTinDeviceMsisdnValue = False
        self.CONTEXTdeviceMsisdnText = ''
        self.CONTEXTinDeviceImsiValue = False
        self.CONTEXTdeviceImsiText = ''
        self.CONTEXTinDeviceImeiValue = False
        self.CONTEXTdeviceImeiText = ''

        self.CONTEXTinImages = False
        self.CONTEXTinImage = False
        self.CONTEXTimagePath = []
        self.CONTEXTimageSize = []
        self.CONTEXTinImageMetadataHash = False
        self.CONTEXTinImageMetadataHashValueSHA = False
        self.CONTEXTinImageMetadataHashValueMD5 = False
        self.CONTEXTimageMetadataHashTextSHA = ''
        self.CONTEXTimageMetadataHashTextMD5 = ''
        self.CONTEXTimageMetadataHashSHA = []
        self.CONTEXTimageMetadataHashMD5 = []

    def __cleanText(self, text):
        '''
        It cleans the text getting rid of carriage return, line feed and doublw quote.
            :param text: The original text to be cleaned (string)
            :return: The cleaned text (string).
        '''         
        text = text.replace('\n', ' ')
        text = text.replace('"', "'")
        text = text.replace('\n', ' ')
        return text

    def __cleanPhoneNumber(self, phoneNum):
        '''
        It cleans the phone number. If the phone number does not contain the expected characters, only the ones
        including in the regexp are returned.
            :param phoneNum: The orginal phone number text (string)
            :return: The phone number with only the expected characters, defined in the regexp (string).
        '''        
        phonePattern = '([0-9]+)'
        phoneNum = phoneNum.strip().replace(' ', '')
        phoneMatch = re.search(phonePattern, phoneNum)
        if phoneMatch:
            phoneNum = phoneMatch.group()
            
        return phoneNum

    def createOutFile(self, filename):
        '''
        It transfers all the Traces (Observable in CUCO/CASE terminology) from the memory to the file, whose name has been
        provided as an argument in the command line.
            :param filename: The JSON-LD filename that is being generated, complied with the UOC/CASE ontologies (string).
            :return:  None.
        '''         
        self.fOut = codecs.open(filename, 'w', encoding='utf8')

    def findOwnerPhone(self, UserAccounts):
        '''
        It finds the owner's phone number relying on the whataspp application, that should be installed
        on the mobile device.
            :param UserAccounts: List of the user accounts (list).
            :return:  The owner name, empty in case the whataspp application is not installed.
        '''          
        ownerPhone = ''
        for account in UserAccounts:
            posAccount = account.find('@s.whatsapp.net')
            if posAccount > -1:
                ownerPhone = account[0:posAccount]
                break
        return ownerPhone
    
    def storeTraceStatus(self, listTrace, status, nDeleted):
        '''
        It stores the status of the Trace currewntly processed.
            :param listTrace: List of the status of the Trace of the kind currently processes, such as Call, Chat etc. (list).
            :param status: The status of the current Trace item, possible values are Intact or Deleted (string).
            :para nDeleted: It counts the number of deleted items of the current Trace (int).
            :return:  None.
        '''         
        if status == 'Deleted':
            listTrace.append('Deleted')
            nDeleted +=1
        else:
            listTrace.append('Intact')
                        

    def printObservable(self, oName, oCount):        
        '''
        It prints the number of the kind of Trace item currently processed.
            :param oName: Name of the kind of Trace such as Contact, Call, Chat etc.  (string).
            :param oCount: The number of the kind of Trace item currently processed (int).
            :return:  None.
        '''            
        line =  "".join(['Extracting artifacts --> ', oName, ' n. ', str(oCount), self.C_BLACK])
        if self.verbose:            
            if oCount == 1:
                print("".join([self.C_GREEN, '\n', line]), end='\r') 
            else:
                print("".join([self.C_GREEN, line]), end='\r') 

    def __startElementModelCALL(self, attrValue, CALLid, CALLstate):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="Call"]
            :param attrValue: Value of the attribute name of the ELement (string).
            :param CALLid: The value of the id attribute of the Element  (string).
            :param CALLstate: The value of the  deleted_state attribute of the Element  (string).
            :return:  None.
        '''         
        if attrValue == 'Call':
            self.CALLin = True
            self.CALLtotal += 1
            self.printObservable('CALL', self.CALLtotal)
            self.CALLid.append(CALLid)
            self.storeTraceStatus(self.CALLstatus, CALLstate, self.CALLdeleted)
            self.skipLine = True 
            self.Observable = True 
        elif attrValue == 'Party':                                
            self.CALLinParty = True 

    def __startElementModelBLUETOOTH(self, attrType, BLUETOOTHid, BLUETOOTHstate):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="DeviceConnectivity"]
            :param attrValue: Value of the attribute name of the ELement (string).
            :param BLUETOOTHid: The value of the id attribute of the Element  (string).
            :param BLUETOOTHstate: The value of the  deleted_state attribute of the Element  (string).
            :return:  None.
        '''         
        if attrType == 'DeviceConnectivity':
            self.BLUETOOTHin = True
            self.BLUETOOTHtotal += 1            
            self.printObservable('BLUETOOTH', self.BLUETOOTHtotal)            
            self.storeTraceStatus(self.BLUETOOTHstatus, BLUETOOTHstate, self.BLUETOOTHdeleted)
            self.skipLine = True 
            self.Observable = True
            self.BLUETOOTHid.append(BLUETOOTHid)
            self.BLUETOOTHkeys.append('')
            self.BLUETOOTHvalues.append('')
        elif attrType == 'KeyValueModel':
            self.BLUETOOTHinKeyValueModel = True
    
    def __startElementModelCALENDAR(self, attrValue, CALENDARid, CALENDARstate):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="CalendarEntry"]
            :param attrValue: Value of the attribute name of the ELement (string).
            :param CALENDARid: The value of the id attribute of the Element  (string).
            :param CALENDARstate: The value of the  deleted_state attribute of the Element  (string).
            :return:  None.
        '''         
        if attrValue == 'CalendarEntry':
            self.CALENDARin = True
            self.CALENDARtotal += 1
            self.printObservable('CALENDAR', self.CALENDARtotal)
            self.CALENDARid.append(CALENDARid)
            self.storeTraceStatus(self.CALENDARstatus, CALENDARstate, self.CALENDARdeleted)
            self.skipLine = True 
            self.Observable = True 

            self.CALENDARcategory.append('')
            self.CALENDARsubject.append('')
            self.CALENDARdetails.append('')
            self.CALENDARstartDate.append('')
            self.CALENDARendDate.append('')
            self.CALENDARrepeatUntil.append('')
            self.CALENDARrepeatDay.append('')
            self.CALENDARrepeatInterval.append('')

    def __startElementModelCELL_SITE(self, attrValue, CELL_SITEid, CELL_SITEstate):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="CellTower"]. In UCO/CASE the correspondent Observable
        is Cellsite.
            :param attrValue: Value of the attribute name of the ELement (string).
            :param CELL_SITEid: The value of the id attribute of the Element  (string).
            :param CELL_SITEstate: The value of the  deleted_state attribute of the Element  (string).
            :return:  None.
        '''         
        if attrValue == 'CellTower':
            self.CELL_SITEin = True
            self.CELL_SITEtotal += 1
            self.printObservable('CELL_SITE', self.CELL_SITEtotal)
            self.CELL_SITEid.append(CELL_SITEid)
            self.storeTraceStatus(self.CELL_SITEstatus, CELL_SITEstate, 
                self.CELL_SITEdeleted)
            self.skipLine = True 
            self.Observable = True 

            self.CELL_SITElongitude.append('')
            self.CELL_SITElatitude.append('')
            self.CELL_SITEtimeStamp.append('')
            self.CELL_SITEmcc.append('')
            self.CELL_SITEmnc.append('')
            self.CELL_SITElac.append('')
            self.CELL_SITEcid.append('')
            self.CELL_SITEnid.append('')
            self.CELL_SITEbid.append('')
            self.CELL_SITEsid.append('')

    def __startElementModelCHAT(self, attrType, CHATid, CHATstate):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="Chat"]
            :param attrValue: Value of the attribute name of the ELement (string).
            :param CHATid: The value of the id attribute of the Element  (string).
            :param CHATstate: The value of the  deleted_state attribute of the Element  (string).
            :return:  None.
        '''        
        if self.CHATinMultiModelFieldPhotos or \
            self.CHATinMultiModelFieldTo or \
            self.CHATinMultiModelFieldSharedContacts or \
            self.CHATinMultiModelFieldMessageExtraData:
            pass 
        elif attrType == 'Chat':
            self.CHATin = True
            self.CHATtotal += 1
            self.printObservable('CHAT', self.CHATtotal)
            self.CHATid.append(CHATid)
            self.storeTraceStatus(self.CHATstatus, CHATstate, self.CHATdeleted)
            self.skipLine = True 
            self.Observable = True 
            self.CHATsource.append('') 
        elif attrType == 'Party':
            if self.CHATinMultiModelFieldParticipants:
                self.CHATinParty = True
        elif attrType == 'InstantMessage': 
            self.CHATinInstantMessage = True
            self.CHATmsgStatus.append(CHATstate)
            self.CHATmsgNum += 1   
            self.CHATmsgIdentifierFrom.append('')
            self.CHATmsgNameFrom.append('')
#---    the body is initialised with a space text, instead of an empty value. 
#       This allows to iterate on this item, otherwise in case the body is empty
#       it will be ignored and no MessageFacet will be generated                
            self.CHATmsgBody.append(' ')
            self.CHATmsgOutcome.append('')
            self.CHATmsgTimeStamp.append('')
            self.CHATmsgAttachmentFilename.append('')
            self.CHATmsgAttachmentUrl.append('')
        elif attrType == 'Attachment':
            self.CHATinMsgAttachment = True
                
    def __startElementModelCONTACT(self, attrValue, CONTACTid, CONTACTstate):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="Contact"]
            :param attrValue: Value of the attribute name of the ELement (string).
            :param CONTACTid: The value of the id attribute of the Element  (string).
            :param CONTACTstate: The value of the  deleted_state attribute of the Element  (string).
            :return:  None.
        '''          
        if self.CONTACTinMultiModelFieldPhotos:
            pass            
        elif self.CONTACTinMultiModelFieldEntries:
            if attrValue == 'UserID':
                self.CONTACTinModelUserId = True
            elif attrValue == "PhoneNumber":
                self.CONTACTinModelPhoneNumber  = True
            elif attrValue == "ProfilePicture":
                self.CONTACTinModelProfilePicture = True # to be ignored
        elif attrValue == 'Contact':
            self.CONTACTin = True
            self.CONTACTtotal += 1
            self.printObservable('CONTACT', self.CONTACTtotal)
            self.skipLine = True  
            self.Observable = True 
            self.CONTACTid.append(CONTACTid)
            self.storeTraceStatus(self.CONTACTstatus, CONTACTstate, self.CONTACTdeleted)        
            self.CONTACTsource.append('')
            self.CONTACTname.append('')                
            self.CONTACTaccount.append('')

    def __startElementModelCOOKIE(self, attrValue, COOKIEid, COOKIEstate):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="Cookie"]
            :param attrValue: Value of the attribute name of the ELement (string).
            :param COOKIEid: The value of the id attribute of the Element  (string).
            :param COOKIEstate: The value of the  deleted_state attribute of the Element  (string).
            :return:  None.
        '''        
        if attrValue == 'Cookie':
            self.COOKIEin = True
            self.COOKIEtotal += 1
            self.printObservable('COOKIE', self.COOKIEtotal)
            self.COOKIEid.append(COOKIEid)
            self.storeTraceStatus(self.COOKIEstatus, COOKIEstate, 
                self.COOKIEdeleted)
            self.skipLine = True 
            self.Observable = True 

            self.COOKIEsource.append('')
            self.COOKIEname.append('')
            self.COOKIEvalue.append('')
            self.COOKIEdomain.append('')
            self.COOKIEcreationTime.append('')
            self.COOKIElastAccessTime.append('')
            self.COOKIEexpiry.append('')


    def __startElementModelDEVICE_EVENT(self, attrValue, DEVICE_EVENTid, DEVICE_EVENTstate):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="DeviceEvent"]
            :param attrValue: Value of the attribute name of the ELement (string).
            :param DEVICE_EVENTid: The value of the id attribute of the Element  (string).
            :param DEVICE_EVENTstate: The value of the  deleted_state attribute of the Element  (string).
            :return:  None.
        '''        
        if attrValue == 'DeviceEvent':
            self.DEVICE_EVENTin = True
            self.DEVICE_EVENTtotal += 1
            self.printObservable('DEVICE_EVENT', self.DEVICE_EVENTtotal)
            self.DEVICE_EVENTid.append(DEVICE_EVENTid)
            self.storeTraceStatus(self.DEVICE_EVENTstatus, DEVICE_EVENTstate, 
                self.DEVICE_EVENTdeleted)
            self.skipLine = True 
            self.Observable = True 

            self.DEVICE_EVENTtimeStamp.append('')
            self.DEVICE_EVENTeventType.append('')
            self.DEVICE_EVENTvalue.append('')

    def __startElementModelEMAIL(self, attrValue, EMAILid, EMAILstate):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="Email"]
            :param attrValue: Value of the attribute name of the ELement (string).
            :param EMAILid: The value of the id attribute of the Element  (string).
            :param EMAILstate: The value of the  deleted_state attribute of the Element  (string).
            :return:  None.
        '''        
        if attrValue == 'Email':                
            self.EMAILin = True
            self.EMAILtotal += 1
            self.printObservable('EMAIL', self.EMAILtotal)
            self.EMAILid.append(EMAILid)
            self.storeTraceStatus(self.EMAILstatus, EMAILstate, self.EMAILdeleted) 
            self.skipLine = True  
            self.Observable = True 

            self.EMAILsource.append('')
            self.EMAILidentifierFROM.append('')
            self.EMAILbody.append('')
            self.EMAILsubject.append('')
            self.EMAILtimeStamp.append('')


    def __startElementModelINSTANT_MSG(self, attrValue, INSTANT_MSGid, INSTANT_MSGstate):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="InstantMessage"]
            :param attrValue: Value of the attribute name of the ELement (string).
            :param INSTANT_MSGid: The value of the id attribute of the Element  (string).
            :param INSTANT_MSGstate: The value of the  deleted_state attribute of the Element  (string).
            :return:  None.
        '''         
        if attrValue == 'InstantMessage':
            self.INSTANT_MSGin = True
            self.INSTANT_MSGtotal += 1
            self.printObservable('INSTANT_MSG', self.INSTANT_MSGtotal)
            self.INSTANT_MSGid.append(INSTANT_MSGid)
            self.storeTraceStatus(self.INSTANT_MSGstatus, INSTANT_MSGstate, 
                self.INSTANT_MSGdeleted)
            self.skipLine = True 
            self.Observable = True 

            self.INSTANT_MSGsource.append('')
            self.INSTANT_MSGfromIdentifier.append('')
            self.INSTANT_MSGfromName.append('')
            self.INSTANT_MSGtoIdentifier.append('')
            self.INSTANT_MSGtoName.append('')
            self.INSTANT_MSGsubject.append('')
            self.INSTANT_MSGbody.append('')
            self.INSTANT_MSGtimeStamp.append('')
            self.INSTANT_MSGstatusMsg.append('')
            self.INSTANT_MSGtype.append('')
            self.INSTANT_MSGfolder.append('')
            self.INSTANT_MSGapplication.append('')

    def __startElementModelLOCATION(self, attrValue, LOCATIONid, LOCATIONstate):        
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="Location"]
            :param attrValue: Value of the attribute name of the ELement (string).
            :param LOCATIONid: The value of the id attribute of the Element  (string).
            :param LOCATIONstate: The value of the  deleted_state attribute of the Element  (string).
            :return:  None.
        '''        
        if attrValue == 'Location':
            self.LOCATIONtotal += 1
            self.LOCATIONin = True                                                    
            self.printObservable('LOCATION', self.LOCATIONtotal)
            self.LOCATIONid.append(LOCATIONid)
            self.storeTraceStatus(self.LOCATIONstatus, LOCATIONstate,
                self.LOCATIONdeleted)
            self.skipLine = True
            self.Observable = True                
            self.LOCATIONlongitude.append('')
            self.LOCATIONlatitude.append('')
            self.LOCATIONaltitude.append('')
            self.LOCATIONtimeStamp.append('')
            self.LOCATIONcategory.append('')      

    def __startElementModelSEARCHED_ITEM(self, attrValue, SEARCHED_ITEMid, SEARCHED_ITEMstate):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="SearchedItem"]
            :param attrValue: Value of the attribute name of the ELement (string).
            :param SEARCHED_ITEMid: The value of the id attribute of the Element  (string).
            :param SEARCHED_ITEMstate: The value of the  deleted_state attribute of the Element  (string).
            :return:  None.
        '''        
        if attrValue == 'SearchedItem':
            self.SEARCHED_ITEMin = True
            self.SEARCHED_ITEMtotal += 1
            self.printObservable('SEARCHED_ITEM', self.SEARCHED_ITEMtotal)
            self.SEARCHED_ITEMid.append(SEARCHED_ITEMid)
            self.storeTraceStatus(self.SEARCHED_ITEMstatus, SEARCHED_ITEMstate, 
                self.SEARCHED_ITEMdeleted)
            self.skipLine = True 
            self.Observable = True 
            
            self.SEARCHED_ITEMsource.append('')
            self.SEARCHED_ITEMtimeStamp.append('')
            self.SEARCHED_ITEMvalue.append('')
            self.SEARCHED_ITEMsearchResult.append('')

    def __startElementModelSMS(self, attrValue, SMSid, SMSstate):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="SMS"]
            :param attrValue: Value of the attribute name of the ELement (string).
            :param SMSid: The value of the id attribute of the Element  (string).
            :param SMSstate: The value of the  deleted_state attribute of the Element  (string).
            :return:  None.
        '''        
        if attrValue == 'SMS':                
            self.SMSin = True
            self.SMStotal += 1
            self.printObservable('SMS', self.SMStotal)
            self.SMSid.append(SMSid)
            self.storeTraceStatus(self.SMSstatus, SMSstate, self.SMSdeleted) 
            self.skipLine = True 
            self.Observable = True  

    def __startElementModelSOCIAL_MEDIA(self, attrValue, SOCIAL_MEDIAid, SOCIAL_MEDIAstate):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="SocialMediaActivity"]
            :param attrValue: Value of the attribute name of the ELement (string).
            :param SOCIAL_MEDIAid: The value of the id attribute of the Element  (string).
            :param SOCIAL_MEDIAstate: The value of the  deleted_state attribute of the Element  (string).
            :return:  None.
        '''         
        if attrValue == 'SocialMediaActivity':
            self.SOCIAL_MEDIAtotal += 1
            self.SOCIAL_MEDIAin = True                                                    
            self.printObservable('SOCIAL_MEDIA', self.SOCIAL_MEDIAtotal)
            self.SOCIAL_MEDIAid.append(SOCIAL_MEDIAid)
            self.storeTraceStatus(self.SOCIAL_MEDIAstatus, SOCIAL_MEDIAstate,
                self.SOCIAL_MEDIAdeleted)
            self.skipLine = True
            self.Observable = True

            self.SOCIAL_MEDIAsource.append('')
            self.SOCIAL_MEDIAtimeStamp.append('')
            self.SOCIAL_MEDIAbody.append('')
            self.SOCIAL_MEDIAtitle.append('')
            self.SOCIAL_MEDIAurl.append('')
            self.SOCIAL_MEDIAidentifier.append('')
            self.SOCIAL_MEDIAname.append('')
            self.SOCIAL_MEDIAreactionsCount.append('')
            self.SOCIAL_MEDIAsharesCount.append('')
            self.SOCIAL_MEDIAactivityType.append('')
            self.SOCIAL_MEDIAcommentCount.append('')
            self.SOCIAL_MEDIAaccount.append('')

    def __startElementModelU_ACCOUNT(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="UserAccount"]
            :param attrValue: Value of the attribute name of the Element (string).
            :return:  None.
        '''          
        if attrValue == 'UserAccount':
            self.U_ACCOUNTin = True
            self.U_ACCOUNTtotal+=1
            self.printObservable('U_ACCOUNT', self.U_ACCOUNTtotal)
            self.skipLine = True  
            self.Observable = True 
        elif attrValue == "ContactPhoto":
            if self.U_ACCOUNTin:
                self.U_ACCOUNTinContactPhoto = True
        elif attrValue == "ContactEntry":
            if self.U_ACCOUNTin:
                self.U_ACCOUNTinContactEntry = True
        elif attrValue == "EmailAddress":
            if self.U_ACCOUNTin:
                self.U_ACCOUNTinEmailAddress = True
        elif attrValue == "UserID":
            if self.U_ACCOUNTin:
                self.U_ACCOUNTinUserID = True


    def __startElementModelWEB_PAGE(self, attrValue, WEB_PAGEid, WEB_PAGEstate):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="VisitedPage"]
            :param attrValue: Value of the attribute name of the ELement (string).
            :param WEB_PAGEid: The value of the id attribute of the Element  (string).
            :param WEB_PAGEstate: The value of the  deleted_state attribute of the Element  (string).
            :return:  None.
        '''         
        if attrValue == 'VisitedPage':                
            self.WEB_PAGEin = True
            self.WEB_PAGEtotal += 1
            self.printObservable('WEB_HISTORY', self.WEB_PAGEtotal)
            self.WEB_PAGEid.append(WEB_PAGEid)
            self.storeTraceStatus(self.WEB_PAGEstatus, WEB_PAGEstate, self.WEB_PAGEdeleted) 
            self.skipLine = True 
            self.Observable = True  

    def __startElementModelWIRELESS_NET(self, attrValue, WIRELESS_NETid, WIRELESS_NETstate):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="WirelessNetwork"]
            :param attrValue: Value of the attribute name of the ELement (string).
            :param WIRELESS_NETid: The value of the id attribute of the Element  (string).
            :param WIRELESS_NETstate: The value of the  deleted_state attribute of the Element  (string).
            :return:  None.
        '''         
        if attrValue == 'WirelessNetwork':
            self.WIRELESS_NETtotal += 1
            #if self.ARTIFACTmax > self.WIRELESS_NETtotal:                
            self.WIRELESS_NETin = True                                        
            self.printObservable('WIRELESS_NET', self.WIRELESS_NETtotal)
            self.WIRELESS_NETid.append(WIRELESS_NETid)
            self.storeTraceStatus(self.WIRELESS_NETstatus, WIRELESS_NETstate, 
                self.WIRELESS_NETdeleted)
            self.skipLine = True 
            self.Observable = True 

            self.WIRELESS_NETlongitude.append('')
            self.WIRELESS_NETlatitude.append('')
            self.WIRELESS_NETtimeStamp.append('')
            self.WIRELESS_NETlastConnection.append('')
            self.WIRELESS_NETbssid.append('')
            self.WIRELESS_NETssid.append('')
                
    def __startElementMultiModelFieldCALENDAR(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="CalendarEntry"]/multiModelField[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''         
        if self.CALENDARin:
            if attrValue == 'Attendees':
                self.CALENDARinAttendees = True
            elif attrValue == 'Attachments':
                self.CALENDARinAttachments = True

    def __startElementMultiModelFieldCONTACT(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="Contact"]/multiModelField[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if self.CONTACTin:  
            if attrValue == 'Photos':
                self.CONTACTinMultiModelFieldPhotos = True
            elif attrValue == 'Entries':
                self.CONTACTinMultiModelFieldEntries = True

    def __startElementMultiModelFieldEMAIL(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="Email"]/multiModelField[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if self.EMAILin:            
            if attrValue == 'To':
                self.EMAILinMultiModelFieldTO = True
                self.EMAILidentifierTO.append('')
            elif attrValue == 'Cc':
                self.EMAILinMultiModelFieldCC = True
                self.EMAILidentifierCC.append('')
            elif attrValue == 'Bcc':
                self.EMAILinMultiModelFieldBCC = True
                self.EMAILidentifierBCC.append('')
            elif attrValue == 'Attachments':
                self.EMAILinMultiModelFieldAttachments = True
                self.EMAILattachmentFilename.append('')

    def __startElementMultiModelFieldCHAT(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="Chat"]/multiModelField[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''            
        if attrValue == 'Participants':
            self.CHATinMultiModelFieldParticipants = True
        elif attrValue == 'Photos':
            self.CHATinMultiModelFieldPhotos = True
        elif attrValue == 'Attachments':
            self.CHATinMultiModelFieldAttachments = True
        elif attrValue == 'SharedContacts':
            self.CHATinMultiModelFieldSharedContacts = True
        elif attrValue == 'MessageExtraData':
            self.CHATinMultiModelFieldMessageExtraData = True
        elif attrValue == 'To':
            self.CHATinMultiModelFieldTo = True

    def __startElementMultiModelFieldINSTANT_MSG(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="InstantMessage"]/multiModelField[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''            
        if self.INSTANT_MSGin:
            if attrValue == 'To':
                self.INSTANT_MSGinPartyTo = True
            elif attrValue == 'Attachments':
                self.INSTANT_MSGinAttachments = True
            elif attrValue == 'SharedContacts':
                self.INSTANT_MSGinSharedContacts = True
            
    def __startElementMultiModelFieldSOCIAL_MEDIA(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="SocialMediaActivity"]/multiModelField[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''            
        if self.SOCIAL_MEDIAin:
            if attrValue == 'Attachments':
                self.SOCIAL_MEDIAinAttachments = True
            elif attrValue == 'TaggedParties':
                self.SOCIAL_MEDIAinTaggedParties = True

    def __startElementMultiModelFieldSMS(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="SMS"]/multiModelField[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''
        if attrValue == 'Parties':
            self.SMSinParty = True 
        elif attrValue == 'AllTimeStamps':
            self.SMSinAllTimeStamps = True
                        
    def __startElementModelFieldCELL_SITE(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="CellTower"]//modelField[@Position=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''
        if attrValue == 'Position':
            self.CELL_SITEinPosition = True
            
    def __startElementModelFieldCHAT(self, attrName): 
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="Chat"]//modelField[@name=...]
            :param attrName: Name of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if attrName == 'From':
            self.CHATinMsgFrom = True
        if attrName == 'Attachment':
            self.CHATinModelFieldAttachment = True
              
    def __startElementModelFieldEMAIL(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="Email"]//modelField[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''
        if attrValue == 'From':
            self.EMAILinModelFieldFROM = True

    def __startElementModelFieldLOCATION(self, attrName):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="Location"]//modelField[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if attrName == 'Position':
            self.LOCATIONinPosition = True

    def __startElementModelFieldSOCIAL_MEDIA(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="SocialMediaActivity"]//modelField[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if attrValue == 'Author':
            self.SOCIAL_MEDIAinAuthor = True

    def __startElementModelFieldINSTANT_MSG(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="InstantMessage"]//modelField[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if attrValue == 'From':
            self.INSTANT_MSGinPartyFrom = True
        elif attrValue == 'Attachment':
            self.INSTANT_MSGinAttachment = True                    

    def __startElementModelFieldWIRELESS_NET(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="WirelessNetwork"]//modelField[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if attrValue == 'Position':
            self.WIRELESS_NETinPosition = True
    
    def __startElementFieldCALL(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="Call"]/field[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if self.CALLinParty:
            if attrValue == 'Identifier':
                self.CALLinIdentifier = True
            elif attrValue == 'Role':
                self.CALLinRole = True            
            elif attrValue == 'Name':
                self.CALLinName = True            
        else:
            if attrValue == 'Source':
                self.CALLinSource = True            
            elif attrValue == 'Direction':
                self.CALLinDirection = True
            elif attrValue == 'Type':
                self.CALLinType = True
            elif attrValue == 'Status':                
                self.CALLinOutcome = True
            elif attrValue == 'TimeStamp':
                self.CALLinTimeStamp = True                       
            elif attrValue == 'Duration':
                self.CALLinDuration = True
            
    def __startElementFieldBLUETOOTH(self, attrName):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="DeviceIdentifiers"]/field[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if self.BLUETOOTHinKeyValueModel:
            if attrName == 'Key':
                self.BLUETOOTHinKey = True
            elif attrName == 'Value':
                self.BLUETOOTHinValue = True
            
    def __startElementFieldCALENDAR(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="Calendar"]/field[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if attrValue == 'Category':
            self.CALENDARinCategory = True
        elif attrValue == 'Subject':
            self.CALENDARinSubject = True               
        elif attrValue == 'Details':
            self.CALENDARinDetails = True
        elif attrValue == 'StartDate':
            self.CALENDARinStartDate = True
        elif attrValue == 'EndDate':
            self.CALENDARinEndDate= True
        elif attrValue == 'RepeatUntil':
            self.CALENDARinRepeatUntil = True
        elif attrValue == 'RepeatDay':
            self.CALENDARinRepeatDay = True
        elif attrValue == 'RepeatInterval':
            self.CALENDARinRepeatUntil = True

    def __startElementFieldCELL_SITE(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="CellTower"]/field[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if attrValue == 'Longitude':
            self.CELL_SITEinLongitude = True
        elif attrValue == 'Latitude':
            self.CELL_SITEinLatitude = True
        elif attrValue == 'TimeStamp':
            self.CELL_SITEinTimeStamp = True
        elif attrValue == 'MCC':
            self.CELL_SITEinMCC = True
        elif attrValue == 'MNC':
            self.CELL_SITEinMNC = True        
        elif attrValue == 'LAC':
            self.CELL_SITEinLAC = True
        elif attrValue == 'CID':
            self.CELL_SITEinCID = True
        elif attrValue == 'NID':
            self.CELL_SITEinNID = True
        elif attrValue == 'BID':
            self.CELL_SITEinBID = True
        elif attrValue == 'SID':
            self.CELL_SITEinSID = True

    def __startElementFieldDEVICE_EVENT(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="DeviceEvent"]/field[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if attrValue == 'StartTime':
            self.DEVICE_EVENTinTimeStamp = True
        elif attrValue == 'EventType':
            self.DEVICE_EVENTinEventType = True
        elif attrValue == 'Value':
            self.DEVICE_EVENTinValue = True

    def __startElementFieldCHAT(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="Chat"]/field[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if self.CHATinModelType:            
            if attrValue == 'Identifier':
                if self.CHATinMsgFrom:
                    self.CHATinMsgIdentifierFrom = True
                elif self.CHATinParty:
                    self.CHATinPartyIdentifier = True
            elif attrValue == 'Name':
                if self.CHATinMsgFrom:
                    self.CHATinMsgNameFrom = True
                elif self.CHATinParty:
                    self.CHATinPartyName = True   
            elif attrValue == 'Body':
                self.CHATinMsgBody = True
            elif attrValue == 'TimeStamp':
                self.CHATinMsgTimeStamp = True
            elif attrValue == 'Status':
                self.CHATinMsgOutcome = True
            elif attrValue =='Filename':
                if self.CHATinMsgAttachment:
                    self.CHATinMsgAttachmentFilename = True                
            elif attrValue =='URL':
                if self.CHATinMsgAttachment:
                    self.CHATinMsgAttachmentUrl = True
            elif attrValue == 'Source':
                self.CHATinSource = True

    def __startElementFieldCONTACT(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="Contact"]/field[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if (self.CONTACTinMultiModelFieldPhotos or  
            self.CONTACTinModelProfilePicture):
            pass 
        elif self.CONTACTinModelUserId:
            if attrValue == 'Value':
                self.CONTACTinUserId = True 
        elif self.CONTACTinModelPhoneNumber:
            if attrValue == 'Value':
                self.CONTACTinPhoneNum = True
        else:
            if attrValue == 'Source':
                self.CONTACTinSource = True
            elif attrValue == 'Name':
                self.CONTACTinName = True                
            elif attrValue == 'Account':
                self.CONTACTinAccount = True

    def __startElementFieldCOOKIE(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="Cookie"]/field[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if attrValue == 'Source':
            self.COOKIEinSource = True
        elif attrValue == 'Name':
            self.COOKIEinName = True
        elif attrValue == 'Value':
            self.COOKIEinValue = True
        elif attrValue == 'Domain':
            self.COOKIEinDomain = True
        elif attrValue == 'CreationTime':
            self.COOKIEinCreationTime = True
        elif attrValue == 'LastAccessTime':
            self.COOKIEinLastAccessTime = True
        elif attrValue == 'Expiry':
            self.COOKIEinExpiry = True

    def __startElementFieldEMAIL(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="Email"]/field[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if self.EMAILinModelFieldFROM:
            if attrValue == 'Identifier':
                self.EMAILinIdentifierFROM = True
        elif self.EMAILinMultiModelFieldTO:
            if attrValue == 'Identifier':
                self.EMAILinIdentifierTO = True
        elif self.EMAILinMultiModelFieldCC:
            if attrValue == 'Identifier':
                self.EMAILinIdentifierCC = True
        elif self.EMAILinMultiModelFieldBCC:
            if attrValue == 'Identifier':
                self.EMAILinIdentifierBCC = True
        elif self.EMAILinMultiModelFieldAttachments:
            if attrValue == 'Filename':
                self.EMAILinAttachmentFilename = True
            #if attrValue == 'URL': # not processed so far
                #pass 
        else:
            if attrValue == 'Source':
                self.EMAILinSource = True
            elif attrValue == 'Subject':
                self.EMAILinSubject = True
            elif attrValue == 'Body':
                self.EMAILinBody = True
            elif attrValue == 'TimeStamp':
                self.EMAILinTimeStamp = True
    
    def __startElementFieldCONTEXT(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //caseInformation/field[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if self.CONTEXTinCaseInfo:
            if attrValue == 'ExaminerName':
                self.CONTEXTinExaminerNameValue = True

    def __startElementFieldINSTANT_MSG(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="InstantMessage"]/field[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''
        if attrValue == 'Source':
            self.INSTANT_MSGinSource = True
        elif attrValue == 'Identifier':
            if self.INSTANT_MSGinPartyFrom:
                self.INSTANT_MSGinFromIdentifier = True
            elif self.INSTANT_MSGinPartyTo:
                self.INSTANT_MSGinToIdentifier = True
        elif attrValue == 'Name':
            if self.INSTANT_MSGinPartyFrom:
                self.INSTANT_MSGinFromName = True
            elif self.INSTANT_MSGinPartyTo:
                self.INSTANT_MSGinToName = True
        elif attrValue == 'Subject':
            self.INSTANT_MSGinSubject = True
        elif attrValue == 'Body':
            self.INSTANT_MSGinBody = True
        elif attrValue == 'TimeStamp':
            self.INSTANT_MSGinTimeStamp = True
        elif self.INSTANT_MSGinAttachments:
            pass
        elif self.INSTANT_MSGinAttachment:
            pass
        elif self.INSTANT_MSGinSharedContacts:
            pass
        elif attrValue == 'Status':
            self.INSTANT_MSGinStatusMsg = True
        elif attrValue == 'Type':
            self.INSTANT_MSGinType = True
        elif attrValue == 'Folder':
            self.INSTANT_MSGinFolder = True
        elif attrValue == 'SourceApplication':
            self.INSTANT_MSGinApplication = True

    def __startElementFieldLOCATION(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="Location"]/field[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if attrValue == 'Longitude':
            self.LOCATIONinLongitude = True
        elif attrValue == 'Latitude':
            self.LOCATIONinLatitude = True
        elif attrValue == 'Elevation':
            self.LOCATIONinAltitude = True
        elif attrValue == 'TimeStamp':
            self.LOCATIONinTimeStamp = True
        elif attrValue == 'Category':
            self.LOCATIONinCategory = True

    def __startElementFieldSEARCHED_ITEM(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="SearchedItem"]/field[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if attrValue == 'Source':
            self.SEARCHED_ITEMinSource = True
        elif attrValue == 'TimeStamp':
            self.SEARCHED_ITEMinTimeStamp = True
        elif attrValue == 'Value':
            self.SEARCHED_ITEMinValue = True

    def __startElementFieldSMS(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="SMS"]/field[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if self.SMSinParty:
            if attrValue == 'Identifier':
                self.SMSinPartyIdentifier = True
            elif attrValue == 'Role':
                self.SMSinPartyRole = True      
            elif attrValue == 'Name':
                self.SMSinPartyName = True
        else:
            if attrValue == 'Source':
                self.SMSinSource = True
            elif attrValue == 'TimeStamp':
                self.SMSinTimeStamp = True
            elif attrValue == 'Body':
                self.SMSinBody = True
            elif attrValue == 'Folder':
                self.SMSinFolder = True
            elif attrValue == 'SMSC':
                self.SMSinSmsc = True
             
    def __startElementFieldSOCIAL_MEDIA(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="SocialActivityType"]/field[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if not self.SOCIAL_MEDIAinAttachments:
            if attrValue == 'Source':
                self.SOCIAL_MEDIAinSource = True
            elif attrValue == 'TimeStamp':
                self.SOCIAL_MEDIAinTimeStamp = True
            elif attrValue == 'Body':
                self.SOCIAL_MEDIAinBody = True
            elif attrValue == 'Title':
                self.SOCIAL_MEDIAinTitle = True
            elif attrValue == 'Url':
                self.SOCIAL_MEDIAinUrl = True
            elif attrValue == 'ReactionsCount':
                self.SOCIAL_MEDIAinReactionsCount = True
            elif attrValue == 'SharesCount':
                self.SOCIAL_MEDIAinSharesCount = True
            elif attrValue == 'SocialActivityType':
                self.SOCIAL_MEDIAinActivityType = True
            elif attrValue == 'CommentCount':
                self.SOCIAL_MEDIAinCommentCount = True
            elif attrValue == 'Account':
                self.SOCIAL_MEDIAinAccount = True
            elif self.SOCIAL_MEDIAinAuthor:
                if attrValue == 'Identifier':
                    self.SOCIAL_MEDIAinIdentifier = True
                if attrValue == 'Name':
                    self.SOCIAL_MEDIAinName = True

    def __startElementFieldU_ACCOUNT(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="UserAccount"]/field[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if self.U_ACCOUNTinContactPhoto:
            return(0)
        elif self.U_ACCOUNTinEmailAddress:
            return(0)
        elif self.U_ACCOUNTinUserID:
            return(0)
        elif attrValue == 'Source':
            self.U_ACCOUNTinSource = True
        elif attrValue == 'Name':
            self.U_ACCOUNTinName = True
        elif attrValue == 'Username':
            self.U_ACCOUNTinUsername = True

    def __startElementFieldWEB_PAGE(self, attrValue):        
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="VisitedPage"]/field[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if attrValue == 'Source':
            self.WEB_PAGEinSource = True
        elif attrValue == 'Title':
            self.WEB_PAGEinTitle = True
        elif attrValue == 'Url':
            self.WEB_PAGEinUrl = True
        elif attrValue == 'LastVisited':
            self.WEB_PAGEinLastVisited = True
        elif attrValue == 'VisitCount':
            self.WEB_PAGEinVisitCount = True
        

    def __startElementFieldWIRELESS_NET(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/model[@type="WirelessNetwork"]/field[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''
        if attrValue == 'Longitude':
            self.WIRELESS_NETinLongitude = True
        elif attrValue == 'Latitude':
            self.WIRELESS_NETinLatitude = True
        elif attrValue == 'TimeStamp':
            self.WIRELESS_NETinTimeStamp = True
        elif attrValue == 'LastConnection':
            self.WIRELESS_NETinLastConnection = True
        elif attrValue == 'BSSId':
            self.WIRELESS_NETinBssid = True
        elif attrValue == 'SSId':
            self.WIRELESS_NETinSsid = True

    def __startElementItemCONTEXT(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //metadata[@section="Additional Fields"]/item[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if self.CONTEXTinAdditionalFields:
            if attrValue == 'DeviceInfoCreationTime':
                self.CONTEXTinDeviceCreationTimeValue = True
            elif attrValue == 'UFED_PA_Version':
                self.CONTEXTinUfedVersionValue = True
        
        if self.CONTEXTinExtractionData:
            if attrValue == 'DeviceInfoExtractionStartDateTime':
                self.CONTEXTinDeviceExtractionStart = True
            elif attrValue == 'DeviceInfoExtractionEndDateTime':
                self.CONTEXTinDeviceExtractionEnd = True

        if self.CONTEXTinDeviceInfo:            
            if attrValue == 'DeviceInfoOSVersion':
                self.CONTEXTinDeviceOsVersionValue = True
            elif attrValue == 'DeviceInfoDetectedPhoneVendor':
                self.CONTEXTinDevicePhoneVendorValue = True
            elif attrValue == 'DeviceInfoDetectedPhoneModel':
                self.CONTEXTinDevicePhoneModelValue = True
            elif attrValue in ('DeviceInfoAppleID', 'DeviceInfoAndroidID'):
                self.CONTEXTinDeviceIdValue = True
            elif attrValue in ('Indirizzo MAC', 'Mac Address', 'DeviceInfoWiFiMACAddress'):
                self.CONTEXTinDeviceMacAddressValue = True
            elif attrValue == 'ICCID':
                self.CONTEXTinDeviceIccidValue = True
            elif attrValue in ('MSISDN', 'LastUsedMSISDN'):
                self.CONTEXTinDeviceMsisdnValue = True
            elif attrValue in ('Indirizzo MAC Bluetooth', 'Bluetooth MAC Address', 
                'DeviceInfoBluetoothDeviceAddress'):
                self.CONTEXTinDeviceBluetoothAddressValue = True
            elif attrValue == 'DeviceInfoBluetoothDeviceName':
                self.CONTEXTinDeviceBluetoothName = True 
            elif attrValue == 'IMSI':
                self.CONTEXTinDeviceImsiValue = True
            elif attrValue == 'IMEI':
                self.CONTEXTinDeviceImeiValue = True
            elif attrValue == 'DeviceInfoOSType':
                self.CONTEXTinDeviceOsTypeValue = True

        if self.CONTEXTinImageMetadataHash:
            if attrValue == 'SHA256':
                self.CONTEXTinImageMetadataHashValueSHA = True
            elif attrValue =='MD5':
                self.CONTEXTinImageMetadataHashValueMD5 = True

    def __startElementMultiFieldSEARCHED_ITEM(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="SearchedItem"]/field[@name=...]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''        
        if attrValue == 'SearchResults':
            self.SEARCHED_ITEMinSearchResult = True

    def __startElementItemTAGGED_FILES(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //taggedFiles//metadata/item[@name="..."]
            :param attrValue: Value of the attribute name of the ELement (string).
            :return:  None.
        '''           
        if self.TAGGED_FILESinFile:
            if self.TAGGED_FILESsystem:
                pass
            else:
                if attrValue == 'MD5':
                    self.TAGGED_FILESinMD5 = True
                elif attrValue == 'Tags':
                    self.TAGGED_FILESinTags = True
                elif attrValue == 'Local Path':
                    self.TAGGED_FILESinLocalPath = True
        
        if self.TAGGED_FILESinMetadata:
            if self.TAGGED_FILESsystem:
                pass
            else:
                if attrValue == 'Inode Number':
                    self.TAGGED_FILESinInodeNumber = True
                elif attrValue == 'CoreFileSystemFileSystemNodeModifyTime':
                    self.TAGGED_FILESinInodeTimeModify = True
                elif attrValue == 'Owner GID':
                    self.TAGGED_FILESinOwnerGID = True
                elif attrValue == 'Owner UID':
                    self.TAGGED_FILESinOwnerUID = True
                elif attrValue == 'ExifEnumGPSLatitudeRef':
                    self.TAGGED_FILESinExifLatitudeRef = True 
                elif attrValue == 'ExifEnumGPSLatitude':
                    self.TAGGED_FILESinExifLatitude = True
                elif attrValue == 'ExifEnumGPSLongitudeRef':
                    self.TAGGED_FILESinExifLongitudeRef = True
                elif attrValue == 'ExifEnumGPSLongitude':
                    self.TAGGED_FILESinExifLongitude = True
                elif attrValue == 'ExifEnumGPSAltitude':
                    self.TAGGED_FILESinExifAltitude = True
                elif attrValue == 'ExifEnumMake':
                    self.TAGGED_FILESinExifMake = True
                elif attrValue == 'ExifEnumModel':
                    self.TAGGED_FILESinExifModel = True

    def __startElementValueCALL(self):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="Call"]/field[@name=...]/value
            :return:  None.
        '''         
        if self.CALLinSource:
            self.CALLinSourceValue = True
        elif self.CALLinDirection:
            self.CALLinDirectionValue = True
        elif self.CALLinTimeStamp:
            self.CALLinTimeStampValue = True
        elif self.CALLinType:
            self.CALLinTypeValue = True
        elif self.CALLinDuration:
            self.CALLinDurationValue = True
        elif self.CALLinOutcome:
            self.CALLinOutcomeValue = True
        elif self.CALLinIdentifier:
            self.CALLinIdentifierValue = True
        elif self.CALLinRole:
            self.CALLinRoleValue = True
        elif self.CALLinName:
            self.CALLinNameValue = True            

    def __startElementValueBLUETOOTH(self):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //model[@type="KeyValueModel"]/field[@name=...]/value
            :return:  None.
        '''        
        if self.BLUETOOTHinKey:
            self.BLUETOOTHinKeyValue = True
        elif self.BLUETOOTHinValue:
            self.BLUETOOTHinValueValue = True
            
    def __startElementValueCALENDAR(self):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="CalendarEntry"]/field[@name=...]/value
            :return:  None.
        '''        
        if self.CALENDARinCategory:
            self.CALENDARinCategoryValue = True
        elif self.CALENDARinSubject:
            self.CALENDARinSubjectValue = True
        elif self.CALENDARinDetails:
            self.CALENDARinDetailsValue = True
        elif self.CALENDARinStartDate:
            self.CALENDARinStartDateValue = True
        elif self.CALENDARinEndDate:
            self.CALENDARinEndDateValue = True
        elif self.CALENDARinRepeatUntil:
            self.CALENDARinRepeatUntilValue = True
        elif self.CALENDARinRepeatDay:
            self.CALENDARinRepeatDayValue = True
        elif self.CALENDARinRepeatInterval:
            self.CALENDARinRepeatIntervalValue = True      

    def __startElementValueCELL_SITE(self):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="CellTower"]/field[@name=...]/value
            :return:  None.
        '''        
        if self.CELL_SITEinLongitude:
            self.CELL_SITEinLongitudeValue = True
        elif self.CELL_SITEinLatitude:
            self.CELL_SITEinLatitudeValue = True
        elif self.CELL_SITEinTimeStamp:
            self.CELL_SITEinTimeStampValue = True
        elif self.CELL_SITEinMCC:
            self.CELL_SITEinMCCValue = True
        elif self.CELL_SITEinMNC:
            self.CELL_SITEinMNCValue = True
        elif self.CELL_SITEinLAC:
            self.CELL_SITEinLACValue = True
        elif self.CELL_SITEinCID:
            self.CELL_SITEinCIDValue = True
        elif self.CELL_SITEinNID:
            self.CELL_SITEinNIDValue = True
        elif self.CELL_SITEinBID:
            self.CELL_SITEinBIDValue = True
        elif self.CELL_SITEinSID:
            self.CELL_SITEinSIDValue = True

    def __startElementValueCONTACT(self):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="Contact"]/field[@name=...]/value
            :return:  None.
        '''        
        if self.CONTACTinSource:
            self.CONTACTinSourceValue = True
        elif self.CONTACTinName:
            self.CONTACTinNameValue = True
        elif self.CONTACTinUserId:
            self.CONTACTinUserIdValue = True
        elif self.CONTACTinPhoneNum:
            self.CONTACTinPhoneNumValue = True
        elif self.CONTACTinAccount:
            self.CONTACTinAccountValue = True

    def __startElementValueCHAT(self, attrValue):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="Chat"]/field[@name=...]/value
            :return:  None.
        '''        
        if self.CHATinSource:
            self.CHATinSourceValue = True
        elif self.CHATinPartyIdentifier:
            self.CHATinPartyIdentifierValue = True
        elif self.CHATinPartyName:
            self.CHATinPartyNameValue = True
        elif self.CHATinMsgNameFrom:
            self.CHATinMsgNameFromValue = True
        elif self.CHATinMsgIdentifierFrom:
            self.CHATinMsgIdentifierFromValue = True
        elif self.CHATinMsgBody:
            self.CHATinMsgBodyValue = True
        elif self.CHATinMsgOutcome:
            if attrValue == "MessageStatus":
                self.CHATinMsgOutcomeValue = True
        elif self.CHATinMsgTimeStamp:
            self.CHATinMsgTimeStampValue = True
        elif self.CHATinMsgAttachmentFilename:
            self.CHATinMsgAttachmentFilenameValue = True
        elif self.CHATinMsgAttachmentUrl:
            self.CHATinMsgAttachmentUrlValue = True

    def __startElementValueCOOKIE(self):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="Cookie"]/field[@name=...]/value
            :return:  None.
        '''        
        if self.COOKIEinSource:
            self.COOKIEinSourceValue = True
        elif self.COOKIEinName:
            self.COOKIEinNameValue = True
        elif self.COOKIEinValue:
            self.COOKIEinValueValue = True
        elif self.COOKIEinDomain:
            self.COOKIEinDomainValue = True
        elif self.COOKIEinCreationTime:
            self.COOKIEinCreationTimeValue = True
        elif self.COOKIEinLastAccessTime:
            self.COOKIEinLastAccessTimeValue = True
        elif self.COOKIEinExpiry:
            self.COOKIEinExpiryValue = True

    def __startElementValueDEVICE_EVENT(self):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="DeviceEvent"]/field[@name=...]/value
            :return:  None.
        '''        
        if self.DEVICE_EVENTinTimeStamp:
            self.DEVICE_EVENTinTimeStampValue = True
        elif self.DEVICE_EVENTinEventType:
            self.DEVICE_EVENTinEventTypeValue = True
        elif self.DEVICE_EVENTinValue:
            self.DEVICE_EVENTinValueValue = True
        

    def __startElementValueEMAIL(self):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="Email"]/field[@name=...]/value
            :return:  None.
        '''        
        if self.EMAILinIdentifierFROM:
            self.EMAILinIdentifierFROMvalue = True
        elif self.EMAILinIdentifierTO:
            self.EMAILinIdentifierTOvalue = True
        elif self.EMAILinIdentifierCC:
            self.EMAILinIdentifierCCvalue = True
        elif self.EMAILinIdentifierBCC:
            self.EMAILinIdentifierBCCvalue = True
        elif self.EMAILinSource:
            self.EMAILinSourceValue = True
        elif self.EMAILinBody:
            self.EMAILinBodyValue = True
        elif self.EMAILinSubject:
            self.EMAILinSubjectValue = True
        elif self.EMAILinTimeStamp:
            self.EMAILinTimeStampValue = True
        elif self.EMAILinAttachmentFilename:
            self.EMAILinAttachmentFilenameValue = True

    def __startElementValueINSTANT_MSG(self):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="InstantMessage"]/field[@name=...]/value
            :return:  None.
        '''        
        if self.INSTANT_MSGinSource:
            self.INSTANT_MSGinSourceValue = True
        elif self.INSTANT_MSGinFromIdentifier:
            self.INSTANT_MSGinFromIdentifierValue = True
        elif self.INSTANT_MSGinFromName:
            self.INSTANT_MSGinFromNameValue = True
        elif self.INSTANT_MSGinToIdentifier:
            self.INSTANT_MSGinToIdentifierValue = True
        elif self.INSTANT_MSGinToName:
            self.INSTANT_MSGinToNameValue = True
        elif self.INSTANT_MSGinSubject:
            self.INSTANT_MSGinSubjectValue = True
        elif self.INSTANT_MSGinBody:
            self.INSTANT_MSGinBodyValue = True
        elif self.INSTANT_MSGinTimeStamp:
            self.INSTANT_MSGinTimeStampValue = True
        elif self.INSTANT_MSGinStatusMsg:
            self.INSTANT_MSGinStatusMsgValue = True
        elif self.INSTANT_MSGinType:
            self.INSTANT_MSGinTypeValue = True
        elif self.INSTANT_MSGinFolder:
            self.INSTANT_MSGinFolderValue = True
        elif self.INSTANT_MSGinApplication:
            self.INSTANT_MSGinApplicationValue = True

    def __startElementValueLOCATION(self):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="Location"]/field[@name=...]/value
            :return:  None.
        '''        
        if self.LOCATIONinLongitude:
            self.LOCATIONinLongitudeValue = True
        elif self.LOCATIONinLatitude:
            self.LOCATIONinLatitudeValue = True
        elif self.LOCATIONinAltitude:
            self.LOCATIONinAltitudeValue = True
        elif self.LOCATIONinTimeStamp:
            self.LOCATIONinTimeStampValue = True
        elif self.LOCATIONinCategory:
            self.LOCATIONinCategoryValue = True

    def __startElementValueSEARCHED_ITEM(self):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="SearchedItem"]/field[@name=...]/value
            :return:  None.
        '''        
        if self.SEARCHED_ITEMinSource:
            self.SEARCHED_ITEMinSourceValue = True
        elif self.SEARCHED_ITEMinTimeStamp:
            self.SEARCHED_ITEMinTimeStampValue = True
        elif self.SEARCHED_ITEMinValue:
            self.SEARCHED_ITEMinValueValue = True
        elif self.SEARCHED_ITEMinSearchResult:
            self.SEARCHED_ITEMinSearchResultValue = True

    def __startElementValueSMS(self):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="SMS"]/field[@name=...]/value
            :return:  None.
        '''        
        if self.SMSinSource:
            self.SMSinSourceValue = True
        elif self.SMSinTimeStamp:
            self.SMSinTimeStampValue = True
        elif self.SMSinBody:
            self.SMSinBodyValue = True
        elif self.SMSinFolder:
            self.SMSinFolderValue = True
        elif self.SMSinSmsc:
            self.SMSinSmscValue = True        
        elif self.SMSinPartyRole:
            self.SMSinPartyRoleValue = True            
        elif self.SMSinPartyIdentifier:
            self.SMSinPartyIdentifierValue = True        
        elif self.SMSinPartyName:
            self.SMSinPartyNameValue = True

    def __startElementValueSOCIAL_MEDIA(self):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="SocialMediaActivity"]/field[@name=...]/value
            :return:  None.
        '''        
        if self.SOCIAL_MEDIAinSource:
            self.SOCIAL_MEDIAinSourceValue = True
        elif self.SOCIAL_MEDIAinTimeStamp:
            self.SOCIAL_MEDIAinTimeStampValue = True
        elif self.SOCIAL_MEDIAinBody:
            self.SOCIAL_MEDIAinBodyValue = True
        elif self.SOCIAL_MEDIAinTitle:
            self.SOCIAL_MEDIAinTitleValue = True
        elif self.SOCIAL_MEDIAinUrl:                
            self.SOCIAL_MEDIAinUrlValue = True
        elif self.SOCIAL_MEDIAinIdentifier:
            self.SOCIAL_MEDIAinIdentifierValue = True
        elif self.SOCIAL_MEDIAinName:
            self.SOCIAL_MEDIAinNameValue = True
        elif self.SOCIAL_MEDIAinReactionsCount:
            self.SOCIAL_MEDIAinReactionsCountValue = True
        elif self.SOCIAL_MEDIAinSharesCount:
            self.SOCIAL_MEDIAinSharesCountValue = True
        elif self.SOCIAL_MEDIAinActivityType:
            self.SOCIAL_MEDIAinActivityTypeValue = True
        elif self.SOCIAL_MEDIAinCommentCount:
            self.SOCIAL_MEDIAinCommentCountValue = True
        elif self.SOCIAL_MEDIAinAccount:
            self.SOCIAL_MEDIAinAccountValue = True

    def __startElementValueU_ACCOUNT(self):        
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="Account"]/field[@name=...]/value
            :return:  None.
        '''        
        if self.U_ACCOUNTinSource:
            self.U_ACCOUNTinSourceValue = True
        elif self.U_ACCOUNTinName:
            self.U_ACCOUNTinNameValue = True
        elif self.U_ACCOUNTinUsername:
            self.U_ACCOUNTinUsernameValue = True

    def __startElementValueWEB_PAGE(self):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="VisitedPage"]/field[@name=...]/value
            :return:  None.
        '''        
        if self.WEB_PAGEinSource:
            self.WEB_PAGEinSourceValue = True
        elif self.WEB_PAGEinTitle:
            self.WEB_PAGEinTitleValue = True
        elif self.WEB_PAGEinUrl:
            self.WEB_PAGEinUrlValue = True 
        elif self.WEB_PAGEinVisitCount:
            self.WEB_PAGEinVisitCountValue = True
        elif self.WEB_PAGEinLastVisited:
            self.WEB_PAGEinLastVisitedValue = True    

    def __startElementValueWIRELESS_NET(self):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="WirelessNetwork"]/field[@name=...]/value
            :return:  None.
        '''        
        if self.WIRELESS_NETin:
            if self.WIRELESS_NETinLongitude:
                self.WIRELESS_NETinLongitudeValue = True
            elif self.WIRELESS_NETinLatitude:
                self.WIRELESS_NETinLatitudeValue = True
            elif self.WIRELESS_NETinTimeStamp:
                self.WIRELESS_NETinTimeStampValue = True
            elif self.WIRELESS_NETinLastConnection:
                self.WIRELESS_NETinLastConnectionValue = True
            elif self.WIRELESS_NETinBssid:
                self.WIRELESS_NETinBssidValue = True
            elif self.WIRELESS_NETinSsid:
                self.WIRELESS_NETinSsidValue = True

    def __startElementEmptyCALL(self):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="Call"]/field[@name=...]/empty
            :return:  None.
        '''        
        if self.CALLinSourceValue:
            self.CALLsourceText = ''

    def __startElementEmptyU_ACCOUNT(self):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="UserAccount"]/field[@name=...]/empty
            :return:  None.
        '''        
        if self.U_ACCOUNTinSource:
            self.U_ACCOUNTsourceValueText = ''
            self.U_ACCOUNTinSourceValue = False
        elif self.U_ACCOUNTinName:
            self.U_ACCOUNTnameValueText = ''
            self.U_ACCOUNTinNameValue = False
        elif self.U_ACCOUNTinUsername:
            self.U_ACCOUNTusernameValueText = ''
            self.U_ACCOUNTinUsernameValue = False

    def __startElementEmptyWEB_PAGE(self):
        '''
        It captures the opening of the XML Element matching with the XPath expression
        //modelType/multiField[@type="VisitedPage"]/field[@name=...]/empty
            :return:  None.
        '''        
        if self.WEB_PAGEinTitleValue:
            self.WEB_PAGEtitleText = ''
        elif self.WEB_PAGEinVisitCountValue:
            self.WEB_PAGEvisitCountText = ''
        elif self.WEB_PAGEinLastVisitedValue:
            self.WEB_PAGElastVisitedText = ''        
    
    def startElement(self, name, attrs):
        '''
        It captures the opening of any XML Element, the order depends on their 
        position from the beginning of the document.
            :return:  None.
        '''        
        self.lineXML +=1
        attrType = attrs.get('type')
        attrName = attrs.get('name')
        attrSection = attrs.get('section')
        
        if name == 'modelType':
            self.__startElementModelType(attrType)
            
        elif name == 'model':                                    
            traceState = attrs.get('deleted_state')
            id = attrs.get('id')
            self.__startElementModel(attrType, id, traceState)
                      
        elif name == 'multiModelField':
            self.__startMultiModelField(attrName)
            
        elif name == 'modelField':
            self.__startModelField(attrName)            
        elif name == 'multiField':
            if self.SEARCHED_ITEMin:
                self.__startElementMultiFieldSEARCHED_ITEM(attrName) 
        elif name == 'field':
            self.__startElementField(attrName, attrs)                                                              
        elif name == 'value':
            self.__startElementValue(attrType)            
        elif name == 'empty':
            self.__startElementEmptyCALL()
            self.__startElementEmptyU_ACCOUNT()
            self.__startElementEmptyWEB_PAGE()
        elif name == 'taggedFiles':
            self.TAGGED_FILESin = True

#---    extraInfo @id is the link with the Trace @id, for any kind of Trace 
#            
        elif name == 'extraInfo':
            self.EXTRA_INFOin = True
            self.EXTRA_INFOid = attrs.get('id')
            self.EXTRA_INFOlistId.append(self.EXTRA_INFOid)
            self.EXTRA_INFOdictPath[self.EXTRA_INFOid] = ''
            self.EXTRA_INFOdictSize[self.EXTRA_INFOid] = ''
            self.EXTRA_INFOdictTableName[self.EXTRA_INFOid] = ''
            self.EXTRA_INFOdictOffset[self.EXTRA_INFOid] = ''
            self.EXTRA_INFOdictNodeInfoId[self.EXTRA_INFOid] = ''
        elif name == 'nodeInfo':
            if self.EXTRA_INFOin:
                self.EXTRA_INFOnodeInfoin = True              

#---    key of the dictionaries containing the infoNode values.
#       Different values are separated by @@@
                i = self.EXTRA_INFOid

#---    in some cases there are more than one single nodeInfo
#       contained in the extraInfo element, so a dictionary with
#       key = extraInfoID is necessary to store the whole info                         
                if attrs.get('id') is None:                    
                    self.EXTRA_INFOdictNodeInfoId[i] = ''
                    charSep = ''
                else:
                    self.EXTRA_INFOdictNodeInfoId[i] += "".join(['@@@', attrs.get('id')])
                    charSep = '@@@'

                self.EXTRA_INFOdictPath[i] += "".join([charSep, str(attrs.get('path'))])
                self.EXTRA_INFOdictSize[i] += "".join([charSep, str(attrs.get('size'))])
                self.EXTRA_INFOdictTableName[i] += "".join([charSep, str(attrs.get('tableName'))])
                self.EXTRA_INFOdictOffset[i] += "".join([charSep, str(attrs.get('offset'))])
        elif name == 'file':
            if self.TAGGED_FILESin:                
                if attrs.get('fs').lower().find('system') > -1:
                    self.TAGGED_FILESsystem = True
                else:
                    self.TAGGED_FILESsystem = False
                    self.TAGGED_FILESinFile = True
                    self.FILEid.append(attrs.get('id'))
                    self.FILEpath.append(attrs.get('path'))
                    self.FILEsize.append(attrs.get('size'))
                    self.FILEtimeCreate.append('')
                    self.FILEtimeModify.append('')
                    self.FILEtimeAccess.append('')
                    self.FILEiNodeNumber.append('000')
                    self.FILEiNodeTimeModify.append('00-00-0000 00:00:00')
                    self.FILEownerGID.append('0')
                    self.FILEownerUID.append('0')
                    self.FILEexifLatitudeRef.append('')
                    self.FILEexifLatitude.append('')
                    self.FILEexifLongitudeRef.append('')
                    self.FILEexifLongitude.append('')
                    self.FILEexifAltitude.append('')
                    self.FILEexifMake.append('')
                    self.FILEexifModel.append('')
                    self.FILEidx += 1
        elif name == 'accessInfo':
            if self.TAGGED_FILESinFile:
                if self.TAGGED_FILESsystem:
                    pass
                else:
                    self.TAGGED_FILESinAccessInfo = True                
        elif name == "timestamp":
            if self.TAGGED_FILESinAccessInfo:
                if attrName == 'CreationTime':
                    self.TAGGED_FILESinAccessInfoCreate = True           
                if attrName == 'ModifyTime':
                    self.TAGGED_FILESinAccessInfoModify = True
                if attrName == 'AccessTime':
                    self.TAGGED_FILESinAccessInfoAccess = True
        elif name == 'metadata':
            if self.TAGGED_FILESin:
                if self.TAGGED_FILESsystem:
                    pass
                else:
                    if attrSection == "File":
                        self.TAGGED_FILESinFile = True
                    if attrSection == "MetaData":
                        self.TAGGED_FILESinMetadata = True
            else:               
                if attrSection == 'Additional Fields':
                    self.CONTEXTinAdditionalFields = True 

                if attrSection == 'Extraction Data':
                    self.CONTEXTinExtractionData = True
                
                if attrSection == 'Device Info':
                    self.CONTEXTinDeviceInfo = True

                if attrSection == 'Hashes':
                    if self.CONTEXTinImage:
                        self.CONTEXTinImageMetadataHash = True
        elif name == 'item':
            self.__startElementItemTAGGED_FILES(attrName)
            self.__startElementItemCONTEXT(attrName)
        elif name == 'images':
            self.CONTEXTinImages = True
        elif name == 'image':
            if self.CONTEXTinImages:
                self.CONTEXTinImage = True
                self.CONTEXTimagePath.append(attrs.get('path'))
                self.CONTEXTimageSize.append(attrs.get('size'))
        elif name == 'caseInformation':
            self.CONTEXTinCaseInfo = True                                     
        
        if (not self.Observable):
            line = "".join([self.C_GREY, '*\tProcessing Element <', name, '> at line ',  str(self.lineXML), ' ...', self.C_BLACK])
            if self.verbose:
                if self.skipLine:
                    print ('\n' + line , end='\r')
                    self.skipLine = False                  
                else:
                    print (line , end='\r') 

    def __startElementModelType(self, attrType):
        '''
        It captures the opening of any XML Element matching with the XPath expression
        //modelType/
            :return:  None.
        '''        
        self.Observable = False
        if attrType == 'Call':
            self.CALLinModelType = True
        elif attrType == "DeviceConnectivity": # Bluetooth connectivity
            self.BLUETOOTHinModelType = True
        elif attrType == 'CalendarEntry':
            self.CALENDARinModelType = True            
        elif attrType == 'CellTower':
            self.CELL_SITEinModelType = True
        elif attrType == 'Chat':
            self.CHATinModelType = True
        elif attrType == 'Contact':
            self.CONTACTinModelType = True
        elif attrType == 'Cookie':
            self.COOKIEinModelType = True
        elif attrType == 'DeviceEvent':
            self.DEVICE_EVENTinModelType = True
        elif attrType == 'Email':
            self.EMAILinModelType = True
        elif attrType == 'InstantMessage':
            self.INSTANT_MSGinModelType = True
        elif attrType == 'Location':
            self.LOCATIONinModelType = True
        elif attrType == 'SearchedItem':
            self.SEARCHED_ITEMinModelType = True
        elif attrType == 'SMS':
            self.SMSinModelType = True
        elif attrType == 'SocialMediaActivity':
            self.SOCIAL_MEDIAinModelType = True
        elif attrType == 'VisitedPage':
            self.WEB_PAGEinModelType = True
        elif attrType == 'WirelessNetwork':
            self.WIRELESS_NETinModelType = True

    def __startElementModel(self, attrType, id, traceState):
        '''
        It captures the opening of any XML Element matching with the XPath expression
        //model/
            :return:  None.
        '''                
        if self.CALLinModelType:
            self.__startElementModelCALL(attrType, id, traceState)
        elif self.BLUETOOTHinModelType:
            self.__startElementModelBLUETOOTH(attrType, id, traceState)
        elif self.CALENDARinModelType:
            self.__startElementModelCALENDAR(attrType, id, traceState)        
        elif self.CELL_SITEinModelType:
            self.__startElementModelCELL_SITE(attrType, id, traceState)
        elif self.CHATinModelType:
            self.__startElementModelCHAT(attrType, id, traceState)
        elif self.CONTACTinModelType:
            self.__startElementModelCONTACT(attrType, id, traceState)
        elif self.COOKIEinModelType:
            self.__startElementModelCOOKIE(attrType, id, traceState)
        elif self.DEVICE_EVENTinModelType:
            self.__startElementModelDEVICE_EVENT(attrType, id, traceState)
        elif self.EMAILinModelType:
            self.__startElementModelEMAIL(attrType, id, traceState)
        elif self.INSTANT_MSGinModelType:
            self.__startElementModelINSTANT_MSG(attrType, id, traceState)
        elif self.LOCATIONinModelType:
            self.__startElementModelLOCATION(attrType, id, traceState)
        elif self.SEARCHED_ITEMinModelType:
            self.__startElementModelSEARCHED_ITEM(attrType, id, traceState)
        elif self.SMSinModelType:
            self.__startElementModelSMS(attrType, id, traceState)
        elif self.SOCIAL_MEDIAinModelType:
            self.__startElementModelSOCIAL_MEDIA(attrType, id, traceState)
        elif self.WEB_PAGEinModelType:
            self.__startElementModelWEB_PAGE(attrType, id, traceState)
        elif self.WIRELESS_NETinModelType:
            self.__startElementModelWIRELESS_NET(attrType, id, traceState)                                       
        self.__startElementModelU_ACCOUNT(attrType)  
                
    def __startMultiModelField(self, attrName):
        '''
        It captures the opening of any XML Element matching with the XPath expression
        //modelField/
            :return:  None.
        '''                
        if self.CHATinModelType:
            self.__startElementMultiModelFieldCHAT(attrName)
        elif self.CALENDARinModelType:
            self.__startElementMultiModelFieldCALENDAR(attrName)
        elif self.CONTACTinModelType:
            self.__startElementMultiModelFieldCONTACT(attrName)
        elif self.EMAILinModelType:
            self.__startElementMultiModelFieldEMAIL(attrName)
        elif self.INSTANT_MSGinModelType:
            self.__startElementMultiModelFieldINSTANT_MSG(attrName)
        elif self.SMSinModelType:
            self.__startElementMultiModelFieldSMS(attrName)
        elif self.SOCIAL_MEDIAinModelType:
            self.__startElementMultiModelFieldSOCIAL_MEDIA(attrName)        
        
    def __startModelField(self, attrName):
        '''
        It captures the opening of any XML Element matching with the XPath expression
        //modelField/
            :return:  None.
        '''                
        if self.CHATin:
            self.__startElementModelFieldCHAT(attrName)
        elif self.CELL_SITEin:
            self.__startElementModelFieldCELL_SITE(attrName)        
        elif self.EMAILin:
            self.__startElementModelFieldEMAIL(attrName)            
        elif self.LOCATIONin:
            self.__startElementModelFieldLOCATION(attrName)
        elif self.INSTANT_MSGin:
            self.__startElementModelFieldINSTANT_MSG(attrName)
        elif self.SOCIAL_MEDIAin:
            self.__startElementModelFieldSOCIAL_MEDIA(attrName)
        elif self.WIRELESS_NETin:
            self.__startElementModelFieldWIRELESS_NET(attrName)
        
    def __startElementField(self, attrName, attrs):
        '''
        It captures the opening of any XML Element matching with the XPath expression
        //field/
            :return:  None.
        '''                
        if self.CALLin:
            self.__startElementFieldCALL(attrName)
        elif self.BLUETOOTHin:
            self.__startElementFieldBLUETOOTH(attrName)
        elif self.CALENDARin:
            self.__startElementFieldCALENDAR(attrName)        
        elif self.CHATin:
            self.__startElementFieldCHAT(attrName)            
        elif self.CELL_SITEin:
            self.__startElementFieldCELL_SITE(attrName)
        elif self.CONTACTin:
            self.__startElementFieldCONTACT(attrName)
        elif self.COOKIEin:
            self.__startElementFieldCOOKIE(attrName)
        elif self.DEVICE_EVENTin:
            self.__startElementFieldDEVICE_EVENT(attrName)
        elif self.EMAILin:
            self.__startElementFieldEMAIL(attrName)
        elif self.INSTANT_MSGin:
            self.__startElementFieldINSTANT_MSG(attrName)
        elif self.LOCATIONin:
            self.__startElementFieldLOCATION(attrName)
        elif self.SEARCHED_ITEMin:
            self.__startElementFieldSEARCHED_ITEM(attrName)
        elif self.SMSin:
            self.__startElementFieldSMS(attrName)
        elif self.SOCIAL_MEDIAin:
            self.__startElementFieldSOCIAL_MEDIA(attrName)
        elif self.U_ACCOUNTin:
            self.__startElementFieldU_ACCOUNT(attrName)
        elif self.WEB_PAGEin:
            self.__startElementFieldWEB_PAGE(attrName)
        elif self.WIRELESS_NETin:
            self.__startElementFieldWIRELESS_NET(attrName)
        attrFieldType = attrs.get('fieldType')
        self.__startElementFieldCONTEXT(attrFieldType)
    
    def __startElementValue(self, attrType):        
        '''
        It captures the opening of any XML Element matching with the XPath expression
        //value/
            :return:  None.
        '''                
        if self.CALLin:
            self.__startElementValueCALL()
        elif self.BLUETOOTHinKeyValueModel:
            self.__startElementValueBLUETOOTH()
        elif self.CALENDARin:
            self.__startElementValueCALENDAR()        
        elif self.CELL_SITEin:
            self.__startElementValueCELL_SITE()
        elif self.CHATin:
            self.__startElementValueCHAT(attrType)
        elif self.CONTACTin:
            self.__startElementValueCONTACT()
        elif self.COOKIEin:
            self.__startElementValueCOOKIE()
        elif self.DEVICE_EVENTin:
            self.__startElementValueDEVICE_EVENT()
        elif self.EMAILin:
            self.__startElementValueEMAIL()
        elif self.INSTANT_MSGin:
            self.__startElementValueINSTANT_MSG()
        elif self.LOCATIONin:
            self.__startElementValueLOCATION()
        elif self.SEARCHED_ITEMin:
            self.__startElementValueSEARCHED_ITEM()
        elif self.SMSin:
            self.__startElementValueSMS()
        elif self.SOCIAL_MEDIAin:
            self.__startElementValueSOCIAL_MEDIA()
        elif self.U_ACCOUNTin:
            self.__startElementValueU_ACCOUNT()
        elif self.WEB_PAGEin:
            self.__startElementValueWEB_PAGE()
        elif self.WIRELESS_NETin:
            self.__startElementValueWIRELESS_NET()
    
    def __charactersBLUETOOTH(self, ch):
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //modelType[@type="Call"]//value/
            :return:  None.
        '''        
        if self.BLUETOOTHinValueValue:
            self.BLUETOOTHvalueText += ch
        elif self.BLUETOOTHinKeyValue:
            self.BLUETOOTHkeyText += ch            
            
    def __charactersCALENDAR(self, ch):
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //modelType[@type="Calendar"]//value/
            :return:  None.
        '''
        if self.CALENDARinCategoryValue:
            self.CALENDARcategoryText += ch
        elif self.CALENDARinSubjectValue:
            self.CALENDARsubjectText += ch
        elif self.CALENDARinDetailsValue:
            self.CALENDARdetailsText += ch
        elif self.CALENDARinStartDateValue:
            self.CALENDARstartDateText += ch
        elif self.CALENDARinEndDateValue:
            self.CALENDARendDateText += ch
        elif self.CALENDARinRepeatUntilValue:
            self.CALENDARrepeatUntilText += ch
        elif self.CALENDARinRepeatDayValue:
            self.CALENDARrepeatDayText += ch
        elif self.CALENDARinRepeatIntervalValue:
            self.CALENDARrepeatIntervalText += ch    

    def __charactersCALL(self, ch):
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //modelType[@type="Call"]//value/
            :return:  None.
        '''        
        if self.CALLinSourceValue:
            self.CALLsourceText += ch
        elif self.CALLinTimeStampValue:
            self.CALLtimeStampText += ch
        elif self.CALLinDirectionValue:
            self.CALLdirectionText += ch
        elif self.CALLinTypeValue:
            self.CALLtypeText += ch
        elif self.CALLinDurationValue:
            self.CALLdurationText += ch
        elif self.CALLinOutcomeValue:
            self.CALLoutcomeText += ch
        elif self.CALLinRoleValue:
            self.CALLroleText += ch
        elif self.CALLinNameValue:
            self.CALLnameText += ch
        elif self.CALLinIdentifierValue:
            self.CALLidentifierText += ch

    def __charactersCELL_SITE(self, ch):
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //modelType[@type="CellTower"]//value/
            :return:  None.
        '''        
        if self.CELL_SITEinLongitudeValue:
            self.CELL_SITElongitudeText += ch
        elif self.CELL_SITEinLatitudeValue:
            self.CELL_SITElatitudeText += ch
        elif self.CELL_SITEinTimeStampValue:
            self.CELL_SITEtimeStampText += ch
        elif self.CELL_SITEinMCCValue:
            self.CELL_SITEmccText += ch
        elif self.CELL_SITEinMNCValue:
            self.CELL_SITEmncText += ch
        elif self.CELL_SITEinLACValue:
            self.CELL_SITElacText += ch
        elif self.CELL_SITEinCIDValue:
            self.CELL_SITEcidText += ch
        elif self.CELL_SITEinNIDValue:
            self.CELL_SITEnidText += ch
        elif self.CELL_SITEinBIDValue:
            self.CELL_SITEbidText += ch
        elif self.CELL_SITEinSIDValue:
            self.CELL_SITEsidText += ch

    def __charactersCONTACT(self, ch):
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //modelType[@type="Contact"]//value/
            :return:  None.
        '''        
        if self.CONTACTinSourceValue:
            self.CONTACTsourceText += ch
        if self.CONTACTinNameValue:
            self.CONTACTnameText += ch        
        elif self.CONTACTinUserIdValue:
            if self.CONTACTuserIdText == '':                
                self.CONTACTuserIdText += ch
            else:
                self.CONTACTuserIdText += '###' + ch
        elif self.CONTACTinPhoneNumValue:
            if self.CONTACTphoneNumText == '':
                self.CONTACTphoneNumText += ch
            else:
                self.CONTACTphoneNumText += '###' + ch
        elif self.CONTACTinAccountValue:
            self.CONTACTaccountText += ch

    def __charactersCHAT(self, ch):
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //modelType[@type="Chat"]//value/
            :return:  None.
        '''        
        if self.CHATinSourceValue:
            if self.CHATsourceText == "":
                self.CHATsourceText += ch
            else:
                self.CHATsourceText = ch
        elif self.CHATinPartyIdentifierValue:
            self.CHATpartyIdentifierText += ch 
        elif self.CHATinPartyNameValue:
            self.CHATpartyNameText += ch 
        elif self.CHATinMsgIdentifierFromValue:
            self.CHATmsgIdentifierFromText += ch            
        elif self.CHATinMsgNameFromValue:
            self.CHATmsgNameFromText += ch
        elif self.CHATinMsgBodyValue:
            self.CHATmsgBodyText += ch
        elif self.CHATinMsgOutcomeValue:
            self.CHATmsgOutcomeText += ch
        elif self.CHATinMsgTimeStampValue:
            self.CHATmsgTimeStampText += ch
        elif self.CHATinMsgAttachmentFilenameValue:
            if self.CHATmsgAttachmentFilenameText == '':
                self.CHATmsgAttachmentFilenameText += ch
            else:
#---    The separator ### is for dividing more than one attachment to the same msg
                self.CHATmsgAttachmentFilenameText += '###' + ch
        elif self.CHATinMsgAttachmentUrlValue:
            if self.CHATmsgAttachmentUrlText == '':
                self.CHATmsgAttachmentUrlText += ch
            else:
                self.CHATmsgAttachmentUrlText += '###' + ch  

    def __charactersCOOKIE(self, ch):
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //modelType[@type="Cookie"]//value/
            :return:  None.
        '''        
        if self.COOKIEinSourceValue:
            self.COOKIEsourceText += ch
        elif self.COOKIEinNameValue:
            self.COOKIEnameText += ch
        elif self.COOKIEinValueValue:
            self.COOKIEvalueText += ch
        elif self.COOKIEinDomainValue:
            self.COOKIEdomainText += ch
        elif self.COOKIEinCreationTimeValue:
            self.COOKIEcreationTimeText += ch
        elif self.COOKIEinLastAccessTimeValue:
            self.COOKIElastAccessTimeText += ch
        elif self.COOKIEinExpiryValue:
            self.COOKIEexpiryText += ch

    def __charactersDEVICE_EVENT(self, ch):
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //modelType[@type="DeviceEvent"]//value/
            :return:  None.
        '''        
        if self.DEVICE_EVENTinTimeStampValue:
            self.DEVICE_EVENTtimeStampText += ch
        elif self.DEVICE_EVENTinEventTypeValue:
            self.DEVICE_EVENTeventTypeText += ch
        elif self.DEVICE_EVENTinValueValue:
            self.DEVICE_EVENTvalueText += ch

    def __charactersEMAIL(self, ch):
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //modelType[@type="Email"]//value/
            :return:  None.
        '''        
        if self.EMAILinSourceValue:
            self.EMAILsourceText += ch
        elif self.EMAILinIdentifierFROMvalue:
            self.EMAILidentifierFROMtext += ch
        elif self.EMAILinIdentifierTOvalue:
            self.EMAILidentifierTOtext += ch
        elif self.EMAILinIdentifierCCvalue:
            self.EMAILidentifierCCtext += ch
        elif self.EMAILinIdentifierBCCvalue:
            self.EMAILidentifierBCCtext += ch
        elif self.EMAILinBodyValue:
            self.EMAILbodyText += ch
        elif self.EMAILinSubjectValue:
            self.EMAILsubjectText += ch
        elif self.EMAILinTimeStampValue:
            self.EMAILtimeStampText += ch
        elif self.EMAILinAttachmentFilenameValue:
            self.EMAILattachmentFilenameText += ch

    def __charactersINSTANT_MSG(self, ch):
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //modelType[@type="InstantMessage"]//value/
            :return:  None.
        '''        
        if self.INSTANT_MSGinSourceValue:
            self.INSTANT_MSGsourceText += ch
        elif self.INSTANT_MSGinFromIdentifierValue:            
            self.INSTANT_MSGfromIdentifierText += ch
        elif self.INSTANT_MSGinFromNameValue:
            self.INSTANT_MSGfromNameText += ch
        elif self.INSTANT_MSGinToIdentifierValue:
            if self.INSTANT_MSGtoIdentifierText != '':
                self.INSTANT_MSGtoIdentifierText += '@@@' + ch
            else:
                self.INSTANT_MSGtoIdentifierText += ch
        elif self.INSTANT_MSGinToNameValue:
            if self.INSTANT_MSGtoNameText != '':
                self.INSTANT_MSGtoNameText += '@@@' + ch
            else:
                self.INSTANT_MSGtoNameText += ch

        elif self.INSTANT_MSGinSubjectValue:
            self.INSTANT_MSGsubjectText += ch
        elif self.INSTANT_MSGinBodyValue:
            self.INSTANT_MSGbodyText += ch
        elif self.INSTANT_MSGinTimeStampValue:
            self.INSTANT_MSGtimeStampText += ch
        elif self.INSTANT_MSGinStatusMsgValue:
            self.INSTANT_MSGstatusMsgText += ch
        elif self.INSTANT_MSGinTypeValue:
            self.INSTANT_MSGtypeText += ch
        elif self.INSTANT_MSGinFolderValue:
            self.INSTANT_MSGfolderText += ch
        elif self.INSTANT_MSGinApplicationValue:
            self.INSTANT_MSGapplicationText += ch

    def __charactersLOCATION(self, ch):
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //modelType[@type="Location"]//value/
            :return:  None.
        '''        
        if self.LOCATIONinLongitudeValue:
            self.LOCATIONlongitudeText += ch
        elif self.LOCATIONinLatitudeValue:
            self.LOCATIONlatitudeText += ch
        elif self.LOCATIONinAltitudeValue:
            self.LOCATIONaltitudeText += ch
        elif self.LOCATIONinTimeStampValue:
            self.LOCATIONtimeStampText += ch
        elif self.LOCATIONinCategoryValue:
            self.LOCATIONcategoryText += ch

    def __charactersSEARCHED_ITEM(self, ch):
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //modelType[@type="SearchedItem"]//value/
            :return:  None.
        '''        
        if self.SEARCHED_ITEMinSourceValue:
            self.SEARCHED_ITEMsourceText += ch
        elif self.SEARCHED_ITEMinTimeStampValue:
            self.SEARCHED_ITEMtimeStampText += ch
        elif self.SEARCHED_ITEMinValue:
            self.SEARCHED_ITEMvalueText += ch
        elif self.SEARCHED_ITEMinSearchResultValue:
            self.SEARCHED_ITEMsearchResultText += ch

    def __charactersSMS(self, ch):
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //modelType[@type="SMS"]//value/
            :return:  None.
        '''        
        if self.SMSinSourceValue:
            self.SMSsourceText += ch
        elif self.SMSinTimeStampValue:
            self.SMStimeStampText += ch
        elif self.SMSinBodyValue:
            self.SMSbodyText += ch 
        elif self.SMSinFolderValue:
            self.SMSfolderText += ch 
        elif self.SMSinSmscValue:
            self.SMSsmscText += ch           
        elif self.SMSinPartyIdentifierValue:
            self.SMSpartyIdentifierText += ch
        elif self.SMSinPartyRoleValue:
            self.SMSpartyRoleText += ch        
        elif self.SMSinPartyNameValue:
            self.SMSpartyNameText += ch

    def __charactersSOCIAL_MEDIA(self, ch):
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //modelType[@type="SocialMediaActivity"]//value/
            :return:  None.
        '''        
        if self.SOCIAL_MEDIAinSourceValue:
            self.SOCIAL_MEDIAsourceText += ch
        elif self.SOCIAL_MEDIAinTimeStampValue:
            self.SOCIAL_MEDIAtimeStampText += ch
        elif self.SOCIAL_MEDIAinBodyValue:
            self.SOCIAL_MEDIAbodyText += ch
        elif self.SOCIAL_MEDIAinTitleValue:
            self.SOCIAL_MEDIAtitleText += ch
        elif self.SOCIAL_MEDIAinUrlValue:
            self.SOCIAL_MEDIAurlText += ch               
        elif self.SOCIAL_MEDIAinIdentifierValue:
            self.SOCIAL_MEDIAidentifierText += ch
        elif self.SOCIAL_MEDIAinNameValue:
            self.SOCIAL_MEDIAnameText += ch
        elif self.SOCIAL_MEDIAinReactionsCountValue:
            self.SOCIAL_MEDIAreactionsCountText += ch
        elif self.SOCIAL_MEDIAinSharesCountValue:
            self.SOCIAL_MEDIAsharesCountText += ch
        elif self.SOCIAL_MEDIAinActivityTypeValue:
            self.SOCIAL_MEDIAactivityTypeText += ch
        elif self.SOCIAL_MEDIAinCommentCountValue:
            self.SOCIAL_MEDIAcommentCountText += ch
        elif self.SOCIAL_MEDIAinAccountValue:
            self.SOCIAL_MEDIAaccountText += ch

    def __charactersU_ACCOUNT(self, ch):
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //modelType[@type="Account"]//value/ 
            :return:  None.
        '''        
        if self.U_ACCOUNTinSourceValue:
            self.U_ACCOUNTsourceValueText += ch
        elif self.U_ACCOUNTinNameValue:
            self.U_ACCOUNTnameValueText += ch
        elif self.U_ACCOUNTinUsernameValue:
            self.U_ACCOUNTusernameValueText += ch

    def __charactersWEB_PAGE(self, ch):
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //modelType[@type="VisitedPage"]//value/
            :return:  None.
        '''        
        if self.WEB_PAGEinSourceValue:
            self.WEB_PAGEsourceText += ch
        elif self.WEB_PAGEinUrlValue:
            self.WEB_PAGEurlText += ch
        elif self.WEB_PAGEinTitleValue:
            self.WEB_PAGEtitleText += ch
        elif self.WEB_PAGEinVisitCountValue:
            self.WEB_PAGEvisitCountText += ch
        elif self.WEB_PAGEinLastVisitedValue:
            self.WEB_PAGElastVisitedText += ch

    def __charactersWIRELESS_NET(self, ch):
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //modelType[@type="WirelessNetwork"]//value/
            :return:  None.
        '''        
        if self.WIRELESS_NETinLongitudeValue:
            self.WIRELESS_NETlongitudeText += ch
        elif self.WIRELESS_NETinLatitudeValue:
            self.WIRELESS_NETlatitudeText += ch
        elif self.WIRELESS_NETinTimeStampValue:
            self.WIRELESS_NETtimeStampText += ch
        elif self.WIRELESS_NETinLastConnectionValue:
            self.WIRELESS_NETlastConnectionText += ch
        elif self.WIRELESS_NETinBssidValue:
            self.WIRELESS_NETbssidText += ch
        elif self.WIRELESS_NETinSsidValue:
            self.WIRELESS_NETssidText += ch

    def __charactersTAGGED_FILES(self, ch):
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //taggedFile
            :return:  None.
        '''        
        if self.TAGGED_FILESinAccessInfoCreate:
            self.TAGGED_FILESCreateText += ch
        elif self.TAGGED_FILESinAccessInfoModify:
            self.TAGGED_FILESModifyText += ch
        elif self.TAGGED_FILESinAccessInfoAccess:
            self.TAGGED_FILESAccessText += ch
        elif self.TAGGED_FILESinMD5:
            self.TAGGED_FILESmd5Text += ch
        elif self.TAGGED_FILESinTags:
            self.TAGGED_FILEStagsText += ch
        elif self.TAGGED_FILESinLocalPath:
            self.TAGGED_FILESlocalPathText += ch
        elif self.TAGGED_FILESinInodeNumber:
            self.TAGGED_FILESiNodeNumberText += ch
        elif self.TAGGED_FILESinInodeTimeModify:
            self.TAGGED_FILESiNodeTimeModifyText += ch
        elif self.TAGGED_FILESinOwnerGID:
            self.TAGGED_FILESownerGIDText += ch
        elif self.TAGGED_FILESinOwnerUID:
            self.TAGGED_FILESownerUIDText += ch
        elif self.TAGGED_FILESinExifLatitudeRef:
            self.TAGGED_FILESexifLatitudeRef += ch
        elif self.TAGGED_FILESinExifLatitude:
            self.TAGGED_FILESexifLatitude += ch
        elif self.TAGGED_FILESinExifLongitudeRef:
            self.TAGGED_FILESexifLongitudeRef += ch
        elif self.TAGGED_FILESinExifLongitude:
            self.TAGGED_FILESexifLongitude += ch
        elif self.TAGGED_FILESinExifAltitude:
            self.TAGGED_FILESexifAltitude += ch
        elif self.TAGGED_FILESinExifMake:
            self.TAGGED_FILESexifMake += ch
        elif self.TAGGED_FILESinExifModel:
            self.TAGGED_FILESexifModel += ch  

    def __charactersCONTEXT(self, ch):
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //metadata//item/
            :return:  None.
        '''        
        if self.CONTEXTinDeviceCreationTimeValue:
            if self.CONTEXTdeviceCreationTimeText == '':
                self.CONTEXTdeviceCreationTimeText += ch
        elif self.CONTEXTinUfedVersionValue:
            self.CONTEXTufedVersionText += ch        
        elif self.CONTEXTinExaminerNameValue:
            self.CONTEXTexaminerNameText += ch        
        elif self.CONTEXTinDeviceExtractionStart:
            if self.CONTEXTdeviceExtractionStartText == '':
                self.CONTEXTdeviceExtractionStartText += ch
        elif self.CONTEXTinDeviceExtractionEnd:
            if self.CONTEXTdeviceExtractionEndText == '':
                self.CONTEXTdeviceExtractionEndText += ch
        elif self.CONTEXTinDeviceOsVersionValue:
            self.CONTEXTdeviceOsVersionText  += ch
        elif self.CONTEXTinDevicePhoneVendorValue:
            self.CONTEXTdevicePhoneVendorText  += ch
        elif self.CONTEXTinDevicePhoneModelValue:
            self.CONTEXTdevicePhoneModelText  += ch
        elif self.CONTEXTinDeviceIdValue:
            if self.CONTEXTdeviceIdText.strip() == '':
                self.CONTEXTdeviceIdText  += ch
        elif self.CONTEXTinDeviceMacAddressValue:
            self.CONTEXTdeviceMacAddressText  += ch
        elif self.CONTEXTinDeviceIccidValue:
            self.CONTEXTdeviceIccidText  += ch
        elif self.CONTEXTinDeviceMsisdnValue:
            if self.CONTEXTdeviceMsisdnText.strip() == '':
                self.CONTEXTdeviceMsisdnText  += ch
            else:
                self.CONTEXTdeviceMsisdnText  += '/' + ch
        elif self.CONTEXTinDeviceBluetoothAddressValue:
            if self.CONTEXTdeviceBluetoothAddressText == '':
                self.CONTEXTdeviceBluetoothAddressText  += ch
        elif self.CONTEXTinDeviceBluetoothName:
            self.CONTEXTdeviceBluetoothNameText  += ch
        elif self.CONTEXTinDeviceImsiValue:
            self.CONTEXTdeviceImsiText  += ch
        elif self.CONTEXTinDeviceImeiValue:
            self.CONTEXTdeviceImeiText  += ch
        elif self.CONTEXTinDeviceOsTypeValue:
            self.CONTEXTdeviceOsTypeText  += ch  
        elif self.CONTEXTinImageMetadataHashValueSHA:
            self.CONTEXTimageMetadataHashTextSHA += ch          
        elif self.CONTEXTinImageMetadataHashValueMD5:
            self.CONTEXTimageMetadataHashTextMD5 += ch           

#---    it captures the value/character inside the Text Elements
#                
    def characters(self, ch):        
        '''
        It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
        //modelType//value/
            :return:  None.
        '''
        self.__charactersCONTEXT(ch)
        if self.CALENDARin:
            self.__charactersCALENDAR(ch)
        elif self.BLUETOOTHin:
            self.__charactersBLUETOOTH(ch)
        elif self.CALLin:
            self.__charactersCALL(ch)            
        elif self.CELL_SITEin:
            self.__charactersCELL_SITE(ch)
        elif self.CONTACTin:
            self.__charactersCONTACT(ch)
        elif self.CHATin:
            self.__charactersCHAT(ch)
        elif self.COOKIEin:
            self.__charactersCOOKIE(ch)
        elif self.DEVICE_EVENTin:
            self.__charactersDEVICE_EVENT(ch)
        elif self.EMAILin:
            self.__charactersEMAIL(ch)
        elif self.INSTANT_MSGin:
            self.__charactersINSTANT_MSG(ch)
        elif self.LOCATIONin:
            self.__charactersLOCATION(ch)
        elif self.SEARCHED_ITEMin:
            self.__charactersSEARCHED_ITEM(ch)
        elif self.SMSin:
            self.__charactersSMS(ch)
        elif self.SOCIAL_MEDIAin:
            self.__charactersSOCIAL_MEDIA(ch)
        elif self.U_ACCOUNTin:
            self.__charactersU_ACCOUNT(ch)
        elif self.WEB_PAGEin:
            self.__charactersWEB_PAGE(ch)
        elif self.WIRELESS_NETin:
            self.__charactersWIRELESS_NET(ch)
        self.__charactersTAGGED_FILES(ch)

    def __endElementModelSMS(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="SMS"]/model/
            :return:  None.
        '''
        if self.SMSinAllTimeStamps:
            pass
        elif self.SMSinParty:
                self.SMSpartyIdentifier.append(self.SMSpartyIdentifierText)
                self.SMSpartyRole.append(self.SMSpartyRoleText)
                self.SMSpartyName.append(self.SMSpartyNameText)
                self.SMSpartyRoleText = ''
                self.SMSpartyIdentifierText = ''
                self.SMSpartyNameText = ''
        else:
            self.SMSsource.append(self.SMSsourceText)
            self.SMStimeStamp.append(self.SMStimeStampText)
            self.SMSbodyText = self.__cleanText(self.SMSbodyText)
            self.SMSbody.append(self.SMSbodyText)
            self.SMSfolder.append(self.SMSfolderText)
            self.SMSsmsc.append(self.SMSsmscText)
            self.SMSpartyIdentifiers.append(self.SMSpartyIdentifier[:])
            self.SMSpartyRoles.append(self.SMSpartyRole[:])
            self.SMSpartyNames.append(self.SMSpartyName[:])            
            self.SMSsourceText = ''
            self.SMStimeStampText = ''
            self.SMSbodyText = ''
            self.SMSfolderText = ''
            self.SMSsmscText = ''  
            self.SMSpartyIdentifier.clear()
            self.SMSpartyRole.clear()
            self.SMSpartyName.clear()
            self.SMSin = False
    
    def __endElementModelBLUETOOTH(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="DeviceConnectivity"]/model/
            :return:  None.
        '''        
        if self.BLUETOOTHinKeyValueModel:
            self.BLUETOOTHinKeyValueModel = False
#--- end of a single Bluetooth connection item
        elif self.BLUETOOTHin:
            idx = self.BLUETOOTHtotal - 1
            self.BLUETOOTHkeys[idx] = self.BLUETOOTHkeyText
            self.BLUETOOTHvalues[idx] = self.BLUETOOTHvalueText
            self.BLUETOOTHvalueText = ''
            self.BLUETOOTHkeyText = ''
            self.BLUETOOTHin = False
                
    def __endElementModelCALENDAR(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="CalendarEntry"]/model/
            :return:  None.
        '''        
        if self.CALENDARin:

            if (not self.CALENDARinAttendees) and (not self.CALENDARinAttachments):
                idx = self.CALENDARtotal - 1
                self.CALENDARcategory[idx] = self.CALENDARcategoryText
                self.CALENDARsubject[idx] = self.CALENDARsubjectText
                self.CALENDARdetails[idx] = self.CALENDARdetailsText
                self.CALENDARstartDate[idx] = self.CALENDARstartDateText
                self.CALENDARendDate[idx] = self.CALENDARendDateText
                self.CALENDARrepeatUntil[idx] = self.CALENDARrepeatUntilText
                self.CALENDARrepeatDay[idx] = self.CALENDARrepeatDayText
                self.CALENDARrepeatInterval[idx] = self.CALENDARrepeatIntervalText
                self.CALENDARcategoryText = ''
                self.CALENDARsubjectText = ''
                self.CALENDARdetailsText = ''                
                self.CALENDARstartDateText = ''
                self.CALENDARendDateText = ''
                self.CALENDARrepeatUntilText = ''
                self.CALENDARrepeatDayText = ''
                self.CALENDARrepeatIntervalText = ''
                self.CALENDARin = False
                self.CALENDARinAttendees = False 
                self.CALENDARinAttachments = False 


    def __endElementModelCELL_SITE(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="CellTower"]/model/
            :return:  None.
        '''        
        if self.CELL_SITEin:

            if not self.CELL_SITEinPosition:
                idx = self.CELL_SITEtotal - 1
                self.CELL_SITElongitude[idx] = self.CELL_SITElongitudeText
                self.CELL_SITElatitude[idx] = self.CELL_SITElatitudeText
                self.CELL_SITEtimeStamp[idx] = self.CELL_SITEtimeStampText
                self.CELL_SITEmcc[idx] = self.CELL_SITEmccText
                self.CELL_SITEmnc[idx] = self.CELL_SITEmncText
                self.CELL_SITElac[idx] = self.CELL_SITElacText
                self.CELL_SITEcid[idx] = self.CELL_SITEcidText
                self.CELL_SITEnid[idx] = self.CELL_SITEnidText
                self.CELL_SITEbid[idx] = self.CELL_SITEbidText
                self.CELL_SITEsid[idx] = self.CELL_SITEsidText
                self.CELL_SITElongitudeText = ''
                self.CELL_SITElatitudeText = ''
                self.CELL_SITEtimeStampText = ''                
                self.CELL_SITEmccText = ''
                self.CELL_SITEmncText = ''
                self.CELL_SITElacText = ''
                self.CELL_SITEcidText = ''
                self.CELL_SITEnidText = ''
                self.CELL_SITEbidText = ''
                self.CELL_SITEsidText = ''
                self.CELL_SITEin = False                

    def __endElementModelCALL(self):        
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="Call"]/model/
            :return:  None.
        '''        
        if self.CALLinParty:
            self.CALLinParty = False
            if self.CALLroleText.upper() == 'TO':
                self.CALLroleTO.append(self.CALLroleText)
                self.CALLroleFROM.append('')
                self.CALLidentifierTO.append(self.CALLidentifierText)
                self.CALLidentifierFROM.append('')
                self.CALLnameTO.append(self.CALLnameText)
                self.CALLnameFROM.append('')
            else:
                self.CALLroleFROM.append(self.CALLroleText)
                self.CALLroleTO.append('')
                self.CALLidentifierFROM.append(self.CALLidentifierText)
                self.CALLidentifierTO.append('')
                self.CALLnameFROM.append(self.CALLnameText)
                self.CALLnameTO.append('')

            self.CALLidentifierText = ''
            self.CALLroleText = ''
            self.CALLnameText = ''
        
        elif self.CALLin:                                   
            self.CALLsource.append(self.CALLsourceText)
            self.CALLtimeStamp.append(self.CALLtimeStampText)
            
            if self.CALLdirectionText.strip() == '':
                self.CALLdirectionText = self.CALLtypeText

            self.CALLdirection.append(self.CALLdirectionText)
            self.CALLduration.append(self.CALLdurationText)
            self.CALLoutcome.append(self.CALLoutcomeText)
            self.CALLrolesTO.append(self.CALLroleTO[:])
            self.CALLrolesFROM.append(self.CALLroleFROM[:])  
            self.CALLidentifiersTO.append(self.CALLidentifierTO[:])
            self.CALLidentifiersFROM.append(self.CALLidentifierFROM[:])
            self.CALLnamesFROM.append(self.CALLnameFROM[:])  
            self.CALLnamesTO.append(self.CALLnameTO[:])                  
            self.CALLsourceText = ''
            self.CALLtimeStampText = ''
            self.CALLdirectionText = ''
            self.CALLdurationText = ''
            self.CALLtypeText = ''
            self.CALLoutcomeText = ''
            self.CALLroleText = ''
            self.CALLnameText = ''
            self.CALLidentifierText = ''
            self.CALLroleTO.clear()
            self.CALLroleFROM.clear()
            self.CALLidentifierTO.clear()
            self.CALLidentifierFROM.clear()
            self.CALLnameTO.clear()
            self.CALLnameFROM.clear()
            self.CALLin = False

    def __endElementModelCONTACT(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="Contact"]/model/
            :return:  None.
        '''        
        if self.CONTACTinModelUserId:
            self.CONTACTinModelUserId = False
        elif self.CONTACTinModelPhoneNumber:
                self.CONTACTinModelPhoneNumber = False
        elif self.CONTACTinModelProfilePicture:
                self.CONTACTinModelProfilePicture = False
        elif self.CONTACTinMultiModelFieldPhotos:
                pass
        elif self.CONTACTin:            
            self.CONTACTsource[self.CONTACTtotal - 1] = self.CONTACTsourceText
            self.CONTACTname[self.CONTACTtotal - 1] = self.CONTACTnameText
            self.CONTACTphoneNum = self.CONTACTphoneNumText.split('###')
            self.CONTACTuserId = self.CONTACTuserIdText.split('###')
            
            lenPhoneNums  = len(self.CONTACTphoneNum)
            lenUserIds = len(self.CONTACTuserId)
            for i in range(0, lenPhoneNums - lenUserIds):
                self.CONTACTuserId.append('')
            for i in range(0, lenUserIds - lenPhoneNums):
                self.CONTACTphoneNum.append('')

            self.CONTACTuserIds.append(self.CONTACTuserId[:])            
            self.CONTACTphoneNums.append(self.CONTACTphoneNum[:])
            self.CONTACTaccount[self.CONTACTtotal - 1] = self.CONTACTaccountText                        
            
            self.CONTACTsourceText = ''
            self.CONTACTnameText = ''
            self.CONTACTuserIdText = ''
            self.CONTACTphoneNumText = ''
            self.CONTACTaccountText = ''
            self.CONTACTuserId.clear()
            self.CONTACTphoneNum.clear()
            self.CONTACTin = False

    def __endElementModelCHAT(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="Chat"]/model/
            :return:  None.
        '''        
        if self.CHATinMultiModelFieldPhotos:            
            pass
        elif self.CHATinParty:
            self.CHATpartyIdentifier.append(self.CHATpartyIdentifierText)
            self.CHATpartyName.append(self.CHATpartyNameText) 
            self.CHATpartyIdentifierText = ''
            self.CHATpartyNameText = ''               
            self.CHATinParty = False                        
        elif self.CHATinInstantMessage:            
            if self.CHATinMultiModelFieldTo or \
                self.CHATinMultiModelFieldAttachments or \
                self.CHATinMultiModelFieldSharedContacts or \
                self.CHATinMultiModelFieldMessageExtraData or \
                self.CHATinModelFieldAttachment or \
                self.CHATinMsgFrom:
                pass
            else:                
                self.CHATmsgIdentifierFrom[self.CHATmsgNum] = self.CHATmsgIdentifierFromText.strip()
                self.CHATmsgNameFrom[self.CHATmsgNum] = self.CHATmsgNameFromText.strip()
                self.CHATmsgBody[self.CHATmsgNum] = self.CHATmsgBodyText.strip()
                self.CHATmsgOutcome[self.CHATmsgNum] = self.CHATmsgOutcomeText.strip()
                self.CHATmsgTimeStamp[self.CHATmsgNum] = self.CHATmsgTimeStampText
                self.CHATmsgAttachmentFilename[self.CHATmsgNum] = self.CHATmsgAttachmentFilenameText.strip()
                self.CHATmsgAttachmentUrl[self.CHATmsgNum] = self.CHATmsgAttachmentUrlText.strip()
                self.CHATmsgIdentifierFromText = ''
                self.CHATmsgNameFromText = ''
                self.CHATmsgBodyText = ''
                self.CHATmsgOutcomeText = ''
                self.CHATmsgTimeStampText = ''
                self.CHATmsgAttachmentFilenameText = ''
                self.CHATmsgAttachmentUrlText = ''
                self.CHATinInstantMessage = False
        elif self.CHATin:                    
#---    use the list slicing to generate a new list where each item is a list, otherwise the next clear would 
#       empty both lists: clearing the CHAT.msgBody would empty the same item in the container list CHAT.msgBodies                       
            self.CHATsource[self.CHATtotal - 1] = self.CHATsourceText
            self.CHATsourceText = ''
            self.CHATpartyIdentifiers.append(self.CHATpartyIdentifier[:])
            self.CHATpartyNames.append(self.CHATpartyName[:])
            self.CHATmsgIdentifiersFrom.append(self.CHATmsgIdentifierFrom[:])
            self.CHATmsgNamesFrom.append(self.CHATmsgNameFrom[:])
            self.CHATmsgBodies.append(self.CHATmsgBody[:])
            self.CHATmsgStatuses.append(self.CHATmsgStatus[:])
            self.CHATmsgOutcomes.append(self.CHATmsgOutcome[:])
            self.CHATmsgTimeStamps.append(self.CHATmsgTimeStamp[:])
            self.CHATmsgAttachmentFilenames.append(self.CHATmsgAttachmentFilename[:])
            self.CHATmsgAttachmentUrls.append(self.CHATmsgAttachmentUrl[:])
            
            self.CHATpartyIdentifier.clear()
            self.CHATpartyName.clear()
            self.CHATmsgIdentifierFrom.clear()
            self.CHATmsgNameFrom.clear()
            self.CHATmsgBody.clear()
            self.CHATmsgOutcome.clear()
            self.CHATmsgStatus.clear()
            self.CHATmsgTimeStamp.clear()
            self.CHATmsgAttachmentFilename.clear()
            self.CHATmsgAttachmentUrl.clear()
            self.CHATmsgNum = -1
            self.CHATin = False
                                
    def __endElementModelCOOKIE(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="Cookie"]/model/
            :return:  None.
        '''         
        if self.COOKIEin:
            idx = self.COOKIEtotal - 1
            self.COOKIEsource[idx] = self.COOKIEsourceText
            self.COOKIEname[idx] = self.COOKIEnameText
            self.COOKIEvalue[idx] = self.COOKIEvalueText
            self.COOKIEdomain[idx] = self.COOKIEdomainText
            self.COOKIEcreationTime[idx] = self.COOKIEcreationTimeText
            self.COOKIElastAccessTime[idx] = self.COOKIElastAccessTimeText
            self.COOKIEexpiry[idx] = self.COOKIEexpiryText
            self.COOKIEsourceText = ''
            self.COOKIEnameText = ''
            self.COOKIEvalueText = ''                
            self.COOKIEdomainText = ''
            self.COOKIEcreationTimeText = ''
            self.COOKIElastAccessTimeText = ''
            self.COOKIEexpiryText = ''
            self.COOKIEin = False

    def __endElementModelDEVICE_EVENT(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="DeviceEvent"]/model/
            :return:  None.
        '''         
        if self.DEVICE_EVENTin:
            idx = self.DEVICE_EVENTtotal - 1
            self.DEVICE_EVENTtimeStamp[idx] = self.DEVICE_EVENTtimeStampText
            self.DEVICE_EVENTeventType[idx] = self.DEVICE_EVENTeventTypeText
            self.DEVICE_EVENTvalue[idx] = self.DEVICE_EVENTvalueText
            self.DEVICE_EVENTtimeStampText = ''
            self.DEVICE_EVENTeventTypeText = ''
            self.DEVICE_EVENTvalueText = ''                
            self.DEVICE_EVENTin = False

    def __endElementModelEMAIL(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="Email"]/model/
            :return:  None.
        '''         
        if self.EMAILinModelFieldFROM:
            self.EMAILinModelFieldFROM = False
        elif self.EMAILinMultiModelFieldTO:
            #self.EMAILinMultiModelFieldTO = False
            idx = len(self.EMAILidentifierTO)
            self.EMAILidentifierTO[idx - 1] = self.EMAILidentifierTOtext
            self.EMAILidentifierTOtext = ''
        elif self.EMAILinMultiModelFieldCC:
            #self.EMAILinMultiModelFieldCC = False
            idx = len(self.EMAILidentifierCC)
            self.EMAILidentifierCC[idx - 1] = self.EMAILidentifierCCtext
            self.EMAILidentifierCCtext = ''
        elif self.EMAILinMultiModelFieldBCC:
            #self.EMAILinMultiModelFieldBCC = False
            idx = len(self.EMAILidentifierBCC)
            self.EMAILidentifierBCC[idx - 1] = self.EMAILidentifierBCCtext
            self.EMAILidentifierBCCtext = ''
        elif self.EMAILinMultiModelFieldAttachments:
            idx = len(self.EMAILattachmentFilename)
            self.EMAILattachmentFilename[idx - 1] = self.EMAILattachmentFilenameText
            self.EMAILattachmentFilenameText = ''            
        elif self.EMAILin:                                
                self.EMAILsource[self.EMAILtotal - 1] = self.EMAILsourceText
                self.EMAILidentifierFROM[self.EMAILtotal - 1] = self.EMAILidentifierFROMtext
                if self.EMAILidentifierTO:
                    self.EMAILidentifierTO.append('')

                self.EMAILidentifiersTO.append(self.EMAILidentifierTO[:])
                self.EMAILidentifiersCC.append(self.EMAILidentifierCC[:])
                self.EMAILidentifiersBCC.append(self.EMAILidentifierBCC[:])
                self.EMAILattachmentsFilename.append(self.EMAILattachmentFilename[:])
                bodyClean = self.__cleanText(self.EMAILbodyText)
                self.EMAILbody[self.EMAILtotal - 1] = bodyClean
                self.EMAILsubject[self.EMAILtotal - 1] = self.EMAILsubjectText
                self.EMAILtimeStamp[self.EMAILtotal - 1] = self.EMAILtimeStampText
                self.EMAILsourceText = ''
                self.EMAILidentifierFROMtext = ''
                self.EMAILidentifierTO.clear()
                self.EMAILidentifierCC.clear()
                self.EMAILidentifierBCC.clear()
                self.EMAILattachmentFilename.clear()
                self.EMAILbodyText = ''
                self.EMAILsubjectText = ''
                self.EMAILtimeStampText = ''
                self.EMAILattachmentFilenameText = ''
                self.EMAILin = False
                self.EMAILinSource = False

    def __endElementModelINSTANT_MSG(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="InstantMessage"]/model/
            :return:  None.
        '''         
        if self.INSTANT_MSGin:
            if  not self.INSTANT_MSGinPartyFrom and \
                not self.INSTANT_MSGinPartyTo and \
                not self.INSTANT_MSGinAttachments and \
                not self.INSTANT_MSGinAttachment and \
                not self.INSTANT_MSGinSharedContacts:

                idx = self.INSTANT_MSGtotal - 1
                self.INSTANT_MSGsource[idx] = self.INSTANT_MSGsourceText
                self.INSTANT_MSGfromIdentifier[idx] = self.INSTANT_MSGfromIdentifierText
                self.INSTANT_MSGfromName[idx] = self.INSTANT_MSGfromNameText
                self.INSTANT_MSGtoIdentifier[idx] = self.INSTANT_MSGtoIdentifierText
                self.INSTANT_MSGtoName[idx] = self.INSTANT_MSGtoNameText
                self.INSTANT_MSGsubject[idx] = self.INSTANT_MSGsubjectText
                self.INSTANT_MSGbody[idx] = self.INSTANT_MSGbodyText
                self.INSTANT_MSGtimeStamp[idx] = self.INSTANT_MSGtimeStampText
                self.INSTANT_MSGstatusMsg[idx] = self.INSTANT_MSGstatusMsgText
                self.INSTANT_MSGtype[idx] = self.INSTANT_MSGtypeText
                self.INSTANT_MSGfolder[idx] = self.INSTANT_MSGfolderText
                self.INSTANT_MSGapplication [idx] = self.INSTANT_MSGapplicationText
                self.INSTANT_MSGsourceText = ''
                self.INSTANT_MSGfromIdentifierText = ''                
                self.INSTANT_MSGfromNameText = ''
                self.INSTANT_MSGtoIdentifierText = ''
                self.INSTANT_MSGtoNameText = ''
                self.INSTANT_MSGsubjectText = ''
                self.INSTANT_MSGbodyText = ''
                self.INSTANT_MSGtimeStampText = ''
                self.INSTANT_MSGstatusMsgText = ''
                self.INSTANT_MSGtypeText = ''
                self.INSTANT_MSGfolderText = ''
                self.INSTANT_MSGapplicationText = ''
                self.INSTANT_MSGin = False                
            
    def __endElementModelLOCATION(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="Location"]/model/
            :return:  None.
        '''         
        if self.LOCATIONin:
            if not self.LOCATIONinPosition:
                idx = self.LOCATIONtotal - 1
                self.LOCATIONlongitude[idx] = self.LOCATIONlongitudeText
                self.LOCATIONlatitude[idx] = self.LOCATIONlatitudeText
                self.LOCATIONaltitude[idx] = self.LOCATIONaltitudeText
                self.LOCATIONtimeStamp[idx] = self.LOCATIONtimeStampText
                self.LOCATIONcategory[idx] = self.LOCATIONcategoryText
                self.LOCATIONlongitudeText = ''
                self.LOCATIONlatitudeText = ''
                self.LOCATIONaltitudeText = ''                
                self.LOCATIONtimeStampText = ''
                self.LOCATIONcategoryText = ''
                self.LOCATIONin = False

    def __endElementModelU_ACCOUNT(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="UserAccount"]/model/
            :return:  None.
        '''         
        if self.U_ACCOUNTinContactEntry:
            self.U_ACCOUNTinContactEntry = False
            return(0)
        if self.U_ACCOUNTinContactPhoto:
            self.U_ACCOUNTinContactPhoto = False
            return(0)
        if self.U_ACCOUNTinEmailAddress:
            self.U_ACCOUNTinEmailAddress = False
            return(0)
        if self.U_ACCOUNTinUserID:
            self.U_ACCOUNTinUserID = False
            return(0)
        
        if self.U_ACCOUNTin:
            source = self.U_ACCOUNTsourceValueText.replace('\n', ' ')
            source = source.strip()
            if source == '':
                pass
            else:

#---    in UFED the field Source represents the application and the Whatsapp value is not 
#       WhatsAppMessage but just Whatsapp! 
                source = source.replace('WhatsAppiMessage', 'Whatsapp')
                source = source.replace('FacebookiMessage', 'Facebook')
                source = source.replace('Facebook MessengeriMessage', 'Facebook Messenger')
                
                self.U_ACCOUNTsource.append(source.lower())
            if source == '':
                pass
            else:
                value = self.U_ACCOUNTnameValueText.replace('\n', ' ')
                value = value.strip()
                self.U_ACCOUNTname.append(value)            
            if source == '':
                pass
            else:
                value = self.U_ACCOUNTusernameValueText.replace('\n', ' ')
                value = value.strip()
                self.U_ACCOUNTusername.append(value)
                        
            self.U_ACCOUNTsourceValueText = ''
            self.U_ACCOUNTnameValueText = ''            
            self.U_ACCOUNTusernameValueText = ''
            self.U_ACCOUNTin = False

    def __endElementModelSEARCHED_ITEM(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="SearchedItem"]/model/
            :return:  None.
        '''         
        if self.SEARCHED_ITEMin:
            idx = self.SEARCHED_ITEMtotal - 1
            self.SEARCHED_ITEMsource[idx] = self.SEARCHED_ITEMsourceText
            self.SEARCHED_ITEMtimeStamp[idx] = self.SEARCHED_ITEMtimeStampText
            self.SEARCHED_ITEMvalue[idx] = self.SEARCHED_ITEMvalueText
            self.SEARCHED_ITEMsearchResult[idx] = self.SEARCHED_ITEMsearchResultText
            self.SEARCHED_ITEMsourceText = ''
            self.SEARCHED_ITEMtimeStampText = ''
            self.SEARCHED_ITEMvalueText = ''
            self.SEARCHED_ITEMsearchResultText = ''               
            self.SEARCHED_ITEMin = False

    def __endElementModelSOCIAL_MEDIA(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="SocialMediaActivity"]/model/
            :return:  None.
        '''         
        if self.SOCIAL_MEDIAin:
            if not self.SOCIAL_MEDIAinAttachments and \
                not self.SOCIAL_MEDIAinTaggedParties and \
                not self.SOCIAL_MEDIAinAuthor:
                idx = self.SOCIAL_MEDIAtotal - 1
                self.SOCIAL_MEDIAsource[idx] = self.SOCIAL_MEDIAsourceText
                self.SOCIAL_MEDIAtimeStamp[idx] = self.SOCIAL_MEDIAtimeStampText
                self.SOCIAL_MEDIAbody[idx] = self.SOCIAL_MEDIAbodyText
                self.SOCIAL_MEDIAtitle[idx] = self.SOCIAL_MEDIAtitleText
                self.SOCIAL_MEDIAurl[idx] = self.SOCIAL_MEDIAurlText
                self.SOCIAL_MEDIAidentifier[idx] = self.SOCIAL_MEDIAidentifierText
                self.SOCIAL_MEDIAname[idx] = self.SOCIAL_MEDIAnameText
                self.SOCIAL_MEDIAreactionsCount[idx] = self.SOCIAL_MEDIAreactionsCountText
                self.SOCIAL_MEDIAsharesCount[idx] = self.SOCIAL_MEDIAsharesCountText
                self.SOCIAL_MEDIAactivityType[idx] = self.SOCIAL_MEDIAactivityTypeText
                self.SOCIAL_MEDIAcommentCount[idx] = self.SOCIAL_MEDIAcommentCountText
                self.SOCIAL_MEDIAaccount[idx] = self.SOCIAL_MEDIAaccountText
                self.SOCIAL_MEDIAsourceText = ''
                self.SOCIAL_MEDIAtimeStampText = ''
                self.SOCIAL_MEDIAbodyText = ''                
                self.SOCIAL_MEDIAtitleText = ''                
                self.SOCIAL_MEDIAurlText = ''
                self.SOCIAL_MEDIAidentifierText = ''
                self.SOCIAL_MEDIAnameText = ''
                self.SOCIAL_MEDIAreactionsCountText = ''
                self.SOCIAL_MEDIAsharesCountText = ''
                self.SOCIAL_MEDIAactivityTypeText = ''
                self.SOCIAL_MEDIAcommentCountText = ''
                self.SOCIAL_MEDIAaccountText = ''
                self.SOCIAL_MEDIAin = False

    def __endElementModelWEB_PAGE(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="VisitedPage"]/model/
            :return:  None.
        '''         
        if self.WEB_PAGEin:             
            self.WEB_PAGEsource.append(self.WEB_PAGEsourceText)
            self.WEB_PAGEurl.append(self.WEB_PAGEurlText)
            self.WEB_PAGEtitle.append(self.WEB_PAGEtitleText)
            self.WEB_PAGEvisitCount.append(self.WEB_PAGEvisitCountText)
            self.WEB_PAGElastVisited.append(self.WEB_PAGElastVisitedText)                                    
            self.WEB_PAGEsourceText = ''
            self.WEB_PAGEurlText = ''
            self.WEB_PAGEtitleText = ''
            self.WEB_PAGEvisitCountText = ''
            self.WEB_PAGElastVisitedText = ''
            self.WEB_PAGEin = False

    def __endElementModelWIRELESS_NET(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="WirelessNetwork"]/model/
            :return:  None.
        '''         
        if self.WIRELESS_NETin:
            if not self.WIRELESS_NETinPosition:
                idx = self.WIRELESS_NETtotal - 1
                self.WIRELESS_NETlongitude[idx] = self.WIRELESS_NETlongitudeText
                self.WIRELESS_NETlatitude[idx] = self.WIRELESS_NETlatitudeText
                self.WIRELESS_NETtimeStamp[idx] = self.WIRELESS_NETtimeStampText
                self.WIRELESS_NETlastConnection[idx] = self.WIRELESS_NETlastConnectionText
                self.WIRELESS_NETbssid[idx] = self.WIRELESS_NETbssidText
                self.WIRELESS_NETssid[idx] = self.WIRELESS_NETssidText
                self.WIRELESS_NETlongitudeText = ''
                self.WIRELESS_NETlatitudeText = ''
                self.WIRELESS_NETtimeStampText = ''                
                self.WIRELESS_NETlastConnectionText = ''
                self.WIRELESS_NETbssidText = ''
                self.WIRELESS_NETssidText = ''
                self.WIRELESS_NETin = False

    def __endElementFieldCALL(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="Call"]//field/
            :return:  None.
        '''         
        if self.CALLinSource:
            self.CALLinSource = False
        elif self.CALLinDirection:
            self.CALLinDirection = False
        elif self.CALLinType:
            self.CALLinType = False
        elif self.CALLinOutcome:
            self.CALLinOutcome = False
        elif self.CALLinTimeStamp:
            self.CALLinTimeStamp = False        
        elif self.CALLinDuration:
            self.CALLinDuration = False        
        elif self.CALLinIdentifier:
            self.CALLinIdentifier = False         
        elif self.CALLinRole:
            self.CALLinRole = False
        elif self.CALLinName:
            self.CALLinName = False                                        

    def __endElementFieldBLUETOOTH(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="DeviceConnectivity"]//field/
            :return:  None.
        '''         
        if self.BLUETOOTHinKey:
            self.BLUETOOTHinKey = False
        elif self.BLUETOOTHinValue:
            self.BLUETOOTHinValue = False

    def __endElementFieldCALENDAR(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="CalendarEntry"]//field/
            :return:  None.
        '''         
        if self.CALENDARinCategory:
            self.CALENDARinCategory = False
        elif self.CALENDARinSubject:
            self.CALENDARinSubject = False
        elif self.CALENDARinDetails:
            self.CALENDARinDetails = False
        elif self.CALENDARinStartDate:
            self.CALENDARinStartDate = False
        elif self.CALENDARinEndDate:
            self.CALENDARinEndDate = False
        elif self.CALENDARinRepeatUntil:
            self.CALENDARinRepeatUntil = False
        elif self.CALENDARinRepeatDay:
            self.CALENDARinRepeatDay = False
        elif self.CALENDARinRepeatInterval:
            self.CALENDARinRepeatInterval = False

    def __endElementFieldCELL_SITE(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="CellTower"]//field/
            :return:  None.
        '''         
        if self.CELL_SITEinLongitude:
            self.CELL_SITEinLongitude = False
        elif self.CELL_SITEinLatitude:
            self.CELL_SITEinLatitude = False
        elif self.CELL_SITEinTimeStamp:
            self.CELL_SITEinTimeStamp = False
        elif self.CELL_SITEinMCC:
            self.CELL_SITEinMCC = False
        elif self.CELL_SITEinMNC:
            self.CELL_SITEinMNC = False
        elif self.CELL_SITEinLAC:
            self.CELL_SITEinLAC = False
        elif self.CELL_SITEinCID:
            self.CELL_SITEinCID = False
        elif self.CELL_SITEinNID:
            self.CELL_SITEinNID = False
        elif self.CELL_SITEinBID:
            self.CELL_SITEinBID = False
        elif self.CELL_SITEinSID:
            self.CELL_SITEinSID = False  

    def __endElementFieldWIRELESS_NET(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="WirelessNetwork"]//field/
            :return:  None.
        '''         
        if self.WIRELESS_NETinLongitude:
            self.WIRELESS_NETinLongitude = False
        elif self.WIRELESS_NETinLatitude:
            self.WIRELESS_NETinLatitude = False
        elif self.WIRELESS_NETinTimeStamp:
            self.WIRELESS_NETinTimeStamp = False
        elif self.WIRELESS_NETinLastConnection:
            self.WIRELESS_NETinLastConnection = False
        elif self.WIRELESS_NETinBssid:
            self.WIRELESS_NETinBssid = False
        elif self.WIRELESS_NETinSsid:
            self.WIRELESS_NETinSsid = False

    def __endElementFieldCOOKIE(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="Cookie"]//field/
            :return:  None.
        '''         
        if self.COOKIEinSource:
            self.COOKIEinSource = False
        elif self.COOKIEinName:
            self.COOKIEinName = False
        elif self.COOKIEinValue:
            self.COOKIEinValue = False
        elif self.COOKIEinDomain:
            self.COOKIEinDomain = False
        elif self.COOKIEinCreationTime:
            self.COOKIEinCreationTime = False
        elif self.COOKIEinLastAccessTime:
            self.COOKIEinLastAccessTime = False
        elif self.COOKIEinExpiry:
            self.COOKIEinExpiry = False

    def __endElementFieldCONTACT(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="Contact"]//field/
            :return:  None.
        '''         
        if self.CONTACTinSource:
            self.CONTACTinSource = False
        elif self.CONTACTinName:
            self.CONTACTinName = False
        elif self.CONTACTinModelUserId:
            if self.CONTACTinUserId:
                self.CONTACTinUserId = False 
        elif self.CONTACTinModelPhoneNumber:
            if self.CONTACTinPhoneNum:
                self.CONTACTinPhoneNum = False      
        elif self.CONTACTinAccount:
            self.CONTACTinAccount = False
    
    def __endElementFieldCHAT(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="Chat"]//field/
            :return:  None.
        '''         
        if self.CHATinSource:
            self.CHATinSource = False
        elif self.CHATinPartyIdentifier:
            self.CHATinPartyIdentifier = False
        elif self.CHATinPartyName:
            self.CHATinPartyName = False
        elif self.CHATinMsgIdentifierFrom:
            self.CHATinMsgIdentifierFrom = False
        elif self.CHATinMsgNameFrom:
            self.CHATinMsgNameFrom = False
        elif self.CHATinMsgBody:
            self.CHATinMsgBody = False
        elif self.CHATinMsgOutcome:
            self.CHATinMsgOutcome = False
        elif self.CHATinMsgTimeStamp:
            self.CHATinMsgTimeStamp = False
        elif self.CHATinMsgAttachmentFilename:
            self.CHATinMsgAttachmentFilename = False
        elif self.CHATinMsgAttachmentUrl:
            self.CHATinMsgAttachmentUrl = False
        
    def __endElementFieldDEVICE_EVENT(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="DeviceEvent"]//field/
            :return:  None.
        '''         
        if self.DEVICE_EVENTinTimeStamp:
            self.DEVICE_EVENTinTimeStamp = False
        elif self.DEVICE_EVENTinEventType:
            self.DEVICE_EVENTinEventType = False
        elif self.DEVICE_EVENTinValue:
            self.DEVICE_EVENTinValue = False

    def __endElementFieldEMAIL(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="Email"]//field/
            :return:  None.
        '''         
        if self.EMAILin:
            if self.EMAILinSource:
                self.EMAILinSource = False
            elif self.EMAILinIdentifierFROM:
                self.EMAILinIdentifierFROM = False
            elif self.EMAILinIdentifierTO:
                self.EMAILinIdentifierTO = False
            elif self.EMAILinIdentifierCC:
                self.EMAILinIdentifierCC = False
            elif self.EMAILinIdentifierBCC:
                self.EMAILinIdentifierBCC = False
            elif self.EMAILinBody:
                self.EMAILinBody = False
            elif self.EMAILinSubject:
                self.EMAILinSubject = False
            elif self.EMAILinTimeStamp:
                self.EMAILinTimeStamp = False
            elif self.EMAILinAttachmentFilename:
                self.EMAILinAttachmentFilename = False

    def __endElementFieldINSTANT_MSG(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="InstantMessage"]//field/
            :return:  None.
        '''         
        if self.INSTANT_MSGinSource:
            self.INSTANT_MSGinSource = False
        elif self.INSTANT_MSGinFromIdentifier:
            self.INSTANT_MSGinFromIdentifier = False
        elif self.INSTANT_MSGinFromName:
            self.INSTANT_MSGinFromName = False
        elif self.INSTANT_MSGinToIdentifier:
            self.INSTANT_MSGinToIdentifier = False
        elif self.INSTANT_MSGinToName:
            self.INSTANT_MSGinToName = False
        elif self.INSTANT_MSGinSubject:
            self.INSTANT_MSGinSubject = False
        elif self.INSTANT_MSGinBody:
            self.INSTANT_MSGinBody = False
        elif self.INSTANT_MSGinTimeStamp:
            self.INSTANT_MSGinTimeStamp = False
        elif self.INSTANT_MSGinType:
            self.INSTANT_MSGinType = False
        elif self.INSTANT_MSGinFolder:
            self.INSTANT_MSGinFolder = False
        elif self.INSTANT_MSGinApplication:
            self.INSTANT_MSGinApplication = False

    def __endElementFieldLOCATION(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="Location"]//field/
            :return:  None.
        '''         
        if self.LOCATIONinLongitude:
            self.LOCATIONinLongitude = False
        elif self.LOCATIONinLatitude:
            self.LOCATIONinLatitude = False
        elif self.LOCATIONinAltitude:
            self.LOCATIONinAltitude = False
        elif self.LOCATIONinTimeStamp:
            self.LOCATIONinTimeStamp = False
        elif self.LOCATIONinCategory:
            self.LOCATIONinCategory = False

    def __endElementFieldSEARCHED_ITEM(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="SearchedItem"]//field/
            :return:  None.
        '''         
        if self.SEARCHED_ITEMinSource:
            self.SEARCHED_ITEMinSource = False
        elif self.SEARCHED_ITEMinTimeStamp:
            self.SEARCHED_ITEMinTimeStamp = False
        elif self.SEARCHED_ITEMinValue:
            self.SEARCHED_ITEMinValue = False

    def __endElementFieldSMS(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="SMS"]//field/
            :return:  None.
        '''         
        if self.SMSinSource:
            self.SMSinSource = False 
        elif self.SMSinTimeStamp:
            self.SMSinTimeStamp = False
        elif self.SMSinBody:
            self.SMSinBody = False
        elif self.SMSinFolder:
            self.SMSinFolder = False
        elif self.SMSinSmsc:
            self.SMSinSmsc = False
        elif self.SMSinPartyRole:
            self.SMSinPartyRole = False
        elif self.SMSinPartyIdentifier:
            self.SMSinPartyIdentifier = False         
        elif self.SMSinPartyName:
            self.SMSinPartyName = False 
        
    def __endElementFieldSOCIAL_MEDIA(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="SocialMediaActivity"]//field/
            :return:  None.
        '''         
        if self.SOCIAL_MEDIAinSource:
            self.SOCIAL_MEDIAinSource = False
        elif self.SOCIAL_MEDIAinTimeStamp:
            self.SOCIAL_MEDIAinTimeStamp = False
        elif self.SOCIAL_MEDIAinBody:
            self.SOCIAL_MEDIAinBody = False
        elif self.SOCIAL_MEDIAinTitle:
            self.SOCIAL_MEDIAinTitle = False
        elif self.SOCIAL_MEDIAinUrl:
            self.SOCIAL_MEDIAinUrl = False            
        elif self.SOCIAL_MEDIAinIdentifier:
            self.SOCIAL_MEDIAinIdentifier = False
        elif self.SOCIAL_MEDIAinName:
            self.SOCIAL_MEDIAinName = False
        elif self.SOCIAL_MEDIAinReactionsCount:
            self.SOCIAL_MEDIAinReactionsCount = False
        elif self.SOCIAL_MEDIAinSharesCount:
            self.SOCIAL_MEDIAinSharesCount = False
        elif self.SOCIAL_MEDIAinActivityType:
            self.SOCIAL_MEDIAinActivityType = False
        elif self.SOCIAL_MEDIAinCommentCount:
            self.SOCIAL_MEDIAinCommentCount = False
        elif self.SOCIAL_MEDIAinAccount:
            self.SOCIAL_MEDIAinAccount = False

    def __endElementFieldU_ACCOUNT(self):        
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="UserAccount"]//field/
            :return:  None.
        '''         
        if self.U_ACCOUNTinSource:
                self.U_ACCOUNTinSource = False
        elif self.U_ACCOUNTinName:
            self.U_ACCOUNTinName = False
        elif self.U_ACCOUNTinUsername:
                self.U_ACCOUNTinUsername = False    

    def __endElementFieldCONTEXT(self):
        if self.CONTEXTinCaseInfo:
            if self.CONTEXTinExaminerNameValue:
                self.CONTEXTinExaminerNameValue = False

    def __endElementFieldWEB_PAGE(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="VisitedPage"]//field/
            :return:  None.
        '''
        if self.WEB_PAGEin:
            if self.WEB_PAGEinSource:
                self.WEB_PAGEinSource = False
            elif self.WEB_PAGEinUrl:
                self.WEB_PAGEinUrl = False
            elif self.WEB_PAGEinTitle:
                self.WEB_PAGEinTitle = False
            elif self.WEB_PAGEinVisitCount:
                self.WEB_PAGEinVisitCount = False
            elif self.WEB_PAGEinLastVisited:
                self.WEB_PAGEinLastVisited = False

    def __endElementValueBLUETOOTH(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="DeviceConnectivity"]//value/
            :return:  None.
        '''
        if self.BLUETOOTHinKeyValue:
            self.BLUETOOTHinKeyValue = False
        elif self.BLUETOOTHinValueValue:
            self.BLUETOOTHinValueValue = False        
    
    def __endElementValueCALL(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="Call"]//value/
            :return:  None.
        '''
        if self.CALLinSourceValue:
            self.CALLinSourceValue = False
        elif self.CALLinDirectionValue:
            self.CALLinDirectionValue = False
        elif self.CALLinTypeValue:
            self.CALLinTypeValue = False
        elif self.CALLinOutcomeValue:
            self.CALLinOutcomeValue = False
        elif self.CALLinTimeStampValue:
            self.CALLinTimeStampValue = False        
        elif self.CALLinDurationValue:
            self.CALLinDurationValue = False        
        elif self.CALLinIdentifierValue:
            self.CALLinIdentifierValue = False
        elif self.CALLinRoleValue:
            self.CALLinRoleValue = False
        elif self.CALLinNameValue:            
            self.CALLinNameValue = False                

    def __endElementValueCALENDAR(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="CalendarEntry"]//value/
            :return:  None.
        '''        
        if self.CALENDARinCategoryValue:
            self.CALENDARinCategoryValue = False
        elif self.CALENDARinSubjectValue:
            self.CALENDARinSubjectValue = False
        elif self.CALENDARinDetailsValue:
            self.CALENDARinDetailsValue = False
        elif self.CALENDARinStartDateValue:
            self.CALENDARinStartDateValue = False
        elif self.CALENDARinEndDateValue:
            self.CALENDARinEndDateValue = False
        elif self.CALENDARinRepeatUntilValue:
            self.CALENDARinRepeatUntilValue = False
        elif self.CALENDARinRepeatDayValue:
            self.CALENDARinRepeatDayValue = False
        elif self.CALENDARinRepeatIntervalValue:
            self.CALENDARinRepeatIntervalValue = False

    def __endElementValueCELL_SITE(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="CellTower"]//value/
            :return:  None.
        '''        
        if self.CELL_SITEinLongitudeValue:
            self.CELL_SITEinLongitudeValue = False
        elif self.CELL_SITEinLatitudeValue:
            self.CELL_SITEinLatitudeValue = False
        elif self.CELL_SITEinTimeStampValue:
            self.CELL_SITEinTimeStampValue = False
        elif self.CELL_SITEinMCCValue:
            self.CELL_SITEinMCCValue = False
        elif self.CELL_SITEinMNCValue:
            self.CELL_SITEinMNCValue = False
        elif self.CELL_SITEinLACValue:
            self.CELL_SITEinLACValue = False
        elif self.CELL_SITEinCIDValue:
            self.CELL_SITEinCIDValue = False
        elif self.CELL_SITEinNIDValue:
            self.CELL_SITEinNIDValue = False
        elif self.CELL_SITEinBIDValue:
            self.CELL_SITEinBIDValue = False
        elif self.CELL_SITEinSIDValue:
            self.CELL_SITEinSIDValue = False

    def __endElementValueDEVICE_EVENT(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="DeviceEvent"]//value/
            :return:  None.
        '''        
        if self.DEVICE_EVENTinTimeStampValue:
            self.DEVICE_EVENTinTimeStampValue = False
        elif self.DEVICE_EVENTinEventTypeValue:
            self.DEVICE_EVENTinEventTypeValue = False
        elif self.DEVICE_EVENTinValueValue:
            self.DEVICE_EVENTinValueValue = False        

    def __endElementValueCOOKIE(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="Cookie"]//value/
            :return:  None.
        '''        
        if self.COOKIEinSourceValue:
            self.COOKIEinSourceValue = False
        elif self.COOKIEinNameValue:
            self.COOKIEinNameValue = False
        elif self.COOKIEinValueValue:
            self.COOKIEinValueValue = False
        elif self.COOKIEinDomainValue:
            self.COOKIEinDomainValue = False
        elif self.COOKIEinCreationTimeValue:
            self.COOKIEinCreationTimeValue = False
        elif self.COOKIEinLastAccessTimeValue:
            self.COOKIEinLastAccessTimeValue = False
        elif self.COOKIEinExpiryValue:
            self.COOKIEinExpiryValue = False

    def __endElementValueCHAT(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="Chat"]//value/
            :return:  None.
        '''        
        if self.CHATin:
            if self.CHATinSourceValue:            
                self.CHATinSourceValue = False
            elif self.CHATinPartyIdentifierValue:
                self.CHATinPartyIdentifierValue = False
            elif self.CHATinPartyNameValue:
                self.CHATinPartyNameValue = False
            elif self.CHATinMsgIdentifierFromValue:
                self.CHATinMsgIdentifierFromValue = False
            elif self.CHATinMsgNameFromValue:                
                self.CHATinMsgNameFromValue = False
            elif self.CHATinMsgBodyValue:
                self.CHATinMsgBodyValue = False
            elif self.CHATinMsgOutcomeValue:
                self.CHATinMsgOutcomeValue = False
            elif self.CHATinMsgTimeStampValue:
                self.CHATinMsgTimeStampValue = False
            elif self.CHATinMsgAttachmentFilenameValue:
                self.CHATinMsgAttachmentFilenameValue = False
            elif self.CHATinMsgAttachmentUrlValue:
                self.CHATinMsgAttachmentUrlValue = False

    def __endElementValueCONTACT(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="Contact"]//value/
            :return:  None.
        '''        
        if self.CONTACTinSourceValue:
            self.CONTACTinSourceValue = False
        elif self.CONTACTinNameValue:
            self.CONTACTinNameValue = False
        elif self.CONTACTinUserIdValue:
            self.CONTACTinUserIdValue = False 
        elif self.CONTACTinPhoneNumValue:            
            self.CONTACTphoneNumText = self.CONTACTphoneNumText.strip().replace(' ', '')
            self.CONTACTinPhoneNumValue = False
        elif self.CONTACTinAccountValue:
            self.CONTACTinAccountValue = False 

    def __endElementValueEMAIL(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="Email"]//value/
            :return:  None.
        '''        
        if self.EMAILinSourceValue:
            self.EMAILinSourceValue = False
        elif self.EMAILinIdentifierFROMvalue:
            self.EMAILinIdentifierFROMvalue = False
        elif self.EMAILinIdentifierTOvalue:
            self.EMAILinIdentifierTOvalue = False
        elif self.EMAILinIdentifierCCvalue:
            self.EMAILinIdentifierCCvalue = False
        elif self.EMAILinIdentifierBCCvalue:
            self.EMAILinIdentifierBCCvalue = False
        elif self.EMAILinBodyValue:
            self.EMAILinBodyValue = False
        elif self.EMAILinSubjectValue:
            self.EMAILinSubjectValue = False
        elif self.EMAILinTimeStampValue:
            self.EMAILinTimeStampValue = False
        elif self.EMAILinAttachmentFilenameValue:
            self.EMAILinAttachmentFilenameValue = False

    def __endElementValueINSTANT_MSG(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="InstantMessage"]//value/
            :return:  None.
        '''        
        if self.INSTANT_MSGinSourceValue:
            self.INSTANT_MSGinSourceValue = False
        elif self.INSTANT_MSGinFromIdentifierValue:
            self.INSTANT_MSGinFromIdentifierValue = False
        elif self.INSTANT_MSGinFromNameValue:
            self.INSTANT_MSGinFromNameValue = False
        elif self.INSTANT_MSGinToIdentifierValue:
            self.INSTANT_MSGinToIdentifierValue = False
        elif self.INSTANT_MSGinToNameValue:
            self.INSTANT_MSGinToNameValue = False
        elif self.INSTANT_MSGinSubjectValue:
            self.INSTANT_MSGinSubjectValue = False
        elif self.INSTANT_MSGinBodyValue:
            self.INSTANT_MSGinBodyValue = False
        elif self.INSTANT_MSGinTimeStampValue:
            self.INSTANT_MSGinTimeStampValue = False
        elif self.INSTANT_MSGinStatusMsgValue:
            self.INSTANT_MSGinStatusMsgValue = False
        elif self.INSTANT_MSGinTypeValue:
            self.INSTANT_MSGinTypeValue = False
        elif self.INSTANT_MSGinFolderValue:
            self.INSTANT_MSGinFolderValue = False
        elif self.INSTANT_MSGinApplicationValue:
            self.INSTANT_MSGinApplicationValue = False

    def __endElementValueLOCATION(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="Location"]//value/
            :return:  None.
        '''        
        if self.LOCATIONinLongitudeValue:
            self.LOCATIONinLongitudeValue = False
        elif self.LOCATIONinLatitudeValue:
            self.LOCATIONinLatitudeValue = False
        elif self.LOCATIONinAltitudeValue:
            self.LOCATIONinAltitudeValue = False
        elif self.LOCATIONinTimeStampValue:
            self.LOCATIONinTimeStampValue = False
        elif self.LOCATIONinCategoryValue:
            self.LOCATIONinCategoryValue = False

    def __endElementValueSEARCHED_ITEM(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="SearchedItem"]//value/
            :return:  None.
        '''        
        if self.SEARCHED_ITEMinSourceValue:
            self.SEARCHED_ITEMinSourceValue = False
        elif self.SEARCHED_ITEMinTimeStampValue:
            self.SEARCHED_ITEMinTimeStampValue = False
        elif self.SEARCHED_ITEMinValueValue:
            self.SEARCHED_ITEMinValueValue = False

    def __endElementValueSMS(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="SMS"]//value/
            :return:  None.
        '''        
        if self.SMSinSourceValue:
            self.SMSinSourceValue = False 
        elif self.SMSinTimeStampValue:
            self.SMSinTimeStampValue = False
        elif self.SMSinBodyValue:
            self.SMSinBodyValue = False
        elif self.SMSinFolderValue:
            self.SMSinFolderValue = False
        elif self.SMSinSmscValue:
            self.SMSinSmscValue = False
        elif self.SMSinPartyIdentifierValue:
            self.SMSinPartyIdentifierValue = False
        elif self.SMSinPartyRoleValue:            
            self.SMSinPartyRoleValue = False                
        elif self.SMSinPartyNameValue:
            self.SMSinPartyNameValue = False 

    def __endElementValueSOCIAL_MEDIA(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="SocialMediaActivity"]//value/
            :return:  None.
        '''        
        if self.SOCIAL_MEDIAinSourceValue:
            self.SOCIAL_MEDIAinSourceValue = False
        elif self.SOCIAL_MEDIAinTimeStampValue:
            self.SOCIAL_MEDIAinTimeStampValue= False
        elif self.SOCIAL_MEDIAinBodyValue:
            self.SOCIAL_MEDIAinBodyValue = False
        elif self.SOCIAL_MEDIAinTitleValue:
            self.SOCIAL_MEDIAinTitleValue = False
        elif self.SOCIAL_MEDIAinUrlValue:
            self.SOCIAL_MEDIAinUrlValue = False
        elif self.SOCIAL_MEDIAinIdentifierValue:
            self.SOCIAL_MEDIAinIdentifierValue = False
        elif self.SOCIAL_MEDIAinNameValue:
            self.SOCIAL_MEDIAinNameValue = False
        elif self.SOCIAL_MEDIAinReactionsCountValue:
            self.SOCIAL_MEDIAinReactionsCountValue = False
        elif self.SOCIAL_MEDIAinSharesCountValue:
            self.SOCIAL_MEDIAinSharesCountValue = False
        elif self.SOCIAL_MEDIAinActivityTypeValue:
            self.SOCIAL_MEDIAinActivityTypeValue = False
        elif self.SOCIAL_MEDIAinCommentCountValue:
            self.SOCIAL_MEDIAinCommentCountValue = False
        elif self.SOCIAL_MEDIAinAccountValue:
            self.SOCIAL_MEDIAinAccountValue = False

    def __endElementValueU_ACCOUNT(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="UserAccount"]//value/
            :return:  None.
        '''        
        if self.U_ACCOUNTinSourceValue:
            self.U_ACCOUNTinSourceValue = False
        elif self.U_ACCOUNTinNameValue:
            self.U_ACCOUNTinNameValue = False            
        elif self.U_ACCOUNTinUsernameValue:
            self.U_ACCOUNTinUsernameValue = False


    def __endElementValueWEB_PAGE(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="VisitedPage"]//value/
            :return:  None.
        '''        
        if self.WEB_PAGEin:
            if self.WEB_PAGEinSourceValue:
                self.WEB_PAGEinSourceValue = False 
            elif self.WEB_PAGEinUrlValue:
                self.WEB_PAGEinUrlValue = False 
            elif self.WEB_PAGEinTitleValue:
                self.WEB_PAGEinTitleValue = False 
            elif self.WEB_PAGEinVisitCountValue:
                self.WEB_PAGEinVisitCountValue = False 
            elif self.WEB_PAGEinLastVisitedValue:
                self.WEB_PAGEinLastVisitedValue = False 

    def __endElementValueWIRELESS_NET(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //modelType[@type="WirelessNetwork"]//value/
            :return:  None.
        '''        
        if self.WIRELESS_NETinLongitudeValue:
            self.WIRELESS_NETinLongitudeValue = False
        elif self.WIRELESS_NETinLatitudeValue:
            self.WIRELESS_NETinLatitudeValue = False
        elif self.WIRELESS_NETinTimeStampValue:
            self.WIRELESS_NETinTimeStampValue = False
        elif self.WIRELESS_NETinLastConnectionValue:
            self.WIRELESS_NETinLastConnectionValue = False
        elif self.WIRELESS_NETinBssidValue:
            self.WIRELESS_NETinBssidValue = False
        elif self.WIRELESS_NETinSsidValue:
            self.WIRELESS_NETinSsidValue = False

    def __endElementTimeStampTAGGED_FILE(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //taggedFiles
            :return:  None.
        '''        
        if self.TAGGED_FILESinAccessInfoCreate:
            self.FILEtimeCreate[self.FILEidx] = self.TAGGED_FILESCreateText
            self.TAGGED_FILESCreateText = ''
            self.TAGGED_FILESinAccessInfoCreate = False
        elif self.TAGGED_FILESinAccessInfoModify:
            self.FILEtimeModify[self.FILEidx] = self.TAGGED_FILESModifyText
            self.TAGGED_FILESModifyText = ''
            self.TAGGED_FILESinAccessInfoModify = False
        elif self.TAGGED_FILESinAccessInfoAccess:
            self.FILEtimeAccess[self.FILEidx] = self.TAGGED_FILESAccessText
            self.TAGGED_FILESAccessText = ''
            self.TAGGED_FILESinAccessInfoAccess = False

    def __endElementItemTAGGED_FILE(self):
        '''
        It captures the end of the XML Element matching with the XPath expression
        //taggedFiles//item
            :return:  None.
        '''        
        if self.TAGGED_FILESinMD5:
            self.FILEmd5.append(self.TAGGED_FILESmd5Text)
            self.TAGGED_FILESmd5Text = ''
            self.TAGGED_FILESinMD5 = False
        elif self.TAGGED_FILESinTags:
            self.FILEtags.append(self.TAGGED_FILEStagsText)
            self.TAGGED_FILEStagsText = ''
            self.TAGGED_FILESinTags = False
        elif self.TAGGED_FILESinLocalPath:
            self.FILElocalPath.append(os.path.join(self.TAGGED_FILESbaseLocalPath, 
                self.TAGGED_FILESlocalPathText))
            self.TAGGED_FILESlocalPathText = ''
            self.TAGGED_FILESinLocalPath = False
        elif self.TAGGED_FILESinInodeNumber:
            self.FILEiNodeNumber[self.FILEidx] = self.TAGGED_FILESiNodeNumberText
            self.TAGGED_FILESiNodeNumberText = ''
            self.TAGGED_FILESinInodeNumber = False
        elif self.TAGGED_FILESinInodeTimeModify:
            self.FILEiNodeTimeModify[self.FILEidx] = self.TAGGED_FILESiNodeTimeModifyText
            self.TAGGED_FILESiNodeTimeModifyText = ''
            self.TAGGED_FILESinInodeTimeModify = False
        elif self.TAGGED_FILESinExifLatitudeRef:
            self.FILEexifLatitudeRef[self.FILEidx] = self.TAGGED_FILESexifLatitudeRef
            self.TAGGED_FILESexifLatitudeRef = ''
            self.TAGGED_FILESinExifLatitudeRef = False
        elif self.TAGGED_FILESinExifLatitude:
            self.FILEexifLatitude[self.FILEidx] = self.TAGGED_FILESexifLatitude
            self.TAGGED_FILESexifLatitude = ''
            self.TAGGED_FILESinExifLatitude = False
        elif self.TAGGED_FILESinExifLongitudeRef:
            self.FILEexifLongitudeRef[self.FILEidx] = self.TAGGED_FILESexifLongitudeRef
            self.TAGGED_FILESexifLongitudeRef = ''
            self.TAGGED_FILESinExifLongitudeRef = False
        elif self.TAGGED_FILESinExifLongitude:
            self.FILEexifLongitude[self.FILEidx] = self.TAGGED_FILESexifLongitude
            self.TAGGED_FILESexifLongitude = ''
            self.TAGGED_FILESinExifLongitude = False
        elif self.TAGGED_FILESinExifAltitude:
            self.FILEexifAltitude[self.FILEidx] = self.TAGGED_FILESexifAltitude
            self.TAGGED_FILESexifAltitude = ''
            self.TAGGED_FILESinExifAltitude = False
        elif self.TAGGED_FILESinExifMake:
            self.FILEexifMake[self.FILEidx] = self.TAGGED_FILESexifMake
            self.TAGGED_FILESexifMake = ''
            self.TAGGED_FILESinExifMake = False
        elif self.TAGGED_FILESinExifModel:
            self.FILEexifModel[self.FILEidx] = self.TAGGED_FILESexifModel
            self.TAGGED_FILESexifModel = ''
            self.TAGGED_FILESinExifModel = False
        elif self.TAGGED_FILESinOwnerGID:
            self.FILEownerGID[self.FILEidx] = self.TAGGED_FILESownerGIDText
            self.TAGGED_FILESownerGIDText = ''
            self.TAGGED_FILESinOwnerGID = False
        elif self.TAGGED_FILESinOwnerUID:
            self.FILEownerUID[self.FILEidx] = self.TAGGED_FILESownerUIDText
            self.TAGGED_FILESownerUIDText = ''
            self.TAGGED_FILESinOwnerUID = False
    
    def __endElementItemCONTEXT(self):        
        '''
        It captures the end of the XML Element matching with the XPath expression
        //metadata//item
            :return:  None.
        '''
        if self.CONTEXTinDeviceExtractionStart:
            self.CONTEXTinDeviceExtractionStart = False
        elif self.CONTEXTinDeviceExtractionEnd:
            self.CONTEXTinDeviceExtractionEnd = False
        elif self.CONTEXTinUfedVersionValue:
            self.CONTEXTinUfedVersionValue = False
        elif self.CONTEXTinDeviceCreationTimeValue:
            self.CONTEXTinDeviceCreationTimeValue = False
        elif self.CONTEXTinDeviceBluetoothAddressValue:
            self.CONTEXTinDeviceBluetoothAddressValue = False
        elif self.CONTEXTinDeviceBluetoothName:
            self.CONTEXTinDeviceBluetoothName = False
        elif self.CONTEXTinDeviceIdValue:
            self.CONTEXTinDeviceIdValue = False
        elif self.CONTEXTinDevicePhoneModelValue:
            self.CONTEXTinDevicePhoneModelValue = False
        elif self.CONTEXTinDeviceOsTypeValue:
            self.CONTEXTinDeviceOsTypeValue = False
        elif self.CONTEXTinDeviceOsVersionValue:
            self.CONTEXTinDeviceOsVersionValue = False
        elif self.CONTEXTinDevicePhoneVendorValue:
            self.CONTEXTinDevicePhoneVendorValue = False
        elif self.CONTEXTinDeviceMacAddressValue:
            self.CONTEXTinDeviceMacAddressValue = False
        elif self.CONTEXTinDeviceIccidValue:
            self.CONTEXTinDeviceIccidValue = False
        elif self.CONTEXTinDeviceMsisdnValue:
            self.CONTEXTinDeviceMsisdnValue = False
        elif self.CONTEXTinDeviceImsiValue:
            self.CONTEXTinDeviceImsiValue = False
        elif self.CONTEXTinDeviceImeiValue:
            self.CONTEXTinDeviceImeiValue = False        
        elif self.CONTEXTinImageMetadataHashValueSHA:
            self.CONTEXTinImageMetadataHashValueSHA = False
        elif self.CONTEXTinImageMetadataHashValueMD5:
            self.CONTEXTinImageMetadataHashValueMD5 = False


    def endElement(self, name):
        '''
        It captures the closure of any XML Element, the method is included in the SAXparser class
            :return:  None.
        '''        
        self.lineXML +=1

        if name == 'model':
            if self.CALLinModelType:
                self.__endElementModelCALL()
            elif self.BLUETOOTHinModelType:
                self.__endElementModelBLUETOOTH()
            elif self.CALENDARinModelType:
                self.__endElementModelCALENDAR()            
            elif self.CELL_SITEinModelType:
                self.__endElementModelCELL_SITE()
            elif self.CONTACTinModelType:
                self.__endElementModelCONTACT()
            elif self.CHATinModelType:
                self.__endElementModelCHAT()
            elif self.COOKIEinModelType:
                self.__endElementModelCOOKIE()
            elif self.DEVICE_EVENTinModelType:
                self.__endElementModelDEVICE_EVENT()
            elif self.EMAILinModelType:
                self.__endElementModelEMAIL()
            elif self.INSTANT_MSGinModelType:
                self.__endElementModelINSTANT_MSG()
            elif self.LOCATIONinModelType:
                self.__endElementModelLOCATION()
            elif self.SEARCHED_ITEMinModelType:
                self.__endElementModelSEARCHED_ITEM()
            elif self.SMSinModelType:
                self.__endElementModelSMS()
            elif self.SOCIAL_MEDIAinModelType:
                self.__endElementModelSOCIAL_MEDIA()            
            elif self.WEB_PAGEinModelType:
                self.__endElementModelWEB_PAGE()
            elif self.WIRELESS_NETinModelType:
                self.__endElementModelWIRELESS_NET()            
            self.__endElementModelU_ACCOUNT()
        elif name == 'modelType':
            if self.CALLinModelType:
                self.CALLinModelType = False
            elif self.BLUETOOTHinModelType:
                self.BLUETOOTHinModelType = False
            elif self.CALENDARinModelType:
                self.CALENDARinModelType = False            
            elif self.CELL_SITEinModelType:
                self.CELL_SITEinModelType = False
            elif self.COOKIEinModelType:
                self.COOKIEinModelType = False
            elif self.CHATinModelType:
                self.CHATinModelType = False
            elif self.CONTACTinModelType:
                self.CONTACTinModelType = False                
            elif self.DEVICE_EVENTinModelType:
                self.DEVICE_EVENTinModelType = False
            elif self.EMAILinModelType:
                self.EMAILinModelType = False
            elif self.INSTANT_MSGinModelType:
                self.INSTANT_MSGinModelType = False
            elif self.LOCATIONinModelType:
                self.LOCATIONinModelType = False
            elif self.SEARCHED_ITEMinModelType:
                self.SEARCHED_ITEMinModelType = False
            elif self.SMSinModelType:
                self.SMSinModelType = False
            elif self.SOCIAL_MEDIAinModelType:
                self.SOCIAL_MEDIAinModelType = False
            elif self.WEB_PAGEinModelType:
                self.WEB_PAGEinModelType = False
            elif self.WIRELESS_NETinModelType:
                self.WIRELESS_NETinModelType = False
        elif name == 'modelField':
            if self.CELL_SITEinPosition:
                self.CELL_SITEinPosition = False  
            if self.CHATinModelFieldAttachment:
                self.CHATinModelFieldAttachment = False
            elif self.CHATinMsgFrom:
                self.CHATinMsgFrom = False            
            elif self.INSTANT_MSGin:      
                if self.INSTANT_MSGinPartyFrom:
                    self.INSTANT_MSGinPartyFrom = False                                 
                elif self.INSTANT_MSGinAttachment:
                    self.INSTANT_MSGinAttachment = False 
            elif self.LOCATIONin:
                if self.LOCATIONinPosition:
                    self.LOCATIONinPosition = False
            elif self.SOCIAL_MEDIAin:
                if self.SOCIAL_MEDIAinAuthor:
                    self.SOCIAL_MEDIAinAuthor = False
            elif self.EMAILinModelType: 
                if self.EMAILinModelFieldFROM:
                    self.EMAILinModelFieldFROM = False
            elif self.WIRELESS_NETinModelType:
                if self.WIRELESS_NETinPosition:
                    self.WIRELESS_NETinPosition = False 
        elif name == 'multiModelField':
            if self.CALENDARinModelType:
                if self.CALENDARinAttendees:
                    self.CALENDARinAttendees = False
                elif self.CALENDARinAttachments:
                    self.CALENDARinAttachments = False  
            elif self.INSTANT_MSGinModelType:
                if self.INSTANT_MSGinPartyTo:
                        self.INSTANT_MSGinPartyTo = False
                elif self.INSTANT_MSGinAttachments:
                    self.INSTANT_MSGinAttachments = False
                elif self.INSTANT_MSGinSharedContacts:
                    self.INSTANT_MSGinSharedContacts = False          
            elif self.CONTACTinModelType:                
                if self.CONTACTinMultiModelFieldEntries:
                    self.CONTACTinMultiModelFieldEntries = False                
                elif self.CONTACTinMultiModelFieldPhotos: 
                    self.CONTACTinMultiModelFieldPhotos = False
            elif self.CHATinModelType:
                if self.CHATinMultiModelFieldParticipants:
                    self.CHATinMultiModelFieldParticipants = False                    
                elif self.CHATinMultiModelFieldPhotos:
                    self.CHATinMultiModelFieldPhotos = False
                elif self.CHATinMultiModelFieldTo:
                    self.CHATinMultiModelFieldTo = False                
                elif self.CHATinMultiModelFieldSharedContacts:
                    self.CHATinMultiModelFieldSharedContacts = False
                elif self.CHATinMultiModelFieldMessageExtraData:
                    self.CHATinMultiModelFieldMessageExtraData = False
                elif self.CHATinMultiModelFieldAttachments:
                    self.CHATinMultiModelFieldAttachments = False
                elif self.CHATinParty:
                    self.CHATinParty = False            
            elif self.SMSinModelType:
                if self.SMSinParty:
                    self.SMSinParty = False
                elif self.SMSinAllTimeStamps:
                    self.SMSinAllTimeStamps = False
            elif self.SOCIAL_MEDIAinModelType:                
                if self.SOCIAL_MEDIAinAttachments:
                    self.SOCIAL_MEDIAinAttachments = False
                elif self.SOCIAL_MEDIAinTaggedParties:
                    self.SOCIAL_MEDIAinTaggedParties = False
            elif self.EMAILinModelType:                
                if self.EMAILinMultiModelFieldTO:
                    self.EMAILinMultiModelFieldTO = False
                elif self.EMAILinMultiModelFieldCC:
                    self.EMAILinMultiModelFieldCC = False
                elif self.EMAILinMultiModelFieldBCC:
                    self.EMAILinMultiModelFieldBCC = False
                elif self.EMAILinMultiModelFieldAttachments:
                    self.EMAILinMultiModelFieldAttachments = False
        elif name == 'field':
            if self.CALLin:
                self.__endElementFieldCALL()
            elif self.CALENDARin:
                self.__endElementFieldCALENDAR()
            elif self.BLUETOOTHin:
                self.__endElementFieldBLUETOOTH()            
            elif self.CELL_SITEin:
                self.__endElementFieldCELL_SITE()
            elif self.CONTACTin:
                self.__endElementFieldCONTACT()            
            elif self.COOKIEin:
                self.__endElementFieldCOOKIE()
            elif self.DEVICE_EVENTin:
                self.__endElementFieldDEVICE_EVENT()
            elif self.EMAILin:
                self.__endElementFieldEMAIL()
            elif self.INSTANT_MSGin:
                self.__endElementFieldINSTANT_MSG()
            elif self.LOCATIONin:
                self.__endElementFieldLOCATION()
            elif self.SEARCHED_ITEMin:
                self.__endElementFieldSEARCHED_ITEM()
            elif self.SMSin:
                self.__endElementFieldSMS()
            elif self.SOCIAL_MEDIAin:
                self.__endElementFieldSOCIAL_MEDIA()
            elif self.U_ACCOUNTin:
                self.__endElementFieldU_ACCOUNT()
            #elif self.WEB_PAGEin:
                #self.__endElementFieldWEB_PAGE()
            elif self.WIRELESS_NETin:
                self.__endElementFieldWIRELESS_NET()
            self.__endElementFieldCHAT()
            self.__endElementFieldCONTEXT()
            self.__endElementFieldWEB_PAGE()
        elif name == 'value':
            if self.CALLin:
                self.__endElementValueCALL()
            elif self.BLUETOOTHin:
                self.__endElementValueBLUETOOTH()
            elif self.CALENDARin:
                self.__endElementValueCALENDAR()            
            elif self.CELL_SITEin:
                self.__endElementValueCELL_SITE()            
            elif self.CONTACTin:
                self.__endElementValueCONTACT()
            elif self.COOKIEin:
                self.__endElementValueCOOKIE()
            elif self.DEVICE_EVENTin:
                self.__endElementValueDEVICE_EVENT()
            elif self.EMAILin:
                self.__endElementValueEMAIL()
            elif self.INSTANT_MSGin:
                self.__endElementValueINSTANT_MSG()
            elif self.LOCATIONin:
                self.__endElementValueLOCATION()
            elif self.SEARCHED_ITEMin:
                self.__endElementValueSEARCHED_ITEM()
            elif self.SMSin:
                self.__endElementValueSMS()
            elif self.SOCIAL_MEDIAin:
                self.__endElementValueSOCIAL_MEDIA()
            elif self.U_ACCOUNTin:
                self.__endElementValueU_ACCOUNT()
            elif self.WIRELESS_NETin:
                self.__endElementValueWIRELESS_NET()
            self.__endElementValueCHAT()
            self.__endElementValueWEB_PAGE()
        elif name == 'timestamp':
            self.__endElementTimeStampTAGGED_FILE()            
        elif name == 'nodeInfo':
            if self.EXTRA_INFOin:
                self.EXTRA_INFOnodeInfoin = False              
        elif name == 'extraInfo':
            self.EXTRA_INFOin = False
        elif name =='taggedFiles':
            self.TAGGED_FILESin = False
        elif name =='item':
            self.__endElementItemTAGGED_FILE()
            self.__endElementItemCONTEXT()
        elif name == "metadata":
            if self.CONTEXTinAdditionalFields:
                self.CONTEXTinAdditionalFields = False
                self.CONTEXTinUfedVersionValue = False
                self.CONTEXTinDeviceCreationTimeValue = False
            elif self.CONTEXTinDeviceInfo:                                
                self.CONTEXTinDeviceInfo = False
            elif self.CONTEXTinImageMetadataHash:
                self.CONTEXTinImageMetadata = False
        elif name == 'caseInformation':
            self.CONTEXTinCaseInfo = False
            self.CONTEXTinExaminerNameValue = False
        elif name == 'image':
            if self.CONTEXTinImages:
                self.CONTEXTinImage = False                
                self.CONTEXTimageMetadataHashSHA.append(self.CONTEXTimageMetadataHashTextSHA)
                self.CONTEXTimageMetadataHashMD5.append(self.CONTEXTimageMetadataHashTextMD5)
                self.CONTEXTimageMetadataHashText = ''
        elif name == 'images':
            self.CONTEXTinImages = False

if __name__ == '__main__':

#--- colours for diplayng messages on the standard output, if verbose is True the messages will be
#    shown on the std. output    
    C_CYAN = '\033[36m'
    C_BLACK = '\033[0m'   
    verbose = True 

    parserArgs = argparse.ArgumentParser(description='Parser to convert XML Report from UFED PA into CASE-JSON-LD standard.')

#---    report XML exported by UFED PA, to be converted/parsed into CASE
    parserArgs.add_argument('-r', '--report', dest='inFileXML', required=True, 
                    help='The UFED XML report from which to extract digital traces and convert them into CASE; it supports UFED PA version from 7.24 to 7.37')

    parserArgs.add_argument('-o', '--output', dest='output_CASE_JSON', required=True, help='File CASE-JSON-LD to be generated')

    parserArgs.add_argument('-d', '--debug', dest='output_DEBUG', required=False, help='File for writing debug')

    args = parserArgs.parse_args()


    if args.output_CASE_JSON is None:
        path, name = os.path.split("".join([args.inFileXML[0:-3], 'JSON']))
        args.output_CASE_JSON = name

    head, tail = os.path.split(args.output_CASE_JSON)
    
    if verbose:
        print('*--- Input paramaters start \n')
        print("".join(['\tFile XML:\t\t', args.inFileXML]))
        print("".join(['\tFile Output:\t\t', args.output_CASE_JSON]))

    if args.output_DEBUG is None:
        pass
    else:
        if verbose:
            print("".join(['\tFile Debug:\t\t', args.output_DEBUG]))

    if verbose:
        print('\n*--- Input paramaters end')
        print("".join(['\n\n', C_CYAN, '*** Start processing: ', strftime("%Y-%m-%d %H:%M:%S", localtime()), C_BLACK, '\n']))

#---    baseLocalPath is for setting the fileLocalPath property of teh Observables. 
    baseLocalPath = ''
    sax_parser = UFEDparser(report_xml=args.inFileXML, json_output=args.output_CASE_JSON, 
        base_local_path=baseLocalPath, mode_verbose=verbose)
    
    Handler = sax_parser.processXmlReport()

    if args.output_DEBUG is None:
        pass
    else: 
        import UFEDdebug
        debug = UFEDdebug.ParserDebug(args.output_DEBUG)
        #debug.writeDebugEXTRA_INFO(Handler)     
        #debug.writeDebugCALL(Handler)              
        #debug.writeDebugCHAT(Handler)     
        #debug.writeDebugCONTACT(Handler)  
        #debug.writeDebugCONTEXT(Handler)       
        #debug.writeDebugEMAIL(Handler)         
        #debug.writeDebugFILES(Handler)     
        #debug.writeDebugSMS(Handler)     
        #debug.writeDebugU_ACCOUNT(Handler)     
        #debug.writeDebugWEB_PAGE(Handler)     
        debug.closeDebug() 
            
    sax_parser.show_elapsed_time(sax_parser.tic_start, 'End processing')
