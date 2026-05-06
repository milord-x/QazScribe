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

If the server is behind a router, forward these ports to the server:

```text
80/tcp
443/tcp
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
