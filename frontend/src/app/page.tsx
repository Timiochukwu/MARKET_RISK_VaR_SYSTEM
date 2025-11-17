'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import {
  Activity,
  BarChart3,
  TrendingUp,
  Shield,
  Zap,
  Globe,
  Lock,
  Smartphone,
  ArrowRight,
  CheckCircle2,
  LineChart,
  PieChart,
  Brain,
  Sparkles,
  ChevronRight,
  Play,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export default function Home() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) return null

  return (
    <div className="flex min-h-screen flex-col">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-info">
              <Activity className="h-6 w-6 text-white" />
            </div>
            <span className="text-xl font-bold gradient-text">RiskPro</span>
          </div>

          <div className="hidden md:flex items-center gap-8">
            <Link href="#features" className="text-sm font-medium hover:text-primary transition-colors">
              Features
            </Link>
            <Link href="#solutions" className="text-sm font-medium hover:text-primary transition-colors">
              Solutions
            </Link>
            <Link href="#pricing" className="text-sm font-medium hover:text-primary transition-colors">
              Pricing
            </Link>
            <Link href="#about" className="text-sm font-medium hover:text-primary transition-colors">
              About
            </Link>
          </div>

          <div className="flex items-center gap-4">
            <Button variant="ghost" asChild className="hidden sm:inline-flex">
              <Link href="/login">Sign In</Link>
            </Button>
            <Button asChild>
              <Link href="/dashboard">Get Started</Link>
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden border-b">
        {/* Background gradient */}
        <div className="absolute inset-0 -z-10 bg-gradient-to-br from-primary/5 via-background to-info/5" />
        <div className="absolute inset-0 -z-10 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))] dark:bg-grid-slate-700/25" />

        <div className="container mx-auto px-4 py-20 sm:py-32">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mx-auto max-w-4xl text-center"
          >
            <Badge className="mb-4 bg-primary/10 text-primary hover:bg-primary/20">
              <Sparkles className="mr-1 h-3 w-3" />
              Institutional-Grade Analytics
            </Badge>

            <h1 className="mb-6 text-4xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
              Professional Risk Management
              <span className="gradient-text"> Platform</span>
            </h1>

            <p className="mb-8 text-xl text-muted-foreground sm:text-2xl max-w-2xl mx-auto">
              Real-time VaR analysis, portfolio optimization, and DeFi analytics.
              Built for institutional traders and quantitative analysts.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button size="lg" asChild className="min-w-[200px]">
                <Link href="/dashboard">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="min-w-[200px]">
                <Play className="mr-2 h-4 w-4" />
                Watch Demo
              </Button>
            </div>

            <div className="mt-12 flex flex-wrap justify-center gap-8 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-profit" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-profit" />
                <span>14-day free trial</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-profit" />
                <span>Cancel anytime</span>
              </div>
            </div>
          </motion.div>

          {/* Dashboard Preview */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="mx-auto mt-20 max-w-6xl"
          >
            <div className="relative rounded-xl border bg-card shadow-2xl">
              <div className="flex items-center gap-2 border-b p-4">
                <div className="h-3 w-3 rounded-full bg-red-500" />
                <div className="h-3 w-3 rounded-full bg-yellow-500" />
                <div className="h-3 w-3 rounded-full bg-profit" />
              </div>
              <div className="p-8 bg-gradient-to-br from-primary/5 to-info/5">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-background rounded-lg p-4 shadow-sm">
                    <div className="text-sm text-muted-foreground">Portfolio Value</div>
                    <div className="text-2xl font-bold financial-number">$2,547,891</div>
                    <div className="text-sm text-profit flex items-center">
                      <TrendingUp className="h-4 w-4 mr-1" />
                      +12.4% (24h)
                    </div>
                  </div>
                  <div className="bg-background rounded-lg p-4 shadow-sm">
                    <div className="text-sm text-muted-foreground">VaR (95%)</div>
                    <div className="text-2xl font-bold financial-number">$48,250</div>
                    <div className="text-sm text-muted-foreground">1-day horizon</div>
                  </div>
                  <div className="bg-background rounded-lg p-4 shadow-sm">
                    <div className="text-sm text-muted-foreground">Sharpe Ratio</div>
                    <div className="text-2xl font-bold financial-number">2.43</div>
                    <div className="text-sm text-profit">Excellent</div>
                  </div>
                </div>
                <div className="bg-background rounded-lg p-4 shadow-sm h-[200px] flex items-center justify-center">
                  <LineChart className="h-16 w-16 text-muted-foreground/20" />
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 border-b">
        <div className="container">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { number: '10K+', label: 'Active Users', icon: Activity },
              { number: '$500B+', label: 'Assets Analyzed', icon: BarChart3 },
              { number: '99.9%', label: 'Uptime', icon: Shield },
              { number: '<100ms', label: 'Response Time', icon: Zap },
            ].map((stat, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: idx * 0.1 }}
                className="text-center"
              >
                <stat.icon className="mx-auto mb-4 h-8 w-8 text-primary" />
                <div className="text-3xl font-bold financial-number">{stat.number}</div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 lg:py-32">
        <div className="container">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <Badge className="mb-4">Features</Badge>
            <h2 className="text-3xl font-bold sm:text-4xl mb-4">
              Everything you need for
              <span className="gradient-text"> risk management</span>
            </h2>
            <p className="text-lg text-muted-foreground">
              Professional tools used by hedge funds, banks, and trading desks worldwide
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: LineChart,
                title: 'Market Risk VaR',
                description: '6 VaR calculation methods with GARCH & ARIMA models. Real-time risk monitoring.',
                features: ['Historical VaR', 'Monte Carlo', 'GARCH Models', 'Backtesting'],
              },
              {
                icon: Globe,
                title: 'DeFi Analytics',
                description: 'Comprehensive DeFi protocol analysis with smart contract risk assessment.',
                features: ['Yield Optimization', 'Impermanent Loss', 'Liquidity Analysis', 'Protocol Risk'],
              },
              {
                icon: Brain,
                title: 'ML Models',
                description: 'Transformer VaR, RL trading agents, sentiment analysis, and credit risk.',
                features: ['Deep Learning', 'Reinforcement Learning', 'Sentiment Analysis', 'Explainable AI'],
              },
              {
                icon: PieChart,
                title: 'Portfolio Optimization',
                description: 'Advanced portfolio construction with multi-asset class support.',
                features: ['Mean-Variance', 'Risk Parity', 'Black-Litterman', 'Factor Models'],
              },
              {
                icon: Shield,
                title: 'Regulatory Compliance',
                description: 'Basel III, FRTB, and stress testing reports for regulatory submissions.',
                features: ['Basel III', 'FRTB', 'Stress Testing', 'Audit Trails'],
              },
              {
                icon: Smartphone,
                title: 'Mobile Responsive',
                description: 'Full-featured mobile app with real-time alerts and notifications.',
                features: ['iOS & Android', 'Push Alerts', 'Biometric Auth', 'Offline Mode'],
              },
            ].map((feature, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: idx * 0.1 }}
              >
                <Card className="p-6 h-full hover:shadow-lg transition-all duration-300 hover:-translate-y-1 cursor-pointer group">
                  <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground mb-4">{feature.description}</p>
                  <ul className="space-y-2">
                    {feature.features.map((item, i) => (
                      <li key={i} className="flex items-center text-sm">
                        <CheckCircle2 className="mr-2 h-4 w-4 text-profit" />
                        {item}
                      </li>
                    ))}
                  </ul>
                  <Button variant="ghost" className="mt-4 w-full group-hover:bg-primary/10">
                    Learn more
                    <ChevronRight className="ml-2 h-4 w-4" />
                  </Button>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Solutions Section */}
      <section id="solutions" className="py-20 lg:py-32 bg-muted/30">
        <div className="container">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <Badge className="mb-4">Solutions</Badge>
            <h2 className="text-3xl font-bold sm:text-4xl mb-4">
              Built for<span className="gradient-text"> every role</span>
            </h2>
            <p className="text-lg text-muted-foreground">
              Tailored solutions for different financial professionals
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {[
              {
                title: 'Hedge Funds',
                description: 'Advanced portfolio analytics, ML models, and options trading tools',
                link: '/solutions/hedge-funds',
              },
              {
                title: 'Banks',
                description: 'Regulatory compliance, credit risk, and Basel III reporting',
                link: '/solutions/banks',
              },
              {
                title: 'Trading Desks',
                description: 'Real-time VaR, live trading integration, and risk limits',
                link: '/solutions/trading',
              },
            ].map((solution, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: idx * 0.1 }}
              >
                <Card className="p-8 h-full hover:shadow-lg transition-all duration-300 cursor-pointer group">
                  <h3 className="text-2xl font-bold mb-4">{solution.title}</h3>
                  <p className="text-muted-foreground mb-6">{solution.description}</p>
                  <Link
                    href={solution.link}
                    className="inline-flex items-center text-primary font-medium group-hover:gap-2 transition-all"
                  >
                    Explore solution
                    <ArrowRight className="ml-1 h-4 w-4" />
                  </Link>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 lg:py-32">
        <div className="container">
          <div className="mx-auto max-w-4xl">
            <Card className="p-8 lg:p-12 bg-gradient-to-br from-primary/10 via-background to-info/10 border-2">
              <div className="text-center">
                <h2 className="text-3xl font-bold sm:text-4xl mb-4">
                  Ready to transform your risk management?
                </h2>
                <p className="text-lg text-muted-foreground mb-8">
                  Join thousands of professionals using RiskPro for institutional-grade analytics
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Button size="lg" asChild className="min-w-[200px]">
                    <Link href="/dashboard">
                      Start Free Trial
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                  <Button size="lg" variant="outline" asChild className="min-w-[200px]">
                    <Link href="/contact">
                      Contact Sales
                    </Link>
                  </Button>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12">
        <div className="container">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="#" className="hover:text-foreground">Features</Link></li>
                <li><Link href="#" className="hover:text-foreground">Pricing</Link></li>
                <li><Link href="#" className="hover:text-foreground">Security</Link></li>
                <li><Link href="#" className="hover:text-foreground">Roadmap</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="#" className="hover:text-foreground">About</Link></li>
                <li><Link href="#" className="hover:text-foreground">Blog</Link></li>
                <li><Link href="#" className="hover:text-foreground">Careers</Link></li>
                <li><Link href="#" className="hover:text-foreground">Contact</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Resources</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="#" className="hover:text-foreground">Documentation</Link></li>
                <li><Link href="#" className="hover:text-foreground">API Reference</Link></li>
                <li><Link href="#" className="hover:text-foreground">Guides</Link></li>
                <li><Link href="#" className="hover:text-foreground">Support</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="#" className="hover:text-foreground">Privacy</Link></li>
                <li><Link href="#" className="hover:text-foreground">Terms</Link></li>
                <li><Link href="#" className="hover:text-foreground">License</Link></li>
                <li><Link href="#" className="hover:text-foreground">Compliance</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t pt-8 flex flex-col sm:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary" />
              <span className="font-semibold">RiskPro</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © 2024 RiskPro. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
