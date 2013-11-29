"""
(C) Copyright 2011, 10gen

Unless instructed by 10gen, do not modify default settings.

When upgrading your agent, you must also upgrade your settings.py file.
"""

#
# Seconds between Mongo status checks. Please do not change this.
#
collection_interval = 56

#
# Seconds between cloud configuration checks. Please do not change this.
#
conf_interval = 120

#
# Seconds between log data collection (if enabled in UI). Please do not change this.
#
log_interval = 5

#
# The mms server
#
mms_server = "https://mms.10gen.com"

#
# The mms ping url
#
ping_url = mms_server + "/ping/v1/%s"

#
# The mms config url
#
config_url = mms_server + "/conf/v2/%(key)s?am=true&ah=%(hostname)s&sk=%(sessionKey)s&av=%(agentVersion)s&sv=%(srcVersion)s"

#
# The mms agent version url
#
version_url = mms_server + "/agent/v1/version/%(key)s"

#
# The mms agent upgrade url
#
upgrade_url = mms_server + "/agent/v1/upgrade/%(key)s"

#
# The mms agent log path.
#
logging_url = mms_server + "/agentlog/v1/catch/%(key)s"

#
# Enter your API key  - See: http://mms.10gen.com/settings
#
mms_key = "0788b0eea2592b764695e7c7e8d7963a"

secret_key = "e25105c6674881bc13addc0415f80d53"

src_version = "1a5750de968efe6307227591132b3967db0523ed"

#
# Enabled by default
#
autoUpdateEnabled = True

#
# The global authentication credentials to be used by the agent.
#
# The user must be created on the "admin" database.
#
# If the global username/password is set then all hosts monitored by the
# agent *must* use the same username password.
#
# Example usage:
#
# globalAuthUsername="""yourAdminUser"""
# globalAuthPassword="""yourAdminPassword"""
#
#
# If you do not use this, the values must be set to None.
#
# Please use """ quotes to ensure everything is escaped properly.
#
# E.g.,
#
# globalAuthPassword="""yourAdminPasswordWith"DoubleQuotes"""
#
# globalAuthPassword="""yourAdminPasswordWith'SingleQuote"""
#
# For more information about MongoDB authentication, see:
#
# http://www.mongodb.org/display/DOCS/Security+and+Authentication
#
#

globalAuthUsername = None

globalAuthPassword = None

#
# Some config db collection properties
#
configCollectionsEnabled = True
configDatabasesEnabled = True

#
# Set to a specific bind address or 0.0.0.0 for all interfaces. Set to None to disable.
#
shutdownAgentBindAddr = None

#
# You must change the shutdown port if you run multiple agents on a machine.
#
shutdownAgentBindPort = 23017

#
# The shutdown agent bind challenge. You can change this to whatever you like. When
# you send a shutdown message to the agent, this must be the message sent.
#
shutdownAgentBindChallenge = '23237NYouCanChangeThis'

settingsAgentVersion = "1.4.2"

useSslForAllConnections = False

# Set to False if you have no plans to use munin (saves one thread per server)
enableMunin = True

# Misc - Please do not change this.
socket_timeout = 40

