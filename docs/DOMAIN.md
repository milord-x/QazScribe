# qtranscript.kz Domain Setup

## Goal

The production public address should be:

```text
https://qtranscript.kz
```

The application can also answer:

```text
https://www.qtranscript.kz
```

## DNS Records

At the domain registrar or DNS provider, create:

```text
Type: A
Name: @
Value: SERVER_PUBLIC_IP

Type: A
Name: www
Value: SERVER_PUBLIC_IP
```

Replace `SERVER_PUBLIC_IP` with the public IPv4 address of the server or router
that forwards traffic to the server.

For Hoster.kz, this is done in the personal cabinet through domain DNS
management / DNS-hosting records. The exact UI can change, but the target result
is still two A records: root domain and `www`.

Find the public IP on the server:

```bash
curl -4 ifconfig.me
```

or:

```bash
curl -4 https://api.ipify.org
```

Use the returned IPv4 address as `SERVER_PUBLIC_IP`.

If the server is behind a router, forward these ports to the server:

```text
80/tcp
443/tcp
```

This is configured in the router or firewall at the physical network where the
server is installed, not in Hoster.kz. Find the server local network IP:

```bash
hostname -I
```

Example result:

```text
192.168.1.45
```

Router forwarding example:

```text
WAN 80  -> 192.168.1.45:80
WAN 443 -> 192.168.1.45:443
```

## Docker Port

For direct domain access without `:8080`, the server `.env` should include:

```text
QAZSCRIBE_HTTP_PORT=80
```

Docker Compose maps that host port to the Nginx container. Because the value is
kept in `backend/.env`, start Compose with:

```bash
docker compose --env-file backend/.env up -d --build
```

## Start

```bash
cd /media/proart/ssd/qazscribe/repo/QazScribe
docker compose down
git pull
docker compose --env-file backend/.env up -d --build
```

Check locally:

```bash
curl -I http://127.0.0.1/
```

Check by domain after DNS propagation:

```bash
curl -I http://qtranscript.kz/
```

## HTTPS

For a serious presentation, use HTTPS. Two practical options:

### Option A: Cloudflare

Move DNS to Cloudflare or use Cloudflare DNS records. Enable proxying for
`qtranscript.kz` and `www`. Cloudflare can provide HTTPS in front of the server.

### Option B: Certbot on the host

Install Certbot and issue certificates for:

```text
qtranscript.kz
www.qtranscript.kz
```

Then place a TLS reverse proxy on the host in front of the Docker Nginx service.

## Unknowns

The repository cannot complete DNS setup by itself. The operator must provide:

- DNS panel access or the exact DNS provider;
- server public IP;
- router/firewall access if the server is behind NAT.
