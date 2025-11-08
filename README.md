
# Install appropriate dependencies

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Deploy Stack

cdk synth
cdk bootstrap # at a first run
cdk deploy