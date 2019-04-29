import cv2
import threading

#!/usr/bin/env python2
# import cv2
import os
import sys
import numpy as np
sys.path.append('.')
import tensorflow as tf
import detect_face_detection
import time, shutil

import urllib.request

import zerorpc

import send_notifications
import image_upload
import send_message

url='http://172.25.97.40:8080/shot.jpg'
dir_path = os.path.dirname(os.path.realpath(__file__))

UPLOAD_FOLDER = dir_path + "\\images"
arr = []
message_sent_array = []

# if os.path.exists("images"):
#         shutil.rmtree("images")

class camThread(threading.Thread):
    def __init__(self, previewName, camID):
        threading.Thread.__init__(self)
        self.previewName = previewName
        self.camID = camID
    def run(self):
        print ("Starting " + self.previewName)
        camPreview(self.previewName, self.camID)

def camPreview(previewName, camID):

    c = zerorpc.Client()
    c.connect("tcp://127.0.0.1:4242")
    if (camID != 'IPCAM'):
        print("Opening Camera number : ", camID)
        video_capture = cv2.VideoCapture(camID)
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    else:
        # video_capture = cv2.VideoCapture(0)
        print("IPCAM Detected || IP : ", url)
    minsize = 25 # minimum size of face
    threshold = [ 0.6, 0.7, 0.7 ]  # three steps's threshold
    factor = 0.709 # scale factor
    fps = 0
    frame_num = 0
    frame = None
    imgs = None

    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.30)
    sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
    with sess.as_default():
        pnet, rnet, onet = detect_face_detection.create_mtcnn(sess, None)
        while(True):
            if (camID == 'IPCAM'):
                imgResponse = urllib.request.urlopen(url)
                imgNp = np.array(bytearray(imgResponse.read()),dtype=np.uint8)
                imgs = cv2.imdecode(imgNp,-1)
                
                # ret, frame = video_capture.read()
                # if not ret:
                #     break
            else:
                ret, frame = video_capture.read()
                if not ret:
                    break
                imgs = frame[:,:,0:3]
            start_time = time.time()
            # vidcap.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
            # ret, frame = video_capture.read()
            # if not ret:
            #     break
            # Display the resulting frame
            # img = frame[:,:,0:3]
            boxes, _ = detect_face_detection.detect_face(imgs, minsize, pnet, rnet, onet, threshold, factor)
            # print(boxes)
            for i in range(boxes.shape[0]):
                pt1 = (int(boxes[i][0]), int(boxes[i][1]))
                pt2 = (int(boxes[i][2]), int(boxes[i][3]))
                x = int(boxes[i][0]) - 150
                y = int(boxes[i][1]) - 150
                w = int(boxes[i][2]) + 190
                h = int(boxes[i][3]) + 150
                frame = cv2.rectangle(imgs, (x,y), (w, h), color=(0, 255, 0))
                
                frame_info = 'Frame: {0}, FPS: {1:.2f}'.format(frame_num, fps)
                
                # if(float(boxes[i][4]) >= 0.90):
                    
                sub_faces = frame[y:h, x:w]
                # sub_faces = frame[p1, p2]
                stamp = str(time.time())
                filename = "face_" + stamp + ".jpg"
                path = UPLOAD_FOLDER + "\\" + filename
                cv2.imwrite(path, sub_faces)
                result = c.classifyFile(path)
                # print(type(result[0]) == dict)
                # print(result)
                if (len(result) != 0):
                    if (type(result[0]) == dict and len(result[0]['candidates']) != 0):
                        # result[0]['candidates']['name']
                        # print(result[0])
                        if(result[0]['candidates']['name'] != 'Not Recognized'):
                            # print(result[0])
                            recognized_faces = result[0]
                            cv2.putText(imgs, recognized_faces['candidates']['name'], (x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                            # for obj in arr:
                            if (camID == 'Demo Camera'):
                            #     print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                            #     print("IP Camera Detected")
                                if not recognized_faces['candidates']['name'] in arr:
                                    print("At Enterance New person detected")
                                    upload_response = image_upload.upload(filename)
                                    response = send_notifications.send_push_notification(upload_response['url'], recognized_faces['candidates']['name'])
                                    # print("!!!!!!!!!!!!!!!!!!!!!")
                                    print("Notification Sent")
                                    arr.append(recognized_faces['candidates']['name'])
                                    # upload_response = image_upload.upload(filename)
                                    # response = send_notifications.send_push_notification(upload_response['url'], recognized_faces['candidates']['name'])
                                    # if (response.status_code == 200):
                                    # print(response)
                            else:
                                print("!!!!!!!!!!!!!!!!!")
                                print(recognized_faces['candidates']['name'] + "is near shelf")
                                if recognized_faces['candidates']['name'] in arr:
                                    if not recognized_faces['candidates']['name'] in message_sent_array:
                                        send_message.send_message()
                                        message_sent_array.append(recognized_faces['candidates']['name'])
                                        print("message sent")
                                        
                                        

                            # os.remove(path)
                    else:
                        cv2.putText(imgs, "Not Recognized", (x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                # if os.path.exists(path):
                #     os.remove(path)
            end_time = time.time()
            fps = fps * 0.9 + 1/(end_time - start_time) * 0.1
            start_time = end_time
            frame_info = 'Frame: {0}, FPS: {1:.2f}'.format(frame_num, fps)
            # cv2.putText(imgs, frame_info, (10, frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.imshow(previewName, imgs)  
            
            

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    video_capture.release()
    cv2.destroyAllWindows()

if os.path.exists("images"):
    shutil.rmtree("images")
os.mkdir('images')
# Create two threads as follows
thread1 = camThread("Interior Aisle Camera", 1)
thread2 = camThread("Demo Camera", 0)
# thread3 = camThread("Exterior Camera", 'IPCAM')
thread1.start()
thread2.start()
# thread3.start()