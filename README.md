Cloudify CloudStack Plugin
==========================

Cloudify's CloudStack plugin provides the ability to create [CloudStack](http://cloudstack.apache.org/) resources using Cloudify.

# Get started

You'll need access to a cloudstack cloud with advanced networking, e.g support for VPC and Isolated networking

Very condensed HOWTO, more to follow:

* cd~
* virtualenv cfy-demo
* cd ~/cfy-demo
* git clone https://github.com/schubergphilis/cloudify-cloudstack-plugin.git
* git clone https://github.com/schubergphilis/cloudify-manager-blueprints.git
* git clone https://github.com/schubergphilis/cloudify-nodecellar-example
* pip install -r cloudify-cloudstack-plugin/dev-requirements.txt
* cp cloudify-manager-blueprints/cloudstack/inputs.json.template ~/cfy-demo/cloudify-config.json
* vi cloudify-config.json - fill in your cloud specific details
* vi cloudify-nodecellar-example/cloudstack-blueprint.yaml - should not need much editing, check firewall:
* cfy init -r
* cfy bootstrap -p cloudify-manager-blueprints/cloudstack.yaml -i cloudify-config.json
* at this stage your manager will be deployed fingers crossed :)
* look at the returned public ip - should be accessible in your browser
* cfy blueprints upload -p cloudify-nodecellar-example/cloudstack-blueprint.yaml b my-first-blueprint
* surf to http://your-manager-ip
* go to blueprints and click create deployment - fill in cs-api-url and keys
* deploy!
* fingercrossed - if all ok - your sample app should be accessible on port :8080

If you are here without problems, good for me :)
If not: rkuipers@schubergphilis.com, cloudify dev-list, irc-channel or twitter @_BouL_


##Disclaimer

The code in this repository has been contributed by the Cloudify community (thanks [Roeland Kuipers](https://github.com/boul)). We intend to put it through our comprehensive testing framework in the near future, but until then please note that it's considered experimental and provided as is.
