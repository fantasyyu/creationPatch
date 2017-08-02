#!/usr/bin/env
# -*- coding: UTF-8 -*-


from cgi import parse_header
import sys, urllib
import cgi, cgitb 
import json
import os
import logging
import email
import sys, json
import shutil, glob, msilib
import logging, datetime,stat
import xml.dom.minidom
import xml
import xml.etree.ElementTree as ET
from email.mime.text import MIMEText
import smtplib, socket

#cgitb.enable()
#form = cgi.FieldStorage()

#Function: Get the msi productcode
def GetProductCode(srcMsi):
    logging.info("start to get ProductCode from: "+str(srcMsi))
    msi_DB=msilib.OpenDatabase(srcMsi,msilib.MSIDBOPEN_READONLY)
    view=msi_DB.OpenView("SELECT Value FROM Property WHERE Property='ProductCode'")
    view.Execute(None)
    record=view.Fetch()
    productCode=record.GetString(1)
    return productCode

def GetLanguagePackCode(srcMsi):
    try:
        logging.info("start to get GetISLanguagePack from: "+str(srcMsi))
        msi_DB=msilib.OpenDatabase(srcMsi,msilib.MSIDBOPEN_READONLY)
        view=msi_DB.OpenView("SELECT Value FROM Property WHERE Property='SETUP_ISLANGUAGEPACK'")
        view.Execute(None)
        record=view.Fetch()
        ISLanguagePack=record.GetString(1)

        view=msi_DB.OpenView("SELECT Value FROM Property WHERE Property='ProductLanguage'")
        view.Execute(None)
        record=view.Fetch()
        LanguagePackCode = record.GetString(1)
        return ISLanguagePack,LanguagePackCode
    except Exception as E:
        logger.info ("Exception in GetLanguagePackCode is:" + str(E))
        return "false", "false"

#Function: Get the msi productName
def GetProductName(srcMsi):
    logging.info("start to get ProductName from: "+str(srcMsi))
    msi_DB=msilib.OpenDatabase(srcMsi,msilib.MSIDBOPEN_READONLY)
    view=msi_DB.OpenView("SELECT Value FROM Property WHERE Property='ProductName'")
    view.Execute(None)
    record=view.Fetch()
    productName=record.GetString(1)
    return productName

#Function: Get the msi productVersion
def GetProductVersion(srcMsi):
    logging.info("start to get ProductVersion from: "+str(srcMsi))
    msi_DB=msilib.OpenDatabase(srcMsi,msilib.MSIDBOPEN_READONLY)
    view=msi_DB.OpenView("SELECT Value FROM Property WHERE Property='ProductVersion'")
    view.Execute(None)
    record=view.Fetch()
    productVersion=record.GetString(1)
    return productVersion

def GetFeatureParent(srcMsi):
    logging.info("start to get FeatureParent from: "+str(srcMsi))
    msiDB=msilib.OpenDatabase(srcMsi,msilib.MSIDBOPEN_TRANSACT)        
    view = msiDB.OpenView("SELECT Feature FROM Feature WHERE Feature_Parent=''")  
    view.Execute(None)
    record=view.Fetch()
    FeatureName=record.GetString(1)

    return FeatureName

def SetHotfixUpgradeMSIProductVersion(srcMsi, baseVersion):
    logging.info("start to SetHotfixUpgradeMSIProductVersion from: "+str(srcMsi)+ "baseVersion: "+str(baseVersion))
    msiDB=msilib.OpenDatabase(srcMsi,msilib.MSIDBOPEN_TRANSACT)
    version = baseVersion
    view=msiDB.OpenView("UPDATE Property SET Value='%s' WHERE Property='ProductVersion'"%(version))
    view.Execute(None)
    view.Close()
    msiDB.Commit()


#Function: Add the ARP Component for Patch 
def AddSPComponent(msiSrcPath,patch_level):
    try:
        
        FeatureName=GetFeatureParent(msiSrcPath)
        logger.info("FeatureName :"+str(FeatureName))
        componUUID=msilib.gen_uuid()
        patchName=str(patchType)+str(patch_level)
        logger.info("patchName :"+str(patchName))
        sp_product_name = '[ProductName] '+patchName
        logger.info("sp_product_name :"+str(sp_product_name))
        patch_reg_key = 'Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\'+sp_product_name
        MsiProductCode = GetProductCode(msiSrcPath)
        msiDB = msilib.OpenDatabase(msiSrcPath,msilib.MSIDBOPEN_TRANSACT)
        #add component for SP
        msilib.add_data(msiDB, 'Component', [(patchName+'_RegistryUninstall',componUUID,'INSTALLDIR',260,'PATCH',patchName+'_UNINSTALLSTRING')])
        msilib.add_data(msiDB, 'FeatureComponents', [(FeatureName, patchName+'_RegistryUninstall')])
        msilib.add_data(msiDB, 'Registry', [(patchName+'_UNINSTALLSTRING', 2, patch_reg_key, 'UninstallString', 'Msiexec.exe /uninstall '+str(PatchUUID)+' /package [ProductCode] /qb', patchName+'_RegistryUninstall'),
                                            (patchName+'_SHELL_ENTRY', 2, patch_reg_key, '*', '', patchName+'_RegistryUninstall'),
                                            (patchName+'_DISPLAYICON', 2, patch_reg_key, 'DisplayIcon', '[SetupFolder]SetupRes\\amar.ico', patchName+'_RegistryUninstall'),
                                            (patchName+'_DISPLAYNAME', 2, patch_reg_key, 'DisplayName', '[ProductName] '+patchName+'-64bit ', patchName+'_RegistryUninstall'),
                                            (patchName+'_DISPLAYVERSION', 2, patch_reg_key, 'DisplayVersion', '[ProductVersion]', patchName+'_RegistryUninstall'),
                                            (patchName+'_NOMODIFY', 2, patch_reg_key, 'NoModify', '#1', patchName+'_RegistryUninstall'),
                                            (patchName+'_NOREMOVE', 2, patch_reg_key, 'NoRemove', '#0', patchName+'_RegistryUninstall'),
                                            (patchName+'_NOREPAIR', 2, patch_reg_key, 'NoRepair', '#1', patchName+'_RegistryUninstall'),
                                            (patchName+'_PARENTDISPLAYNAME', 2, patch_reg_key, 'ParentDisplayName', '[ProductName]', patchName+'_RegistryUninstall'),
                                            (patchName+'_PARENTKEYNAME', 2, patch_reg_key, 'ParentKeyName', '[ProductName]', patchName+'_RegistryUninstall'),
                                            (patchName+'_INSTALLDATE', 2, patch_reg_key, 'InstallDate', '[Date]', patchName+'_RegistryUninstall'),
                                            (patchName+'_RELEASETYPE', 2, patch_reg_key, 'ReleaseType', 'Product Update', patchName+'_RegistryUninstall'),
                                            (patchName+'_PUBLISHER', 2, patch_reg_key, 'Publisher', '[Manufacturer]', patchName+'_RegistryUninstall')])
        msiDB.Commit()
    except Exception as E:
        logger.info ("Exception in AddSPComponent is:" + str(E))

#Function: Generate the Patch WXS
def GeneratePatchWXS(msiList):
    try:
        logger.info ("start to generate WXS")
        doc = xml.dom.minidom.Document()
        WixRoot = doc.createElement('Wix')
        WixRoot.setAttribute('xmlns','http://schemas.microsoft.com/wix/2006/wi')
        doc.appendChild(WixRoot)

        baseMsiPath = msiList['MsiGroup0']['baseImagePath']
    
        productName=GetProductName(baseMsiPath)
    
        PatchCreation = doc.createElement('PatchCreation')

        PatchCreation.setAttribute('Id',PatchUUID)#packageId
        PatchCreation.setAttribute('Codepage','1252')
        PatchCreation.setAttribute('CleanWorkingFolder','yes')
        PatchCreation.setAttribute('WholeFilesOnly','yes')
        PatchCreation.setAttribute('AllowMajorVersionMismatches','no')
        PatchCreation.setAttribute('AllowProductCodeMismatches','no')

        PatchInformation = doc.createElement('PatchInformation')
        PatchInformation.setAttribute('Description',productName + ' '+patchType + SPversion)#description
        PatchInformation.setAttribute('Comments',productName + ' '+patchType + SPversion)#comments
        PatchInformation.setAttribute('Manufacturer','Autodesk')
        PatchCreation.appendChild(PatchInformation)

        PatchMetadata = doc.createElement('PatchMetadata')
        PatchMetadata.setAttribute('AllowRemoval','yes')
        PatchMetadata.setAttribute('Description',productName + ' '+patchType + SPversion)#Description
        PatchMetadata.setAttribute('ManufacturerName','Autodesk')
        PatchMetadata.setAttribute('TargetProductName',productName)#TargetProductName
        PatchMetadata.setAttribute('MoreInfoURL','http://www.autodesk.com/')
        PatchMetadata.setAttribute('Classification',patchType)
        PatchMetadata.setAttribute('DisplayName',productName + ' '+patchType + SPversion)#DisplayName
        PatchCreation.appendChild(PatchMetadata)

        Family = doc.createElement('Family')
        strFamilyName = MainProductAliasName
        if len(MainProductAliasName) > 8:
            strFamilyName = MainProductAliasName[:8]
        Family.setAttribute('Name',strFamilyName)#use product name in setup.ini to be name, ex:DFM_SP
        Family.setAttribute('SequenceStart','15000')
        PatchCreation.appendChild(Family)

        for tmpMsiGroup in msiList:
            (IS_LP,LP_Code)=GetLanguagePackCode(msiList[tmpMsiGroup]['baseImagePath'])
            logger.info("IS_LP is: "+IS_LP+"\t LP_Code is: "+LP_Code)

            if IS_LP == 'false' or LP_Code == 'false':
                strLP = 'Core'

            if IS_LP == '0':
                strLP = 'Core'
            else:
                if LP_Code == '1033':
                    strLP = 'EN'
                elif LP_Code == '1031':
                    strLP = 'DE'
                elif LP_Code == '1034':
                    strLP = 'ES'
                elif LP_Code == '1036':
                    strLP = 'FR'
                elif LP_Code == '1040':
                    strLP = 'IT'
                elif LP_Code == '1041':
                    strLP = 'JP'
                elif LP_Code == '1042':
                    strLP = 'KO'
                elif LP_Code == '2070':
                    strLP = 'PT'
                elif LP_Code == '2052':
                    strLP = 'CN'
                elif LP_Code == '1028':
                    strLP = 'TW'
            UpgradeImage = doc.createElement('UpgradeImage')
            UpgradeImage.setAttribute('Id', strLP+'_upgrade')
            UpgradeImage.setAttribute('SourceFile',msiList[tmpMsiGroup]['upgradeImagePath'])

            TargetImage = doc.createElement('TargetImage')
            TargetImage.setAttribute('Id', strLP+'_target')
            TargetImage.setAttribute('SourceFile',msiList[tmpMsiGroup]['baseImagePath'])
            TargetImage.setAttribute('Order','0')
            TargetImage.setAttribute('IgnoreMissingFiles','yes')
            TargetImage.setAttribute('Validation','0x00000922')
            Family.appendChild(UpgradeImage)
            UpgradeImage.appendChild(TargetImage)

            upgradeMsiPath = msiList[tmpMsiGroup]['upgradeImagePath']
            m_productVersion=GetProductVersion(upgradeMsiPath).split('.')
            PatchSequence = doc.createElement('PatchSequence')

            PatchSequence.setAttribute('PatchFamily',strFamilyName+'_'+strLP)
            PatchSequence.setAttribute('TargetImage',strLP+'_target')
            PatchSequence.setAttribute('Sequence','%s.%s.0.0' % (m_productVersion[0],m_productVersion[1]))
            if patchType == 'ServicePack':
                PatchSequence.setAttribute('Supersede','yes')
            else:
                PatchSequence.setAttribute('Supersede','no')
            PatchCreation.appendChild(PatchSequence)

        PatchProperty = doc.createElement('PatchProperty')
        PatchProperty.setAttribute('Name','MinimumRequiredMsiVersion')
        PatchProperty.setAttribute('Value','300')
        PatchCreation.appendChild(PatchProperty)
    
        WixRoot.appendChild(PatchCreation)

        xml_str = doc.toprettyxml(indent="  ")
        if os.path.exists(workspacePatchPath+"patch\\"):
            shutil.rmtree(workspacePatchPath+"patch\\", onerror=on_rm_error)
        os.makedirs(workspacePatchPath+"patch\\")    
        logger.info ("wxs file: "+workspacePatchPath+"patch\\"+MainProductAliasName+"_patch.wxs")
        with open(workspacePatchPath+"patch\\"+MainProductAliasName+"_patch.wxs", "w") as f:
            f.write(xml_str)
    except Exception as Exce:
        logger.info("Error in GeneratePatchWXS is: "+str(Exce))

def GetFileParentDir(rootdir, srcFileList):
    try:
        ParentDirList=[]
        for parent,dirnames,filenames in os.walk(rootdir):    
            for file in srcFileList:
                if file in filenames:
                    ParentDirList.append(str(parent)+"\\"+file)
        return ParentDirList
    except Exception as Except:
        logging.info("Error in GetFileParentDir: "+str(Except))

#Function: When changedfilelist is not empty, replace the files from Upgrade image into Last
def ReplaceFiles(ChangedFileList,UpgradeImageDir,LastImageDir):
    try:
        logging.info("start to Replace file")
        rootdir=UpgradeImageDir
        FileList=ChangedFileList.split('\n')

        FileParentDirList=GetFileParentDir(rootdir,FileList)
        logging.info("FileParentDirList: "+str(FileParentDirList))
        for FileDir in FileParentDirList:
            srcDir=str(FileDir).replace("\\\\","\\")
            destDir=str(srcDir).replace("Upgrade","Last")
            logger.info ("copy file from: "+srcDir + " to: "+destDir)
            shutil.copy2(srcDir,destDir)
    except Exception as Excep:
        logging.info("Error in replace: "+str(Excep))

#Function: Send email to user
def send_mail(content,bSuccess):
    sender='jian.yu@autodesk.com'
    mailto_list=[m_Email]
    if bSuccess == True:
        msg = MIMEText("Please get your patch from "+content,_subtype='plain')
        subject = "Your Patch is ready"
    else:
        msg = MIMEText("Sorry, your patch failed.\r\n The problem is: "+content,_subtype='plain')
        subject = "Your patch failed"
    try:
        logger.info("mail list is: "+str(mailto_list))
        msg['From'] = sender
        msg['To'] = ','.join(mailto_list)
        msg['Subject'] = subject
        text = msg.as_string()
        s = smtplib.SMTP('connect.autodesk.com')
        s.sendmail(sender, mailto_list, text)
        s.quit()
        return True
    except Exception as e:
        logger.info ("send_mail"+str(e))
        return False

#Function: Change the readonly files property
def on_rm_error( func, path, exc_info):
    # path contains the path of the file that couldn't be removed
    # let's just assume that it's read-only and unlink it.
    os.chmod( path, stat.S_IWRITE )
    os.unlink( path )

#Function: Create Patch
def CreatePatchMain(msiList):
	try:
		SP_OUTPATH = workspacePatchPath+"\\patch\\"
		ipaddress = socket.gethostbyname(socket.gethostname())
		os.system("\"C:\\Program Files (x86)\\WiX Toolset v3.10\\bin\\candle.exe\" -nologo -wx " + workspacePatchPath+"patch\\"+MainProductAliasName+"_patch.wxs" + " -out "+workspacePatchPath+"patch\\"+MainProductAliasName+"_patch.wixobj")
		os.system("\"C:\\Program Files (x86)\\WiX Toolset v3.10\\bin\\light.exe\" -nologo " + workspacePatchPath+"patch\\"+MainProductAliasName+"_patch.wixobj" +" -out " + workspacePatchPath+"patch\\"+MainProductAliasName+"_patch.pcp")
		os.system("\"C:\\Program Files (x86)\\Microsoft SDKs\\Windows\\v7.0A\\Bin\\msimsp.exe\" -s "+ workspacePatchPath+"patch\\"+MainProductAliasName+"_patch.pcp"+ " -p "+ workspacePatchPath+"patch\\"+MainProductAliasName+"_"+patchType+SPversion+"_patch.msp"+" -lp "+ workspacePatchPath+"patch\\"+MainProductAliasName+"_patch.log")
		if os.path.exists(workspacePatchPath+"patch\\"+MainProductAliasName+"_"+patchType+SPversion+"_patch.msp"):
			os.system("\"E:\\SPworkspace\\codeSign\\signtool.exe\" sign /f E:\\SPworkspace\\codeSign\\Codesign.pfx /p maggie /v /t http://timestamp.verisign.com/scripts/timstamp.dll " + workspacePatchPath+"patch\\"+MainProductAliasName+"_"+patchType+SPversion+"_patch.msp")
			if os.path.exists(sharedFolder+str(MainBaseMsiProductCode)+"\\"):
				logger.infor("The %s path exist, remove it" %(str(MainBaseMsiProductCode)))
				shutil.rmtree(sharedFolder+str(MainBaseMsiProductCode)+"\\")
			shutil.copytree(workspacePatchPath+"patch\\",sharedFolder+str(MainBaseMsiProductCode)+"\\"+str(MainUpgradeMsiProductVersion)+"\\")
			send_mail("\\\\"+str(ipaddress)+"\\shared\\patch\\"+str(MainBaseMsiProductCode)+"\\"+str(MainUpgradeMsiProductVersion)+"\\",True)
	except Exception as ex:
		logger.info("Exception in CreatePatchMain is: "+ str(ex))

def CheckImageExist(srcMsiGroup):
    try:
        strBaseImageDir = MsiGroupList[srcMsiGroup]['baseImageDir']
        strUpgradeImageDir = MsiGroupList[srcMsiGroup]['upgradeImageDir']

        if os.path.exists(strBaseImageDir) == False:
            logger.info(srcMsiGroup+": The Base Image path is not vaild, please check it.")
            send_mail(MsiGroupList[srcMsiGroup]['baseImageDir']+": The Base Image path is not vaild, please check it.",False)
            exit()

        if os.path.exists(strUpgradeImageDir) == False:
            logger.info(srcMsiGroup+": The Upgrade Image path is not vaild, please check it")
            send_mail(MsiGroupList[srcMsiGroup]['upgradeImageDir']+": The Upgrade Image path is not valid, please check it",False)
            exit()

        BaseMsifile = glob.glob(strBaseImageDir+"\\*.msi")
        UpgradeMsiFile = glob.glob(strUpgradeImageDir+"\\*.msi")
        logger.info ("BaseMsifile is: "+str(BaseMsifile))
        logger.info ("UpgradeMsiFile is: "+str(UpgradeMsiFile))
        if BaseMsifile == []:
            logger.info(srcMsiGroup+": The Base Image directory doesn't include .msi file, please check it agagin.")
            send_mail(MsiGroupList[srcMsiGroup]['baseImageDir']+": The Base Image directory doesn't include .msi file, please check it agagin.",False)
            exit()
        if UpgradeMsiFile == []:
            logger.info(srcMsiGroup+": The Upgrade Image directory doesn't include .msi file, please check it agagin.")
            send_mail(MsiGroupList[srcMsiGroup]['upgradeImageDir']+": The Upgrade Image directory doesn't include .msi file, please check it agagin.",False)
            exit()
 
        BaseMsiProductCode = GetProductCode(BaseMsifile[0])
        UpgradeMsiProductCode = GetProductCode(UpgradeMsiFile[0])
        logger.info (srcMsiGroup+": BaseMsiProductCode is: "+str(BaseMsiProductCode))
        logger.info (srcMsiGroup+": UpgradeMsiProductCode is: "+str(UpgradeMsiProductCode))
        if BaseMsiProductCode != UpgradeMsiProductCode:
            logger.info(srcMsiGroup+": The Target MSI and Upgrade MSI ProductCode not same, please check it again.")
            send_mail(MsiGroupList[srcMsiGroup]['baseImageDir']+" And "+MsiGroupList[srcMsiGroup]['upgradeImageDir']+": The Target MSI and Upgrade MSI ProductCode not same, please check it again.",False)
            exit()
        print("Your patch has started to generate, please wait for email")
    except Exception as ex:
        logger.info("Exception in CheckImageExist is: "+ str(ex))

def PrepareImages(srcMsiGroup):
    try:
        tmpBaseImageDir = MsiGroupList[srcMsiGroup]['baseImageDir']
        tmpUpgradeImageDir = MsiGroupList[srcMsiGroup]['upgradeImageDir']
        tmpChangeFileList = MsiGroupList[srcMsiGroup]['changedFileList']

        if os.path.exists(workspaceBuildPath+srcMsiGroup+"_Base\\"):
            shutil.rmtree(workspaceBuildPath+srcMsiGroup+"_Base\\", onerror=on_rm_error)

        if os.path.exists(workspaceBuildPath+srcMsiGroup+"_Upgrade\\"):
            shutil.rmtree(workspaceBuildPath+srcMsiGroup+"_Upgrade\\", onerror=on_rm_error)

        shutil.copytree(tmpBaseImageDir,workspaceBuildPath+srcMsiGroup+"_Base\\")
        shutil.copytree(tmpUpgradeImageDir,workspaceBuildPath+srcMsiGroup+"_Upgrade\\")

        tmpBaseMsiFile = glob.glob(workspaceBuildPath+srcMsiGroup+"_Base\\*.msi")
        tmpProductAliasName = os.path.basename(tmpBaseMsiFile[0]).split('.',1)[0]
        logger.info ("tmpProductAliasName is: "+str(tmpProductAliasName))
        tmpMsiName = tmpProductAliasName+".msi"
        if os.path.exists(workspacePatchPath+srcMsiGroup+"_Base\\"):
            shutil.rmtree(workspacePatchPath+srcMsiGroup+"_Base\\", onerror=on_rm_error)

        if os.path.exists(workspacePatchPath+srcMsiGroup+"_Upgrade\\"):
            shutil.rmtree(workspacePatchPath+srcMsiGroup+"_Upgrade\\", onerror=on_rm_error)

        if os.path.exists(workspacePatchPath+srcMsiGroup+"_Last\\"):
            shutil.rmtree(workspacePatchPath+srcMsiGroup+"_Last\\", onerror=on_rm_error)

        os.system("msiexec.exe /a "+workspaceBuildPath+srcMsiGroup+"_Base\\"+tmpMsiName+" TARGETDIR="+workspacePatchPath+srcMsiGroup+"_Base\\"+" /qb")
        os.system("msiexec.exe /a "+workspaceBuildPath+srcMsiGroup+"_Upgrade\\"+tmpMsiName+" TARGETDIR="+workspacePatchPath+srcMsiGroup+"_Upgrade\\"+" /qb")

        if tmpChangeFileList == '':
            logger.info("There is not changed file for "+srcMsiGroup)            
            shutil.copytree(workspacePatchPath+srcMsiGroup+"_Upgrade\\",workspacePatchPath+srcMsiGroup+"_Last\\")
            AddSPComponent(workspacePatchPath+srcMsiGroup+"_Last\\"+tmpMsiName,SPversion)  
        else:
            logger.info("There are changed files for "+srcMsiGroup)
            shutil.copytree(workspacePatchPath+srcMsiGroup+"_Base\\",workspacePatchPath+srcMsiGroup+"_Last\\")
            ReplaceFiles(tmpChangeFileList,workspacePatchPath+srcMsiGroup+"_Upgrade\\",workspacePatchPath+srcMsiGroup+"_Last\\")
            AddSPComponent(workspacePatchPath+srcMsiGroup+"_Last\\"+tmpMsiName,SPversion)
            os.system("\"C:\\Program Files (x86)\\Microsoft SDKs\\Windows\\v7.0A\\Bin\\msifiler.exe\" -d " + workspacePatchPath+srcMsiGroup+"_Last\\"+tmpMsiName + " -h")
        if patchType != 'SerivcePack':
            SetHotfixUpgradeMSIProductVersion(workspacePatchPath+srcMsiGroup+"_Last\\"+tmpMsiName, GetProductVersion(workspacePatchPath+srcMsiGroup+"_Base\\"+tmpMsiName))
        return (workspacePatchPath+srcMsiGroup+"_Base\\"+tmpMsiName, workspacePatchPath+srcMsiGroup+"_Last\\"+tmpMsiName) 
    except Exception as exc:
        logger.info("Error in PrepareImages is: "+str(exc))

now = datetime.datetime.now()
strLog=str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)+str(now.second)

LOG_FILENAME = "E:\\patchlog\\"+strLog+"log.txt"
logger = logging.getLogger()
handler = logging.FileHandler(LOG_FILENAME)
logger.addHandler(handler)
logger.setLevel(logging.NOTSET)
try:
    myjson = json.load(sys.stdin)
    logger.info("start to log the patch creation")

    #with open("C:\\Users\\yujadmin\\Desktop\\myconfigFile-SJM.json") as json_data:
        #myjson = json.load(json_data)
    logger.info("get json: "+str(myjson))
    print ('Content-Type: application/json\n\n')
    SPversion = myjson['SPversion']
    m_Email = myjson['Email']
    patchType = myjson['PatchType']
    MsiGroupList = myjson['MsiGroupList']
    for msiGroup in MsiGroupList:
        logger.info(msiGroup+":"+MsiGroupList[msiGroup]['baseImageDir'])
        logger.info(msiGroup+":"+MsiGroupList[msiGroup]['upgradeImageDir'])
        logger.info(msiGroup+":"+MsiGroupList[msiGroup]['changedFileList'])
    logger.info ('SPversion: ' + SPversion)
    logger.info ('Email: ' + m_Email)

    for msiGroup in MsiGroupList:
        CheckImageExist(msiGroup)

    MainBaseMsiFile = glob.glob(MsiGroupList['MsiGroup0']['baseImageDir']+"\\*.msi")
    MainProductAliasName = os.path.basename(MainBaseMsiFile[0]).split('.',1)[0]
    logger.info ("MainProductAliasName is: "+str(MainProductAliasName))
    MainMsiName = MainProductAliasName+".msi"

    PatchUUID = msilib.gen_uuid()
    MainBaseMsiProductCode = GetProductCode(MainBaseMsiFile[0])
    MainUpgradeMsiProductVersion = GetProductVersion(MsiGroupList['MsiGroup0']['upgradeImageDir']+"\\"+MainMsiName)
    workspaceBuildPath="E:\\SPworkspace\\Build\\"+str(MainBaseMsiProductCode)+"\\"+MainUpgradeMsiProductVersion+"\\"
    workspacePatchPath="E:\\SPworkspace\\Patch\\"+str(MainBaseMsiProductCode)+"\\"+MainUpgradeMsiProductVersion+"\\"
    sharedFolder = "E:\\shared\\patch\\"

    LocalMsiGroupList = dict()
    for msiGroup in MsiGroupList:
        (localBaseImagePath,localUpgradImagePath) =  PrepareImages(msiGroup)
        LocalMsiGroupList[msiGroup] = dict()
        LocalMsiGroupList[msiGroup]['baseImagePath'] = localBaseImagePath #workspacePatchPath+msiGroup+"_Base\\" #localBaseImagePath
        LocalMsiGroupList[msiGroup]['upgradeImagePath'] = localUpgradImagePath #workspacePatchPath+msiGroup+"_Last\\" #localUpgradImagePath
    
    GeneratePatchWXS(LocalMsiGroupList)
    CreatePatchMain(LocalMsiGroupList)

except Exception as Exce:
    logger.info("Exception is: "+ str(Exce))
