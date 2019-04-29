import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config( 
    cloud_name = "hexai", 
    api_key = "681533659713834", 
    api_secret = "ie2CJwfsgLhovE9azB0Db4P4x7E" 
)

dir_path = "images/"

def upload(local_path):
    # print("Local Path : " + local_path)
    response = cloudinary.uploader.upload(dir_path + local_path)
    # print(response)
    return response