Cloudify CloudStack Plugin
==========================

* Master Branch [![Build Status](https://travis-ci.org/cloudify-cosmo/cloudify-cloudstack-plugin.svg?branch=master)](https://travis-ci.org/cloudify-cosmo/cloudify-cloudstack-plugin)
* PyPI [![PyPI](http://img.shields.io/pypi/dm/cloudify-cloudstack-plugin.svg)](http://img.shields.io/pypi/dm/cloudify-cloudstack-plugin.svg)
* Version [![PypI](http://img.shields.io/pypi/v/cloudify-cloudstack-plugin.svg)](http://img.shields.io/pypi/v/cloudify-cloudstack-plugin.svg)

Cloudify's CloudStack plugin provides the ability to create [CloudStack](http://cloudstack.apache.org/) resources using Cloudify.

# Get started

You'll need access to a cloudstack cloud with advanced networking, e.g support for VPC and Isolated networking

Very condensed HOWTO, more to follow:

* cd ~
* virtualenv cfy-demo
* cd ~/cfy-demo
* source bin/activate
* pip install https://github.com/cloudify-cosmo/cloudify-dsl-parser/archive/master.zip
* pip install https://github.com/cloudify-cosmo/cloudify-rest-client/archive/master.zip
* pip install https://github.com/cloudify-cosmo/cloudify-plugins-common/archive/master.zip
* pip install https://github.com/cloudify-cosmo/cloudify-script-plugin/archive/master.zip
*pip install https://github.com/cloudify-cosmo/cloudify-cli/archive/master.zip
* git clone https://github.com/schubergphilis/cloudify-manager-blueprints.git
* git clone https://github.com/schubergphilis/cloudify-nodecellar-example.git
* cp cloudify-manager-blueprints/cloudstack/inputs.json.template cloudify-config.json
* vi cloudify-config.json - fill in your cloud specific details
* vi cloudify-nodecellar-example/cloudstack-vpc-blueprint.yaml - edit it with your specifics (service offerings , fw settings and such)
* cfy init -r
* cfy bootstrap -p cloudify-manager-blueprints/cloudstack/cloudstack.yaml -i cloudify-config.json --install-plugins
* at this stage your manager will be deployed fingers crossed :)
* look at the returned public ip - should be accessible in your browser
* cfy blueprints upload -p cloudify-nodecellar-example/cloudstack-vpc-blueprint.yaml b my-first-blueprint
* surf to http://your-manager-ip
* start the install workflow in the webui
* fingers-crossed - if all ok - your sample app should be accessible on port :8080

OR

* cd ~
* wget https://raw.githubusercontent.com/schubergphilis/cloudify-cloudstack-plugin/master/bootstrap-demo-env.sh
* ./bootstrap-demo-env.sh
* 1st prompt: edit json with your cloudstack details
* 2nd prompt: edit this YAML with your specifics, especially the firewall bits
* Your manager should be bootstrapping
* browse to the returned IP
* * cfy blueprints upload -p cloudify-nodecellar-example/cloudstack-vpc-blueprint.yaml b my-first-blueprint
* surf to http://your-manager-ip
* start the install workflow in the webui
* fingercrossed - if all ok - your sample app should be accessible on port :8080

If you are here without problems, good for me :)
If not: rkuipers@schubergphilis.com, cloudify dev-list, irc-channel or twitter @\_BouL\_


##Disclaimer

The code in this repository has been contributed by the Cloudify community (thanks [Roeland Kuipers](https://github.com/boul)). We intend to put it through our comprehensive testing framework in the near future, but until then please note that it's considered experimental and provided as is.
