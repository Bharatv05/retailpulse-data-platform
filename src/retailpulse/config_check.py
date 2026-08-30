import os 
from dotenv import load_dotenv

load_dotenv()

print("Current App Name: ", os.getenv("APP_ENV","Default Value"))