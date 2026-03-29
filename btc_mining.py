#!/usr/bin/env python3
"""
Bitcoin Mining Calculator
比特币挖矿成本计算器

Usage:
    python3 btc_mining.py                    # 使用默认参数
    python3 btc_mining.py --price 85000      # 指定BTC价格
    python3 btc_mining.py --electricity 0.35 --machine S19XP  # 指定电价和矿机
    python3 btc_mining.py --interactive     # 交互模式

Author: Arrui.c@gmail.com
Version: 3.0
"""

import argparse
import json
import sys
from datetime import datetime

# ===== 默认配置 =====
DEFAULT_BTC_PRICE_USD = 66852
USD_TO_CNY = 7.2

# 2026年3月 网络参数
NETWORK_HASHRAE_TH = 750_000_000  # 750 EH/s
DAILY_BTC_REWARD = 450  # 每日产出

# 矿机参数
MINERS = {
    "S19KPro": {"hashrate": 110, "power": 3250, "price": 8500, "name": "蚂蚁 S19k Pro"},
    "S19XP": {"hashrate": 140, "power": 3250, "price": 9500, "name": "蚂蚁 S19 XP"},
    "S21XP": {"hashrate": 134, "power": 5300, "price": 12000, "name": "蚂蚁 S21 XP"},
    "S21Pro": {"hashrate": 234, "power": 7150, "price": 18000, "name": "蚂蚁 S21 Pro"},
}

# 电价选项
ELECTRICITY_PRICES = {
    "low": 0.35,    # 低谷电
    "mid": 0.55,    # 平价电
    "high": 0.75,   # 商业电
}


def get_btc_price():
    """获取BTC价格 - 优先API，失败则用默认值"""
    try:
        import urllib.request
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read())
            return float(data["price"])
    except Exception as e:
        print(f"⚠️ 获取API价格失败，使用默认值: {e}")
        return DEFAULT_BTC_PRICE_USD


def calculate_mining(btc_price_usd, miner_key, electricity_price, hashrate_th=10000):
    """计算挖矿收益"""
    btc_price_cny = btc_price_usd * USD_TO_CNY

    # 每 TH/s 每日收益
    daily_btc_per_th = DAILY_BTC_REWARD / NETWORK_HASHRAE_TH

    # 目标算力每日收益
    daily_btc = hashrate_th * daily_btc_per_th
    daily_revenue_cny = daily_btc * btc_price_cny
    daily_revenue_usd = daily_btc * btc_price_usd

    # 电费计算 (10000 TH/s 对应功率)
    # 经验值: 每 TH/s 约 0.025 kW
    power_per_th = 0.025  # kW/TH
    daily_power_kwh = hashrate_th * power_per_th * 24
    daily_electricity = daily_power_kwh * electricity_price

    # 净利润
    daily_profit = daily_revenue_cny - daily_electricity

    # 盈亏平衡 BTC 价格
    breakeven_btc_price = daily_electricity / daily_btc

    return {
        "daily_btc": daily_btc,
        "daily_revenue_cny": daily_revenue_cny,
        "daily_revenue_usd": daily_revenue_usd,
        "daily_electricity": daily_electricity,
        "daily_profit": daily_profit,
        "breakeven_btc_price": breakeven_btc_price,
        "breakeven_btc_usd": breakeven_btc_price / USD_TO_CNY,
    }


def print_analysis(btc_price_usd=None, miner_key=None, electricity_price=None):
    """打印完整分析报告"""

    if btc_price_usd is None:
        btc_price_usd = get_btc_price()

    btc_price_cny = btc_price_usd * USD_TO_CNY

    print("=" * 60)
    print("📊 比特币挖矿成本分析")
    print(f"   更新于: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print(f"\n【市场数据】")
    print(f"BTC价格: ${btc_price_usd:,} ≈ ¥{btc_price_cny:,.0f}")
    print(f"全网算力: {NETWORK_HASHRAE_TH/1e9:.1f} ZH/s")
    print(f"每日产出: {DAILY_BTC_REWARD} BTC")

    # 每 TH/s 收益
    daily_btc_per_th = DAILY_BTC_REWARD / NETWORK_HASHRAE_TH
    print(f"每 TH/s 每日收益: {daily_btc_per_th:.8f} BTC")

    # 电价分析
    print(f"\n{'='*60}")
    print(f"⛏️ 盈亏平衡分析 (10,000 TH/s 算力)")
    print(f"{'='*60}")

    for elec_name, elec_price in ELECTRICITY_PRICES.items():
        result = calculate_mining(btc_price_usd, None, elec_price)
        elec_label = {"low": "低谷电", "mid": "平价电", "high": "商业电"}[elec_name]

        status = "✅ 盈利" if result["daily_profit"] > 0 else "❌ 亏损"
        print(f"\n{elec_label} ¥{elec_price}/kWh:")
        print(f"   每日电费: ¥{result['daily_electricity']:,.0f}")
        print(f"   每日收入: ¥{result['daily_revenue_cny']:,.0f}")
        print(f"   每日利润: ¥{result['daily_profit']:+,.0f} {status}")
        print(f"   BTC保底价: ¥{result['breakeven_btc_price']:,.0f} (${result['breakeven_btc_usd']:,.0f})")

    # 矿机对比
    print(f"\n{'='*60}")
    print(f"🔧 主流矿机对比 (电价 ¥{ELECTRICITY_PRICES['mid']}/kWh)")
    print(f"{'='*60}")

    for key, miner in MINERS.items():
        result = calculate_mining(btc_price_usd, key, ELECTRICITY_PRICES["mid"], miner["hashrate"])

        status = "✅" if result["daily_profit"] > 0 else "❌"
        print(f"\n{status} {miner['name']}")
        print(f"   算力: {miner['hashrate']} TH/s | 功率: {miner['power']}W | 价格: ¥{miner['price']:,}")
        print(f"   日产出: {result['daily_btc']:.6f} BTC ≈ ¥{result['daily_revenue_cny']:,.0f}")
        print(f"   日电费: ¥{result['daily_electricity']:,.0f} | 利润: ¥{result['daily_profit']:+,.0f}")

        if result["daily_profit"] > 0:
            days = miner["price"] / result["daily_profit"]
            print(f"   回本周期: {days:.0f} 天 ({days/365:.1f} 年)")
        else:
            print(f"   状态: 亏损中")

    # 结论
    print(f"\n{'='*60}")
    print(f"💡 结论")
    print(f"{'='*60}")
    print(f"当前BTC价格: ${btc_price_usd:,}")
    print(f"盈亏平衡电价: ${result['breakeven_btc_usd']:,.0f}")
    print(f"在 ¥0.55/kWh 电价下 {'盈利' if result['daily_profit'] > 0 else '亏损'}")
    print(f"\n⚠️ 风险提示: 币价波动大，回本周期长，请谨慎投资")


def interactive_mode():
    """交互模式"""
    print("\n🎯 交互式挖矿计算器")
    print("=" * 40)

    # BTC 价格
    btc_input = input("BTC价格 (USD) [默认 66852]: ").strip()
    btc_price = float(btc_input) if btc_input else get_btc_price()

    # 选择矿机
    print("\n可选矿机:")
    for i, (key, miner) in enumerate(MINERS.items(), 1):
        print(f"  {i}. {miner['name']} ({miner['hashrate']}T / ¥{miner['price']:,})")

    miner_choice = input("选择矿机 [默认 2 S19XP]: ").strip()
    miner_keys = list(MINERS.keys())
    miner_key = miner_keys[int(miner_choice) - 1] if miner_choice.isdigit() else "S19XP"

    # 选择电价
    print("\n电价选项: 1. 低谷 ¥0.35  2. 平价 ¥0.55  3. 商业 ¥0.75")
    elec_choice = input("选择电价 [默认 2]: ").strip()
    elec_prices = [0.35, 0.55, 0.75]
    electricity_price = elec_prices[int(elec_choice) - 1] if elec_choice.isdigit() else 0.55

    # 计算
    miner = MINERS[miner_key]
    result = calculate_mining(btc_price, miner_key, electricity_price, miner["hashrate"])

    print(f"\n{'='*40}")
    print(f"📊 计算结果: {miner['name']}")
    print(f"{'='*40}")
    print(f"算力: {miner['hashrate']} TH/s")
    print(f"功率: {miner['power']}W")
    print(f"电价: ¥{electricity_price}/kWh")
    print(f"每日产出: {result['daily_btc']:.6f} BTC")
    print(f"每日收入: ¥{result['daily_revenue_cny']:,.0f}")
    print(f"每日电费: ¥{result['daily_electricity']:,.0f}")
    print(f"每日利润: ¥{result['daily_profit']:+,.0f}")

    if result["daily_profit"] > 0:
        days = miner["price"] / result["daily_profit"]
        print(f"回本周期: {days:.0f} 天 ({days/365:.1f} 年)")
    else:
        print(f"状态: 亏损中 - 需要 ¥{abs(result['daily_profit']):,.0f}/天才能盈亏平衡")


def main():
    parser = argparse.ArgumentParser(description="比特币挖矿计算器")
    parser.add_argument("--price", type=float, help="BTC价格 (USD)")
    parser.add_argument("--electricity", type=float, help="电价 (CNY/kWh)")
    parser.add_argument("--machine", type=str, help="矿机型号 (S19KPro/S19XP/S21XP/S21Pro)")
    parser.add_argument("--hashrate", type=float, default=10000, help="算力 TH/s")
    parser.add_argument("--interactive", action="store_true", help="交互模式")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    else:
        btc_price = args.price
        elec_price = args.electricity if args.electricity else None

        print_analysis(btc_price, args.machine, elec_price)


if __name__ == "__main__":
    main()