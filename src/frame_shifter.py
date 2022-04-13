import pandas as pd
import json
import os
import shutil
from . import data_loader

class FrameShifter:

    def __init__(self, data_loader_instance, frames_to_shift):
        self.data_loader = data_loader_instance
        self.frames_to_shift = frames_to_shift
        self.frameshifted_tub_path = self.data_loader.tub_path + '_frameshifted_' + str(self.frames_to_shift)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Read here on why this block needs 4 arguments: https://stackoverflow.com/questions/1984325/explaining-pythons-enter-and-exit
        return False

    def make_frameshifted_tub_dir(self):
        
        if not os.path.exists(self.frameshifted_tub_path):
            os.mkdir(self.frameshifted_tub_path)
            print("Directory " , self.frameshifted_tub_path ,  " created!")
        
        else:    
            print("Directory " , self.frameshifted_tub_path ,  " already exists!")

    def copy_images_to_fs_tub(self):
        # fs here meaning 'frameshifted'

        orig_images = os.path.join(self.data_loader.tub_path, 'images')
        fs_images = os.path.join(self.frameshifted_tub_path, 'images')

        if os.path.exists(fs_images):
            print("Removing previously existing images from frameshifted tub!")
            shutil.rmtree(fs_images)
            
        print("Copying original images to frameshifted tub!")
        shutil.copytree(orig_images, fs_images)

    def get_shifted_manifest_lines(self):
        lines = self.data_loader.get_orig_manifest_lines()
        metadata_dict = json.loads(lines[-1])

        # Add 0 to deleted indexes if it had it before
        if 0 in metadata_dict['deleted_indexes']:

            metadata_dict['deleted_indexes'] = [index+self.frames_to_shift for index in metadata_dict['deleted_indexes']]
            metadata_dict['deleted_indexes'].insert(0, 0)
        else:
            metadata_dict['deleted_indexes'] = [index+self.frames_to_shift for index in metadata_dict['deleted_indexes']]
        
        # Remove the ultimate index(es), as it (or they) might be out of bounds
        while metadata_dict['deleted_indexes'][-1] >= metadata_dict['current_index']:
            metadata_dict['deleted_indexes'].pop()

        lines[-1] = str(metadata_dict)
        return lines

    def write_manifest(self):
        fs_manifest_path = os.path.join(self.frameshifted_tub_path, 'manifest.json')

        with open(fs_manifest_path, 'w') as f:
            for line in self.get_shifted_manifest_lines():
                f.write(line)
            print("Frameshifted manifest file created!")

    def shift_catalog_angles(self):
        pass

    def shift_frames(self):
        self.copy_images_to_fs_tub()
        self.write_manifest()
