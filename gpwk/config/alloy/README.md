# Grafana Alloy Docker Setup for GPWK

Run Grafana Alloy in Docker to collect OpenTelemetry signals from GPWK and forward them to Grafana Cloud.

## Quick Start

### 1. Get Grafana Cloud Credentials

Log in to your Grafana Cloud account and get the following:

#### A. OTLP Endpoint
1. Go to **Connections** → **Add new connection**
2. Search for "OpenTelemetry" and select **"OpenTelemetry (OTLP)"**
3. Copy the **OTLP Endpoint** (e.g., `https://otlp-gateway-prod-us-east-0.grafana.net/otlp`)

#### B. Instance ID and API Key
1. Go to **My Account** → **Cloud Portal**
2. Click on your stack
3. Go to **Access Policies** → **Create Access Policy**
4. Name it "GPWK Telemetry"
5. Add these scopes:
   - ✅ `metrics:write`
   - ✅ `logs:write`
   - ✅ `traces:write`
6. Click **Create** and then **Add token**
7. Copy the **Instance ID** (username) and **API Token** (password)

#### C. Prometheus Endpoint
1. In Grafana Cloud, go to **Prometheus**
2. Click **"Details"** on your Prometheus instance
3. Copy the **Remote Write Endpoint** URL

### 2. Configure Environment Variables

```bash
cd gpwk/config/alloy

# Copy the example file
cp .env.example .env

# Edit .env and fill in your credentials
# Use your favorite editor: nano, vim, code, etc.
nano .env
```

Your `.env` should look like:
```bash
# OTLP Configuration (for GPWK telemetry)
GRAFANA_CLOUD_OTLP_ENDPOINT=https://otlp-gateway-prod-us-east-0.grafana.net/otlp
GRAFANA_CLOUD_OTLP_USERNAME=123456  # From Connections → OpenTelemetry

# Prometheus Configuration (for Alloy meta-monitoring)
GRAFANA_CLOUD_PROMETHEUS_URL=https://prometheus-prod-01-us-east-0.grafana.net/api/prom/push
GRAFANA_CLOUD_PROMETHEUS_USERNAME=2731165  # From Prometheus → Details

# API Key (shared by both)
GRAFANA_CLOUD_API_KEY=glc_eyJrIjoiYWJjZGVm...
```

### 3. Start Grafana Alloy

```bash
# Start in detached mode (runs in background)
docker compose up -d

# View logs
docker compose logs -f grafana-alloy

# Check status
docker compose ps
```

You should see:
```
✅ Container gpwk-alloy  Running
```

And in the logs:
```
level=info component=otelcol.receiver.otlp.gpwk msg="Starting GRPC server" endpoint=0.0.0.0:4317
level=info component=otelcol.receiver.otlp.gpwk msg="Starting HTTP server" endpoint=0.0.0.0:4318
```

### 4. Verify Alloy is Running

Open http://localhost:12345 in your browser. You should see the Alloy UI showing:

- ✅ `otelcol.receiver.otlp.gpwk` - **healthy**
- ✅ `otelcol.processor.batch.default` - **healthy**
- ✅ `otelcol.exporter.otlp.grafana_cloud` - **healthy**

### 5. Test GPWK Capture

Now GPWK can send telemetry to Alloy:

```bash
# From the repository root
/gpwk.capture "Test Docker Alloy setup"
```

The telemetry flow:
```
GPWK Python → localhost:4317 → Alloy Container → Grafana Cloud
```

### 6. Verify in Grafana Cloud

1. **Traces**: Go to Grafana Cloud → Explore → Tempo → Search for `service_name=gpwk`
2. **Metrics**: Explore → Prometheus → Query: `{__name__=~"gpwk.*"}`
3. **Logs**: Explore → Loki → Query: `{service_name="gpwk"}`

## Management Commands

```bash
# Start Alloy
docker compose up -d

# Stop Alloy
docker compose down

# Restart Alloy (after config changes)
docker compose restart

# View logs
docker compose logs -f grafana-alloy

# View last 100 lines
docker compose logs --tail=100 grafana-alloy

# Check status
docker compose ps

# Remove everything (including volumes)
docker compose down -v
```

## Configuration

The Alloy configuration is in `gpwk.alloy`. It defines:

1. **OTLP Receiver** (`otelcol.receiver.otlp.gpwk`)
   - Listens on `0.0.0.0:4317` (gRPC)
   - Listens on `0.0.0.0:4318` (HTTP)
   - Receives traces, metrics, logs from GPWK

2. **Batch Processor** (`otelcol.processor.batch.default`)
   - Batches telemetry for efficiency
   - Timeout: 10s
   - Batch size: 1024

3. **OTLP Exporter** (`otelcol.exporter.otlp.grafana_cloud`)
   - Sends to Grafana Cloud via OTLP
   - Uses credentials from environment variables

4. **Meta-Monitoring** (`prometheus.exporter.self.alloy`)
   - Monitors Alloy itself
   - Sends Alloy metrics to Grafana Cloud

## Ports

| Port | Protocol | Purpose |
|------|----------|---------|
| 4317 | gRPC | OTLP receiver for GPWK telemetry |
| 4318 | HTTP | OTLP receiver (alternative) |
| 12345 | HTTP | Alloy Web UI |

All ports are exposed on `localhost` and accessible from your host machine.

## Troubleshooting

### Alloy container won't start

**Check logs**:
```bash
docker compose logs grafana-alloy
```

**Common issues**:
- Missing `.env` file → Copy from `.env.example`
- Invalid credentials → Check Grafana Cloud API key
- Port already in use → Check if another service is using ports 4317, 4318, or 12345

### No telemetry in Grafana Cloud

**1. Check Alloy health**:
- Open http://localhost:12345
- Verify all components show "healthy"

**2. Check Alloy logs**:
```bash
docker compose logs --tail=50 grafana-alloy | grep -i error
```

**3. Verify GPWK is sending to Alloy**:
```bash
# Check Alloy received data
docker compose logs grafana-alloy | grep -i "otlp"
```

**4. Test connectivity to Grafana Cloud**:
```bash
docker compose exec grafana-alloy wget --spider $GRAFANA_CLOUD_OTLP_ENDPOINT
```

### Update Alloy configuration

After editing `gpwk.alloy`:

```bash
# Restart to reload config
docker compose restart grafana-alloy

# Or do a full restart
docker compose down && docker compose up -d
```

### View Alloy component graph

1. Open http://localhost:12345
2. Click on the **Graph** tab
3. See visual representation of the telemetry pipeline

### Reset everything

```bash
# Stop and remove all containers, networks, volumes
docker compose down -v

# Start fresh
docker compose up -d
```

## Security Notes

- ✅ `.env` is gitignored (won't be committed to Git)
- ✅ API keys are only in environment variables
- ✅ Alloy runs in isolated container
- ✅ Only necessary ports are exposed
- ⚠️ Never commit `.env` to version control
- ⚠️ Rotate API keys if they are exposed

## Advanced: Running in Production

For production use, consider:

1. **Use Docker secrets** instead of environment variables
2. **Enable TLS** for OTLP endpoints
3. **Add resource limits**:
   ```yaml
   services:
     grafana-alloy:
       deploy:
         resources:
           limits:
             cpus: '1'
             memory: 512M
           reservations:
             memory: 256M
   ```
4. **Use a reverse proxy** (nginx/traefik) for Alloy UI
5. **Set up log rotation** for container logs
6. **Monitor Alloy itself** with alerts

## Architecture

```
┌──────────────────────────────────────┐
│ GPWK Python (gpwk_core)              │
│ - Generates traces, metrics, logs    │
│ - Exports via OTLP                   │
└─────────────┬────────────────────────┘
              │ OTLP (gRPC)
              │ localhost:4317
              ▼
┌──────────────────────────────────────┐
│ Docker Container: gpwk-alloy         │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ Grafana Alloy                    │ │
│ │                                  │ │
│ │ • Receives OTLP on 0.0.0.0:4317 │ │
│ │ • Batches signals                │ │
│ │ • Exports to Grafana Cloud      │ │
│ │ • Web UI on :12345              │ │
│ └──────────────────────────────────┘ │
└─────────────┬────────────────────────┘
              │ OTLP (HTTPS)
              │ Internet
              ▼
┌──────────────────────────────────────┐
│ Grafana Cloud                        │
│ - Tempo (traces)                     │
│ - Prometheus/Mimir (metrics)         │
│ - Loki (logs)                        │
│ - Grafana (dashboards)               │
└──────────────────────────────────────┘
```

## Dashboards

Pre-built Grafana dashboards are available in the `dashboards/` directory:

- **GPWK Metrics** (`dashboards/gpwk-metrics.json`) - Comprehensive dashboard for capture operations, GitHub API health, latency percentiles, and retry patterns

See `dashboards/README.md` for import instructions and dashboard documentation.

## Next Steps

1. ✅ Start Alloy with `docker compose up -d`
2. ✅ Test `/gpwk.capture "test"`
3. ✅ Verify telemetry in Grafana Cloud
4. ✅ Import dashboards from `dashboards/` directory
5. 🔔 Setup alerts for errors and carryovers
6. 📈 Analyze productivity patterns

Enjoy your observable productivity system! 🚀
