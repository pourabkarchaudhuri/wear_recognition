from twilio.rest import Client

# Your Account Sid and Auth Token from twilio.com/console

account_sid = 'ACd9635007863867a4d72b9ec6b3875931'
auth_token = '611f48880cfbf719a945dc1673f2cde1'
numbers = ["+919748978812", "+918878339946"]
whatsapp_source = "+14155238886"
sms_source = "+18123591204"
payload = 'This is an automated message. Based on your preferences of Polo T-shirts, there are a few offers that might be of interest to you. Get 20% OFF on Turtle shirts above a purchase of $150. There is also a new range of Chinos that you may like to try out!'


def send_message():
    client = Client(account_sid, auth_token)
    for n in numbers:
        whatsapp_message = client.messages.create(
                                    body=payload,
                                    from_='whatsapp:' + whatsapp_source,
                                    to='whatsapp:' + n
                                )
        print("Success on Whatsapp : " + whatsapp_message.sid)
        sms_message = client.messages.create(
                                body=payload,
                                from_=sms_source,
                                to=n
                            )

        print("Success on SMS : " + sms_message.sid)