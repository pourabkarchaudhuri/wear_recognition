import asyncio
import test_request
from threading import Thread

def send_notification(url, name, loop):
    """Generate and send the notification email"""
    print("Send Notification")

    print("URL : ", url)
    print("Name : ",name)
    # Do some work to get payload body


    # Connect package
    response = test_request.send_push_notification(url, name)

    print(response)

    # server.quit()
    # call api

    # return False
    loop.stop()
    

def start_email_worker(loop):
    """Switch to new event loop and run forever"""
    print("Start worker")
    asyncio.set_event_loop(loop)
    loop.run_forever()

# Create the new loop and worker thread
worker_loop = asyncio.new_event_loop()
worker = Thread(target=start_email_worker, args=(worker_loop,))

# Start the thread
worker.start()

# Assume a Flask restful interface endpoint

def notify(url, name):
    """Request notification email"""
    print("Calling Worker Loop")

    worker_loop.call_soon_threadsafe(send_notification, url, name, worker_loop)

print("Starting Module")
notify('https://pbs.twimg.com/profile_images/988274520032272385/VnqVwUCB.jpg', 'Pourab')
print("Next Frame")