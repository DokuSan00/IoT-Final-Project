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


    #handle payload
    def get_body(msg):
        if (msg.is_multipart()):
            return Emailer.get_body(msg.get_payload(0))
        else:
            return msg.get_payload(None, True)

    def search_mail(mailer, sender, subject):
        #set up filter
        filter = ""
        if (sender != None):
            filter += 'FROM "' + sender + '" ' 
        if (subject != None):
            filter += 'SUBJECT "' + subject + '"'
        
        if (not bool(filter)):
            filter = "ALL"

        resp = mailer.search(None, filter, '(UNSEEN)') # search for mail

        return resp

    def read_mail(self, server, sender, subject):
        mailer = imaplib.IMAP4_SSL(server) # connect server
        mailer.login(self.username, self.password) #login 

        mailer.list()
        mailer.select("inbox", False)
        
        status, data = Emailer.search_mail(mailer, sender, subject)

        #set all mails as read (prevent checking same mail)
        for id in data[0].split():
            mailer.store(id, '+FLAGS', '\\SEEN')

        try:
            #get lastest mail. use try to handle index out of bound error here, lazy way
            latest_id = data[0].split()[-1]
        except:
            #if error raise => no result => return null
            return None
        
        res, data = mailer.fetch(latest_id, '(RFC822)')

        #get mail body
        raw = Emailer.get_body(email.message_from_bytes(data[0][1]))

        #decode from bytes to string -> get first line
        resp = raw.decode('utf-8').splitlines()[0]
        return resp.strip()


        