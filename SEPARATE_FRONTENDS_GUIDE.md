# 🎨 Separate Frontends Architecture Guide

## 📁 Project Structure

```
MARKET_RISK_VaR_SYSTEM/
│
├── market-risk-var/
│   ├── src/                           # Backend (Python/FastAPI)
│   ├── dashboard/                     # Streamlit (can be replaced)
│   └── frontend/                      ✅ NEW React Frontend
│       ├── src/app/page.tsx           # VaR Dashboard
│       ├── package.json               # Port 3000
│       └── README.md
│
├── defi-analytics-platform/
│   ├── src/                           # Backend (Python/FastAPI)
│   ├── dashboard/                     # Streamlit (can be replaced)
│   └── frontend/                      ✅ NEW React Frontend
│       ├── src/app/page.tsx           # DeFi Dashboard
│       ├── package.json               # Port 3001
│       └── README.md
│
├── unified-risk-platform/
│   ├── backend/                       # Backend (Python/FastAPI)
│   └── frontend/                      ✅ Combined Dashboard
│       ├── package.json               # Port 3002
│       └── README.md
│
└── frontend/                          ✅ Main Landing Page
    ├── src/app/page.tsx               # Landing/Marketing
    ├── package.json                   # Port 3003
    └── README.md
```

---

## 🎯 Why Separate Frontends?

### **Benefits:**
1. **Independent Deployment** - Deploy each project separately
2. **Self-Contained** - Each frontend works with its own backend
3. **Easy to Share** - Share VaR system without DeFi code
4. **Modular Development** - Teams can work independently
5. **Flexible Tech Stack** - Can use different frameworks per project
6. **Better Organization** - Clear separation of concerns

### **Architecture:**
```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  VaR Frontend   │      │ DeFi Frontend   │      │ Unified Frontend│
│   Port 3000     │      │   Port 3001     │      │   Port 3002     │
└────────┬────────┘      └────────┬────────┘      └────────┬────────┘
         │                        │                        │
         ↓                        ↓                        ↓
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  VaR Backend    │      │ DeFi Backend    │      │ Unified Backend │
│   Port 8000     │      │   Port 8001     │      │   Port 8002     │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

---

## 🚀 Quick Start - Run All Frontends

### **Terminal 1: VaR Frontend**
```bash
cd market-risk-var/frontend
npm install
npm run dev
# Runs on http://localhost:3000
```

### **Terminal 2: DeFi Frontend**
```bash
cd defi-analytics-platform/frontend
npm install
npm run dev
# Runs on http://localhost:3001
```

### **Terminal 3: Unified Frontend**
```bash
cd unified-risk-platform/frontend
npm install
npm run dev
# Runs on http://localhost:3002
```

### **Terminal 4: Main Landing**
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:3003
```

---

## 📊 Frontend Details

### 1️⃣ **Market Risk VaR Frontend** (Port 3000)

**Focus:** VaR calculations and risk metrics

**Features:**
- ✅ Portfolio value tracking
- ✅ 6 VaR methods comparison
- ✅ Portfolio breakdown (pie chart)
- ✅ VaR history (30-day line chart)
- ✅ Backtesting results (Kupiec, Christoffersen, Traffic Light)
- ✅ Risk metrics (Sharpe, Sortino, Max Drawdown)

**Dashboard Sections:**
1. Key Metrics Cards (Portfolio Value, VaR 95%, Sharpe Ratio, Max Drawdown)
2. VaR Methods Bar Chart
3. Portfolio Breakdown Pie Chart
4. VaR History Line Chart
5. Backtesting Results

**API Endpoint:** `http://localhost:8000`

**Navigate to:**
```bash
cd market-risk-var/frontend
npm run dev
open http://localhost:3000
```

---

### 2️⃣ **DeFi Analytics Frontend** (Port 3001)

**Focus:** Protocol analysis and yield optimization

**Features:**
- ✅ TVL tracking across protocols
- ✅ Top yield opportunities table
- ✅ APY trends (30-day multi-line chart)
- ✅ Smart contract risk analysis (radar chart)
- ✅ Impermanent loss calculator
- ✅ Wallet connection (Web3)

**Dashboard Sections:**
1. Key Metrics Cards (TVL, Total Yield, Avg APY, Risk Score)
2. Top Yield Opportunities Table
3. APY Trends Multi-Line Chart
4. Smart Contract Risk Radar Chart
5. Impermanent Loss Calculator

**API Endpoint:** `http://localhost:8001`

**Navigate to:**
```bash
cd defi-analytics-platform/frontend
npm run dev
open http://localhost:3001
```

---

### 3️⃣ **Unified Risk Frontend** (Port 3002)

**Focus:** Combined TradFi + DeFi analytics

**Features:**
- ✅ Unified portfolio view
- ✅ Cross-asset correlation
- ✅ ML model predictions
- ✅ Sentiment analysis
- ✅ ESG scoring
- ✅ Combined risk metrics

**API Endpoint:** `http://localhost:8002`

**Navigate to:**
```bash
cd unified-risk-platform/frontend
npm run dev
open http://localhost:3002
```

---

### 4️⃣ **Main Landing Page** (Port 3003)

**Focus:** Marketing and navigation

**Features:**
- ✅ Hero section with CTAs
- ✅ Features showcase
- ✅ Links to all 3 dashboards
- ✅ Documentation
- ✅ Contact forms

**Navigate to:**
```bash
cd frontend
npm run dev
open http://localhost:3003
```

---

## 🔧 Configuration

### **Environment Variables**

Each frontend needs its own `.env.local`:

**market-risk-var/frontend/.env.local:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Market Risk VaR
```

**defi-analytics-platform/frontend/.env.local:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY
NEXT_PUBLIC_APP_NAME=DeFi Analytics
```

**unified-risk-platform/frontend/.env.local:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8002
NEXT_PUBLIC_VAR_API=http://localhost:8000
NEXT_PUBLIC_DEFI_API=http://localhost:8001
NEXT_PUBLIC_APP_NAME=Unified Risk Platform
```

---

## 📦 Installation

### **Install All Frontends**

```bash
# VaR Frontend
cd market-risk-var/frontend
npm install

# DeFi Frontend
cd ../../defi-analytics-platform/frontend
npm install

# Unified Frontend
cd ../../unified-risk-platform/frontend
npm install

# Landing Page
cd ../../frontend
npm install
```

### **Or use this one-liner:**
```bash
(cd market-risk-var/frontend && npm install) && \
(cd defi-analytics-platform/frontend && npm install) && \
(cd unified-risk-platform/frontend && npm install) && \
(cd frontend && npm install)
```

---

## 🎨 Tech Stack (All Frontends)

**Core:**
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS

**Charts:**
- Recharts (line, bar, pie, radar charts)

**State & Data:**
- SWR (real-time data fetching)
- Axios (HTTP client)

**UI:**
- Lucide Icons
- Framer Motion (animations)
- Dark/Light mode

**DeFi Specific:**
- ethers.js (Web3 integration)

---

## 🚀 Development Workflow

### **Run Individual Frontend**
```bash
# Choose one:
cd market-risk-var/frontend && npm run dev
cd defi-analytics-platform/frontend && npm run dev
cd unified-risk-platform/frontend && npm run dev
cd frontend && npm run dev
```

### **Run All Frontends (4 terminals)**

**Terminal 1:**
```bash
cd market-risk-var/frontend && npm run dev
```

**Terminal 2:**
```bash
cd defi-analytics-platform/frontend && npm run dev
```

**Terminal 3:**
```bash
cd unified-risk-platform/frontend && npm run dev
```

**Terminal 4:**
```bash
cd frontend && npm run dev
```

### **Run All Backends (3 terminals)**

**Terminal 5:**
```bash
cd market-risk-var
uvicorn src.api.main:app --port 8000 --reload
```

**Terminal 6:**
```bash
cd defi-analytics-platform
uvicorn src.api.main:app --port 8001 --reload
```

**Terminal 7:**
```bash
cd unified-risk-platform/backend
uvicorn api.unified_api:app --port 8002 --reload
```

---

## 🌐 URLs Overview

| Project | Frontend URL | Backend URL | Description |
|---------|-------------|-------------|-------------|
| **VaR System** | http://localhost:3000 | http://localhost:8000 | Market Risk VaR Dashboard |
| **DeFi Analytics** | http://localhost:3001 | http://localhost:8001 | DeFi Protocol Analysis |
| **Unified Platform** | http://localhost:3002 | http://localhost:8002 | Combined TradFi + DeFi |
| **Landing Page** | http://localhost:3003 | N/A | Main marketing site |

---

## 📱 Mobile Responsive

All frontends are **fully mobile responsive**:
- ✅ Works on iPhone (375px+)
- ✅ Works on iPad (768px+)
- ✅ Works on Desktop (1024px+)
- ✅ Touch-optimized
- ✅ Responsive charts
- ✅ Adaptive layouts

---

## 🎯 Which Frontend Should I Use?

### **Use VaR Frontend when:**
- You only need VaR calculations
- Working on market risk analysis
- Backtesting trading strategies
- Calculating Sharpe/Sortino ratios

### **Use DeFi Frontend when:**
- You only need DeFi analytics
- Analyzing protocols (Aave, Compound, Uniswap)
- Yield farming optimization
- Calculating impermanent loss
- Smart contract risk assessment

### **Use Unified Frontend when:**
- You need both TradFi + DeFi
- Cross-asset correlation analysis
- ML model predictions
- ESG scoring
- Comprehensive risk management

### **Use Landing Page when:**
- Marketing your platform
- Showcasing all features
- User documentation
- Contact/support forms

---

## 📚 Documentation

Each frontend has its own README:

```
market-risk-var/frontend/README.md            # VaR Dashboard
defi-analytics-platform/frontend/README.md    # DeFi Dashboard
unified-risk-platform/frontend/README.md      # Unified Dashboard
frontend/README.md                             # Landing Page
```

---

## 🔄 Migration from Streamlit

If you want to completely replace Streamlit:

### **Before:**
```bash
streamlit run market-risk-var/dashboard/var_dashboard.py
streamlit run defi-analytics-platform/dashboard/defi_dashboard.py
```

### **After:**
```bash
cd market-risk-var/frontend && npm run dev
cd defi-analytics-platform/frontend && npm run dev
```

**Benefits of React over Streamlit:**
- ✅ Better performance
- ✅ More customization
- ✅ Production-ready
- ✅ Better mobile support
- ✅ Modern UI/UX
- ✅ Easier deployment

---

## 🚢 Deployment

### **Deploy Each Frontend Separately**

**VaR Frontend to Vercel:**
```bash
cd market-risk-var/frontend
vercel
```

**DeFi Frontend to Vercel:**
```bash
cd defi-analytics-platform/frontend
vercel
```

**Unified Frontend to Vercel:**
```bash
cd unified-risk-platform/frontend
vercel
```

### **Or Deploy All Together:**
Use a monorepo setup with Turborepo or Nx.

---

## ✅ Summary

✅ **3 Separate React Frontends Created**
- Market Risk VaR (Port 3000)
- DeFi Analytics (Port 3001)
- Unified Risk (Port 3002)

✅ **Each Frontend:**
- Self-contained
- Mobile responsive
- Dark/Light mode
- Production ready
- Connects to its own backend

✅ **Benefits:**
- Independent deployment
- Clear separation
- Easy to maintain
- Flexible architecture

---

## 🎉 You're All Set!

Run any or all frontends based on your needs. Each one is a complete, professional dashboard ready for production use!

**Questions?** Check individual README files in each frontend folder.

---

**Built with ❤️ using Next.js 14, React 18, and TypeScript**
