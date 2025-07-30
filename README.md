# Mail Client
> Project of Computer Networks course

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://www.python.org/)


## 🚀 Overview
This project is a simple mail client allows users to send email using SMTP protocol and download emails using POP3 protocol from a [Test Mail Server](https://github.com/eugenehr/test-mail-server/releases/download/1.0/test-mail-server-1.0.jar). It is implemented in Python, uses `socket` library to handle network communication, and uses [`customtkinter`](https://customtkinter.tomschimansky.com/) for the GUI.

Team size: 3 members

## ✨ Key Features
- **Send Emails**: Send emails using SMTP protocol, supports TO, CC, BCC, and attachments (txt, pdf, docx, xlsx, png, jpg).
- **Receive Emails**: 
    - Download emails using POP3 protocol, can download email with attachments and save them to local storage.
    - Downloading emails automatically based on time value in `config.json`.
- **Manage Email Status**: Mark emails as read/unread, delete emails.
- **Filter Emails**: Filter emails by sender, subject, contents and can move emails to specific folders.

# 📚 Documentation
Visit the [Report](https://drive.google.com/file/d/1FIShmY0WPV9TmXPgMaLvO5mSM-qVoWXg/view?usp=drive_link) to check the detailed documentation of the project.