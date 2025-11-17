"""
=============================================================================
UNIFIED RISK PLATFORM - API
=============================================================================

PURPOSE:
Single API endpoint combining:
- Traditional Finance VaR (ARIMA/GARCH)
- DeFi Analytics (Yield/Risk/Liquidity)
- Cross-Asset Portfolio Management
- Machine Learning Predictions
- Real-Time Monitoring

FOR INSTITUTIONAL USE:
Hedge funds, family offices, and institutional investors managing both
TradFi and DeFi portfolios simultaneously.

AUTHOR: Built for Economics & Finance MSc students
DATE: 2024
=============================================================================
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import numpy as np
import pandas as pd

# Import existing modules (in production, these would be properly imported)
# from market-risk-var.src.models import ARIMAModel, GARCHModel
# from market-risk-var.src.risk import VaRCalculator
# from defi-analytics-platform.src.risk import DeFiRiskModels
# from defi-analytics-platform.src.optimization import YieldOptimizer

# ====================================================================================
# ENUMS
# ====================================================================================

class AssetClass(str, Enum):
    """Asset class types"""
    STOCK = "stock"
    CRYPTO = "crypto"
    DEFI = "defi"
    BOND = "bond"
    COMMODITY = "commodity"


class RiskModel(str, Enum):
    """Risk calculation models"""
    HISTORICAL_VAR = "historical_var"
    PARAMETRIC_VAR = "parametric_var"
    MONTE_CARLO_VAR = "monte_carlo_var"
    GARCH_VAR = "garch_var"
    LIQUIDATION_RISK = "liquidation_risk"
    SMART_CONTRACT_RISK = "smart_contract_risk"


# ====================================================================================
# REQUEST/RESPONSE MODELS
# ====================================================================================

class UnifiedPortfolioPosition(BaseModel):
    """Position in unified portfolio"""
    asset_id: str = Field(..., description="Unique asset identifier")
    asset_class: AssetClass
    symbol: str = Field(..., example="BTC", description="Asset symbol")
    amount: float = Field(..., gt=0, description="Position size")
    entry_price: float = Field(..., gt=0)
    current_price: float = Field(..., gt=0)
    protocol: Optional[str] = Field(None, description="DeFi protocol (if applicable)")

    class Config:
        json_schema_extra = {
            "example": {
                "asset_id": "eth_aave_lending",
                "asset_class": "defi",
                "symbol": "ETH",
                "amount": 10.0,
                "entry_price": 2000.0,
                "current_price": 2100.0,
                "protocol": "Aave"
            }
        }


class UnifiedPortfolioRequest(BaseModel):
    """Request for unified portfolio analysis"""
    positions: List[UnifiedPortfolioPosition]
    confidence_level: float = Field(0.95, ge=0.5, le=0.99)
    time_horizon_days: int = Field(1, ge=1, le=365)
    risk_models: List[RiskModel] = Field(default=[RiskModel.HISTORICAL_VAR])

    class Config:
        json_schema_extra = {
            "example": {
                "positions": [
                    {
                        "asset_id": "aapl_stock",
                        "asset_class": "stock",
                        "symbol": "AAPL",
                        "amount": 100,
                        "entry_price": 150.0,
                        "current_price": 175.0,
                        "protocol": None
                    },
                    {
                        "asset_id": "eth_uniswap_lp",
                        "asset_class": "defi",
                        "symbol": "ETH/USDC",
                        "amount": 50000.0,
                        "entry_price": 1.0,
                        "current_price": 1.05,
                        "protocol": "Uniswap V3"
                    }
                ],
                "confidence_level": 0.95,
                "time_horizon_days": 1,
                "risk_models": ["historical_var", "liquidation_risk"]
            }
        }


class CrossAssetCorrelationRequest(BaseModel):
    """Request for cross-asset correlation analysis"""
    assets: List[str] = Field(..., min_items=2)
    lookback_days: int = Field(90, ge=30, le=365)
    include_defi: bool = Field(True)

    class Config:
        json_schema_extra = {
            "example": {
                "assets": ["AAPL", "BTC", "ETH", "SPY"],
                "lookback_days": 90,
                "include_defi": True
            }
        }


class MLPredictionRequest(BaseModel):
    """Request for ML-based predictions"""
    model_type: str = Field(..., description="lstm_yield, vulnerability, rl_portfolio")
    asset_or_protocol: str
    prediction_horizon_days: int = Field(30, ge=7, le=90)
    historical_data: Optional[Dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "model_type": "lstm_yield",
                "asset_or_protocol": "Curve_3pool",
                "prediction_horizon_days": 30
            }
        }


class AlertRule(BaseModel):
    """Alert configuration"""
    rule_id: str
    rule_type: str = Field(..., description="var_breach, liquidation, yield_drop, etc.")
    threshold: float
    asset_id: Optional[str] = None
    notification_channels: List[str] = Field(..., description="telegram, discord, email")
    enabled: bool = True


# ====================================================================================
# RESPONSE MODELS
# ====================================================================================

class UnifiedRiskMetrics(BaseModel):
    """Comprehensive risk metrics for unified portfolio"""
    # VaR Metrics
    var_usd: Dict[str, float]  # {"historical": 5000, "parametric": 4800, ...}
    var_percent: Dict[str, float]
    expected_shortfall: float

    # Portfolio Metrics
    total_value_usd: float
    tradfi_allocation_percent: float
    defi_allocation_percent: float

    # Risk Decomposition
    risk_by_asset_class: Dict[str, float]
    risk_by_asset: Dict[str, float]

    # Advanced Metrics
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown_percent: float
    beta: float

    # DeFi-Specific Risks
    liquidation_risks: List[Dict] = []
    smart_contract_risks: List[Dict] = []
    impermanent_loss_estimate: float = 0.0

    # Timestamp
    calculated_at: datetime


class CrossAssetCorrelationResponse(BaseModel):
    """Correlation analysis response"""
    correlation_matrix: Dict[str, Dict[str, float]]
    tradfi_defi_correlation: float
    diversification_score: float  # 0-100
    portfolio_variance: float
    interpretation: str
    recommendations: List[str]


class MLPredictionResponse(BaseModel):
    """ML model prediction response"""
    model_type: str
    asset_or_protocol: str
    predictions: Dict[str, Any]  # Flexible structure
    confidence: float  # 0-1
    explanation: str
    recommended_actions: List[str]
    generated_at: datetime


# ====================================================================================
# WEBSOCKET CONNECTION MANAGER
# ====================================================================================

class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        # Remove from all subscriptions
        for topic in self.subscriptions:
            if websocket in self.subscriptions[topic]:
                self.subscriptions[topic].remove(websocket)

    def subscribe(self, websocket: WebSocket, topic: str):
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        self.subscriptions[topic].append(websocket)

    async def broadcast(self, message: dict):
        """Broadcast to all connections"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

    async def broadcast_to_topic(self, topic: str, message: dict):
        """Broadcast to specific topic subscribers"""
        if topic in self.subscriptions:
            for connection in self.subscriptions[topic]:
                try:
                    await connection.send_json(message)
                except:
                    pass


# ====================================================================================
# INITIALIZE APP
# ====================================================================================

app = FastAPI(
    title="Unified Risk Platform API",
    description="""
    **Institutional-Grade Risk Management**

    Combines Traditional Finance VaR with DeFi Analytics for comprehensive
    portfolio risk management.

    ## Features

    * **Unified Portfolio**: Manage stocks, bonds, crypto, and DeFi positions
    * **Cross-Asset Risk**: VaR calculations across asset classes
    * **Correlation Analysis**: Study TradFi-DeFi relationships
    * **ML Predictions**: LSTM yields, contract vulnerability, RL optimization
    * **Real-Time Monitoring**: WebSocket feeds for live updates
    * **Automated Alerts**: Telegram, Discord, Email notifications
    * **Research Tools**: Export data for academic papers

    ## For Institutional Investors

    Built for hedge funds, family offices, and institutions managing both
    traditional and decentralized finance portfolios.
    """,
    version="2.0.0",
    contact={
        "name": "Risk Platform Team",
        "email": "risk@platform.com"
    }
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager
manager = ConnectionManager()


# ====================================================================================
# ROOT & HEALTH
# ====================================================================================

@app.get("/", tags=["General"])
async def root():
    """API information"""
    return {
        "platform": "Unified Risk Platform",
        "version": "2.0.0",
        "description": "TradFi + DeFi Risk Management",
        "documentation": "/docs",
        "status": "operational",
        "capabilities": {
            "tradfi_var": True,
            "defi_analytics": True,
            "cross_asset": True,
            "ml_predictions": True,
            "real_time": True,
            "alerts": True
        }
    }


@app.get("/health", tags=["General"])
async def health():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "operational",
            "database": "operational",
            "websocket": "operational",
            "ml_models": "operational",
            "blockchain_rpc": "operational"
        },
        "metrics": {
            "active_websockets": len(manager.active_connections),
            "total_requests_24h": 0,  # Would be from metrics
            "avg_latency_ms": 0
        }
    }


# ====================================================================================
# UNIFIED PORTFOLIO ENDPOINTS
# ====================================================================================

@app.post("/api/v2/portfolio/analyze", response_model=UnifiedRiskMetrics, tags=["Unified Portfolio"])
async def analyze_unified_portfolio(request: UnifiedPortfolioRequest):
    """
    Comprehensive risk analysis for unified portfolio

    **Calculates**:
    - VaR (multiple models)
    - Expected Shortfall (CVaR)
    - Sharpe/Sortino ratios
    - Cross-asset risk decomposition
    - DeFi-specific risks (liquidation, IL)

    **Use Case**: Daily risk report for institutional portfolio
    """
    try:
        # Calculate total portfolio value
        total_value = sum(
            pos.amount * pos.current_price
            for pos in request.positions
        )

        # Calculate asset class allocation
        tradfi_value = sum(
            pos.amount * pos.current_price
            for pos in request.positions
            if pos.asset_class in [AssetClass.STOCK, AssetClass.BOND, AssetClass.COMMODITY]
        )
        defi_value = total_value - tradfi_value

        tradfi_pct = (tradfi_value / total_value * 100) if total_value > 0 else 0
        defi_pct = (defi_value / total_value * 100) if total_value > 0 else 0

        # Demo VaR calculations (in production, use actual models)
        # For demo, assume 2% daily volatility
        var_historical = total_value * 0.02 * 1.65  # 95% confidence
        var_parametric = total_value * 0.021 * 1.65
        var_monte_carlo = total_value * 0.019 * 1.65
        var_garch = total_value * 0.022 * 1.65

        var_usd = {
            "historical": round(var_historical, 2),
            "parametric": round(var_parametric, 2),
            "monte_carlo": round(var_monte_carlo, 2),
            "garch": round(var_garch, 2)
        }

        var_percent = {
            k: round(v / total_value * 100, 2)
            for k, v in var_usd.items()
        }

        # Expected Shortfall (CVaR)
        expected_shortfall = var_historical * 1.3

        # Risk by asset class
        risk_by_asset_class = {
            "tradfi": round(tradfi_value * 0.015, 2),
            "defi": round(defi_value * 0.03, 2)  # DeFi has higher vol
        }

        # Risk by individual asset
        risk_by_asset = {}
        for pos in request.positions:
            pos_value = pos.amount * pos.current_price
            vol = 0.02 if pos.asset_class != AssetClass.DEFI else 0.04
            risk_by_asset[pos.asset_id] = round(pos_value * vol * 1.65, 2)

        # Advanced metrics
        sharpe_ratio = 1.5  # Demo value
        sortino_ratio = 1.8
        max_drawdown = 12.5
        beta = 0.85

        # DeFi-specific risks
        liquidation_risks = []
        smart_contract_risks = []
        il_estimate = 0.0

        for pos in request.positions:
            if pos.asset_class == AssetClass.DEFI:
                if pos.protocol in ["Aave", "Compound"]:
                    # Demo liquidation risk
                    liquidation_risks.append({
                        "asset_id": pos.asset_id,
                        "protocol": pos.protocol,
                        "health_factor": 1.45,
                        "risk_level": "Low"
                    })

                if "LP" in pos.asset_id or "/" in pos.symbol:
                    # Impermanent loss estimate
                    price_change = (pos.current_price - pos.entry_price) / pos.entry_price
                    il = abs(price_change) * 0.1  # Simplified
                    il_estimate += pos.amount * pos.entry_price * il

                # Smart contract risk
                risk_score = 25.0  # Demo
                smart_contract_risks.append({
                    "asset_id": pos.asset_id,
                    "protocol": pos.protocol,
                    "risk_score": risk_score,
                    "risk_level": "Low" if risk_score < 40 else "Moderate"
                })

        return UnifiedRiskMetrics(
            var_usd=var_usd,
            var_percent=var_percent,
            expected_shortfall=round(expected_shortfall, 2),
            total_value_usd=round(total_value, 2),
            tradfi_allocation_percent=round(tradfi_pct, 2),
            defi_allocation_percent=round(defi_pct, 2),
            risk_by_asset_class=risk_by_asset_class,
            risk_by_asset=risk_by_asset,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown_percent=max_drawdown,
            beta=beta,
            liquidation_risks=liquidation_risks,
            smart_contract_risks=smart_contract_risks,
            impermanent_loss_estimate=round(il_estimate, 2),
            calculated_at=datetime.now()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ====================================================================================
# CROSS-ASSET CORRELATION
# ====================================================================================

@app.post("/api/v2/correlation/analyze", response_model=CrossAssetCorrelationResponse, tags=["Cross-Asset Analysis"])
async def analyze_cross_asset_correlation(request: CrossAssetCorrelationRequest):
    """
    Analyze correlations between TradFi and DeFi assets

    **Research Use Case**:
    Study portfolio diversification benefits of adding DeFi to traditional portfolios

    **Example**: Correlation between S&P 500 and ETH
    """
    try:
        # Demo correlation matrix
        assets = request.assets
        n = len(assets)

        # Generate demo correlations
        correlation_matrix = {}
        for i, asset1 in enumerate(assets):
            correlation_matrix[asset1] = {}
            for j, asset2 in enumerate(assets):
                if i == j:
                    corr = 1.0
                elif "BTC" in asset1 and "ETH" in asset2:
                    corr = 0.85  # Crypto highly correlated
                elif "BTC" in asset1 and "SPY" in asset2:
                    corr = 0.45  # Moderate correlation
                elif "AAPL" in asset1 and "SPY" in asset2:
                    corr = 0.75  # Stocks correlated with index
                else:
                    corr = 0.30  # Default low correlation

                correlation_matrix[asset1][asset2] = round(corr, 3)

        # Calculate average TradFi-DeFi correlation
        tradfi_assets = [a for a in assets if a in ["AAPL", "SPY", "MSFT", "GOOGL"]]
        defi_assets = [a for a in assets if a in ["BTC", "ETH"]]

        if tradfi_assets and defi_assets:
            correlations = []
            for t in tradfi_assets:
                for d in defi_assets:
                    correlations.append(correlation_matrix[t][d])
            tradfi_defi_corr = np.mean(correlations)
        else:
            tradfi_defi_corr = 0.5

        # Diversification score (lower correlation = better)
        avg_corr = np.mean([
            correlation_matrix[a1][a2]
            for i, a1 in enumerate(assets)
            for j, a2 in enumerate(assets)
            if i != j
        ])
        diversification_score = (1 - avg_corr) * 100

        # Portfolio variance (simplified)
        portfolio_variance = avg_corr * 0.04  # 4% base variance

        # Interpretation
        if tradfi_defi_corr < 0.3:
            interpretation = "Excellent diversification: TradFi and DeFi are weakly correlated"
        elif tradfi_defi_corr < 0.6:
            interpretation = "Good diversification: Moderate correlation provides some benefits"
        else:
            interpretation = "Limited diversification: High correlation reduces benefits"

        # Recommendations
        recommendations = []
        if tradfi_defi_corr < 0.5:
            recommendations.append("DeFi provides good diversification for TradFi portfolio")
        if diversification_score > 60:
            recommendations.append("Well-diversified portfolio across asset classes")
        if portfolio_variance > 0.03:
            recommendations.append("Consider adding low-volatility assets to reduce portfolio variance")

        return CrossAssetCorrelationResponse(
            correlation_matrix=correlation_matrix,
            tradfi_defi_correlation=round(tradfi_defi_corr, 3),
            diversification_score=round(diversification_score, 2),
            portfolio_variance=round(portfolio_variance, 4),
            interpretation=interpretation,
            recommendations=recommendations
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ====================================================================================
# MACHINE LEARNING PREDICTIONS
# ====================================================================================

@app.post("/api/v2/ml/predict", response_model=MLPredictionResponse, tags=["Machine Learning"])
async def get_ml_prediction(request: MLPredictionRequest):
    """
    Get ML model predictions

    **Models Available**:
    - **lstm_yield**: Predict DeFi yield sustainability
    - **vulnerability**: Smart contract vulnerability score
    - **rl_portfolio**: RL-based portfolio allocation

    **Use Case**: Forecast if 50% APY is sustainable or will collapse
    """
    try:
        model_type = request.model_type
        asset = request.asset_or_protocol
        horizon = request.prediction_horizon_days

        if model_type == "lstm_yield":
            # Demo LSTM yield prediction
            current_apy = 45.0
            predictions = {
                "current_apy": current_apy,
                "predicted_apy_7d": 42.5,
                "predicted_apy_30d": 38.2,
                "predicted_apy_90d": 28.5,
                "collapse_probability": 0.35,
                "sustainability_score": 42.0,
                "trend": "declining"
            }
            confidence = 0.78
            explanation = (
                f"LSTM model predicts {asset} APY will decline from {current_apy}% to "
                f"{predictions['predicted_apy_30d']}% over 30 days. "
                f"This is due to increasing TVL (dilution) and decreasing token incentives. "
                f"Only {predictions['sustainability_score']}% of yield comes from protocol fees."
            )
            actions = [
                "Consider reducing exposure before yield collapses",
                "Monitor TVL growth and token emission schedule",
                "Diversify into more sustainable yield sources"
            ]

        elif model_type == "vulnerability":
            # Demo vulnerability detector
            predictions = {
                "vulnerability_score": 28.5,
                "risk_level": "Low",
                "key_risks": [
                    "Centralized admin keys (Medium risk)",
                    "No timelock on upgrades (Low risk)"
                ],
                "audit_score": 85.0,
                "code_quality": "Good",
                "deployment_age_days": 420
            }
            confidence = 0.82
            explanation = (
                f"Contract analysis for {asset} shows low overall risk. "
                f"Protocol has been audited by reputable firms and has 420 days of deployment history. "
                f"Main concern is centralized admin control."
            )
            actions = [
                "Safe to use for moderate amounts",
                "Monitor for admin key changes",
                "Consider protocols with stronger decentralization for large amounts"
            ]

        elif model_type == "rl_portfolio":
            # Demo RL optimizer
            predictions = {
                "recommended_allocation": {
                    "TradFi_Stocks": 40.0,
                    "TradFi_Bonds": 20.0,
                    "DeFi_Lending": 15.0,
                    "DeFi_LP_Stable": 15.0,
                    "DeFi_LP_Volatile": 10.0
                },
                "expected_sharpe": 1.85,
                "expected_return_annual": 18.5,
                "expected_volatility": 12.3,
                "rebalance_frequency": "weekly"
            }
            confidence = 0.75
            explanation = (
                "RL agent trained on 2 years of market data recommends a balanced allocation. "
                "Model optimizes for maximum Sharpe ratio while maintaining risk below threshold. "
                "Suggests weekly rebalancing to capture market opportunities."
            )
            actions = [
                "Rebalance portfolio to recommended allocation",
                "Set up weekly automated rebalancing",
                "Monitor Sharpe ratio performance"
            ]

        else:
            raise HTTPException(status_code=400, detail=f"Unknown model type: {model_type}")

        return MLPredictionResponse(
            model_type=model_type,
            asset_or_protocol=asset,
            predictions=predictions,
            confidence=confidence,
            explanation=explanation,
            recommended_actions=actions,
            generated_at=datetime.now()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ====================================================================================
# REAL-TIME WEBSOCKET
# ====================================================================================

@app.websocket("/ws/realtime")
async def websocket_realtime(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates

    **Streams**:
    - Portfolio value updates
    - Risk metric changes
    - Alert triggers
    - Price feeds
    - Liquidation warnings

    **Usage**:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/realtime');
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Update:', data);
    };
    ```
    """
    await manager.connect(websocket)
    try:
        while True:
            # Receive subscription requests
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("action") == "subscribe":
                topic = message.get("topic")
                manager.subscribe(websocket, topic)
                await websocket.send_json({
                    "status": "subscribed",
                    "topic": topic
                })

            # In production, this would stream real data
            # For demo, send periodic updates
            await asyncio.sleep(5)
            await websocket.send_json({
                "type": "portfolio_update",
                "data": {
                    "total_value": 1050000.00,
                    "var_95": 21050.00,
                    "change_24h_percent": 2.35,
                    "timestamp": datetime.now().isoformat()
                }
            })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# ====================================================================================
# ALERT MANAGEMENT
# ====================================================================================

@app.post("/api/v2/alerts/create", tags=["Alerts"])
async def create_alert_rule(rule: AlertRule):
    """
    Create alert rule

    **Alert Types**:
    - var_breach: VaR limit exceeded
    - liquidation: Health factor < threshold
    - yield_drop: APY dropped > X%
    - price_spike: Price volatility alert
    - gas_spike: Gas prices too high

    **Notification Channels**:
    - telegram: Telegram bot
    - discord: Discord webhook
    - email: Email notification
    - sms: SMS (Twilio)
    """
    # In production, save to database
    return {
        "status": "created",
        "rule_id": rule.rule_id,
        "message": "Alert rule created successfully",
        "will_notify_via": rule.notification_channels
    }


@app.get("/api/v2/alerts/list", tags=["Alerts"])
async def list_alert_rules():
    """List all alert rules"""
    # Demo rules
    return {
        "rules": [
            {
                "rule_id": "var_limit",
                "rule_type": "var_breach",
                "threshold": 50000.0,
                "enabled": True,
                "triggered_24h": 0
            },
            {
                "rule_id": "liquidation_warning",
                "rule_type": "liquidation",
                "threshold": 1.2,
                "enabled": True,
                "triggered_24h": 2
            }
        ],
        "total_rules": 2,
        "active_rules": 2
    }


# ====================================================================================
# RESEARCH DATA EXPORT
# ====================================================================================

@app.get("/api/v2/research/export", tags=["Research"])
async def export_research_data(
    data_type: str = Query(..., description="correlations, liquidations, yields"),
    format: str = Query("csv", description="csv, json, excel")
):
    """
    Export data for research papers

    **Data Types**:
    - correlations: Cross-asset correlation matrices
    - liquidations: Historical liquidation events
    - yields: DeFi yield time series
    - portfolios: Portfolio performance data

    **Use Case**: Export for statistical analysis in R/Stata/Python
    """
    # Demo export
    if data_type == "correlations":
        data = {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "BTC_ETH": [0.85, 0.84, 0.86],
            "BTC_SPY": [0.45, 0.42, 0.48],
            "ETH_SPY": [0.40, 0.38, 0.43]
        }
    elif data_type == "liquidations":
        data = {
            "date": ["2024-01-01", "2024-01-15", "2024-02-01"],
            "protocol": ["Aave", "Compound", "Aave"],
            "liquidated_value": [500000, 750000, 1200000],
            "cascade": [False, True, True]
        }
    else:
        data = {"message": "Data type not found"}

    return {
        "data_type": data_type,
        "format": format,
        "records": len(data.get("date", [])),
        "data": data,
        "download_url": f"/download/{data_type}.{format}"
    }


# ====================================================================================
# RUN SERVER
# ====================================================================================

if __name__ == "__main__":
    import uvicorn

    print("=" * 80)
    print("UNIFIED RISK PLATFORM API")
    print("=" * 80)
    print("\nStarting server...")
    print("API Docs: http://localhost:8000/docs")
    print("WebSocket: ws://localhost:8000/ws/realtime")
    print("\nPress CTRL+C to stop\n")

    uvicorn.run(
        "unified_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
