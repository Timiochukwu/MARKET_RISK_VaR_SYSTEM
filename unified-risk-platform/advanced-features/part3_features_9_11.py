"""
================================================================================
UNIFIED RISK PLATFORM - ADVANCED FEATURES PART 3 (Features 9-11)
================================================================================

This module implements:
    9. ESG Risk Scoring - Environmental, Social, Governance risk assessment
    10. Multi-Asset Expansion - Bonds, Commodities, Real Estate, FX VaR
    11. Regulatory Reporting - Basel III, FRTB, Stress Testing

Author: Economics & Finance MSc Team
Date: 2024
Institution: Leading University

Requirements:
    pip install pandas numpy scipy matplotlib requests

================================================================================
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

from scipy import stats
from scipy.optimize import minimize


################################################################################
# FEATURE 9: ESG RISK SCORING
################################################################################

class ESGRiskAnalyzer:
    """
    ESG (Environmental, Social, Governance) Risk Scoring.

    **What is ESG Risk?**
    - Environmental: Climate change, pollution, resource depletion
    - Social: Labor practices, human rights, diversity
    - Governance: Board structure, executive compensation, shareholder rights

    **Why ESG matters for risk:**
    - ESG controversies can cause stock crashes (e.g., Volkswagen diesel scandal)
    - Climate risk affects long-term valuations
    - Poor governance increases fraud risk

    **Real-world usage:**
    - BlackRock integrates ESG into all investments
    - Pension funds require ESG screening
    - EU requires ESG disclosure (SFDR regulation)
    """

    def __init__(self):
        """
        Initialize ESG risk analyzer.

        Example:
            >>> esg_analyzer = ESGRiskAnalyzer()
            >>> # Score a company
            >>> score = esg_analyzer.calculate_esg_score(
            ...     carbon_emissions=50000,
            ...     renewable_energy_pct=0.30,
            ...     board_independence=0.60,
            ...     employee_turnover=0.15
            ... )
            >>> print(f"ESG Score: {score['total_score']:.0f}/100")
        """
        # ESG weights (can be customized)
        self.weights = {
            'environmental': 0.35,
            'social': 0.35,
            'governance': 0.30
        }

    def calculate_environmental_score(self,
                                     carbon_emissions: float,
                                     revenue_millions: float,
                                     renewable_energy_pct: float,
                                     water_usage_intensity: float = 50.0,
                                     waste_recycling_rate: float = 0.50) -> Dict:
        """
        Calculate Environmental score (0-100).

        Args:
            carbon_emissions: Total CO2 emissions (tonnes/year)
            revenue_millions: Annual revenue ($ millions)
            renewable_energy_pct: % renewable energy (0-1)
            water_usage_intensity: Water usage per $1M revenue (cubic meters)
            waste_recycling_rate: % waste recycled (0-1)

        Returns:
            Environmental score and breakdown

        **Scoring:**
        1. Carbon intensity (40%): Lower is better
        2. Renewable energy (30%): Higher is better
        3. Water efficiency (15%): Lower is better
        4. Waste recycling (15%): Higher is better

        Example:
            >>> # Good environmental performance
            >>> score = analyzer.calculate_environmental_score(
            ...     carbon_emissions=10000,
            ...     revenue_millions=500,
            ...     renewable_energy_pct=0.80,
            ...     water_usage_intensity=20,
            ...     waste_recycling_rate=0.90
            ... )
            >>> print(f"Environmental Score: {score['score']:.0f}/100")
        """
        # 1. Carbon intensity (tonnes CO2 per $1M revenue)
        carbon_intensity = carbon_emissions / revenue_millions

        # Benchmark: Good = <20, Average = 20-100, Poor = >100
        if carbon_intensity < 20:
            carbon_score = 100
        elif carbon_intensity < 100:
            carbon_score = 100 - (carbon_intensity - 20) * 1.25  # Linear decline
        else:
            carbon_score = max(0, 25 - (carbon_intensity - 100) * 0.25)

        # 2. Renewable energy score
        renewable_score = renewable_energy_pct * 100

        # 3. Water efficiency score
        # Benchmark: Good = <30, Average = 30-70, Poor = >70
        if water_usage_intensity < 30:
            water_score = 100
        elif water_usage_intensity < 70:
            water_score = 100 - (water_usage_intensity - 30) * 2.5
        else:
            water_score = max(0, 25 - (water_usage_intensity - 70) * 0.5)

        # 4. Waste recycling score
        waste_score = waste_recycling_rate * 100

        # Weighted total
        env_score = (
            carbon_score * 0.40 +
            renewable_score * 0.30 +
            water_score * 0.15 +
            waste_score * 0.15
        )

        return {
            'score': env_score,
            'carbon_intensity': carbon_intensity,
            'carbon_score': carbon_score,
            'renewable_score': renewable_score,
            'water_score': water_score,
            'waste_score': waste_score,
            'breakdown': {
                'Carbon Efficiency (40%)': carbon_score,
                'Renewable Energy (30%)': renewable_score,
                'Water Efficiency (15%)': water_score,
                'Waste Recycling (15%)': waste_score
            }
        }

    def calculate_social_score(self,
                              employee_turnover: float,
                              gender_diversity_pct: float,
                              workplace_injuries_per_100: float,
                              training_hours_per_employee: float,
                              community_investment_pct_revenue: float = 0.01) -> Dict:
        """
        Calculate Social score (0-100).

        Args:
            employee_turnover: Annual turnover rate (0-1, e.g., 0.15 = 15%)
            gender_diversity_pct: % women in workforce (0-1)
            workplace_injuries_per_100: Injuries per 100 employees
            training_hours_per_employee: Annual training hours per employee
            community_investment_pct_revenue: Community investment as % of revenue

        Returns:
            Social score and breakdown

        **Scoring:**
        1. Employee retention (25%): Lower turnover is better
        2. Diversity (25%): Closer to 50% is better
        3. Safety (25%): Fewer injuries is better
        4. Training (15%): More hours is better
        5. Community impact (10%): Higher investment is better

        Example:
            >>> # Good social performance
            >>> score = analyzer.calculate_social_score(
            ...     employee_turnover=0.08,
            ...     gender_diversity_pct=0.45,
            ...     workplace_injuries_per_100=1.5,
            ...     training_hours_per_employee=50,
            ...     community_investment_pct_revenue=0.02
            ... )
            >>> print(f"Social Score: {score['score']:.0f}/100")
        """
        # 1. Employee retention score
        # Benchmark: Good = <10%, Average = 10-25%, Poor = >25%
        if employee_turnover < 0.10:
            retention_score = 100
        elif employee_turnover < 0.25:
            retention_score = 100 - (employee_turnover - 0.10) * 666.67
        else:
            retention_score = max(0, 25 - (employee_turnover - 0.25) * 100)

        # 2. Diversity score (optimal is 50%)
        diversity_distance = abs(gender_diversity_pct - 0.50)
        diversity_score = max(0, 100 - diversity_distance * 200)

        # 3. Safety score
        # Benchmark: Good = <2, Average = 2-5, Poor = >5
        if workplace_injuries_per_100 < 2:
            safety_score = 100
        elif workplace_injuries_per_100 < 5:
            safety_score = 100 - (workplace_injuries_per_100 - 2) * 33.33
        else:
            safety_score = max(0, 25 - (workplace_injuries_per_100 - 5) * 5)

        # 4. Training score
        # Benchmark: Good = >40hrs, Average = 20-40hrs, Poor = <20hrs
        if training_hours_per_employee > 40:
            training_score = 100
        elif training_hours_per_employee > 20:
            training_score = 50 + (training_hours_per_employee - 20) * 2.5
        else:
            training_score = max(0, training_hours_per_employee * 2.5)

        # 5. Community investment score
        # Benchmark: Good = >1%, Average = 0.5-1%, Poor = <0.5%
        community_pct = community_investment_pct_revenue
        if community_pct > 0.01:
            community_score = 100
        elif community_pct > 0.005:
            community_score = 50 + (community_pct - 0.005) * 10000
        else:
            community_score = max(0, community_pct * 10000)

        # Weighted total
        social_score = (
            retention_score * 0.25 +
            diversity_score * 0.25 +
            safety_score * 0.25 +
            training_score * 0.15 +
            community_score * 0.10
        )

        return {
            'score': social_score,
            'retention_score': retention_score,
            'diversity_score': diversity_score,
            'safety_score': safety_score,
            'training_score': training_score,
            'community_score': community_score,
            'breakdown': {
                'Employee Retention (25%)': retention_score,
                'Gender Diversity (25%)': diversity_score,
                'Workplace Safety (25%)': safety_score,
                'Training & Development (15%)': training_score,
                'Community Investment (10%)': community_score
            }
        }

    def calculate_governance_score(self,
                                  board_independence_pct: float,
                                  female_board_members_pct: float,
                                  ceo_pay_ratio: float,
                                  shareholder_rights_score: float = 70.0,
                                  audit_quality: str = 'Big4') -> Dict:
        """
        Calculate Governance score (0-100).

        Args:
            board_independence_pct: % independent board members (0-1)
            female_board_members_pct: % women on board (0-1)
            ceo_pay_ratio: CEO pay / Median employee pay
            shareholder_rights_score: Shareholder rights (0-100)
            audit_quality: Auditor quality ('Big4', 'Top10', 'Other')

        Returns:
            Governance score and breakdown

        **Scoring:**
        1. Board independence (30%): Higher is better
        2. Board diversity (20%): Higher is better
        3. Executive compensation (25%): Lower CEO ratio is better
        4. Shareholder rights (15%): Higher is better
        5. Audit quality (10%): Big4 is best

        Example:
            >>> # Good governance
            >>> score = analyzer.calculate_governance_score(
            ...     board_independence_pct=0.75,
            ...     female_board_members_pct=0.40,
            ...     ceo_pay_ratio=100,
            ...     shareholder_rights_score=80,
            ...     audit_quality='Big4'
            ... )
            >>> print(f"Governance Score: {score['score']:.0f}/100")
        """
        # 1. Board independence score
        # Benchmark: Good = >75%, Average = 50-75%, Poor = <50%
        if board_independence_pct > 0.75:
            independence_score = 100
        elif board_independence_pct > 0.50:
            independence_score = 60 + (board_independence_pct - 0.50) * 160
        else:
            independence_score = max(0, board_independence_pct * 120)

        # 2. Board diversity score
        # Benchmark: Good = >30%, Average = 20-30%, Poor = <20%
        if female_board_members_pct > 0.30:
            board_diversity_score = 100
        elif female_board_members_pct > 0.20:
            board_diversity_score = 70 + (female_board_members_pct - 0.20) * 300
        else:
            board_diversity_score = max(0, female_board_members_pct * 350)

        # 3. Executive compensation score
        # Benchmark: Good = <100x, Average = 100-300x, Poor = >300x
        if ceo_pay_ratio < 100:
            exec_comp_score = 100
        elif ceo_pay_ratio < 300:
            exec_comp_score = 100 - (ceo_pay_ratio - 100) * 0.5
        else:
            exec_comp_score = max(0, 25 - (ceo_pay_ratio - 300) * 0.05)

        # 4. Shareholder rights (passed directly)
        shareholder_score = shareholder_rights_score

        # 5. Audit quality score
        audit_scores = {
            'Big4': 100,      # Deloitte, PwC, EY, KPMG
            'Top10': 75,
            'Other': 50
        }
        audit_score = audit_scores.get(audit_quality, 50)

        # Weighted total
        governance_score = (
            independence_score * 0.30 +
            board_diversity_score * 0.20 +
            exec_comp_score * 0.25 +
            shareholder_score * 0.15 +
            audit_score * 0.10
        )

        return {
            'score': governance_score,
            'independence_score': independence_score,
            'board_diversity_score': board_diversity_score,
            'exec_comp_score': exec_comp_score,
            'shareholder_score': shareholder_score,
            'audit_score': audit_score,
            'breakdown': {
                'Board Independence (30%)': independence_score,
                'Board Diversity (20%)': board_diversity_score,
                'Executive Compensation (25%)': exec_comp_score,
                'Shareholder Rights (15%)': shareholder_score,
                'Audit Quality (10%)': audit_score
            }
        }

    def calculate_esg_score(self,
                           # Environmental
                           carbon_emissions: float,
                           revenue_millions: float,
                           renewable_energy_pct: float,
                           # Social
                           employee_turnover: float,
                           gender_diversity_pct: float,
                           workplace_injuries_per_100: float,
                           training_hours_per_employee: float,
                           # Governance
                           board_independence_pct: float,
                           female_board_members_pct: float,
                           ceo_pay_ratio: float,
                           # Optional parameters
                           **kwargs) -> Dict:
        """
        Calculate comprehensive ESG score.

        Args:
            See individual score methods for parameter descriptions
            **kwargs: Optional parameters for sub-scores

        Returns:
            Complete ESG assessment with scores and risk rating

        Example:
            >>> esg_analyzer = ESGRiskAnalyzer()
            >>>
            >>> # Company A: Good ESG performance
            >>> score_good = esg_analyzer.calculate_esg_score(
            ...     carbon_emissions=10000, revenue_millions=500, renewable_energy_pct=0.80,
            ...     employee_turnover=0.08, gender_diversity_pct=0.45,
            ...     workplace_injuries_per_100=1.5, training_hours_per_employee=50,
            ...     board_independence_pct=0.75, female_board_members_pct=0.40,
            ...     ceo_pay_ratio=100
            ... )
            >>> print(f"Company A ESG Score: {score_good['total_score']:.0f}/100")
            >>> print(f"Rating: {score_good['rating']}")
        """
        print("🌍 Calculating ESG Score...")

        # Calculate component scores
        env_result = self.calculate_environmental_score(
            carbon_emissions=carbon_emissions,
            revenue_millions=revenue_millions,
            renewable_energy_pct=renewable_energy_pct,
            water_usage_intensity=kwargs.get('water_usage_intensity', 50.0),
            waste_recycling_rate=kwargs.get('waste_recycling_rate', 0.50)
        )

        social_result = self.calculate_social_score(
            employee_turnover=employee_turnover,
            gender_diversity_pct=gender_diversity_pct,
            workplace_injuries_per_100=workplace_injuries_per_100,
            training_hours_per_employee=training_hours_per_employee,
            community_investment_pct_revenue=kwargs.get('community_investment_pct_revenue', 0.01)
        )

        governance_result = self.calculate_governance_score(
            board_independence_pct=board_independence_pct,
            female_board_members_pct=female_board_members_pct,
            ceo_pay_ratio=ceo_pay_ratio,
            shareholder_rights_score=kwargs.get('shareholder_rights_score', 70.0),
            audit_quality=kwargs.get('audit_quality', 'Big4')
        )

        # Calculate weighted total
        total_score = (
            env_result['score'] * self.weights['environmental'] +
            social_result['score'] * self.weights['social'] +
            governance_result['score'] * self.weights['governance']
        )

        # Determine rating
        if total_score >= 80:
            rating = 'AAA'
            risk_level = 'Negligible'
        elif total_score >= 70:
            rating = 'AA'
            risk_level = 'Low'
        elif total_score >= 60:
            rating = 'A'
            risk_level = 'Low-Medium'
        elif total_score >= 50:
            rating = 'BBB'
            risk_level = 'Medium'
        elif total_score >= 40:
            rating = 'BB'
            risk_level = 'Medium-High'
        elif total_score >= 30:
            rating = 'B'
            risk_level = 'High'
        else:
            rating = 'CCC'
            risk_level = 'Severe'

        results = {
            'total_score': total_score,
            'rating': rating,
            'risk_level': risk_level,
            'component_scores': {
                'Environmental (35%)': env_result['score'],
                'Social (35%)': social_result['score'],
                'Governance (30%)': governance_result['score']
            },
            'environmental_details': env_result,
            'social_details': social_result,
            'governance_details': governance_result,
            'assessment_date': datetime.now().strftime('%Y-%m-%d')
        }

        print(f"\n📊 ESG Assessment Results:")
        print(f"   Total ESG Score: {total_score:.1f}/100")
        print(f"   Rating: {rating} ({risk_level} Risk)")
        print(f"   Environmental: {env_result['score']:.1f}/100")
        print(f"   Social: {social_result['score']:.1f}/100")
        print(f"   Governance: {governance_result['score']:.1f}/100")

        return results


################################################################################
# FEATURE 10: MULTI-ASSET EXPANSION
################################################################################

class MultiAssetVaR:
    """
    VaR calculation for multiple asset classes:
    - Equities (stocks)
    - Fixed Income (bonds)
    - Commodities (gold, oil, etc.)
    - Real Estate (REITs)
    - Foreign Exchange (FX)

    **Why multi-asset?**
    - Diversification reduces risk
    - Different assets react differently to market shocks
    - Correlation matters for portfolio VaR

    **Real-world usage:**
    - Pension funds hold 60% stocks, 40% bonds
    - Sovereign wealth funds diversify across all asset classes
    - Family offices use multi-asset strategies
    """

    def __init__(self):
        """
        Initialize multi-asset VaR calculator.

        Example:
            >>> ma_var = MultiAssetVaR()
            >>> portfolio = {
            ...     'equities': {'value': 500000, 'returns': equity_returns},
            ...     'bonds': {'value': 300000, 'returns': bond_returns},
            ...     'commodities': {'value': 100000, 'returns': commodity_returns}
            ... }
            >>> var_result = ma_var.calculate_portfolio_var(portfolio, confidence_level=0.95)
        """
        pass

    def calculate_bond_var(self,
                          bond_positions: List[Dict],
                          yield_changes: pd.Series,
                          confidence_level: float = 0.95) -> Dict:
        """
        Calculate VaR for bond portfolio using duration method.

        Args:
            bond_positions: List of bonds with:
                - face_value: Bond face value
                - duration: Modified duration
                - yield_current: Current yield
            yield_changes: Historical yield changes (daily)
            confidence_level: VaR confidence level

        Returns:
            Bond VaR results

        **Formula:**
        Bond Price Change ≈ -Duration × Yield Change

        VaR = Portfolio Value × Duration × VaR(Yield Changes)

        Example:
            >>> # Bond portfolio
            >>> bonds = [
            ...     {'face_value': 1000000, 'duration': 5.5, 'yield_current': 0.04},
            ...     {'face_value': 500000, 'duration': 3.2, 'yield_current': 0.035}
            ... ]
            >>>
            >>> # Historical yield changes
            >>> yield_changes = pd.Series(np.random.normal(0, 0.0002, 252))  # Daily changes
            >>>
            >>> var_result = ma_var.calculate_bond_var(bonds, yield_changes, confidence_level=0.95)
            >>> print(f"Bond VaR (95%): ${var_result['var']:,.0f}")
        """
        print("📊 Calculating Bond VaR (Duration Method)...")

        # Calculate portfolio value and weighted duration
        total_value = sum(b['face_value'] for b in bond_positions)
        weighted_duration = sum(b['face_value'] * b['duration'] for b in bond_positions) / total_value

        # Calculate yield change VaR
        yield_var = np.percentile(yield_changes, (1 - confidence_level) * 100)

        # Calculate bond VaR
        # VaR = Portfolio Value × Duration × |Yield VaR|
        bond_var = total_value * weighted_duration * abs(yield_var)

        results = {
            'var': bond_var,
            'portfolio_value': total_value,
            'weighted_duration': weighted_duration,
            'yield_var': yield_var,
            'confidence_level': confidence_level,
            'n_positions': len(bond_positions)
        }

        print(f"   Portfolio Value: ${total_value:,.0f}")
        print(f"   Weighted Duration: {weighted_duration:.2f}")
        print(f"   Yield VaR: {yield_var*10000:.1f} bps")
        print(f"   Bond VaR (95%): ${bond_var:,.0f}")

        return results

    def calculate_commodity_var(self,
                               commodity_positions: Dict[str, Dict],
                                price_returns: pd.DataFrame,
                               confidence_level: float = 0.95) -> Dict:
        """
        Calculate VaR for commodity portfolio.

        Args:
            commodity_positions: Dict with commodity: {quantity, current_price, unit}
                Example: {'Gold': {'quantity': 100, 'current_price': 1900, 'unit': 'oz'}}
            price_returns: Historical returns for each commodity
            confidence_level: VaR confidence level

        Returns:
            Commodity VaR results

        Example:
            >>> # Commodity positions
            >>> positions = {
            ...     'Gold': {'quantity': 100, 'current_price': 1900, 'unit': 'oz'},
            ...     'Oil': {'quantity': 1000, 'current_price': 80, 'unit': 'barrel'},
            ...     'Copper': {'quantity': 5000, 'current_price': 4.5, 'unit': 'lb'}
            ... }
            >>>
            >>> # Historical returns
            >>> returns = pd.DataFrame({
            ...     'Gold': np.random.normal(0.0003, 0.01, 252),
            ...     'Oil': np.random.normal(0.0005, 0.02, 252),
            ...     'Copper': np.random.normal(0.0002, 0.015, 252)
            ... })
            >>>
            >>> var_result = ma_var.calculate_commodity_var(positions, returns)
            >>> print(f"Commodity VaR: ${var_result['var']:,.0f}")
        """
        print("🥇 Calculating Commodity VaR...")

        # Calculate position values
        position_values = {}
        for commodity, pos in commodity_positions.items():
            value = pos['quantity'] * pos['current_price']
            position_values[commodity] = value

        total_value = sum(position_values.values())

        # Portfolio returns = weighted average of commodity returns
        weights = {c: v/total_value for c, v in position_values.items()}

        portfolio_returns = pd.Series(0.0, index=price_returns.index)
        for commodity in commodity_positions.keys():
            if commodity in price_returns.columns:
                portfolio_returns += price_returns[commodity] * weights[commodity]

        # Calculate VaR
        var_return = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
        commodity_var = abs(var_return * total_value)

        results = {
            'var': commodity_var,
            'portfolio_value': total_value,
            'position_values': position_values,
            'weights': weights,
            'var_return': var_return,
            'confidence_level': confidence_level
        }

        print(f"   Portfolio Value: ${total_value:,.0f}")
        print(f"   Commodity VaR (95%): ${commodity_var:,.0f}")
        for commodity, value in position_values.items():
            print(f"   - {commodity}: ${value:,.0f} ({weights[commodity]*100:.1f}%)")

        return results

    def calculate_portfolio_var(self,
                               asset_classes: Dict[str, Dict],
                               correlation_matrix: Optional[pd.DataFrame] = None,
                               confidence_level: float = 0.95) -> Dict:
        """
        Calculate VaR for multi-asset portfolio considering correlations.

        Args:
            asset_classes: Dict with asset class: {value, returns}
                Example: {
                    'equities': {'value': 500000, 'returns': pd.Series(...)},
                    'bonds': {'value': 300000, 'returns': pd.Series(...)},
                    'commodities': {'value': 100000, 'returns': pd.Series(...)}
                }
            correlation_matrix: Asset class correlations (if None, calculated from returns)
            confidence_level: VaR confidence level

        Returns:
            Multi-asset portfolio VaR

        **Formula:**
        Diversified VaR = sqrt(Σᵢ Σⱼ wᵢ wⱼ VaRᵢ VaRⱼ ρᵢⱼ)

        Where:
        - wᵢ = Weight of asset class i
        - VaRᵢ = VaR of asset class i
        - ρᵢⱼ = Correlation between asset classes i and j

        Example:
            >>> # Multi-asset portfolio
            >>> portfolio = {
            ...     'equities': {
            ...         'value': 500000,
            ...         'returns': pd.Series(np.random.normal(0.0005, 0.015, 252))
            ...     },
            ...     'bonds': {
            ...         'value': 300000,
            ...         'returns': pd.Series(np.random.normal(0.0002, 0.005, 252))
            ...     },
            ...     'commodities': {
            ...         'value': 100000,
            ...         'returns': pd.Series(np.random.normal(0.0003, 0.02, 252))
            ...     }
            ... }
            >>>
            >>> var_result = ma_var.calculate_portfolio_var(portfolio)
            >>> print(f"Diversified VaR: ${var_result['diversified_var']:,.0f}")
            >>> print(f"Undiversified VaR: ${var_result['undiversified_var']:,.0f}")
            >>> print(f"Diversification Benefit: ${var_result['diversification_benefit']:,.0f}")
        """
        print("🌐 Calculating Multi-Asset Portfolio VaR...")

        # Calculate total portfolio value
        total_value = sum(ac['value'] for ac in asset_classes.values())

        # Calculate weights
        weights = {name: ac['value']/total_value for name, ac in asset_classes.items()}

        # Calculate VaR for each asset class
        individual_vars = {}
        for name, ac in asset_classes.items():
            returns = ac['returns']
            var_return = np.percentile(returns, (1 - confidence_level) * 100)
            var_value = abs(var_return * ac['value'])
            individual_vars[name] = var_value

        # Calculate undiversified VaR (simple sum)
        undiversified_var = sum(individual_vars.values())

        # Calculate correlation matrix if not provided
        if correlation_matrix is None:
            returns_df = pd.DataFrame({
                name: ac['returns'] for name, ac in asset_classes.items()
            })
            correlation_matrix = returns_df.corr()

        # Calculate diversified VaR using correlation
        asset_names = list(asset_classes.keys())
        n_assets = len(asset_names)

        # Variance-covariance approach
        diversified_var_squared = 0
        for i, asset_i in enumerate(asset_names):
            for j, asset_j in enumerate(asset_names):
                var_i = individual_vars[asset_i]
                var_j = individual_vars[asset_j]
                corr = correlation_matrix.loc[asset_i, asset_j] if asset_i in correlation_matrix.index and asset_j in correlation_matrix.columns else 1.0
                diversified_var_squared += var_i * var_j * corr

        diversified_var = np.sqrt(max(0, diversified_var_squared))

        # Diversification benefit
        diversification_benefit = undiversified_var - diversified_var
        diversification_pct = (diversification_benefit / undiversified_var * 100) if undiversified_var > 0 else 0

        results = {
            'diversified_var': diversified_var,
            'undiversified_var': undiversified_var,
            'diversification_benefit': diversification_benefit,
            'diversification_pct': diversification_pct,
            'total_portfolio_value': total_value,
            'weights': weights,
            'individual_vars': individual_vars,
            'correlation_matrix': correlation_matrix.to_dict() if correlation_matrix is not None else None,
            'confidence_level': confidence_level
        }

        print(f"\n📊 Multi-Asset VaR Results:")
        print(f"   Portfolio Value: ${total_value:,.0f}")
        print(f"   Diversified VaR: ${diversified_var:,.0f}")
        print(f"   Undiversified VaR: ${undiversified_var:,.0f}")
        print(f"   Diversification Benefit: ${diversification_benefit:,.0f} ({diversification_pct:.1f}%)")
        print(f"\n   Asset Allocation:")
        for name, weight in weights.items():
            print(f"   - {name}: ${asset_classes[name]['value']:,.0f} ({weight*100:.1f}%) | VaR: ${individual_vars[name]:,.0f}")

        return results


################################################################################
# FEATURE 11: REGULATORY REPORTING
################################################################################

class RegulatoryReporter:
    """
    Generate regulatory reports for Basel III and FRTB (Fundamental Review of Trading Book).

    **What is Basel III?**
    - International banking regulations
    - Requires banks to hold capital against risks
    - VaR-based capital requirements

    **What is FRTB?**
    - New market risk framework (effective 2023+)
    - Expected Shortfall (ES) instead of VaR
    - Separate treatment for trading vs banking book

    **Real-world usage:**
    - All major banks must comply
    - Regulators audit these reports
    - Non-compliance = huge fines
    """

    def __init__(self):
        """
        Initialize regulatory reporter.

        Example:
            >>> reporter = RegulatoryReporter()
            >>> # Generate Basel III report
            >>> report = reporter.generate_basel_iii_report(
            ...     var_99=1000000,
            ...     stressed_var_99=1500000,
            ...     bank_tier1_capital=50000000
            ... )
        """
        # Basel III parameters
        self.basel_multiplier_min = 3.0  # Minimum multiplier
        self.basel_multiplier_max = 4.0  # Maximum multiplier

    def generate_basel_iii_report(self,
                                  var_99: float,
                                  stressed_var_99: float,
                                  bank_tier1_capital: float,
                                  backtesting_exceptions: int = 0) -> Dict:
        """
        Generate Basel III market risk capital report.

        Args:
            var_99: 99% VaR (10-day holding period)
            stressed_var_99: 99% VaR under stress (10-day)
            bank_tier1_capital: Bank's Tier 1 capital
            backtesting_exceptions: Number of VaR breaches in last year

        Returns:
            Basel III regulatory capital calculation

        **Formula:**
        Market Risk Capital = max(VaR, mc × VaR_avg) + max(SVaR, ms × SVaR_avg)

        Where:
        - mc, ms = Multipliers (3.0-4.0 based on backtesting)
        - VaR_avg = Average VaR over last 60 days
        - SVaR_avg = Average stressed VaR over last 60 days

        **Traffic Light System:**
        - Green (0-4 exceptions): Multiplier = 3.0
        - Yellow (5-9 exceptions): Multiplier = 3.4-3.85
        - Red (10+ exceptions): Multiplier = 4.0

        Example:
            >>> reporter = RegulatoryReporter()
            >>> report = reporter.generate_basel_iii_report(
            ...     var_99=1000000,
            ...     stressed_var_99=1500000,
            ...     bank_tier1_capital=50000000,
            ...     backtesting_exceptions=2
            ... )
            >>> print(f"Required Capital: ${report['market_risk_capital']:,.0f}")
            >>> print(f"Zone: {report['traffic_light_zone']}")
        """
        print("🏛️ Generating Basel III Market Risk Capital Report...")

        # Determine multiplier based on backtesting exceptions
        if backtesting_exceptions <= 4:
            zone = "Green"
            multiplier = 3.0
        elif backtesting_exceptions <= 9:
            zone = "Yellow"
            # Linear interpolation between 3.4 and 3.85
            multiplier = 3.4 + (backtesting_exceptions - 5) * 0.09
        else:
            zone = "Red"
            multiplier = 4.0

        # Calculate capital requirements
        var_capital = multiplier * var_99
        svar_capital = multiplier * stressed_var_99

        # Total market risk capital
        market_risk_capital = var_capital + svar_capital

        # Capital adequacy ratio
        capital_ratio = (bank_tier1_capital / market_risk_capital * 100) if market_risk_capital > 0 else float('inf')

        # Determine compliance
        is_compliant = bank_tier1_capital >= market_risk_capital

        results = {
            'market_risk_capital': market_risk_capital,
            'var_capital': var_capital,
            'svar_capital': svar_capital,
            'multiplier': multiplier,
            'traffic_light_zone': zone,
            'backtesting_exceptions': backtesting_exceptions,
            'bank_tier1_capital': bank_tier1_capital,
            'capital_adequacy_ratio': capital_ratio,
            'is_compliant': is_compliant,
            'shortfall': max(0, market_risk_capital - bank_tier1_capital),
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'regulation': 'Basel III Market Risk Framework'
        }

        print(f"\n📊 Basel III Report:")
        print(f"   99% VaR (10-day): ${var_99:,.0f}")
        print(f"   Stressed VaR (10-day): ${stressed_var_99:,.0f}")
        print(f"   Backtesting Zone: {zone} ({backtesting_exceptions} exceptions)")
        print(f"   Multiplier: {multiplier:.2f}x")
        print(f"   VaR Capital: ${var_capital:,.0f}")
        print(f"   Stressed VaR Capital: ${svar_capital:,.0f}")
        print(f"   Total Market Risk Capital: ${market_risk_capital:,.0f}")
        print(f"   Tier 1 Capital: ${bank_tier1_capital:,.0f}")
        print(f"   Capital Adequacy Ratio: {capital_ratio:.1f}%")
        print(f"   Compliance: {'✅ YES' if is_compliant else '❌ NO'}")

        if not is_compliant:
            print(f"   ⚠️ Capital Shortfall: ${results['shortfall']:,.0f}")

        return results

    def generate_frtb_report(self,
                            expected_shortfall: float,
                            stress_scenarios: Dict[str, float],
                            default_risk_charge: float,
                            liquidity_horizons: Dict[str, int]) -> Dict:
        """
        Generate FRTB (Fundamental Review of Trading Book) report.

        Args:
            expected_shortfall: 97.5% Expected Shortfall (ES)
            stress_scenarios: Dict of scenario name: loss amount
            default_risk_charge: DRC capital charge
            liquidity_horizons: Risk factor: liquidity horizon (days)

        Returns:
            FRTB regulatory capital calculation

        **FRTB Components:**
        1. Expected Shortfall (replaces VaR)
        2. Stress Scenario Risk Measure
        3. Default Risk Charge
        4. Residual Risk Add-On

        **Liquidity Horizons:**
        - Very liquid (equities): 10 days
        - Liquid (rates): 20 days
        - Less liquid (credit): 60 days
        - Illiquid (exotics): 120 days

        Example:
            >>> stress_scenarios = {
            ...     '2008 Financial Crisis': -2000000,
            ...     'COVID-19 March 2020': -1800000,
            ...     'Rate Shock +200bps': -1500000
            ... }
            >>>
            >>> liquidity_horizons = {
            ...     'equities': 10,
            ...     'rates': 20,
            ...     'credit': 60
            ... }
            >>>
            >>> report = reporter.generate_frtb_report(
            ...     expected_shortfall=1200000,
            ...     stress_scenarios=stress_scenarios,
            ...     default_risk_charge=500000,
            ...     liquidity_horizons=liquidity_horizons
            ... )
        """
        print("🏛️ Generating FRTB Report...")

        # 1. Expected Shortfall capital
        es_capital = expected_shortfall

        # 2. Stress Scenario Risk Measure (worst scenario)
        stress_losses = list(stress_scenarios.values())
        worst_stress_loss = abs(min(stress_losses)) if stress_losses else 0
        stress_capital = worst_stress_loss

        # 3. Default Risk Charge
        drc_capital = default_risk_charge

        # 4. Calculate liquidity-adjusted ES
        # Longer liquidity horizons require more capital
        max_horizon = max(liquidity_horizons.values()) if liquidity_horizons else 10
        liquidity_adjustment = np.sqrt(max_horizon / 10)  # Scale from 10-day base
        liquidity_adjusted_es = es_capital * liquidity_adjustment

        # 5. Total FRTB capital
        # Capital = max(ES, Stress) + DRC
        frtb_capital = max(liquidity_adjusted_es, stress_capital) + drc_capital

        # Identify worst stress scenario
        worst_scenario = min(stress_scenarios.items(), key=lambda x: x[1])[0] if stress_scenarios else "N/A"

        results = {
            'frtb_capital': frtb_capital,
            'expected_shortfall': expected_shortfall,
            'liquidity_adjusted_es': liquidity_adjusted_es,
            'stress_capital': stress_capital,
            'worst_stress_scenario': worst_scenario,
            'worst_stress_loss': worst_stress_loss,
            'default_risk_charge': drc_capital,
            'liquidity_horizons': liquidity_horizons,
            'max_liquidity_horizon': max_horizon,
            'liquidity_adjustment_factor': liquidity_adjustment,
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'regulation': 'FRTB - Fundamental Review of Trading Book'
        }

        print(f"\n📊 FRTB Report:")
        print(f"   Expected Shortfall (97.5%): ${expected_shortfall:,.0f}")
        print(f"   Liquidity Adjustment: {liquidity_adjustment:.2f}x (max horizon: {max_horizon} days)")
        print(f"   Liquidity-Adjusted ES: ${liquidity_adjusted_es:,.0f}")
        print(f"   Worst Stress Scenario: {worst_scenario}")
        print(f"   Stress Capital: ${stress_capital:,.0f}")
        print(f"   Default Risk Charge: ${drc_capital:,.0f}")
        print(f"   Total FRTB Capital: ${frtb_capital:,.0f}")

        return results

    def generate_stress_test_report(self,
                                   baseline_portfolio_value: float,
                                   scenarios: Dict[str, Dict]) -> Dict:
        """
        Generate comprehensive stress testing report.

        Args:
            baseline_portfolio_value: Current portfolio value
            scenarios: Dict with scenario: {description, shocks, expected_loss}

        Returns:
            Stress test report

        **Standard Scenarios:**
        1. 2008 Financial Crisis
        2. 1987 Black Monday
        3. COVID-19 March 2020
        4. Rate shock (+200 bps)
        5. Credit spread widening (+500 bps)

        Example:
            >>> scenarios = {
            ...     '2008 Financial Crisis': {
            ...         'description': 'Equities -50%, Credit spreads +500bps',
            ...         'equity_shock': -0.50,
            ...         'credit_shock': 0.05,
            ...         'expected_loss': -5000000
            ...     },
            ...     'COVID-19 March 2020': {
            ...         'description': 'Equities -35%, Vol spike',
            ...         'equity_shock': -0.35,
            ...         'volatility_multiplier': 3.0,
            ...         'expected_loss': -3500000
            ...     }
            ... }
            >>>
            >>> report = reporter.generate_stress_test_report(
            ...     baseline_portfolio_value=10000000,
            ...     scenarios=scenarios
            ... )
        """
        print("⚠️ Generating Stress Test Report...")

        # Analyze each scenario
        scenario_results = []

        for scenario_name, scenario_data in scenarios.items():
            expected_loss = scenario_data.get('expected_loss', 0)
            loss_pct = (expected_loss / baseline_portfolio_value * 100) if baseline_portfolio_value > 0 else 0
            post_stress_value = baseline_portfolio_value + expected_loss

            scenario_results.append({
                'scenario': scenario_name,
                'description': scenario_data.get('description', ''),
                'expected_loss': expected_loss,
                'loss_percentage': loss_pct,
                'post_stress_value': post_stress_value
            })

        # Find worst scenario
        worst_scenario = min(scenario_results, key=lambda x: x['expected_loss'])

        # Calculate stress VaR (worst loss)
        stress_var = abs(worst_scenario['expected_loss'])

        results = {
            'baseline_portfolio_value': baseline_portfolio_value,
            'scenarios': scenario_results,
            'worst_scenario': worst_scenario['scenario'],
            'worst_case_loss': worst_scenario['expected_loss'],
            'worst_case_loss_pct': worst_scenario['loss_percentage'],
            'stress_var': stress_var,
            'n_scenarios': len(scenarios),
            'report_date': datetime.now().strftime('%Y-%m-%d')
        }

        print(f"\n📊 Stress Test Results:")
        print(f"   Baseline Portfolio Value: ${baseline_portfolio_value:,.0f}")
        print(f"   Number of Scenarios: {len(scenarios)}")
        print(f"\n   Scenario Losses:")

        for sr in scenario_results:
            print(f"   - {sr['scenario']}: ${sr['expected_loss']:,.0f} ({sr['loss_percentage']:.1f}%)")

        print(f"\n   Worst Case Scenario: {worst_scenario['scenario']}")
        print(f"   Worst Case Loss: ${worst_scenario['expected_loss']:,.0f} ({worst_scenario['loss_percentage']:.1f}%)")

        return results


################################################################################
# EXAMPLE USAGE
################################################################################

if __name__ == "__main__":
    print("="*80)
    print("UNIFIED RISK PLATFORM - ADVANCED FEATURES PART 3 (9-11)")
    print("="*80)

    print("\n" + "="*80)
    print("FEATURE 9: ESG RISK SCORING")
    print("="*80)

    esg_analyzer = ESGRiskAnalyzer()

    # Example: Company with good ESG performance
    print("\n📊 Example: Tech Company with Strong ESG")
    esg_score = esg_analyzer.calculate_esg_score(
        # Environmental
        carbon_emissions=15000,
        revenue_millions=500,
        renewable_energy_pct=0.75,
        # Social
        employee_turnover=0.10,
        gender_diversity_pct=0.42,
        workplace_injuries_per_100=1.2,
        training_hours_per_employee=45,
        # Governance
        board_independence_pct=0.70,
        female_board_members_pct=0.35,
        ceo_pay_ratio=120
    )

    # Example: Company with poor ESG performance
    print("\n📊 Example: Heavy Industry with Weak ESG")
    esg_score_poor = esg_analyzer.calculate_esg_score(
        # Environmental
        carbon_emissions=200000,
        revenue_millions=400,
        renewable_energy_pct=0.10,
        # Social
        employee_turnover=0.25,
        gender_diversity_pct=0.20,
        workplace_injuries_per_100=8.5,
        training_hours_per_employee=10,
        # Governance
        board_independence_pct=0.40,
        female_board_members_pct=0.10,
        ceo_pay_ratio=450
    )

    print("\n" + "="*80)
    print("FEATURE 10: MULTI-ASSET VAR")
    print("="*80)

    ma_var = MultiAssetVaR()

    # Example 1: Bond VaR
    print("\n📊 Example 1: Bond Portfolio VaR")
    bonds = [
        {'face_value': 1000000, 'duration': 5.5, 'yield_current': 0.04},
        {'face_value': 500000, 'duration': 3.2, 'yield_current': 0.035},
        {'face_value': 750000, 'duration': 7.8, 'yield_current': 0.045}
    ]

    # Simulate historical yield changes
    np.random.seed(42)
    yield_changes = pd.Series(np.random.normal(0, 0.0002, 252))

    bond_var = ma_var.calculate_bond_var(bonds, yield_changes, confidence_level=0.95)

    # Example 2: Commodity VaR
    print("\n📊 Example 2: Commodity Portfolio VaR")
    commodity_positions = {
        'Gold': {'quantity': 100, 'current_price': 1900, 'unit': 'oz'},
        'Oil': {'quantity': 1000, 'current_price': 80, 'unit': 'barrel'},
        'Copper': {'quantity': 5000, 'current_price': 4.5, 'unit': 'lb'}
    }

    commodity_returns = pd.DataFrame({
        'Gold': np.random.normal(0.0003, 0.01, 252),
        'Oil': np.random.normal(0.0005, 0.02, 252),
        'Copper': np.random.normal(0.0002, 0.015, 252)
    })

    commodity_var = ma_var.calculate_commodity_var(commodity_positions, commodity_returns)

    # Example 3: Multi-Asset Portfolio VaR
    print("\n📊 Example 3: Multi-Asset Portfolio VaR")
    portfolio = {
        'equities': {
            'value': 500000,
            'returns': pd.Series(np.random.normal(0.0005, 0.015, 252))
        },
        'bonds': {
            'value': 300000,
            'returns': pd.Series(np.random.normal(0.0002, 0.005, 252))
        },
        'commodities': {
            'value': 100000,
            'returns': pd.Series(np.random.normal(0.0003, 0.02, 252))
        },
        'real_estate': {
            'value': 100000,
            'returns': pd.Series(np.random.normal(0.0004, 0.008, 252))
        }
    }

    ma_var_result = ma_var.calculate_portfolio_var(portfolio, confidence_level=0.95)

    print("\n" + "="*80)
    print("FEATURE 11: REGULATORY REPORTING")
    print("="*80)

    reporter = RegulatoryReporter()

    # Example 1: Basel III Report
    print("\n📊 Example 1: Basel III Market Risk Capital")
    basel_report = reporter.generate_basel_iii_report(
        var_99=1000000,
        stressed_var_99=1500000,
        bank_tier1_capital=10000000,
        backtesting_exceptions=3
    )

    # Example 2: FRTB Report
    print("\n📊 Example 2: FRTB Report")
    stress_scenarios = {
        '2008 Financial Crisis': -2000000,
        'COVID-19 March 2020': -1800000,
        'Rate Shock +200bps': -1500000,
        'Credit Spread Widening': -1200000
    }

    liquidity_horizons = {
        'equities': 10,
        'rates': 20,
        'credit': 60,
        'fx': 10
    }

    frtb_report = reporter.generate_frtb_report(
        expected_shortfall=1200000,
        stress_scenarios=stress_scenarios,
        default_risk_charge=500000,
        liquidity_horizons=liquidity_horizons
    )

    # Example 3: Stress Test Report
    print("\n📊 Example 3: Comprehensive Stress Test")
    stress_scenarios_detailed = {
        '2008 Financial Crisis': {
            'description': 'Equities -50%, Credit spreads +500bps, Vol 3x',
            'equity_shock': -0.50,
            'credit_shock': 0.05,
            'volatility_multiplier': 3.0,
            'expected_loss': -5000000
        },
        'COVID-19 March 2020': {
            'description': 'Equities -35%, Vol spike, Flight to quality',
            'equity_shock': -0.35,
            'volatility_multiplier': 2.5,
            'expected_loss': -3500000
        },
        '1987 Black Monday': {
            'description': 'Equities -20% in 1 day',
            'equity_shock': -0.20,
            'expected_loss': -2000000
        },
        'Rate Shock': {
            'description': 'Rates +200 bps',
            'rate_shock': 0.02,
            'expected_loss': -1800000
        }
    }

    stress_report = reporter.generate_stress_test_report(
        baseline_portfolio_value=10000000,
        scenarios=stress_scenarios_detailed
    )

    print("\n" + "="*80)
    print("✅ PART 3 FEATURES COMPLETE!")
    print("="*80)
    print("\nFeatures 9-11 implemented:")
    print("  ✅ Feature 9: ESG Risk Scoring")
    print("  ✅ Feature 10: Multi-Asset Expansion (Bonds, Commodities)")
    print("  ✅ Feature 11: Regulatory Reporting (Basel III, FRTB)")
    print("\nNext: Features 12-14 (Visualizations, Blockchain, Explainable AI)")
    print("="*80)
