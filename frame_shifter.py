import pandas as pd
import json
import os
import shutil
import data_loader

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
        print("-- Handling images! --")

        orig_images = os.path.join(self.data_loader.tub_path, 'images')
        fs_images = os.path.join(self.frameshifted_tub_path, 'images')

        if os.path.exists(fs_images):
            print("\tRemoving previously existing images from frameshifted tub!")
            shutil.rmtree(fs_images)
            
        print("\tCopying original images to frameshifted tub!")
        shutil.copytree(orig_images, fs_images)

    def copy_catalog_manifests(self):
        print("-- Handling catalog_manifest files! --")

        catalog_manifest_paths = [catalog_path + '_manifest' for catalog_path in self.data_loader.catalog_paths]

        for catalog_manifest_path in catalog_manifest_paths:
            orig_cm = os.path.join(self.data_loader.tub_path, catalog_manifest_path)
            fs_cm = os.path.join(self.frameshifted_tub_path, catalog_manifest_path)

            if os.path.exists(fs_cm):
                print(f"\t\tRemoving previously existing {catalog_manifest_path} from frameshifted tub!")
                os.remove(fs_cm)
                
            print(f"\tCopying original {catalog_manifest_path} to frameshifted tub!")
            shutil.copy(orig_cm, fs_cm)

    def get_shifted_manifest_lines(self):
        lines = self.data_loader.get_orig_manifest_lines()
        metadata_dict = json.loads(lines[-1])

        # Deleted index shift
        # we're subtracting here, because we're going by steering angles. The steering angle originally at frame x will now be at frame x-frameshift.
        metadata_dict['deleted_indexes'] = [index-self.frames_to_shift for index in metadata_dict['deleted_indexes']]
            
        # Add 0 to deleted indexes if it had it before
        if self.frames_to_shift < 0:
            for deleted_index in range(abs(self.frames_to_shift)):
                # Fill the beginning of the deleted index array, if the first frame was deleted in the original
                metadata_dict['deleted_indexes'].insert(deleted_index, deleted_index)
    
        # Remove the ultimate index(es), as it (or they) might be out of bounds
        while metadata_dict['deleted_indexes'][-1] >= metadata_dict['current_index']:
            metadata_dict['deleted_indexes'].pop()
        
        if self.frames_to_shift > 0:
            metadata_dict['deleted_indexes'].pop(0)

        lines[-1] = json.dumps(metadata_dict)
        return lines

    def write_manifest(self):
        print("-- Handling manifest file! --")
        fs_manifest_path = os.path.join(self.frameshifted_tub_path, 'manifest.json')

        with open(fs_manifest_path, 'w') as f:
            for line in self.get_shifted_manifest_lines():
                f.write(line)
            print("Frameshifted manifest file created!")

    def get_shifted_catalog_angles(self):
        print("\tLoading all catalog df...")
        all_catalogs_df = self.data_loader.get_all_catalogs_df()
        
        # Multiplying by -1. 
        # A positive frame shift (such as 50ms, 1 frame on 20Hz) means that frame x will have the original angle of frame x+1.
        all_catalogs_df['user/angle_shifted'] = all_catalogs_df['user/angle'].shift(-1*self.frames_to_shift)

        # Replace NaNs with 0
        all_catalogs_df['user/angle_shifted'] = all_catalogs_df['user/angle_shifted'].fillna(0)

        # Replace original user/angle and then dropping the temporary column
        all_catalogs_df['user/angle'] = all_catalogs_df['user/angle_shifted']
        all_catalogs_df.drop(columns = ['user/angle_shifted'], axis = 1, inplace = True) 

        print("\tSeparating catalog dataframes...")
        # print(f"len(self.data_loader.catalog_paths): {len(self.data_loader.catalog_paths)}")

        separate_catalog_dfs = [all_catalogs_df[all_catalogs_df['catalog_nr'] == catalog_nr] for catalog_nr in range(len(self.data_loader.catalog_paths))]
        # separate_catalog_dfs = []
        # for catalog_nr in range(len(self.data_loader.catalog_paths)):
        #     print("\t\tcatalog_nr: {tcatalog_nr}")
        #     new_df = all_catalogs_df[all_catalogs_df['catalog_nr'] == catalog_nr]
        return separate_catalog_dfs

    def write_catalogs(self):
        print("-- Handling catalog files! -- ")
        separate_catalog_dfs = self.get_shifted_catalog_angles()
        # print(f"separate_catalog_dfs: {separate_catalog_dfs}")

        print(f"\tLooping through catalog dataframes!")
        for catalog_index, catalog_df in enumerate(separate_catalog_dfs):
            catalog_df.drop(['catalog_nr'], axis = 1, inplace = True)
            catalog_dict_array = catalog_df.to_dict(orient = 'records')
            # print(f"first element of catalog_dict_array: {catalog_dict_array[0]}")

            new_catalog_path = os.path.join(self.frameshifted_tub_path, 'catalog_' + str(catalog_index) + '.catalog')

            if os.path.exists(new_catalog_path):
                print(f"\t\tRemoving previously existing {'catalog_' + str(catalog_index) + '.catalog'} from frameshifted tub!")
                os.remove(new_catalog_path)

            with open(new_catalog_path, 'w') as f:
                for line in catalog_dict_array:
                    f.write(json.dumps(line) + "\n")
                print(f"\t\tWrote all lines into {'catalog_' + str(catalog_index) + '.catalog'}!")
        
        print("Catalog files done!")          


    def shift_frames(self):
        self.copy_images_to_fs_tub()
        self.copy_catalog_manifests()
        self.write_manifest()
        self.write_catalogs()
