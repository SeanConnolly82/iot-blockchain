# ================================  INSTALL OTHER COMPONENTS ============================== #

# # Install GIT
# sudo apt-get install git

# # Install curl
# sudo apt-get install curl

# # Install Influx DB
# sudo curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
# sudo echo "deb https://repos.influxdata.com/ubuntu bionic stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
# sudo apt update
# sudo apt install influxdb
# sudo systemctl start influxdb

# # Install telegraf
# sudo apt-get update
# sudo apt-get install telegraf
# sudo systemctl start telegraf

# # Commands to run on InfluxDB
# influx
# CREATE DATABASE metrics;
# USE metrics;
# CREATE USER lrdata WITH PASSWORD 'Edge' WITH ALL PRIVILEGES;

# ==============================  INSTALL SAWTOOTH COMPONENTS ============================= #

# # Add stable Sawtooth repository
# sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8AA7AF1F1091A5FD
# sudo add-apt-repository 'deb [arch=amd64] http://repo.sawtooth.me/ubuntu/chime/stable bionic universe'
# sudo apt-get update

# # Install the Sawtooth packages
# sudo apt-get install -y sawtooth

# # Install the Sawtooth PoET consensus engine package
# sudo apt-get install -y sawtooth \
# python3-sawtooth-poet-cli \
# python3-sawtooth-poet-engine \
# python3-sawtooth-poet-families

# # Install the Sawtooth PBFT consensus engine package
# sudo apt-get install -y sawtooth sawtooth-pbft-engine

# # Install the Sawtooth Devmode consensus engine package
# sudo apt-get install sawtooth-devmode-engine-rust

# # View installed packages
# dpkg -l '*sawtooth*'

# # Add pkg-config, required for sawtooth_sdk
# sudo apt-get install pkg-config

# # Add version 0.13.2 of secp
# pip3 install secp256k1=0.13.2

# # Install the Sawtooth SDK for python
# pip3 install sawtooth_sdk

# # Update Python protobuf
# sudo apt install python3-protobuf

# # Generate a user key
# user=$HOSTNAME
# echo "The name of the key is "$user
# sawtooth keygen $user

# # Generate validator key
# sudo sawadm keygen

# ===================== COMMENT EITHER DEVMODE OR POET FROM SELECTION ===================== #

# # Create the Genesis Block
# cd /tmp
# sawset genesis --key $HOME/.sawtooth/keys/$user.priv -o config-genesis.batch

# ========================================= POET ========================================== #

# # Initialize the PoET consensus engine
# sawset proposal create --key $HOME/.sawtooth/keys/$user.priv \
# -o config-consensus.batch \
# sawtooth.consensus.algorithm.name=PoET \
# sawtooth.consensus.algorithm.version=0.1 \
# sawtooth.poet.report_public_key_pem="$(cat /etc/sawtooth/simulator_rk_pub.pem)" \
# sawtooth.poet.valid_enclave_measurements=$(poet enclave measurement) \
# sawtooth.poet.valid_enclave_basenames=$(poet enclave basename)

# # Create a batch to register the first Sawtooth node
# sudo poet registration create --key /etc/sawtooth/keys/validator.priv -o poet.batch

# # Create a batch to configure other consensus settings
# sawset proposal create --key $HOME/.sawtooth/keys/$user.priv \
# -o poet-settings.batch \
# sawtooth.poet.target_wait_time=5 \
# sawtooth.poet.initial_wait_time=25 \
# sawtooth.publisher.max_batches_per_block=100

# # Combine the separate batches into a single genesis batch 
# sudo -u sawtooth sawadm genesis \
# config-genesis.batch config-consensus.batch poet.batch poet-settings.batch

# ======================================== DEVMODE ======================================== #

# # Initialize the Devmode consensus engine
# sawset proposal create \
# --key $HOME/.sawtooth/keys/$user.priv \
# sawtooth.consensus.algorithm.name=Devmode \
# sawtooth.consensus.algorithm.version=0.1 -o config.batch

# # Combine the separate Devmode batches into a single genesis batch 
# sudo -u sawtooth sawadm genesis config-genesis.batch config.batch

# ========================================== PBFT ========================================== #

# sawset proposal create --key $HOME/.sawtooth/keys/my_key.priv \
# -o config-consensus.batch \
# sawtooth.consensus.algorithm.name=pbft \
# sawtooth.consensus.algorithm.version=1.0 \
# sawtooth.consensus.pbft.members='["VAL1KEY","VAL2KEY",...,"VALnKEY"]'

# sudo -u sawtooth sawadm genesis \
# config-genesis.batch config-consensus.batch pbft-settings.batch

# ================================== TRANSACTOR POLICY ===================================== #

# # Generate a user key for the Raspberry Pi
# sawtooth keygen raspberrypi

# # Add public key to the list of those allowed to change settings
# sudo sawset proposal create --key ~/.sawtooth/keys/$user.priv   
#  sawtooth.identity.allowed_keys=$(cat ~/.sawtooth/keys/$user.pub) --url http://192.168.0.165:8008

# # Create an IoT Policy with the approved public keys including the Raspberry Pi key
# sawtooth identity policy create iot_policy \
#  "PERMIT_KEY $(cat ~/.sawtooth/keys/raspberrypi.pub)" \ 
#  "PERMIT_KEY $(cat ~/.sawtooth/keys/$user.pub)" \
#  "DENY_KEY *" --key ~/.sawtooth/keys/$user.priv --url http://192.168.0.165:8008

# # Assign the IoT Policy to the transactor role
# sawtooth identity role create transactor iot_policy \
#  --key ~/.sawtooth/keys/$user.priv --url http://192.168.0.165:8008

# ==================================== START PROCESSES ===================================== #

# # Start the validator
# sudo -u sawtooth sawtooth-validator \
# --bind component:tcp://127.0.0.1:4004 \
# --bind network:tcp://192.168.0.164:8800 \
# --bind consensus:tcp://192.168.0.164:5050 \
# --endpoint tcp://192.168.0.164:8800 -vv

# # Start the Rest API
# sudo -u sawtooth sawtooth-rest-api -vv -B 192.168.0.164:8008

# # Start the settings tp
# sudo -u sawtooth settings-tp -vv

# # Start the identity tp
# identity-tp -v

# # start the PoET Validator Registry transaction processor
# sudo -u sawtooth poet-validator-registry-tp -vv

# # Start PoET consensus engine
# sudo -u sawtooth poet-engine -vv

# # start the Devmode Validator Registry transaction processor
# sudo -u sawtooth devmode-engine-rust -vv --connect tcp://192.168.0.164:5050

# =================================== START/STOP SERVICES ================================== #

# # Start the Sawtooth services
# sudo systemctl start sawtooth-rest-api.service
# sudo systemctl start sawtooth-validator.service
# sudo systemctl start sawtooth-settings-tp.service
# sudo systemctl start sawtooth-poet-validator-registry-tp.service
# sudo systemctl start sawtooth-poet-engine.service

# # Stop the Sawtooth services
# sudo systemctl stop sawtooth-rest-api.service
# sudo systemctl stop sawtooth-validator.service
# sudo systemctl stop sawtooth-settings-tp.service
# sudo systemctl stop sawtooth-poet-validator-registry-tp.service
# sudo systemctl stop sawtooth-poet-engine.service