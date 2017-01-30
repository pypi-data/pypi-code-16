def upstart_script_template(script, script_name, author):
    return """description "%(script_name)s"
author "%(author)s"

pre-start script
  mkdir -p /var/log/app
  chown -R root /var/log/app

  while [ ! -f "/tmp/envvars" ]; # wait for envvars to be available, before starting up
  do
    sleep 5
    logger -i -t "$UPSTART_JOB" "Waiting 5s for /tmp/envvars to be available..."
  done
  size=`ls -lah /tmp/envvars | awk '{ print $5 }'`
  logger -i -t "$UPSTART_JOB" "Found /tmp/envvars, size: ${size}"


  while [ ! -f "/credentials/settings.yml" ]; # wait for envvars to be available, before starting up
  do
    sleep 5
    logger -i -t "$UPSTART_JOB" "Waiting 5s for /credentials/settings.yml to be available..."
  done
  size=`ls -lah /credentials/settings.yml | awk '{ print $5 }'`
  logger -i -t "$UPSTART_JOB" "Found /credentials/settings.yml, size: ${size}"
end script

start on runlevel [2345]

respawn
respawn limit 1000 1
console log
chdir /app/

script
  logger -i -t "$UPSTART_JOB" "Starting app"
  . /tmp/envvars
  exec %(script)s >> /var/log/app/%(script_name)s.log 2>&1
end script
    """.replace("$", "\$").replace('`', '\`') % {
        'script_name': script_name,
        'author': author,
        'script': script,
    }