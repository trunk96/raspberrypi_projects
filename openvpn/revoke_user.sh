OVPN_DATA="ovpn-data-casa"
docker run -v $OVPN_DATA:/etc/openvpn --rm openvpn-server easyrsa revoke $1
