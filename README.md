# Projects for Raspberry Pi

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

to activate the service (it runs on port :8080)
