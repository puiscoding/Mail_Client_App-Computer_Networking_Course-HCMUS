# Email Client Application

## Overview
This is a project in the course Computer Networking, aiming to understand socket and how the protocol SMTP and POP3 work to send and receive emails.  

## Features
- **Sign Up**: Users can sign up with any email domains and they are not need to be real because we use a Test Mail Sever which allows any email to access. The only reason why you need to create account is that this Mail Client App requires an account :>
- **Log In**: Once you sign up, you can log in with your account. If you don't want to sign up, you can use our default account: 
    - username: defaultuser@meomeo.com
    - password: 12345678

- **Compose email**: You can write email with the app's (un)friendly interface :>
- **Send email**: You can send email to any email account, even it doesn't exist. You can check wether the mail is sent in the Test Mail Sever's Mailboxes. 
- **Read email**: Your mails are filtered into 6 folders: Inboxes, Sent, Importance, Work, Project, Spam. You can read your mail in the respective folder. 
- **Log out**: Log out to switch to another account. 

## Installation and Run
1. Clone the repository: <space> <space>
   - git clone https://github.com/puiscoding/Mail_Client_App-Computer_Networking_Course-HCMUS/
2. Config the Test Mail Sever
   - Open the file "test-mail-server-1.0.jar" in the Source/Sever folder (This is the Test Mail Sever running in Java environment. If you dont have Java installed yet, you may need to install Java. Here where you can install Java: https://www.java.com/download/ie_manual.jsp)
   - After openning the Test Mail Sever, change the SMTP port to 2225, change the POP3 port to 3335. Don't forget to click on the Pause button next to the port to make the port run.
3. Navigate to the Source directory:
   - In the root folder, change dir to the Source folder by typing the following command in the terminal:
    cd source
4. Run the application:
   - In the Source folder, type the following command in the terminal to run the app:
    python mail_client.py 
   - (You need to have Python to run the app:>. If you don't, you can install Python here: https://www.python.org/downloads/)
     
###### p/s: dont judge our messy code (actually you can) :>



