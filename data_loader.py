# from .. import donkeycar as local_dk
# from local_dk.donkeycar.pipeline.types import TubDataset, TubRecord
# from donkeycar_local.donkeycar.pipeline.types import TubDataset, TubRecord

# from donkeycar_local.donkeycar.pipeline.types import TubDataset, TubRecord

# import donkeycar_local

import donkeycar as dk
from donkeycar.pipeline.types import TubDataset, TubRecord
import numpy as np
import pandas as pd
import os


class DataLoader:

    def __init__(self, tub_name):
        self.tub_path = os.path.join('data', tub_name)
        self.cfg = dk.load_config(config_path = os.path.join('donkeycar', 'mycar', 'config.py'))
        self.catalog_paths = self.get_tub_dataset().tubs[0].manifest.catalog_paths

    def get_tub_element_path(self, element):
        return os.path.join(self.tub_path, element)

    def get_catalog_df(self, catalog_name):
        catalog_path = self.get_tub_element_path(catalog_name)
        catalog_df = pd.read_json(catalog_path, lines = True)
        catalog_df['catalog_nr'] = int(catalog_name.split('.')[0][8:])
        return catalog_df

    def get_tub_dataset(self):
        dataset = TubDataset(
            config = self.cfg,
            tub_paths = np.array([self.tub_path]),
            seq_size = 0
        )
        return dataset

    def get_all_catalogs_df(self):
        catalog_dfs = [self.get_catalog_df(catalog_name) for catalog_name in self.catalog_paths]
        all_catalogs_df = pd.concat(catalog_dfs)
        return all_catalogs_df

    def get_orig_manifest_lines(self):
        manifest_path = os.path.join(self.tub_path, 'manifest.json')
        with open(manifest_path, 'r') as f:
            return f.readlines()