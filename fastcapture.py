# import the necessary packages
from __future__ import print_function
from pathlib import Path
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import numpy as np
import argparse
import cv2

DEFAULT_NFRAMES = 200*5
 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("source", nargs='?', default="/dev/video0",
    help="the address of the camera to capture frames from")
ap.add_argument("-o", "--output", default="out.avi",#
    help="path to the output movie file")
ap.add_argument("-n", "--num-frames", type=int, default=DEFAULT_NFRAMES,
	help="# of frames to loop over for FPS test")
ap.add_argument("-r", "--output-rate", type=float, default=200.0,
    help="the frame rate of the output video (nothing to do with the acquisition rate)")
ap.add_argument("-q", "--nodisplay", dest="display", action='store_false',
	help="suppress the frames to be displayed on-line")

args = vars(ap.parse_args())
print("[INFO] source={source}, frames={num_frames}, display={display}, output={output}".format(**args))

# created a *threaded* video stream, allow the camera sensor to warmup,
# and start the FPS counter
print("[INFO] sampling THREADED frames from webcam...")
vs     = WebcamVideoStream(src=args["source"]).start()
frames = []
fps    = FPS().start()
 
# loop over some frames...this time using the threaded stream
while fps._numFrames < args["num_frames"]:
    # grab the frame from the threaded video stream
    frame = vs.read()
 
    # check to see if the frame should be displayed to our screen
    if args["display"] == True:
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
    frames.append(np.array(frame))
 
    # update the FPS counter
    fps.update()
 
# stop the timer and display FPS information
fps.stop()
vs.stop()
height, width = frames[-1].shape[:2]
rate          = args['output_rate']

print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

path   = Path(args["output"]).with_suffix(".avi")
fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
writer = cv2.VideoWriter(str(path), fourcc, rate, (width, height))
print(f"[INFO] writing at frame rate {rate}", end='', flush=True)
for i, frame in enumerate(frames):
    writer.write(frame)
    if i % 100 == 99:
        print(".", end=" " if i % 1000 == 999 else "", flush=True)
writer.release()
print(f"done (-> {path}).")

# do a bit of cleanup
vs.stream.release()
cv2.destroyAllWindows()