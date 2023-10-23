import smtplib, ssl

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
        print(session)