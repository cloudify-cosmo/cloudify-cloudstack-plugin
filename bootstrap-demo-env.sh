#!/bin/bash

virtualenv cfy-demo
. cfy-demo/bin/activate
cd cfy-demo
git clone https://github.com/schubergphilis/cloudify-cloudstack-plugin.git
cd cloudify-cloudstack-plugin
git checkout 3.1m5
cd ..
pip install cloudify-cloudstack-plugin/
git clone https://github.com/schubergphilis/cloudify-manager-blueprints.git
git clone https://github.com/schubergphilis/cloudify-nodecellar-example.git
pip install -r cloudify-cloudstack-plugin/dev-requirements.txt
cp cloudify-manager-blueprints/cloudstack/inputs.json.template cloudify-config.json
vi cloudify-config.json
vi cloudify-nodecellar-example/cloudstack-blueprint.yaml
cfy init -r
cfy bootstrap -p cloudify-manager-blueprints/cloudstack/cloudstack.yaml -i cloudify-config.json
