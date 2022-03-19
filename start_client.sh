# assign name for virtual environment
env=iot-client-TEST
# initialise the command line arguments
method=post
device_id=TEMP001
device_type=temp
interval=1
# set up and install the virtual environment
python3 -m venv $env
source $env/bin/activate
pip install -r requirements.txt
# start the client
python3 iot.py $method $device_id $device_type -i $interval