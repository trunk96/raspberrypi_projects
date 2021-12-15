git clone https://github.com/kylemanna/docker-openvpn.git docker-openvpn
OVPN_DATA="ovpn-data-casa"
docker volume create --name $OVPN_DATA
docker build -t openvpn-server:latest ./docker-openvpn
docker run -v $OVPN_DATA:/etc/openvpn --rm openvpn-server ovpn_genconfig -u udp://VPN.SERVERNAME.COM
docker run -v $OVPN_DATA:/etc/openvpn --rm -it openvpn-server ovpn_initpki
