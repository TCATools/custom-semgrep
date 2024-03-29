FROM busybox

# ruleid: use-absolute-workdir
WORKDIR usr/src/app

# ok: use-absolute-workdir
WORKDIR /usr/src/app

ENV dirpath=bar
# ruleid: use-absolute-workdir
WORKDIR ${dirpath}   # WORKDIR bar

ENV dirpath=/bar
# ok: use-absolute-workdir
WORKDIR ${dirpath}   # WORKDIR /bar
