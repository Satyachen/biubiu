---
name: 1panel-management
description: Manage 1Panel server management panel via REST API. Query dashboards, system info, network stats, containers, cron jobs and more. Trigger on mentioning 1Panel or panel.
---

# 1Panel Management Skill

Control your [1Panel](https://1panel.cn) Linux server management panel programmatically.

## Prerequisites

- 1Panel v2.x installed and running
- API interface enabled in 1Panel settings → Panel Settings → API
- API key configured (or use built-in API key from database)
- Root/sudo access to the 1Panel server for DB operations (optional)

## Environment Variables

Set these in your `~/.hermes/.env` or `~/.hermes/config.yaml`:

```bash
# 1Panel connection
PANEL_URL=http://127.0.0.1:18090          # 1Panel web URL
PANEL_API_KEY=your-api-key                 # API key (from 1Panel settings)
PANEL_USER=admin                           # Web UI username
PANEL_PASS=password                        # Web UI password
PANEL_DB_PATH=/opt/1panel/db/core.db       # SQLite DB path (for captcha bypass)
```

## Authentication

### Method A: API Key Token (Recommended for automation)

1Panel uses a simple token-based auth for API access:

```
Token = MD5("1panel" + API-Key + UnixTimestamp)
```

Send as HTTP headers:
```
1Panel-Token: <token>
1Panel-Timestamp: <unix_timestamp>
```

### Method B: Session Cookie (Web UI automation)

Requires RSA PKCS1v1.5 encrypted password (JSEncrypt compatible).

## API Endpoints

### Dashboard
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/dashboard/base/all/all` | GET | Overview (websites, databases, cron jobs, app count) |
| `/api/v2/dashboard/base/os` | GET | System info (OS, kernel, platform) |
| `/api/v2/dashboard/current/all/all` | GET | Real-time monitoring data |
| `/api/v2/dashboard/app/launcher` | GET | App launcher config |

### Host Monitoring
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/hosts/monitor/netoptions` | GET | Network interface list |
| `/api/v2/hosts/monitor/iooptions` | GET | Disk IO options |

### System Settings
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/core/settings/search` | GET | Search system settings |
| `/api/v2/settings/get/SystemIP` | GET | Get system IP |
| `/api/v2/core/nodes/list` | GET | Node list |
| `/api/v2/core/nodes/simple/all` | GET | Simplified node list |

### Logs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/logs/tasks/executing/count` | GET | Currently executing tasks |

### Files
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/files/download` | GET | File download |

## Database Bypass (Root Required)

When captcha blocks automated access, manipulate the SQLite database directly:

```bash
# Database location (default)
/opt/1panel/db/core.db

# Clear login logs (resets captcha counter)
sqlite3 $PANEL_DB_PATH 'DELETE FROM login_logs'

# Check/modify settings
sqlite3 $PANEL_DB_PATH \
  "SELECT key, value FROM settings WHERE key IN ('ApiInterfaceStatus','ApiKey','AllowIPs','NoAuthSetting')"

# Restart services after DB changes
systemctl restart 1panel-core 1panel-agent
```

## Helper Script

A companion Python script (`panel_api.py`) is available in this skill's `scripts/` directory. It handles API key token generation and request signing:

```bash
# Get dashboard overview
python3 panel_api.py /api/v2/dashboard/base/all/all

# Get system info
python3 panel_api.py /api/v2/dashboard/base/os

# List network interfaces
python3 panel_api.py /api/v2/hosts/monitor/netoptions

# Use session auth instead of API key (for troubleshooting)
python3 panel_api.py --no-apikey /api/v2/dashboard/base/all/all
```

## Discovering More Endpoints

1Panel is an SPA. To discover container/cron/other endpoints:

1. Open 1Panel in browser DevTools
2. Navigate to the feature page
3. Watch Network tab for XHR/fetch calls to `/api/v2/...`

Or search the JS bundle:
```bash
curl -s http://$PANEL_URL/assets/js/index-*.js | grep -oP '"/api/v2/[^"]+"' | sort -u
```
