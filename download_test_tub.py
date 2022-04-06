import gdown
import zipfile
import os

gdown.download('https://drive.google.com/uc?export=download&id=19H0aAuTy4homTugpQQ4eUvSN6vS-JeWn', '20hz_test_tub.zip', quiet=False)

print("Unzipping test data...")
with zipfile.ZipFile("20hz_test_tub.zip", 'r') as zip_ref:
    zip_ref.extractall("./data")

os.remove("20hz_test_tub.zip")   
print("Test tub downloaded and unzipped at ./data!")