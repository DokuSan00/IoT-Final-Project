import smtplib, ssl

class Emailer:
    SMTP_SERVER = 'smtp-mail.outlook.com'  #Email Server (don't change!)
    SMTP_PORT = 587  #Server Port (don't change!)
    session = None

    def __init__(self, username, password):
        self.username = username
        self.password = password

        Emailer.session = smtplib.SMTP(Emailer.SMTP_SERVER, Emailer.SMTP_PORT)
        Emailer.session.starttls()
        Emailer.session.login(self.username, self.password)

    def sendmail(self, recipient, subject, content):
        if (Emailer.session == None):
            return
        #Create Headers
        headers = [
            "From: " + self.username, "Subject: " + subject, "To: " + recipient,
            "MIME-Version: 1.0", "Content-Type: text/html"
        ]
        headers = "\r\n".join(headers)

        #Login to Gmail
        Emailer.session.login(self.username, self.password)

        #Send Email & Exit
        Emailer.session.sendmail(self.username, recipient, headers + "\r\n\r\n" + content)