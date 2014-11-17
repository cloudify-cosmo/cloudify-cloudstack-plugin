Cloudify CloudStack Plugin
==========================

Cloudify's CloudStack plugin provides the ability to create [CloudStack](http://cloudstack.apache.org/) resources using Cloudify.

# Get started

You'll need access to a cloudstack cloud with advanced networking, e.g support for VPC and Isolated networking

Very condensed HOWTO, more to follow:

* cd ~
* virtualenv cfy-demo
* cd ~/cfy-demo
* source bin/activate
* git clone https://github.com/schubergphilis/cloudify-cloudstack-plugin.git
* cd cloudify-cloudstack-plugin
* git checkout 3.1m5
* cd ..
* pip install cloudify-cloudstack-plugin/
* git clone https://github.com/schubergphilis/cloudify-manager-blueprints.git
* git clone https://github.com/schubergphilis/cloudify-nodecellar-example.git
* pip install -r cloudify-cloudstack-plugin/dev-requirements.txt
* cp cloudify-manager-blueprints/cloudstack/inputs.json.template cloudify-config.json
* vi cloudify-config.json - fill in your cloud specific details
* vi cloudify-nodecellar-example/cloudstack-vpc-blueprint.yaml - edit it with your specifics (service offerings , fw settings and such)
* cfy init -r
* cfy bootstrap -p cloudify-manager-blueprints/cloudstack/cloudstack.yaml -i cloudify-config.json
* at this stage your manager will be deployed fingers crossed :)
* look at the returned public ip - should be accessible in your browser
* cfy blueprints upload -p cloudify-nodecellar-example/cloudstack-vpc-blueprint.yaml b my-first-blueprint
* surf to http://your-manager-ip
* start the install workflow in the webui
* fingercrossed - if all ok - your sample app should be accessible on port :8080

OR

* cd ~
* wget https://raw.githubusercontent.com/schubergphilis/cloudify-cloudstack-plugin/3.1m5/bootstrap-demo-env.sh
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
