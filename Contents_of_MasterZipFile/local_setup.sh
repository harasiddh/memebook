#! /bin/sh
echo "======================================================================"
echo "Welcome to the setup. This will setup the local virtual env."
echo "And then it will install all the required python libraries."
echo "You can rerun this without any issues."
echo "----------------------------------------------------------------------"
if [ -d ".env" ];
then
    echo ".env folder exists. Installing using pip"
else
    echo "creating .env and install using pip"
    python3 -m venv .env
fi

# Activate virtual env
. .env/bin/activate

# Upgrade the PIP
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
# Work done. so deactivate the virtual env
deactivate
