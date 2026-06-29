# Ohio Department of Development (ODD) — grants, loans, and tax incentives

Statewide disbursement and incentive data exported from the Ohio Department of
Development's public reporting systems. Covers the full state; filter on
`SERVICE_LOCATION_DESCR` (grants/loans) or `COUNTY` (tax incentives) for per-site
analysis.

## Files

### `grants_and_loans.csv`

33,371 rows. One row per purchase-order distribution line for every ODD grant or loan
disbursement. Key columns:

| Column | Meaning |
|---|---|
| `GRANT_LOAN` | `Grant` or `Loan` |
| `VENDOR_NAME1` | Recipient organization |
| `SERVICE_LOCATION_DESCR` | County served (e.g. `ALLEN COUNTY`) |
| `PROGRAM_DESCR` | Program category |
| `FUND_DESCR` | Federal/state fund source |
| `PO_DISTRIB_MERCHANT_AMT` | Amount disbursed on this line |
| `REMAINING_BALANCE` | Outstanding balance (loans) |
| `PO_BUDGET_PERIOD` | State fiscal year (2010–2026) |

**Allen County (Lima) summary:** 522 rows, ~$103.5M total.
Dominant recipients: West Ohio Community Action Partnership ($41.7M, HEAP/CSBG),
Allen County ($9.8M), Allen County Port Authority ($7.5M).

### `tax_incentives.csv`

2,298 rows. One row per approved tax incentive agreement. Key columns:

| Column | Meaning |
|---|---|
| `COMPANYNAME` | Company receiving the incentive |
| `COUNTY` | Ohio county |
| `PROGRAM` | `JCTC Job Creation Tax Credit`, `JRTC-NR`, `Ohio Historic Preservation Tax Credit`, `Datacenter Tax Exemption` |
| `ORIGINAL_ESTIMATED_VALUE` | State's estimated credit value |
| `INVESTMENT` | Company's capital investment commitment |
| `NEW_JOBS` / `RETAINED_JOBS` | Job commitment |
| `STATUS` | `Servicing`, `Completed`, `Cancelled`, `Approved` |

**Allen County (Lima) summary:** 19 records. Largest: P&G (2022 JCTC, $501M investment,
135 new + 749 retained jobs). Ford Motor has both a JCTC and a JRTC. No Datacenter Tax
Exemptions in Allen County — all 9 statewide datacenter exemptions are in Franklin,
Cuyahoga, Hamilton, Licking, and Monroe counties.

## Source

Ohio Department of Development public reporting portal. Data pulled **2026-06-28**.
No API — these are direct exports from ODD's transparency site. To regenerate, download
fresh exports from the ODD public portal and replace these files.

## Gaps

- Grants/loans file reflects PO distribution lines, not final expenditure — a completed
  grant shows `REMAINING_BALANCE = 0` but the row is still present.
- Tax incentives represent approved agreements, not actual credits taken; cancelled
  agreements are included in the export.
- Statewide data only — no sub-county breakdown.
- Date range: budget periods 2010–2026; records before 2010 are not in this export.
