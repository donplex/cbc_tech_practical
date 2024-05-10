import re
from datetime import date
from os import path
from os import makedirs
from os import listdir
from os import remove
from shutil import move
import pandas as pd


#-----------Today Date-----------
strToday = date.today().strftime("%Y_%m_%d")


#--------Regex Patterns----
strTextFileHeaderSperatorPattern = r'_+\n\t'
strMessageIndetification = r'[-]*\s*Message\s*Text\s*[-]*'
strAccountIdentificationPattern = r'\s*Account\s*Identification\s*\d+\s*28C\s*'
strStatementNumberPattern = r'\s*Statement\s*Number\s*/\s*Sequence\s*Number\s*\d+/\d+\s*61\:\s*Statement\s*Line\s*'
strLineDataPattern = r'\s*Statement\s*Line\s*'


#--------- Statment Header Data Init---------
strAccountIdentification = ""
strStatementNumber = ""


#----------Folder Paths-----------
strPendingPath = ".\\STATEMENTS\\PENDING\\"+ strToday+"\\"
strSuccessfullPath = ".\\STATEMENTS\SUCCESFULL\\"+ strToday+"\\"
strRejectedPath = ".\\STATEMENTS\\REJECTED\\"+ strToday+"\\"
strMessagesTextPath =".\\MessagesText\\"+ strToday+"\\"





#---------Folder Creation Fuction---------
def create_folder_structure( strFolderPath):

    try:
        if( not path.exists( strFolderPath ) ):
            makedirs( strFolderPath )
            print("Folder Path Created. Path : ", strFolderPath )
        else:
            print("Folder Path Exists, No Need to Create !")

    except Exception as e:
        print("Folder Creation Exception : ", e)



#---------Move Files------------
def move_file( strSourceFilePath, strDestinationFilePath ):
    try:
        if ( path.isfile( strDestinationFilePath + path.basename(strSourceFilePath) ) ) :
            remove( strDestinationFilePath + path.basename(strSourceFilePath) )       
        move( strSourceFilePath, strDestinationFilePath )
        print("File Moved to Path : "+strSourceFilePath+" into Path : "+strDestinationFilePath +" is Successfully !")
        return True
    
    except Exception as e:
        print("File Moved to Path : "+strSourceFilePath+" into Path : "+strDestinationFilePath +" is Failed ! Exception : "+str(e) )
        return False





#-----------Read Text File------------
def text_file_read( strTextFilePath ):
    try:
        strTextFileData = ""

        with open( strTextFilePath, "r" ) as file:
            strTextFileData = file.read()
            print("Text File Read Succesfully !")
            return strTextFileData
    
    except Exception as e:
        print("Text File Reading Exception : ", e)




#-----------Get All Text Files In Path-------------
def get_file_lsit( strTextFilePath ):
    try:
        text_files_list = []

        for file in listdir( strTextFilePath ) :
            if file.endswith( ".txt" ):
                # xml_files.append( path.join( strPath, file ))
                text_files_list.append( file )

        if ( ( text_files_list is None ) or ( len( text_files_list ) == 0 ) ):
            print("Text Files Cannot Found in Path : "+strTextFilePath ) 
            return 0, text_files_list
        else:
            print( "Text Files Found : "+ str( len( text_files_list ) ) ) 
            return len( text_files_list ), text_files_list
    
    except Exception as e:
        print("Get Text File in Folder Path Exception : ", e )










####################-----Process-----#####################

#-----------Folder Structure Creation---------------
create_folder_structure( strPendingPath )
create_folder_structure( strSuccessfullPath )
create_folder_structure( strRejectedPath )
create_folder_structure( strMessagesTextPath )



#------------Get All Available Text Files-----------------------
intTextFileCount , strTextFileList = get_file_lsit( strPendingPath )

#Text File Cont > 0
if( intTextFileCount > 0 ):

    for textFile in strTextFileList:

        boolSuccessStatus = False

        textFile = strPendingPath+textFile

        strTextFileData = text_file_read( textFile )


        #-------Text File Header Remove--------
        strTextFileData = ( re.split( strTextFileHeaderSperatorPattern , strTextFileData ) )[1]

        #-------Text FIle Message Text Grouping---------
        strMessagesList = ( re.split( strMessageIndetification , strTextFileData ,re.IGNORECASE) )

        strMessagesList = [item for item in strMessagesList if item is not None and item != ""]


        #---------Message Text Availability Check---------- 
        if( len(strMessagesList) > 0 ):

            for message in strMessagesList:
                strAccountIdentification = ""
                strStatementNumber = ""

                # print("Message Text Ouput : ", message )

                #-----------Account Identification Number-----------
                strAccountIdentification = re.search( r'\d+', (re.search( strAccountIdentificationPattern, message , re.IGNORECASE)[0] )).group(0)

                #----------Statement Number-----------
                strStatementNumber = re.search( r'\d+/\d+' , ( re.search( strStatementNumberPattern, message , re.IGNORECASE)[0] ) ).group(0)


                print( "Account Identification : "+strAccountIdentification  +"   |   StatementNumber : "+strStatementNumber )


                #----------Line Data Extraction as a Table Format-------------
                strLineData = re.split( strLineDataPattern , message , re.IGNORECASE)[1] 

                LineRowsList = strLineData.strip().split('\n')

                tableDataList = [ row.split() for row in LineRowsList ]

                if( (tableDataList is None) or len(tableDataList) > 0 ):
                    
                    dfLineData = pd.DataFrame( tableDataList[1:] , columns=tableDataList[0] )

                    # cleansedLineData = dfLineData[ dfLineData['Amount' ] is not None  or dfLineData['Amount' !="" ] ]
                    cleansedLineData = dfLineData[ dfLineData['Amount' ].notna()]

                    #>>>>>>>>>>>> If need Multi line Transaction Referece Concatination into one line that also can do


                    #>>>>>>>>>>Cleanse Row Values<<<<<<<<<<<<<<<<<<
                    for rowIndex, row in cleansedLineData.iterrows():
                        #Cleanse Amount Column Data
                        row['Amount'] = ( re.search( r'\d+\.\d+' , row['Amount'] ) ).group(0)

                        #----- If need cleansing for other columns also can do within this loop



                    strOutputFilePath = ( strMessagesTextPath + strAccountIdentification+"_"+strStatementNumber.replace("/","_")+ ".xlsx" )

                    cleansedLineData.to_excel( strOutputFilePath , index=False, sheet_name="LineData")

                    boolSuccessStatus = True

                else:
                    print("Text File Line Data is Not Available !")

        else:
            print("No Messages Text")


        #-----------Original Text File Move------
        if( boolSuccessStatus == True ):
            #Successful
            move_file( textFile, strSuccessfullPath )
        else:
            #Rejected
            move_file( textFile, strRejectedPath )



