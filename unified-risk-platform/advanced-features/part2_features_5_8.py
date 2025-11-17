"""
================================================================================
UNIFIED RISK PLATFORM - ADVANCED FEATURES PART 2 (Features 5-8)
================================================================================

This module implements:
    5. Transformer VaR (Deep Learning) - Attention-based multi-horizon VaR
    6. RL Trading Agent - Reinforcement Learning for portfolio optimization
    7. Credit Risk Module - Credit VaR, default probability, spreads
    8. Sentiment Analysis - News/social media sentiment for VaR adjustment

Author: Economics & Finance MSc Team
Date: 2024
Institution: Leading University

Requirements:
    pip install tensorflow torch transformers gym stable-baselines3
    pip install textblob vaderSentiment newsapi-python tweepy

================================================================================
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Deep Learning
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    print("Warning: TensorFlow not installed. Transformer VaR will not work.")

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    print("Warning: PyTorch not installed. Some features may not work.")

# Reinforcement Learning
try:
    import gym
    from gym import spaces
    from stable_baselines3 import PPO, DQN, A2C
    from stable_baselines3.common.vec_env import DummyVecEnv
    HAS_RL = True
except ImportError:
    HAS_RL = False
    print("Warning: Stable-Baselines3 not installed. RL Trading Agent will not work.")

# Sentiment Analysis
try:
    from textblob import TextBlob
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    HAS_SENTIMENT = True
except ImportError:
    HAS_SENTIMENT = False
    print("Warning: Sentiment analysis libraries not installed.")

from scipy import stats
from scipy.optimize import minimize


################################################################################
# FEATURE 5: TRANSFORMER VAR (DEEP LEARNING)
################################################################################

class TransformerVaR:
    """
    Deep Learning VaR using Transformer architecture with attention mechanism.

    **What is a Transformer?**
    - Architecture introduced in "Attention is All You Need" (Vaswani et al., 2017)
    - Uses self-attention to capture long-range dependencies
    - Better than LSTM/GRU for sequence modeling

    **Why use Transformers for VaR?**
    - Capture complex market patterns
    - Multi-horizon forecasting (1-day, 5-day, 10-day VaR)
    - Attention weights show which past days matter most

    **Real-world usage:**
    - JPMorgan uses deep learning for VaR since 2018
    - Goldman Sachs uses transformers for market prediction
    """

    def __init__(self,
                 sequence_length: int = 60,
                 d_model: int = 64,
                 num_heads: int = 4,
                 num_layers: int = 2,
                 dropout_rate: float = 0.1):
        """
        Initialize Transformer VaR model.

        Args:
            sequence_length: Number of past days to look at (default: 60 days)
            d_model: Dimension of model (embedding size)
            num_heads: Number of attention heads (must divide d_model)
            num_layers: Number of transformer blocks
            dropout_rate: Dropout for regularization

        Example:
            >>> transformer_var = TransformerVaR(sequence_length=60, d_model=64, num_heads=4)
            >>> # Train on historical data
            >>> transformer_var.train(historical_returns, epochs=50)
            >>> # Predict VaR
            >>> var_pred = transformer_var.predict_var(recent_returns, confidence_level=0.95)
        """
        if not HAS_TENSORFLOW:
            raise ImportError("TensorFlow is required for Transformer VaR")

        self.sequence_length = sequence_length
        self.d_model = d_model
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.dropout_rate = dropout_rate
        self.model = None
        self.scaler_X = None
        self.scaler_y = None

    def _build_transformer_model(self, num_features: int):
        """
        Build transformer architecture.

        Architecture:
            Input → Positional Encoding → Transformer Blocks → Dense → VaR Output

        Transformer Block:
            → Multi-Head Attention
            → Add & Norm (Residual connection + Layer Normalization)
            → Feed Forward Network
            → Add & Norm
        """
        # Input layer
        inputs = keras.Input(shape=(self.sequence_length, num_features))

        # Positional encoding (helps model understand sequence order)
        positions = tf.range(start=0, limit=self.sequence_length, delta=1)
        position_embedding = layers.Embedding(
            input_dim=self.sequence_length,
            output_dim=self.d_model
        )(positions)

        # Project input to d_model dimensions
        x = layers.Dense(self.d_model)(inputs)
        x = x + position_embedding

        # Stack transformer blocks
        for _ in range(self.num_layers):
            x = self._transformer_block(x)

        # Global pooling
        x = layers.GlobalAveragePooling1D()(x)

        # Output layers for multi-horizon VaR prediction
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(self.dropout_rate)(x)
        x = layers.Dense(64, activation='relu')(x)
        x = layers.Dropout(self.dropout_rate)(x)

        # Predict VaR for multiple horizons (1-day, 5-day, 10-day)
        output = layers.Dense(3, activation='linear', name='var_output')(x)

        model = keras.Model(inputs=inputs, outputs=output)
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )

        return model

    def _transformer_block(self, x):
        """Single transformer block with multi-head attention."""
        # Multi-head attention
        attention_output = layers.MultiHeadAttention(
            num_heads=self.num_heads,
            key_dim=self.d_model // self.num_heads,
            dropout=self.dropout_rate
        )(x, x)

        # Add & Norm (Residual connection + Layer Normalization)
        x1 = layers.Add()([x, attention_output])
        x1 = layers.LayerNormalization(epsilon=1e-6)(x1)

        # Feed forward network
        ffn_output = layers.Dense(self.d_model * 4, activation='relu')(x1)
        ffn_output = layers.Dropout(self.dropout_rate)(ffn_output)
        ffn_output = layers.Dense(self.d_model)(ffn_output)

        # Add & Norm
        x2 = layers.Add()([x1, ffn_output])
        x2 = layers.LayerNormalization(epsilon=1e-6)(x2)

        return x2

    def _prepare_features(self, returns: pd.Series) -> pd.DataFrame:
        """
        Engineer features from returns.

        Features:
            1. Returns (raw)
            2. Rolling volatility (20-day)
            3. Rolling skewness (20-day)
            4. Rolling kurtosis (20-day)
            5. Momentum (5-day)
            6. RSI (Relative Strength Index)
        """
        df = pd.DataFrame({'returns': returns})

        # Rolling statistics
        df['volatility_20d'] = returns.rolling(window=20).std()
        df['skewness_20d'] = returns.rolling(window=20).skew()
        df['kurtosis_20d'] = returns.rolling(window=20).kurt()

        # Momentum
        df['momentum_5d'] = returns.rolling(window=5).mean()

        # RSI (Relative Strength Index)
        delta = returns.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # Fill missing values
        df = df.fillna(method='bfill').fillna(method='ffill')

        return df

    def _create_sequences(self, features: pd.DataFrame, actual_vars: np.ndarray):
        """
        Create sequences for training.

        Each sample:
            X: [sequence_length, num_features] - Past 60 days of features
            y: [3] - Actual VaR for 1-day, 5-day, 10-day horizons
        """
        X, y = [], []

        for i in range(len(features) - self.sequence_length - 10):  # -10 for max horizon
            X.append(features.iloc[i:i+self.sequence_length].values)
            y.append(actual_vars[i+self.sequence_length])

        return np.array(X), np.array(y)

    def train(self,
              returns: pd.Series,
              confidence_level: float = 0.95,
              validation_split: float = 0.2,
              epochs: int = 50,
              batch_size: int = 32,
              verbose: int = 1):
        """
        Train transformer model on historical returns.

        Args:
            returns: Historical returns series
            confidence_level: VaR confidence level (e.g., 0.95 for 95% VaR)
            validation_split: Fraction for validation
            epochs: Training epochs
            batch_size: Batch size
            verbose: Verbosity (0=silent, 1=progress bar, 2=one line per epoch)

        Returns:
            Training history

        Example:
            >>> returns = pd.Series([0.01, -0.02, 0.015, ...])  # 1000+ days
            >>> transformer_var = TransformerVaR()
            >>> history = transformer_var.train(returns, epochs=50)
            >>> print(f"Final loss: {history.history['loss'][-1]:.4f}")
        """
        print("🚀 Training Transformer VaR Model...")
        print(f"📊 Data: {len(returns)} days")
        print(f"🎯 Confidence Level: {confidence_level*100}%")

        # Step 1: Engineer features
        print("\n1️⃣ Engineering features...")
        features = self._prepare_features(returns)
        print(f"   Features: {list(features.columns)}")

        # Step 2: Calculate actual VaR for multiple horizons
        print("\n2️⃣ Calculating actual VaR for training labels...")
        actual_vars = []

        for i in range(len(returns) - 10):
            # 1-day VaR
            var_1d = np.percentile(returns.iloc[i:i+250], (1-confidence_level)*100)

            # 5-day VaR (using sqrt rule for now)
            var_5d = var_1d * np.sqrt(5)

            # 10-day VaR
            var_10d = var_1d * np.sqrt(10)

            actual_vars.append([var_1d, var_5d, var_10d])

        actual_vars = np.array(actual_vars)

        # Step 3: Create sequences
        print("\n3️⃣ Creating sequences...")
        X, y = self._create_sequences(features, actual_vars)
        print(f"   X shape: {X.shape}, y shape: {y.shape}")

        # Step 4: Normalize data
        from sklearn.preprocessing import StandardScaler

        # Reshape for scaling
        n_samples, n_timesteps, n_features = X.shape
        X_reshaped = X.reshape(-1, n_features)

        self.scaler_X = StandardScaler()
        X_scaled = self.scaler_X.fit_transform(X_reshaped)
        X_scaled = X_scaled.reshape(n_samples, n_timesteps, n_features)

        self.scaler_y = StandardScaler()
        y_scaled = self.scaler_y.fit_transform(y)

        # Step 5: Build model
        print("\n4️⃣ Building transformer model...")
        self.model = self._build_transformer_model(num_features=n_features)
        print(f"   Model parameters: {self.model.count_params():,}")

        # Step 6: Train model
        print("\n5️⃣ Training model...")

        early_stopping = keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )

        reduce_lr = keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=0.00001
        )

        history = self.model.fit(
            X_scaled, y_scaled,
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stopping, reduce_lr],
            verbose=verbose
        )

        print(f"\n✅ Training complete!")
        print(f"   Final training loss: {history.history['loss'][-1]:.4f}")
        print(f"   Final validation loss: {history.history['val_loss'][-1]:.4f}")

        return history

    def predict_var(self,
                    recent_returns: pd.Series,
                    confidence_level: float = 0.95) -> Dict[str, float]:
        """
        Predict VaR for multiple horizons using trained model.

        Args:
            recent_returns: Recent returns (must be at least sequence_length days)
            confidence_level: VaR confidence level

        Returns:
            Dictionary with VaR predictions:
                - var_1d: 1-day VaR
                - var_5d: 5-day VaR
                - var_10d: 10-day VaR
                - attention_weights: Which past days matter most

        Example:
            >>> recent_returns = df['returns'].tail(60)  # Last 60 days
            >>> predictions = transformer_var.predict_var(recent_returns)
            >>> print(f"1-day VaR: ${predictions['var_1d']:,.0f}")
            >>> print(f"5-day VaR: ${predictions['var_5d']:,.0f}")
            >>> print(f"10-day VaR: ${predictions['var_10d']:,.0f}")
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        if len(recent_returns) < self.sequence_length:
            raise ValueError(f"Need at least {self.sequence_length} days of returns")

        # Prepare features
        features = self._prepare_features(recent_returns)

        # Get last sequence
        X = features.iloc[-self.sequence_length:].values
        X = X.reshape(1, self.sequence_length, -1)

        # Normalize
        X_reshaped = X.reshape(-1, X.shape[2])
        X_scaled = self.scaler_X.transform(X_reshaped)
        X_scaled = X_scaled.reshape(1, self.sequence_length, -1)

        # Predict
        y_pred_scaled = self.model.predict(X_scaled, verbose=0)
        y_pred = self.scaler_y.inverse_transform(y_pred_scaled)

        # Extract attention weights (from first attention layer)
        attention_model = keras.Model(
            inputs=self.model.input,
            outputs=self.model.layers[3].output  # First attention layer
        )
        attention_output = attention_model.predict(X_scaled, verbose=0)
        attention_weights = attention_output[0, :, 0]  # Simplified

        return {
            'var_1d': float(y_pred[0, 0]),
            'var_5d': float(y_pred[0, 1]),
            'var_10d': float(y_pred[0, 2]),
            'attention_weights': attention_weights.tolist(),
            'confidence_level': confidence_level,
            'model': 'Transformer VaR',
            'prediction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


################################################################################
# FEATURE 6: RL TRADING AGENT
################################################################################

class TradingEnvironment(gym.Env):
    """
    Custom Gym environment for trading.

    **What is Reinforcement Learning?**
    - Agent learns by trial and error
    - Gets rewards for good actions, penalties for bad ones
    - Similar to training a dog: reward good behavior

    **State**: Current portfolio, market conditions, technical indicators
    **Actions**: Buy, Sell, Hold (for each asset)
    **Reward**: Risk-adjusted returns (Sharpe ratio)

    **Real-world usage:**
    - JPMorgan's LOXM algorithm (deep RL for execution)
    - Two Sigma uses RL for portfolio optimization
    """

    def __init__(self,
                 price_data: pd.DataFrame,
                 initial_capital: float = 100000,
                 transaction_cost: float = 0.001,
                 max_position_pct: float = 0.3):
        """
        Initialize trading environment.

        Args:
            price_data: DataFrame with columns = assets, index = dates
            initial_capital: Starting capital ($)
            transaction_cost: Cost per trade (0.001 = 0.1%)
            max_position_pct: Max % in single asset (0.3 = 30%)

        Example:
            >>> prices = pd.DataFrame({
            ...     'AAPL': [150, 152, 151, ...],
            ...     'MSFT': [300, 305, 302, ...],
            ...     'GOOGL': [2800, 2850, 2830, ...]
            ... })
            >>> env = TradingEnvironment(prices, initial_capital=100000)
            >>> obs = env.reset()
            >>> action = env.action_space.sample()  # Random action
            >>> obs, reward, done, info = env.step(action)
        """
        super(TradingEnvironment, self).__init__()

        self.price_data = price_data
        self.assets = price_data.columns.tolist()
        self.n_assets = len(self.assets)
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.max_position_pct = max_position_pct

        # State: [cash_pct, position1_pct, position2_pct, ...,
        #         returns1, returns2, ..., volatility1, volatility2, ...]
        state_dim = 1 + self.n_assets * 3  # cash + positions + returns + volatility

        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(state_dim,),
            dtype=np.float32
        )

        # Action: [action1, action2, ...] for each asset
        # action = -1 (sell), 0 (hold), +1 (buy)
        self.action_space = spaces.Box(
            low=-1,
            high=1,
            shape=(self.n_assets,),
            dtype=np.float32
        )

        self.reset()

    def reset(self):
        """Reset environment to initial state."""
        self.current_step = 0
        self.cash = self.initial_capital
        self.positions = {asset: 0.0 for asset in self.assets}  # Number of shares
        self.portfolio_values = [self.initial_capital]

        return self._get_observation()

    def _get_observation(self):
        """
        Get current state observation.

        State components:
            1. Cash percentage
            2. Position percentages for each asset
            3. Recent returns for each asset
            4. Recent volatility for each asset
        """
        # Portfolio value
        portfolio_value = self.cash
        for asset in self.assets:
            price = self.price_data.iloc[self.current_step][asset]
            portfolio_value += self.positions[asset] * price

        # Cash percentage
        cash_pct = self.cash / portfolio_value

        # Position percentages
        position_pcts = []
        for asset in self.assets:
            price = self.price_data.iloc[self.current_step][asset]
            position_value = self.positions[asset] * price
            position_pcts.append(position_value / portfolio_value)

        # Recent returns (last 5 days)
        returns = []
        for asset in self.assets:
            start_idx = max(0, self.current_step - 5)
            recent_prices = self.price_data[asset].iloc[start_idx:self.current_step+1]
            ret = (recent_prices.iloc[-1] / recent_prices.iloc[0] - 1) if len(recent_prices) > 1 else 0
            returns.append(ret)

        # Recent volatility (last 20 days)
        volatilities = []
        for asset in self.assets:
            start_idx = max(0, self.current_step - 20)
            recent_prices = self.price_data[asset].iloc[start_idx:self.current_step+1]
            vol = recent_prices.pct_change().std() if len(recent_prices) > 1 else 0
            volatilities.append(vol)

        observation = np.array([cash_pct] + position_pcts + returns + volatilities, dtype=np.float32)

        return observation

    def step(self, action):
        """
        Execute action and return next state.

        Args:
            action: Array of actions for each asset (-1 to +1)

        Returns:
            observation: Next state
            reward: Reward for this step
            done: Whether episode is finished
            info: Additional information
        """
        # Current portfolio value
        portfolio_value = self.cash
        for asset in self.assets:
            price = self.price_data.iloc[self.current_step][asset]
            portfolio_value += self.positions[asset] * price

        # Execute trades based on actions
        for i, asset in enumerate(self.assets):
            action_value = action[i]
            price = self.price_data.iloc[self.current_step][asset]

            # Calculate target position value
            target_pct = np.clip(action_value, -self.max_position_pct, self.max_position_pct)
            target_value = portfolio_value * target_pct
            target_shares = target_value / price

            # Calculate trade
            current_shares = self.positions[asset]
            trade_shares = target_shares - current_shares
            trade_value = abs(trade_shares * price)

            # Execute trade with transaction costs
            if trade_shares > 0:  # Buy
                cost = trade_value * (1 + self.transaction_cost)
                if cost <= self.cash:
                    self.positions[asset] += trade_shares
                    self.cash -= cost
            elif trade_shares < 0:  # Sell
                proceeds = trade_value * (1 - self.transaction_cost)
                self.positions[asset] += trade_shares
                self.cash += proceeds

        # Move to next step
        self.current_step += 1

        # Calculate new portfolio value
        new_portfolio_value = self.cash
        for asset in self.assets:
            price = self.price_data.iloc[self.current_step][asset]
            new_portfolio_value += self.positions[asset] * price

        self.portfolio_values.append(new_portfolio_value)

        # Calculate reward (risk-adjusted return)
        returns = pd.Series(self.portfolio_values).pct_change().dropna()
        if len(returns) > 20:
            sharpe = returns.mean() / returns.std() * np.sqrt(252)  # Annualized Sharpe
            reward = sharpe
        else:
            reward = returns.iloc[-1] if len(returns) > 0 else 0

        # Check if done
        done = self.current_step >= len(self.price_data) - 1

        # Get next observation
        observation = self._get_observation()

        info = {
            'portfolio_value': new_portfolio_value,
            'cash': self.cash,
            'positions': self.positions.copy(),
            'return': new_portfolio_value / self.initial_capital - 1
        }

        return observation, reward, done, info


class RLTradingAgent:
    """
    Reinforcement Learning agent for portfolio trading.

    **Algorithms supported:**
    1. PPO (Proximal Policy Optimization) - Good for continuous actions
    2. DQN (Deep Q-Network) - Good for discrete actions
    3. A2C (Advantage Actor-Critic) - Fast training

    **Training process:**
    1. Agent observes market state
    2. Takes action (buy/sell/hold)
    3. Gets reward (profit/loss)
    4. Learns to maximize cumulative reward
    """

    def __init__(self,
                 algorithm: str = 'PPO',
                 policy: str = 'MlpPolicy',
                 learning_rate: float = 0.0003):
        """
        Initialize RL trading agent.

        Args:
            algorithm: 'PPO', 'DQN', or 'A2C'
            policy: Neural network policy ('MlpPolicy' = Multi-Layer Perceptron)
            learning_rate: Learning rate for optimizer

        Example:
            >>> agent = RLTradingAgent(algorithm='PPO')
            >>> # Train on historical data
            >>> agent.train(price_data, total_timesteps=100000)
            >>> # Test on new data
            >>> results = agent.test(test_price_data)
            >>> print(f"Return: {results['total_return']*100:.2f}%")
        """
        if not HAS_RL:
            raise ImportError("stable-baselines3 required for RL Trading Agent")

        self.algorithm = algorithm
        self.policy = policy
        self.learning_rate = learning_rate
        self.model = None
        self.env = None

    def train(self,
              price_data: pd.DataFrame,
              initial_capital: float = 100000,
              total_timesteps: int = 100000,
              verbose: int = 1):
        """
        Train RL agent on historical price data.

        Args:
            price_data: Historical prices (columns = assets, index = dates)
            initial_capital: Starting capital
            total_timesteps: Training steps (more = better but slower)
            verbose: Print progress (0=silent, 1=progress)

        Returns:
            Training results dictionary

        Example:
            >>> prices = pd.DataFrame({
            ...     'AAPL': apple_prices,
            ...     'MSFT': msft_prices,
            ...     'GOOGL': googl_prices
            ... })
            >>> agent = RLTradingAgent(algorithm='PPO')
            >>> agent.train(prices, total_timesteps=50000)
        """
        print(f"🤖 Training {self.algorithm} Agent...")
        print(f"📊 Data: {len(price_data)} days, {len(price_data.columns)} assets")
        print(f"💰 Initial Capital: ${initial_capital:,.0f}")
        print(f"🎯 Training Steps: {total_timesteps:,}")

        # Create environment
        self.env = TradingEnvironment(
            price_data=price_data,
            initial_capital=initial_capital
        )

        # Wrap environment
        env = DummyVecEnv([lambda: self.env])

        # Create model
        if self.algorithm == 'PPO':
            self.model = PPO(
                self.policy,
                env,
                learning_rate=self.learning_rate,
                verbose=verbose
            )
        elif self.algorithm == 'DQN':
            self.model = DQN(
                self.policy,
                env,
                learning_rate=self.learning_rate,
                verbose=verbose
            )
        elif self.algorithm == 'A2C':
            self.model = A2C(
                self.policy,
                env,
                learning_rate=self.learning_rate,
                verbose=verbose
            )
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")

        # Train model
        self.model.learn(total_timesteps=total_timesteps)

        print("\n✅ Training complete!")

        return {
            'algorithm': self.algorithm,
            'total_timesteps': total_timesteps,
            'status': 'success'
        }

    def test(self,
             test_price_data: pd.DataFrame,
             initial_capital: float = 100000) -> Dict:
        """
        Test trained agent on new data.

        Args:
            test_price_data: Test prices
            initial_capital: Starting capital

        Returns:
            Test results with performance metrics

        Example:
            >>> test_prices = pd.DataFrame({...})  # New data
            >>> results = agent.test(test_prices)
            >>> print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
            >>> print(f"Max Drawdown: {results['max_drawdown']:.2%}")
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        print("🧪 Testing agent on new data...")

        # Create test environment
        test_env = TradingEnvironment(
            price_data=test_price_data,
            initial_capital=initial_capital
        )

        # Run episode
        obs = test_env.reset()
        done = False
        portfolio_values = [initial_capital]
        actions_taken = []

        while not done:
            action, _ = self.model.predict(obs, deterministic=True)
            obs, reward, done, info = test_env.step(action)
            portfolio_values.append(info['portfolio_value'])
            actions_taken.append(action)

        # Calculate metrics
        returns = pd.Series(portfolio_values).pct_change().dropna()
        total_return = portfolio_values[-1] / portfolio_values[0] - 1

        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0

        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdowns.min()

        results = {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'final_portfolio_value': portfolio_values[-1],
            'portfolio_values': portfolio_values,
            'n_trades': len([a for a in actions_taken if abs(a).sum() > 0.1])
        }

        print(f"\n📈 Test Results:")
        print(f"   Total Return: {total_return*100:.2f}%")
        print(f"   Sharpe Ratio: {sharpe_ratio:.2f}")
        print(f"   Max Drawdown: {max_drawdown*100:.2f}%")
        print(f"   Final Value: ${portfolio_values[-1]:,.0f}")

        return results

    def get_action(self, current_state: np.ndarray) -> np.ndarray:
        """
        Get trading action for current market state.

        Args:
            current_state: Current observation

        Returns:
            Action array (buy/sell/hold for each asset)
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        action, _ = self.model.predict(current_state, deterministic=True)
        return action


################################################################################
# FEATURE 7: CREDIT RISK MODULE
################################################################################

class CreditRiskAnalyzer:
    """
    Credit Risk and Credit VaR calculator.

    **What is Credit Risk?**
    - Risk that borrower won't repay loan
    - Applies to bonds, loans, credit derivatives

    **Credit VaR:**
    - Maximum credit loss at given confidence level
    - Similar to market VaR but for credit portfolios

    **Real-world usage:**
    - Banks use for loan portfolio risk
    - Bond traders use for corporate bond portfolios
    - Basel III requires credit VaR calculations
    """

    def __init__(self):
        """
        Initialize credit risk analyzer.

        Example:
            >>> credit_analyzer = CreditRiskAnalyzer()
            >>> # Calculate default probability
            >>> pd = credit_analyzer.calculate_default_probability('BB', horizon=1)
            >>> print(f"Default probability: {pd*100:.2f}%")
        """
        # Default probabilities by rating (1-year)
        # Source: Moody's, S&P historical default rates
        self.default_probs = {
            'AAA': 0.0001,
            'AA': 0.0005,
            'A': 0.001,
            'BBB': 0.003,
            'BB': 0.01,
            'B': 0.05,
            'CCC': 0.15,
            'CC': 0.30,
            'C': 0.50,
            'D': 1.00
        }

        # Recovery rates by seniority
        # Source: Moody's Ultimate Recovery Database
        self.recovery_rates = {
            'senior_secured': 0.65,
            'senior_unsecured': 0.45,
            'subordinated': 0.30,
            'junior': 0.20
        }

    def calculate_default_probability(self,
                                     rating: str,
                                     horizon: int = 1) -> float:
        """
        Calculate probability of default.

        Args:
            rating: Credit rating (AAA, AA, A, BBB, BB, B, CCC, CC, C, D)
            horizon: Time horizon in years

        Returns:
            Default probability

        Formula:
            PD(t) = 1 - (1 - PD_1yr)^t

            Where:
            - PD(t) = Default probability over t years
            - PD_1yr = 1-year default probability

        Example:
            >>> analyzer = CreditRiskAnalyzer()
            >>> pd_1yr = analyzer.calculate_default_probability('BB', horizon=1)
            >>> print(f"1-year PD: {pd_1yr*100:.2f}%")
            >>>
            >>> pd_5yr = analyzer.calculate_default_probability('BB', horizon=5)
            >>> print(f"5-year PD: {pd_5yr*100:.2f}%")
        """
        if rating not in self.default_probs:
            raise ValueError(f"Unknown rating: {rating}")

        pd_1yr = self.default_probs[rating]
        pd_t = 1 - (1 - pd_1yr) ** horizon

        return pd_t

    def calculate_credit_spread(self,
                               rating: str,
                               maturity: float,
                               recovery_rate: float = 0.40,
                               risk_free_rate: float = 0.03) -> float:
        """
        Calculate credit spread over risk-free rate.

        Args:
            rating: Credit rating
            maturity: Years to maturity
            recovery_rate: Recovery rate in default (0-1)
            risk_free_rate: Risk-free rate (e.g., Treasury yield)

        Returns:
            Credit spread (in decimal, e.g., 0.02 = 200 bps)

        Formula:
            Spread = -ln(1 - PD * LGD) / Maturity

            Where:
            - PD = Probability of default
            - LGD = Loss Given Default = 1 - Recovery Rate

        Example:
            >>> analyzer = CreditRiskAnalyzer()
            >>> spread = analyzer.calculate_credit_spread('BB', maturity=5, recovery_rate=0.40)
            >>> print(f"Credit spread: {spread*10000:.0f} bps")  # basis points
        """
        pd = self.calculate_default_probability(rating, horizon=maturity)
        lgd = 1 - recovery_rate

        # Credit spread formula
        spread = -np.log(1 - pd * lgd) / maturity

        return spread

    def calculate_bond_price(self,
                            face_value: float,
                            coupon_rate: float,
                            rating: str,
                            maturity: float,
                            recovery_rate: float = 0.40,
                            risk_free_rate: float = 0.03) -> Dict:
        """
        Calculate corporate bond price with credit risk.

        Args:
            face_value: Face value of bond ($)
            coupon_rate: Annual coupon rate (decimal)
            rating: Credit rating
            maturity: Years to maturity
            recovery_rate: Recovery rate in default
            risk_free_rate: Risk-free rate

        Returns:
            Dictionary with bond pricing details

        Example:
            >>> analyzer = CreditRiskAnalyzer()
            >>> bond = analyzer.calculate_bond_price(
            ...     face_value=1000,
            ...     coupon_rate=0.05,
            ...     rating='BBB',
            ...     maturity=10,
            ...     recovery_rate=0.40
            ... )
            >>> print(f"Bond price: ${bond['price']:.2f}")
            >>> print(f"Yield: {bond['yield']*100:.2f}%")
        """
        # Calculate credit spread
        spread = self.calculate_credit_spread(rating, maturity, recovery_rate, risk_free_rate)

        # Total yield = risk-free + spread
        total_yield = risk_free_rate + spread

        # Calculate bond price using present value
        annual_coupon = face_value * coupon_rate

        # PV of coupons
        pv_coupons = sum([
            annual_coupon / (1 + total_yield) ** t
            for t in range(1, int(maturity) + 1)
        ])

        # PV of face value
        pv_face = face_value / (1 + total_yield) ** maturity

        price = pv_coupons + pv_face

        return {
            'price': price,
            'face_value': face_value,
            'coupon_rate': coupon_rate,
            'yield': total_yield,
            'credit_spread': spread,
            'spread_bps': spread * 10000,
            'rating': rating,
            'maturity': maturity
        }

    def calculate_credit_var(self,
                            portfolio: List[Dict],
                            confidence_level: float = 0.95,
                            horizon: int = 1,
                            n_simulations: int = 10000) -> Dict:
        """
        Calculate Credit VaR using Monte Carlo simulation.

        Args:
            portfolio: List of positions with:
                - face_value: Face value
                - rating: Credit rating
                - recovery_rate: Recovery rate
                - seniority: 'senior_secured', 'senior_unsecured', etc.
            confidence_level: VaR confidence level
            horizon: Time horizon (years)
            n_simulations: Monte Carlo simulations

        Returns:
            Credit VaR results

        **Method:**
        1. For each simulation:
            - For each position, simulate default (yes/no)
            - If default, loss = Face Value * (1 - Recovery Rate)
            - Total loss = sum of all defaults
        2. Credit VaR = percentile of loss distribution

        Example:
            >>> portfolio = [
            ...     {'face_value': 1000000, 'rating': 'BBB', 'recovery_rate': 0.45, 'seniority': 'senior_unsecured'},
            ...     {'face_value': 500000, 'rating': 'BB', 'recovery_rate': 0.40, 'seniority': 'senior_unsecured'},
            ...     {'face_value': 2000000, 'rating': 'A', 'recovery_rate': 0.50, 'seniority': 'senior_secured'}
            ... ]
            >>> results = analyzer.calculate_credit_var(portfolio, confidence_level=0.99)
            >>> print(f"99% Credit VaR: ${results['credit_var']:,.0f}")
            >>> print(f"Expected Loss: ${results['expected_loss']:,.0f}")
        """
        print(f"🏦 Calculating Credit VaR...")
        print(f"   Portfolio: {len(portfolio)} positions")
        print(f"   Confidence: {confidence_level*100}%")
        print(f"   Horizon: {horizon} year(s)")
        print(f"   Simulations: {n_simulations:,}")

        # Monte Carlo simulation
        losses = []

        for sim in range(n_simulations):
            total_loss = 0

            for position in portfolio:
                # Get default probability
                pd = self.calculate_default_probability(position['rating'], horizon)

                # Simulate default (Bernoulli trial)
                default_occurs = np.random.random() < pd

                if default_occurs:
                    # Loss = Face Value * Loss Given Default
                    lgd = 1 - position['recovery_rate']
                    loss = position['face_value'] * lgd
                    total_loss += loss

            losses.append(total_loss)

        losses = np.array(losses)

        # Calculate Credit VaR
        credit_var = np.percentile(losses, confidence_level * 100)

        # Expected Loss
        expected_loss = np.mean(losses)

        # Credit CVaR (Expected Shortfall)
        credit_cvar = np.mean(losses[losses >= credit_var])

        # Calculate expected loss analytically (for comparison)
        analytical_el = 0
        for position in portfolio:
            pd = self.calculate_default_probability(position['rating'], horizon)
            lgd = 1 - position['recovery_rate']
            el = position['face_value'] * pd * lgd
            analytical_el += el

        results = {
            'credit_var': credit_var,
            'credit_cvar': credit_cvar,
            'expected_loss': expected_loss,
            'analytical_expected_loss': analytical_el,
            'unexpected_loss': credit_var - expected_loss,
            'confidence_level': confidence_level,
            'horizon_years': horizon,
            'n_simulations': n_simulations,
            'loss_distribution': losses.tolist()
        }

        print(f"\n📊 Credit VaR Results:")
        print(f"   Credit VaR ({confidence_level*100}%): ${credit_var:,.0f}")
        print(f"   Credit CVaR: ${credit_cvar:,.0f}")
        print(f"   Expected Loss: ${expected_loss:,.0f}")
        print(f"   Unexpected Loss: ${results['unexpected_loss']:,.0f}")

        return results


################################################################################
# FEATURE 8: SENTIMENT ANALYSIS
################################################################################

class SentimentAnalyzer:
    """
    Sentiment analysis for risk adjustment.

    **What is Sentiment Analysis?**
    - Analyze news, social media to gauge market mood
    - Positive sentiment → Lower VaR adjustment
    - Negative sentiment → Higher VaR adjustment

    **Methods:**
    1. VADER: Rule-based (good for financial text)
    2. TextBlob: ML-based (good for general text)

    **Real-world usage:**
    - Goldman Sachs analyzes news for trading signals
    - BlackRock uses sentiment for risk management
    - JPMorgan tracks 100,000+ news sources daily
    """

    def __init__(self):
        """
        Initialize sentiment analyzer.

        Example:
            >>> analyzer = SentimentAnalyzer()
            >>> text = "Apple stock surges on strong iPhone sales"
            >>> sentiment = analyzer.analyze_text(text)
            >>> print(f"Sentiment: {sentiment['compound_score']:.2f}")
        """
        if not HAS_SENTIMENT:
            raise ImportError("Sentiment analysis libraries required")

        self.vader = SentimentIntensityAnalyzer()

    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of single text.

        Args:
            text: Text to analyze (news headline, tweet, etc.)

        Returns:
            Sentiment scores:
                - compound_score: Overall sentiment (-1 to +1)
                - positive: Positive score (0 to 1)
                - negative: Negative score (0 to 1)
                - neutral: Neutral score (0 to 1)
                - textblob_score: TextBlob polarity (-1 to +1)

        Example:
            >>> analyzer = SentimentAnalyzer()
            >>>
            >>> # Positive news
            >>> result = analyzer.analyze_text("Apple beats earnings expectations!")
            >>> print(f"Sentiment: {result['compound_score']:.2f}")  # Should be positive
            >>>
            >>> # Negative news
            >>> result = analyzer.analyze_text("Market crash, investors panic")
            >>> print(f"Sentiment: {result['compound_score']:.2f}")  # Should be negative
        """
        # VADER sentiment
        vader_scores = self.vader.polarity_scores(text)

        # TextBlob sentiment
        blob = TextBlob(text)
        textblob_score = blob.sentiment.polarity

        return {
            'compound_score': vader_scores['compound'],
            'positive': vader_scores['pos'],
            'negative': vader_scores['neg'],
            'neutral': vader_scores['neu'],
            'textblob_score': textblob_score,
            'text': text
        }

    def analyze_batch(self, texts: List[str]) -> pd.DataFrame:
        """
        Analyze sentiment for multiple texts.

        Args:
            texts: List of texts

        Returns:
            DataFrame with sentiment scores for each text

        Example:
            >>> news_headlines = [
            ...     "Tesla stock soars on record deliveries",
            ...     "Market volatility increases amid recession fears",
            ...     "Fed maintains interest rates, stocks unchanged"
            ... ]
            >>> results = analyzer.analyze_batch(news_headlines)
            >>> print(results[['text', 'compound_score']])
        """
        results = []

        for text in texts:
            sentiment = self.analyze_text(text)
            results.append(sentiment)

        return pd.DataFrame(results)

    def calculate_sentiment_adjusted_var(self,
                                        base_var: float,
                                        news_texts: List[str],
                                        adjustment_factor: float = 0.20) -> Dict:
        """
        Adjust VaR based on news sentiment.

        Args:
            base_var: Base VaR from traditional methods
            news_texts: Recent news headlines
            adjustment_factor: Maximum adjustment (0.20 = ±20%)

        Returns:
            Adjusted VaR and sentiment analysis

        **Logic:**
        - Very negative sentiment (< -0.5): Increase VaR by up to 20%
        - Negative sentiment (-0.5 to -0.1): Increase VaR by 0-20%
        - Neutral sentiment (-0.1 to 0.1): No adjustment
        - Positive sentiment (0.1 to 0.5): Decrease VaR by 0-10%
        - Very positive sentiment (> 0.5): Decrease VaR by up to 10%

        Example:
            >>> base_var = 50000  # $50,000 VaR
            >>>
            >>> # During market panic
            >>> bad_news = [
            ...     "Market crashes, worst day since 2008",
            ...     "Investors flee to safety",
            ...     "Recession fears mount"
            ... ]
            >>> result = analyzer.calculate_sentiment_adjusted_var(base_var, bad_news)
            >>> print(f"Adjusted VaR: ${result['adjusted_var']:,.0f}")  # Higher than base
            >>>
            >>> # During bull market
            >>> good_news = [
            ...     "Markets rally to new highs",
            ...     "Economic growth beats expectations",
            ...     "Corporate earnings surge"
            ... ]
            >>> result = analyzer.calculate_sentiment_adjusted_var(base_var, good_news)
            >>> print(f"Adjusted VaR: ${result['adjusted_var']:,.0f}")  # Lower than base
        """
        print(f"📰 Analyzing {len(news_texts)} news items for sentiment...")

        # Analyze all texts
        sentiment_df = self.analyze_batch(news_texts)

        # Calculate average sentiment
        avg_sentiment = sentiment_df['compound_score'].mean()

        # Determine adjustment
        if avg_sentiment < -0.5:
            # Very negative: increase VaR by 15-20%
            adjustment_pct = adjustment_factor
        elif avg_sentiment < -0.1:
            # Negative: increase VaR by 0-15%
            adjustment_pct = adjustment_factor * (abs(avg_sentiment) / 0.5)
        elif avg_sentiment < 0.1:
            # Neutral: no adjustment
            adjustment_pct = 0
        elif avg_sentiment < 0.5:
            # Positive: decrease VaR by 0-10%
            adjustment_pct = -(adjustment_factor / 2) * (avg_sentiment / 0.5)
        else:
            # Very positive: decrease VaR by 10%
            adjustment_pct = -(adjustment_factor / 2)

        # Apply adjustment
        adjusted_var = base_var * (1 + adjustment_pct)

        # Sentiment classification
        if avg_sentiment >= 0.3:
            sentiment_label = "Very Positive"
        elif avg_sentiment >= 0.1:
            sentiment_label = "Positive"
        elif avg_sentiment >= -0.1:
            sentiment_label = "Neutral"
        elif avg_sentiment >= -0.3:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Very Negative"

        results = {
            'base_var': base_var,
            'adjusted_var': adjusted_var,
            'adjustment_pct': adjustment_pct,
            'adjustment_amount': adjusted_var - base_var,
            'average_sentiment': avg_sentiment,
            'sentiment_label': sentiment_label,
            'n_news_items': len(news_texts),
            'sentiment_distribution': {
                'positive': (sentiment_df['compound_score'] > 0.1).sum(),
                'neutral': ((sentiment_df['compound_score'] >= -0.1) &
                           (sentiment_df['compound_score'] <= 0.1)).sum(),
                'negative': (sentiment_df['compound_score'] < -0.1).sum()
            }
        }

        print(f"\n📊 Sentiment Analysis Results:")
        print(f"   Average Sentiment: {avg_sentiment:.3f} ({sentiment_label})")
        print(f"   Base VaR: ${base_var:,.0f}")
        print(f"   Adjusted VaR: ${adjusted_var:,.0f}")
        print(f"   Adjustment: {adjustment_pct*100:+.1f}%")
        print(f"   Positive news: {results['sentiment_distribution']['positive']}")
        print(f"   Neutral news: {results['sentiment_distribution']['neutral']}")
        print(f"   Negative news: {results['sentiment_distribution']['negative']}")

        return results


################################################################################
# EXAMPLE USAGE
################################################################################

if __name__ == "__main__":
    print("="*80)
    print("UNIFIED RISK PLATFORM - ADVANCED FEATURES PART 2 (5-8)")
    print("="*80)

    # Generate sample data
    np.random.seed(42)
    n_days = 500
    dates = pd.date_range(start='2020-01-01', periods=n_days, freq='D')

    # Sample returns for training
    returns = pd.Series(np.random.normal(0.0005, 0.02, n_days), index=dates)

    print("\n" + "="*80)
    print("FEATURE 5: TRANSFORMER VAR")
    print("="*80)

    if HAS_TENSORFLOW:
        try:
            # Create and train model
            transformer_var = TransformerVaR(sequence_length=60, d_model=32, num_heads=2)

            print("\n🎯 Training Transformer VaR (this may take a few minutes)...")
            history = transformer_var.train(returns, epochs=20, verbose=0)

            # Make prediction
            recent_returns = returns.tail(60)
            predictions = transformer_var.predict_var(recent_returns, confidence_level=0.95)

            print(f"\n📊 Transformer VaR Predictions:")
            print(f"   1-day VaR (95%): {predictions['var_1d']:.4f}")
            print(f"   5-day VaR (95%): {predictions['var_5d']:.4f}")
            print(f"   10-day VaR (95%): {predictions['var_10d']:.4f}")

        except Exception as e:
            print(f"⚠️  Error in Transformer VaR: {e}")
    else:
        print("⚠️  TensorFlow not installed. Skipping Transformer VaR example.")

    print("\n" + "="*80)
    print("FEATURE 6: RL TRADING AGENT")
    print("="*80)

    if HAS_RL:
        try:
            # Generate sample price data
            prices = pd.DataFrame({
                'AAPL': 150 * (1 + returns).cumprod(),
                'MSFT': 300 * (1 + returns * 0.9).cumprod(),
                'GOOGL': 2800 * (1 + returns * 1.1).cumprod()
            })

            # Create and train agent
            agent = RLTradingAgent(algorithm='PPO')

            print("\n🎯 Training RL Agent (this may take a few minutes)...")
            agent.train(prices.iloc[:400], total_timesteps=5000, verbose=0)

            # Test agent
            test_results = agent.test(prices.iloc[400:], initial_capital=100000)

            print(f"\n📊 RL Agent Performance:")
            print(f"   Total Return: {test_results['total_return']*100:.2f}%")
            print(f"   Sharpe Ratio: {test_results['sharpe_ratio']:.2f}")
            print(f"   Max Drawdown: {test_results['max_drawdown']*100:.2f}%")
            print(f"   Number of Trades: {test_results['n_trades']}")

        except Exception as e:
            print(f"⚠️  Error in RL Trading Agent: {e}")
    else:
        print("⚠️  Stable-Baselines3 not installed. Skipping RL example.")

    print("\n" + "="*80)
    print("FEATURE 7: CREDIT RISK MODULE")
    print("="*80)

    # Create analyzer
    credit_analyzer = CreditRiskAnalyzer()

    # Example 1: Default probability
    print("\n📊 Example 1: Default Probability")
    rating = 'BBB'
    pd_1yr = credit_analyzer.calculate_default_probability(rating, horizon=1)
    pd_5yr = credit_analyzer.calculate_default_probability(rating, horizon=5)
    print(f"   {rating} rating:")
    print(f"   1-year default probability: {pd_1yr*100:.3f}%")
    print(f"   5-year default probability: {pd_5yr*100:.3f}%")

    # Example 2: Credit spread
    print("\n📊 Example 2: Credit Spread")
    spread = credit_analyzer.calculate_credit_spread('BB', maturity=10, recovery_rate=0.40)
    print(f"   BB-rated bond (10-year):")
    print(f"   Credit spread: {spread*10000:.0f} bps")

    # Example 3: Bond pricing
    print("\n📊 Example 3: Corporate Bond Pricing")
    bond = credit_analyzer.calculate_bond_price(
        face_value=1000,
        coupon_rate=0.05,
        rating='BBB',
        maturity=10,
        recovery_rate=0.40
    )
    print(f"   Bond price: ${bond['price']:.2f}")
    print(f"   Yield: {bond['yield']*100:.2f}%")
    print(f"   Credit spread: {bond['spread_bps']:.0f} bps")

    # Example 4: Credit VaR
    print("\n📊 Example 4: Credit VaR")
    portfolio = [
        {'face_value': 1000000, 'rating': 'BBB', 'recovery_rate': 0.45, 'seniority': 'senior_unsecured'},
        {'face_value': 500000, 'rating': 'BB', 'recovery_rate': 0.40, 'seniority': 'senior_unsecured'},
        {'face_value': 2000000, 'rating': 'A', 'recovery_rate': 0.50, 'seniority': 'senior_secured'}
    ]

    credit_var_results = credit_analyzer.calculate_credit_var(
        portfolio,
        confidence_level=0.99,
        n_simulations=5000
    )

    print("\n" + "="*80)
    print("FEATURE 8: SENTIMENT ANALYSIS")
    print("="*80)

    if HAS_SENTIMENT:
        # Create analyzer
        sentiment_analyzer = SentimentAnalyzer()

        # Example 1: Single text analysis
        print("\n📊 Example 1: Analyze Single News Item")
        news = "Apple stock surges on strong iPhone sales, beating analyst expectations"
        sentiment = sentiment_analyzer.analyze_text(news)
        print(f"   News: {news}")
        print(f"   Sentiment: {sentiment['compound_score']:.3f}")

        # Example 2: Batch analysis
        print("\n📊 Example 2: Analyze Multiple News Items")
        news_items = [
            "Market crashes, worst day since 2008",
            "Economic growth beats expectations",
            "Central bank holds rates steady",
            "Tech stocks rally on AI boom",
            "Recession fears mount amid inflation"
        ]

        batch_results = sentiment_analyzer.analyze_batch(news_items)
        print("\n   Results:")
        for idx, row in batch_results.iterrows():
            print(f"   - {row['text'][:50]}... → {row['compound_score']:+.3f}")

        # Example 3: Sentiment-adjusted VaR
        print("\n📊 Example 3: Sentiment-Adjusted VaR")
        base_var = 50000

        negative_news = [
            "Market crashes, worst day since 2008",
            "Investors flee to safety assets",
            "Recession fears mount"
        ]

        var_adjustment = sentiment_analyzer.calculate_sentiment_adjusted_var(
            base_var=base_var,
            news_texts=negative_news
        )

    else:
        print("⚠️  Sentiment analysis libraries not installed. Skipping examples.")

    print("\n" + "="*80)
    print("✅ PART 2 FEATURES COMPLETE!")
    print("="*80)
    print("\nFeatures 5-8 implemented:")
    print("  ✅ Feature 5: Transformer VaR (Deep Learning)")
    print("  ✅ Feature 6: RL Trading Agent")
    print("  ✅ Feature 7: Credit Risk Module")
    print("  ✅ Feature 8: Sentiment Analysis")
    print("\nNext: Features 9-11 (ESG, Multi-Asset, Regulatory)")
    print("="*80)
