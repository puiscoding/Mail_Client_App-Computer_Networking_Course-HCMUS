import base64
import socket
import time
import os
import json
import webbrowser
import tempfile
from tkinter import * 
from tkinter.filedialog import askopenfilenames
from tkinter import messagebox
from tkinter import ttk
import tkinter as tk
from multiprocessing import Process, Event, Queue, Value
import re
import base64
from io import BytesIO

class Mail:
    def __init__(self):
        self.sender = ""
        self.to = str()   
        self.cc = str()
        self.bcc = str()
        self.subject = ""
        self.content = ""
        self.attachments = []
        self.sent = False
        self.read = False
    def add_to(self, recipient: str):
        self.to.append(recipient)
    def add_cc(self, recipient: str):
        self.cc.append(recipient)
    def add_bcc(self, recipient: str):
        self.bcc.append(recipient)
    def set_subject(self, subject: str):
        self.subject = subject  
    def set_content(self, content: str):
        self.content = content
    def add_attachment(self, file_path: str):
        self.attachments.append(file_path)
    def set_sender(self, sender:str):
        self.sender = sender
    def set_to(self, to:list):
        self.to = to
    def set_cc(self, cc:list):
        self.cc = cc
    def set_bcc(self, bcc:list):
        self.bcc = bcc  
    def set_attachments(self, attachments:list):
        self.attachments = attachments
    def get_sender(self):
        return self.sender
    def get_to(self):
        return self.to
    def get_cc(self):
        return self.cc
    def get_bcc(self):
        return self.bcc
    def get_subject(self):
        return self.subject
    def get_content(self):
        return self.content
    def get_attachments(self):
        return self.attachments
    def send_mail(self):
        sender_email = self.get_sender()
        receiver_email = re.split(", |; | ", self.get_to())
        ccReceiver_email = re.split(", |; | ", self.get_cc())
        bccReceiver_email = re.split(", |; | ", self.get_bcc())
        subject = self.get_subject()
        message = self.get_content()
        attachments = self.get_attachments()

        # thiết lập kết nối socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # thiết lập kết nối socket với máy chủ mail thông qua cổng 2225
        client_socket.connect((Host, SMTP_Port))

        # nhận dữ liệu từ server
        recv_data = client_socket.recv(1024).decode()
        #print(recv_data)

        if recv_data[:3] != "220":
            # label = Label(send_mail_frame, text="Failed to connect to server", fg="red")
            # label.grid(column=1, row=7)
            #print("Failed to connect to server")
            return

        # gửi lệnh EHLO hay HELO để bắt đầu phiên làm việc
        ehlo_command = "EHLO\r\n"
        client_socket.send(ehlo_command.encode())

        # nhận dữ liệu từ server
        recv_data = client_socket.recv(1024).decode()
        #print(recv_data)

        if recv_data[:3] != "250":
            #print("EHLO command failed")
            return

        # gửi lệnh MAIL FROM để chỉ định người gửi
        mail_from_command = "MAIL FROM: " + sender_email + "\r\n"
        client_socket.send(mail_from_command.encode())

        # nhận dữ liệu từ server
        recv_data = client_socket.recv(1024).decode()
        #print(recv_data)

        if recv_data[:3] != "250":
            #print("MAIL FROM command failed")
            return

        # gửi lệnh RCPT TO để chỉ định người nhận
        # to
        # receivers = receiver_email.split(" ")
        for receiver in receiver_email:
            if (receiver == ""):
                continue
            rcpt_to_command = "RCPT TO: " + receiver + "\r\n"
            client_socket.send(rcpt_to_command.encode())

            # nhận dữ liệu từ server
            recv_data = client_socket.recv(1024).decode()
            #print(recv_data)

            if recv_data[:3] != "250":
                #print("RCPT command failed")
                return

        
        for receiverCC in ccReceiver_email:
            if (receiverCC == ""):
                continue
            rcpt_to_command = "RCPT TO: " + receiverCC + "\r\n"
            client_socket.send(rcpt_to_command.encode())

            # nhận dữ liệu từ server
            recv_data = client_socket.recv(1024).decode()
            #print(recv_data)

            if recv_data[:3] != "250":
                #print("RCPT command failed")
                return

        for receiverBCC in bccReceiver_email:
            if (receiverBCC == ""):
                continue
            rcpt_to_command = "RCPT TO: " + receiverBCC + "\r\n"
            client_socket.send(rcpt_to_command.encode())

            # nhận dữ liệu từ server
            recv_data = client_socket.recv(1024).decode()
            #print(recv_data)

            if recv_data[:3] != "250":
                #print("RCPT command failed")
                return
            

        # gửi lệnh DATA để bắt đầu gửi nội dung mail
        data_command = "DATA\r\n"
        client_socket.send(data_command.encode())


        # nhận dữ liệu từ server
        recv_data = client_socket.recv(1024).decode()
        #print(recv_data)

        if recv_data[:3] != "354":
            return
        
        email_data =""

        if (len(attachments) > 0):
            email_data+= "Content-Type: multipart/mixed; boundary=\"==BOUNDARY==\"\r\n"
            email_data += "MIME-Version: 1.0\r\n"
        # gửi nội dung email
        email_data += "From: " + str(sender_email) + "\r\n"
        email_data += "To: " #+ str(receiver_email) + "\r\n"
        if (len(receiver_email) > 0):
            for receiver in receiver_email[:len(receiver_email)-1]:
                email_data += str(receiver) + ", "
            email_data += str(receiver_email[len(receiver_email)-1]) + "\r\n"
        else:
            email_data += "\r\n"

        email_data += "Cc: "# + str(ccReceiver_email) + "\r\n"
        if (len(ccReceiver_email) > 0):
            for receiverCC in ccReceiver_email[:len(ccReceiver_email)-1]:
                email_data += str(receiverCC) + ", "
            email_data += str(ccReceiver_email[len(ccReceiver_email)-1]) + "\r\n"
        else:
            email_data += "\r\n"
       

        email_data += "Subject: " + "=?UTF-8?B?" + base64.b64encode(subject.encode('utf-8')).decode() + "?=\r\n"
        if (len(attachments) > 0):
            email_data += "\r\n"
            email_data+="This is a multi-part message in MIME format.\r\n"
            email_data+="--==BOUNDARY==\r\n"
        email_data += "Content-Type: text/plain; charset=\"UTF-8\"\r\n"
        email_data += "Content-Transfer-Encoding: 8bit\r\n\r\n"
        client_socket.send(email_data.encode())

        # gửi nội dung email
        email_data = message + "\r\n"

        if (len(attachments) > 0):
            email_data += "\r\n"
        email_data = base64.b64encode(email_data.encode('utf-8')).decode('ascii') + "\r\n"
        client_socket.send(email_data.encode())

        # đọc file đính kèm nếu có
        if len(attachments) > 0:
            boundary = '--==BOUNDARY=='
           
            for attachment_path in attachments:
                if (attachment_path == ""):
                    continue
                client_socket.send((boundary+ "\r\n").encode())
                base, extension = os.path.splitext(attachment_path["name"]) 

                #mime format: content-type
                if (extension.lower() == ".txt"):   
                    client_socket.send(("Content-Type: text/plain; name=\"" + attachment_path["name"] + "\"\r\n").encode())
                elif (extension.lower() == ".pdf"):
                    client_socket.send(("Content-Type: application/pdf; name=\"" + attachment_path["name"] + "\"\r\n").encode())
                elif (extension.lower() == ".jpg" or extension.lower() == ".jpeg"):
                    client_socket.send(("Content-Type: image/jpeg; name=\"" + attachment_path["name"] + "\"\r\n").encode())
                elif (extension.lower() == ".png"):
                    client_socket.send(("Content-Type: image/png; name=\"" + attachment_path["name"] + "\"\r\n").encode())
                elif (extension.lower() == ".docx"):
                    client_socket.send(("Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document; name=\"" + attachment_path["name"] + "\"\r\n").encode())
                elif (extension.lower() == ".zip"):
                    client_socket.send(("Content-Type: application/zip; name=\"" + attachment_path["name"] + "\"\r\n").encode())
                name = attachment_path["name"]
                
                client_socket.send(("Content-Disposition: attachment; filename=\"" + attachment_path["name"] + "\"\r\n").encode())
                client_socket.send(("Content-Transfer-Encoding: base64\r\n\r\n").encode())
                
                attached_data_base64 = attachment_path["data"] 
               
                start = 0
                flag = True
                while start < len(attached_data_base64):
                    end = start + 16384#max length file
                    if end >= len(attached_data_base64):
                        end = len(attached_data_base64)
                        flag = False
                    
                    client_socket.send((attached_data_base64[start:end] + "\r\n").encode())
                    if not flag:
                        break
                    start = end
            client_socket.send((boundary+ "--\r\n").encode())

        client_socket.send(b'.\r\n')

        # nhận dữ liệu từ server
        recv_data = client_socket.recv(1024).decode()

        if recv_data[:3] != "250":
            #print("Failed to send mail")

            # đóng kết nối client
            client_socket.close()
            return

        # gửi lệnh QUIT để kết thúc phiên làm việc
        quit_command = "QUIT\r\n"
        client_socket.send(quit_command.encode())

        # đóng kết nối client
        client_socket.close()

       
        messagebox.showinfo("", "Email sent successfully")
        self.sent = True
        self.bcc =[]

    def display_in_console(self):
        print("Sender: " + self.sender)
        print("To: ")
        print(self.to)
        print("Cc: ")
        print(self.cc)
        print("Bcc: ")
        print(self.bcc)
        print("Subject: " + self.subject)
        print("Content: " + self.content)
        print("Attachments: ")
        print( self.attachments)
   
    def extract_and_save_attachment(self, fileId):
        attachments = self.get_attachments()
        if (fileId>=0 and fileId<len(attachments)):
            attachment = attachments[fileId]
            basename, extension = os.path.splitext(attachment["name"])
            if (extension == ".txt"):
                content = base64.b64decode(attachment["data"])
                content = content.decode('ascii')
                current_dir = os.getcwd()
                name = attachment["name"]
                file_path = os.path.join(current_dir, name)
                with open(file_path, "w") as file:
                    file.write(content)

    def show_attachment(self, fileId:int):
        attachments = self.get_attachments()
        if (fileId>=0 and fileId<len(attachments)):
            attachment = attachments[fileId]
            temp_dir = tempfile.gettempdir()
            content = attachment["data"]
            content = base64.b64decode(content)
            dir_path = temp_dir
            name = attachment["name"]
            full_path = os.path.join(dir_path, name)
            with open(full_path, 'wb') as f:
                f.write(content)
            if os.path.exists(full_path):
                webbrowser.open(full_path) 
class User:
    def __init__(self, username:str, password:str, inbox:list, spam:list, sent:list, work:list):
        if (username != "" and password != ""):
            self.userName = username
            self.password = password
            self.inbox = inbox
            self.spam = spam
            self.sent = sent
            self.work = work
            self.project = []
            self.important = []
            if (user[self.userName].get("last_retrieve") == None):
                self.last_retrieve = 0
                user[self.userName]["last_retrieve"] = 0
            else:
                self.last_retrieve = user[self.userName]["last_retrieve"] 
            global last_retrieve
            last_retrieve = Value('i', self.last_retrieve)
            self.inApp = True
            self.autoloader = None
            print(last_retrieve, self.last_retrieve)
    
    
    def extract_number(self, filename):
        return int(''.join([char for char in filename if char.isdigit()]))
    def load_inbox(self):
      
        dir_path = 'Database/' + self.userName +'/' + 'inbox'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        else:
            files = sorted(os.listdir(dir_path), key=lambda x: self.extract_number(x))
            for file in files:
                if file.endswith(".json"):
                    full_path = os.path.join(dir_path, file)
                    with open(full_path, 'r') as file:
                        data = json.load(file)
                        new_Mail = Mail()
                        new_Mail.set_sender(data["Sender"])
                        new_Mail.set_to(data["To"])
                        new_Mail.set_cc(data["Cc"])
                        new_Mail.set_bcc(data["Bcc"])
                        new_Mail.set_subject(data["Subject"])
                        new_Mail.set_content(data["Content"])
                        new_Mail.set_attachments(data["Attachments"])
                        #print(full_path, data["Read"])
                        new_Mail.read = data["Read"]
                        self.inbox.append(new_Mail)
                    if (new_Mail.read == True):
                        inbox_treeview.insert("", 0, value = (new_Mail.sender, new_Mail.subject), tags = "read")
                    else:
                        inbox_treeview.insert("", 0, value = (new_Mail.sender, new_Mail.subject), tags = ("unread"))               
    def load_sent(self):
        dir_path = 'Database/' + self.userName +'/' + 'sent'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        else:
            files = sorted(os.listdir(dir_path), key=lambda x: self.extract_number(x))
            for file in files:
                if file.endswith(".json"):
                    full_path = os.path.join(dir_path, file)
                    with open(full_path, 'r') as file:
                        data = json.load(file)
                        new_Mail = Mail()
                        new_Mail.set_sender(data["Sender"])
                        new_Mail.set_to(data["To"])
                        new_Mail.set_cc(data["Cc"])
                        new_Mail.set_bcc(data["Bcc"])
                        new_Mail.set_subject(data["Subject"])
                        new_Mail.set_content(data["Content"])
                        new_Mail.set_attachments(data["Attachments"])
                        new_Mail.read = data["Read"]
                        self.sent.append(new_Mail)
                    if (new_Mail.read == True):
                        sent_treeview.insert("", 0, value = (new_Mail.to, new_Mail.subject), tags = "read")
                    else:
                        sent_treeview.insert("", 0, value = (new_Mail.to, new_Mail.subject), tags = ("unread"))
    def load_spam(self):
        dir_path = 'Database/' + self.userName +'/' + 'spam'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        else:
            files = sorted(os.listdir(dir_path),key=lambda x: self.extract_number(x))
            for file in files:
                if file.endswith(".json"):
                    full_path = os.path.join(dir_path, file)
                    with open(full_path, 'r') as file:
                        data = json.load(file)
                        new_Mail = Mail()
                        new_Mail.set_sender(data["Sender"])
                        new_Mail.set_to(data["To"])
                        new_Mail.set_cc(data["Cc"])
                        new_Mail.set_bcc(data["Bcc"])
                        new_Mail.set_subject(data["Subject"])
                        new_Mail.set_content(data["Content"])
                        new_Mail.set_attachments(data["Attachments"])
                        new_Mail.read = data["Read"]
                        self.spam.append(new_Mail)
                    if (new_Mail.read == True):
                        spam_treeview.insert("", 0, value = (new_Mail.sender, new_Mail.subject), tags = "read")
                    else:
                        spam_treeview.insert("", 0, value = (new_Mail.sender, new_Mail.subject), tags = ("unread"))
    def load_work(self):
        dir_path = 'Database/' + self.userName + '/work'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        else:
            files = sorted(os.listdir(dir_path), key=lambda x: self.extract_number(x))
            for file in files:
                if file.endswith(".json"):
                    full_path = os.path.join(dir_path, file)
                    with open(full_path, 'r') as file:
                        data = json.load(file)
                        new_Mail = Mail()
                        new_Mail.set_sender(data["Sender"])
                        new_Mail.set_to(data["To"])
                        new_Mail.set_cc(data["Cc"])
                        new_Mail.set_bcc(data["Bcc"])
                        new_Mail.set_subject(data["Subject"])
                        new_Mail.set_content(data["Content"])
                        new_Mail.set_attachments(data["Attachments"])
                        new_Mail.read = data["Read"]
                        self.work.append(new_Mail)
                    if (new_Mail.read == True):
                        work_treeview.insert("", 0, value = (new_Mail.sender, new_Mail.subject), tags = "read")
                    else:
                        work_treeview.insert("", 0, value = (new_Mail.sender, new_Mail.subject), tags = ("unread"))
    def load_project(self):
        dir_path = 'Database/' + self.userName +'/' + 'project'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        else:
            files = sorted(os.listdir(dir_path), key=lambda x: self.extract_number(x))
            for file in files:
                if file.endswith(".json"):
                    full_path = os.path.join(dir_path, file)
                    with open(full_path, 'r') as file:
                        data = json.load(file)
                        new_Mail = Mail()
                        new_Mail.set_sender(data["Sender"])
                        new_Mail.set_to(data["To"])
                        new_Mail.set_cc(data["Cc"])
                        new_Mail.set_bcc(data["Bcc"])
                        new_Mail.set_subject(data["Subject"])
                        new_Mail.set_content(data["Content"])
                        new_Mail.set_attachments(data["Attachments"])
                        new_Mail.read = data["Read"]
                        self.project.append(new_Mail)
                    if (new_Mail.read == True):
                        project_treeview.insert("", 0, value = (new_Mail.sender, new_Mail.subject), tags = "read")
                    else:
                        project_treeview.insert("", 0, value = (new_Mail.sender, new_Mail.subject), tags = "unread")
    def load_important(self):
        dir_path = 'Database/' + self.userName +'/' + 'important'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        else:
            files = sorted(os.listdir(dir_path), key=lambda x: self.extract_number(x))
            for file in files:
                if file.endswith(".json"):
                    full_path = os.path.join(dir_path, file)
                    with open(full_path, 'r') as file:
                        data = json.load(file)
                        new_Mail = Mail()
                        new_Mail.set_sender(data["Sender"])
                        new_Mail.set_to(data["To"])
                        new_Mail.set_cc(data["Cc"])
                        new_Mail.set_bcc(data["Bcc"])
                        new_Mail.set_subject(data["Subject"])
                        new_Mail.set_content(data["Content"])
                        new_Mail.set_attachments(data["Attachments"])
                        new_Mail.read = data["Read"]
                        self.important.append(new_Mail)
                    if (new_Mail.read == True):
                        important_treeview.insert("", 0, value = (new_Mail.sender, new_Mail.subject), tags = "read")
                    else:
                        important_treeview.insert("", 0, value = (new_Mail.sender, new_Mail.subject), tags = ("unread"))
    def get_sent(self):
        return self.sent
    def get_inbox(self):
        return self.inbox
    def get_spam(self):
        return self.spam
    def get_work(self):
        return self.work
    def get_project(self):
        return self.project
    def get_important(self):
        return self.important
    
    def set_username(self, username:str):
        self.username = username
    def set_password(self, password:str):
        self.password = password
    def get_username(self):
        return self.userName
    def get_password(self): 
        return self.password
    
    def compose_mail(self, reciever_entry: Entry, receiverCC_entry: Entry, bcc_entry:Entry, subject_entry: Entry, message_text):
        new_Mail = Mail()
        new_Mail.set_sender(self.get_username())
        new_Mail.set_to(reciever_entry.get())
        new_Mail.set_cc(receiverCC_entry.get())
        new_Mail.set_bcc(bcc_entry.get())
        new_Mail.set_subject(subject_entry.get())
        new_Mail.set_content(message_text.get("1.0",END))
        new_Mail.set_attachments(list_attachments)
        return new_Mail
       

    def send_mail(self, reciever_entry: Entry, receiverCC_entry: Entry, bcc_entry:Entry, subject_entry: Entry, message_text: Text):
        new_Mail = self.compose_mail(reciever_entry, receiverCC_entry, bcc_entry, subject_entry, message_text)
        new_Mail.send_mail()
        if (new_Mail.sent == True):
            self.sent.append(new_Mail)
            if (new_Mail.read == True):
                sent_treeview.insert("", 0, value = (new_Mail.to, new_Mail.subject))
            else:
                sent_treeview.insert("", 0, value = (new_Mail.to, new_Mail.subject), tags = ("unread"))
            dir_path = 'Database/' + self.userName +'/' + 'sent'
            name = "sent" + str(len(self.sent)) + ".json"
            full_path = os.path.join(dir_path, name)
            last_sent_mail = self.sent[len(self.sent)-1]
            with open(full_path, 'w') as file:
                data = dict()
                data["Sender"] = last_sent_mail.sender
                data["To"] = last_sent_mail.to
                data["Cc"] = last_sent_mail.cc
                data["Bcc"] = last_sent_mail.bcc
                data["Subject"] = last_sent_mail.subject
                data["Content"] = last_sent_mail.content
                data["Attachments"] = last_sent_mail.attachments
                data["Read"] = last_sent_mail.read
                json.dump(data,file,indent=4)
               
    def load_mail_from_server(self, Host, POP3_Port, filter:dict, last_retrieve: Value, loaded_mails):
        # thiết lập kết nối socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # thiết lập kết nối socket với mail server để lấy mail thông qua cổng 3335
       
        client_socket.connect((Host, POP3_Port))

        # nhận dữ liệu từ server
        recv_data = client_socket.recv(1024).decode()
        #print(recv_data)

        # Send USER command
        userCommand = f'USER {self.userName}\r\n'
        client_socket.send(userCommand.encode())
        recv1 = client_socket.recv(1024).decode()
        #print(recv1)

        # Send PASS command
        passCommand = f'PASS {self.password}\r\n'
        client_socket.send(passCommand.encode())
        recv2 = client_socket.recv(1024).decode()
        #print(recv2)

        # Send LIST command to get the list of emails
        listCommand = 'LIST\r\n'
        client_socket.send(listCommand.encode())
        recv3 = client_socket.recv(1024).decode()
        recv3 = recv3.split("\r\n")
        numOfMails = 0
        if (len(recv3) >=4):
            numOfMails = int(recv3[len(recv3)-3].split(" ")[0])
        if (numOfMails > last_retrieve.value):
            for i  in range(last_retrieve.value+1,numOfMails+1):
                command = 'RETR ' + str(i) + '\r\n'
                retrCommand = command
                client_socket.send(retrCommand.encode())
                email_data = ''
                while True:
                    chunk = client_socket.recv(1024)
                    chunk = chunk.decode()
                    email_data += chunk
                    if ('\r\n.\r\n' in email_data):
                        break
                

                loaded_mail = Mail()
                email_data = email_data.split("\r\n")
                
                #load mail with attachments
                if ("boundary=" in email_data[1]):
                    boundary = email_data[1].split("boundary=")[1]
                    boundary = boundary[1:len(boundary)-1]

                    #load header
                    header = list()
                    if "--" + boundary in email_data:
                        header = email_data[1:email_data.index("--" + boundary)]  
                    encoded8bit = False
                    thunderBird = False


                    for line in header:
                        if ("From: " in line):
                            loaded_mail.sender = line.split("From: ")[1]
                            break


                    to_lines = []
                    collecting_to = False
                    for line in header:
                        if line.startswith('To: '):
                            loaded_mail.to = line.split('To: ')[1]
                            collecting_to = True
                        elif line!="" and not line[0].isspace():
                            if collecting_to == True:
                                break
                            #collecting_to = False
                        elif collecting_to:
                            to_lines.append(line.strip()) 
                    loaded_mail.to += ', '.join(to_lines)

                    cc_lines = []
                    collecting_cc = False
                    for line in header:
                        if line.startswith('Cc: '):
                            loaded_mail.cc = line.split('Cc: ')[1]
                            collecting_cc = True
                        elif line!= "" and not line[0].isspace():
                            if collecting_cc == True:
                                break
                            #collecting_cc = False
                        elif collecting_cc:
                            cc_lines.append(line.strip())
                    loaded_mail.cc += ', '.join(cc_lines)

                    bcc_lines = []
                    collecting_bcc = False
                    for line in header:
                        if line.startswith('Bcc: '):
                            loaded_mail.bcc = line.split('Bcc: ')[1]
                            collecting_bcc = True
                        elif line!= "" and not line[0].isspace():
                            if collecting_bcc == True:
                                break
                            #collecting_bcc = False
                        elif collecting_bcc:
                            bcc_lines.append(line.strip())
                    loaded_mail.bcc += ', '.join(bcc_lines)
                    
                    subject_lines =[]
                    collecting_subject = False
                    for line in header:
                        if line.startswith('Subject: '):
                            loaded_mail.subject = line.split('Subject: ')[1]
                            collecting_subject = True
                        elif line!= "" and not line[0].isspace():
                            if collecting_subject == True:
                                break
                            #collecting_subject = False
                        elif collecting_subject:
                            subject_lines.append(line.strip())
                    loaded_mail.subject += ' '.join(subject_lines)
                    if ("=?UTF-8?B?" in loaded_mail.subject):
                        start = loaded_mail.subject.index("=?UTF-8?B?") + 10
                        end = loaded_mail.subject.index("?=")
                        loaded_mail.subject = base64.b64decode(loaded_mail.subject[start:end]).decode('utf-8')

                    for line in header:
                        if (line == "User-Agent: Mozilla Thunderbird"):
                            thunderBird = True

                    #load body
                    if ("--" +boundary in email_data and email_data.index("--" + boundary)+1 < len(email_data)):
                        email_data = email_data[email_data.index("--" + boundary)+1:]
                    for line in email_data:
                        if ("Content-Transfer-Encoding: 8bit" in line):
                            encoded8bit = True
                            break
                    body = str()
                    for line in email_data[3:email_data.index("--" + boundary)]: 
                        body += line 
                    loaded_mail.content = body
                    

                    if (encoded8bit and thunderBird == False):
                        loaded_mail.content = base64.b64decode(loaded_mail.content).decode('utf-8')
                    
                    #load attachment
                    if ("--"+boundary in email_data and email_data.index("--" + boundary)+1 < len(email_data)):
                        email_data = email_data[email_data.index("--" + boundary)+1:]
                
                    while ("--"+boundary in email_data or "--"+boundary+"--" in email_data):
                        attachment = dict()
                        
                        for line in email_data:
                            if ("name=" in line):
                                attachment["name"] = line.split("name=")[1]
                                attachment["name"] = attachment["name"][1:len(attachment["name"])-1]
                                break

                        attachment_data = list()
                        if ("--"+boundary in email_data):
                            attachment_data = email_data[email_data.index("")+1:email_data.index("--" + boundary)]
                        elif ("--"+boundary+"--" in email_data):
                            attachment_data = email_data[email_data.index("")+1:email_data.index("--" + boundary+"--")]
                        attachment["data"] = str()

                        for line in attachment_data:
                            attachment["data"] += line
                        
                        attachment["size"] = len(attachment["data"])
                        loaded_mail.attachments.append(attachment)
                        if ("--"+boundary in email_data and email_data.index("--" + boundary)+1 < len(email_data)):
                            email_data = email_data[email_data.index("--" + boundary)+1:]
                        elif ("--"+boundary+"--" in email_data):
                            break
                #load mail without attachments
                else:
                    if "" in email_data:
                        header = email_data[1:email_data.index("")]
                        email_data = email_data[email_data.index("")+1:]

                        encoded8bit = False
                        thunderBird = False
                        for line in header:
                            if ("From: " in line):
                                loaded_mail.sender = line.split("From: ")[1]
                                break


                        to_lines = []
                        collecting_to = False
                        for line in header:
                            if line.startswith('To: '):
                                loaded_mail.to = line.split('To: ')[1]
                                collecting_to = True
                            elif line!= "" and not line[0].isspace():
                                if collecting_to == True:
                                    break
                                #collecting_to = False
                            elif collecting_to:
                                to_lines.append(line.strip()) 
                        loaded_mail.to += ', '.join(to_lines)

                        cc_lines = []
                        collecting_cc = False
                        for line in header:
                            if line.startswith('Cc: '):
                                loaded_mail.cc = line.split('Cc: ')[1]
                                collecting_cc = True
                            elif line!= "" and not line[0].isspace():
                                if collecting_cc == True:
                                    break
                                #collecting_cc = False
                            elif collecting_cc:
                                cc_lines.append(line.strip())
                        loaded_mail.cc += ', '.join(cc_lines)

                        bcc_lines = []
                        collecting_bcc = False
                        for line in header:
                            if line.startswith('Bcc: '):
                                loaded_mail.bcc = line.split('Bcc: ')[1]
                                collecting_bcc = True
                            elif line!= "" and not line[0].isspace():
                                if collecting_bcc == True:
                                    break
                                #collecting_bcc = False
                            elif collecting_bcc:
                                bcc_lines.append(line.strip())
                        loaded_mail.bcc += ', '.join(bcc_lines)
                    
                        subject_lines =[]
                        collecting_subject = False
                        for line in header:
                            if line.startswith('Subject: '):
                                loaded_mail.subject = line.split('Subject: ')[1]
                                collecting_subject = True
                            elif line!= "" and not line[0].isspace():
                                if collecting_subject == True:
                                    break
                                #collecting_subject = False
                            elif collecting_subject:
                                subject_lines.append(line.strip())
                        loaded_mail.subject += ' '.join(subject_lines)
                        if ("=?UTF-8?B?" in loaded_mail.subject):
                            start = loaded_mail.subject.index("=?UTF-8?B?") + 10
                            end = loaded_mail.subject.index("?=")
                            loaded_mail.subject = base64.b64decode(loaded_mail.subject[start:end]).decode('utf-8')
                        for line in header:
                            if (line == "User-Agent: Mozilla Thunderbird"):
                                thunderBird = True
                            if (line == "Content-Transfer-Encoding: 8bit"):
                                encoded8bit = True

                        
                        body = str()
                        for line in email_data:
                            body += line
                        loaded_mail.content = body
                        if (encoded8bit and thunderBird == False):
                            loaded_mail.content = base64.b64decode(loaded_mail.content).decode('utf-8')

                        
                
                #add to queue
                loaded_mails.put(loaded_mail)
                
        
        last_retrieve.value= max(last_retrieve.value,numOfMails)
        quitCommand = 'QUIT\r\n'
        client_socket.send(quitCommand.encode())
        recv5 = client_socket.recv(1024).decode()
        client_socket.close()
        #print(recv5)
     
    def autoload_mail_from_server(self, Host, POP3_Port, autoload, filter:dict, stop_event, last_retrieve:Value, loaded_mails):
        while (not stop_event.is_set()):
            if (self.userName != "" and self.password != ""):
                self.load_mail_from_server(Host, POP3_Port, filter, last_retrieve, loaded_mails)
                time.sleep(autoload)
                
    def filter_mail(self, mail: Mail, filter:dict):
        sender = filter.get("From",{})
        senderList = sender.keys()
        for curSender in senderList:
            if (curSender.upper() == mail.sender.upper()):
                self.put_mail_in_folder(mail, "project")
                return
        subject = filter.get("Subject",{})
        subjectList = subject.keys()
        
        for curSubject in subjectList:
            if (curSubject.upper() in mail.subject.upper()):
                self.put_mail_in_folder(mail, subject[curSubject])
                return

        content = filter.get("Content",{})
        contentList = content.keys()
       
        for curContent in contentList:
            if (curContent.upper() in mail.content.upper()):
                self.put_mail_in_folder(mail, content[curContent])
                return
        self.put_mail_in_folder(mail, "inbox")   
    
    def put_mail_in_folder(self, mail:Mail, folder:str):
        dir_path = 'Database/' + self.userName +'/' + folder +'/'
        name = str()
        if (folder == "inbox"):
            name = "inbox" + str(len(self.inbox)+1) + ".json"
            self.inbox.append(mail)
            if (mail.read == True):
                inbox_treeview.insert("", 0, value = (mail.sender, mail.subject), tags = ("read"))
            else:
                inbox_treeview.insert("", 0, value = (mail.sender, mail.subject), tags = ("unread"))
           
        elif (folder == "spam"):
            name = "spam" + str(len(self.spam)+1) + ".json"
            self.spam.append(mail)
            if (mail.read == True):
                spam_treeview.insert("", 0, value = (mail.sender, mail.subject), tags = ("read"))
            else:
                spam_treeview.insert("", 0, value = (mail.sender, mail.subject), tags = ("unread"))
          
        elif (folder == "work"):
            name = "work" + str(len(self.work)+1) + ".json"
            self.work.append(mail)
            if (mail.read == True):
                work_treeview.insert("", 0, value = (mail.sender, mail.subject), tags = ("read"))
            else:
                work_treeview.insert("", 0, value = (mail.sender, mail.subject), tags = ("unread"))
          
        elif (folder == "important"):
            name = "important" + str(len(self.important) + 1) + ".json"
            self.important.append(mail)
            if (mail.read == True):
                important_treeview.insert("", 0, value = (mail.sender, mail.subject), tags = ("read"))
            else:
                important_treeview.insert("", 0, value = (mail.sender, mail.subject), tags = ("unread"))
         
        elif (folder == "project"):
            name = "project" + str(len(self.project) + 1) + ".json"
            self.project.append(mail)
            if (mail.read == True):
                project_treeview.insert("", 0, value = (mail.sender, mail.subject), tags = ("read"))
            else:
                project_treeview.insert("", 0, value = (mail.sender, mail.subject), tags = ("unread"))
           
        full_path = os.path.join(dir_path, name)
        with open(full_path, 'w') as file:
            data = dict()
            data["Sender"] = mail.sender
            data["To"] = mail.to
            data["Cc"] = mail.cc
            data["Bcc"] = mail.bcc
            data["Subject"] = mail.subject
            data["Content"] = mail.content
            data["Attachments"] = mail.attachments
            data["Read"] = mail.read
            json.dump(data,file,indent=4)       

def setUpSystem():
    with open("Server/config.json", 'r') as file:
        data = json.load(file)
        global general_data
        general_data = data.get('General', {})
        global Host, SMTP_Port, POP3_Port, user,autoload
        Host = general_data.get('ServerName')
        
        SMTP_Port = general_data.get('SMTP_PORT')
        
        POP3_Port = general_data.get('POP3_PORT')
       
        user = data.get('User',{})
       
        autoload = data['Autoload']
       
        global filter
        filter = data.get('Filter', {}) 

def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not '@' in email:
        return False
    return bool(re.match(pattern, email))

def login(username_entry: Entry, password_entry: Entry):
    userName = username_entry.get()
    password = password_entry.get()
   
    inbox_treeview.delete(*inbox_treeview.get_children())
    sent_treeview.delete(*sent_treeview.get_children())
    important_treeview.delete(*important_treeview.get_children())
    work_treeview.delete(*work_treeview.get_children())
    project_treeview.delete(*project_treeview.get_children())
    spam_treeview.delete(*spam_treeview.get_children())


    if user.get(userName)!=None and user.get(userName)['password'] == password:
        global curUser
        curUser = User(userName, password, [], [], [], [])
        curUser.load_sent()
        curUser.load_inbox()
        curUser.load_spam()
        curUser.load_work() 
        curUser.load_project()
        curUser.load_important()
        curUser.inApp = True
        curUser.autoloader = Process(target = curUser.autoload_mail_from_server, args=(Host, POP3_Port, autoload, filter, stop_event, last_retrieve, loaded_mails))
        curUser.autoloader.start()
        root.after(autoload*1000, check_mail, curUser)
        login_frame.grid_forget()
        login_bar.grid_forget
        tool_frame.grid(row=0, column=0, padx=28, pady=25, sticky=NW)
        compose_mail_page()
    else:
        messagebox.showerror("Log in", "wrong username or password")             

def signup(username_entry: Entry, password_entry: Entry):
    userName = username_entry.get()
    password = password_entry.get()

    inbox_treeview.delete(*inbox_treeview.get_children())
    sent_treeview.delete(*sent_treeview.get_children())
    important_treeview.delete(*important_treeview.get_children())
    work_treeview.delete(*work_treeview.get_children())
    project_treeview.delete(*project_treeview.get_children())
    spam_treeview.delete(*spam_treeview.get_children())

    if user.get(userName) == None and is_valid_email(userName) and len(password) >= 8:
        user[userName] ={'password':password}
        global curUser
        curUser = User(userName, password, [], [], [], [])
        curUser.load_sent()
        curUser.load_inbox()
        curUser.load_spam()
        curUser.load_work()
        curUser.load_project()
        curUser.load_important()  
        curUser.inApp = True  
        curUser.autoloader = Process(target = curUser.autoload_mail_from_server, args=(Host, POP3_Port, autoload, filter, stop_event, last_retrieve, loaded_mails))
        curUser.autoloader.start()
        root.after(autoload*1000, check_mail, curUser)
        signup_frame.grid_forget()
        signup_bar.grid_forget
        tool_frame.grid(row=0, column=0, padx=28, pady=25, sticky=NW)
        compose_mail_page()
    elif is_valid_email(userName) == False:
        messagebox.showerror("Sign up", "Invalid username!")
    elif user.get(userName) != None:
        messagebox.showerror("Sign up", "Username already exists.")
        #Label(signup_bar, text="Username already exists!", bg="white", fg= "red").grid(row=2, column=2, padx=5, pady=5, sticky=W)
    else:
        messagebox.showerror("Sign up", "Password must have at least 8 characters.")
        # Label(signup_bar, text="Password must have at least 8 characters", bg="white", fg= "red").grid(row=2, column=2, padx=5, pady=5, sticky=W)

def logout():
    curUser.inApp = False
    curUser.userName = ""
    curUser.password = ""
    curUser.inbox.clear()
    curUser.spam.clear()
    curUser.sent.clear()
    curUser.work.clear()
    curUser.project.clear()
    curUser.important.clear()
    
    stop_event.set()
    curUser.autoloader.join()
    curUser.last_retrieve = last_retrieve.value
    user[curUser.userName] = {"password":curUser.password}
    user[curUser.userName]["last_retrieve"] = curUser.last_retrieve

    data = dict()
    data["General"] = {"ServerName":Host}
    data["General"]["SMTP_PORT"] = SMTP_Port
    data["General"]["POP3_PORT"] = POP3_Port
    data["User"] = user  
    data["Autoload"] = autoload
    data["Filter"] = filter
    with open('Server/config.json', 'w') as file:
          json.dump(data,file,indent=4)
    login_page()

def exitApp():
    if (curUser != None):
        curUser.inApp = False
        stop_event.set()
        curUser.autoloader.join()
        curUser.last_retrieve = last_retrieve.value
        #user[curUser.userName]["last_retrieve"] = user[curUser.userName]["last_retrieve"].value
        user[curUser.userName]["last_retrieve"] = curUser.last_retrieve
    data = dict()
    data["General"] = {"ServerName":Host}
    data["General"]["SMTP_PORT"] = SMTP_Port
    data["General"]["POP3_PORT"] = POP3_Port
    data["User"] = user  
    data["Autoload"] = autoload
    data["Filter"] = filter
    with open('Server/config.json', 'w') as file:
          json.dump(data,file,indent=4)
    exit()

def open_files():
    global file_paths
    file_paths = askopenfilenames()
    for file_path in file_paths:
        if (os.path.getsize(file_path) > 3*1024*1024):
            messagebox.showerror("Error", os.path.basename(file_path) +  " is too large")
            continue
        attached_file = open(file_path, "rb")
        attached_data = attached_file.read()  # ascii
        attached_data_base64 = base64.b64encode(attached_data).decode()
        file = dict()
        file["name"] = os.path.basename(file_path)
        file["size"] = len(attached_data_base64)
        file["data"] = attached_data_base64
        list_attachments.append(file)
        global button
        button = Button(text = os.path.basename(file_path), command = lambda cur_file_path = file_path:webbrowser.open(cur_file_path))
        panedwindow2.add(button)

def clear_all_files():
    list_attachments.clear()
    for pane_id in panedwindow2.panes():
        widget = root.nametowidget(pane_id)
        widget.destroy()

def check_mail(curUser:User):
    while not loaded_mails.empty():
            loaded_mail = loaded_mails.get()
            curUser.filter_mail(loaded_mail, filter)
    if (curUser.inApp == True):
        root.after(autoload*1000, check_mail, curUser)

def create_tool_bar_frame():
    global tool_frame, picture, left_bar, inboxes, compose, sent, importance, work, project, spam, logoutB
    tool_frame = Frame(root, width=100, height=350)

    image = PhotoImage(file=r"Images/email.png")
    original_image = image.subsample(10,10)  # resize image using subsample
    picture = Label(tool_frame, image=original_image)
    picture.image = original_image
    picture.grid(row=1, column=0, padx=5, pady=5)

    left_bar = Frame(tool_frame, width=100, height=300,bg="white")
    inboxes=Button(left_bar, text="Inboxes",bg="white",width=15, command =inbox_page)
    compose=Button(left_bar, text="Compose",bg="white",width=15, command = compose_mail_page)
    sent=Button(left_bar, text="Sent",bg="white",width=15, command = sent_page)
    importance=Button(left_bar, text="Importance",bg="white",width=15, command = important_page)
    work=Button(left_bar, text="Work",bg="white",width=15, command = work_page)
    project=Button(left_bar, text="Project",bg="white",width=15, command = project_page)
    spam=Button(left_bar, text="Spam",bg="white",width=15, command = spam_page)
    logoutB=Button(left_bar, text="Log out",bg="light salmon",width=15, command = logout)

    inboxes.grid(row=2,column=0,padx=5,pady=5,sticky=W)
    compose.grid(row=3,column=0,padx=5,pady=5,sticky=W)
    sent.grid(row=4,column=0,padx=5,pady=5,sticky=W)
    importance.grid(row=5,column=0,padx=5,pady=5,sticky=W)
    work.grid(row=6,column=0,padx=5,pady=5,sticky=W)
    project.grid(row=7,column=0,padx=5,pady=5,sticky=W)
    spam.grid(row=8,column=0,padx=5,pady=5,sticky=W)
    logoutB.grid(row=9,column=0,padx=5,pady=5,sticky=W)

    left_bar.grid(row=2, column=0, padx=5, pady=5)

def create_compose_frame():
    global compose_frame, compose_bar, from_bar, to_bar, cc_bar, bcc_bar, subject_bar, your_mail, scrolled, panedwindow2, clear_all, send_button
    compose_frame = Frame(root, width=470, height=350)

    compose_bar = Frame(compose_frame, width=470,height=360, bg="white")

    Label(compose_frame, text="Compose email", font=("Arial Bold",11)).grid(row=1, column=0, padx=5, pady=5)

    Label(compose_bar, text="From", bg="white").grid(row=1, column=1, padx=5, pady=5, sticky=W)
    from_bar = Label(compose_bar, width=51, bd=2)
    from_bar.grid(row=1, column=2, padx=5, pady=5)

    Label(compose_bar, text="To", bg="white").grid(row=2, column=1, padx=5, pady=5, sticky=W)
    to_bar = Entry(compose_bar, width=60, bd=2)
    to_bar.grid(row=2, column=2, padx=5, pady=5)

    Label(compose_bar, text="Cc", bg="white").grid(row=3, column=1, padx=5, pady=5, sticky=W)
    cc_bar = Entry(compose_bar, width=60, bd=2)
    cc_bar.grid(row=3, column=2, padx=5, pady=5)

    Label(compose_bar, text="Bcc", bg="white").grid(row=4, column=1, padx=5, pady=5, sticky=W)
    bcc_bar = Entry(compose_bar, width=60, bd=2)
    bcc_bar.grid(row=4, column=2, padx=5, pady=5)

    Label(compose_bar, text="Subject", bg="white").grid(row=5, column=1, padx=5, pady=5, sticky=W)
    subject_bar = Entry(compose_bar, width=60, bd=2)
    subject_bar.grid(row=5, column=2, padx=5, pady=5)

    scrolled=Scrollbar(compose_bar, orient="vertical")
    scrolled.grid(row=6, column=3, padx=5, pady=5, sticky=W)

    Label(compose_bar, text="Compose", bg="white").grid(row=6, column=1, padx=5, pady=5, sticky=NW)
    your_mail=Text(compose_bar, width=45, height=10, bd=2, yscrollcommand=scrolled.set)
    your_mail.grid(row=6, column=2, padx=5, pady=5)

    attachedFile_button = Button(compose_bar, text="Attach file", bg="light cyan", command = open_files)
    attachedFile_button.grid(row=7, column=2,sticky=W,pady=5)

    clear_all = Button(compose_bar, text="Clear", bg="light cyan", command = lambda: clear_all_files())
    clear_all.grid(row=7, column=3, pady=5, sticky = W)
   
    canvas = Canvas(compose_bar,width=300, height=25)
    canvas.grid(row=7, column=2, sticky=E)

    # Tạo một thanh cuộn
    scrollbar = Scrollbar(compose_bar, orient="horizontal", command=canvas.xview)
    scrollbar.grid(row=8, column=2, padx=5, pady=5,sticky=S)

    # Thiết lập Canvas để sử dụng thanh cuộn
    canvas.configure(xscrollcommand=scrollbar.set)

    # Đặt Canvas làm khung con của thanh cuộn
    # scrollbar.config(command=scroll_frame)

    # Tạo một khung con bên trong Canvas để chứa nội dung
    panedwindow2 = ttk.Panedwindow(canvas, orient=tk.HORIZONTAL)
    panedwindow2.grid(row=7,column = 2)
    # Tạo một Canvas

    # Đặt khung con vào Canvas
    canvas.create_window((0, 0), window=panedwindow2, anchor="nw")

    # Thiết lập khung cuộn để cuộn theo nội dung của Canvas
    def configure_canvas(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    panedwindow2.bind("<Configure>", configure_canvas)
    #
    send_button = Button(compose_bar, text="Send mail", bg="pale turquoise", command = lambda:curUser.send_mail(to_bar, cc_bar, bcc_bar, subject_bar, your_mail))
    send_button.grid(row=8, column=2, sticky = W, pady=5)

    compose_bar.grid(row=2, column=0, padx=5, pady=5)

def on_enter_inbox(event):
    selected_mail = inbox_treeview.selection()[0]  # Get the selected item
    selected_mail_index= inbox_treeview.index(selected_mail)
    size = len(curUser.inbox)
    selected_mail_index = size - selected_mail_index-1
    if (curUser.inbox[selected_mail_index].read == False):
        curUser.inbox[selected_mail_index].read = True
        full_path = 'Database/' + curUser.userName +'/inbox/inbox' + str(selected_mail_index+1) + ".json"
        with open(full_path, 'w') as file:
            print(full_path)
            data = dict()
            data["Sender"] = curUser.inbox[selected_mail_index].sender
            data["To"] = curUser.inbox[selected_mail_index].to
            data["Cc"] = curUser.inbox[selected_mail_index].cc
            data["Bcc"] = curUser.inbox[selected_mail_index].bcc
            data["Subject"] = curUser.inbox[selected_mail_index].subject
            data["Content"] = curUser.inbox[selected_mail_index].content
            data["Attachments"] = curUser.inbox[selected_mail_index].attachments
            data["Read"] = curUser.inbox[selected_mail_index].read
            json.dump(data,file,indent=4)
        inbox_treeview.item(selected_mail, tags = ("read"))

    folder_name.configure(text = "Inboxes")
    from_bar_read.configure(text = curUser.inbox[selected_mail_index].sender)
    to_bar_read.configure(text = curUser.inbox[selected_mail_index].to)
    cc_bar_read.configure(text = curUser.inbox[selected_mail_index].cc)
    subject_bar_read.configure(text = curUser.inbox[selected_mail_index].subject)
    your_mail_read.configure(state = NORMAL)
    your_mail_read.delete("1.0", END)
    your_mail_read.insert(END, curUser.inbox[selected_mail_index].content)
    your_mail_read.configure(state = DISABLED)
    files = curUser.inbox[selected_mail_index].attachments
    for pane_id in panedwindow.panes():
        widget = root.nametowidget(pane_id)
        widget.destroy()
    for i in range(0,len(files)):
        file = files[i]
        global button 
        button = Button(receive_bar_read, text = file["name"], bg = "white", command = lambda fileindex = i, s=selected_mail_index: curUser.inbox[s].show_attachment(fileindex))
        panedwindow.add(button)
    
    read_mail_page()

def create_inbox_frame():
    global inbox_frame, inbox_outer, inbox_treeview
    inbox_frame = Frame(root, width=550, height=420)
    inbox_outer = Frame(inbox_frame, width=550, height=430, bg = "white")
    Label(inbox_frame, text="Inboxes", font=("Arial Bold",11)).grid(row=1, column=0, padx=5, pady=5)
    inbox_treeview = ttk.Treeview(inbox_outer, columns=("From", "Subject"), show="headings", height=15)
    inbox_treeview.tag_configure("unread", font = ("Arial", 10, "bold") )
    inbox_treeview.tag_configure("read", font = ("Arial", 10))
    inbox_treeview.heading("From", text="From:")
    inbox_treeview.heading("Subject", text="Subject:")

    inbox_treeview.column("From", width=225)
    inbox_treeview.column("Subject", width=225)
    inbox_treeview.bind("<Return>", on_enter_inbox)

    inbox_treeview.grid(row = 2, column = 0)
    
    inbox_outer.grid(row=2, column=0, padx=5, pady=5)
def on_enter_sent(event):
    selected_mail = sent_treeview.selection()[0]  # Get the selected item
    selected_mail_index= sent_treeview.index(selected_mail)
    size = len(curUser.sent)
    selected_mail_index = size - selected_mail_index-1
    folder_name.configure(text = "Sent")
    if (curUser.sent[selected_mail_index].read == False):
        curUser.sent[selected_mail_index].read = True
        full_path = 'Database/' + curUser.userName +'/sent/sent' + str(selected_mail_index+1) + ".json"
        with open(full_path, 'w') as file:
            data = dict()
            data["Sender"] = curUser.sent[selected_mail_index].sender
            data["To"] = curUser.sent[selected_mail_index].to
            data["Cc"] = curUser.sent[selected_mail_index].cc
            data["Bcc"] = curUser.sent[selected_mail_index].bcc
            data["Subject"] = curUser.sent[selected_mail_index].subject
            data["Content"] = curUser.sent[selected_mail_index].content
            data["Attachments"] = curUser.sent[selected_mail_index].attachments
            data["Read"] = curUser.sent[selected_mail_index].read
            json.dump(data,file,indent=4)
        sent_treeview.item(selected_mail, tags = ("read"))
    from_bar_read.configure(text = curUser.sent[selected_mail_index].sender)
    to_bar_read.configure(text = curUser.sent[selected_mail_index].to)
    cc_bar_read.configure(text = curUser.sent[selected_mail_index].cc)
    subject_bar_read.configure(text = curUser.sent[selected_mail_index].subject)
    your_mail_read.configure(state = NORMAL)
    your_mail_read.delete("1.0", END)
    your_mail_read.insert(END, curUser.sent[selected_mail_index].content)
    your_mail_read.configure(state = DISABLED)
    files = curUser.sent[selected_mail_index].attachments
    for pane_id in panedwindow.panes():
        widget = root.nametowidget(pane_id)
        widget.destroy()
    for i in range(0,len(files)):
        file = files[i]
        global button 
        button = Button(receive_bar_read, text = file["name"], bg = "white", command = lambda fileindex = i, s=selected_mail_index: curUser.sent[s].show_attachment(fileindex))
        panedwindow.add(button)
   
    read_mail_page()
def create_sent_frame():
    global sent_frame, sent_outer, sent_treeview
    sent_frame = Frame(root, width=550, height=420)
    sent_outer = Frame(sent_frame, width=550, height=430, bg = "white")
    Label(sent_frame, text="Sent", font=("Arial Bold",11)).grid(row=1, column=0, padx=5, pady=5)
    sent_treeview = ttk.Treeview(sent_outer, columns=("To", "Subject"), show="headings", height=15)
    sent_treeview.tag_configure("unread", font = ("Arial", 10, "bold") )
    sent_treeview.tag_configure("read", font = ("Arial", 10))
    sent_treeview.heading("To", text="To:")
    sent_treeview.heading("Subject", text="Subject:")

    sent_treeview.column("To", width=225)
    sent_treeview.column("Subject", width=225)
    sent_treeview.bind("<Return>", on_enter_sent)

    sent_treeview.grid(row = 2, column = 0)
    
    sent_outer.grid(row=2, column=0, padx=5, pady=5)
def on_enter_important(event):
    selected_mail = important_treeview.selection()[0]  # Get the selected item
    selected_mail_index= important_treeview.index(selected_mail)
    size = len(curUser.important)
    selected_mail_index = size - selected_mail_index-1
    folder_name.configure(text = "Importance")
    from_bar_read.configure(text = curUser.important[selected_mail_index].sender)
    if (curUser.important[selected_mail_index].read == False):
        curUser.important[selected_mail_index].read = True
        full_path = 'Database/' + curUser.userName +'/important/important' + str(selected_mail_index+1) + ".json"
        with open(full_path, 'w') as file:
            data = dict()
            data["Sender"] = curUser.important[selected_mail_index].sender
            data["To"] = curUser.important[selected_mail_index].to
            data["Cc"] = curUser.important[selected_mail_index].cc
            data["Bcc"] = curUser.important[selected_mail_index].bcc
            data["Subject"] = curUser.important[selected_mail_index].subject
            data["Content"] = curUser.important[selected_mail_index].content
            data["Attachments"] = curUser.important[selected_mail_index].attachments
            data["Read"] = curUser.important[selected_mail_index].read
            json.dump(data,file,indent=4)
        important_treeview.item(selected_mail, tags = ("read"))
    to_bar_read.configure(text = curUser.important[selected_mail_index].to)
    cc_bar_read.configure(text = curUser.important[selected_mail_index].cc)
    subject_bar_read.configure(text = curUser.important[selected_mail_index].subject)
    your_mail_read.configure(state = NORMAL)
    your_mail_read.delete("1.0", END)
    your_mail_read.insert(END, curUser.important[selected_mail_index].content)
    your_mail_read.configure(state = DISABLED)
    files = curUser.important[selected_mail_index].attachments
    for pane_id in panedwindow.panes():
        widget = root.nametowidget(pane_id)
        widget.destroy()
    for i in range(0,len(files)):
        file = files[i]
        global button 
        button = Button(receive_bar_read, text = file["name"], bg = "white", command = lambda fileindex = i, s=selected_mail_index: curUser.important[s].show_attachment(fileindex))
    read_mail_page()
def create_important_frame():
    global important_frame, important_outer, important_treeview
    important_frame = Frame(root, width=550, height=420)
    important_outer = Frame(important_frame, width=550, height=430, bg = "white")
    Label(important_frame, text="Importance", font=("Arial Bold",11)).grid(row=1, column=0, padx=5, pady=5)
    important_treeview = ttk.Treeview(important_outer, columns=("From", "Subject"), show="headings", height=15)
    important_treeview.tag_configure("unread", font = ("Arial", 10, "bold") )
    important_treeview.tag_configure("read", font = ("Arial", 10))
    important_treeview.heading("From", text="From:")
    important_treeview.heading("Subject", text="Subject:")

    important_treeview.column("From", width=225)
    important_treeview.column("Subject", width=225)
    important_treeview.bind("<Return>", on_enter_important)
    important_treeview.grid(row = 2, column = 0)
    important_outer.grid(row=2, column=0, padx=5, pady=5)
def on_enter_work(event):
    selected_mail = work_treeview.selection()[0]  # Get the selected item
    selected_mail_index= work_treeview.index(selected_mail)
    size = len(curUser.work)
    selected_mail_index = size - selected_mail_index-1
    folder_name.configure(text = "Work")
    from_bar_read.configure(text = curUser.work[selected_mail_index].sender)
    if (curUser.work[selected_mail_index].read == False):
        curUser.work[selected_mail_index].read = True
        full_path = 'Database/' + curUser.userName +'/work/work' + str(selected_mail_index+1) + ".json"
        with open(full_path, 'w') as file:
            data = dict()
            data["Sender"] = curUser.work[selected_mail_index].sender
            data["To"] = curUser.work[selected_mail_index].to
            data["Cc"] = curUser.work[selected_mail_index].cc
            data["Bcc"] = curUser.work[selected_mail_index].bcc
            data["Subject"] = curUser.work[selected_mail_index].subject
            data["Content"] = curUser.work[selected_mail_index].content
            data["Attachments"] = curUser.work[selected_mail_index].attachments
            data["Read"] = curUser.work[selected_mail_index].read
            json.dump(data,file,indent=4)
        work_treeview.item(selected_mail, tags = ("read"))
    to_bar_read.configure(text = curUser.work[selected_mail_index].to)
    cc_bar_read.configure(text = curUser.work[selected_mail_index].cc)
    subject_bar_read.configure(text = curUser.work[selected_mail_index].subject)
    your_mail_read.configure(state = NORMAL)
    your_mail_read.delete("1.0", END)
    your_mail_read.insert(END, curUser.work[selected_mail_index].content)
    your_mail_read.configure(state = DISABLED)
    files = curUser.work[selected_mail_index].attachments
    for pane_id in panedwindow.panes():
        widget = root.nametowidget(pane_id)
        widget.destroy()
    for i in range(0,len(files)):
        file = files[i]
        global button 
        button = Button(receive_bar_read, text = file["name"], bg = "white", command = lambda fileindex = i, s=selected_mail_index: curUser.work[s].show_attachment(fileindex))
    read_mail_page()
def create_work_frame():
    global work_frame, work_outer, work_treeview
    work_frame = Frame(root, width=550, height=420)
    work_outer = Frame(work_frame, width=550, height=430, bg = "white")
    Label(work_frame, text="Work", font=("Arial Bold",11)).grid(row=1, column=0, padx=5, pady=5)
    work_treeview = ttk.Treeview(work_outer, columns=("From", "Subject"), show="headings", height=15)
    work_treeview.tag_configure("unread", font = ("Arial", 10, "bold") )
    work_treeview.tag_configure("read", font = ("Arial", 10))
    work_treeview.heading("From", text="From:")
    work_treeview.heading("Subject", text="Subject:")

    work_treeview.column("From", width=225)
    work_treeview.column("Subject", width=225)
    work_treeview.bind("<Return>", on_enter_work)
    work_treeview.grid(row = 2, column = 0)
    work_outer.grid(row=2, column=0, padx=5, pady=5)
def on_enter_project(event):
    selected_mail = project_treeview.selection()[0]  # Get the selected item
    selected_mail_index= project_treeview.index(selected_mail)
    size = len(curUser.project)
    selected_mail_index = size - selected_mail_index-1
    folder_name.configure(text = "Project")
    from_bar_read.configure(text = curUser.project[selected_mail_index].sender)
    if (curUser.project[selected_mail_index].read == False):
        curUser.project[selected_mail_index].read = True
        full_path = 'Database/' + curUser.userName +'/project/project' + str(selected_mail_index+1) + ".json"
        with open(full_path, 'w') as file:
            data = dict()
            data["Sender"] = curUser.project[selected_mail_index].sender
            data["To"] = curUser.project[selected_mail_index].to
            data["Cc"] = curUser.project[selected_mail_index].cc
            data["Bcc"] = curUser.project[selected_mail_index].bcc
            data["Subject"] = curUser.project[selected_mail_index].subject
            data["Content"] = curUser.project[selected_mail_index].content
            data["Attachments"] = curUser.project[selected_mail_index].attachments
            data["Read"] = curUser.project[selected_mail_index].read
            json.dump(data,file,indent=4)
        project_treeview.item(selected_mail, tags = ("read"))
    to_bar_read.configure(text = curUser.project[selected_mail_index].to)
    cc_bar_read.configure(text = curUser.project[selected_mail_index].cc)
    subject_bar_read.configure(text = curUser.project[selected_mail_index].subject)
    your_mail_read.configure(state = NORMAL)
    your_mail_read.delete("1.0", END)
    your_mail_read.insert(END, curUser.project[selected_mail_index].content)
    your_mail_read.configure(state = DISABLED)
    files = curUser.project[selected_mail_index].attachments
    for pane_id in panedwindow.panes():
        widget = root.nametowidget(pane_id)
        widget.destroy()
    for i in range(0,len(files)):
        file = files[i]
        global button 
        button = Button(receive_bar_read, text = file["name"], bg = "white", command = lambda fileindex = i, s=selected_mail_index: curUser.project[s].show_attachment(fileindex))
    read_mail_page()
def create_project_frame():
    global project_frame, project_outer, project_treeview
    project_frame = Frame(root, width=550, height=420)
    project_outer = Frame(project_frame, width=550, height=430, bg = "white")
    Label(project_frame, text="Project", font=("Arial Bold",11)).grid(row=1, column=0, padx=5, pady=5)
    project_treeview = ttk.Treeview(project_outer, columns=("From", "Subject"), show="headings", height=15)
    project_treeview.tag_configure("unread", font = ("Arial", 10, "bold") )
    project_treeview.tag_configure("read", font = ("Arial", 10))
    project_treeview.heading("From", text="From:")
    project_treeview.heading("Subject", text="Subject:")

    project_treeview.column("From", width=225)
    project_treeview.column("Subject", width=225)
    project_treeview.bind("<Return>", on_enter_project)
    project_treeview.grid(row = 2, column = 0)
    project_outer.grid(row=2, column=0, padx=5, pady=5)
def on_enter_spam(event):
    selected_mail = spam_treeview.selection()[0]  # Get the selected item
    selected_mail_index= spam_treeview.index(selected_mail)
    size = len(curUser.spam)
    selected_mail_index = size - selected_mail_index-1
    folder_name.configure(text = "Spam")
    from_bar_read.configure(text = curUser.spam[selected_mail_index].sender)
    if (curUser.spam[selected_mail_index].read == False):
        curUser.spam[selected_mail_index].read = True
        full_path = 'Database/' + curUser.userName +'/spam/spam' + str(selected_mail_index+1) + ".json"
        with open(full_path, 'w') as file:
            data = dict()
            data["Sender"] = curUser.spam[selected_mail_index].sender
            data["To"] = curUser.spam[selected_mail_index].to
            data["Cc"] = curUser.spam[selected_mail_index].cc
            data["Bcc"] = curUser.spam[selected_mail_index].bcc
            data["Subject"] = curUser.spam[selected_mail_index].subject
            data["Content"] = curUser.spam[selected_mail_index].content
            data["Attachments"] = curUser.spam[selected_mail_index].attachments
            data["Read"] = curUser.spam[selected_mail_index].read
            json.dump(data,file,indent=4)
        spam_treeview.item(selected_mail, tags = ("read"))
    to_bar_read.configure(text = curUser.spam[selected_mail_index].to)
    cc_bar_read.configure(text = curUser.spam[selected_mail_index].cc)
    subject_bar_read.configure(text = curUser.spam[selected_mail_index].subject)
    your_mail_read.configure(state = NORMAL)
    your_mail_read.delete("1.0", END)
    your_mail_read.insert(END, curUser.spam[selected_mail_index].content)
    your_mail_read.configure(state = DISABLED)
    files = curUser.spam[selected_mail_index].attachments
    for pane_id in panedwindow.panes():
        widget = root.nametowidget(pane_id)
        widget.destroy()
    for i in range(0,len(files)):
        file = files[i]
        global button 
        button = Button(receive_bar_read, text = file["name"], bg = "white", command = lambda fileindex = i, s=selected_mail_index: curUser.spam[s].show_attachment(fileindex))
    read_mail_page()
def create_spam_frame():
    global spam_frame, spam_outer, spam_treeview
    spam_frame = Frame(root, width=550, height=420)
    spam_outer = Frame(spam_frame, width=550, height=430, bg = "white")
    Label(spam_frame, text="Spam", font=("Arial Bold",11)).grid(row=1, column=0, padx=5, pady=5)
    spam_treeview = ttk.Treeview(spam_outer, columns=("From", "Subject"), show="headings", height=15)
    spam_treeview.tag_configure("unread", font = ("Arial", 10, "bold") )
    spam_treeview.tag_configure("read", font = ("Arial", 10))
    spam_treeview.heading("From", text="From:")
    spam_treeview.heading("Subject", text="Subject:")

    spam_treeview.column("From", width=225)
    spam_treeview.column("Subject", width=225)
    spam_treeview.bind("<Return>", on_enter_spam)
    spam_treeview.grid(row = 2, column = 0)
    spam_outer.grid(row=2, column=0, padx=5, pady=5)
def create_read_mail_frame():
    global receive_frame, receive_bar_read, from_bar_read, to_bar_read, cc_bar_read, subject_bar_read, your_mail_read, scrolled_read, back_button, folder_name, panedwindow
    # Create Frame widget
    receive_frame = Frame(root, width=470, height=350)
    #receive_frame.grid(row=0, column=1, padx=0, pady=25, sticky = NW)

    # Create frame within compose_frame
    receive_bar_read = Frame(receive_frame, width=470,height=360, bg="white")
    receive_bar_read.grid(row=2, column=0, padx=5, pady=5)

    folder_name = Label(receive_frame, text="", font=("Arial Bold",11))
    folder_name.grid(row=1, column=0, padx=5, pady=5)

    # Name label and entry widgets
    Label(receive_bar_read, text="From", bg="white").grid(row=1, column=1, padx=5, pady=5, sticky=W)
    from_bar_read = Label(receive_bar_read, text = "", width=51, bd=2)
    from_bar_read.grid(row=1, column=2, padx=5, pady=5)

    Label(receive_bar_read, text="To", bg="white").grid(row=2, column=1, padx=5, pady=5, sticky=W)
    to_bar_read = Label(receive_bar_read, text = "", width=51, bd=2)
    to_bar_read.grid(row=2, column=2, padx=5, pady=5)

    Label(receive_bar_read, text="Cc", bg="white").grid(row=3, column=1, padx=5, pady=5, sticky=W)
    cc_bar_read = Label(receive_bar_read, text = "", width=51, bd=2)
    cc_bar_read.grid(row=3, column=2, padx=5, pady=5)

    Label(receive_bar_read, text="Subject", bg="white").grid(row=5, column=1, padx=5, pady=5, sticky=W)
    subject_bar_read = Label(receive_bar_read, text = "", width=51, bd=2)
    subject_bar_read.grid(row=5, column=2, padx=5, pady=5)

    scrolled_read=Scrollbar(receive_bar_read, orient="vertical")
    scrolled_read.grid(row=6, column=3, padx=5, pady=5, sticky=W)

    Label(receive_bar_read, text="Content", bg="white").grid(row=6, column=1, padx=5, pady=5, sticky=NW)
    your_mail_read=Text(receive_bar_read, width=45, height=10, bd=2, yscrollcommand=scrolled.set)
    your_mail_read.grid(row=6, column=2, padx=5, pady=5)

    attachedFile_button = Label(receive_bar_read, text="Attach file", bg="pale turquoise",bd=5)
    attachedFile_button.grid(row=7, column=2,sticky=W,pady=5)
    canvas = Canvas(receive_bar_read,width=300, height=25)
    canvas.grid(row=7, column=2, sticky=E)

    # Tạo một thanh cuộn
    scrollbar = Scrollbar(receive_bar_read, orient="horizontal", command=canvas.xview)
    scrollbar.grid(row=8, column=2, padx=5, pady=5,sticky=S)

    # Thiết lập Canvas để sử dụng thanh cuộn
    canvas.configure(xscrollcommand=scrollbar.set)
    panedwindow = ttk.Panedwindow(receive_bar_read, orient=tk.HORIZONTAL)
    panedwindow.grid(row=7,column = 2)

    # Đặt khung con vào Canvas
    canvas.create_window((0, 0), window=panedwindow, anchor="nw")

    # Thiết lập khung cuộn để cuộn theo nội dung của Canvas
    def configure_canvas(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    panedwindow.bind("<Configure>", configure_canvas)
def compose_mail_page():
    receive_frame.grid_forget()
    inbox_frame.grid_forget()
    work_frame.grid_forget()
    project_frame.grid_forget()
    spam_frame.grid_forget()
    important_frame.grid_forget()
    sent_frame.grid_forget()
    
    from_bar.configure(text = curUser.userName)
    compose_frame.grid(row=0, column=1, padx=0, pady=25, sticky = NW)
def inbox_page():
    receive_frame.grid_forget()
    compose_frame.grid_forget()
    work_frame.grid_forget()
    project_frame.grid_forget()
    spam_frame.grid_forget()
    important_frame.grid_forget()
    sent_frame.grid_forget()
    inbox_frame.grid(row=0, column=1, padx=0, pady=25, sticky = NW)
    
    #inbox_frame.pack()
def sent_page():
    receive_frame.grid_forget()
    compose_frame.grid_forget()
    inbox_frame.grid_forget()
    work_frame.grid_forget()
    project_frame.grid_forget()
    spam_frame.grid_forget()
    important_frame.grid_forget()
    sent_frame.grid(row=0, column=1, padx=0, pady=25, sticky = NW)
def important_page():
    receive_frame.grid_forget()
    compose_frame.grid_forget()
    inbox_frame.grid_forget()
    work_frame.grid_forget()
    project_frame.grid_forget()
    spam_frame.grid_forget()
    sent_frame.grid_forget()
    important_frame.grid(row=0, column=1, padx=0, pady=25, sticky = NW)
def work_page():
    receive_frame.grid_forget()
    compose_frame.grid_forget()
    inbox_frame.grid_forget()
    important_frame.grid_forget()
    project_frame.grid_forget()
    spam_frame.grid_forget()
    sent_frame.grid_forget()
    work_frame.grid(row=0, column=1, padx=0, pady=25, sticky = NW)
def project_page():
    receive_frame.grid_forget()
    compose_frame.grid_forget()
    inbox_frame.grid_forget()
    important_frame.grid_forget()
    work_frame.grid_forget()
    spam_frame.grid_forget()
    sent_frame.grid_forget()
    project_frame.grid(row=0, column=1, padx=0, pady=25, sticky = NW)
def spam_page():
    receive_frame.grid_forget()
    compose_frame.grid_forget()
    inbox_frame.grid_forget()
    important_frame.grid_forget()
    work_frame.grid_forget()
    project_frame.grid_forget()
    sent_frame.grid_forget()
    spam_frame.grid(row=0, column=1, padx=0, pady=25, sticky = NW)
def read_mail_page():
    inbox_frame.grid_forget()
    compose_frame.grid_forget()
    work_frame.grid_forget()
    project_frame.grid_forget()
    spam_frame.grid_forget()
    important_frame.grid_forget()
    sent_frame.grid_forget()
    receive_frame.grid(row=0, column=1, padx=0, pady=25, sticky = NW)
def create_login_frame():
    global login_frame, login_bar, title, username_login, password_login, noti_login, login_button, suggest_text_1, signup_button2
    login_frame = Frame(root, width=470, height=350)
    login_bar = Frame(login_frame, width=400, height=300, bg="white")
    title = Label(login_frame, text="Log in", font=("Arial Bold",13))
    title.grid(row=1, column=0, padx=5, pady=5)

    # Profile picture
    image = PhotoImage(file=r"Images/login.png")
    small_img = image.subsample(3,3)
    img = Label(login_bar, image=small_img)
    img.image = small_img
    img.grid(row=0, column=0, rowspan=6, padx=0, pady=0)

    # Name label and entry widgets
    Label(login_bar, text="Username", bg="white").grid(row=0, column=1, padx=5, pady=5, sticky=W)

    username_login = Entry(login_bar, width=25, bd=3)
    username_login.grid(row=0, column=2, padx=5, pady=5)

    # Password label and entry widgets
    Label(login_bar, text="Password", bg="white").grid(row=1, column=1, padx=5, pady=5, sticky=W)
    password_login = Entry(login_bar, width=25, bd=3, show="*")
    password_login.grid(row=1, column=2, padx=5, pady=5)

    #noti
    noti_login = Label(login_bar, text="", bg="white", fg="red")
    noti_login.grid(row=2, column=2, padx=5, pady=5, sticky=W)

    
    login_button = Button(login_bar, text="Log In", bg= "white", activebackground= "light green", relief=RAISED, command = lambda: login(username_login, password_login))
    login_button.grid(row=2,column=1, pady=5)

    #suggest text
    suggest_text_1 = Label(login_bar,text="Don't have an account?", bg="white",fg="steel blue")
    suggest_text_1.grid(row=3,column=1,columnspan=2,padx=5, pady=5,sticky=NW)

    signup_button2 = Button(login_bar, text="Sign Up", bg= "white", activebackground= "light blue", relief=RAISED, command = signup_page)
    signup_button2.grid(row=3,column=2, padx=30, pady=5, sticky=NE)
    login_bar.grid(row=2, column=0, padx=5, pady=5)
def login_page():
    receive_frame.grid_forget()
    signup_frame.grid_forget()
    inbox_frame.grid_forget()
    compose_frame.grid_forget()
    work_frame.grid_forget()
    project_frame.grid_forget()
    spam_frame.grid_forget()
    important_frame.grid_forget()
    sent_frame.grid_forget()
    tool_frame.grid_forget()

    login_frame.grid(row=1, column=1, padx=140, pady=120)
def create_signup_frame():
    global signup_frame, signup_bar, title, username, password, noti, login_button2, suggest_text

    signup_frame = Frame(root, width=400, height=300)
    signup_bar = Frame(signup_frame, width=400, height=300, bg="white")

    title = Label(signup_frame, text="Sign up", font=("Arial Bold",13))
    title.grid(row=1, column=0, padx=5, pady=5)

    # Profile picture
    image = PhotoImage(file=r"Images/login.png")
    small_img = image.subsample(3,3)

    img = Label(signup_bar, image=small_img)
    img.image = small_img
    img.grid(row=0, column=0, rowspan=6, padx=0, pady=0)

    Label(signup_bar, text="Username", bg="white").grid(row=0, column=1, padx=5, pady=5, sticky=W)

    username = Entry(signup_bar, width=25, bd=3)
    username.grid(row=0, column=2, padx=5, pady=5)

    # Password label and entry widgets
    Label(signup_bar, text="Password", bg="white").grid(row=1, column=1, padx=5, pady=5, sticky=W)
    password = Entry(signup_bar, width=25, bd=3, show="*")
    password.grid(row=1, column=2, padx=5, pady=5)

    #noti
    noti = Label(signup_bar, text="", bg="white", fg="red")
    noti.grid(row=2, column=2, padx=5, pady=5, sticky=W)

    signup_button = Button(signup_bar, text="Sign Up", bg= "white", activebackground= "light green", relief=RAISED, command = lambda: signup(username, password))
    signup_button.grid(row=2,column=1, pady=5)

    #suggest text
    suggest_text = Label(signup_bar,text="Already have an account?", bg="white",fg="steel blue")
    suggest_text.grid(row=3,column=1,columnspan=2,padx=5, pady=5,sticky=NW)

    login_button2 = Button(signup_bar, text="Log In", bg= "white", activebackground= "light blue", relief=RAISED, command = login_page)
    login_button2.grid(row=3,column=2, padx=30, pady=5, sticky=NE)
    signup_bar.grid(row=2, column=0, padx=5, pady=5)
def signup_page():
    receive_frame.grid_forget()
    login_frame.grid_forget()
    inbox_frame.grid_forget()
    compose_frame.grid_forget()
    work_frame.grid_forget()
    project_frame.grid_forget()
    spam_frame.grid_forget()
    important_frame.grid_forget()
    sent_frame.grid_forget()
    tool_frame.grid_forget()
    signup_frame.grid(row=1, column=1, padx=140, pady=120)
def main():
    global loaded_mails
    loaded_mails = Queue()
    setUpSystem()
    global stop_event, root, list_attachments

    list_attachments = []
    stop_event = Event()
    
    root = Tk()
    root.title("Email Client")
    root.geometry("700x500")  # set starting size of window
    root.maxsize(700, 500)  # width x height
    root.config(bg="skyblue")
    
    create_tool_bar_frame()
    create_compose_frame()
    create_inbox_frame()
    create_sent_frame()
    create_important_frame()
    create_work_frame()
    create_project_frame()
    create_spam_frame()
    create_read_mail_frame()
    create_login_frame()
    create_signup_frame()
    
    login_page()
    
    root.mainloop()
    try:
        exitApp()
    except:
        pass
if (__name__ == "__main__"):
    main()  
    