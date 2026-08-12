def _supply_block(s):
    flag = "ON" if s["collateral"] else "OFF"
    return (
        f"{s['symbol']}\n"
        f" {s['balance']:,.2f}  ${s['balance_usd']:,.2f}\n"
        f" APY {s['apy']:.2f}%  collat:{flag}"
    )


def _borrow_block(b):
    return (
        f"{b['symbol']}\n"
        f" {b['debt']:,.2f}  ${b['debt_usd']:,.2f}\n"
        f" APY {b['apy']:.2f}%"
    )


def format_dashboard(data):
    header = [
        "\U0001F4CA *Monad Market*",
        f"Net worth `${data['net_worth_usd']:,.2f}`",
        f"Net APY `{data['net_apy']:.2f}%`  HF `{data['health_factor']:.2f}`",
    ]

    if not data["supplies"] and not data["borrows"]:
        header.append("")
        header.append("_포지션 없음 (no active position)_")
        return "\n".join(header)

    table_lines = []
    if data["supplies"]:
        table_lines.append("[Supplies]")
        table_lines.extend(_supply_block(s) for s in data["supplies"])

    if data["borrows"]:
        if table_lines:
            table_lines.append("")
        table_lines.append("[Borrows]")
        table_lines.extend(_borrow_block(b) for b in data["borrows"])

    # Each line is kept short (<25 chars) so a fixed-width code block never
    # wraps mid-number on a narrow mobile screen.
    body = "```\n" + "\n".join(table_lines) + "\n```"
    return "\n".join(header) + "\n" + body
