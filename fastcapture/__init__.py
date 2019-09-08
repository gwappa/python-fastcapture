#
# MIT License
#
# Copyright (c) 2019 Paul Zimmer-Harwood & Keisuke Sehara
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from __future__ import print_function
from pathlib import Path
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import numpy as np
import argparse
import cv2
import subprocess as sp


AUTO_EXPOSURE_OFF = 0.25
AUTO_EXPOSURE_ON  = 0.75

VERSION_STR = "1.0a2"

DEFAULT_SOURCE   = "/dev/video0"
DEFAULT_OUTPUT   = "local/out.avi"
DEFAULT_NFRAMES  = 200*60*2
DEFAULT_RATE     = 200.0
DEFAULT_EXPOSURE = 500
DEFAULT_MAX_EXP  = 30000000

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("source", nargs='?', default=DEFAULT_SOURCE,
    help="the address of the camera to capture frames from")
ap.add_argument("-o", "--output", default=DEFAULT_OUTPUT,
    help="path to the output movie file")
ap.add_argument("-n", "--num-frames", type=int, default=DEFAULT_NFRAMES,
	help="# of frames to loop over for FPS test")
ap.add_argument("-r", "--output-rate", type=float, default=DEFAULT_RATE,
    help="the frame rate of the output video (nothing to do with the acquisition rate)")
ap.add_argument("-u", "--exposure-us", type=int, default=DEFAULT_EXPOSURE,
        help="the exposure time in microseconds.")
ap.add_argument("-q", "--nodisplay", dest="display", action='store_false',
	help="suppress the frames to be displayed on-line")
ap.add_argument("-x", "--nosave", dest="saved", action="store_false",
        help="supress the frames to be stored.")

def main():
    run(**vars(ap.parse_args()))

def run(source=DEFAULT_SOURCE, output=DEFAULT_OUTPUT,
        exposure_us=DEFAULT_EXPOSURE, max_exposure_us=DEFAULT_MAX_EXP,
        num_frames=DEFAULT_NFRAMES, output_rate=DEFAULT_RATE,
        display=True, saved=True):
    print(f"[INFO]  source={source}, frames={num_frames}, display={display}, output={output}")

    # currently I cannot deal with auto-gain through OpenCV...
    sp.run(f"v4l2-ctl -d {source} -c gain_auto=0", check=True, shell=True)
    
    # created a *threaded* video stream, allow the camera sensor to warmup,
    # and start the FPS counter
    vs     = WebcamVideoStream(src=source)
    vs.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, AUTO_EXPOSURE_OFF)
    vs.stream.set(cv2.CAP_PROP_EXPOSURE,      exposure_us / max_exposure_us)
    print("[DEBUG] OpenCV exposure value: ", vs.stream.get(cv2.CAP_PROP_EXPOSURE))
    print("[INFO]  sampling THREADED frames from webcam ", end='', flush=True)
    vs.start()
    frames = []
    fps    = FPS().start()

    # loop over some frames...this time using the threaded stream
    while fps._numFrames < num_frames:
        # grab the frame from the threaded video stream
        frame = vs.read()[1]

        # check to see if the frame should be displayed to our screen
        if display == True:
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
            if key < 255:
                break
        if saved == True:
            frames.append(np.array(frame))

        # update the FPS counter
        fps.update()
        if fps._numFrames % 100 == 99:
            print(".", end=" " if fps._numFrames % 1000 == 999 else "", flush=True)

    # stop the timer and display FPS information
    fps.stop()
    vs.stop()

    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    if saved == True:
        height, width = frames[-1].shape[:2]
        path   = Path(output).with_suffix(".avi")
        fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
        writer = cv2.VideoWriter(str(path), fourcc, output_rate, (width, height))
        print(f"[INFO] writing at frame rate {output_rate:.1f}", end='', flush=True)
        for i, frame in enumerate(frames):
            writer.write(frame)
            if i % 100 == 99:
                print(".", end=" " if i % 1000 == 999 else "", flush=True)
        writer.release()
        print(f"done (-> {path}).")

    # do a bit of cleanup
    vs.stream.release()
    cv2.destroyAllWindows()
