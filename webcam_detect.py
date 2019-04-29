#!/usr/bin/env python2
import cv2
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

url='http://172.25.97.45:8080/shot.jpg'
# url='http://192.168.43.133:8080/shot.jpg'
dir_path = os.path.dirname(os.path.realpath(__file__))

UPLOAD_FOLDER = dir_path + "\\images"
arr = list()

def main():
    c = zerorpc.Client()
    c.connect("tcp://127.0.0.1:4242")
    if os.path.exists("images"):
        shutil.rmtree("images")

    os.mkdir('images')
    # tempCam = cv2.VideoCapture(0)
    video_capture = cv2.VideoCapture(0)
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    minsize = 25 # minimum size of face
    threshold = [ 0.6, 0.7, 0.7 ]  # three steps's threshold
    factor = 0.709 # scale factor
    fps = 0
    frame_num = 0

    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.30)
    sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
    with sess.as_default():
        pnet, rnet, onet = detect_face_detection.create_mtcnn(sess, None)
        while(True):
            imgResponse = urllib.request.urlopen(url)
            imgNp = np.array(bytearray(imgResponse.read()),dtype=np.uint8)
            imgs = cv2.imdecode(imgNp,-1)
            start_time = time.time()
            # vidcap.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
            ret, frame = video_capture.read()
            if not ret:
                break
            # Display the resulting frame
            # imgs = frame[:,:,0:3]
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
                # print("[INFO]:Processing : " + filename)
                cv2.imwrite(path, sub_faces)
                result = c.classifyFile(path)

                # print(type(result[0]) == dict)
                if (len(result) != 0):
                    if (type(result[0]) == dict and len(result[0]['candidates']) != 0):
                        # result[0]['candidates']['name']
                        if(result[0]['candidates']['name'] != 'Not Recognized'):
                            print("[INFO]: Detected Results : ", result[0])
                            # print(result[0])
                            recognized_faces = result[0]
                            cv2.putText(imgs, recognized_faces['candidates']['name'], (x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                            if not recognized_faces['candidates']['name'] in arr:
                                upload_response = image_upload.upload(filename)
                                response = send_notifications.send_push_notification(upload_response['url'], recognized_faces['candidates']['name'])
                                # if (response.status_code == 200):

                                print("[INFO]: Pushing Notification for : ", recognized_faces['candidates']['name'])
                                arr.append(recognized_faces['candidates']['name'])
                            # os.remove(path)
                    else:
                        cv2.putText(imgs, "Not Recognized", (x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                if os.path.exists(path):
                    os.remove(path)
            end_time = time.time()
            fps = fps * 0.9 + 1/(end_time - start_time) * 0.1
            start_time = end_time
            frame_info = 'Frame: {0}, FPS: {1:.2f}'.format(frame_num, fps)
            cv2.putText(imgs, frame_info, (10, frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.imshow('video', imgs)
            # p1 = int(boxes[0][2])
            # p2 = int(boxes[0][3])
            
            
            

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    video_capture.release()
    cv2.destroyAllWindows()




if __name__ == '__main__':
    main()
