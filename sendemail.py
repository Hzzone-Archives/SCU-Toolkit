import smtplib
from email.mime.text import MIMEText

def sendEmail(course_name, course_text):
	_user = "1141408077@qq.com"
	_pwd  = "emxrefjwdjprigcg"
	_to   = "zhizhonghwang@gmail.com"

	msg = MIMEText(course_text)
	msg["Subject"] = course_name
	msg["From"]    = _user
	msg["To"]      = _to

	try:
	    s = smtplib.SMTP_SSL("smtp.qq.com", 465)
	    s.login(_user, _pwd)
	    s.sendmail(_user, _to, msg.as_string())
	    s.quit()
	    print("Success!")
	except smtplib.SMTPException:
	    print("Falied,%s"%e)

# if __name__ == "__main__":
# 	sendEmail("hahahah", '100')