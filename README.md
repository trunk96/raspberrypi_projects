# Projects for Raspberry Pi

---

## Installation

First thing to do is clone this github repository:

```
git clone https://github.com/trunk96/raspberrypi_projects.git
```

then set the ``run.sh`` script to be owned by root:

```
sudo chmod 755 run.sh
sudo chown root:root run.sh
```

finally add the following line at the end of the ``/etc/rc.local`` file (just before the ``exit 0`` command):

```
/complete/path/to/your/cloned/repository/run.sh &
```

---
## Proxy Server

Once cloned the repository, the first thing to do is to start the proxy server. In such a way it is possible to bind different services into port :80.
Go to `proxy` and run:

```
sudo ./env/bin/python proxy.py &
```


## Shelly turn off automation

In order to start this service go to `home_automation` and run:

```
./env/bin/python turn_all_off.py &
```

to activate the service (it runs on port :8080).

This service exposes also the list of discovered shellies at `http://127.0.0.1/get_shellies` for any other service that requests them.

## Test service
In order to start this service go to `test` and run:

```
./env/bin/python test.py &
```

to activate the service (it runs on port :8081).
This service makes use of Shelly turn off automation one, so please start Test service after it.   
