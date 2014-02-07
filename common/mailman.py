# -*- coding: utf-8 -*-
import email
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import smtplib
import mailutil

def sendEmail(authInfo, fromAdd, toAdd, subject, plainText, htmlText):
    strFrom = fromAdd
    strTo = ', '.join(toAdd)
    
    server = authInfo.get('server')
    user = authInfo.get('user')
    passwd = authInfo.get('password')
    
    if not (server and user and passwd) :
        print 'incomplete login info, exit now'
        return
    
    # 设定root信息
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subject
    msgRoot['From'] = strFrom
    msgRoot['To'] = strTo
    msgRoot.preamble = 'This is a multi-part message in MIME format.'
    
    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)
    
    #设定纯文本信息
    #        msgText = MIMEText(plainText, 'plain', 'utf-8')
    #        msgAlternative.attach(msgText)
    
    #设定HTML信息
    msgText = MIMEText(htmlText, 'html', 'utf-8')
    msgAlternative.attach(msgText)
    
    #设定内置图片信息
    #        fp = open('test.jpg', 'rb')
    #        msgImage = MIMEImage(fp.read())
    #        fp.close()
    #        msgImage.add_header('Content-ID', '<image1>')
    #        msgRoot.attach(msgImage)
    
    #发送邮件
    smtp = smtplib.SMTP()
    #设定调试级别，依情况而定
    smtp.set_debuglevel(1)
    smtp.connect(server)
    smtp.login(user, passwd)
    smtp.sendmail(strFrom, toAdd, msgRoot.as_string())
    smtp.quit()
    return

def sendEmailByDefault(subject, plainText, htmlText):
    authInfo = {}
    authInfo['server'] = mailutil.get_smtp_server()
    authInfo['user'] = mailutil.get_sent_user()
    authInfo['password'] = mailutil.get_sent_password()
    fromAdd = authInfo['user']
    toAdd = mailutil.get_mail_to()
    sendEmail(authInfo, fromAdd, toAdd, subject, plainText, htmlText)

if __name__ == '__main__' :
    authInfo = {}
    authInfo['server'] = mailutil.get_smtp_server()
    authInfo['user'] = mailutil.get_sent_user()
    authInfo['password'] = mailutil.get_sent_password()
    fromAdd = authInfo['user']
    toAdd = mailutil.get_mail_to()
    print toAdd
    subject = 'title'
    plainText = '这里是普通文本'
    htmlText = '<B>HTML文本</B>'
    sendEmail(authInfo, fromAdd, toAdd, subject, plainText, htmlText)
