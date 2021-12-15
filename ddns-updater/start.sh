docker run -d -p 8886:8000 -v "$(pwd)"/ddns-updater:/updater/data -e IPV6_PREFIX=/64 -e LOG_LEVEL=info --name ddns-updater --restart unless-stopped qmcgaw/ddns-updater
