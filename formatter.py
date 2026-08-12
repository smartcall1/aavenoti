def _hf_status(hf):
    if hf < 1.1:
        return "\U0001F6A8 위험"
    if hf < 1.5:
        return "⚠️ 주의"
    return "✅ 안전"


def _supply_block(s):
    flag = "담보 사용중" if s["collateral"] else "담보 미사용"
    return (
        f"{s['symbol']}\n"
        f" {s['balance']:,.2f}   ${s['balance_usd']:,.2f}\n"
        f" APY {s['apy']:.2f}%   {flag}"
    )


def _borrow_block(b):
    return (
        f"{b['symbol']}\n"
        f" {b['debt']:,.2f}   ${b['debt_usd']:,.2f}\n"
        f" APY {b['apy']:.2f}%"
    )


def format_dashboard(data):
    hf = data["health_factor"]
    header = [
        "\U0001F4CA *Monad Market*",
        f"\U0001F4B0 순자산 `${data['net_worth_usd']:,.2f}`",
        f"\U0001F4C8 순APY `{data['net_apy']:.2f}%`   "
        f"❤️ 건강계수 `{hf:.2f}` ({_hf_status(hf)})",
    ]

    if not data["supplies"] and not data["borrows"]:
        header.append("")
        header.append("_포지션 없음_")
        return "\n".join(header)

    table_lines = []
    if data["supplies"]:
        table_lines.append("[공급 자산]")
        table_lines.extend(_supply_block(s) for s in data["supplies"])

    if data["borrows"]:
        if table_lines:
            table_lines.append("")
        table_lines.append("[대출 자산]")
        table_lines.extend(_borrow_block(b) for b in data["borrows"])

    # Each line is kept short (<25 chars) so a fixed-width code block never
    # wraps mid-number on a narrow mobile screen.
    body = "```\n" + "\n".join(table_lines) + "\n```"
    return "\n".join(header) + "\n" + body
