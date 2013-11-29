Project RHTEST page
===================

.. literalinclude:: README


Launcher:
---------

   ./bin/launcher --help

To run particular testecases selected by tags against EC2 instance tagged by 'QE_user-dev':
   ./bin/launcher -t "Test by sprint22 tag" -g sprint22 -A QE_user-dev


Following example will run the same tests against current devenv AMI-ID:

   ./bin/launcher -t "Test by sprint22 tag" -g sprint22 


Environment variables:
----------------------

* RHTEST_DEBUG
* RHTEST_HOME
* RHTEST_ARGS
* RHTEST_REST_TIMEOUT
* RHTEST_RHC_CLIENT_OPTIONS
* OPENSHIFT_libra_server
* OPENSHIFT_user_email
* OPENSHIFT_user_passwd
