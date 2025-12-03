from dotenv import load_dotenv
import os

load_dotenv()
print("MONGODB_URI =", os.getenv("MONGODB_URI"))
print("MONGODB_DB =", os.getenv("MONGODB_DB"))
