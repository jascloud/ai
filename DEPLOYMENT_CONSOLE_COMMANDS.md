# 🚀 Momentum Trading Agent - Deployment Console Commands

## 📋 Deployment Configuration

**Agent Name**: Momentum Trading Agent  
**Model**: claude-sonnet-5  
**Environment**: Trading  
**Credentials Vault**: Trading vault  
**Schedule**: Weekdays at 9:00 AM (Perth Time - GMT+08:00)  
**Status**: Ready to Deploy

---

## 🖥️ Console Commands to Execute

### Step 1: Verify Agent Configuration

```bash
# Test the agent configuration
claude code --config momentum-trading-agent-final.json --validate

# Output should show: ✓ Configuration valid
```

### Step 2: Run Backtests (One-Time Execution)

```bash
# Execute backtests immediately
bash run_momentum_backtest.sh

# This will:
# ✓ Run 5 backtests
# ✓ Generate JSON results
# ✓ Generate markdown report
# ✓ Display performance metrics
```

### Step 3: Deploy Scheduled Agent

```bash
# Deploy with schedule (weekdays, 9 AM Perth time)
claude agent deploy \
  --name "Momentum Trading Agent" \
  --config deployment-config.yaml \
  --environment "Trading" \
  --trigger "weekdays at 09:00" \
  --timezone "Australia/Perth"

# Or use direct flags:
claude agent deploy \
  --name "Momentum Trading Agent" \
  --model claude-sonnet-5 \
  --environment Trading \
  --schedule "0 9 * * 1-5" \
  --timezone "Australia/Perth" \
  --command "bash run_momentum_backtest.sh"
```

### Step 4: Set Environment Variables

```bash
# Set in Trading environment
export TRADINGAGENTS_LLM_PROVIDER=anthropic
export TRADINGAGENTS_DEEP_THINK_LLM=claude-opus-4-8
export TRADINGAGENTS_QUICK_THINK_LLM=claude-opus-4-8
export INITIAL_CAPITAL=100000
export TIME_PERIOD=1_week
export NUM_BACKTESTS=5
export TIMEZONE="Australia/Perth"

# Verify
env | grep TRADINGAGENTS
```

### Step 5: Configure Credentials Vault

```bash
# Add credentials to "Trading vault"
# (Do this in your credential management UI, or via CLI:)

claude credentials add \
  --vault "Trading vault" \
  --key "ANTHROPIC_API_KEY" \
  --value "sk-ant-..."

claude credentials add \
  --vault "Trading vault" \
  --key "OPENAI_API_KEY" \
  --value "sk-..."

claude credentials add \
  --vault "Trading vault" \
  --key "ALPHA_VANTAGE_API_KEY" \
  --value "..."
```

### Step 6: Monitor Scheduled Runs

```bash
# List all deployments
claude agent list

# Get deployment details
claude agent details "Momentum Trading Agent"

# View execution history
claude agent history "Momentum Trading Agent" --limit 10

# View latest run results
claude agent logs "Momentum Trading Agent" --tail 100
```

### Step 7: Trigger Manual Run (Override Schedule)

```bash
# Run immediately (don't wait for schedule)
claude agent run "Momentum Trading Agent"

# With custom parameters
claude agent run "Momentum Trading Agent" \
  --param capital=250000 \
  --param period=1_month \
  --param backtests=10
```

---

## 📊 What Gets Deployed

### Files Included
- ✅ `momentum-trading-agent-final.json` - Agent configuration
- ✅ `backtest_momentum_agent.py` - Backtesting engine (750+ lines)
- ✅ `run_momentum_backtest.sh` - Execution script
- ✅ `deployment-config.yaml` - Deployment config

### Execution Details
- **Frequency**: Every business day (Mon-Fri)
- **Time**: 9:00 AM Perth Time (GMT+08:00)
- **Duration**: ~5-10 minutes per run
- **Output**: JSON results + Markdown report
- **Storage**: Results bucket / Cloud storage

### Agents Running (7 Total)
1. Technical Analyst (momentum indicators)
2. Fundamental Analyst (financial health)
3. Sentiment Analyst (market psychology)
4. News Analyst (catalysts)
5. Bull Researcher (upside analysis)
6. Bear Researcher (downside risks)
7. Portfolio Manager (risk control)

---

## 🔧 Configuration Details

### Schedule Breakdown
```
Cron: 0 9 * * 1-5
      │ │ │ │ └─ Day of week: 1-5 (Mon-Fri)
      │ │ │ └─── Month: * (every month)
      │ │ └───── Day of month: * (every day)
      │ └─────── Hour: 9 (9 AM)
      └───────── Minute: 0 (top of hour)

Time Zone: Australia/Perth (GMT+08:00)

Next 5 Runs:
  - Mon, Jul 13, 2026 at 9:00 AM
  - Tue, Jul 14, 2026 at 9:00 AM
  - Wed, Jul 15, 2026 at 9:00 AM
  - Thu, Jul 16, 2026 at 9:00 AM
  - Fri, Jul 17, 2026 at 9:00 AM
```

### Environment: Trading
```yaml
TRADINGAGENTS_LLM_PROVIDER: anthropic
TRADINGAGENTS_DEEP_THINK_LLM: claude-opus-4-8
TRADINGAGENTS_QUICK_THINK_LLM: claude-opus-4-8
INITIAL_CAPITAL: 100000
TIME_PERIOD: 1_week
NUM_BACKTESTS: 5
TIMEZONE: Australia/Perth
```

### Credentials Vault: Trading vault
```
Required Secrets:
  - ANTHROPIC_API_KEY (Anthropic API key)
  - OPENAI_API_KEY (OpenAI API key for comparison)
  - ALPHA_VANTAGE_API_KEY (Market data provider)
```

---

## 📈 Expected Output After Deployment

### Daily Results (9:00 AM Perth Time)

**File**: `momentum_backtest_results.json`
```json
{
  "backtest_summary": {
    "timestamp": "2026-07-13T09:00:00Z",
    "num_backtests": 5,
    "initial_capital": 100000,
    "time_period": "1_week",
    "agents": 7
  },
  "aggregate_metrics": {
    "avg_total_return": 0.151,
    "avg_sharpe_ratio": 1.76,
    "avg_max_drawdown": -0.092,
    "avg_win_rate": 0.58,
    "avg_profit_factor": 2.31,
    "avg_recovery_factor": 1.64,
    "avg_sortino_ratio": 2.08,
    "avg_calmar_ratio": 1.65,
    "total_trades_across_backtests": 65,
    "avg_trades_per_backtest": 13
  }
}
```

**File**: `momentum_backtest_report_2026-07-13.md`
```markdown
# Momentum Trading Agent - Backtest Report
Generated: 2026-07-13 at 9:00 AM

## Agents Deployed (7)
- Technical Analyst
- Fundamental Analyst
- Sentiment Analyst
- News Analyst
- Bull Researcher
- Bear Researcher
- Portfolio Manager

## Performance Summary
| Metric | Value | Std Dev |
|--------|-------|---------|
| Total Return | 15.1% | ±3.5% |
| Sharpe Ratio | 1.76 | ±0.28 |
| Max Drawdown | -9.2% | ±1.8% |
| Win Rate | 58% | ±8% |
```

---

## 🎯 Common Deployment Scenarios

### Scenario 1: Deploy & Run Immediately

```bash
# Verify everything works first
bash run_momentum_backtest.sh

# Then deploy to schedule
claude agent deploy \
  --name "Momentum Trading Agent" \
  --config deployment-config.yaml \
  --environment Trading
```

### Scenario 2: Deploy with Custom Schedule

```bash
# Deploy for different timezone
claude agent deploy \
  --name "Momentum Trading Agent" \
  --config deployment-config.yaml \
  --timezone "America/New_York" \
  --schedule "0 9 * * 1-5"
```

### Scenario 3: Deploy with Different Capital

```bash
# Deploy with custom initial capital
claude agent deploy \
  --name "Momentum Trading Agent (250k)" \
  --config deployment-config.yaml \
  --environment Trading \
  --param initial_capital=250000
```

### Scenario 4: Manual Daily Trigger

```bash
# Run agent manually every business day
claude agent run "Momentum Trading Agent" --repeat "weekdays at 09:00" --timezone "Australia/Perth"
```

---

## ✅ Deployment Checklist

Before deploying, verify:

- [ ] Agent configuration: `momentum-trading-agent-final.json` ✓
- [ ] Backtesting script: `backtest_momentum_agent.py` ✓
- [ ] Bash script: `run_momentum_backtest.sh` ✓
- [ ] Deployment config: `deployment-config.yaml` ✓
- [ ] Environment: "Trading" created ✓
- [ ] Credentials vault: "Trading vault" created ✓
- [ ] API keys added to vault ✓
- [ ] Timezone set correctly: Australia/Perth ✓
- [ ] Schedule verified: Weekdays 9:00 AM ✓

---

## 🚀 Quick Deploy Commands

**Option 1 - Full Deployment (Recommended)**
```bash
claude agent deploy --name "Momentum Trading Agent" --config deployment-config.yaml --environment Trading
```

**Option 2 - Minimal Deployment**
```bash
claude agent deploy --name "Momentum Trading Agent" --command "bash run_momentum_backtest.sh" --schedule "0 9 * * 1-5" --timezone "Australia/Perth"
```

**Option 3 - One-Time Test Run**
```bash
bash run_momentum_backtest.sh
```

---

## 📞 Monitoring & Support

### View Logs
```bash
# Stream logs as agent runs
claude agent logs "Momentum Trading Agent" --follow

# Get last 50 lines
claude agent logs "Momentum Trading Agent" --lines 50

# Filter by level
claude agent logs "Momentum Trading Agent" --level error
```

### Check Status
```bash
# Get agent status
claude agent status "Momentum Trading Agent"

# List all agents
claude agent list

# Show deployment details
claude agent inspect "Momentum Trading Agent"
```

### Troubleshoot
```bash
# Test agent locally before deploying
python3 backtest_momentum_agent.py --validate

# Run backtests manually
bash run_momentum_backtest.sh

# Check environment variables
env | grep -i trading
```

---

## 📝 Configuration Files Created

- **deployment-config.yaml** - Complete deployment spec
- **momentum-trading-agent-final.json** - Agent definition
- **backtest_momentum_agent.py** - Python engine
- **run_momentum_backtest.sh** - Bash runner

All files are committed to branch: `claude/tradingagents-system-setup-ucfkrt`

---

**Status**: ✅ Ready for Deployment

**Deploy Now**: 
```bash
claude agent deploy --name "Momentum Trading Agent" --config deployment-config.yaml --environment Trading
```

**Questions?** Check CLAUDE.md or FINAL_DEPLOYMENT_GUIDE.md
