import os
import argparse
import frame_shifter
import data_loader

parser = argparse.ArgumentParser()
parser.add_argument(
    '-fs',
    '--frameshift',
    action = "store",
    help = "Specifies the number of frames to shift (positive values shift a frame at position x to have the steering angle at frame x + frameshift). ",
    dest = "frames_to_shift"
)
args = parser.parse_args()

my_data_loader = data_loader.DataLoader('tub_85_22-03-31')
my_frame_shifter = frame_shifter.FrameShifter(my_data_loader, int(args.frames_to_shift))
my_frame_shifter.shift_frames()

print("Frameshift done!")