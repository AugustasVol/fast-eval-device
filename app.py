#!/usr/bin/env python
from flask import Flask, render_template, Response, url_for, request, jsonify
import numpy as np
import cv2
import random
from time import sleep

from written_test_automation import result, pre

app = Flask(__name__)
camera = cv2.VideoCapture(0)#"/home/av/my_prog/mct.MP4")

answersheet_names = [{"image":"q50.png", "pdf":"q50.pdf"},
                     {"image":"q40.png", "pdf":"q40.pdf"},
                     {"image":"q30.png", "pdf":"q30.pdf"},
                     {"image":"q20.png", "pdf":"q20.pdf"},
                     {"image":"q10.png", "pdf":"q10.pdf"}]

answer_values = {"A":[1,0,0,0,0,0],
                 "B":[0,1,0,0,0,0],
                 "C":[0,0,1,0,0,0],
                 "D":[0,0,0,1,0,0],
                 "E":[0,0,0,0,1,0],
                 "None":[0,0,0,0,0,1]}

question_q = [50,40,30,20,10]

# results from camera a global variable, because only one camera
camera_results = None

def video_stream():
    global camera_results
    while True:
        rval, frame = camera.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = pre.rotate_bound(gray, 270)
        try:
            camera_results = np.argmax(result.predict(gray), axis=1)
            #print("video" , camera_results)
        except Exception as e:
            #print(e)
            camera_results = None
            #print("video", camera_results)

        rval, encoded = cv2.imencode(".jpeg", gray)
        jpeg_bytes = encoded.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg_bytes + b'\r\n')

def prepare_form(form):
    '''
    sort and argmax values from client
    '''
    form = form.items()
    form = list(map(lambda x: (int(x[0]),x[1]) , form))
    form = sorted(form, key=lambda x: x[0])
    answer_arr = list(map(lambda x: answer_values[x[1]], form))
    answer_argmax = np.argmax(np.array(answer_arr), axis=1)

    return list(answer_argmax)

@app.route("/")
def index():
    return render_template("index.html", names = answersheet_names, quantities = question_q )

@app.route("/questions/<int:number>")
def questions(number):
    return render_template("questions.html", half_number=int(number / 2) )

@app.route('/evaluate', methods=["POST"])
def evaluate():
    form = request.form
    answers = prepare_form(form)
 
    return render_template('realtime.html', answers=answers)

@app.route('/result', methods=["POST"])
def evaluation():
    right_answers = request.get_json()["answers"]

    if type(camera_results) == type(None):
        result = "No result"
    else:
        bool_list = np.array(camera_results) == np.array(right_answers)
        result = 100 * (np.sum(bool_list) / len(bool_list))

    return jsonify({"evaluation":result})


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
        app.run(host='0.0.0.0', debug=False, threaded=True)
               