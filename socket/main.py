from email.mime import image
from operator import truediv
from tkinter import *
from tkinter import dialog
from tkinter import scrolledtext
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import *
import tkinter as tk
import os
from turtle import width
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
import os
from email import encoders
import base64
from tkinter import Image, ttk
from tkinter import messagebox
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tkinter import font
from tkinter import filedialog
from tkinter.tix import IMAGETEXT
from webbrowser import BackgroundBrowser
import socket
from support import *
import sys
import time
import threading
import customtkinter

customtkinter.set_appearance_mode("light")

def closeWindow(main_window,thread_and_event_dic):
    for thread,event in thread_and_event_dic.items():
        if thread.is_alive():
            event.set()
            del thread_and_event_dic[thread]
            break
    main_window.destroy()
    sys.exit()
def attachFileClicked(attachment_name_list,work_frame,attach_box,max_size):
    file_path = filedialog.askopenfilename(title="Choose a file", filetypes=[("All files", "*.*")])
    attachment_path_var = tk.StringVar()
    attachment_path_var.set(file_path)
    if file_path:
        file_name = os.path.basename(file_path)
        size_file = os.path.getsize(file_path)
    
        if(size_file > max_size - sum(attachment_name_list.values())):
            fail_annouce_label = tk.Label(work_frame,text ="File size exceed max size. Please choose another file!")
            fail_annouce_label.place(x=1,y=1)
        else:
            #attach_box.configure("blue", foreground="blue")
            attach_box.insert(tk.END, f"{file_name}\n","blue")
            choosed_annouce_label = tk.Label(work_frame,text ="Choosed file!")
            choosed_annouce_label.place(x=1,y=1)
            attachment_name_list[file_path] = size_file
def sendClicked(work_frame,to_entry,cc_entry,bcc_entry,subject_entry, body_entry,attachment_list, host, SMTP_port,data):
     subject = subject_entry.get()
     content = body_entry.get("1.0","end-1c")
     to = to_entry.get()
     cc = cc_entry.get()
     bcc = bcc_entry.get()

     if to == "" and cc == "" and bcc == "":
         empty_recv_label = customtkinter.CTkLabel(work_frame,text = "Empty recipient. Please input again!")
         empty_recv_label.pack()
         return
     if subject == "":
         empty_subject_label = customtkinter.CTkLabel(work_frame,text = "Empty subject. Please input again!")
         empty_subject_label.pack()
         return
     if content == "":
         empty_content_label = customtkinter.CTkLabel(work_frame,text = "Empty body. Please input again!")
         empty_content_label.pack()
         return

     sender_email = data["General"]["Email"]
     password = data["General"]["Password"]
     recipient_list ={}
     bcc_list = bcc.split(",")
     to_list = to.split(",")
     cc_list = cc.split(",")

     if bcc != "":
         for recv in bcc_list:
             recipient_list[recv] = 'bcc'
     if cc != "":
         for recv in cc_list:
             recipient_list[recv] = 'cc'
     if to != "":
         for recv in to_list:
             recipient_list[recv] = 'to'

     # Send email message
     for recv,send_type in recipient_list.items():

         #Starting
         client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         server_address = (host, SMTP_port)
         print('Connecting to  port ' + str(server_address))
         client.connect(server_address)
         print("Connect succesfull!")
         print(client.recv(1024).decode())

         # Creat MIMEMultiPart object
         msg = MIMEMultipart()
         msg['Subject'] = subject
         msg['From'] = sender_email
         if to != "":
            msg['To'] = to
         if cc != "":
            msg['Cc'] = cc
         if send_type == 'bcc':
             msg['Bcc'] = recv
         msg.attach(MIMEText(content,'plain','us-ascii'))
         # attach attachments in mail
         if len(attachment_list) != 0:
            for file_path in attachment_list.keys():
                file_name = os.path.basename(file_path)
                with open(file_path,"rb") as file:
                    file_content = file.read()
         
                # Creat MIMEBase Object    
                attachment = MIMEBase('application','octet-stream')
                attachment.set_payload(file_content)
                # Encode MIMEBase Object
                encoders.encode_base64(attachment)
                # Write title and file name
                attachment.add_header('Content-Disposition', f'attachment; filename={file_name}')
                msg.attach(attachment)
         
         # send commands to server
         client.sendall(f'MAIL FROM: <{sender_email}>\r\n'.encode())
         print(client.recv(1024).decode())

         client.sendall(f'RCPT TO: <{recv}>\r\n'.encode())
         print(client.recv(1024).decode())

         client.sendall(b'DATA\r\n')
         print(client.recv(1024).decode())

         # send content of email to server
         client.sendall(f'{msg.as_string()}.\r\n'.encode())
         response = client.recv(1024).decode()
         print(response)

         # Close
         client.sendall(b'QUIT\r\n')
         print(client.recv(1024).decode())
         client.close()

     sent_annou=customtkinter.CTk()
     sent_annou.resizable(False,False)
     sent_label = customtkinter.CTkLabel(sent_annou,text="Message sent!"
                                        ,font=("Inter",12,'bold')
                                        ,text_color="#D15FEE")
     sent_label.pack()
     sent_annou.protocol("WM_DELETE_WINDOW",lambda: sent_annou.destroy())
     sent_annou.mainloop()
def sendEmailWindow(work_frame,thread_and_event_dic):
    for widget in work_frame.winfo_children():
           widget.destroy()
    for thread,event in thread_and_event_dic.items():
        if thread.is_alive():
            event.set()
            del thread_and_event_dic[thread]
            break
    message_frame = customtkinter.CTkFrame(work_frame, fg_color="#34495e", corner_radius=5, border_color="#104E8B", border_width=2)
    message_frame.pack(side="left", expand=True, fill="both")
    
    to_label = customtkinter.CTkLabel(message_frame,font=("Montserrat", 14, 'bold'),text_color="#778899",text="To: ")
    to_label.place(x=140,y=44)
    to_entry = customtkinter.CTkEntry(message_frame,placeholder_text="Nếu nhập nhiều địa chỉ, thi mỗi địa chỉ cách nhau bới dấu phẩy và không chứa dấu cách",
                                      text_color="#708090" ,height=40,width=600,fg_color="#34495e",border_color="#2c3e50",border_width=2,corner_radius=10)
    to_entry.place(x=210,y=40)
    
    
    bc_label = customtkinter.CTkLabel(message_frame,font=("Montserrat", 14, 'bold'),text_color="#778899",text="BCC: ")
    bc_label.place(x=140,y=44+60)
    bc_entry = customtkinter.CTkEntry(message_frame,text_color="#708090" ,placeholder_text="Nếu nhập nhiều địa chỉ, thi mỗi địa chỉ cách nhau bới dấu phẩy và không chứa dấu cách",
                                      height=40,width=600,fg_color="#34495e",border_color="#2c3e50",border_width=2,corner_radius=10)
    bc_entry.place(x=210,y=40+60)

    cc_label = customtkinter.CTkLabel(message_frame,font=("Montserrat", 14, 'bold'),text_color="#778899",text="CC: ")
    cc_label.place(x=140,y=44+60+60)
    cc_entry = customtkinter.CTkEntry(message_frame,text_color="#708090" ,placeholder_text="Nếu nhập nhiều địa chỉ, thi mỗi địa chỉ cách nhau bới dấu phẩy và không chứa dấu cách",
                                      height=40,width=600,fg_color="#34495e",border_color="#2c3e50",border_width=2,corner_radius=10)
    cc_entry.place(x=210,y=40+60+60)
    
    
    subject_label = customtkinter.CTkLabel(message_frame,font=("Montserrat", 14, 'bold'),text_color="#778899",text="Subject: ")
    subject_label.place(x=140,y=44+60*3)
    subject_entry = customtkinter.CTkEntry(message_frame,text_color="#708090" ,placeholder_text="Nhập tiêu đề",height=40,width=600,fg_color="#34495e",border_color="#2c3e50",border_width=2,corner_radius=10)
    subject_entry.place(x=210,y=40+60*3)
    
    body_label = customtkinter.CTkLabel(message_frame,font=("Montserrat", 14, 'bold'),text_color="#778899",text="Content: ")
    body_label.place(x=140,y=44+60*4)
    body_entry=customtkinter.CTkTextbox(message_frame,height=200,text_color="#B0C4DE",width=600,fg_color="#34495e",border_color="#2c3e50",border_width=2)
    body_entry.place(x=210,y=44+60*4+20)

    attach_box=customtkinter.CTkTextbox(message_frame,height=100,text_color="#B0C4DE",
                                        width=600,fg_color="#34495e",border_color="#2c3e50",
                                        border_width=2,corner_radius=10)
    attach_box.place(x=210,y=510)

    # attach button
    #iconAttach_name="attached.png"
    #iconAttach_path=os.path.abspath(iconAttach_name)
    #icon_attach = customtkinter.PhotoImage(file=iconAttach_path)
    #icon_attach = icon_attach.subsample(20)
    attachment_list ={}
    max_size = 1024 ** 2
    attach_button = customtkinter.CTkButton(message_frame,
                               text="File",
                               font=("Montserrat", 14, 'bold'),
                               width=10,
                               fg_color="#51677d",
                               hover_color="#68838B",
                               command=lambda: attachFileClicked(attachment_list,work_frame,attach_box,max_size))
    attach_button.place(x=130,y=510)
    
    #send button
    send_button = customtkinter.CTkButton(message_frame,text="Send"
                             ,font=('Roboto',14,'bold')
                             ,fg_color="#2c3e50"
                             ,text_color="#778899"
                             ,border_color="#4A708B"
                             ,border_width=1
                             ,bg_color="#34495e"
                             ,command = lambda: sendClicked(work_frame,to_entry,cc_entry,bc_entry,subject_entry,body_entry,attachment_list,host,SMTP_port,data))
    send_button.place(x=400,y=640) 
def attachmentButtonClicked(parts_of_part):
    folder_path_to_save = filedialog.askdirectory(title="Choose folder to save attachment:")
    encode_attachment_content = parts_of_part[1]
     # Decode encode attachment content
    try:
      attachment_content1 = base64.b64decode(encode_attachment_content)
    except Exception as e:
      print(f"Error decoding base64: {e}")
    attachment_content2 = base64.b64decode(attachment_content1)
    # name of attachment and add attachment in attachment list
    attachment_name_position = parts_of_part[0].find(b"Attachment")
    temp = slice(attachment_name_position+12,len(parts_of_part[0]))
    attachment_name = parts_of_part[0][temp].decode()
    new_file_path = f"{folder_path_to_save}/{attachment_name}"

    try:
        with open(new_file_path,'wb') as file:
            file.write(attachment_content2)
    except Exception as e:
        print(f"Error :{e}")
    downloaded=customtkinter.CTk()
    downloaded.resizable(False,False)
    downloaded_label = customtkinter.CTkLabel(downloaded,text="Downloaded!"
                                        ,font=("Inter",12,'bold')
                                        ,text_color="#D15FEE")
    downloaded_label.pack()
    downloaded.protocol("WM_DELETE_WINDOW",lambda: downloaded.destroy())
    downloaded.mainloop()
def newprocessViewEmailOnInterface(content_frame,i,folder_path,mailname_list,display_name_list,mailbutton_list):
    
    for widget in content_frame.winfo_children():
        widget.destroy()

    mail_path = os.path.join(folder_path,mailname_list[i])
    with open(mail_path,'rb') as file:
       email_data = file.read()

    sub_parts = email_data.split(b"\r\n\r\n")
    attachment_list = {}

    text = customtkinter.CTkTextbox(content_frame, width=300, height=500,font=('Calibri',15,'bold'),text_color="#BFEFFF",fg_color="#34495e")
    text.delete(1.0,tk.END)
    text.insert(tk.END,sub_parts[0])
    text.insert(tk.END,"\r\n\r\n")
    text.insert(tk.END,sub_parts[1])
    text.pack(side = tk.TOP,fill=tk.BOTH)
   
    print(i)

    if("Unread" in mailname_list[i]):
        newname = mailname_list[i].replace("Unread","")
        mailname_list[i] = newname
        newdisplay_name = display_name_list[i].replace("(Unread)","")
        display_name_list[i] = newdisplay_name
        mail_newpath = os.path.join(os.path.dirname(mail_path),mailname_list[i])
        os.rename(mail_path,mail_newpath)
        mailbutton_list[i].configure(text = display_name_list[i])

    for i, part in enumerate(sub_parts):
             if  i > 1 and i != len(sub_parts)-1: # attachment content of email 
                 parts_of_part = part.split(b"\n")
                 encode_attachment_content = parts_of_part[1]
                 attachment_button =customtkinter.CTkButton(content_frame,text=parts_of_part[0],
                                                            font=('Calibri',15,'bold'),
                                                            text_color="#BFEFFF",
                                                            fg_color="#34495e",
                                                            height=50,
                                                            width=189,
                                                            command =lambda parts_of_part = parts_of_part: attachmentButtonClicked(parts_of_part))
                 attachment_button.pack()
             else:
                 pass
def autoloadThreadFunctionProject(host,POP3_port,data,listmail_frame,content_frame,folder_name,project_stop_event,time_to_autoload):
    while not project_stop_event.is_set():
        receiveMail(host,POP3_port,data)
        current_directory = os.getcwd()
        folder_path = os.path.join(current_directory,folder_name)
        if not os.path.exists(folder_path):
             os.makedirs(folder_path)
        for widget in listmail_frame.winfo_children():
           widget.destroy()
        mailname_list,display_name_list = findEmailListOfFolder(folder_path)
        if len(mailname_list) == 0:
            empty_text = customtkinter.CTkLabel(listmail_frame,text = "Empty..",
                                                font=('Calibri',15,'bold'),
                                                text_color="#BFEFFF",
                                                fg_color="#34495e",
                                                height=50,
                                                width=300)
            empty_text.pack()
        else:
            mailbutton_list = []
            for i in range(len(mailname_list)):
                mail_button = customtkinter.CTkButton(listmail_frame,text = display_name_list[i],
                                                      font=('Calibri',15,'bold'),
                                                      text_color="#BFEFFF",
                                                      fg_color="#34495e",
                                                      height=50,
                                                      width=300,
                                                      command = lambda i =i: newprocessViewEmailOnInterface(content_frame,i,folder_path,mailname_list,display_name_list,mailbutton_list))
                mail_button.pack()
                mailbutton_list.append(mail_button)
        time.sleep(time_to_autoload)
def autoloadThreadFunctionWork(host,POP3_port,data,listmail_frame,content_frame,folder_name,work_stop_event,time_to_autoload):
    while not work_stop_event.is_set():
        receiveMail(host,POP3_port,data)
        current_directory = os.getcwd()
        folder_path = os.path.join(current_directory,folder_name)
        if not os.path.exists(folder_path):
             os.makedirs(folder_path)
        for widget in listmail_frame.winfo_children():
           widget.destroy()
        mailname_list,display_name_list = findEmailListOfFolder(folder_path)
        if len(mailname_list) == 0:
            empty_text = customtkinter.CTkLabel(listmail_frame,text = "Empty..",
                                                font=('Calibri',15,'bold'),
                                                text_color="#BFEFFF",
                                                fg_color="#34495e",
                                                height=50,
                                                width=300)
            empty_text.pack()
        else:
            mailbutton_list = []
            for i in range(len(mailname_list)):
                mail_button = customtkinter.CTkButton(listmail_frame,text = display_name_list[i],
                                                      font=('Calibri',15,'bold'),
                                                      text_color="#BFEFFF",
                                                      fg_color="#34495e",
                                                      height=50,
                                                      width=300,
                                                      command = lambda i =i: newprocessViewEmailOnInterface(content_frame,i,folder_path,mailname_list,display_name_list,mailbutton_list))
                mail_button.pack()
                mailbutton_list.append(mail_button)
        time.sleep(time_to_autoload)
def autoloadThreadFunctionInbox(host,POP3_port,data,listmail_frame,content_frame,folder_name,inbox_stop_event,time_to_autoload):
    while not inbox_stop_event.is_set():
        receiveMail(host,POP3_port,data)
        current_directory = os.getcwd()
        folder_path = os.path.join(current_directory,folder_name)
        if not os.path.exists(folder_path):
             os.makedirs(folder_path)
        for widget in listmail_frame.winfo_children():
           widget.destroy()
        mailname_list,display_name_list = findEmailListOfFolder(folder_path)
        if len(mailname_list) == 0:
            empty_text = customtkinter.CTkLabel(listmail_frame,text = "Empty..",
                                                font=('Calibri',15,'bold'),
                                                text_color="#BFEFFF",
                                                fg_color="#34495e",
                                                height=50,
                                                width=300)
            empty_text.pack()
        else:
            mailbutton_list = []
            for i in range(len(mailname_list)):
                mail_button = customtkinter.CTkButton(listmail_frame,text = display_name_list[i],
                                                      font=('Calibri',15,'bold'),
                                                      text_color="#BFEFFF",
                                                      fg_color="#34495e",
                                                      height=50,
                                                      width=300,
                                                      command = lambda i =i: newprocessViewEmailOnInterface(content_frame,i,folder_path,mailname_list,display_name_list,mailbutton_list))
                mail_button.pack()
                mailbutton_list.append(mail_button)
        time.sleep(time_to_autoload)
def autoloadThreadFunctionImportant(host,POP3_port,data,listmail_frame,content_frame,folder_name,important_stop_event,time_to_autoload):
    while not important_stop_event.is_set():
        receiveMail(host,POP3_port,data)
        current_directory = os.getcwd()
        folder_path = os.path.join(current_directory,folder_name)
        if not os.path.exists(folder_path):
             os.makedirs(folder_path)
        
        for widget in listmail_frame.winfo_children():
           widget.destroy()
        mailname_list,display_name_list = findEmailListOfFolder(folder_path)
        if len(mailname_list) == 0:
            empty_text = customtkinter.CTkLabel(listmail_frame,text = "Empty..",
                                                font=('Calibri',15,'bold'),
                                                text_color="#BFEFFF",
                                                fg_color="#34495e",
                                                height=50,
                                                width=300)
            empty_text.pack()
        else:
            mailbutton_list = []
            for i in range(len(mailname_list)):
                mail_button = customtkinter.CTkButton(listmail_frame,text = display_name_list[i],
                                                      font=('Calibri',15,'bold'),
                                                      text_color="#BFEFFF",
                                                      fg_color="#34495e",
                                                      height=50,
                                                      width=300,
                                                      command = lambda i =i: newprocessViewEmailOnInterface(content_frame,i,folder_path,mailname_list,display_name_list,mailbutton_list))
                mail_button.pack()
                mailbutton_list.append(mail_button)
        time.sleep(time_to_autoload)
def autoloadThreadFunctionSpam(host,POP3_port,data,listmail_frame,content_frame,folder_name,spam_stop_event,time_to_autoload):
    while not spam_stop_event.is_set():
        receiveMail(host,POP3_port,data)
        current_directory = os.getcwd()
        folder_path = os.path.join(current_directory,folder_name)
        if not os.path.exists(folder_path):
             os.makedirs(folder_path)
        for widget in listmail_frame.winfo_children():
           widget.destroy()
        mailname_list,display_name_list = findEmailListOfFolder(folder_path)
        if len(mailname_list) == 0:
            empty_text = customtkinter.CTkLabel(listmail_frame,text = "Empty..",
                                  font=('Calibri',15,'bold'),
                                  text_color="#BFEFFF",
                                  fg_color="#34495e",
                                  height=50,
                                  width=300)             
            empty_text.pack()
        else:
            mailbutton_list = []
            for i in range(len(mailname_list)):
                mail_button = customtkinter.CTkButton(listmail_frame,text = display_name_list[i],
                                                      font=('Calibri',15,'bold'),
                                                      text_color="#BFEFFF",
                                                      fg_color="#34495e",
                                                      height=50,
                                                      width=300,
                                                      command = lambda i =i: newprocessViewEmailOnInterface(content_frame,i,folder_path,mailname_list,display_name_list,mailbutton_list))
                mail_button.pack()
                mailbutton_list.append(mail_button)
        time.sleep(time_to_autoload)
def projectButton(check_mailbox_window,listmail_frame,content_frame,thread_and_event_dic):
    for thread,event in thread_and_event_dic.items():
        if thread.is_alive():
            event.set()
            del thread_and_event_dic[thread]
            break

    stop_event = threading.Event()
    autoload_thread = threading.Thread(target = autoloadThreadFunctionInbox,
                                             args =(host,POP3_port,data,listmail_frame,content_frame,"Project",stop_event,time_to_autoload))
    thread_and_event_dic[autoload_thread] = stop_event
    autoload_thread.start()
def inboxButton(check_mailbox_window,listmail_frame,content_frame,thread_and_event_dic):
    for thread,event in thread_and_event_dic.items():
        if thread.is_alive():
            event.set()
            del thread_and_event_dic[thread]
            break

    stop_event = threading.Event()
    autoload_thread = threading.Thread(target = autoloadThreadFunctionInbox,
                                             args =(host,POP3_port,data,listmail_frame,content_frame,"Inbox",stop_event,time_to_autoload))
    thread_and_event_dic[autoload_thread] = stop_event
    autoload_thread.start()
def importantButton(check_mailbox_window,listmail_frame,content_frame,thread_and_event_dic):
    for thread,event in thread_and_event_dic.items():
        if thread.is_alive():
            event.set()
            del thread_and_event_dic[thread]
            break

    stop_event = threading.Event()
    autoload_thread = threading.Thread(target = autoloadThreadFunctionImportant,
                                             args =(host,POP3_port,data,listmail_frame,content_frame,"Important",stop_event,time_to_autoload))
    thread_and_event_dic[autoload_thread] = stop_event
    autoload_thread.start()
def workButton(check_mailbox_window,listmail_frame,content_frame,thread_and_event_dic):
    for thread,event in thread_and_event_dic.items():
        if thread.is_alive():
            event.set()
            del thread_and_event_dic[thread]
            break

    stop_event = threading.Event()
    autoload_thread = threading.Thread(target = autoloadThreadFunctionInbox,
                                             args =(host,POP3_port,data,listmail_frame,content_frame,"Work",stop_event,time_to_autoload))
    thread_and_event_dic[autoload_thread] = stop_event
    autoload_thread.start()
def spamButton(check_mailbox_window,listmail_frame,content_frame,thread_and_event_dic):
   for thread,event in thread_and_event_dic.items():
        if thread.is_alive():
            event.set()
            del thread_and_event_dic[thread]
            break

   stop_event = threading.Event()
   autoload_thread = threading.Thread(target = autoloadThreadFunctionInbox,
                                             args =(host,POP3_port,data,listmail_frame,content_frame,"Spam",stop_event,time_to_autoload))
   thread_and_event_dic[autoload_thread] = stop_event
   autoload_thread.start()
def newcheckMailboxWindow(work_frame):
    for widget in work_frame.winfo_children():
           widget.destroy()
    # create frame to show mail folders
    mailfolder_frame = customtkinter.CTkFrame(work_frame, width=200, fg_color="#34495e", corner_radius=5, border_color="#104E8B", border_width=2)
    mailfolder_frame.pack(side="left", expand=False, fill="y")
    
    # create frame to show maillist of a folder
    listmail_frame = customtkinter.CTkScrollableFrame(work_frame, 
                                            width=300,
                                            fg_color="#2c3e50",
                                            corner_radius=5,
                                            border_color="#104E8B",
                                            border_width=2)
    listmail_frame.pack(side="left", expand=False, fill="y")

    # create frame to show mail content
    mailcontent_frame = customtkinter.CTkScrollableFrame(work_frame,fg_color="#2c3e50",
                                                corner_radius=5,
                                                border_color="#104E8B",
                                                border_width=2)
    mailcontent_frame.pack(side="left",fill="both",expand=True)
             

    # add button in mailfolder frame
    inbox_button = customtkinter.CTkButton(mailfolder_frame,
                                           text = "Inbox",
                                           font=('Calibri',15,'bold'),
                                           text_color="#BFEFFF",
                                           fg_color="#34495e",
                                           height=50,
                                           width=189,
                                           command = lambda: inboxButton(main_window,listmail_frame,mailcontent_frame,thread_and_event_dic))
    inbox_button.pack()
    project_button = customtkinter.CTkButton(mailfolder_frame,
                                             text = "Project",
                                             font=('Calibri',15,'bold'),
                                             text_color="#BFEFFF",
                                             fg_color="#34495e",
                                             height=50,
                                             width=189,
                                             command = lambda: projectButton(main_window,listmail_frame,mailcontent_frame,thread_and_event_dic))
    project_button.pack()
    important_button = customtkinter.CTkButton(mailfolder_frame,
                                               text = "Important",
                                               font=('Calibri',15,'bold'),
                                               text_color="#BFEFFF",
                                               fg_color="#34495e",
                                               height=50,
                                               width=189,
                                               command = lambda: importantButton(main_window,listmail_frame,mailcontent_frame,thread_and_event_dic))
    important_button.pack()
    work_button = customtkinter.CTkButton(mailfolder_frame,
                                          text = "Work",
                                          font=('Calibri',15,'bold'),
                                          text_color="#BFEFFF",
                                          fg_color="#34495e",
                                          height=50,
                                          width=189,
                                          command = lambda: workButton(main_window,listmail_frame,mailcontent_frame,thread_and_event_dic))
    work_button.pack()
    spam_button = customtkinter.CTkButton(mailfolder_frame,
                                          text = "Spam",
                                          font=('Calibri',15,'bold'),
                                          text_color="#BFEFFF",
                                          fg_color="#34495e",
                                          height=50,
                                          width=189,
                                          command = lambda: spamButton(main_window,listmail_frame,mailcontent_frame,thread_and_event_dic))
    spam_button.pack()
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")
def loginClicked(login_window,username,password,user_entry,password_entry):
    user_input = user_entry.get()
    password_input = password_entry.get()
    if user_input != username or password_input != password:
        failed_login_label=customtkinter.CTkLabel(login_window
                                            ,text="Wrong email address or password. Please input again!"
                                            ,font=("Inter",12,'bold')
                                            ,text_color="#D15FEE")
        failed_login_label.place(x=160,y=10)
        
    else:
        login_window.destroy()
def loginWindow():
    login_window = customtkinter.CTk()
    login_window.geometry('600x500')
    login_window._set_appearance_mode("light")
    
    login_window.title("Login")
    center_window(login_window,600,500)
    
    background_name="login_background.png"
    background_path=os.path.abspath(background_name)
    background_image = tk.PhotoImage(file=background_path)
    background_image = background_image.subsample(3)
    
    background_label=customtkinter.CTkLabel(login_window,image=background_image,height=500,width=600)
    background_label.place(x=0,y=0)
    login_frame=customtkinter.CTkFrame(login_window,height=499,width=300,fg_color="white",corner_radius=10)
    login_frame.place(x=300,y=1)
    

    

    welcome = customtkinter.CTkLabel(login_frame, text="Welcome Back!", font=("Inter", 20,'bold'),text_color="#8A2BE2")
    welcome.place(x=45,y=50)
    
    Title = customtkinter.CTkLabel(login_frame, text="Sign in to your account", font=("Inter", 10,'bold'),text_color="#DDA0DD")
    Title.place(x=50,y=80)

 
    mail_image_label=customtkinter.CTkLabel(login_frame
                                            ,text=""
                                            
                                            )     
    mail_image_label.place(x=40,y=120)
    mail_image_label=customtkinter.CTkLabel(login_frame
                                            
                                            ,text=" Email:"
                                            ,font=("Inter",12,'bold')
                                            ,text_color="#D15FEE")
    mail_image_label.place(x=63,y=120)

    user_entry=customtkinter.CTkEntry(login_frame,
                                      border_color="#D15FEE",
                                      placeholder_text="someone@example.com",
                                      placeholder_text_color="#8A2BE2",
                                      border_width=2,
                                      fg_color="white",
                                      text_color="#8A2BE2",
                                      width=200)
    user_entry.place(x=40,y=150)
    
    
    
    #iconLock_name="lock.png"
    #iconLock_path=os.path.abspath(iconLock_name)
    #lock_image = tk.PhotoImage(file=iconLock_path)
    #lock_image = lock_image.subsample(20)

    # Convert the resized image to a PhotoImage object
   
    mail_image_label=customtkinter.CTkLabel(login_frame
                                            ,text=""
                                            
                                            )     
    mail_image_label.place(x=40,y=190)
    mail_image_label=customtkinter.CTkLabel(login_frame
                                            ,text=" Password:"
                                            ,font=("Inter",12,'bold')
                                            ,text_color="#D15FEE")
    mail_image_label.place(x=63,y=190)

    password_entry=customtkinter.CTkEntry(login_frame,
                                      border_color="#D15FEE",
                                      placeholder_text="password",
                                      placeholder_text_color="#8A2BE2",
                                      border_width=2,
                                      fg_color="white",
                                      text_color="#8A2BE2",
                                      show="*",
                                      width=200)
    password_entry.place(x=40,y=220)
    
    login_button=customtkinter.CTkButton(login_frame,text="Login",fg_color="#8A2BE2",font=("Inter",12,'bold'),width=200,command = lambda: loginClicked(login_window,username,password,user_entry,password_entry))
    login_button.place(x=40,y=280)

    login_window.protocol("WM_DELETE_WINDOW",lambda: closeWindow(login_window,thread_and_event_dic))
    login_window.mainloop()



if __name__ == "__main__":
    # Retrieve information of file config
    data = readFileConfig()
    time_to_autoload = data["General"]["Autoload"]
    host = data["General"]["MailServer"]
    SMTP_port = int(data["General"]["SMTP"])
    POP3_port = int(data["General"]["POP3"])
    username = data["General"]["Email"]
    password = data["General"]["Password"]

     #  dictionary to manage threads is alive
    thread_and_event_dic = {}

    #login window
    loginWindow()

    # create mailbox window
    main_window = customtkinter.CTk()
    main_window.title("App")
    main_window.geometry('1600x900')
    main_window._set_appearance_mode("light")
   
   

    #option frame
    option_frame = customtkinter.CTkFrame(main_window, height=40, fg_color="#2c3e50", corner_radius=15, border_color="#104E8B", border_width=2)
    option_frame.pack(fill="both")

    option_frame.grid_rowconfigure(0, weight=1)
    option_frame.grid_columnconfigure(0, weight=1)
    option_frame.grid_columnconfigure(1, weight=1)
    option_frame.grid_columnconfigure(2, weight=1)

    # Create work frame
    work_frame = customtkinter.CTkFrame(main_window, height=900-250, width=1600, fg_color="#2c3e50", corner_radius=3, border_color="#104E8B", border_width=2)
    work_frame.pack(expand=True, fill="both")

    send_email_button = customtkinter.CTkButton(option_frame, text="Send Email",
                                             text_color="#5D478B",
                                             corner_radius=10,
                                             fg_color="#2c3e50",
                                             border_color="#2c3e50",
                                             border_width=1,
                                             font=("Helvetica", 15, 'bold'),
                                             hover_color="#43586e",
                                             command = lambda: sendEmailWindow(work_frame,thread_and_event_dic))
                                             
    send_email_button.place(x=150, y=6)

    mailbox_button = customtkinter.CTkButton(option_frame, text="Mailbox",
                                             text_color="#5D478B",
                                             corner_radius=10,
                                             fg_color="#2c3e50",
                                             border_color="#2c3e50",
                                             border_width=1,
                                             font=("Helvetica", 15, 'bold'),
                                             hover_color="#43586e",
                                             command = lambda: newcheckMailboxWindow(work_frame))
    mailbox_button.place(x=5, y=6)

    main_window.protocol("WM_DELETE_WINDOW",lambda: closeWindow(main_window,thread_and_event_dic))
    main_window.mainloop()
    
