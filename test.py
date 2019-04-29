from threading import Thread, Lock
import time, os, sys, shutil
import imutils
import cv2

import numpy as np
sys.path.append('.')
import tensorflow as tf
import detect_face_detection

import urllib.request

import zerorpc

import send_notifications
import image_upload


url='http://172.25.97.64:8080/shot.jpg'
dir_path = os.path.dirname(os.path.realpath(__file__))

UPLOAD_FOLDER = dir_path + "\\images"
arr = list()

print("Loading Module")
class WebcamVideoStream :
    def __init__(self, src = 0, width = 1920, height = 1080) :
        
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        (self.grabbed, self.frame) = self.stream.read()
        self.started = False
        self.read_lock = Lock()

    def start(self) :
        if self.started :
            print ("already started!!")
            return None
        self.started = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self) :
        while self.started :
            
            (grabbed, frame) = self.stream.read()
            self.read_lock.acquire()
            self.grabbed, self.frame = grabbed, frame
            self.read_lock.release()

    def read(self) :
        self.read_lock.acquire()
        frame = self.frame.copy()
        self.read_lock.release()
        return frame

    def stop(self) :
        self.started = False
        self.thread.join()

    def __exit__(self, exc_type, exc_value, traceback) :
        self.stream.release()

    # def process(self):
    #     self.thread.start()
    #     return self



if __name__ == "__main__" :
    vs = WebcamVideoStream().start()

    c = zerorpc.Client()
    c.connect("tcp://127.0.0.1:4242")
    if os.path.exists("images"):
        shutil.rmtree("images")

    os.mkdir('images')

    minsize = 25 # minimum size of face
    threshold = [ 0.6, 0.7, 0.7 ]  # three steps's threshold
    factor = 0.709 # scale factor

    fps = 0
    frame_num = 60

    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.30)
    sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
    with sess.as_default():
        pnet, rnet, onet = detect_face_detection.create_mtcnn(sess, None)
        while True :
            imgResponse = urllib.request.urlopen(url)
            imgNp = np.array(bytearray(imgResponse.read()),dtype=np.uint8)
            imgs = cv2.imdecode(imgNp,-1)
            # fps = FPS().start()
            start_time = time.time()
            frame = vs.read()
            img = frame[:,:,0:3]
            boxes, _ = detect_face_detection.detect_face(imgs, minsize, pnet, rnet, onet, threshold, factor)
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
                if (len(result) != 0):
                    if (type(result[0]) == dict and len(result[0]['candidates']) != 0):
                        # result[0]['candidates']['name']
                        if(result[0]['candidates']['name'] != 'Not Recognized'):
                            print(result[0])
                            recognized_faces = result[0]
                            cv2.putText(imgs, recognized_faces['candidates']['name'], (x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                            if not recognized_faces['candidates']['name'] in arr:
                                upload_response = image_upload.upload(filename)
                                response = send_notifications.send_push_notification(upload_response['url'], recognized_faces['candidates']['name'])
                                # if (response.status_code == 200):
                                # print(response)
                                arr.append(recognized_faces['candidates']['name'])
                            # os.remove(path)
                    else:
                        cv2.putText(imgs, "Not Recognized", (x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                if os.path.exists(path):
                    os.remove(path)

            end_time = time.time()
            fps = fps * 0.9 + 1/(end_time - start_time) * 60
            # fps = (end_time - start_time) / frame_num
            frame_info = 'Frame: {0}, FPS: {1:.2f}'.format(frame_num, fps)
            cv2.putText(imgs, frame_info, (10, frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.imshow('webcam', imgs)

            # cv2.putText(img, frame_info, (10, frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            # cv2.imshow('video', imgs)
            if cv2.waitKey(1) & 0xFF == ord('q') :
                break
            # fps.update()

    # fps.stop()

    vs.stop()
    cv2.destroyAllWindows()