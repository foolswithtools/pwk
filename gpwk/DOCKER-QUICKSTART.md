# GPWK + Grafana Alloy Docker: Quick Start Guide

**Goal**: Get GPWK sending telemetry to Grafana Cloud in 5 minutes using Docker.

## Prerequisites

- ✅ Docker and Docker Compose installed
- ✅ Grafana Cloud account (free tier: https://grafana.com)
- ✅ Python dependencies already installed (we did this!)

## Step-by-Step Setup

### Step 1: Get Grafana Cloud Credentials (3 minutes)

#### 1.1 Get OTLP Endpoint
1. Log in to https://grafana.com
2. Go to **Connections** → **Add new connection**
3. Search "OpenTelemetry" → Select "OpenTelemetry (OTLP)"
4. Copy the **OTLP Endpoint**
   - Example: `https://otlp-gateway-prod-us-east-0.grafana.net/otlp`

#### 1.2 Create API Token
1. Go to **My Account** → **Cloud Portal**
2. Click your stack → **Access Policies**
3. **Create Access Policy** named "GPWK Telemetry"
4. Add scopes: `metrics:write`, `logs:write`, `traces:write`
5. Click **Create** → **Add token**
6. Save:
   - **Instance ID** (username number like `123456`)
   - **API Token** (long string starting with `glc_`)

#### 1.3 Get Prometheus Endpoint
1. In Grafana Cloud, go to **Prometheus**
2. Click **Details** on your instance
3. Copy **Remote Write Endpoint**
   - Example: `https://prometheus-prod-01-us-east-0.grafana.net/api/prom/push`

### Step 2: Configure Environment (1 minute)

```bash
cd gpwk/config/alloy

# Copy the example file
cp .env.example .env

# Edit with your credentials
nano .env
```

Fill in your values:
```bash
# OTLP Configuration (for GPWK telemetry)
GRAFANA_CLOUD_OTLP_ENDPOINT=https://otlp-gateway-prod-us-east-0.grafana.net/otlp
GRAFANA_CLOUD_OTLP_USERNAME=123456  # From Connections → OpenTelemetry

# Prometheus Configuration (for Alloy meta-monitoring)
GRAFANA_CLOUD_PROMETHEUS_URL=https://prometheus-prod-01-us-east-0.grafana.net/api/prom/push
GRAFANA_CLOUD_PROMETHEUS_USERNAME=123456  # From Prometheus → Details

# API Key (shared by both)
GRAFANA_CLOUD_API_KEY=glc_eyJrIjoiYWJjZGVm...  # Your actual token
```

Save and exit (Ctrl+X, Y, Enter in nano).

### Step 3: Start Grafana Alloy (30 seconds)

```bash
# From gpwk/config/alloy directory
docker compose up -d
```

Expected output:
```
✅ Container gpwk-alloy  Started
```

**Verify it's running**:
```bash
# Check status
docker compose ps

# Should show:
# NAME         STATUS   PORTS
# gpwk-alloy   Up       0.0.0.0:4317->4317/tcp, 0.0.0.0:4318->4318/tcp, 0.0.0.0:12345->12345/tcp
```

**Check the Web UI**:
Open http://localhost:12345 in your browser.

You should see all components showing **"healthy"**:
- ✅ `otelcol.receiver.otlp.gpwk`
- ✅ `otelcol.processor.batch.default`
- ✅ `otelcol.exporter.otlp.grafana_cloud`

### Step 4: Test GPWK Capture (30 seconds)

```bash
# Go back to repository root
cd /path/to/your/repo

# Test 1: Simple capture
/gpwk.capture "Testing Docker Alloy setup with telemetry"
```

Expected output:
```
✓ Captured: Testing Docker Alloy setup with telemetry
  Issue: #46 (https://github.com/OWNER/REPO/issues/46)
  Duration: XXXms

  Run /gpwk.triage to move to Today/This Week
```

```bash
# Test 2: Special characters (tests the escaping fix)
/gpwk.capture "Test with (parentheses) and 'quotes' works!"

# Test 3: Completed activity (tests completion detection)
/gpwk.capture "I tested the Docker setup between 10:00-10:15. This is complete."
```

### Step 5: Verify Telemetry in Grafana Cloud (1 minute)

#### View Traces
1. Go to Grafana Cloud
2. **Explore** → Select **Tempo** data source
3. Search for: `service_name="gpwk"`
4. Click on a trace to see the breakdown:
   ```
   gpwk_capture (543ms)
     ├─ parse (12ms)
     ├─ create_issue (234ms)
     ├─ add_to_project (89ms)
     │   └─ retry_attempt_2 (15ms) ← See retries!
     ├─ set_fields (156ms)
     └─ update_log (52ms)
   ```

#### View Metrics
1. **Explore** → Select **Prometheus** data source
2. Query: `{__name__=~"gpwk.*"}`
3. You should see metrics like:
   - `gpwk_capture_total`
   - `gpwk_capture_duration_bucket`
   - `gpwk_github_api_latency_bucket`

#### View Logs
1. **Explore** → Select **Loki** data source
2. Query: `{service_name="gpwk"}`
3. See structured logs with trace IDs

---

## You're Done! 🎉

Your GPWK system is now fully observable!

```
GPWK Python → localhost:4317 → Alloy Container → Grafana Cloud
```

## Common Commands

```bash
# View Alloy logs
cd gpwk/config/alloy
docker compose logs -f grafana-alloy

# Restart Alloy
docker compose restart

# Stop Alloy
docker compose down

# Start Alloy
docker compose up -d
```

## What's Next?

### 1. Build a Dashboard
Let me know when you're ready and I'll help you create a Grafana dashboard showing:
- Task completion rates over time
- GitHub API performance
- Error rates and retry frequency
- Daily productivity metrics

### 2. Setup Alerts
We can configure alerts for:
- High error rate in captures
- Excessive carryover tasks
- GitHub API latency spikes

### 3. Test More Features
Try these to see the telemetry in action:

```bash
# AI-delegatable task with priority
/gpwk.capture "Research Grafana Alloy deployment patterns [AI] !high ~deep"

# Personal task with energy marker
/gpwk.capture "Update team on GPWK progress [P] ~shallow"

# Completed activity with time range
/gpwk.capture "I wrote documentation from 9-11 AM. This is complete."
```

Each one creates a trace you can explore in Grafana!

---

## Troubleshooting

### Container won't start
```bash
# Check logs
docker compose logs grafana-alloy

# Common fix: restart
docker compose down && docker compose up -d
```

### No telemetry in Grafana
1. Check Alloy UI: http://localhost:12345 (all should be green)
2. Check Grafana Cloud credentials in `.env`
3. View Alloy logs: `docker compose logs grafana-alloy | grep error`

### Update configuration
```bash
# Edit gpwk.alloy
nano gpwk.alloy

# Restart to apply changes
docker compose restart
```

---

**Ready to use!** Your productivity system is now observable. Every capture, every retry, every error is tracked and visualized. 🚀
