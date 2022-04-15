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
parser.add_argument(
    '-t',
    '--tub',
    action = "store",
    help = "Specifies the tub you want to make a copy of and frameshift",
    dest = "tub_name",
    default = 'tub_85_22-03-31'
)
args = parser.parse_args()

print("Starting frameshifter...")

my_data_loader = data_loader.DataLoader(args.tub_name)
my_frame_shifter = frame_shifter.FrameShifter(my_data_loader, int(args.frames_to_shift))
my_frame_shifter.shift_frames()

print("Frameshift done!")