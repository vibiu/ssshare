rm -rf /tmp/shadowsocks.sock \
    && ssserver --manager-address /tmp/shadowsocks.sock \
    -c conf/server.json -d start  \
    --pid-file data/ssserver.pid \
    --log-file data/ssserver.log
