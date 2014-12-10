#!/bin/bash

virtualenv cfy-demo
. cfy-demo/bin/activate
cd cfy-demo
pip install https://github.com/cloudify-cosmo/cloudify-dsl-parser/archive/master.zip
pip install https://github.com/cloudify-cosmo/cloudify-rest-client/archive/master.zip
pip install https://github.com/cloudify-cosmo/cloudify-plugins-common/archive/master.zip
pip install https://github.com/cloudify-cosmo/cloudify-script-plugin/archive/master.zip
pip install https://github.com/cloudify-cosmo/cloudify-cli/archive/master.zip
git clone https://github.com/schubergphilis/cloudify-manager-blueprints.git
git clone https://github.com/schubergphilis/cloudify-nodecellar-example.git
cp cloudify-manager-blueprints/cloudstack/inputs.json.template cloudify-config.json
vi cloudify-config.json
vi cloudify-manager-blueprints/cloudstack/cloudstack.yaml
cfy init -r
cfy bootstrap -p cloudify-manager-blueprints/cloudstack/cloudstack.yaml -i cloudify-config.json --install-plugins
