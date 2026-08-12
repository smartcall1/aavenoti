def _hf_status(hf):
    if hf < 1.1:
        return "\U0001F6A8 Danger"
    if hf < 1.5:
        return "⚠️ Caution"
    return "✅ Safe"


def _net_worth_delta_str(delta):
    if delta is None:
        return ""
    sign = "+" if delta >= 0 else "-"
    return f" ({sign}${abs(delta):,.2f})"


def _supply_lines(s):
    flag = "ON" if s["collateral"] else "OFF"
    return [
        f"{s['symbol']}  {s['balance']:,.2f}  (${s['balance_usd']:,.2f})",
        f"  APY {s['apy']:.2f}%  (Collateral {flag})",
    ]


def _borrow_lines(b):
    return [
        f"{b['symbol']}  {b['debt']:,.2f}  (${b['debt_usd']:,.2f})",
        f"  APY {b['apy']:.2f}%",
    ]


def format_dashboard(data, net_worth_delta=None):
    hf = data["health_factor"]
    lines = [
        "\U0001F4CA Monad Market",
        "",
        "*[SUMMARY]*",
        f"\U0001F4C8 Net APY {data['net_apy']:.2f}%",
        f"\U0001F4B0 Net worth ${data['net_worth_usd']:,.2f}"
        f"{_net_worth_delta_str(net_worth_delta)}",
        f"❤️ HF {hf:.2f} ({_hf_status(hf)})",
    ]

    if not data["supplies"] and not data["borrows"]:
        lines.append("")
        lines.append("No active position")
        return "\n".join(lines)

    if data["supplies"]:
        lines.append("")
        lines.append("*[\U0001F7E2 Supplies]*")
        for s in data["supplies"]:
            lines.extend(_supply_lines(s))

    if data["borrows"]:
        lines.append("")
        lines.append("*[\U0001F534 Borrows]*")
        for b in data["borrows"]:
            lines.extend(_borrow_lines(b))

    return "\n".join(lines)
