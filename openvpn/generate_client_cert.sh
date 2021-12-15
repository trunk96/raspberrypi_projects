OVPN_DATA="ovpn-data-casa"
docker run -v $OVPN_DATA:/etc/openvpn --rm -it openvpn-server easyrsa build-client-full $1 nopass
docker run -v $OVPN_DATA:/etc/openvpn --rm openvpn-server ovpn_getclient $1 > $1.ovpn
