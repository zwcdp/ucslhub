ARG JUPYTERHUB_VERSION=0.9.2
FROM jupyterhub/jupyterhub:${JUPYTERHUB_VERSION}

LABEL maintainer="Mohit Sharma <Mohitsharma44@gmail.com>"

# Add dockerspawner
ADD dockerspawner /tmp/dockerspawner
# Install oAuthenticator
RUN pip install --no-cache oauthenticator /tmp/dockerspawner/
# load configuration
COPY jupyterhub_config.py admins.txt teaching_assistants.txt /srv/jupyterhub/
