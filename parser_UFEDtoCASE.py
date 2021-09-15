#!/usr/bin/env python3

####
#	parser_UFEDtoCASE: SAX parser for extracrtiong the main Artifacts from a 
#   UFED XML report
###

import xml.sax 
import string
import argparse
import os
import codecs
import UFEDtoJSON as CJ
import re
import timeit

class UFEDgadget():
    def __init__(self, xmlReport, jsonCASE, baseLocalPath):    
        self.xmlReport = xmlReport
        self.jsonCASE = jsonCASE
        self.baseLocalPath = baseLocalPath

    def processXmlReport(self):
#---    create the SAX parser
#    
        SAXparser = xml.sax.make_parser()

#---    override the default ContextHandler
#            
        Handler = ExtractTraces(self.baseLocalPath) 
        Handler.createOutFile(self.jsonCASE)

        SAXparser.setContentHandler(Handler)
       
        SAXparser.parse(self.xmlReport)
        
        print('\n\n\nCASE is being generated ...')

        phoneNumber = Handler.findOwnerPhone(Handler.U_ACCOUNTusername).replace(' ', '')
        
        if phoneNumber == '':
            phoneNumber = Handler.CONTEXTdeviceMsisdnText.replace(' ', '')

        print(Handler.C_cyan + "owner's phone number: " + phoneNumber + '\n' + Handler.C_end)

        caseTrace = CJ.UFEDtoJSON(Handler.fOut, Handler.U_ACCOUNTsource, 
        Handler.U_ACCOUNTname, Handler.U_ACCOUNTusername)

#---    caseTrace.storeUserAccount(Handler.U_ACCOUNTsource, Handler.U_ACCOUNTname,
#       Handler.U_ACCOUNTusername)

        caseTrace.writeHeader()


        caseTrace.writePhoneOwner(phoneNumber)

        caseTrace.writeExtraInfo(Handler.EXTRA_INFOdictPath, Handler.EXTRA_INFOdictSize,
                        Handler.EXTRA_INFOdictTableName, Handler.EXTRA_INFOdictOffset,
                        Handler.EXTRA_INFOdictNodeInfoId)

        caseTrace.writeFiles(Handler.FILEid, Handler.FILEpath, Handler.FILEsize,
                        Handler.FILEmd5, Handler.FILEtags, Handler.FILEtimeCreate, 
                        Handler.FILEtimeModify, Handler.FILEtimeAccess, Handler.FILElocalPath, 
                        Handler.FILEiNodeNumber, Handler.FILEiNodeTimeModify, 
                        Handler.FILEownerGID, Handler.FILEownerUID)


#---    CONTACTname is a list of names of contacts, 
#       CONTACTphoneNums is a list of list of phone numbers, each item represents 
#       the list of phone numbers of a contact. So a contact is identified by 
#       the item CONTACname[i] and this contact may have many phone numbers 
#       identified by CONTACTphoneNums[i][j] iterating on the index j
#       The writeContacts method must be invoked before the processing of
#       the SMS and Call traces, both of them are based on the list of phone numbers        
#  
        caseTrace.writePhoneAccountFromContacts(Handler.CONTACTname, Handler.CONTACTphoneNums)

#---    all parameters are lists containing data of the extracted SMS
#    
        caseTrace.writeSms(Handler.SMSid, Handler.SMSstatus, Handler.SMStimeStamp, 
                    Handler.SMSpartyRoles, Handler.SMSpartyIdentifiers, 
                    Handler.SMSsmsc, Handler.SMSpartyNames, Handler.SMSfolder, 
                    Handler.SMSbody, Handler.SMSsource)

#---    all parameters are lists containing data of the extracted CALL_LOG
#    
        caseTrace.writeCall(Handler.CALLid, Handler.CALLstatus, Handler.CALLsource, 
                    Handler.CALLtimeStamp, Handler.CALLdirection, Handler.CALLduration,
                    Handler.CALLrolesTO, Handler.CALLrolesFROM, Handler.CALLnamesTO, 
                    Handler.CALLnamesFROM, Handler.CALLoutcome, Handler.CALLidentifiersTO, 
                    Handler.CALLidentifiersFROM)

#---    all parameters are lists containing data of the extracted CHAT
#    
        caseTrace.writeChat(Handler.CHATid, Handler.CHATstatus, Handler.CHATsource, 
                    Handler.CHATpartyIdentifiers, Handler.CHATpartyNames, 
                    Handler.CHATmsgIdentifiersFrom, Handler.CHATmsgNamesFrom, 
                    Handler.CHATmsgIdentifiersTo, Handler.CHATmsgNamesTo,
                    Handler.CHATmsgBodies, Handler.CHATmsgStatuses,
                    Handler.CHATmsgOutcomes, Handler.CHATmsgTimeStamps, 
                    Handler.CHATmsgAttachmentFilenames, Handler.CHATmsgAttachmentUrls)

#---    all parameters are lists containing data of the extracted EMAIL
#
        caseTrace.writeEmail(Handler.EMAILid, Handler.EMAILstatus, Handler.EMAILsource, 
                    Handler.EMAILidentifierFROM, Handler.EMAILidentifiersTO, 
                    Handler.EMAILidentifiersCC, Handler.EMAILidentifiersBCC, 
                    Handler.EMAILbody, Handler.EMAILsubject,
                    Handler.EMAILtimeStamp, Handler.EMAILattachmentsFilename)

# all parameters are lists containing data of the extracted WEB_PAGE
#
        caseTrace.writeWebPages(Handler.WEB_PAGEid, Handler.WEB_PAGEstatus, Handler.WEB_PAGEsource, 
                    Handler.WEB_PAGEurl, Handler.WEB_PAGEtitle, Handler.WEB_PAGEvisitCount,
                    Handler.WEB_PAGElastVisited)

#---    write the context info: Device info, Forensic tool info, 
#       Acquisition/Extraction investigative Actions, Peformer info
#       deviceCreationTime is the Extraction start time
#
        caseTrace.writeContextUfed(Handler.CONTEXTufedVersionText, 
            Handler.CONTEXTdeviceCreationTimeText, Handler.CONTEXTdeviceExtractionStartText,
            Handler.CONTEXTdeviceExtractionEndText, Handler.CONTEXTexaminerNameText,
            Handler.CONTEXTdeviceBluetoothAddressText, Handler.CONTEXTdeviceIdText, 
            Handler.CONTEXTdevicePhoneModelText, Handler.CONTEXTdeviceOsTypeText, 
            Handler.CONTEXTdeviceOsVersionText, Handler.CONTEXTdevicePhoneVendorText, 
            Handler.CONTEXTdeviceMacAddressText, Handler.CONTEXTdeviceIccidText, 
            Handler.CONTEXTdeviceImsiText, Handler.CONTEXTdeviceImeiText, 
            Handler.CONTEXTimagePath, Handler.CONTEXTimageSize, 
            Handler.CONTEXTimageMetadataHashSHA, Handler.CONTEXTimageMetadataHashMD5)

#---    this write a single line to complete the JSON output file
#    
        caseTrace.writeLastLine()  

        Handler.fOut.close()  
        return Handler


class ExtractTraces(xml.sax.ContentHandler):
    def __init__(self, baseLocalPath):
        self.fOut = ''
        self.lineXML = 0
        self.skipLine = False
        self.Observable = False

        self.C_green  = '\033[32m'
        self.C_grey  = '\033[37m'
        self.C_red = '\033[31m'
        self.C_cyan = '\033[36m'
        self.C_end = '\033[0m'

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

        self.EXTRA_INFOin = False 
        self.EXTRA_INFOnodeInfoin = False
        self.EXTRA_INFOid = ''
        self.EXTRA_INFOlistId = []
        self.EXTRA_INFOdictPath = {}
        self.EXTRA_INFOdictSize = {}
        self.EXTRA_INFOdictTableName = {}
        self.EXTRA_INFOdictOffset = {}
        self.EXTRA_INFOdictNodeInfoId = {}

#--     CALL  section
#        
        self.CALLtrace = 'call'
        self.CALLin = False
        self.CALLinSource = False
        self.CALLinSourceValue = False
        self.CALLinDirection = False
        self.CALLinDirectionValue = False        
        self.CALLinType = False
        self.CALLinTypeValue = False        
        self.CALLinOutcome = False
        self.CALLinOutcomeValue = False
        self.CALLinTimeStamp = False
        self.CALLinTimeStampValue = False
        self.CALLinDuration = False
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

#---    CHAT section
#        
        self.CHATtrace = "chat"
        self.CHATin = False
        self.CHATinSource = False
        self.CHATinSourceValue = False
        self.CHATinModel = False
        self.CHATinParty = False
        self.CHATinPartyIdentifier = False
        self.CHATinPartyIdentifierValue = False
        self.CHATinPartyName = False        
        self.CHATinPartyNameValue = False 
        self.CHATinMsg = False
        self.CHATinMsgParty = False
        self.CHATinMsgFrom = False
        self.CHATinMsgTo = False
        self.CHATinMsgIdentifierFrom = False
        self.CHATinMsgIdentifierFromValue = False
        self.CHATinMsgIdentifierTo = False
        self.CHATinMsgIdentifierToValue = False        
        self.CHATinMsgNameFrom = False
        self.CHATinMsgNameFromValue = False
        self.CHATinMsgNameTo = False
        self.CHATinMsgNameToValue = False
        self.CHATinMsgAttachment = False
        self.CHATinMsgContactPhoto = False
        self.CHATinMsgCoordinate = False
        self.CHATinMsgExtraData = False
        self.CHATinMsgSharedContacts = False
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
        self.CHATmsgNameTo = []
        self.CHATmsgNamesTo = []
        self.CHATmsgIdentifierTo = []
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
#        
        self.CHATpartyIdentifiers = []
        self.CHATpartyNames = []
        self.CHATmsgIdentifiersFrom = []
        self.CHATmsgNamesFrom = []
        self.CHATmsgIdentifiersTo = []
        self.CHATmsgBodies = []
        self.CHATmsgStatuses = []
        self.CHATmsgOutcomes = []
        self.CHATmsgTimeStamp = []
        self.CHATmsgTimeStamps = []
        self.CHATmsgAttachmentFilenames = []
        self.CHATmsgAttachmentUrls = [] 

        # EMAIL section
        self.EMAILtrace = 'email'
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
        self.SMStrace = 'sms'
        self.SMSin = False
        self.SMSinSource = False
        self.SMSinSourceValue = False        
        self.SMSinTimeStamp = False
        self.SMSinTimeStampValue = False
        self.SMSinBody = False
        self.SMSinBodyValue = False
        self.SMSinFolder = False
        self.SMSinFolderValue = False

#---    Short Message Service Center
#        
        self.SMSinSmsc = False
        self.SMSinSmscValue = False

        self.SMSinParty = False
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
        

# CONTACT section
#        
        self.CONTACTtrace = 'contact'
        self.CONTACTin = False
        self.CONTACTinPhoneEntries = False
        self.CONTACTinPhoneNum = False
        self.CONTACTinPhoneNumValue = False
        self.CONTACTinName = False
        self.CONTACTinNameValue = False
        self.CONTACTinElementModelIgnore = False
        self.CONTACTtotal = 0
        self.CONTACTdeleted = 0
        self.CONTACTnameText = ''
        self.CONTACTphoneNumText = ''
        self.CONTACTid = []
        self.CONTACTstatus = []
        self.CONTACTname = []

#---    the CONTACTphoneNum list contains the phone numbers of a CONTACT. 
#       At the end of CONTACT elements processing, this list is appended to 
#       the below  CONTACTphoneNums list
#        
        self.CONTACTphoneNum = []

#---    list of list: the first list contains all contacts, each item of this list, 
#       that is, each contact may contain more than one phone number.
#       so CONTACTphoneNums[i] is the list of phone numbers of the contact i,
#       all the phone numbers of the CONTACT i is contained in the list
#       CONTACTphoneNums[i][j]
#
        self.CONTACTphoneNums = []


#---    WEB HISTORY section
#        
        self.WEB_PAGEtrace = 'url'
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
        
        # USER ACCOUNT section, it is for detecting username account
        # of the owner's phone number for all application installed on
        # the device (i.e. account Whatsapp that includes the phone number, 
        # Skype, Telegram, Snapchat, etc.)
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

#---    Data for the context (tool, mobile device info, acquisition and 
#       extraction investigative action
#        
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
        text = text.replace('\n', ' ')
        text = text.replace('"', "'")
        text = text.replace('\n', ' ')
        return text

    def createOutFile(self, filename):
        self.fOut = codecs.open(filename, 'w', encoding='utf8')

    def findOwnerPhone(self, UserAccounts):
        ownerPhone = ''
        for account in UserAccounts:
            posAccount = account.find('@s.whatsapp.net')
            if posAccount > -1:
                ownerPhone = account[0:posAccount]
                break
        return ownerPhone
    
    def storeTraceStatus(self, listTrace, status, sDeleted):
        if status == 'Deleted':
            listTrace.append('Deleted')
            sDeleted +=1
        else:
            listTrace.append('Intact')
                        

    def printObservable(self, oName, oCount):        
        line =  'processing traces --> ' + oName +  ' n. ' +  \
            str(oCount) + self.C_end
        if oCount == 1:
            print(self.C_green + '\n' + line, end='\r') 
        else:
            print(self.C_green + line, end='\r') 

    def __startElementModelCALL(self, attrValue, CALLid, CALLstate):
        if attrValue == 'Call':
            self.CALLin = True
            self.CALLtotal += 1
            self.printObservable('CALL', self.CALLtotal)
            self.CALLid.append(CALLid)
            self.storeTraceStatus(self.CALLstatus, CALLstate, self.CALLdeleted)
            self.skipLine = True 
            self.Observable = True 

    def __startElementModelCHAT(self, attrValue, CHATid, CHATstate):
        if attrValue == 'Chat':                
            self.CHATin = True
            self.CHATtotal += 1
            self.printObservable('CHAT', self.CHATtotal)
            self.CHATid.append(CHATid)
            self.storeTraceStatus(self.CHATstatus, CHATstate, self.CHATdeleted)
            self.skipLine = True 
            self.Observable = True             

        if attrValue == 'InstantMessage': 
            if self.CHATin:
                self.CHATinMsg = True
                # status of the Chat Message, deleted or intact
                self.CHATmsgStatus.append(CHATstate)
                self.CHATmsgNum += 1

        if attrValue == 'Attachment':
            if self.CHATin:                
                self.CHATinMsgAttachment = True

        if attrValue == 'ContactPhoto':
            if self.CHATin:
                self.CHATinMsgContactPhoto = True

        if attrValue == 'Coordinate':
            if self.CHATin:
                self.CHATinMsgCoordinate = True

        if attrValue == 'MessageExtraData':
            if self.CHATin:
                self.CHATinMsgExtraData = True

        if attrValue == 'SharedContacts':
            if self.CHATin:
                self.CHATinMsgSharedContacts = True        

        if attrValue == 'InstantMessage': 
            if self.CHATin:
                self.CHATinMsg = True
                self.CHATmsgNum += 1

    def __startElementModelCONTACT(self, attrValue, CONTACTid, CONTACTstate):
        if attrValue == 'Contact':
            self.CONTACTin = True
            self.CONTACTtotal += 1
            self.printObservable('CONTACT', self.CONTACTtotal)
            self.skipLine = True  
            self.Observable = True 
            self.CONTACTid.append(CONTACTid)
            self.storeTraceStatus(self.CONTACTstatus, CONTACTstate, self.CONTACTdeleted)        
        
        else:
            if attrValue == "PhoneNumber":
                if self.CONTACTin:
                    self.CONTACTinPhoneEntries  = True
            else:
                if self.CONTACTin:
                    self.CONTACTinElementModelIgnore = True

    def __startElementModelEMAIL(self, attrValue, EMAILid, EMAILstate):
        if attrValue == 'Email':                
            self.EMAILin = True
            self.EMAILtotal += 1
            self.printObservable('EMAIL', self.EMAILtotal)
            self.EMAILid.append(EMAILid)
            self.storeTraceStatus(self.EMAILstatus, EMAILstate, self.EMAILdeleted) 
            self.skipLine = True  
            self.Observable = True 


    def __startElementModelSMS(self, attrValue, SMSid, SMSstate):
        if attrValue == 'SMS':                
            self.SMSin = True
            self.SMStotal += 1
            self.printObservable('SMS', self.SMStotal)
            self.SMSid.append(SMSid)
            self.storeTraceStatus(self.SMSstatus, SMSstate, self.SMSdeleted) 
            self.skipLine = True 
            self.Observable = True  

    def __startElementModelU_ACCOUNT(self, attrValue):
        if attrValue == 'UserAccount':
            self.U_ACCOUNTin = True
            self.U_ACCOUNTtotal+=1
            self.printObservable('U_ACCOUNT', self.U_ACCOUNTtotal)
            self.skipLine = True  
            self.Observable = True 

        if attrValue == "ContactPhoto":
            if self.U_ACCOUNTin:
                self.U_ACCOUNTinContactPhoto = True
        if attrValue == "ContactEntry":
            if self.U_ACCOUNTin:
                self.U_ACCOUNTinContactEntry = True
        if attrValue == "EmailAddress":
            if self.U_ACCOUNTin:
                self.U_ACCOUNTinEmailAddress = True
        if attrValue == "UserID":
            if self.U_ACCOUNTin:
                self.U_ACCOUNTinUserID = True


    def __startElementModelWEB_PAGE(self, attrValue, WEB_PAGEid, WEB_PAGEstate):
        if attrValue == 'VisitedPage':                
            self.WEB_PAGEin = True
            self.WEB_PAGEtotal += 1
            self.printObservable('WEB_HISTORY', self.WEB_PAGEtotal)
            self.WEB_PAGEid.append(WEB_PAGEid)
            self.storeTraceStatus(self.WEB_PAGEstatus, WEB_PAGEstate, self.WEB_PAGEdeleted) 
            self.skipLine = True 
            self.Observable = True  

    def __startElementModelFieldCHAT(self, attrValue):
        self.CHATinModel = True
        if self.CHATinMsg:
            if attrValue == 'From':
                self.CHATinMsgFrom = True

#---    not always the From/To Identifier and Name are present, so
#       in order to maintain the same number of items, the current
#       item is set to empty values 
#                
            if attrValue == 'To':
                self.CHATinMsgTo = True

#---    the element modelField with attribute name=From or To is
#       always present, but it may occur that there is no descendants
#       elements below. The ChatmsgNum variable takes trace of the number
#       of message, within a given Chat, that is being processed
#               
    def __startElementModelFieldEMAIL(self, attrValue):
        if self.EMAILin:
            if attrValue == 'From':
                self.EMAILinModelFieldFROM = True
            if attrValue == 'To':
                self.EMAILinMultiModelFieldTO = True
            if attrValue == 'Cc':
                self.EMAILinMultiModelFieldCC = True
            if attrValue == 'Bcc':
                self.EMAILinMultiModelFieldBCC = True
            if attrValue == 'Attachments':
                self.EMAILinMultiModelFieldAttachments = True

    def __startElementModelFieldSMS(self, attrValue):
        if self.SMSin:
            if attrValue == 'Parties':
                self.SMSinParty = True 

    def __startElementFieldCALL(self, attrValue):
        if self.CALLin:
            if attrValue == 'Source':
                if self.CALLinParty:
                    pass
                else:
                    self.CALLinSource = True
            
            if attrValue == 'Direction':
                self.CALLinDirection = True

            if attrValue == 'Type':
                self.CALLinType = True

            if attrValue == 'Status':
                if self.CALLinParty:
                    pass
                else:
                    self.CALLinOutcome = True

            if attrValue == 'TimeStamp':
                self.CALLinTimeStamp = True                       
            
            if attrValue == 'Duration':
                self.CALLinDuration = True                        

#---    fields inside the Party element
#            
            if attrValue == 'Role':
                self.CALLinRole = True
            
            if attrValue == 'Name':
                self.CALLinName = True
            
            if attrValue == 'Identifier':
                self.CALLinIdentifier = True

    def __startElementFieldCHAT(self, attrValue):
        if self.CHATinMsg:                                             
            if attrValue == 'Identifier':
                if self.CHATinMsgFrom:
                    self.CHATinMsgIdentifierFrom = True
                if self.CHATinMsgTo:
                    self.CHATinMsgIdentifierTo = True
            if attrValue == 'Name':
                if self.CHATinMsgFrom:
                    self.CHATinMsgNameFrom = True
                if self.CHATinMsgTo:
                    self.CHATinMsgNameTo = True
            if attrValue == 'Body':
                self.CHATinMsgBody = True
            if attrValue == 'TimeStamp':
                self.CHATinMsgTimeStamp = True
            if attrValue == 'Status':
                self.CHATinMsgOutcome = True

            if self.CHATinMsgAttachment:
                if attrValue =='Filename':                    
                    self.CHATinMsgAttachmentFilename = True
                if attrValue =='URL':
                    self.CHATinMsgAttachmentUrl = True
        else:
            if self.CHATinParty:
                if attrValue == 'Name': 
                    self.CHATinPartyName = True
                if attrValue == 'Identifier': 
                    self.CHATinPartyIdentifier = True
            else:
                if self.CHATin :
                        if attrValue == 'Source':
                            if not self.CHATinModel:
                                self.CHATinSource = True

    def __startElementFieldCONTACT(self, attrValue):
        if self.CONTACTin:
            if self.CONTACTinPhoneEntries:
                if attrValue == 'Value':
                    self.CONTACTinPhoneNum = True 
            else:
                if attrValue == 'Name':
                    self.CONTACTinName = True 

    def __startElementFieldEMAIL(self, attrValue):
        if self.EMAILin:
            if attrValue == 'Source':
                if (self.EMAILinModelFieldFROM or \
                    self.EMAILinMultiModelFieldTO or \
                    self.EMAILinMultiModelFieldCC or \
                    self.EMAILinMultiModelFieldBCC or \
                    self.EMAILinMultiModelFieldAttachments):
                    pass
                else:
                    self.EMAILinSource = True

            if attrValue == 'Subject':
                self.EMAILinSubject = True
            
            if attrValue == 'Identifier':
                if self.EMAILinModelFieldFROM:
                    self.EMAILinIdentifierFROM = True
                if self.EMAILinMultiModelFieldTO:
                    self.EMAILinIdentifierTO = True
                if self.EMAILinMultiModelFieldCC:
                    self.EMAILinIdentifierCC = True
                if self.EMAILinMultiModelFieldBCC:
                    self.EMAILinIdentifierBCC = True

            if attrValue == 'Filename':
                if self.EMAILinMultiModelFieldAttachments:
                    self.EMAILinAttachmentFilename = True
            
            if attrValue == 'Body':
                self.EMAILinBody = True
            
            if attrValue == 'TimeStamp':
                self.EMAILinTimeStamp = True
    
    def __startElementFieldCONTEXT(self, attrValue):
        if self.CONTEXTinCaseInfo:
            if attrValue == 'ExaminerName':
                self.CONTEXTinExaminerNameValue = True

    def __startElementFieldSMS(self, attrValue):
        if self.SMSin:
            if self.SMSinParty:
                if attrValue == 'Identifier':
                    self.SMSinPartyIdentifier = True            
                if attrValue == 'Role':
                    self.SMSinPartyRole = True            
                if attrValue == 'Name':
                    self.SMSinPartyName = True
            else:
                if attrValue == 'Source':
                    self.SMSinSource = True
                if attrValue == 'TimeStamp':
                    self.SMSinTimeStamp = True
                if attrValue == 'Body':
                    self.SMSinBody = True
                if attrValue == 'Folder':
                    self.SMSinFolder = True
                if attrValue == 'SMSC':
                    self.SMSinSmsc = True
             

    def __startElementFieldU_ACCOUNT(self, attrValue):
        if self.U_ACCOUNTin:
            if self.U_ACCOUNTinContactPhoto:
                return(0)
            if self.U_ACCOUNTinEmailAddress:                
                return(0)
            if self.U_ACCOUNTinUserID:
                return(0)
            if attrValue == 'Source':
                self.U_ACCOUNTinSource = True
            if attrValue == 'Name':
                self.U_ACCOUNTinName = True
            if attrValue == 'Username':
                self.U_ACCOUNTinUsername = True

    def __startElementFieldWEB_PAGE(self, attrValue):
        if self.WEB_PAGEin:
            if attrValue == 'Source':
                self.WEB_PAGEinSource = True
            if attrValue == 'Title':
                self.WEB_PAGEinTitle = True
            if attrValue == 'Url':
                self.WEB_PAGEinUrl = True
            if attrValue == 'LastVisited':
                self.WEB_PAGEinLastVisited = True
            if attrValue == 'VisitCount':
                self.WEB_PAGEinVisitCount = True

    def __startElementItemCONTEXT(self, attrValue):
        if self.CONTEXTinAdditionalFields:
            if attrValue == 'DeviceInfoCreationTime':
                self.CONTEXTinDeviceCreationTimeValue = True
            if attrValue == 'UFED_PA_Version':
                self.CONTEXTinUfedVersionValue = True
        
        if self.CONTEXTinExtractionData:
            if attrValue == 'DeviceInfoExtractionStartDateTime':
                self.CONTEXTinDeviceExtractionStart = True
            if attrValue == 'DeviceInfoExtractionEndDateTime':
                self.CONTEXTinDeviceExtractionEnd = True

        if self.CONTEXTinDeviceInfo:
            if attrValue == 'DeviceInfoOSVersion':
                self.CONTEXTinDeviceOsVersionValue = True
            if attrValue == 'DeviceInfoDetectedPhoneVendor':
                self.CONTEXTinDevicePhoneVendorValue = True
            if attrValue == 'DeviceInfoDetectedPhoneModel':
                self.CONTEXTinDevicePhoneModelValue = True
            if (attrValue == 'DeviceInfoAppleID') or \
                (attrValue == 'DeviceInfoAndroidID') :
                self.CONTEXTinDeviceIdValue = True
            if (attrValue == 'Indirizzo MAC') or \
                (attrValue == 'MAC Address'):
                self.CONTEXTinDeviceMacAddressValue = True
            if attrValue == 'ICCID':
                self.CONTEXTinDeviceIccidValue = True
            if attrValue == 'MSISDN':
                self.CONTEXTinDeviceMsisdnValue = True
            if (attrValue == 'Indirizzo MAC Bluetooth') or \
                (attrValue == 'Bluetooth MAC Address'):
                self.CONTEXTinDeviceBluetoothAddressValue = True
            if attrValue == 'IMSI':
                self.CONTEXTinDeviceImsiValue = True
            if attrValue == 'IMEI':
                self.CONTEXTinDeviceImeiValue = True
            if attrValue == 'DeviceInfoOSType':
                self.CONTEXTinDeviceOsTypeValue = True

        if self.CONTEXTinImageMetadataHash:
            if attrValue == 'SHA256':
                self.CONTEXTinImageMetadataHashValueSHA = True
            if attrValue =='MD5':
                self.CONTEXTinImageMetadataHashValueMD5 = True

    def __startElementItemTAGGED_FILES(self, attrValue):
        if self.TAGGED_FILESinFile:
            if self.TAGGED_FILESsystem:
                pass
            else:
                if attrValue == 'MD5':
                    self.TAGGED_FILESinMD5 = True
                if attrValue == 'Tags':
                    self.TAGGED_FILESinTags = True
                if attrValue == 'Local Path':
                    self.TAGGED_FILESinLocalPath = True
        
        if self.TAGGED_FILESinMetadata:
            if self.TAGGED_FILESsystem:
                pass
            else:
                if attrValue == 'Inode Number':
                    self.TAGGED_FILESinInodeNumber = True
                if attrValue == 'CoreFileSystemFileSystemNodeModifyTime':
                    self.TAGGED_FILESinInodeTimeModify = True
                if attrValue == 'Owner GID':
                    self.TAGGED_FILESinOwnerGID = True
                if attrValue == 'Owner UID':
                    self.TAGGED_FILESinOwnerUID = True 

    def __startElementValueCALL(self):
        if self.CALLinSource:
            self.CALLinSourceValue = True
        if self.CALLinDirection:
            self.CALLinDirectionValue = True
        if self.CALLinType:
            self.CALLinTypeValue = True
        if self.CALLinDuration:
            self.CALLinDurationValue = True
        if self.CALLinOutcome:
            self.CALLinOutcomeValue = True
        if self.CALLinTimeStamp:
            self.CALLinTimeStampValue = True
        if self.CALLinRole:
            self.CALLinRoleValue = True
        if self.CALLinName:
            self.CALLinNameValue = True
        if self.CALLinIdentifier:
            #print('CALLinIdentifierValue')
            self.CALLinIdentifierValue = True

    def __startElementValueCONTACT(self):
        if self.CONTACTinName:
            self.CONTACTinNameValue = True            
        if self.CONTACTinPhoneNum:
            self.CONTACTinPhoneNumValue = True

    def __startElementValueCHAT(self, attrValue):
        if self.CHATinSource:
            self.CHATinSourceValue = True
        if self.CHATinPartyIdentifier:
            self.CHATinPartyIdentifierValue = True
        if self.CHATinPartyName:
            self.CHATinPartyNameValue = True
        if self.CHATinMsgNameFrom:
            self.CHATinMsgNameFromValue = True
        if self.CHATinMsgIdentifierFrom:
            self.CHATinMsgIdentifierFromValue = True
        if self.CHATinMsgNameTo:
            self.CHATinMsgNameToValue = True
        if self.CHATinMsgIdentifierTo:
            self.CHATinMsgIdentifierToValue = True
        if self.CHATinMsgBody:
            self.CHATinMsgBodyValue = True
        if self.CHATinMsgOutcome:
            if attrValue == "MessageStatus":
                self.CHATinMsgOutcomeValue = True
        if self.CHATinMsgTimeStamp:
            self.CHATinMsgTimeStampValue = True
        if self.CHATinMsgAttachmentFilename:
            self.CHATinMsgAttachmentFilenameValue = True
        if self.CHATinMsgAttachmentUrl:
            self.CHATinMsgAttachmentUrlValue = True

    def __startElementValueEMAIL(self):
        if self.EMAILin:
            if self.EMAILinIdentifierFROM:
                self.EMAILinIdentifierFROMvalue = True
            if self.EMAILinIdentifierTO:
                self.EMAILinIdentifierTOvalue = True
            if self.EMAILinIdentifierCC:
                self.EMAILinIdentifierCCvalue = True
            if self.EMAILinIdentifierBCC:
                self.EMAILinIdentifierBCCvalue = Tru
            if self.EMAILinSource:
                self.EMAILinSourceValue = True
            if self.EMAILinBody:
                self.EMAILinBodyValue = True
            if self.EMAILinSubject:
                self.EMAILinSubjectValue = True
            if self.EMAILinTimeStamp:
                self.EMAILinTimeStampValue = True
            if self.EMAILinAttachmentFilename:
                self.EMAILinAttachmentFilenameValue = True

    def __startElementValueSMS(self):
        if self.SMSinSource:
            self.SMSinSourceValue = True
        if self.SMSinTimeStamp:
            self.SMSinTimeStampValue = True
        if self.SMSinBody:
            self.SMSinBodyValue = True
        if self.SMSinFolder:
            self.SMSinFolderValue = True
        if self.SMSinSmsc:
            self.SMSinSmscValue = True
        
        if self.SMSinPartyRole:
            self.SMSinPartyRoleValue = True            
        if self.SMSinPartyIdentifier:
            self.SMSinPartyIdentifierValue = True        
        if self.SMSinPartyName:
            self.SMSinPartyNameValue = True

    def __startElementValueU_ACCOUNT(self):
        if self.U_ACCOUNTin:                
            if self.U_ACCOUNTinSource:
                self.U_ACCOUNTinSourceValue = True
            if self.U_ACCOUNTinName:
                self.U_ACCOUNTinNameValue = True
            if self.U_ACCOUNTinUsername:
                self.U_ACCOUNTinUsernameValue = True

    def __startElementValueWEB_PAGE(self):
        if self.WEB_PAGEinSource:
            self.WEB_PAGEinSourceValue = True
        if self.WEB_PAGEinTitle:
            self.WEB_PAGEinTitleValue = True
        if self.WEB_PAGEinUrl:
            self.WEB_PAGEinUrlValue = True
        if self.WEB_PAGEinVisitCount:
            self.WEB_PAGEinVisitCountValue = True
        if self.WEB_PAGEinLastVisited:
            self.WEB_PAGEinLastVisitedValue = True    

    def __startElementEmptyCALL(self):
        if self.CALLinSourceValue:
            self.CALLsourceText = ''

    def __startElementEmptyU_ACCOUNT(self):
        if self.U_ACCOUNTinSource:
            self.U_ACCOUNTsourceValueText = ''
            self.U_ACCOUNTinSourceValue = False
        if self.U_ACCOUNTinName:
            self.U_ACCOUNTnameValueText = ''
            self.U_ACCOUNTinNameValue = False
        if self.U_ACCOUNTinUsername:
            self.U_ACCOUNTusernameValueText = ''
            self.U_ACCOUNTinUsernameValue = False

    def __startElementEmptyWEB_PAGE(self):
        if self.WEB_PAGEinTitleValue:
            self.WEB_PAGEtitleText = ''
        if self.WEB_PAGEinVisitCountValue:
            self.WEB_PAGEvisitCountText = ''
        if self.WEB_PAGEinLastVisitedValue:
            self.WEB_PAGElastVisitedText = ''

#---    It captures each Element when it is opened., the order depends on their 
#       position from the beginning of the document
#            
    def startElement(self, name, attrs):
                                                                                        
        self.lineXML +=1
        attrType = attrs.get('type')
        attrName = attrs.get('name')
        attrSection = attrs.get('section')
        
        if name == 'model':                                    
            traceState = attrs.get('deleted_state')
            id = attrs.get('id')                        
            self.__startElementModelCALL(attrType, id, traceState) 
            self.__startElementModelCHAT(attrType, id, traceState)         
            self.__startElementModelCONTACT(attrType, id, traceState)
            self.__startElementModelEMAIL(attrType, id, traceState)
            self.__startElementModelSMS(attrType, id, traceState)
            self.__startElementModelU_ACCOUNT(attrType)
            self.__startElementModelWEB_PAGE(attrType, id, traceState)    

            if attrType == 'Party':                
                
                if self.CALLin:
                    self.CALLinParty = True 
                
                if self.CHATin:
                    if self.CHATinMsg: 
                        self.CHATinMsgParty = True 
                    else:
                        self.CHATinParty = True 
           
        if (name == 'modelField' or name =='multiModelField'):
            self.__startElementModelFieldCHAT(attrName)
            self.__startElementModelFieldEMAIL(attrName)
            self.__startElementModelFieldSMS(attrName)

        if name == 'field':             
            self.__startElementFieldCALL(attrName)
            self.__startElementFieldCHAT(attrName)
            self.__startElementFieldCONTACT(attrName)
            self.__startElementFieldEMAIL(attrName)
            self.__startElementFieldSMS(attrName)
            self.__startElementFieldU_ACCOUNT(attrName)
            self.__startElementFieldWEB_PAGE(attrName)
            attrFieldType = attrs.get('fieldType')
            self.__startElementFieldCONTEXT(attrFieldType)

                                                  
        if name == 'value':            
            self.__startElementValueCALL()            
            self.__startElementValueCHAT(attrType)
            self.__startElementValueCONTACT()
            self.__startElementValueEMAIL()
            self.__startElementValueSMS()
            self.__startElementValueU_ACCOUNT()
            self.__startElementValueWEB_PAGE()

        if name == 'empty':
            self.__startElementEmptyCALL()
            self.__startElementEmptyU_ACCOUNT()
            self.__startElementEmptyWEB_PAGE()

        if name == 'taggedFiles':
            self.TAGGED_FILESin = True

#---    extraInfo @id is the link with the Trace @id, for any kind of Trace 
#            
        if name == 'extraInfo':
            self.EXTRA_INFOin = True
            self.EXTRA_INFOid = attrs.get('id')
            self.EXTRA_INFOlistId.append(self.EXTRA_INFOid)
            self.EXTRA_INFOdictPath[self.EXTRA_INFOid] = ''
            self.EXTRA_INFOdictSize[self.EXTRA_INFOid] = ''
            self.EXTRA_INFOdictTableName[self.EXTRA_INFOid] = ''
            self.EXTRA_INFOdictOffset[self.EXTRA_INFOid] = ''
            self.EXTRA_INFOdictNodeInfoId[self.EXTRA_INFOid] = ''


        if name == 'nodeInfo':
            if self.EXTRA_INFOin:
                self.EXTRA_INFOnodeInfoin = True              

#---    key of the dictionaries containing the infoNode values.
#       Different values are separated by @@@
#                
                i = self.EXTRA_INFOid

#---    in some cases there are more than one single nodeInfo
#       contained in the extraInfo element, so a dictionary with
#       key = extraInfoID is necessary to store the whole info                
#                
                if attrs.get('id') is None:                    
                    self.EXTRA_INFOdictNodeInfoId[i] = ''
                    charSep = ''
                else:
                    self.EXTRA_INFOdictNodeInfoId[i] += '@@@' + attrs.get('id')
                    charSep = '@@@'

                self.EXTRA_INFOdictPath[i] += charSep + str(attrs.get('path'))
                self.EXTRA_INFOdictSize[i] += charSep + str(attrs.get('size'))
                self.EXTRA_INFOdictTableName[i] += charSep + str(attrs.get('tableName'))
                self.EXTRA_INFOdictOffset[i] += charSep + str(attrs.get('offset'))
                    

        if name == 'file':
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
                    self.FILEidx += 1                                        

        if name == 'accessInfo':
            if self.TAGGED_FILESinFile:
                if self.TAGGED_FILESsystem:
                    pass
                else:
                    self.TAGGED_FILESinAccessInfo = True
                
        if name == "timestamp":
            if self.TAGGED_FILESinAccessInfo:
                if attrName == 'CreationTime':
                    self.TAGGED_FILESinAccessInfoCreate = True           
                if attrName == 'ModifyTime':
                    self.TAGGED_FILESinAccessInfoModify = True
                if attrName == 'AccessTime':
                    self.TAGGED_FILESinAccessInfoAccess = True

        if name == 'metadata':
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

        if name == 'item':
            self.__startElementItemTAGGED_FILES(attrName)
            self.__startElementItemCONTEXT(attrName)

        if name == 'images':
            self.CONTEXTinImages = True

        if name == 'image':
            if self.CONTEXTinImages:
                self.CONTEXTinImage = True
                #print("attr namme=image, CONTEXTimagePath: " + attrs.get('path'))
                self.CONTEXTimagePath.append(attrs.get('path'))
                self.CONTEXTimageSize.append(attrs.get('size'))

        if name == 'caseInformation':
            self.CONTEXTinCaseInfo = True            
                         

        if (not self.Observable):
            line = self.C_grey + '*\tProcessing Element <' + name + '> at line '
            line += str(self.lineXML) + ' ...'  + self.C_end
            if self.skipLine:
                print ('\n' + line , end='\r')
                self.skipLine = False                  
            else:
                print (line , end='\r') 

#---    it captures the value/character inside the Text Elements
#                
    def characters(self, ch):
#---    SMS processing
#        
        if self.SMSinSourceValue:
            self.SMSsourceText += ch
        if self.SMSinTimeStampValue:
            self.SMStimeStampText += ch
        if self.SMSinBodyValue:
            self.SMSbodyText += ch 
        if self.SMSinFolderValue:
            self.SMSfolderText += ch 
        if self.SMSinSmscValue:
            self.SMSsmscText += ch   
        
        if self.SMSinPartyIdentifierValue:
            self.SMSpartyIdentifierText += ch
        if self.SMSinPartyRoleValue:
            self.SMSpartyRoleText += ch        
        if self.SMSinPartyNameValue:
            self.SMSpartyNameText += ch

#---    CHAT processing
#            
        if self.CHATinSourceValue:
            self.CHATsourceText += ch        
        if self.CHATinPartyIdentifierValue:
            self.CHATpartyIdentifierText += ch        
        if self.CHATinPartyNameValue:
            self.CHATpartyNameText += ch        
        if self.CHATinMsgIdentifierFromValue:
            self.CHATmsgIdentifierFromText += ch               
        if self.CHATinMsgNameFromValue:
            self.CHATmsgNameFromText += ch        
        if self.CHATinMsgIdentifierToValue:
            if  self.CHATmsgIdentifierToText == '':
                self.CHATmsgIdentifierToText += ch
            else:
                self.CHATmsgIdentifierToText += '###' + ch
        if self.CHATinMsgNameToValue:
            if self.CHATmsgNameToText == '':
                self.CHATmsgNameToText += ch
            else:
                self.CHATmsgNameToText += '###' + ch
        if self.CHATinMsgBodyValue:
            self.CHATmsgBodyText += ch
        if self.CHATinMsgOutcomeValue:
            self.CHATmsgOutcomeText += ch
        if self.CHATinMsgTimeStampValue:
            self.CHATmsgTimeStampText += ch
        if self.CHATinMsgAttachmentFilenameValue:
            if self.CHATmsgAttachmentFilenameText == '':
                self.CHATmsgAttachmentFilenameText += ch
            else:

#---    The separator ### is for dividing more than one attachment to the same msg
#                
                self.CHATmsgAttachmentFilenameText += '###' + ch
        if self.CHATinMsgAttachmentUrlValue:
            if self.CHATmsgAttachmentUrlText == '':
                self.CHATmsgAttachmentUrlText += ch
            else:
                self.CHATmsgAttachmentUrlText += '###' + ch

#---    CALL processing
#                
        if self.CALLinSourceValue:
            self.CALLsourceText += ch
        if self.CALLinTimeStampValue:
            self.CALLtimeStampText += ch
        if self.CALLinDirectionValue:
            self.CALLdirectionText += ch
        if self.CALLinTypeValue:
            self.CALLtypeText += ch
        if self.CALLinDurationValue:
            self.CALLdurationText += ch
        if self.CALLinOutcomeValue:
            self.CALLoutcomeText += ch
        if self.CALLinRoleValue:
            self.CALLroleText += ch
        if self.CALLinNameValue:
            self.CALLnameText += ch
            #print(f'#call {self.CALLtotal}, name caller {self.CALLnameText}')
        if self.CALLinIdentifierValue:
            self.CALLidentifierText += ch

#---    CONTACT processing
#            
        if self.CONTACTinNameValue:
            self.CONTACTnameText += ch        
        if self.CONTACTinPhoneNumValue:
            self.CONTACTphoneNumText += ch

#---    EMAIL processing
#            
        if self.EMAILinSourceValue:
            self.EMAILsourceText += ch
        if self.EMAILinIdentifierFROMvalue:
            self.EMAILidentifierFROMtext += ch
        if self.EMAILinIdentifierTOvalue:
            self.EMAILidentifierTOtext += ch
        if self.EMAILinIdentifierCCvalue:
            self.EMAILidentifierCCtext += ch
        if self.EMAILinIdentifierBCCvalue:
            self.EMAILidentifierBCCtext += ch
        if self.EMAILinBodyValue:
            self.EMAILbodyText += ch
        if self.EMAILinSubjectValue:
            self.EMAILsubjectText += ch
        if self.EMAILinTimeStampValue:
            self.EMAILtimeStampText += ch
        if self.EMAILinAttachmentFilenameValue:
            self.EMAILattachmentFilenameText += ch
        
#---    WEB_PAGE processing
#            
        if self.WEB_PAGEinSourceValue:
            self.WEB_PAGEsourceText += ch
        if self.WEB_PAGEinUrlValue:
            self.WEB_PAGEurlText += ch
        if self.WEB_PAGEinTitleValue:
            self.WEB_PAGEtitleText += ch
        if self.WEB_PAGEinVisitCountValue:
            self.WEB_PAGEvisitCountText += ch
        if self.WEB_PAGEinLastVisitedValue:
            self.WEB_PAGElastVisitedText += ch
        
#---    U_ACCOUNT processing for the owner phone number
#            
        if self.U_ACCOUNTinSourceValue:
            self.U_ACCOUNTsourceValueText += ch
        if self.U_ACCOUNTinNameValue:
            self.U_ACCOUNTnameValueText += ch
        if self.U_ACCOUNTinUsernameValue:
            self.U_ACCOUNTusernameValueText += ch
        
#---    TAGGED_FILES processing for Chain of Evidence
#            
        if self.TAGGED_FILESinAccessInfoCreate:
            self.TAGGED_FILESCreateText += ch
        if self.TAGGED_FILESinAccessInfoModify:
            self.TAGGED_FILESModifyText += ch
        if self.TAGGED_FILESinAccessInfoAccess:
            self.TAGGED_FILESAccessText += ch
        if self.TAGGED_FILESinMD5:
            self.TAGGED_FILESmd5Text += ch
        if self.TAGGED_FILESinTags:
            self.TAGGED_FILEStagsText += ch
        if self.TAGGED_FILESinLocalPath:
            self.TAGGED_FILESlocalPathText += ch
        if self.TAGGED_FILESinInodeNumber:
            self.TAGGED_FILESiNodeNumberText += ch
        if self.TAGGED_FILESinInodeTimeModify:
            self.TAGGED_FILESiNodeTimeModifyText += ch
        if self.TAGGED_FILESinOwnerGID:
            self.TAGGED_FILESownerGIDText += ch
        if self.TAGGED_FILESinOwnerUID:
            self.TAGGED_FILESownerUIDText += ch

#---    CONTEXT for the information about device, tool, 
#       acquisition/extrtaction actions
#
        if self.CONTEXTinDeviceCreationTimeValue:
            self.CONTEXTdeviceCreationTimeText += ch
        if self.CONTEXTinUfedVersionValue:
            self.CONTEXTufedVersionText += ch
        
        if self.CONTEXTinExaminerNameValue:
            self.CONTEXTexaminerNameText += ch
        
        if self.CONTEXTinDeviceExtractionStart:
            self.CONTEXTdeviceExtractionStartText += ch
        if self.CONTEXTinDeviceExtractionEnd:
            self.CONTEXTdeviceExtractionEndText += ch

        if self.CONTEXTinDeviceOsVersionValue:
            self.CONTEXTdeviceOsVersionText  += ch
        if self.CONTEXTinDevicePhoneVendorValue:
            self.CONTEXTdevicePhoneVendorText  += ch
        if self.CONTEXTinDevicePhoneModelValue:
            self.CONTEXTdevicePhoneModelText  += ch
        if self.CONTEXTinDeviceIdValue:
            self.CONTEXTdeviceIdText  += ch
        if self.CONTEXTinDeviceMacAddressValue:
            self.CONTEXTdeviceMacAddressText  += ch
        if self.CONTEXTinDeviceIccidValue:
            self.CONTEXTdeviceIccidText  += ch
        if self.CONTEXTinDeviceMsisdnValue:
            if self.CONTEXTdeviceMsisdnText.strip() == '':
                self.CONTEXTdeviceMsisdnText  += ch
        if self.CONTEXTinDeviceBluetoothAddressValue:
            self.CONTEXTdeviceBluetoothAddressText  += ch
        if self.CONTEXTinDeviceImsiValue:
            self.CONTEXTdeviceImsiText  += ch
        if self.CONTEXTinDeviceImeiValue:
            self.CONTEXTdeviceImeiText  += ch
        if self.CONTEXTinDeviceOsTypeValue:
            self.CONTEXTdeviceOsTypeText  += ch  

        if self.CONTEXTinImageMetadataHashValueSHA:
            self.CONTEXTimageMetadataHashTextSHA += ch          

        if self.CONTEXTinImageMetadataHashValueMD5:
            self.CONTEXTimageMetadataHashTextMD5 += ch          

    def __endElementModelSMS(self):
        if self.SMSinParty:
                self.SMSpartyIdentifier.append(self.SMSpartyIdentifierText)
                self.SMSpartyRole.append(self.SMSpartyRoleText)
                self.SMSpartyName.append(self.SMSpartyNameText)
                self.SMSpartyRoleText = ''
                self.SMSpartyIdentifierText = ''
                self.SMSpartyNameText = ''
        else:
            if self.SMSin:                                   
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
    
    def __endElementModelCALL(self):
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
        
        else:
            if self.CALLin:                                   
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
        if self.CONTACTinPhoneEntries:
                self.CONTACTinPhoneEntries = False        
        else:
            if self.CONTACTinElementModelIgnore:
                self.CONTACTinElementModelIgnore = False
            else:
                if self.CONTACTin:
                    self.CONTACTphoneNums.append(self.CONTACTphoneNum[:])
                    self.CONTACTname.append(self.CONTACTnameText)                    
                    self.CONTACTnameText = ''
                    self.CONTACTphoneNumText = ''
                    self.CONTACTphoneNum.clear()
                    self.CONTACTin = False

    def __endElementModelCHAT(self):
        # The element Party contains the two (or more?) subjects 
        # (identifier and name) involved in the Chat.   
        self.CHATinModel = False          
        if self.CHATinParty:
            if self.CHATpartyIdentifierText.strip() == '':
                pass
            else:
                self.CHATpartyIdentifier.append(self.CHATpartyIdentifierText)
                self.CHATpartyName.append(self.CHATpartyNameText)
            self.CHATpartyIdentifierText = ''
            self.CHATpartyNameText = ''               
            self.CHATinParty = False                
        else:
            if self.CHATinMsgParty:
                self.CHATinMsgParty = False
            # This corresponds to the end of the element model (type="InstantMessage") that
            # occurs when a message has been processed
            else:
                if (self.CHATinMsgAttachment or self.CHATinMsgContactPhoto or \
                        self.CHATinMsgCoordinate or self.CHATinMsgExtraData or \
                        self.CHATinMsgSharedContacts):
                        if self.CHATinMsgAttachment:
                            self.CHATinMsgAttachment = False
                        else:
                            if self.CHATinMsgContactPhoto:
                                self.CHATinMsgContactPhoto = False
                            else:
                                if self.CHATinMsgCoordinate:
                                    self.CHATinMsgCoordinate = False
                                else:
                                    if self.CHATinMsgExtraData:
                                        self.CHATinMsgExtraData = False
                                    else:
                                        if self.CHATinMsgSharedContacts:
                                            self.CHATinMsgSharedContacts = False
                else:
                    if self.CHATinMsg:
                        self.CHATmsgIdentifierFrom.append(self.CHATmsgIdentifierFromText.strip())
                        self.CHATmsgIdentifierTo.append(self.CHATmsgIdentifierToText.strip())
                        self.CHATmsgNameFrom.append(self.CHATmsgNameFromText.strip())
                        self.CHATmsgNameTo.append(self.CHATmsgNameToText.strip())
                        self.CHATmsgBody.append(self.CHATmsgBodyText.strip())
                        self.CHATmsgOutcome.append(self.CHATmsgOutcomeText.strip())
                        self.CHATmsgTimeStamp.append(self.CHATmsgTimeStampText)
                        self.CHATmsgAttachmentFilename.append(self.CHATmsgAttachmentFilenameText.strip())
                        self.CHATmsgAttachmentUrl.append(self.CHATmsgAttachmentUrlText.strip())
                        
                        #print('CHAT n.:' + str(self.CHATtotal))
                        #print('\tCHATmsgIdentifierFrom:' + str(self.CHATmsgIdentifierFromText))
                        #print('\tCHATmsgIdentifierTo:' + str(self.CHATmsgIdentifierToText))
                        self.CHATmsgIdentifierFromText = ''
                        self.CHATmsgIdentifierToText = ''
                        self.CHATmsgNameFromText = ''
                        self.CHATmsgNameToText = ''
                        self.CHATmsgBodyText = ''
                        self.CHATmsgOutcomeText = ''
                        self.CHATmsgTimeStampText = ''
                        self.CHATmsgAttachmentFilenameText = ''
                        self.CHATmsgAttachmentUrlText = ''
                        self.CHATinMsg = False
#---    This corresponds to the end of the element model (type="Chat") that
#       occurs when a Chat has been processed 
#                        
                    else: 
                        if self.CHATin:                    
#---    the notation msg[:] creates a copy of the list, otherwise the 
#       next clear would empty both instances: clearing the CHAT.msgBody
#       would empty the same item in the container list CHAT.msgBodies
#                            
                            if len(self.CHATmsgBody) == 0:
                                self.CHATmsgBody.append("")
                            if len(self.CHATmsgIdentifierTo) == 0:
                                self.CHATmsgIdentifierTo.append("")
                            if len(self.CHATmsgIdentifierFrom) == 0:
                                self.CHATmsgIdentifierFrom.append("")
                            if len(self.CHATmsgTimeStamp) == 0:
                                self.CHATmsgTimeStamp.append("")
                            if len(self.CHATmsgOutcome) == 0:
                                self.CHATmsgOutcome.append("")
                            if len(self.CHATmsgStatus) == 0:
                                self.CHATmsgStatus.append("")
                            if len(self.CHATmsgAttachmentFilename) == 0:
                                self.CHATmsgAttachmentFilename.append("")
                            if len(self.CHATmsgAttachmentUrl) == 0:
                                self.CHATmsgAttachmentUrl.append("")
                            if len(self.CHATmsgNameFrom) == 0:
                                self.CHATmsgNameFrom.append("")
                            if len(self.CHATmsgNameTo) == 0:
                                self.CHATmsgNameTo.append("")

                            self.CHATpartyIdentifiers.append(self.CHATpartyIdentifier[:])
                            self.CHATpartyNames.append(self.CHATpartyName[:])
                            self.CHATmsgIdentifiersFrom.append(self.CHATmsgIdentifierFrom[:])
                            self.CHATmsgIdentifiersTo.append(self.CHATmsgIdentifierTo[:])
                            self.CHATmsgNamesFrom.append(self.CHATmsgNameFrom[:])
                            self.CHATmsgNamesTo.append(self.CHATmsgNameTo[:])
                            self.CHATmsgBodies.append(self.CHATmsgBody[:])
                            self.CHATmsgStatuses.append(self.CHATmsgStatus[:])
                            self.CHATmsgOutcomes.append(self.CHATmsgOutcome[:])
                            self.CHATmsgTimeStamps.append(self.CHATmsgTimeStamp[:])
                            self.CHATmsgAttachmentFilenames.append(self.CHATmsgAttachmentFilename[:])
                            self.CHATmsgAttachmentUrls.append(self.CHATmsgAttachmentUrl[:])
                            self.CHATpartyIdentifier.clear()
                            self.CHATpartyName.clear()
                            self.CHATmsgIdentifierFrom.clear()
                            self.CHATmsgIdentifierTo.clear()
                            self.CHATmsgNameFrom.clear()
                            self.CHATmsgNameTo.clear()
                            self.CHATmsgBody.clear()
                            self.CHATmsgOutcome.clear()
                            self.CHATmsgStatus.clear()
                            self.CHATmsgTimeStamp.clear()
                            self.CHATmsgAttachmentFilename.clear()
                            self.CHATmsgAttachmentUrl.clear()
                            self.CHATmsgNum = -1
                            self.CHATin = False
                            
    def __endElementModelEMAIL(self):
        if (self.EMAILinModelFieldFROM or self.EMAILinMultiModelFieldTO or \
            self.EMAILinMultiModelFieldCC or self.EMAILinMultiModelFieldBCC or \
            self.EMAILinMultiModelFieldAttachments):
            if self.EMAILinModelFieldFROM:
                self.EMAILinModelFieldFROM = False
            if self.EMAILinMultiModelFieldTO:
                self.EMAILinMultiModelFieldTO = False
                self.EMAILidentifierTO.append(self.EMAILidentifierTOtext)
                self.EMAILidentifierTOtext = ''
            if self.EMAILinMultiModelFieldCC:
                self.EMAILinMultiModelFieldCC = False
                self.EMAILidentifierCC.append(self.EMAILidentifierCCtext)
                self.EMAILidentifierCCtext = ''
            if self.EMAILinMultiModelFieldBCC:
                self.EMAILinMultiModelFieldBCC = False
                self.EMAILidentifierBCC.append(self.EMAILidentifierBCCtext)
                self.EMAILidentifierBCCtext = ''
            if self.EMAILinMultiModelFieldAttachments:
                self.EMAILinMultiModelFieldAttachments = False
                self.EMAILattachmentFilename.append(self.EMAILattachmentFilenameText)
                self.EMAILattachmentFilenameText = ''
        else:
            if self.EMAILin:
                self.EMAILsource.append(self.EMAILsourceText)
                self.EMAILidentifierFROM.append(self.EMAILidentifierFROMtext)
                self.EMAILidentifiersTO.append(self.EMAILidentifierTO[:])
                self.EMAILidentifiersCC.append(self.EMAILidentifierCC[:])
                self.EMAILidentifiersBCC.append(self.EMAILidentifierBCC[:])
                self.EMAILattachmentsFilename.append(self.EMAILattachmentFilename[:])
                bodyClean = self.__cleanText(self.EMAILbodyText)                
                self.EMAILbody.append(bodyClean)
                self.EMAILsubject.append(self.EMAILsubjectText)
                self.EMAILtimeStamp.append(self.EMAILtimeStampText)
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
                self.EMAILinPartyTO = False
                self.EMAILinPartyCC = False
                self.EMAILinPartyBCC = False
                self.EMAILinMultiModelFieldTO = False
                self.EMAILinMultiModelFieldCC = False
                self.EMAILinMultiModelFieldBCC = False


    def __endElementModelU_ACCOUNT(self):
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

#---    in UFED the field Source represents the application
#       and the Whatsapp value is not WhatsAppiMessage but
#       just Whatsapp! 
#                
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

    def __endElementModelWEB_PAGE(self):
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

    def __endElementFieldCALL(self):
        if self.CALLinSource:
            self.CALLinSource = False
        if self.CALLinDirection:
            self.CALLinDirection = False
        if self.CALLinType:
            self.CALLinType = False
        if self.CALLinOutcome:
            self.CALLinOutcome = False
        if self.CALLinTimeStamp:
            self.CALLinTimeStamp = False        
        if self.CALLinDuration:
            self.CALLinDuration = False
        
        if self.CALLinIdentifier:
            self.CALLinIdentifier = False         
        if self.CALLinRole:
            self.CALLinRole = False
        if self.CALLinName:
            self.CALLinName = False                                
        

    def __endElementFieldCONTACT(self):
        if self.CONTACTinName:
            self.CONTACTinName = False
        if self.CONTACTinPhoneNum:
            self.CONTACTinPhoneNum = False
    
    def __endElementFieldCHAT(self):
        if self.CHATinSource:
            self.CHATinSource = False
        if self.CHATinPartyIdentifier:
            self.CHATinPartyIdentifier = False
        if self.CHATinPartyName:
            self.CHATinPartyName = False
        if self.CHATinMsgIdentifierFrom:
            self.CHATinMsgIdentifierFrom = False
        if self.CHATinMsgNameFrom:
            self.CHATinMsgNameFrom = False
        if self.CHATinMsgIdentifierTo:
            self.CHATinMsgIdentifierTo = False
        if self.CHATinMsgNameTo:
            self.CHATinMsgNameTo = False
        if self.CHATinMsgBody:
            self.CHATinMsgBody = False
        if self.CHATinMsgOutcome:
            self.CHATinMsgOutcome = False
        if self.CHATinMsgTimeStamp:
            self.CHATinMsgTimeStamp = False
        if self.CHATinMsgAttachmentFilename:
            self.CHATinMsgAttachmentFilename = False
        if self.CHATinMsgAttachmentUrl:
            self.CHATinMsgAttachmentUrl = False
        
    def __endElementFieldEMAIL(self):
        if self.EMAILin:
            if self.EMAILinSource:
                self.EMAILinSource = False
            if self.EMAILinIdentifierFROM:
                self.EMAILinIdentifierFROM = False
            if self.EMAILinIdentifierTO:
                self.EMAILinIdentifierTO = False
            if self.EMAILinIdentifierCC:
                self.EMAILinIdentifierCC = False
            if self.EMAILinIdentifierBCC:
                self.EMAILinIdentifierBCC = False
            if self.EMAILinBody:
                self.EMAILinBody = False
            if self.EMAILinSubject:
                self.EMAILinSubject = False
            if self.EMAILinTimeStamp:
                self.EMAILinTimeStamp = False
            if self.EMAILinAttachmentFilename:
                self.EMAILinAttachmentFilename = False

    def __endElementFieldSMS(self):
        if self.SMSinSource:
            self.SMSinSource = False 
        if self.SMSinTimeStamp:
            self.SMSinTimeStamp = False
        if self.SMSinBody:
            self.SMSinBody = False
        if self.SMSinFolder:
            self.SMSinFolder = False
        if self.SMSinSmsc:
            self.SMSinSmsc = False

        if self.SMSinPartyRole:
            self.SMSinPartyRole = False
        if self.SMSinPartyIdentifier:
            self.SMSinPartyIdentifier = False         
        if self.SMSinPartyName:
            self.SMSinPartyName = False 
        

    def __endElementFieldU_ACCOUNT(self):        
        if self.U_ACCOUNTinSource:
                self.U_ACCOUNTinSource = False
        if self.U_ACCOUNTinName:
            self.U_ACCOUNTinName = False
        if self.U_ACCOUNTinUsername:
                self.U_ACCOUNTinUsername = False    

    def __endElementFieldCONTEXT(self):
        if self.CONTEXTinCaseInfo:
            if self.CONTEXTinExaminerNameValue:
                self.CONTEXTinExaminerNameValue = False

    def __endElementFieldWEB_PAGE(self):
        if self.WEB_PAGEinSource:
            self.WEB_PAGEinSource = False
        if self.WEB_PAGEinUrl:
            self.WEB_PAGEinUrl = False
        if self.WEB_PAGEinTitle:
            self.WEB_PAGEinTitle = False
        if self.WEB_PAGEinVisitCount:
            self.WEB_PAGEinVisitCount = False
        if self.WEB_PAGEinLastVisited:
            self.WEB_PAGEinLastVisited = False

    def __endElementValueCALL(self):
        if self.CALLinSourceValue:
            self.CALLinSourceValue = False
        if self.CALLinDirectionValue:
            self.CALLinDirectionValue = False
        if self.CALLinTypeValue:
            self.CALLinTypeValue = False
        if self.CALLinOutcomeValue:
            self.CALLinOutcomeValue = False
        if self.CALLinTimeStampValue:
            self.CALLinTimeStampValue = False        
        if self.CALLinDurationValue:
            self.CALLinDurationValue = False
        
        if self.CALLinIdentifierValue:
            self.CALLinIdentifierValue = False
        if self.CALLinRoleValue:
            self.CALLinRoleValue = False
        if self.CALLinNameValue:            
            self.CALLinNameValue = False                

    def __endElementValueCHAT(self):
        if self.CHATinSourceValue:
            self.CHATsource.append(self.CHATsourceText)
            self.CHATinSourceValue = False
            self.CHATsourceText = ''
        if self.CHATinPartyIdentifierValue:
            self.CHATinPartyIdentifierValue = False
        if self.CHATinPartyNameValue:
            self.CHATinPartyNameValue = False
        if self.CHATinMsgIdentifierFromValue:
            self.CHATinMsgIdentifierFromValue = False
        if self.CHATinMsgIdentifierToValue:
            self.CHATinMsgIdentifierToValue = False
        if self.CHATinMsgNameFromValue:                
            self.CHATinMsgNameFromValue = False
        if self.CHATinMsgNameToValue:
            self.CHATinMsgNameToValue = False
        if self.CHATinMsgBodyValue:
            self.CHATinMsgBodyValue = False
        if self.CHATinMsgOutcomeValue:
            self.CHATinMsgOutcomeValue = False
        if self.CHATinMsgTimeStampValue:
            self.CHATinMsgTimeStampValue = False
        if self.CHATinMsgAttachmentFilenameValue:
            self.CHATinMsgAttachmentFilenameValue = False
        if self.CHATinMsgAttachmentUrlValue:
            self.CHATinMsgAttachmentUrlValue = False

    def __endElementValueCONTACT(self):
        if self.CONTACTinNameValue:
            self.CONTACTinNameValue = False
        if self.CONTACTinPhoneNumValue:            
            if self.CONTACTphoneNumText == '':
                pass
            else:
                phonePattern = '([0-9]+)'
                phoneNum = self.CONTACTphoneNumText.replace(' ', '')
                phoneNum = phoneNum.replace('+', '00')
                phoneMatch = re.search(phonePattern, phoneNum) 
                if phoneMatch:
                    phoneNum = phoneMatch.group()
                    self.CONTACTphoneNum.append(phoneNum) 
                self.CONTACTphoneNumText = ''
            self.CONTACTinPhoneNumValue = False

    def __endElementValueEMAIL(self):
        if self.EMAILinSourceValue:
            self.EMAILinSourceValue = False
        if self.EMAILinIdentifierFROMvalue:
           self.EMAILinIdentifierFROMvalue = False
        if self.EMAILinIdentifierTOvalue:
           self.EMAILinIdentifierTOvalue = False
        if self.EMAILinIdentifierCCvalue:
           self.EMAILinIdentifierCCvalue = False
        if self.EMAILinIdentifierBCCvalue:
           self.EMAILinIdentifierBCCvalue = False
        if self.EMAILinBodyValue:
            self.EMAILinBodyValue = False
        if self.EMAILinSubjectValue:
            self.EMAILinSubjectValue = False
        if self.EMAILinTimeStampValue:
            self.EMAILinTimeStampValue = False
        if self.EMAILinAttachmentFilenameValue:
            self.EMAILinAttachmentFilenameValue = False

    def __endElementValueSMS(self):
        if self.SMSinSourceValue:
            self.SMSinSourceValue = False 
        if self.SMSinTimeStampValue:
            self.SMSinTimeStampValue = False
        if self.SMSinBodyValue:
            self.SMSinBodyValue = False
        if self.SMSinFolderValue:
            self.SMSinFolderValue = False
        if self.SMSinSmscValue:
            self.SMSinSmscValue = False

        if self.SMSinPartyIdentifierValue:
            self.SMSinPartyIdentifierValue = False
        if self.SMSinPartyRoleValue:            
            self.SMSinPartyRoleValue = False                
        if self.SMSinPartyNameValue:
            self.SMSinPartyNameValue = False 

    def __endElementValueU_ACCOUNT(self):
        if self.U_ACCOUNTinSourceValue:
            self.U_ACCOUNTinSourceValue = False

        if self.U_ACCOUNTinNameValue:
            self.U_ACCOUNTinNameValue = False
            
        if self.U_ACCOUNTinUsernameValue:
            self.U_ACCOUNTinUsernameValue = False


    def __endElementValueWEB_PAGE(self):
        if self.WEB_PAGEinSourceValue:
            self.WEB_PAGEinSourceValue = False 
        if self.WEB_PAGEinUrlValue:
            self.WEB_PAGEinUrlValue = False 
        if self.WEB_PAGEinTitleValue:
            self.WEB_PAGEinTitleValue = False 
        if self.WEB_PAGEinVisitCountValue:
            self.WEB_PAGEinVisitCountValue = False 
        if self.WEB_PAGEinLastVisitedValue:
            self.WEB_PAGEinLastVisitedValue = False 

    def __endElementTimeStampTAGGED_FILE(self):
        if self.TAGGED_FILESinAccessInfoCreate:
            self.FILEtimeCreate[self.FILEidx] = self.TAGGED_FILESCreateText
            self.TAGGED_FILESCreateText = ''
            self.TAGGED_FILESinAccessInfoCreate = False
        if self.TAGGED_FILESinAccessInfoModify:
            self.FILEtimeModify[self.FILEidx] = self.TAGGED_FILESModifyText
            self.TAGGED_FILESModifyText = ''
            self.TAGGED_FILESinAccessInfoModify = False
        if self.TAGGED_FILESinAccessInfoAccess:
            self.FILEtimeAccess[self.FILEidx] = self.TAGGED_FILESAccessText
            self.TAGGED_FILESAccessText = ''
            self.TAGGED_FILESinAccessInfoAccess = False

    def __endElementItemTAGGED_FILE(self):
        if self.TAGGED_FILESinMD5:
            self.FILEmd5.append(self.TAGGED_FILESmd5Text)
            self.TAGGED_FILESmd5Text = ''
            self.TAGGED_FILESinMD5 = False
        if self.TAGGED_FILESinTags:
            self.FILEtags.append(self.TAGGED_FILEStagsText)
            self.TAGGED_FILEStagsText = ''
            self.TAGGED_FILESinTags = False
        if self.TAGGED_FILESinLocalPath:
            self.FILElocalPath.append(self.TAGGED_FILESbaseLocalPath + 
                self.TAGGED_FILESlocalPathText)
            self.TAGGED_FILESlocalPathText = ''
            self.TAGGED_FILESinLocalPath = False
        if self.TAGGED_FILESinInodeNumber:
            self.FILEiNodeNumber[self.FILEidx] = self.TAGGED_FILESiNodeNumberText
            self.TAGGED_FILESiNodeNumberText = ''
            self.TAGGED_FILESinInodeNumber = False
        if self.TAGGED_FILESinInodeTimeModify:
            self.FILEiNodeTimeModify[self.FILEidx] = self.TAGGED_FILESiNodeTimeModifyText
            self.TAGGED_FILESiNodeTimeModifyText = ''
            self.TAGGED_FILESinInodeTimeModify = False
        if self.TAGGED_FILESinOwnerGID:
            self.FILEownerGID[self.FILEidx] = self.TAGGED_FILESownerGIDText
            self.TAGGED_FILESownerGIDText = ''
            self.TAGGED_FILESinOwnerGID = False
        if self.TAGGED_FILESinOwnerUID:
            self.FILEownerUID[self.FILEidx] = self.TAGGED_FILESownerUIDText
            self.TAGGED_FILESownerUIDText = ''
            self.TAGGED_FILESinOwnerUID = False
    
    def __endElementItemCONTEXT(self):
        
        if self.CONTEXTinDeviceExtractionStart:
            self.CONTEXTinDeviceExtractionStart = False
        if self.CONTEXTinDeviceExtractionEnd:
            self.CONTEXTinDeviceExtractionEnd = False

        if self.CONTEXTinUfedVersionValue:
            self.CONTEXTinUfedVersionValue = False
        if self.CONTEXTinDeviceCreationTimeValue:
            self.CONTEXTinDeviceCreationTimeValue = False
        if self.CONTEXTinDeviceBluetoothAddressValue:
            self.CONTEXTinDeviceBluetoothAddressValue = False
        if self.CONTEXTinDeviceIdValue:
            self.CONTEXTinDeviceIdValue = False
        if self.CONTEXTinDevicePhoneModelValue:
            self.CONTEXTinDevicePhoneModelValue = False
        if self.CONTEXTinDeviceOsTypeValue:
            self.CONTEXTinDeviceOsTypeValue = False
        if self.CONTEXTinDeviceOsVersionValue:
            self.CONTEXTinDeviceOsVersionValue = False
        if self.CONTEXTinDevicePhoneVendorValue:
            self.CONTEXTinDevicePhoneVendorValue = False
        if self.CONTEXTinDeviceMacAddressValue:
            self.CONTEXTinDeviceMacAddressValue = False
        if self.CONTEXTinDeviceIccidValue:
            self.CONTEXTinDeviceIccidValue = False
        if self.CONTEXTinDeviceMsisdnValue:
            self.CONTEXTinDeviceMsisdnValue = False
        if self.CONTEXTinDeviceImsiValue:
            self.CONTEXTinDeviceImsiValue = False
        if self.CONTEXTinDeviceImeiValue:
            self.CONTEXTinDeviceImeiValue = False
        
        if self.CONTEXTinImageMetadataHashValueSHA:
            self.CONTEXTinImageMetadataHashValueSHA = False
        if self.CONTEXTinImageMetadataHashValueMD5:
            self.CONTEXTinImageMetadataHashValueMD5 = False


#---    It captures each Element when it is closed
#            
    def endElement(self, name):
        self.lineXML +=1

        if name == 'model':
            self.__endElementModelCALL()
            self.__endElementModelCONTACT()
            self.__endElementModelCHAT()
            self.__endElementModelEMAIL()
            self.__endElementModelSMS()
            self.__endElementModelU_ACCOUNT()
            self.__endElementModelWEB_PAGE()            

        if (name == 'modelField' or name == 'multiModelField'):
            if self.CHATinMsgFrom:
                self.CHATinMsgFrom = False
            if self.CHATinMsgTo:
                self.CHATinMsgTo = False
            
            if self.SMSinParty:
                self.SMSinParty = False
            
#---    this works when a <multiModelField> element is followed by 
#       an <empty> element
#                
            if self.EMAILinModelFieldFROM:
                self.EMAILinModelFieldFROM = False
            if self.EMAILinMultiModelFieldTO:
                self.EMAILinMultiModelFieldTO = False
            if self.EMAILinMultiModelFieldCC:
                self.EMAILinMultiModelFieldCC = False
            if self.EMAILinMultiModelFieldBCC:
                self.EMAILinMultiModelFieldBCC = False
            if self.EMAILinMultiModelFieldAttachments:
                self.EMAILinMultiModelFieldAttachments = False

        if name == 'field':        
            self.__endElementFieldCALL()
            self.__endElementFieldCONTACT()
            self.__endElementFieldCHAT()
            self.__endElementFieldEMAIL()
            self.__endElementFieldSMS()
            self.__endElementFieldU_ACCOUNT()
            self.__endElementFieldWEB_PAGE()
            self.__endElementFieldCONTEXT()

        if name == 'value':
            self.__endElementValueCALL()
            self.__endElementValueCHAT()
            self.__endElementValueCONTACT()
            self.__endElementValueEMAIL()
            self.__endElementValueSMS()
            self.__endElementValueU_ACCOUNT()
            self.__endElementValueWEB_PAGE()

        if name == 'timestamp':
            self.__endElementTimeStampTAGGED_FILE()
            
        if name == 'nodeInfo':
           if self.EXTRA_INFOin:
                self.EXTRA_INFOnodeInfoin = False  
            
        if name == 'extraInfo':
            self.EXTRA_INFOin = False

        if name =='taggedFiles':
            self.TAGGED_FILESin = False

        if name =='item':
            self.__endElementItemTAGGED_FILE()
            self.__endElementItemCONTEXT()

        if name == "metadata":
            if self.CONTEXTinAdditionalFields:
                self.CONTEXTinAdditionalFields = False
                self.CONTEXTinUfedVersionValue = False
                self.CONTEXTinDeviceCreationTimeValue = False
            if self.CONTEXTinDeviceInfo:                                
                self.CONTEXTinDeviceInfo = False
            if self.CONTEXTinImageMetadataHash:
                self.CONTEXTinImageMetadata = False

        if name == 'caseInformation':
            self.CONTEXTinCaseInfo = False
            self.CONTEXTinExaminerNameValue = False

        if name == 'image':
            if self.CONTEXTinImages:
                self.CONTEXTinImage = False                
                self.CONTEXTimageMetadataHashSHA.append(self.CONTEXTimageMetadataHashTextSHA)
                self.CONTEXTimageMetadataHashMD5.append(self.CONTEXTimageMetadataHashTextMD5)
                self.CONTEXTimageMetadataHashText = ''

        if name == 'images':
            self.CONTEXTinImages = False

if __name__ == '__main__':

#---    debug: ctime processing
#
    tic=timeit.default_timer()

    parserArgs = argparse.ArgumentParser(description='Parser to convert XML Report from UFED PA into CASE-JSON-LD standard.')

#---    report XML exported by UFED PA, to be converted/parsed into CASE
#
    parserArgs.add_argument('-r', '--report', dest='inFileXML', required=True, 
                    help='The UFED XML report from which to extract digital traces and convert them into CASE; it supports UFED PA version from 7.24 to 7.37')

    parserArgs.add_argument('-o', '--output', dest='output_CASE_JSON', required=True, help='File CASE-JSON-LD to be generated')

    parserArgs.add_argument('-d', '--debug', dest='output_DEBUG', required=False, help='File for writing debug')

    args = parserArgs.parse_args()


    if args.output_CASE_JSON is None:
        path, name = os.path.split(args.inFileXML[0:-3] + 'JSON')
        args.output_CASE_JSON = name

    print('*--- Input paramaters start \n')
    print('\tFile XML:\t\t' + args.inFileXML)

    head, tail = os.path.split(args.output_CASE_JSON)
    print('\tFile Output:\t\t' + args.output_CASE_JSON)

    if args.output_DEBUG is None:
        pass
    else:
        print('\tFile Debug:\t\t' + args.output_DEBUG)

    print('\n*--- Input paramaters end')
    print('\n\n*** Start processing\n')

#---    baseLocalPath is for setting the fileLocalPath property of FileFacet 
#       Observable. 
#    
    baseLocalPath = ''
    gadget = UFEDgadget(args.inFileXML, args.output_CASE_JSON, baseLocalPath)    
    
    Handler = gadget.processXmlReport()

    if args.output_DEBUG is None:
        pass
    else: 
        import UFEDdebug
        debug = UFEDdebug.ParserDebug(args.output_DEBUG)
        debug.writeDebugEXTRA_INFO(Handler)     
        debug.writeDebugCALL(Handler)              
        debug.writeDebugCHAT(Handler)     
        debug.writeDebugCONTACT(Handler)  
        debug.writeDebugCONTEXT(Handler)       
        debug.writeDebugEMAIL(Handler)         
        debug.writeDebugFILES(Handler)     
        debug.writeDebugSMS(Handler)     
        debug.writeDebugU_ACCOUNT(Handler)     
        debug.writeDebugWEB_PAGE(Handler)     
        debug.closeDebug() 
            

    toc=timeit.default_timer()
    elapsedTime = round(toc - tic, 2)
    (ss, ms) = divmod(elapsedTime, 1)
    elapsedMm = str(int(ss) // 60)
    elapsedSs = str(int(ss) % 60)
    elapsedMs = str(round(ms, 2))[2:]
    elapsedTime = elapsedMm + ' min. ' +  elapsedSs + ' sec. and ' + \
        elapsedMs + ' hundredths'
    print(Handler.C_green + '\n*** End processing, elapsed time: ' + elapsedTime + \
        '\n\n' + Handler.C_end)

# else:
# #---    
#     xmlFile = '../CASE-dataset.xml.reports/UFED/ANDROID/19_UFED_ANDROID_CROSSOVER.xml'
#     jsonFile = './_19gadget.json'   
#     gadget = UFEDgadget(xmlFile, jsonFile)
#     gadget.processXmlReport()
#     print("end XML processing, created " + jsonFile) 

