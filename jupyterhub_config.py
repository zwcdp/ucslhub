import os
# Teaching Assistants (these will be able to create and modify assignments)
teaching_assistants = ['syn']

# The proxy is in another container
c.ConfigurableHTTPProxy.should_start = False
c.ConfigurableHTTPProxy.api_url = 'http://proxy:8001'

# use oauth
c.JupyterHub.authenticator_class = 'oauthenticator.generic.GenericOAuthenticator'
c.OAuthenticator.client_id = os.environ['OAUTH2_CLIENTID']  # oauth2 client id for your app
c.OAuthenticator.client_secret =  os.environ['OAUTH2_CLIENT_SECRET']  # oauth2 client secret for your app..
c.GenericOAuthenticator.token_url = os.environ['OAUTH2_TOKEN_URL'] # oauth2 provider's token url
c.GenericOAuthenticator.userdata_url = os.environ['OAUTH2_USERDATA_URL'] # oauth2 provider's endpoint with user data
c.GenericOAuthenticator.userdata_method = 'GET'  # method used to request user data endpoint
c.GenericOAuthenticator.userdata_params = {"state": "state"} # params to send for userdata endpoint
c.GenericOAuthenticator.username_key = "preferred_username"  # username key from json returned from user data endpoint

# use SwarmSpawner
# Mount user directory
import pwd
def mount_user_dirs(spawner):
    username = spawner.user.name
    basedir = os.environ['JUPYHOST_BASEDIR']
    userpath = os.path.join(basedir, username)
    if not os.path.exists(userpath):
        os.makedirs(userpath)
        # this is run as root, so chown to uscluser
        # get uid and gid for ucsluser
        uid = 1002 #pwd.getpwnam('ucsluser').pw_uid
        gid = 1002 #pwd.getpwnam('ucsluser').pw_gid
        os.chown(userpath, uid, gid)
    mounts_user = [
        {'type': 'bind',
         'source': os.path.join(basedir, username),
         'target': '/home/jovyan/{}'.format(username)}
    ]
    spawner.extra_container_spec = {'mounts': mounts_user}
    spawner.notebook_dir = '/home/jovyan/{}'.format(username)
    if username in teaching_assistants:
        spawner.image = os.environ['HUB_TA_IMAGE']
    else:
        spawner.image = os.environ['HUB_STUDENT_IMAGE']


c.Spawner.pre_spawn_hook = mount_user_dirs
c.JupyterHub.spawner_class = 'dockerspawner.SwarmSpawner'
c.SwarmSpawner.extra_placement_spec = { 'constraints' : ['node.labels.type==ucslworker'] }

# Culling
c.JupyterHub.services = [
    {
        'name': 'cull-idle',
        'admin': True,
        'command': [sys.executable, '/tmp/dockerspawner/tools/cull_idle_servers.py', '--timeout=3600'],
    }
]

# Messing around with JupyterHub
c.JupyterHub.template_paths = ['/tmp/dockerspawner/templates']

# The Hub should listen on all interfaces,
# so user servers can connect
c.JupyterHub.hub_ip = '0.0.0.0'
# this is the name of the 'service' in docker-compose.yml
c.JupyterHub.hub_connect_ip = 'hub'
# this is the network name for jupyterhub in docker-compose.yml
c.SwarmSpawner.network_name = 'ucslhub_jupynet'
c.SwarmSpawner.use_internal_ip = True
#c.SwarmSpawner.extra_host_config = {'network_mode': 'jupyterhub_jupynet'}
#c.SwarmSpawner.remove_services = True
#c.Spawner.mem_limit = '1G'
#c.Spawner.cpu_limit = 2

# start jupyterlab
c.Spawner.pre_spawn_hook = mount_user_dirs
c.Spawner.cmd = ["jupyter", "labhub"]
c.SwarmSpawner.debug = True
c.Spawner.args = ['--NotebookApp.allow_origin=*']

# debug-logging for testing
import logging
c.JupyterHub.log_level = logging.DEBUG