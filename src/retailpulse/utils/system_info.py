import platform
import sys
def sys_info():
    print("Python Version: ", platform.python_version())
    print("=="*8)
    print("Operating System: ",platform.system())
    print("=="*8)
    print("Environment Name: ",sys.prefix)
    print("=="*8)
    print("Is it Virtual Environment? ", sys.prefix != sys.base_prefix)
    return ""

if __name__ == "__main__":
    sys_info()