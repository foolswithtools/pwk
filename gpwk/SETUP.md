# GPWK Python + OpenTelemetry Setup Guide

This guide will help you set up the Python-based GPWK implementation with OpenTelemetry instrumentation and Grafana Cloud integration.

## Prerequisites

- Python 3.8 or later
- Grafana Cloud account (free tier available at https://grafana.com)
- Grafana Alloy installed on your machine
- GitHub CLI (`gh`) authenticated

## ⚠️ Security Warning

This setup process will create local configuration files containing GitHub project IDs and may involve Grafana Cloud credentials. **Important security practices:**

- **NEVER commit `gpwk/config/alloy/.env`** - This file contains real API keys and credentials
- The `.env` file is protected by `.gitignore` - verify it's ignored before committing
- **Always use `.env.example` as a template** when creating your `.env` file
- GitHub project IDs in `gpwk/memory/github-config.md` are safe to commit (they don't contain credentials)
- Use `gh auth login` for GitHub authentication (no tokens needed in files)
- Keep all API keys and tokens in environment variables, never hardcoded

## Step 1: Install Python Dependencies

```bash
cd gpwk/lib/python
pip install -r requirements.txt
```

Or use a virtual environment (recommended):

```bash
cd gpwk/lib/python
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Configure Grafana Cloud

### Get Your Grafana Cloud Credentials

1. Log in to your Grafana Cloud account at https://grafana.com
2. Navigate to **My Account** → **Cloud Portal**
3. Click on your stack (or create a new one)
4. Navigate to **Access Policies** → **Create Access Policy**
5. Create a policy with the following scopes:
   - `metrics:write`
   - `logs:write`
   - `traces:write`
6. Generate a token and save it securely

### Get Your OTLP Endpoint

1. In Grafana Cloud, go to **Connections** → **Add new connection**
2. Search for "OpenTelemetry"
3. Click **"OpenTelemetry (OTLP)"**
4. Copy the following information:
   - **OTLP Endpoint** (e.g., `otlp-gateway-prod-us-east-0.grafana.net:443`)
   - **Instance ID** (your Grafana Cloud user ID)

### Get Your Prometheus Endpoint

1. In Grafana Cloud, go to **Prometheus**
2. Click on **"Details"** for your Prometheus instance
3. Copy the **Remote Write Endpoint** URL

## Step 3: Set Environment Variables

Create a file `~/.gpwk-env` with your Grafana Cloud credentials:

```bash
# Grafana Cloud OTLP configuration
export GRAFANA_CLOUD_OTLP_ENDPOINT="https://otlp-gateway-prod-us-east-0.grafana.net/otlp"
export GRAFANA_CLOUD_INSTANCE_ID="<your-instance-id>"
export GRAFANA_CLOUD_API_KEY="<your-api-key>"

# Grafana Cloud Prometheus configuration
export GRAFANA_CLOUD_PROMETHEUS_URL="https://prometheus-prod-01-us-east-0.grafana.net/api/prom/push"

# Local OTLP endpoint (for Python library to send to Alloy)
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
```

Load these variables in your shell:

```bash
# Add to your ~/.bashrc or ~/.zshrc
source ~/.gpwk-env
```

## Step 4: Install and Configure Grafana Alloy

### Install Grafana Alloy

**macOS (Homebrew)**:
```bash
brew install grafana/grafana/alloy
```

**Linux (Debian/Ubuntu)**:
```bash
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt update
sudo apt install alloy
```

**Other platforms**: See https://grafana.com/docs/alloy/latest/get-started/install/

### Start Grafana Alloy

```bash
# Load environment variables first
source ~/.gpwk-env

# Start Alloy with the GPWK configuration
alloy run gpwk/config/alloy/gpwk.alloy
```

You should see output like:
```
ts=2025-12-20T10:00:00Z level=info msg="starting Alloy" version=...
ts=2025-12-20T10:00:01Z level=info component=otelcol.receiver.otlp.gpwk msg="Starting GRPC server" endpoint=127.0.0.1:4317
```

### Verify Alloy is Running

1. Open http://localhost:12345 in your browser
2. You should see the Alloy Web UI
3. Check that components are healthy:
   - `otelcol.receiver.otlp.gpwk` should show "healthy"
   - `otelcol.processor.batch.default` should show "healthy"
   - `otelcol.exporter.otlp.grafana_cloud` should show "healthy"

## Step 5: Test the Setup

### Test 1: Simple Capture

```bash
# Run the Python CLI directly
gpwk/bin/gpwk-capture "Test capture to verify telemetry"
```

Expected output:
```
✓ Captured: Test capture to verify telemetry
  Issue: #XX (https://github.com/...)
  Duration: XXXms

  Run /gpwk.triage to move to Today/This Week
```

### Test 2: Capture with Special Characters

This tests that we've fixed the shell escaping issue:

```bash
gpwk/bin/gpwk-capture "Test with (parentheses) and 'quotes' and \"double quotes\""
```

Should succeed without parse errors!

### Test 3: Completed Activity

This tests completion detection:

```bash
gpwk/bin/gpwk-capture "I took Mr. Noodles for a walk between 9:00 AM - 10:00 AM. This is complete."
```

The issue should be created, added to project, AND closed automatically.

## Step 6: Verify Telemetry in Grafana Cloud

### Check Traces

1. Log in to Grafana Cloud
2. Navigate to **Explore**
3. Select **Tempo** as the data source
4. Search for traces with service name: `gpwk`
5. You should see traces like:
   ```
   gpwk_capture (543ms)
     ├─ parse (12ms)
     ├─ create_issue (234ms)
     ├─ add_to_project (89ms)
     ├─ set_fields (156ms)
     └─ update_log (52ms)
   ```

### Check Metrics

1. In **Explore**, select **Prometheus** as the data source
2. Query for GPWK metrics:
   ```promql
   {__name__=~"gpwk.*"}
   ```
3. You should see metrics like:
   - `gpwk_capture_total`
   - `gpwk_capture_duration_bucket`
   - `gpwk_github_api_calls_total`
   - `gpwk_github_api_latency_bucket`

### Check Logs

1. In **Explore**, select **Loki** as the data source
2. Query for GPWK logs:
   ```logql
   {service_name="gpwk"}
   ```
3. You should see structured logs with trace IDs

## Step 7: Update Claude Code Command

Now update the `/gpwk.capture` command to use the Python backend:

The command file is at: `.claude/commands/gpwk.capture.md`

Replace the implementation with a simple call to the Python CLI:

```bash
gpwk/bin/gpwk-capture "$ARGUMENTS"
```

## Troubleshooting

### Issue: "No module named 'gpwk_core'"

**Solution**: Make sure you've installed the dependencies and the path is correct:
```bash
cd gpwk/lib/python
pip install -r requirements.txt
```

### Issue: Alloy shows "unhealthy" for OTLP exporter

**Solution**: Check your Grafana Cloud credentials:
```bash
# Verify environment variables are set
echo $GRAFANA_CLOUD_OTLP_ENDPOINT
echo $GRAFANA_CLOUD_INSTANCE_ID
echo $GRAFANA_CLOUD_API_KEY

# Restart Alloy
alloy run gpwk/config/alloy/gpwk.alloy
```

### Issue: No traces appearing in Grafana Cloud

**Solution**:
1. Check Alloy logs for errors
2. Verify the Python script is actually running (check for logs)
3. Try running with debug logging:
   ```bash
   OTEL_LOG_LEVEL=debug gpwk/bin/gpwk-capture "test"
   ```

### Issue: GitHub API rate limit errors

**Solution**: The retry logic will handle transient errors, but if you hit rate limits:
1. Check current rate limit: `gh api rate_limit`
2. Wait for reset or use a GitHub token with higher limits

## Running Alloy as a Service

### macOS (launchd)

Create `~/Library/LaunchAgents/com.grafana.alloy.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.grafana.alloy</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/alloy</string>
        <string>run</string>
        <string>/Users/YOUR_USERNAME/path/to/gpwk/config/alloy/gpwk.alloy</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>GRAFANA_CLOUD_OTLP_ENDPOINT</key>
        <string>YOUR_ENDPOINT</string>
        <key>GRAFANA_CLOUD_INSTANCE_ID</key>
        <string>YOUR_INSTANCE_ID</string>
        <key>GRAFANA_CLOUD_API_KEY</key>
        <string>YOUR_API_KEY</string>
        <key>GRAFANA_CLOUD_PROMETHEUS_URL</key>
        <string>YOUR_PROMETHEUS_URL</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/alloy.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/alloy.err</string>
</dict>
</plist>
```

Load the service:
```bash
launchctl load ~/Library/LaunchAgents/com.grafana.alloy.plist
```

### Linux (systemd)

Create `/etc/systemd/system/alloy.service`:

```ini
[Unit]
Description=Grafana Alloy
After=network-online.target

[Service]
Type=simple
User=YOUR_USERNAME
Environment="GRAFANA_CLOUD_OTLP_ENDPOINT=YOUR_ENDPOINT"
Environment="GRAFANA_CLOUD_INSTANCE_ID=YOUR_INSTANCE_ID"
Environment="GRAFANA_CLOUD_API_KEY=YOUR_API_KEY"
Environment="GRAFANA_CLOUD_PROMETHEUS_URL=YOUR_PROMETHEUS_URL"
ExecStart=/usr/bin/alloy run /path/to/gpwk/config/alloy/gpwk.alloy
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable alloy
sudo systemctl start alloy
sudo systemctl status alloy
```

## Next Steps

1. **Create Dashboards**: Build Grafana dashboards to visualize your productivity metrics
2. **Setup Alerts**: Configure alerts for high error rates or carryover issues
3. **Migrate Other Commands**: Apply this pattern to `/gpwk.plan`, `/gpwk.triage`, etc.
4. **Advanced Analytics**: Use the telemetry data for `/gpwk.optimize` insights

## Support

- **Grafana Alloy Docs**: https://grafana.com/docs/alloy/latest/
- **OpenTelemetry Python**: https://opentelemetry.io/docs/instrumentation/python/
- **Grafana Cloud**: https://grafana.com/docs/grafana-cloud/

Happy tracking! 🚀
