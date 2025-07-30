import socket
import json
import base64
import os
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from tkinter import CURRENT
from tkinter import *
from tkinter.ttk import *
import tkinter as tk

def readFileConfig():
    with open("config.json",'r') as json_file:
        data = json.load(json_file)
    return data
def sanitizeFilename(filename):
    return ''.join(c for c in filename if c.isalnum() or c in (' ', '.', '-'))
def filterEmail(send_from,subject,content,filter):
    for index,element in enumerate(filter):
        if index == 0:
            for name in filter[index]["From"]:
                if name in send_from.decode():
                   return filter[index]["ToFolder"]
        if index == 1:
            for value in filter[index]["Subject"]:
                if value in subject.decode():
                    return filter[index]["ToFolder"]
        if index == 2:
            for value in filter[index]["Content"]:
                if value in content.decode():
                    return filter[index]["ToFolder"]
        if index == 3:
            for value in filter[index]["Spam"]:
                if value in subject.decode() or value in content.decode():
                    return filter[index]["ToFolder"]
    
    return "Inbox"

def numberOfDownloadedEmail(folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        file_list = os.listdir(folder_path)
        file_number = int(len(file_list))
        return file_number
    else:
        return 0

def receiveMail(host,port,data):
     #Starting
     client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     server_address = (host, port)
     print('Connecting to  port ' + str(server_address))
     try:
         client.connect(server_address)
         print("Server:",client.recv(1024).decode())
         print("Connect succesfull!")
     except Exception as e:
         print(e)
     email_address = data["General"]["Email"]
     password = data["General"]["Password"]

     #Log in
     client.sendall(f'USER {email_address}\r\n'.encode())
     response = client.recv(4096).decode()
     print("Server: ",response)
     client.sendall(f'PASS {password}\r\n'.encode())
     response = client.recv(4096).decode()
     print("Server: ",response)

     # Number of emails
     client.sendall(b'STAT\r\n')
     response = client.recv(4096).decode()
     print("Server: ",response,'\n')
     current_number_of_emails = int(response.split(" ")[1]) # number of email on server
     
     # number of email in folder
     current_directory = os.getcwd()
     inbox_email_number = numberOfDownloadedEmail(os.path.join(current_directory,"Inbox"))
     project_email_number = numberOfDownloadedEmail(os.path.join(current_directory,"Project"))
     important_email_number = numberOfDownloadedEmail(os.path.join(current_directory,"Important"))
     spam_email_number = numberOfDownloadedEmail(os.path.join(current_directory,"Spam"))
     work_email_number = numberOfDownloadedEmail(os.path.join(current_directory,"Work"))

     # number of downloaded email
     downloaded_email_number = inbox_email_number + project_email_number + important_email_number + spam_email_number + work_email_number
     downloaded_email_number = downloaded_email_number + 1

     # Retrive content of emails

     while downloaded_email_number <= current_number_of_emails:
         client.sendall(b"LIST\r\n") # LIST: retrive order and size of emails
         response = client.recv(4096)
         print("Server: ", response.decode())
         lines = response.decode().split('\r\n')
         expected_size = int(lines[downloaded_email_number].split(" ")[1])

         downloaded_email_number_str = str(downloaded_email_number)
         command = b'RETR ' + downloaded_email_number_str.encode() + b'\r\n'
         client.sendall(command)

         #Retrive content of a email
         email_data = b""

         while len(email_data) < expected_size:
            try:
                response = client.recv(4096)
                if not response:
                    # Connect End
                    break
                email_data += response
            except socket.error as e:
                # Handle connect error
                print(f"Error receiving data: {e}")
                break

         if b'boundary' in email_data:
             # find boundary of MIMEMultiPart mail
             boundary_index = email_data.find(b'boundary')
             spot1_index = email_data.find(b'"',boundary_index)
             spot2_index = email_data.find(b'"',spot1_index+1)
             temp = slice(spot1_index+1,spot2_index)
             boundary = email_data[temp]
     
             # Split parts of MIMEMultiPart mail
             parts = email_data.split(b"--" + boundary)
             clean_parts = [part.strip() for part in parts]
             attachment_list = {} # dictionary include name and content of attachment
         
             to = ""
             cc = ""
             bcc =""

             # iterate parts of email
             for i, part in enumerate(clean_parts):
             
                 if i == 0: # information of mail
                     parts_of_part = part.split(b"\n")
                     for j, sub_part in enumerate(parts_of_part):
         
                         if sub_part.find(b"Subject") != -1:
                             subject = sub_part[slice(sub_part.find(b"Subject") + 9,len(sub_part))]
                         if sub_part.find(b"From") != -1:
                             send_from = sub_part[slice(sub_part.find(b"From") + 6,len(sub_part)-1)]
                         if sub_part.find(b"To") != -1:
                             to = sub_part[slice(sub_part.find(b"Subject") + 4,len(sub_part))]
                         if sub_part.find(b"Cc") != -1:
                             cc = sub_part[slice(sub_part.find(b"Subject") + 4,len(sub_part))]
                         if sub_part.find(b"Bcc") != -1:
                             bcc = sub_part[slice(sub_part.find(b"Subject") + 5,len(sub_part))]
                 elif i == 1: # text content of email
                     parts_of_part = part.split(b"\r\n\r\n")
                     content = parts_of_part[1]
                 elif i != len(clean_parts)-1: # attachment content of email 
                     parts_of_part = part.split(b"\r\n\r\n")
                     encode_attachment_content = parts_of_part[1]
                     base64_encoded_content = base64.b64encode(encode_attachment_content)

                     attachment_infor = parts_of_part[0].split(b"\n")
                     for infor in attachment_infor:
                         if b"filename" in infor:
                             name_attach_infor = infor
                     attachment_name_position = name_attach_infor.find(b"filename")
                     temp = slice(attachment_name_position+9,len(name_attach_infor))
                     attachment_name = name_attach_infor[temp].decode()
                     attachment_name = attachment_name.replace('"','')
                     attachment_name = attachment_name.replace('\r','')
                     attachment_list[attachment_name] = base64_encoded_content
             
             folder_name = filterEmail(send_from,subject,content,data["Filter"])
             pre_folder_path = os.getcwd()
             folder_path = os.path.join(pre_folder_path,folder_name)
             if not os.path.exists(folder_path):
                 os.makedirs(folder_path)
             newfile_name = "Unread_Email" + downloaded_email_number_str +".bin"
             newfile_name = sanitizeFilename(newfile_name)
             newfile_path = f"{folder_path}/{newfile_name}"
             with open(newfile_path,'wb') as file:
                 file.write(b"From: " + send_from+ b"\r\n")
                 file.write(b"Subject: " + subject + b"\r\n")
                 if to != "":
                     file.write(b"To: " + to + b"\r\n")
                 if cc != "":
                     file.write(b"Cc: " + cc + b"\r\n")
                 if bcc != "":
                     file.write(b"Bcc: " + bcc + b"\r\n")
                 file.write(b"\r\n\r\n")
                 file.write(content)
                 file.write(b"\r\n\r\n")
                 attachment_number = 1
                 for name,attachment_content in attachment_list.items():
                     file.write(b"Attachment")
                     file.write(str(attachment_number).encode())
                     file.write(b":")
                     file.write(name.encode())
                     file.write(b"\n")
                     file.write(attachment_content)
                     file.write(b"\r\n\r\n")
                     attachment_number += 1
                

             downloaded_email_number = downloaded_email_number + 1
         else:
             # Split parts of MIMEMultiPart mail
             parts = email_data.split(b'\r\n\r\n')
             clean_parts = [part.strip() for part in parts]
             attachment_list = {} # dictionary include name and content of attachment
         
             to = ""
             cc = ""
             bcc =""

             # iterate parts of email
             for i, part in enumerate(clean_parts):
             
                 if i == 0: # information of mail
                     parts_of_part = part.split(b"\n")
                     for j, sub_part in enumerate(parts_of_part):
         
                         if sub_part.find(b"Subject") != -1:
                             subject = sub_part[slice(sub_part.find(b"Subject") + 9,len(sub_part))]
                         if sub_part.find(b"From") != -1:
                             send_from = sub_part[slice(sub_part.find(b"From") + 6,len(sub_part)-1)]
                         if sub_part.find(b"To") != -1:
                             to = sub_part[slice(sub_part.find(b"Subject") + 4,len(sub_part))]
                         if sub_part.find(b"Cc") != -1:
                             cc = sub_part[slice(sub_part.find(b"Subject") + 4,len(sub_part))]
                         if sub_part.find(b"Bcc") != -1:
                             bcc = sub_part[slice(sub_part.find(b"Subject") + 5,len(sub_part))]
                 elif i == 1: # text content of email
                     content = part
                
             
             folder_name = filterEmail(send_from,subject,content,data["Filter"])
             pre_folder_path = os.getcwd()
             folder_path = os.path.join(pre_folder_path,folder_name)
             if not os.path.exists(folder_path):
                 os.makedirs(folder_path)
             newfile_name = "Unread_Email" + downloaded_email_number_str +".bin"
             newfile_name = sanitizeFilename(newfile_name)
             newfile_path = f"{folder_path}/{newfile_name}"
             with open(newfile_path,'wb') as file:
                 file.write(b"From: " + send_from+ b"\r\n")
                 file.write(b"Subject: " + subject + b"\r\n")
                 if to != "":
                     file.write(b"To: " + to + b"\r\n")
                 if cc != "":
                     file.write(b"Cc: " + cc + b"\r\n")
                 if bcc != "":
                     file.write(b"Bcc: " + bcc + b"\r\n")
                 file.write(b"\r\n\r\n")
                 file.write(content)
                 file.write(b"\r\n\r\n")
               
               
                

             downloaded_email_number = downloaded_email_number + 1

     client.sendall(b'QUIT\r\n')
     client.close()

def findEmailListOfFolder(folder_path):
    list_mail = os.listdir(folder_path)    
    mailname_list = []
    display_name_list = []
    for index, mail_name in enumerate(list_mail,start = 1):
        mail_path = os.path.join(folder_path,mail_name)

        with open(mail_path,'rb') as file:
            email_data = file.read()

        parts = email_data.split(b"\r\n")
        sender_name_start_position = parts[0].find(b"From")
        temp = slice(sender_name_start_position+6,len(parts[0]))
        sender_name = parts[0][temp].decode()
                
        subject_start_position = parts[1].find(b"Subject")
        temp = slice(sender_name_start_position+9,len(parts[1]))
        subject = parts[1][temp].decode()

        if "Unread" in mail_name:
            status = "(Unread)"
        else:
            status = ""

        mailname_list  = mailname_list + [mail_name]
        display_name_list = display_name_list + [status + sender_name + " - " + subject]
        
           
        
    return mailname_list,display_name_list

if __name__ == "__main__":
   data = readFileConfig()
   receiveMail(data["General"]["MailServer"],int(data["General"]["POP3"]),data)
  
   
