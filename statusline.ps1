[Console]::InputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$raw = [Console]::In.ReadToEnd()
if (-not $raw.Trim()) { exit 0 }
try { $json = $raw | ConvertFrom-Json } catch { exit 0 }

$ESC    = [char]27
$RESET  = "$ESC[0m"
$GREEN  = "$ESC[32m"
$YELLOW = "$ESC[33m"
$RED    = "$ESC[31m"
$CYAN   = "$ESC[36m"
$BOLD   = "$ESC[1m"
$DIM    = "$ESC[2m"

function ColorPct($pct) {
    if ($pct -lt 50) { return $GREEN }
    elseif ($pct -lt 80) { return $YELLOW }
    else { return $RED }
}

function MakeBar($pct, $width = 10) {
    $filled = [int][math]::Round($pct * $width / 100)
    $empty  = $width - $filled
    return ("█" * $filled) + ("░" * $empty)
}

function UnixToLocal($unix) {
    return [DateTimeOffset]::FromUnixTimeSeconds($unix).ToLocalTime().ToString("HH:mm")
}

$model   = if ($json.model.display_name) { $json.model.display_name } else { "Claude" }

$ctxPct  = if ($null -ne $json.context_window.used_percentage) { [int][math]::Round([double]$json.context_window.used_percentage) } else { 0 }
$ctxCol  = ColorPct $ctxPct
$ctxBar  = MakeBar $ctxPct

$rl5h    = $json.rate_limits.five_hour
$s_pct   = if ($null -ne $rl5h.used_percentage) { [int][math]::Round([double]$rl5h.used_percentage) } else { $null }

$rl7d    = $json.rate_limits.seven_day
$w_pct   = if ($null -ne $rl7d.used_percentage) { [int][math]::Round([double]$rl7d.used_percentage) } else { $null }

$cost    = if ($null -ne $json.cost.total_cost_usd) { "`$$([math]::Round([double]$json.cost.total_cost_usd, 4))" } else { $null }

$line  = "${BOLD}${CYAN} $model ${RESET}"
$line += "  ${DIM}|${RESET}  "
$line += "${ctxCol}Ctx ${ctxBar} ${ctxPct}%${RESET}"

if ($null -ne $s_pct) {
    $uCol = ColorPct $s_pct
    $uBar = MakeBar $s_pct
    $resetTime = if ($rl5h.resets_at) { UnixToLocal $rl5h.resets_at } else { "" }
    $line += "  ${DIM}|${RESET}  "
    $line += "${uCol}5h ${uBar} ${s_pct}%${RESET}"
    if ($resetTime) { $line += " ${DIM}→ $resetTime${RESET}" }
}

if ($null -ne $w_pct) {
    $wCol = ColorPct $w_pct
    $wBar = MakeBar $w_pct
    $line += "  ${DIM}|${RESET}  "
    $line += "${wCol}7d ${wBar} ${w_pct}%${RESET}"
}

if ($cost) {
    $line += "  ${DIM}| $cost${RESET}"
}

Write-Host $line
