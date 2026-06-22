import fitz  # pymupdf
import os

SRC_DIR = r"C:\Users\chaiy\OneDrive\Desktop\Charging_CSC"
OUT_DIR = r"C:\Users\chaiy\OneDrive\Desktop\Charging_CSC_Markdown"

# Markdown content keyed by PDF filename (stem)
MARKDOWN_CONTENT = {

"Double_Charges_Problem": """\
# Double Charges Problem

**Case Reference:** CSC 266897857

## Problem

The customer disputed what appeared to be a double charge for an add-on subscription,
claiming the item was purchased only once but billed twice.

## Investigation

Order Entry was reviewed. Both orders were placed by the customer through the MyUMobile App.

![Account Receivable Billing Detail](images/page_1.png)

Both customer orders are listed below, each showing a separate Modify Offer action initiated
by the customer via the self-service channel:

![Order 1 — Customer Order 2503001083703090](images/page_2.png)

![Order 2 — Customer Order 2503001081979992](images/page_3.png)

## Confirmation

Both transactions were initiated by the customer through the self-service channel
(MyUMobile App). The `Accept Channel` field in both orders confirms this.

## Reply

As investigated, both orders were created via the MyUMobile App, confirming that the
purchases were self-initiated by the customer. The system did not generate any duplicate
charge — both charges are valid and there is no system-side duplication.
""",

"Fail_To_MTCall": """\
# MT Call Failure Investigation

**Case Reference:** CSC 282365093

## Problem

An inbound MT (Mobile Terminated) call to **60139829293** failed to connect.

## Investigation Steps

### Step 1 — Single-MSISDN Tracing

Single-MSISDN tracing was performed on the called number.

![Whale Cloud — Single-MSISDN Trace](images/page_1.png)

### Step 2 — CCR/CCA Log Review

The trace returned **Response Code 2001 (Success)**, confirming that the rating layer
successfully accepted the call leg at the OCS side.

![CCR/CCA Log — Result-Code 2001](images/page_2.png)

### Step 3 — charging_rest API Log Analysis

The `charging_rest` API logs under `data/api_log/charging_rest/` were reviewed for the
same date using the following commands:

```bash
grep 27766704 charging_rest* | grep query_credit_limit     # 27766704 = ACCT_ID
grep -A 1 27766704 charging_rest* | grep query_credit_limit
```

![charging_rest API Log — query_credit_limit result](images/page_3.png)

## Finding

The `query_credit_limit` response shows that the account's remaining credit on the call date
was only **RM 3.60**, which was insufficient to authorise the call.

## Root Cause

The MT call failed because the account balance (RM 3.60) was below the minimum required
to authorise the call. This is the confirmed root cause of the call connection failure.
""",

"Free_Incoming_Calls": """\
# Free Incoming Calls — Roaming MTC Investigation

**Case Reference:** CSC 302898967

## Conclusion

All charges have been verified as valid.

## Findings

### Finding 1 — Applied Price Plan

The customer was charged under the **Roaming Price Plan** (Price Plan ID: 10200),
**not** under Postpaid 5G Roaming MTC. This is confirmed by CDR field `919 = 10200`.

![CDR EXT_ATTR showing 919=10200 and PRICE_PLAN table](images/page_2.png)

### Finding 2 — Free MTC Condition

Under the Postpaid 5G Roaming MTC plan, incoming roaming calls are free **only** when
the **Called VLR Number** falls within the configured MTC CC zone.

![Postpaid 5G Roaming MTC price plan — MTC CC condition](images/page_3.png)

### Finding 3 — Called VLR Number Not in MTC CC Zone

The CDR shows `Called VLR Number = 998`. A configuration check confirms that **998 is
NOT defined** in the MTC CC zone — the zone table shows no matching entry.

![MTC CC zone configuration — 998 not present](images/page_4.png)

![Zone configuration — MTC CC empty for value 998](images/page_5.png)

## Root Cause

Because the Called VLR Number (998) does not satisfy the MTC CC condition, the call did
not qualify for free incoming roaming. The system correctly fell back to the standard
Roaming Price Plan and applied the applicable charge.

## Conclusion

The charges are rated correctly by the system. No waiver is applicable.
""",

"GX38_AUTO-RENEWAL_CONFLICT": """\
# GX38 Auto-Renewal Conflict — PAYU Charges Investigation

**Case Reference:** CSC 267791640

## Customer Problem

- **Issue 1:** Customer purchased GX38 at `2025-03-21 00:38:37`, but the plan was set to
  Inactive at `2025-03-21 00:38:38` and PAYU was subsequently charged.
- **Issue 2:** Customer purchased GX38 again at `2025-03-21 09:26:47` on the same day and
  was still charged PAYU.

![Customer 360 — Order history showing all three transactions](images/page_1.png)

---

## Issue 1 — Investigation

### Step 1

Searched `api_log/RecurrRefund` using the Order Number — **no matching record found**.

> **Note:** RecurrRefund logs cover plan rental top-up, refund, and renewal interface activity.

![RecurrRefund search result — no record for this order](images/page_2.png)

### Root Cause (Issue 1)

GX38 became Inactive because the system was scheduled to auto-renew the plan at the same
moment the customer also manually subscribed. When the auto-renewal job ran, it detected
**insufficient balance** and set the existing plan to Inactive. Subsequent data usage was
therefore rated under PAYU.

---

## Issue 2 — Investigation

![Charging Detail — data session at 09:26:04 before GX38 at 09:26:47](images/page_3.png)

### Root Cause (Issue 2)

The customer started using data at `2025-03-21 09:26:04`, while the second GX38 purchase
was only completed at `2025-03-21 09:26:47` — a difference of **43 seconds**. Because data
usage began before the plan was activated, the initial usage was correctly rated under PAYU.

---

## Summary

| Issue | Root Cause | Charge Valid? |
|-------|-----------|---------------|
| Issue 1 | Auto-renewal ran simultaneously with manual purchase; insufficient balance caused plan to go Inactive | Yes |
| Issue 2 | Data session started 43 seconds before GX38 provisioning completed | Yes |
""",

"Incoming_Call": """\
# International Roaming Incoming Call Charges

**Case Reference:** CSC 302376377

## Explanation

Hi Team,

Upon investigation, this is **not a charging system issue**. The charging detail records show
two International Roaming Incoming (Roaming MT) voice events:

| # | Date & Time | Calling Number |
|---|-------------|----------------|
| 1 | 28/11/2025 at 17:16:21 | 0162992345 |
| 2 | 25/11/2025 at 14:25:41 | 0362580234 |

Each event has a valid call start time, end time, and duration. The presence of all three
values confirms that the calls were successfully delivered and terminated to the subscriber
while roaming.

Under international roaming, **charging for an incoming voice call is triggered as soon as
the call is successfully routed to the customer's number** — regardless of whether the
customer answers.

## Conclusion

The charges are valid and are not caused by any network or charging-system issue.

## Customer Advisory

To avoid international roaming incoming call charges in future, the customer should
**disable the Voice service (and SMS) before travelling overseas** if they do not intend to
receive roaming voice calls.
""",

"Roaming_Unable_Use": """\
# Roaming Add-On Unable to Use — IR Service Not Activated

**Case Reference:** CSC 275055036

## Finding

The customer purchased the **30-Day Roaming (Multi-Country)** plan twice on 2025-04-03
— first at `08:20:27` and again at `19:18:33`. However, the **Full International Roaming (IR)**
service was only activated on **2025-04-11 at 18:42:24**.

![Charging detail and Order Entry — IR activation date 2025-04-11](images/page_1.png)

## Root Cause

The customer did **not** have active IR service at the time the roaming plans were purchased.
Without IR enabled at the network layer, the roaming plan cannot be used — even if the
plan itself exists on the account.

The blocker was the **missing IR service entitlement**, not the roaming plan itself.

## Customer Advisory

Always ensure that the **International Roaming (IR) service is enabled on the line BEFORE
purchasing any roaming plan**. If IR is not active, the plan will be provisioned but data
roaming will remain blocked until IR is switched on.
""",

"Minimum_Payment_CL_Change_Lead_BAR": """\
# Minimum Payment Credit Limit — Discrepancy Explanation

## Billing Cycle Summary

**Billing Cycle: 2025-05-21 to 2025-06-20**

| Charge Item | Amount |
|-------------|--------|
| Plan charge | RM 98.00 |
| Other charge | RM 5.00 |
| Usage / additional charges | RM 53.79 |

![Bill Detail — Billing Cycle 2025-05-21 to 2025-06-20](images/page_1.png)

**Billing Cycle: 2025-06-21 to 2025-07-20 (Advance)**

| Charge Item | Amount |
|-------------|--------|
| Plan charge (advance) | RM 98.00 |

![Bill Detail — Advance billing cycle 2025-06-21 to 2025-07-20](images/page_2.png)

**Total (excluding tax) = RM 254.79**

---

## Explanation

At **00:00 on 2025-06-21**, the SMS notifying the customer of the Minimum Payment
Credit Limit (CL) amount was sent using the **Consumed Credit Limit without tax
(RM 6.18)**, because the daily bill run had not yet executed at that point. The minimum
payment required to lift the Credit Limit bar was therefore calculated as **RM 254.79**.

After the bill run completed in the morning, tax (RM 6.18) was applied to the cycle,
increasing the total payable amount accordingly.

## Conclusion

The discrepancy between the SMS amount and the post-bill-run amount is caused by a
**timing difference**:

- The midnight SMS used the pre-tax figure (RM 254.79).
- The post-bill-run figure correctly includes tax (RM 254.79 + RM 6.18).

Both values are accurate for the moment they were calculated. This is the reason for the
apparent change in the Minimum Payment CL amount.
""",

"Overseas_Careline": """\
# Overseas Careline Call — Charged Instead of Free

**Case Reference:** ISR-50129

## Problem

Please investigate the configuration for the **Overseas Careline Call** number
`60183886688`. Overseas U Mobile customers calling this number should be charged
**Free of Charge**, but the customer was billed.

---

## Root Cause Explanation

Calls to the Overseas Careline number are expected to pass through a specific decision node
(**Judgecalltomalalysia3**) in the rating workflow.

![Charging Pre-processing Workflow — Judgecalltomalaysia3 node](images/page_1.png)

However, the call did **not** satisfy the rule expressions defined for that node. The CDR
values show:

- **Peer Number = 60183886688**
- **Call Nature = 0**

![CDR — Peer Number = 60183886688](images/page_2.png)

![CDR — Call Nature = 0](images/page_3.png)

Because these values did not meet the required criteria, the call was routed to subsequent
nodes in the workflow and was rated as a **charged event** (RE_ID = 20023, Roaming Call
Local).

For Overseas Careline calls, the expected event should be **RE_ID = 20022 (Roaming Call
Back)**, which carries a zero charge.

![RE table — RE_ID 20022 (Roaming Call Back) vs 20023 (Roaming Call Local)](images/page_4.png)

---

## Cross-Check — Other Customers

For the billing cycle of **2025-06-15**, several other calls to `60183886688` were also
charged. CDR review confirms that all affected records carry `Call Nature = 0`, causing
them to be processed as RE_ID = 20023 (charged).

![EVENT_USAGE query — multiple charged records with Call Nature = 0](images/page_5.png)

In contrast, calls to `60183886688` that were **not** charged correctly carry
**Call Nature = 1**, which routes the call to the free event (RE_ID = 20022).

![EVENT_USAGE query — uncharged records with Call Nature = 1](images/page_6.png)

---

## Conclusion

The rating engine behaved correctly based on the Call Nature value it received. The root
cause is that the **core network passed Call Nature = 0** instead of the expected value of 1.

**Next Step:** The Call Nature value must be verified with the **network team** to
determine why it is being transmitted as 0 for calls to the Overseas Careline number.
""",

"Prepaid_GX38_PAYU_PROVISIONING": """\
# Prepaid GX38 — PAYU Charge Due to Provisioning Timing

**Case Reference:** CSC 267842071

## Problem

The customer purchased GX38 at `2025-03-21 12:05:00` but was charged **RM 0.10 PAYU**
at `2025-03-21 12:05:02`.

![Charging Detail — PAYU RM 0.10 at 12:05:02, GX38 activated at 12:05:05](images/page_1.png)

---

## Investigation

### Step 1 — Dispatch Order Query

Dispatch Order Query was performed using the customer's Service Number.

![Dispatch Order Query — Order 767768241 created at 12:05:02](images/page_2.png)

### Step 2 — PCC → AddPckg Provisioning Detail

Drilled into the workflow node **PCC → AddPckg**. The Work Order Detail confirms that
provisioning was only **completed at `2025-03-21 12:05:02.801`**.

![Work Order Detail — AddPckg completed at 12:05:02.801](images/page_3.png)

---

## Root Cause

The customer started using data at **`2025-03-21 12:05:02.000`** (refer to LOCAL_DATA),
while the GX38 package became effective at **`2025-03-21 12:05:02.801`** (refer to
GX38_PROVISIONING).

Although the gap is only **801 milliseconds**, data usage began **before** GX38 was
provisioned. The RM 0.10 PAYU charge is therefore valid.

| Event | Timestamp |
|-------|-----------|
| Data usage started | 2025-03-21 12:05:02.000 |
| GX38 package activated | 2025-03-21 12:05:02.801 |
| Gap | 801 ms |
""",

"RG35": """\
# GX38 PAYU Charge — RG35 Transmitted by Network

**Case Reference:** CSC 288522667

## Problem

- Customer already purchased GX38, but was still being charged PAYU.
- Customer disputes the PAYU charges and requests a refund.

---

## Explanation

The GX38 package was successfully renewed on **2025-08-24 at 07:20:04**, but the customer
was still charged PAYU at **2025-08-24 at 07:20:06**.

The PCC package provisioning request was sent at **2025-08-24 07:20:05.110**.

![Charging Detail — GX38 renewal and PAYU charge timeline](images/page_2.png)

For GX38 data usage, **RG1154** should be transmitted from the network to the OCS. The
Rating Group (RG) received from the network determines which package is applied.

In this case, PAYU was charged because the core network transmitted **RG35** instead of
RG1154.

![EVENT_USAGE — RATING_GROUP_ID = 35](images/page_4.png)

![Work Order Detail — PCC AddPckg at 07:20:05](images/page_3.png)

## Root Cause

The OCS behaved correctly based on the RG value it received. The issue originates from the
**core network transmitting RG35 instead of RG1154**.

## Next Step

This needs to be escalated to the **network team** for investigation. The OCS-side logic is
correct.
""",

"Reserve_RM10": """\
# Reserve RM 10 — Charging Detail vs Balance Discrepancy

**Case Reference:** CSC 282610244

## Problem

The Charging Detail figures do not match the customer's credit balance and top-up history.

---

## Explanation

### How PAYU Data Charging Works

1. Initially, **6 MB of free data** is allocated to the customer.
2. Once the 6 MB is consumed, the system opens an additional **100 MB block** and
   **reserves RM 10** from the customer's balance.
3. Per the configured pricing, every **100 MB used** incurs a charge of **RM 10**.
4. If the customer does **not** exceed the allocated 100 MB quota within the session, the
   **reserved RM 10 is released back** to the balance when the session ends.

This reservation-and-release mechanism is why the Charging Detail view can show higher
figures than the customer's actual balance deductions or top-up history. **There is no
charging error.**

![Usage Price configuration — RM 0.1 per 1,048,576 bytes (1 MB)](images/page_2.png)

### Reference Screenshots

- `Rounded_Value.png` — shows the 100 MB block allocation and RM 10 reservation.
- `Usage_Price.png` — confirms the RM 0.1 per MB pricing configuration.
""",

"Roaming_Add_On_AFTER_EXPIRED": """\
# Roaming Add-On Usage After Parent Pass Expiry

**Case Reference:** CSC 266247713

## Problem

The customer asked:
1. Why could they continue using the roaming add-on even after the **7-Day Roaming Pass**
   had expired?
2. Why did the **24-Hour Roaming RM 15** charge only appear **after** the add-on quota
   was exhausted?
3. Why were the charges not yet reflected in Charging Detail?

---

## Reply

### Question 1 — Add-On After Parent Pass Expiry

The customer can continue using the **"2 GB (RM 10 / 24 hours)"** add-on even after the
"7-Day Roaming Pass" has expired, because the add-on carries its own **independent
24-hour validity window** from the time of purchase. The expiry of the parent pass does not
invalidate the add-on.

### Question 2 — UDR15 Triggered After Add-On Exhausted

The original 2 GB quota was **fully exhausted on 14 March 2025 at 21:23:11**.

![add_on.png — 2 GB quota exhausted at 21:23:11](images/page_1.png)

The customer continued using data after the quota was depleted. This automatically
triggered the **UDR15 charge on 14 March 2025 at 23:13:31**.

![UDR15.png — UDR15 charged at 23:13:31](images/page_2.png)

All charges are valid.

### Question 3 — Charges Not in Charging Detail

Charges may not appear in the Charging Detail view immediately; there can be a short
processing lag before they are reflected. No action is required.
""",

"UDR38_Double_Charge": """\
# UDR38 Double Charge — RG35 Network Issue

## Customer Problem

Please help check why the system auto-subscribed to the **24-Hour Roaming RM 38** plan
when the customer already had the same plan active.

| # | Transaction | Time | Channel |
|---|------------|------|---------|
| 1 | 24-Hour Roaming RM 38 (Manual) | 2025-04-19 17:16:21 | MyUMobile App |
| 2 | 24-Hour Roaming RM 38 (Auto) | 2025-04-19 19:14:32 | ZSmart |

---

## Reply

### Timeline of Events

The user initiated a data session on **2025-04-19 at 17:14:17**, which was recorded under
**RG35**.

![Charging Detail — Roaming Data session at 17:14:17 under RG35](images/page_1.png)

The user then manually subscribed to the UDR38 plan at **17:16:22**.

At **19:14:18**, a CCR-U / CCR-T update reported more than **4 MB of data usage** under
RG35, exceeding the free-data quota threshold. This automatically triggered the system to
purchase UDR38 again.

![EVENT_USAGE — RATING_GROUP_ID = 35](images/page_2.png)

---

## Root Cause

The original data session was tagged under **RG35**, not under the rating group bound to
the manually-purchased UDR38. Because the OCS observed RG35 traffic exceeding the
free-quota threshold, it correctly applied the auto-purchase rule.

The duplicate UDR38 is a direct consequence of the **core network reporting traffic under
RG35 instead of the expected rating group** for the active UDR38 plan.

## Next Step

This needs to be escalated to the **network team** to investigate why the session was tagged
under RG35 after a UDR38 plan was already active. The OCS logic itself is correct.
""",

"UDR38_Partial_Charging_Breakdown_Postpaid": """\
# UDR38 Partial Charging Breakdown — Postpaid

**MSISDN:** 601111120560

## Charging Overview

![Charging Detail — two Roaming Data sessions on 2025-04-27](images/page_1.png)

---

## UDR38 Trigger Mechanism

UDR38 is triggered when:
- **CCR-U** (Update) reports usage **≥ 4 MB + 48 KB**, **OR**
- **CCR-T** (Terminate) reports usage **≥ 3 MB + 48 KB**

---

## Session Analysis

### Session 1 — 2025-04-27 19:49:33

CCR-T reported **1 MB + 48 KB**, which is **below** the 3 MB + 48 KB threshold.

The system therefore applied **segmented billing at RM 9.50 per MB**, resulting in a charge
of **RM 9.50**.

![Detail Information — Session 1, Charge RM 9.50, Rounded Volume 1 MB 48 KB](images/page_2.png)

### Session 2 — 2025-04-27 19:52:35

Because Session 1 had already consumed 1 MB + 48 KB on the same day, Session 2 only
needed CCR-T usage above **2 MB** to trigger UDR38.

UDR38 has a **daily cap of RM 38.00**. The system applied a protective mechanism and
limited the deduction to **RM 28.50** (the remaining headroom under the daily cap),
preventing over-charging.

**Daily total: RM 9.50 + RM 28.50 = RM 38.00 = UDR38 daily cap.**

![Detail Information — Session 2, Charge RM 28.50, Rounded Volume 6 MB 189 KB](images/page_3.png)

---

## Summary

| Session | Start Time | CCR-T Usage | Charge | Reason |
|---------|-----------|-------------|--------|--------|
| Session 1 | 19:49:33 | 1 MB + 48 KB | RM 9.50 | Below UDR38 threshold — segmented billing |
| Session 2 | 19:52:35 | 6 MB + 189 KB | RM 28.50 | UDR38 triggered; capped at daily limit remainder |
| **Total** | | | **RM 38.00** | = UDR38 daily cap |
""",

"UDR38_Partial_Charging_Breakdown_Prepaid": """\
# UDR38 Partial Charging Breakdown — Prepaid (Insufficient Balance)

## Customer Problem

The customer was roaming in Cambodia. Their prepaid account balance was insufficient to
purchase the full 24-Hour UDR38 pass (RM 38), but charges were still deducted. The
customer questioned whether this was a PAYU charge or a UDR38 charge.

---

## Plan Verification

Investigation confirms the customer's Price Plan is **12603 = UDR Roaming Price Plan**
— this is **not** PAYU. When the account balance is insufficient to activate the full UDR38
pass, the system automatically falls back to the **per-MB charging rule** built into the UDR
Roaming Price Plan (RM 9.50 per MB).

![PRICE_PLAN table — Price Plan 12603 = UDR Roaming Price Plan](images/page_1.png)

---

## Detailed Calculation

| Step | Operation | Value |
|------|-----------|-------|
| 1 | Total reported usage (two sessions combined) | 767,648 + 1,378,890 = **2,146,538 bytes** |
| 2 | Deduct first 48 KB free allowance | 2,146,538 − (48 × 1,024) = **2,097,386 bytes** |
| 3 | Convert to MB | 2,097,386 / 1,048,576 ≈ **2.000223 MB** |
| 4 | Round up to nearest whole MB | **3 MB** |
| 5 | Apply RM 9.50 per MB | 3 × RM 9.50 = **RM 28.50** |
| 6 | Actual deduction (balance cap protection) | Balance was only **RM 21.64** → system deducted full balance |

![Charging Detail and CDR — usage breakdown and billing](images/page_2.png)

---

## Conclusion

- The charges are rated under the **UDR Roaming Price Plan**, not PAYU.
- Since the balance (RM 21.64) was insufficient for the full UDR38 pass (RM 38), the
  system applied the per-MB fallback rule at **RM 9.50 per MB**.
- The final deduction of RM 21.64 reflects the system's **balance-cap protection**,
  which prevents over-charging beyond the available balance.
- The second charge on 2025-03-16 was calculated using the same per-MB method.

> **Note:** The second charge on 2025-03-16 was calculated using the same UDR38 per-MB
> charging method.
""",

"Use_Before_Buy": """\
# Use Before Buy — Roaming Charge Triggered Before Manual Pass Purchase

**Case Reference:** CSC 302870398

## Findings

### Finding 1

The customer started using roaming data on **2025-12-23 at 18:23:01**.

### Finding 2

The **24-Hour Roaming RM 15** pass was purchased only on **2025-12-23 at 18:25:33** —
approximately **2 minutes 32 seconds** after roaming data usage had already begun.

### Finding 3

Further analysis confirms that all subsequent roaming records share the **same SESSION_ID**,
indicating that all data usage belongs to a **single continuous roaming session** that started
before the pass was purchased. Within that session, usage exceeded the 48 KB free threshold,
which automatically triggered the 24-Hour Roaming pass auto-purchase.

---

## Root Cause

The auto 24-Hour Roaming charge triggered on **2025-12-23 at 18:25:33** is valid, because
the roaming session was already active before the manual roaming pass was purchased.

An auto-trigger that fires within an existing session **cannot be retroactively cancelled** by
a manual purchase made later in the same session.

## Conclusion

All roaming charges are valid.

## Customer Advisory

Customers should **purchase the roaming pass BEFORE enabling data roaming** or using
any roaming-dependent app. Once a roaming data session has started, the system may
auto-trigger a pass purchase the moment usage crosses 48 KB — even if the customer
manually purchases a pass moments later.
""",

"Case_320585002_Call_Rejection_RCA": """\
# Call Rejection Root Cause Analysis

**Case ID:** 320585002 | **Ticket:** INC000100939422 | **Author:** CHAI YEU HARNG | **Date:** 13 May 2026

---

## Incident Summary

| Field | Detail |
|-------|--------|
| Subject | AI RUDDER ISBC SIP TRUNK \| ERROR CODE 540 \| Call rejected by WCT with Cause 21 |
| Incident Date | 30 April 2026, 09:09:51 |
| A-Party (Calling) | 0393882149 / 03331018 |
| B-Party (Called) | 60188732400, 60139404789 |
| Reported By | Mohd. Fadli Bin Ahmad Kamal |
| **Root Cause** | **Called party subscription status was not Active (A) at the time of the call attempt** |

---

## 1. Problem Scenario

On **30 April 2026**, an inbound call from A-party `0393882149` to B-party `60188732400`
was rejected. The caller observed a **SIP 540 / ERROR CODE 540**, with the call being
released at the WCT (Wholesale Call Termination) leg carrying **Q.850 Cause Code 21
(Call Rejected)**.

The call flow traversed: `VMSKPA → vSTKPA → CELKP01MP08 → vSTHXA → WCT HTSAUPR1`.
The rejection was initiated by **CELKP01MP08** (IN/SCP node) sending
`INVOKE RELEASECALL (Cause: 21)` toward WCT.

### 1.1 Original Case Detail

![Figure 1 — KBS Case Detail view](images/page_1.png)

### 1.2 PCAP Call Flow

![Figure 2 — SIP/CAP call ladder diagram; RELEASECALL Cause 21 from CELKP01MP08](images/page_2.png)

---

## 2. Investigation Approach

The initial Cause Code 21 is generic at the Q.850 layer. The investigation followed a
structured isolation approach to determine whether the fault was on the A-party, B-party,
or in the routing/charging logic.

### 2.1 Hypotheses Considered

- **A-party barring / suspension** — calling subscriber has outgoing call barring or credit issue.
- **B-party subscription status** — called subscriber is suspended, barred, or terminated.
- **MNP / Routing error** — number portability database returning incorrect routing prefix.
- **WCT routing policy / blacklist** — WCT internal anti-fraud or routing table rejection.
- **IN/SCP charging logic** — CAMEL/IN service triggered rejection based on subscriber profile.

### 2.2 Approach Taken

Given that RELEASECALL was sent by **CELKP01MP08** (IN/SCP), the most likely failure
domain was the charging/IN logic acting on the B-party profile. The subscription status of
both called numbers was verified in the **PROD_HIS** database at the time of the incident.

---

## 3. Database Verification — Subscriber Status Check

Queries were executed against the `PROD_HIS` table for both called numbers.

### 3.1 B-Party: 60188732400

![Figure 3 — PROD_HIS query for 60188732400](images/page_3.png)

The most recent state record shows **PROD_STATE = 'E'**, effective from
**2026-04-26 02:11:27** — approximately 4 days before the failed call.

### 3.2 B-Party: 60139404789

![Figure 4 — PROD_HIS query for 60139404789](images/page_4.png)

The state record shows **PROD_STATE = 'M'**, effective from **2026-04-15 00:01:47** —
approximately 15 days before the call attempt.

### 3.3 PROD_STATE Reference

| Code | State Name | Standard State | Description |
|------|-----------|----------------|-------------|
| A | Active | A | Subscriber is fully active. |
| E | Suspended | E | Two-Way Block (cannot make or receive calls). |
| M | Barred | D | Barring state. |

**Conclusion of database check:** Both B-parties were in **non-Active states** (E = Suspended,
M = Barred) at the time of the call attempt.

---

## 4. Charging Workflow Logic Verification

The IN-Process Rule under the **Usage Pre-processing Workflow** was inspected to confirm
that a non-Active subscription status deterministically triggers call rejection.

### 4.1 'Not Active' Validation Node Logic

Within the **MT IR Process** branch, a node named **'Not Active'** is positioned immediately
after 'Set IR MT attribute'. This node enforces:

```
Rule Expression:  {{ (Main Product State) != A }}
Result:           OCS Result Code = Assign(OCS Result Code, 4010)
System Action:    Release call → Voice End
```

If the called party's Main Product State is not 'A' (Active), the system assigns OCS Result
Code 4010 and terminates the call branch, which translates to a release with **Cause 21**
toward the originating signalling path.

![Figure 6 — IN-Process Rule: 'Not Active' node under MT IR Process](images/page_5.png)

---

## 5. Root Cause Summary

| Domain | Finding |
|--------|---------|
| A-party | No issue. Calling subscriber successfully originated the call signalling. |
| Network / Routing | No fault. Signalling reached the IN node correctly via SS7/SIP. |
| WCT | Not the originator of the rejection. WCT only relayed/observed Cause 21. |
| **B-party Subscription** | **Root cause.** Both called numbers were in non-Active states (E and M) at incident time. |
| Charging Logic | Behaved as designed. 'Not Active' node correctly enforced the business rule. |

---

*Internal use only. Document prepared by CHAI YEU HARNG, 13 May 2026.*
""",

"15GB_Roaming_Exhausted_Charged_UDR15": """\
# 15GB Roaming Quota Exhausted — Three UDR15 Charges

**Case Reference:** CSC 283054399

## Problem

The customer disputed being charged **UDR15 three times**.

---

## Explanation

Three separate roaming data sessions were identified, each triggering an automatic RM 15
charge:

| Session | Date & Time | Charge |
|---------|-------------|--------|
| Session 1 | 04/07/2025 20:47:36 | RM 15 |
| Session 2 | 05/07/2025 20:51:13 | RM 15 |
| Session 3 | 06/07/2025 22:58:14 | RM 15 |

---

### Session 1 — 04/07/2025 20:47:36

The customer's **U Postpaid 98 Roaming 15GB** quota was fully exhausted on
**2025-07-04 at 16:16:57**. After exhaustion, the customer resumed data usage. At
**20:47:36**, the total usage recorded was 5 MB 512 KB 7 Bytes. Since CCR-T reported
usage above the 48 KB free threshold, a UDR15 was triggered automatically.

![First UDR15 — quota exhausted at 16:16:57, charge at 20:47:36](images/page_1.png)

### Session 2 — 05/07/2025 20:51:13

A UDR15 pass is valid for **24 hours**. The first UDR15 expired at **2025-07-05 20:49:04**.
The customer used data again at **20:51:13** (approximately 2 minutes after expiry), and
usage once again exceeded the 48 KB free threshold, triggering a **new UDR15**.

![Second UDR15 — expiry at 20:49:04, new charge at 20:51:13](images/page_2.png)

### Session 3 — 06/07/2025 22:58:14

Similarly, the second UDR15 expired after its 24-hour validity. The customer's usage again
exceeded the 48 KB threshold at this timestamp, triggering a **third UDR15**.

---

## Conclusion

All three UDR15 charges are correctly triggered. After the original 15GB quota was exhausted,
each subsequent roaming data session that exceeded the 48 KB free threshold (after the
prior UDR15's 24-hour validity had lapsed) automatically triggered a new UDR15.

The charges are valid and no waiver is applicable.

## Customer Advisory

Once the bundled roaming quota is exhausted, the customer should either:
- **Purchase a top-up roaming pass** before resuming data usage, or
- **Disable mobile data roaming** on the device to avoid further automatic UDR15 triggers.
""",

"RG35_Network_Retrived": """\
# RG35 Transmitted by Network — UDR15 & Incoming Call Charges

## Summary of Findings

Two distinct issues were identified for this case.

---

## Finding 1 — UDR15 Charges (Root Cause: RG35 Transmitted by Network)

CDR records confirm the customer has used the **U Biz Share 128 Roaming** service.

For this package to apply correctly, the network side must transmit **RG7154** to the OCS.
The Rating Group received from the core network determines which package is applied.

The customer was charged UDR15 **twice** because the core network transmitted **RG35**
instead of **RG7154**.

![Charging Detail — RG35 roaming session details](images/page_1.png)

![CDR — RATING_GROUP_ID = 35 instead of expected 7154](images/page_2.png)

**Next Step:** Escalate to the **network team** — the OCS logic is correct.

---

## Finding 2 — Roaming Incoming Call Charges (Expected Behaviour)

The roaming incoming call charges are **correctly applied**. The customer's current plan
(**U Biz Share**) does **not** include the Postpaid 5G Roaming MT service. As a result,
any incoming calls received while roaming are billed at standard international roaming rates.

The **U Biz Share 128** plan includes Postpaid 5G Roaming MT (free incoming calls while
roaming). The customer would need to upgrade to the 128 plan to benefit from free roaming
incoming calls.

![Tariff Plan comparison — U Biz Share vs U Biz Share 128 (Postpaid 5G Roaming MTC)](images/page_3.png)

---

## Summary

| Issue | Root Cause | Action Required |
|-------|-----------|----------------|
| UDR15 data charges | Network transmitted RG35 instead of RG7154 | Escalate to network team |
| Roaming incoming call charges | Plan does not include Roaming MT service | Valid charge — advise customer to upgrade to U Biz Share 128 if free MT is required |
""",

"SMS_DELAY": """\
# SMS Notification Delay — Roaming Charge vs Alert Timing

**Case Reference:** CSC 265463254

## Problem

The customer claimed that:
1. The free roaming reminder SMS arrived only around **7:00 PM**, by which time the alert
   period had already ended.
2. They had not actually used roaming, yet charges were observed starting from around
   **6:00 PM** on the same day.

---

## Investigation Timeline

| Timestamp | Event |
|-----------|-------|
| 2025-01-25 19:15:30 | UDR free quota fully consumed |
| 2025-01-25 19:33:58 | UDR charge triggered |
| 2025-01-25 19:34:12 | Notification SMS triggered from Zsmart CIC |
| 2025-01-26 01:55:24 | SMSC returned delivery acknowledgement (>6 hours later) |

![Charging Detail — UDR quota exhausted at 19:15:30, charge at 19:33:58](images/page_1.png)

![Elastic — CIC notification trigger at 19:34:12](images/page_2.png)

---

## Cross-Check via Customer 360 View

- SMS triggered out from Zsmart CIC at **2025-01-25 19:34:12**.
- Zsmart CIC received the delivery response from SMSC at **2025-01-26 01:55:24** —
  a delay of **more than 6 hours**.

![Customer 360 — SMS interaction log showing CIC trigger vs SMSC delivery time](images/page_3.png)

---

## Root Cause

The CIC notification trigger fired correctly at **19:34:12**. However, the SMSC only
delivered the acknowledgement at **01:55:24** the following day. This is a **delivery /
processing delay on the SMSC side**, not an issue with the rating engine or the
notification trigger.

## Recommendation

Escalate to the **SMSC team** to investigate the cause of the multi-hour delivery lag and
verify their timestamps. Until resolved, customers may continue to perceive a mismatch
between when charges begin and when they receive the alert SMS.
""",

}


import base64
import re as _re


def render_pages_as_b64(pdf_path):
    """Render each PDF page as PNG and return list of base64 strings."""
    doc = fitz.open(pdf_path)
    pages_b64 = []
    for page in doc:
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)
        png_bytes = pix.tobytes("png")
        b64 = base64.b64encode(png_bytes).decode("ascii")
        pages_b64.append(b64)
    doc.close()
    return pages_b64


def embed_images_in_markdown(md_text, pages_b64):
    """Replace images/page_N.png references with inline base64 data URIs."""
    def replacer(m):
        alt = m.group(1)
        page_num = int(m.group(2)) - 1  # 0-indexed
        if page_num < len(pages_b64):
            data = pages_b64[page_num]
            return f"![{alt}](data:image/png;base64,{data})"
        return m.group(0)  # leave unchanged if page not found

    return _re.sub(r'!\[([^\]]*)\]\(images/page_(\d+)\.png\)', replacer, md_text)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    pdfs = [f for f in os.listdir(SRC_DIR) if f.lower().endswith(".pdf")]
    print(f"Found {len(pdfs)} PDF files.")

    for pdf_file in pdfs:
        stem = os.path.splitext(pdf_file)[0]
        pdf_path = os.path.join(SRC_DIR, pdf_file)

        file_out_dir = os.path.join(OUT_DIR, stem)
        os.makedirs(file_out_dir, exist_ok=True)

        print(f"  Processing: {pdf_file}")

        content = MARKDOWN_CONTENT.get(stem)
        if not content:
            print(f"    -> WARNING: No markdown content defined for '{stem}', skipping.")
            continue

        # Only render pages if the markdown references images
        if "images/page_" in content:
            pages_b64 = render_pages_as_b64(pdf_path)
            content = embed_images_in_markdown(content, pages_b64)

        md_path = os.path.join(file_out_dir, f"{stem}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        print(f"    -> Written: {stem}.md ({os.path.getsize(md_path) // 1024} KB)")

    print(f"\nDone. Output folder: {OUT_DIR}")


if __name__ == "__main__":
    main()
