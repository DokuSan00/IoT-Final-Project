import smtplib
import imaplib
import email

class Emailer:
    session = None

    def __init__(self, server, port, username, password):
        #set up stmp server information
        self.server = server
        self.port = port

        self.username = username
        self.password = password

    #handle payload
    def get_body(msg):
        if (msg.is_multipart()):
            return Emailer.get_body(msg.get_payload(0))
        else:
            return msg.get_payload(None, True)


    def sendmail(self, recipient, subject, content):
        #Create message
        headers = [
            "From: " + self.username, "Subject: " + subject, "To: " + recipient,
            "MIME-Version: 1.0", "Content-Type: text/html"
        ]
        headers = "\r\n".join(headers)

        #connect server
        Emailer.session = smtplib.SMTP(self.server, self.port)

        Emailer.session.starttls()

        #Login to Gmail
        Emailer.session.login(self.username, self.password)

        #Send Email & Exit
        Emailer.session.sendmail(self.username, recipient, headers + "\r\n\r\n" + content)
        Emailer.session.quit()
        print(Emailer.session)

    def readmail(self, server, sender, subject):
        mail = imaplib.IMAP4_SSL(server) # connect server
        mail.login(self.username, self.password) #login 

        mail.list()
        mail.select("inbox")
        
        #set up filter
        filter = ""
        if (sender != None):
            filter += 'FROM "' + sender + '"'
            
        if (subject != None):
            filter += 'SUBJECT "' + subject + '"'
        
        if (filter == ""):
            filter = "ALL"
        
        res, data = mail.search(None, filter) # search for mail
        try:
            #get lastest mail. use try to handle index out of bound error here, lazy way
            latest_id = data[0].split()[-1]
            #fetch mail
            res, data = mail.fetch(latest_id, '(RFC822)')
            #get mail body
            raw = Emailer.get_body(email.message_from_bytes(data[0][1]))
            #decode message from bytest to string
            #get the first line
            resp = raw.decode('utf-8').splitlines()[0]
            #return first line
            return resp
        except:
            return ""


        