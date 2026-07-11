# ✅ TMDL Model Fixes — Verification Checklist

*Last updated: 2026-07-11*

---

## Fix 1 — FactSalesTargets: Remove Bi-Directional Relationship ✅
**File:** `definition/relationships.tmdl`

Removed `crossFilteringBehavior: bothDirections` and `fromCardinality: one` from the `DimDate → FactSalesTargets` relationship.

**Before (broken):**
```
relationship f0c93f68-3f6d-c5ce-69d8-234572cf47a5
    crossFilteringBehavior: bothDirections
    fromCardinality: one
    fromColumn: DimDate.Date
    toColumn: FactSalesTargets.Period
```
**After (correct):**
```
relationship f0c93f68-3f6d-c5ce-69d8-234572cf47a5
    fromColumn: DimDate.Date
    toColumn: FactSalesTargets.Period
```
> Standard one-to-many, single-direction filter flow restored.

---

## Fix 2 — FactInventory: Dynamic Unpivoting M Code ✅
**File:** `definition/tables/FactInventory.tmdl`

Replaced hardcoded year-month column list with a dynamic `UnpivotOtherColumns` first approach.

**Before (broken):** `ChangedType` listed every month column (`2025-01` through `2025-12`) before unpivot — breaks when new year columns are added.

**After (correct):** `UnpivotOtherColumns` runs immediately after `PromoteHeaders`, then a single `ChangedType` casts the now-scalar `YearMonth` (date) and `Units` (Int64) columns.

> New year columns (2026+) are automatically picked up — no M code changes needed.

---

## Fix 3 — Security Table: Remove Physical Relationships ✅
**File:** `definition/relationships.tmdl`

Deleted both physical relationships from the Security table:
- `DimCustomer.Region → Security.Region` (active)
- `DimGeo.Region → Security.Region` (inactive)

> Security table is now physically disconnected. RLS is enforced exclusively via DAX `LOOKUPVALUE()` in `roles.tmdl`.

> **TMDL Note:** `//` comments at document root scope are **invalid** TMDL — they were removed. The intent is now documented in `roles.tmdl` and this checklist.

---

## Fix 4 — FactPromotionCoverage: Enable Both-Directions Filter ✅
**File:** `definition/relationships.tmdl`

Added `crossFilteringBehavior: bothDirections` to the `FactPromotionCoverage.ProductKey → DimProduct.ProductKey` relationship.

```
relationship d3b8bdbb-ebde-9110-d56c-3bbb75da3851
    crossFilteringBehavior: bothDirections
    fromColumn: FactPromotionCoverage.ProductKey
    toColumn: DimProduct.ProductKey
```
> Enables DimCampaign slicers to propagate through the bridge table and filter DimProduct correctly.

---

## Fix 5 — FactOrderFulfillment: Enforce 1:1 Order Grain ✅
**File:** `definition/tables/FactOrderFulfillment.tmdl`

Replaced naive left-joins (which caused row explosion for orders with multiple shipments/invoices) with pre-aggregated `Table.Group` steps.

**Key changes:**
- Shipments grouped by `OrderID`, taking `List.Max(ShipDate)` and `List.Max(DeliveryDate)`
- Invoices joined to Payments first, then grouped by `OrderID` for `InvoiceDate` and `PayDate`
- Eliminated `InvoiceID` as intermediate join key (was causing fan-out)

> Each OrderID now appears exactly once in FactOrderFulfillment. Measure totals are accurate.

---

## Fix 6 — RLS Roles: Created via Disconnected Security Table ✅
**File:** `definition/roles.tmdl` *(new file)*
**File:** `definition/model.tmdl` *(updated — `ref role` entries added)*

Three roles defined:

| Role | Permission | Filter Logic |
|---|---|---|
| `Regional Sales Rep` | `read` | `DimCustomer[Region]` and `DimGeo[Region]` filtered via `LOOKUPVALUE(Security[Region], Security[UserEmail], USERPRINCIPALNAME())` |
| `Executive` | `read` | No filter — sees all regions |
| `Admin` | `readRefresh` | No filter — full model + refresh access |

> **Pattern:** Security table has zero physical relationships. RLS propagates through the active `DimCustomer → FactSales` and `DimGeo → FactSales` relationships automatically once the dimension rows are filtered.

---

## TMDL Syntax Rules (Lessons Learned)

| ❌ Invalid | ✅ Valid |
|---|---|
| `//` at document root scope | Only `relationship`, `role`, `table`, `annotation` blocks |
| `///` at document root scope | `///` only **inside** indented object bodies |
| `//` comments in TMDL properties | `//` is valid **only inside M query `source =` blocks** |
| `fromCardinality: one` on a standard many-to-one | Only use when the "from" side is genuinely unique |

