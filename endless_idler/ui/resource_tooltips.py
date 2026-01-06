from __future__ import annotations

import html


def build_tokens_tooltip(*, current: int, bonus: int, winstreak: int) -> str:
    """Generate tooltip HTML for tokens/gold display."""
    safe_current = max(0, int(current))
    safe_bonus = max(0, int(bonus))
    safe_winstreak = max(0, int(winstreak))
    
    total = safe_current + safe_winstreak
    soft_capped = total > 100
    
    return (
        "<div style='min-width: 240px;'>"
        "<table style='width: 100%; border-collapse: collapse;'>"
        "<tr><td colspan='2' style='padding: 8px 10px; border-bottom: 2px solid #FFD700;'>"
        "<b style='font-size: 13px; color: #FFD700;'>Tokens (Gold)</b>"
        "</td></tr>"
        
        "<tr><td style='padding: 6px 10px; color: rgba(255,255,255,170);'>Current:</td>"
        f"<td style='padding: 6px 10px; text-align: right; color: rgba(255,255,255,235);'><b>{safe_current}</b></td></tr>"
        
        "<tr style='background: rgba(255,255,255,0.04);'>"
        "<td style='padding: 6px 10px; color: rgba(255,255,255,170);'>Winstreak:</td>"
        f"<td style='padding: 6px 10px; text-align: right; color: rgba(255,255,255,235);'><b>{safe_winstreak}</b></td></tr>"
        
        "<tr><td style='padding: 6px 10px; color: rgba(255,255,255,170);'>Battle Bonus:</td>"
        f"<td style='padding: 6px 10px; text-align: right; color: #FFD700;'><b>+{safe_bonus}</b></td></tr>"
        
        "<tr><td colspan='2' style='padding: 10px; border-top: 1px solid rgba(255,255,255,0.1);'>"
        "<div style='color: rgba(255,255,255,180); font-size: 11px; line-height: 1.4;'>"
        "<b>Earning:</b><br/>"
        "• Win: 5 + bonus<br/>"
        "• Loss: 3 + bonus<br/>"
        "• Sell character: 1 per stack<br/><br/>"
        "<b>Spending:</b><br/>"
        "• Buy character: 1<br/>"
        "• Level up party: varies<br/>"
        "• Reroll shop: 2<br/><br/>"
        f"<b>Bonus Formula:</b><br/>"
        f"Every 5 tokens+winstreak = +1 gold<br/>"
        + (f"<span style='color: #FF3B30;'>Soft cap active (100+)</span>" if soft_capped else "")
        + "</div>"
        "</td></tr>"
        "</table>"
        "</div>"
    )


def build_party_level_tooltip(
    *, 
    level: int, 
    cost: int,
    next_cost: int | None = None,
) -> str:
    """Generate tooltip HTML for party level display."""
    safe_level = max(1, int(level))
    safe_cost = max(0, int(cost))
    
    cost_info = f"Next: {safe_cost} tokens"
    if next_cost is not None and next_cost != safe_cost:
        cost_info += f" (then {next_cost})"
    
    scaling_desc = "Characters scale with party level"
    foe_desc = "Foe level = Party Level × Fight# × 1.3"
    
    cost_formula = (
        "Levels 1-9: Cost × 4 + 2<br/>"
        "Level 10+: Cost × 1.05 (rounded up)"
    )
    
    return (
        "<div style='min-width: 260px;'>"
        "<table style='width: 100%; border-collapse: collapse;'>"
        "<tr><td colspan='2' style='padding: 8px 10px; border-bottom: 2px solid #4A9EFF;'>"
        "<b style='font-size: 13px; color: #4A9EFF;'>Party Level</b>"
        "</td></tr>"
        
        "<tr><td style='padding: 6px 10px; color: rgba(255,255,255,170);'>Current Level:</td>"
        f"<td style='padding: 6px 10px; text-align: right; color: rgba(255,255,255,235);'><b>{safe_level}</b></td></tr>"
        
        "<tr style='background: rgba(255,255,255,0.04);'>"
        "<td style='padding: 6px 10px; color: rgba(255,255,255,170);'>Upgrade Cost:</td>"
        f"<td style='padding: 6px 10px; text-align: right; color: #FFD700;'><b>{safe_cost}</b> tokens</td></tr>"
        
        "<tr><td colspan='2' style='padding: 10px; border-top: 1px solid rgba(255,255,255,0.1);'>"
        "<div style='color: rgba(255,255,255,180); font-size: 11px; line-height: 1.4;'>"
        f"<b>Effect:</b><br/>{html.escape(scaling_desc)}<br/><br/>"
        f"<b>Foe Scaling:</b><br/>{html.escape(foe_desc)}<br/><br/>"
        f"<b>Cost Growth:</b><br/>{cost_formula}"
        "</div>"
        "</td></tr>"
        "</table>"
        "</div>"
    )


def build_party_hp_tooltip(
    *,
    current: int,
    max_hp: int,
    fight_number: int,
) -> str:
    """Generate tooltip HTML for party HP display."""
    safe_current = max(0, int(current))
    safe_max = max(1, int(max_hp))
    safe_fight = max(1, int(fight_number))
    
    percentage = (safe_current / safe_max * 100) if safe_max > 0 else 0
    loss_damage = 15 * safe_fight
    
    status = "Healthy"
    status_color = "#4AFF4A"
    if percentage < 25:
        status = "Critical"
        status_color = "#FF3B30"
    elif percentage < 50:
        status = "Wounded"
        status_color = "#FF9500"
    
    return (
        "<div style='min-width: 260px;'>"
        "<table style='width: 100%; border-collapse: collapse;'>"
        "<tr><td colspan='2' style='padding: 8px 10px; border-bottom: 2px solid #FF3B30;'>"
        "<b style='font-size: 13px; color: #FF3B30;'>Party HP</b>"
        "</td></tr>"
        
        "<tr><td style='padding: 6px 10px; color: rgba(255,255,255,170);'>Current HP:</td>"
        f"<td style='padding: 6px 10px; text-align: right; color: rgba(255,255,255,235);'>"
        f"<b>{safe_current} / {safe_max}</b></td></tr>"
        
        "<tr style='background: rgba(255,255,255,0.04);'>"
        "<td style='padding: 6px 10px; color: rgba(255,255,255,170);'>Status:</td>"
        f"<td style='padding: 6px 10px; text-align: right; color: {status_color};'><b>{status}</b> ({percentage:.1f}%)</td></tr>"
        
        "<tr><td style='padding: 6px 10px; color: rgba(255,255,255,170);'>Next Loss Damage:</td>"
        f"<td style='padding: 6px 10px; text-align: right; color: #FF9500;'><b>{loss_damage}</b></td></tr>"
        
        "<tr><td colspan='2' style='padding: 10px; border-top: 1px solid rgba(255,255,255,0.1);'>"
        "<div style='color: rgba(255,255,255,180); font-size: 11px; line-height: 1.4;'>"
        "<b>Mechanics:</b><br/>"
        "• Loss: Take (15 × Fight#) damage, then heal 2<br/>"
        "• Victory: Heal 4 HP<br/>"
        "• Idle: Heal 1 HP every 15 minutes<br/>"
        "• Run ends when HP reaches 0"
        "</div>"
        "</td></tr>"
        "</table>"
        "</div>"
    )
