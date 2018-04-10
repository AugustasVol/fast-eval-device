#!/usr/bin/env python
from flask import Flask, render_template, Response, url_for
import cv2

app = Flask(__name__)
vc = cv2.VideoCapture(0)

@app.route("/index")
def index():
    question_q = [50,40,30,20,10]
    print(app.static_url_path)
    answersheet_names = [{"image":"q50.png", "pdf":"q50.pdf"},
                         {"image":"q40.png", "pdf":"q40.pdf"},
                         {"image":"q30.png", "pdf":"q30.pdf"},
                         {"image":"q20.png", "pdf":"q20.pdf"},
                         {"image":"q10.png", "pdf":"q10.pdf"}]
    return render_template("index.html", names = answersheet_names, quantities = question_q )

@app.route("/questions/<int:number>")
def questions(number):
    return str(number)

@app.route('/')
def index1():
    """Video streaming"""
    return render_template('index1.html')

def gen():
    """Video streaming generator function."""
    while True:
        rval, frame = vc.read()
        rval, encoded = cv2.imencode(".jpeg", frame)
        jpeg_bytes = encoded.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg_bytes + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/great")
def great():
    return "great"


if __name__ == '__main__':
        app.run(host='0.0.0.0', debug=True, threaded=False)
               