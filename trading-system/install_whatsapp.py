import subprocess
import sys

def install_whatsapp_requirements():
    requirements = [
        'whatsapp-business-api==1.0.0',
        'requests==2.31.0',
        'twilio==8.0.0'
    ]
    
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"تم تثبيت {package} بنجاح")
        except subprocess.CalledProcessError:
            print(f"فشل تثبيت {package}")

if __name__ == "__main__":
    install_whatsapp_requirements()
