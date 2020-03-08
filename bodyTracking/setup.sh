sudo apt-get update
sudo apt-get upgrade
sudo apt-get install libblas-dev
sudo apt-get install liblapack-dev
sudo apt-get install python-dev
sudo apt-get install libatlas-base-dev
sudo apt-get install gfortran

sudo apt-get install python3-pip 
python3 -m pip install --upgrade pip
python3 -m pip install virtualenv
python3 -m virtualenv -p python3 ~/neuro/
source ~/neuro/bin/activate
echo 'alias neuro="source ~/neuro/bin/activate"' >> ~/.bashrc
source ~/.bashrc

python -m pip install -r requirements.txt
