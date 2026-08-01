# SportDGX — Entity Contract

**Version:** 0.1.0
**Status:** Contract only. No runtime framework, renderer, service layer or repository adapter exists yet.
**Machine-readable twin:** [`assets/sdgx/schema/entities.js`](../assets/sdgx/schema/entities.js)

This document and `entities.js` describe the same contract. If a field changes in one, it changes in both. `entities.js` is the authority for exact spelling and types; this document is the authority for intent.

Nothing in the repository imports the schema yet. It is inert and deployed to no page.

> **All example records in this document are fictional placeholders written to illustrate shape.**
> They are marked `EXAMPLE — NOT DATA`. No real venue, team, capacity, date, price, provider, advertiser or partnership is asserted anywhere in this file.

---

## Contents

1. [Conventions](#1-conventions)
2. [Shared field groups](#2-shared-field-groups)
3. [Enumerations](#3-enumerations)
4. [Geography](#4-geography) — Region · CountryOrTerritory · AdministrativeRegion · City · Venue
5. [Sports](#5-sports) — Sport · Competition · SeasonOrEdition · Event · Team
6. [Commercial and distribution](#6-commercial-and-distribution) — TicketProvider · TravelProvider · MerchandiseProvider · Advertiser · CommercialPlacement · Article · SourceRecord · NewsletterSignupSource
7. [Relationship summary](#7-relationship-summary)
8. [Global validation rules](#8-global-validation-rules)
9. [Documented deviations](#9-documented-deviations)

---

## 1. Conventions

### Stable IDs

Format: `{idPrefix}:{stable-key}`

The stable key is chosen once and never changes, even if the display name does. **Display names are never foreign keys.** A venue that is renamed keeps its ID; the rename is recorded in `nameHistory`.

IDs are globally unique across the entire dataset, not merely within an entity type. This makes a polymorphic reference (`targetEntityId` on a placement) unambiguous on its own.

### Slugs

- Lowercase `a-z`, digits `0-9`, hyphens. No leading, trailing or repeated hyphens.
- Uniqueness is scoped, declared per entity as `slugScope`:
  - `per-entityType` — unique among all records of that type
  - `per-country`, `per-city`, `per-sport`, `per-competition`, `per-season` — unique within the named parent
  - `null` — the entity has no slug and no public page

Scoped slugs are what make `/cities/kansas-city/` and a same-named city in another country coexist without ID collisions.

### ISO codes

Used only where the entity genuinely has one — `CountryOrTerritory` (ISO 3166-1) and `AdministrativeRegion` (ISO 3166-2). Both are **optional**: territories, disputed entities and historical records may have none. Venue, Team, Competition and Event carry no ISO codes because none exist for them.

### Commercial configuration

Monetisation is expressed through `CommercialPlacement` records and provider records, **not** duplicated across every factual entity. Entities carry only capability flags that cannot be derived from placements:

| Flag | Why it can't be derived |
|---|---|
| `monetizationEnabled` | Records a deliberate editorial decision. The absence of placements is ambiguous — it could be an oversight. `false` is an assertion. |
| `newsletterTopic` | A topic key for routing signups; not commercial inventory. |

Fields explicitly **not** stored on factual entities, because they are derivable: `ticketingEnabled`, `travelEnabled`, `merchandiseEnabled`, `advertiserInventory`, `commercialPriority`, `supportedCommercialActions`. Ticketing capability is derived from provider records scoped to the entity; priority lives on the placement.

Each entity descriptor declares `commercial.placementTargetable` — whether a placement may point at it.

### Verification

Every factual entity carries `verificationStatus`. Each descriptor also declares `verification.gatedFields`: fields that may **not** render as fact without a supporting `SourceRecord` at or above `minAuthorityForGated`. This is enforced by validation, not left to authorial discipline.

---

## 2. Shared field groups

### FACTUAL_BASE

Applied to: Region, CountryOrTerritory, AdministrativeRegion, City, Venue, Sport, Competition, SeasonOrEdition, Event, Team, Article.

| Field | Type | Required |
|---|---|---|
| `id` | id | ✅ |
| `slug` | slug | ✅ |
| `name` | string (≤200) | ✅ |
| `shortName` | string (≤60) | — |
| `description` | text | — |
| `status` | enum `status` | ✅ |
| `pageStatus` | enum `pageStatus` | ✅ |
| `officialSourceUrl` | url | — |
| `sourceRecordIds` | idRefArray → SourceRecord | — |
| `verifiedAt` | datetime | — |
| `lastUpdated` | datetime | ✅ |
| `verificationStatus` | enum `verificationStatus` | ✅ |
| `notes` | text | — |

### PROVIDER_BASE

Applied to: TicketProvider, TravelProvider, MerchandiseProvider.

| Field | Type | Required |
|---|---|---|
| `id` | id | ✅ |
| `slug` | slug | ✅ |
| `name` | string (≤200) | ✅ |
| `shortName` | string (≤60) | — |
| `description` | text | — |
| `operatorLegalName` | string | — |
| `classification` | enum `providerClassification`, default `informational` | ✅ |
| `url` | url | — |
| `affiliateNetwork` | string | — |
| `affiliateMarker` | string | — |
| `disclosureRequired` | boolean, default `true` | ✅ |
| `appliesToEntityTypes` | stringArray | — |
| `geoScopeCountryIds` | idRefArray → CountryOrTerritory | — |
| `policyNote` | text | — |
| `status` | enum `status` | ✅ |
| `pageStatus` | enum `pageStatus` | — |
| `sourceRecordIds` | idRefArray → SourceRecord | — |
| `verifiedAt` | datetime | — |
| `lastUpdated` | datetime | ✅ |
| `verificationStatus` | enum `verificationStatus` | ✅ |
| `notes` | text | — |

---

## 3. Enumerations

| Enum | Values |
|---|---|
| `status` | `active` · `inactive` · `deprecated` · `draft` |
| `pageStatus` | `database-only` · `draft` · `basic-profile` · `active-hub` · `archived` · `redirected` |
| `verificationStatus` | `verified` · `partially_verified` · `unverified` · `historical` · `archived` · `disputed` |
| `regionType` | `geographic` · `sports_governance` · `commercial_market` |
| `adminLevel` | `state` · `province` · `territory` · `region` · `department` · `prefecture` · `county` · `other` |
| `competitionType` | `league` · `cup` · `tournament` · `friendly` · `exhibition` · `qualifier` |
| `teamType` | `club` · `franchise` · `national` · `territorial` · `representative` |
| `eventStatus` | `scheduled` · `postponed` · `rescheduled` · `live` · `completed` · `abandoned` · `cancelled` |
| `ticketStatus` | `not_on_sale` · `on_sale` · `limited` · `sold_out` · `resale_only` · `not_applicable` · `unknown` |
| `participantRole` | `home` · `away` · `neutral` |
| `providerClassification` | `official` · `authorized` · `affiliate` · `secondary_marketplace` · `informational` · `prohibited` |
| `ticketProviderCategory` | `primary_sale` · `resale` · `hospitality` · `package` · `box_office` |
| `travelProviderCategory` | `hotel` · `flight` · `rail` · `transfer` · `parking` · `car_rental` · `tour` · `esim` · `insurance` · `city_pass` |
| `merchandiseProviderCategory` | `kit` · `apparel` · `collectible` · `memorabilia` · `print` · `accessory` |
| `advertiserStatus` | `prospect` · `active` · `paused` · `ended` |
| `placementType` | `city_sponsor` · `venue_sponsor` · `event_sponsor` · `featured_local_listing` · `recommended_provider` · `affiliate_cta` · `merchandise_placement` · `newsletter_placement` |
| `placementStatus` | `draft` · `scheduled` · `active` · `paused` · `ended` |
| `articleType` | `report` · `guide` · `opinion` · `memoriam` · `archive` · `explainer` |
| `sourceType` | `official_site` · `governing_body` · `press_release` · `news_article` · `wire_service` · `broadcast` · `book` · `dataset` · `direct_communication` |
| `authorityLevel` | `official` · `primary` · `secondary` · `aggregator` · `community` |

**`pageStatus` governs indexability, not merely whether a page exists.** Full rules in [DATA-PUBLISHING-POLICY.md](DATA-PUBLISHING-POLICY.md) §3.

| Value | Public? | Indexable? | Meaning |
|---|---|---|---|
| `database-only` | No | No | Record exists; no public page |
| `draft` | No | No | Page exists but is unfinished |
| `basic-profile` | Yes | **No — `noindex` by default** | Thin page below the indexation threshold |
| `active-hub` | Yes | Yes | Meets the indexation threshold |
| `archived` | Yes | Yes | Kept live and indexable, no longer updated |
| `redirected` | Yes | n/a | Resolves but points elsewhere |

**`pageStatus: redirected`** models pages that still resolve but point elsewhere — the condition found on eight stale root-level city duplicates during repository inspection.

**`ticketStatus` is independent of `eventStatus`** and must never be inferred from it. A completed event may still be `resale_only`; a scheduled event may be `not_on_sale` for months.

---

## 4. Geography

### Region

**Purpose.** A named context grouping countries or territories. Deliberately **not** limited to sports confederations — a Region may be a geographic area, a sports-governance body, or a commercial market. The same country belongs to several Regions of different types simultaneously, and which one applies depends on the question being asked.

**ID:** `region:{key}` · **Slug scope:** `per-entityType`

**Required:** FACTUAL_BASE required fields, plus `regionType`.
**Optional:** FACTUAL_BASE optional fields, plus `parentRegionId`, `governingBodyName`.

**Relationships:** `parentRegionId` → Region (many-to-one, optional, self-nesting).

**Status values:** `status` from `status`; `pageStatus` from `pageStatus`.

**Verification:** `governingBodyName` gated at `primary`.

**Commercial:** not placement-targetable. No capability flags. Regions are navigational.

**Constraints**
- `parentRegionId`, when present, must reference a Region of the same `regionType`.
- A Region may not be its own ancestor.

```json
// EXAMPLE — NOT DATA
{
  "id": "region:example-governance-body",
  "slug": "example-governance-body",
  "name": "Example Governance Region",
  "regionType": "sports_governance",
  "status": "active",
  "pageStatus": "database-only",
  "lastUpdated": "2026-01-01T00:00:00Z",
  "verificationStatus": "unverified"
}
```

---

### CountryOrTerritory

**Purpose.** A sovereign state or a dependent, autonomous or disputed territory. Territories are modelled here rather than in a separate entity so that teams and competitions representing them need no special case.

**ID:** `country:{key}` · **Slug scope:** `per-entityType`

**Required:** FACTUAL_BASE required fields, plus `isTerritory`.
**Optional:** FACTUAL_BASE optional fields, plus `iso3166Alpha2`, `iso3166Alpha3`, `sovereigntyNote`, `regionIds`, `flagAssetRef`.

**Relationships:** `regionIds` → Region (many-to-many). Membership context is read from the referenced `Region.regionType` — the country does not restate it.

**Verification:** `sovereigntyNote` gated at `official`. Sovereignty is contested in real cases and must be sourced, never asserted editorially.

**Commercial:** placement-targetable. No capability flags.

**Constraints**
- `iso3166Alpha2` is optional; some territories and historical entities have none.
- `isTerritory: true` requires `sovereigntyNote`.
- `regionIds` should not contain two Regions of the same `regionType` unless one is an ancestor of the other.

```json
// EXAMPLE — NOT DATA
{
  "id": "country:example-country",
  "slug": "example-country",
  "name": "Example Country",
  "isTerritory": false,
  "regionIds": ["region:example-geographic", "region:example-governance-body"],
  "status": "active",
  "pageStatus": "database-only",
  "lastUpdated": "2026-01-01T00:00:00Z",
  "verificationStatus": "unverified"
}
```

---

### AdministrativeRegion

**Purpose.** A civil subdivision — state, province, department, prefecture. Sits between CountryOrTerritory and City and is **optional in the chain**: a City may attach directly to a country.

**ID:** `adminregion:{key}` · **Slug scope:** `per-country`

**Required:** FACTUAL_BASE required fields, plus `countryOrTerritoryId`, `adminLevel`.
**Optional:** FACTUAL_BASE optional fields, plus `iso3166_2`, `parentAdministrativeRegionId`.

**Relationships:** `countryOrTerritoryId` → CountryOrTerritory (many-to-one, required); `parentAdministrativeRegionId` → AdministrativeRegion (many-to-one, optional).

**Verification:** no gated fields.

**Commercial:** not placement-targetable.

**Constraints**
- `parentAdministrativeRegionId` must belong to the same `countryOrTerritoryId`.
- May not be its own ancestor.

```json
// EXAMPLE — NOT DATA
{
  "id": "adminregion:example-state",
  "slug": "example-state",
  "name": "Example State",
  "countryOrTerritoryId": "country:example-country",
  "adminLevel": "state",
  "status": "active",
  "pageStatus": "database-only",
  "lastUpdated": "2026-01-01T00:00:00Z",
  "verificationStatus": "unverified"
}
```

---

### City

**Purpose.** A populated place hosting venues, events and local commerce. The primary geographic unit for fan-travel content and the main target for city-level sponsorship.

**ID:** `city:{key}` · **Slug scope:** `per-country`

**Required:** FACTUAL_BASE required fields, plus `countryOrTerritoryId`.
**Optional:** FACTUAL_BASE optional fields, plus `administrativeRegionId`, `timezone`, `latitude`, `longitude`, `metroName`, `newsletterTopic`, `monetizationEnabled`.

**Relationships:** `countryOrTerritoryId` → CountryOrTerritory (required); `administrativeRegionId` → AdministrativeRegion (optional).

**Verification:** `latitude`, `longitude`, `timezone` gated at `secondary`.

**Commercial:** placement-targetable. Flags: `monetizationEnabled`, `newsletterTopic`.

**Constraints**
- `administrativeRegionId`, when present, must belong to `countryOrTerritoryId`.
- `latitude` and `longitude` supplied together or not at all.

```json
// EXAMPLE — NOT DATA
{
  "id": "city:example-city",
  "slug": "example-city",
  "name": "Example City",
  "countryOrTerritoryId": "country:example-country",
  "administrativeRegionId": "adminregion:example-state",
  "status": "active",
  "pageStatus": "database-only",
  "monetizationEnabled": true,
  "lastUpdated": "2026-01-01T00:00:00Z",
  "verificationStatus": "unverified"
}
```

---

### Venue

**Purpose.** A physical place where events are staged. **Venue names change** with naming-rights agreements, so name history is first-class: the current `officialName` is one entry in a dated series, not a standalone fact. Modelling it any other way silently rewrites history every time a sponsor changes.

**ID:** `venue:{key}` · **Slug scope:** `per-city`

**Required:** FACTUAL_BASE required fields, plus `cityId`.
**Optional:** FACTUAL_BASE optional fields, plus `officialName`, `nameHistory`, `capacity`, `capacityAsOf`, `surface`, `isIndoor`, `openedYear`, `latitude`, `longitude`, `schemaOrgType` (default `StadiumOrArena`), `monetizationEnabled`.

**`nameHistory` item shape**

| Field | Type | Required |
|---|---|---|
| `name` | string | ✅ |
| `startDate` | date | — |
| `endDate` | date | — |
| `isNamingRightsDeal` | boolean | — |
| `namingRightsPartner` | string | — |
| `sourceRecordIds` | idRefArray → SourceRecord | — |

**Relationships:** `cityId` → City (many-to-one, required).

**Verification:** `officialName`, `capacity`, `openedYear`, `surface` gated at `official`.

> Capacity and official name must not render as fact without a source at `official` or `primary`. Both change; an unsourced value is a liability, not a detail.

**Commercial:** placement-targetable. Flag: `monetizationEnabled`.

**Constraints**
- `capacity` requires `capacityAsOf`.
- At most one `nameHistory` entry may have no `endDate`; it must match `officialName`.
- `nameHistory` entries must not overlap in date range.
- `namingRightsPartner` requires `isNamingRightsDeal: true`.

```json
// EXAMPLE — NOT DATA
{
  "id": "venue:example-venue",
  "slug": "example-venue",
  "name": "Example Venue",
  "cityId": "city:example-city",
  "officialName": null,
  "capacity": null,
  "nameHistory": [],
  "schemaOrgType": "StadiumOrArena",
  "status": "active",
  "pageStatus": "database-only",
  "lastUpdated": "2026-01-01T00:00:00Z",
  "verificationStatus": "unverified",
  "notes": "officialName and capacity intentionally null pending an official source."
}
```

---

## 5. Sports

### Sport

**Purpose.** A sport discipline. The top of the sporting hierarchy and the axis on which SportDGX expands beyond soccer.

**ID:** `sport:{key}` · **Slug scope:** `per-entityType`

**Required:** FACTUAL_BASE required fields.
**Optional:** FACTUAL_BASE optional fields, plus `governingBodyName`, `newsletterTopic`.

**Relationships:** none.

**Verification:** `governingBodyName` gated at `primary`.

**Commercial:** not placement-targetable. Flag: `newsletterTopic`.

```json
// EXAMPLE — NOT DATA
{
  "id": "sport:example-sport",
  "slug": "example-sport",
  "name": "Example Sport",
  "status": "active",
  "pageStatus": "database-only",
  "lastUpdated": "2026-01-01T00:00:00Z",
  "verificationStatus": "unverified"
}
```

---

### Competition

**Purpose.** A recurring or one-off contest within a sport. A Competition may sit under **several governance bodies and span several geographies at once**, so governance context and geographic context are separate many-to-many links rather than a single parent.

**ID:** `competition:{key}` · **Slug scope:** `per-sport`

**Required:** FACTUAL_BASE required fields, plus `sportId`, `competitionType`.
**Optional:** FACTUAL_BASE optional fields, plus `organizerName`, `governanceRegionIds`, `geographicRegionIds`, `countryOrTerritoryIds`, `gender`, `tier`, `newsletterTopic`, `monetizationEnabled`.

**Relationships**
- `sportId` → Sport (many-to-one, required)
- `governanceRegionIds` → Region (many-to-many) — must be `regionType: sports_governance`
- `geographicRegionIds` → Region (many-to-many) — must be `regionType: geographic`
- `countryOrTerritoryIds` → CountryOrTerritory (many-to-many)

**Verification:** `organizerName`, `tier` gated at `official`.

**Commercial:** placement-targetable. Flags: `monetizationEnabled`, `newsletterTopic`.

**Constraints**
- `governanceRegionIds` must reference Regions with `regionType: sports_governance`.
- `geographicRegionIds` must reference Regions with `regionType: geographic`.

```json
// EXAMPLE — NOT DATA
{
  "id": "competition:example-competition",
  "slug": "example-competition",
  "name": "Example Competition",
  "sportId": "sport:example-sport",
  "competitionType": "league",
  "governanceRegionIds": ["region:example-governance-body"],
  "geographicRegionIds": ["region:example-geographic"],
  "status": "active",
  "pageStatus": "database-only",
  "lastUpdated": "2026-01-01T00:00:00Z",
  "verificationStatus": "unverified"
}
```

---

### SeasonOrEdition

**Purpose.** One instance of a Competition — a league season (`2025-26`) or a tournament edition (`2026`). Carries hosting geography, which can differ from the Competition's own geography.

**ID:** `season:{key}` · **Slug scope:** `per-competition`

**Required:** FACTUAL_BASE required fields, plus `competitionId`, `label`.
**Optional:** FACTUAL_BASE optional fields, plus `startDate`, `endDate`, `hostCountryOrTerritoryIds`, `hostCityIds`, `isCurrent`.

**Relationships:** `competitionId` → Competition (required); `hostCountryOrTerritoryIds` → CountryOrTerritory; `hostCityIds` → City.

**Verification:** `startDate`, `endDate` gated at `official`.

**Commercial:** placement-targetable. No capability flags.

**Constraints**
- `endDate` must not precede `startDate`.
- At most one SeasonOrEdition per `competitionId` may have `isCurrent: true`.
- `label` unique within `competitionId`.

```json
// EXAMPLE — NOT DATA
{
  "id": "season:example-season",
  "slug": "example-season",
  "name": "Example Competition — Example Season",
  "competitionId": "competition:example-competition",
  "label": "0000",
  "isCurrent": false,
  "status": "active",
  "pageStatus": "database-only",
  "lastUpdated": "2026-01-01T00:00:00Z",
  "verificationStatus": "unverified"
}
```

---

### Event

**Purpose.** A single scheduled contest. Supports **one or more venues** (relocations, multi-site events), **any number of participants**, **explicit neutral-site designation**, and a **ticket status that moves independently** of the fixture status.

**ID:** `event:{key}` · **Slug scope:** `per-season`

**Required:** FACTUAL_BASE required fields, plus `competitionId`, `sportId`, `seasonOrEditionId`, `eventStatus`.
**Optional:** FACTUAL_BASE optional fields, plus `venueIds`, `cityIds`, `startsAt`, `endsAt`, `startTimeConfirmed`, `stage`, `isNeutralSite`, `ticketStatus`, `participants`, `resultSummary`, `monetizationEnabled`.

**`participants` item shape**

| Field | Type | Required |
|---|---|---|
| `teamId` | idRef → Team | ✅ |
| `role` | enum `participantRole` | ✅ |
| `score` | integer ≥ 0 | — |
| `isWinner` | boolean | — |
| `resultNote` | string | — |

**Relationships:** `competitionId` → Competition; `sportId` → Sport; `seasonOrEditionId` → SeasonOrEdition (all required, many-to-one). `venueIds` → Venue and `cityIds` → City (many-to-many). `participants[].teamId` → Team (many-to-many).

**Verification:** `startsAt`, `endsAt`, `participants`, `resultSummary` gated at `official`.

> Kickoff times are the single most volatile field in the model. `startTimeConfirmed: false` means the time may render only as provisional.

**Commercial:** placement-targetable. Flag: `monetizationEnabled`.

**Constraints**
- `sportId` must equal the `sportId` of the referenced Competition.
- `seasonOrEditionId` must reference a SeasonOrEdition whose `competitionId` matches this Event.
- `ticketStatus` is independent of `eventStatus` and must not be inferred from it.
- `eventStatus: completed` requires either `resultSummary` or scores on participants.
- `isNeutralSite: true` forbids `home` and `away` roles on the same Event.
- `endsAt` must not precede `startsAt`.
- A `teamId` may appear at most once per Event.

```json
// EXAMPLE — NOT DATA
{
  "id": "event:example-event",
  "slug": "example-event",
  "name": "Example Event",
  "competitionId": "competition:example-competition",
  "sportId": "sport:example-sport",
  "seasonOrEditionId": "season:example-season",
  "venueIds": ["venue:example-venue"],
  "eventStatus": "scheduled",
  "ticketStatus": "unknown",
  "startTimeConfirmed": false,
  "isNeutralSite": false,
  "participants": [],
  "status": "active",
  "pageStatus": "database-only",
  "lastUpdated": "2026-01-01T00:00:00Z",
  "verificationStatus": "unverified",
  "notes": "startsAt intentionally absent pending an official source."
}
```

---

### Team

**Purpose.** A competing side. **Not every team belongs to a city.** National, territorial and representative sides represent a country or territory; franchises relocate; some sides represent a region rather than any single place. Geography is therefore optional and expressed through an explicit `represents` reference.

**ID:** `team:{key}` · **Slug scope:** `per-sport`

**Required:** FACTUAL_BASE required fields, plus `sportId`, `teamType`.
**Optional:** FACTUAL_BASE optional fields, plus `representsEntityType`, `representsEntityId`, `cityId`, `countryOrTerritoryId`, `homeVenueIds`, `competitionIds`, `foundedYear`, `colors`, `newsletterTopic`, `monetizationEnabled`.

**`teamType` semantics**

| Value | Meaning |
|---|---|
| `club` | Member-owned or independent side, typically city-based |
| `franchise` | Licensed side that may relocate between cities |
| `national` | Represents a sovereign state |
| `territorial` | Represents a dependent, autonomous or disputed territory |
| `representative` | Select or invitational side representing a region or body |

`representsEntityType` allows `CountryOrTerritory`, `AdministrativeRegion`, `City`, `Region`.

**Relationships:** `sportId` → Sport (required); polymorphic `represents` (optional); `cityId` → City (optional); `countryOrTerritoryId` → CountryOrTerritory (optional); `homeVenueIds` → Venue; `competitionIds` → Competition.

**Verification:** `foundedYear`, `homeVenueIds` gated at `primary`.

**Commercial:** placement-targetable. Flags: `monetizationEnabled`, `newsletterTopic`.

**Constraints**
- `representsEntityType` and `representsEntityId` supplied together or not at all.
- `teamType` `national` or `territorial` requires `representsEntityType: CountryOrTerritory`.
- `teamType` `club` or `franchise` **should** carry `cityId`, but it is not required — relocations and unresolved cases exist.
- Referenced `competitionIds` must share this Team's `sportId`.

```json
// EXAMPLE — NOT DATA
{
  "id": "team:example-team",
  "slug": "example-team",
  "name": "Example Team",
  "sportId": "sport:example-sport",
  "teamType": "franchise",
  "cityId": "city:example-city",
  "competitionIds": ["competition:example-competition"],
  "status": "active",
  "pageStatus": "database-only",
  "lastUpdated": "2026-01-01T00:00:00Z",
  "verificationStatus": "unverified"
}
```

---

## 6. Commercial and distribution

The three provider types stay separate for now, but share **one classification vocabulary** so a future merge into a single `Provider` entity with a discriminator remains cheap.

> **`classification` defaults to `informational` and must be set deliberately.**
> The presence of a link anywhere in the repository is never evidence of approval.

### TicketProvider

**Purpose.** An organisation through which event tickets are obtained. Separate from the other providers because ticketing carries distinct legal and editorial policy.

**ID:** `ticketprovider:{key}` · **Slug scope:** `per-entityType`

**Required:** PROVIDER_BASE required fields, plus `resaleAllowed`.
**Optional:** PROVIDER_BASE optional fields, plus `providerCategories` (from `ticketProviderCategory`).

**Relationships:** `geoScopeCountryIds` → CountryOrTerritory.

**Verification:** `classification` gated at `official`.

**Commercial:** not placement-targetable; **is** a placement source. Flags: `disclosureRequired`, `resaleAllowed`.

**Constraints**
- `classification: prohibited` forbids use in any CommercialPlacement.
- `classification: secondary_marketplace` requires `resaleAllowed: true` and a `policyNote`.
- `classification: affiliate` requires `affiliateNetwork` and `disclosureRequired: true`.

```json
// EXAMPLE — NOT DATA
{
  "id": "ticketprovider:example-provider",
  "slug": "example-provider",
  "name": "Example Ticket Provider",
  "classification": "informational",
  "resaleAllowed": false,
  "disclosureRequired": true,
  "status": "draft",
  "lastUpdated": "2026-01-01T00:00:00Z",
  "verificationStatus": "unverified"
}
```

---

### TravelProvider

**Purpose.** An organisation supplying travel products around an event or city — accommodation, flights, transfers, parking, passes, connectivity.

**ID:** `travelprovider:{key}` · **Slug scope:** `per-entityType`

**Required:** PROVIDER_BASE required fields, plus `providerCategories` (from `travelProviderCategory`).
**Optional:** PROVIDER_BASE optional fields.

**Relationships:** `geoScopeCountryIds` → CountryOrTerritory.

**Verification:** `classification` gated at `primary`.

**Commercial:** not placement-targetable; is a placement source. Flag: `disclosureRequired`.

**Constraints**
- `classification: prohibited` forbids use in any CommercialPlacement.
- `classification: affiliate` requires `affiliateNetwork` and `disclosureRequired: true`.
- `providerCategories` must contain at least one value.

```json
// EXAMPLE — NOT DATA
{
  "id": "travelprovider:example-travel",
  "slug": "example-travel",
  "name": "Example Travel Provider",
  "classification": "informational",
  "providerCategories": ["hotel"],
  "disclosureRequired": true,
  "status": "draft",
  "lastUpdated": "2026-01-01T00:00:00Z",
  "verificationStatus": "unverified"
}
```

---

### MerchandiseProvider

**Purpose.** An organisation supplying goods — kit, apparel, collectibles, prints. Licensing claims are verification-gated: *official merchandise* is a factual assertion, not a marketing phrase.

**ID:** `merchprovider:{key}` · **Slug scope:** `per-entityType`

**Required:** PROVIDER_BASE required fields, plus `providerCategories` (from `merchandiseProviderCategory`).
**Optional:** PROVIDER_BASE optional fields, plus `licensingNote`, `isOfficiallyLicensed`.

**Relationships:** `geoScopeCountryIds` → CountryOrTerritory.

**Verification:** `classification`, `isOfficiallyLicensed` gated at `official`.

**Commercial:** not placement-targetable; is a placement source. Flags: `disclosureRequired`, `isOfficiallyLicensed`.

**Constraints**
- `classification: prohibited` forbids use in any CommercialPlacement.
- `isOfficiallyLicensed: true` requires `licensingNote` and a source at `authorityLevel: official`.
- `providerCategories` must contain at least one value.

```json
// EXAMPLE — NOT DATA
{
  "id": "merchprovider:example-merch",
  "slug": "example-merch",
  "name": "Example Merchandise Provider",
  "classification": "informational",
  "providerCategories": ["apparel"],
  "isOfficiallyLicensed": false,
  "disclosureRequired": true,
  "status": "draft",
  "lastUpdated": "2026-01-01T00:00:00Z",
  "verificationStatus": "unverified"
}
```

---

### Advertiser

**Purpose.** A paying commercial party, as distinct from an affiliate provider. Holds **no** contact details, contract terms or credentials — those live outside the repository.

**ID:** `advertiser:{key}` · **Slug scope:** `per-entityType`

**Required:** `id`, `slug`, `name`, `advertiserStatus`, `disclosureLabelDefault`, `status`, `lastUpdated`.
**Optional:** `legalName`, `industry`, `externalContactRef`, `notes`.

**Relationships:** none.

**Verification:** none. Advertiser records are contractual, not factual, and carry no `verificationStatus`.

**Commercial:** not placement-targetable; is a placement source.

**Constraints**
- `externalContactRef` must be an opaque reference — never an email address, phone number or credential.
- `disclosureLabelDefault` must be non-empty.

```json
// EXAMPLE — NOT DATA
{
  "id": "advertiser:example-advertiser",
  "slug": "example-advertiser",
  "name": "Example Advertiser",
  "advertiserStatus": "prospect",
  "disclosureLabelDefault": "Sponsored",
  "status": "draft",
  "lastUpdated": "2026-01-01T00:00:00Z"
}
```

---

### CommercialPlacement

**Purpose.** The join between a commercial party and a place on the site. **All monetisation is expressed here** rather than as fields scattered across factual entities, so inventory can be listed, dated and audited in one place.

**ID:** `placement:{key}` · **Slug scope:** none (no public page)

**Required:** `id`, `placementType`, `position`, `status`, `requiresDisclosure`, `lastUpdated`.
**Optional:** `targetEntityType`, `targetEntityId`, `pagePath`, `advertiserId`, `providerEntityType`, `providerEntityId`, `startsAt`, `endsAt`, `disclosureLabel`, `creativeRef`, `priority`, `notes`.

**Targeting.** A placement resolves either to an entity (`targetEntityType` + `targetEntityId`) or to a page (`pagePath`). `targetEntityType` allows exactly the entities whose descriptors declare `commercial.placementTargetable: true`: CountryOrTerritory, City, Venue, Competition, SeasonOrEdition, Event, Team, Article. Region, AdministrativeRegion and Sport are navigational and are deliberately excluded.

**Commercial source.** Exactly one of:
- `advertiserId` → Advertiser — a paying placement, or
- `providerEntityType` + `providerEntityId` → TicketProvider | TravelProvider | MerchandiseProvider — an affiliate or recommendation placement.

Separating these matters because they carry different disclosure obligations and different legal exposure.

**Verification:** none.

**Constraints**
- Must resolve to a target: entity reference **or** `pagePath`.
- `targetEntityType` and `targetEntityId` supplied together or not at all.
- Exactly one commercial source — not both, not neither.
- `providerEntityType` and `providerEntityId` supplied together or not at all.
- `requiresDisclosure: true` requires a non-empty `disclosureLabel`.
- A provider whose `classification` is `prohibited` is invalid here.
- `endsAt` must not precede `startsAt`.
- `status: active` requires the current time to fall inside `startsAt..endsAt` when either is set.
- `targetEntityType` must name an entity whose descriptor has `commercial.placementTargetable: true`.

```json
// EXAMPLE — NOT DATA
{
  "id": "placement:example-placement",
  "placementType": "city_sponsor",
  "targetEntityType": "City",
  "targetEntityId": "city:example-city",
  "position": "example-slot",
  "advertiserId": "advertiser:example-advertiser",
  "status": "draft",
  "requiresDisclosure": true,
  "disclosureLabel": "Sponsored",
  "priority": 0,
  "lastUpdated": "2026-01-01T00:00:00Z"
}
```

---

### Article

**Purpose.** An editorial page. Links narrative content to the entities it covers and to the sources behind it.

`monetizationEnabled` is an **editorial decision recorded as data**, not the incidental absence of placements. The repository already contains a page that must never carry advertising; encoding that as a boolean is what lets it survive future automation.

**ID:** `article:{key}` · **Slug scope:** `per-entityType`

**Required:** FACTUAL_BASE required fields, plus `articleType`, `pagePath`, `monetizationEnabled`.
**Optional:** FACTUAL_BASE optional fields, plus `publishedAt`, `updatedAt`, `authorName`, `displayTitle`, `entityRefs`, `isOpinion`.

**`entityRefs` item shape**

| Field | Type | Required |
|---|---|---|
| `entityType` | polyRefType | ✅ |
| `entityId` | polyRefId | ✅ |
| `relation` | string | — |

**Relationships:** `entityRefs[]` polymorphic (many-to-many); `sourceRecordIds` → SourceRecord (many-to-many).

**Verification:** `articleType: report` should carry at least one `sourceRecordId`. `articleType: opinion` must set `isOpinion: true`.

**Commercial:** placement-targetable. Flag: `monetizationEnabled`.

**Constraints**
- `monetizationEnabled: false` forbids any CommercialPlacement targeting this Article or its `pagePath`.
- `articleType: opinion` requires `isOpinion: true`.
- `articleType: memoriam` defaults `monetizationEnabled` to `false`.
- `pagePath` unique across Articles.
- `name` holds the canonical headline; `displayTitle` overrides it for rendering only.

```json
// EXAMPLE — NOT DATA
{
  "id": "article:example-article",
  "slug": "example-article",
  "name": "Example Article Headline",
  "articleType": "guide",
  "pagePath": "/articles/example-article.html",
  "monetizationEnabled": true,
  "isOpinion": false,
  "entityRefs": [
    { "entityType": "City", "entityId": "city:example-city", "relation": "about" }
  ],
  "status": "draft",
  "pageStatus": "draft",
  "lastUpdated": "2026-01-01T00:00:00Z",
  "verificationStatus": "unverified"
}
```

---

### SourceRecord

**Purpose.** A citation. Every changing fact points at one or more of these, so a claim can always be traced to where it came from and when it was read.

**ID:** `source:{key}` · **Slug scope:** none

**Required:** `id`, `sourceType`, `publisher`, `title`, `accessedAt`, `authorityLevel`.
**Optional:** `url`, `publishedAt`, `notes`.

**Relationships:** none outbound. Referenced by `sourceRecordIds` on factual entities, providers and `nameHistory` entries.

**Verification:** a SourceRecord is the evidence; it is not itself verification-gated.

**Constraints**
- `sourceType` `official_site` or `governing_body` implies `authorityLevel` `official` or `primary`.
- `accessedAt` must not precede `publishedAt`.
- `url` is optional so offline sources (books, direct communication) remain expressible.

```json
// EXAMPLE — NOT DATA
{
  "id": "source:example-source",
  "sourceType": "official_site",
  "publisher": "Example Publisher",
  "title": "Example Source Title",
  "accessedAt": "2026-01-01T00:00:00Z",
  "authorityLevel": "official"
}
```

---

### NewsletterSignupSource

**Purpose.** Describes where a newsletter signup originated, so topic and consent context travel with the signup. **Descriptor only** — no provider integration, and no personal data is modelled here.

**ID:** `nlsource:{key}` · **Primary key field is `sourceId`, not `id`** · **Slug scope:** none

**Required:** `sourceId`, `pagePath`, `consentTextVersion`, `status`, `lastUpdated`.
**Optional:** `entityType`, `entityId`, `campaign`, `topic`, `notes`.

**Relationships:** polymorphic `entityType` + `entityId` (many-to-one, optional).

**Verification:** none.

**Constraints**
- Primary key is `sourceId` — a deliberate deviation, see [§9](#9-documented-deviations).
- `entityType` and `entityId` supplied together or not at all.
- `consentTextVersion` is an opaque version identifier, never the consent text itself.
- **This entity must never hold an email address or any other personal data.**

```json
// EXAMPLE — NOT DATA
{
  "sourceId": "nlsource:example-signup-source",
  "pagePath": "/example-page.html",
  "entityType": "City",
  "entityId": "city:example-city",
  "topic": "example-topic",
  "consentTextVersion": "v0",
  "status": "draft",
  "lastUpdated": "2026-01-01T00:00:00Z"
}
```

---

## 7. Relationship summary

```
Region ──parentRegionId──▶ Region                    (self-nesting, same regionType)
   ▲
   │ regionIds (many-to-many, context from Region.regionType)
   │
CountryOrTerritory ◀── countryOrTerritoryId ── AdministrativeRegion
   ▲                                                   │
   │ countryOrTerritoryId                               │ administrativeRegionId
   │                                                    ▼
   └──────────────────────────────────────────────▶ City ──cityId──▶ Venue

Sport ──sportId──▶ Competition ──competitionId──▶ SeasonOrEdition
  │                    │  │                              │
  │                    │  └─ governanceRegionIds ─▶ Region (sports_governance)
  │                    └──── geographicRegionIds ─▶ Region (geographic)
  │                          countryOrTerritoryIds ─▶ CountryOrTerritory
  │                                                     │
  │                                        seasonOrEditionId
  │                                                     ▼
  ├──────────────── sportId ──────────────────────▶ Event
  │                                                  │  │  │
  │                                        venueIds ─┘  │  └─ cityIds ─▶ City
  │                                             ▼       ▼
  │                                          Venue   participants[].teamId
  │                                                       │
  └──sportId──▶ Team ◀────────────────────────────────────┘
                 │ represents (polymorphic): CountryOrTerritory | AdministrativeRegion | City | Region
                 │ cityId, countryOrTerritoryId, homeVenueIds, competitionIds — all optional

CommercialPlacement ──target (polymorphic)──▶ any entity with placementTargetable: true
        │
        ├── advertiserId ──▶ Advertiser                       ┐ exactly
        └── provider (polymorphic) ──▶ TicketProvider         │  one
                                       TravelProvider         │  of
                                       MerchandiseProvider    ┘ these

Article ──entityRefs[] (polymorphic)──▶ any entity
   │
   └──sourceRecordIds──▶ SourceRecord ◀── sourceRecordIds ── all factual entities,
                                           providers, Venue.nameHistory[]

NewsletterSignupSource ──entityType + entityId (polymorphic)──▶ any entity
```

**Placement-targetable entities:** CountryOrTerritory, City, Venue, Competition, SeasonOrEdition, Event, Team, Article.
**Not targetable:** Region, AdministrativeRegion, Sport, all providers, Advertiser, CommercialPlacement, SourceRecord, NewsletterSignupSource.

---

## 8. Global validation rules

Declared in `entities.js` as `GLOBAL_RULES`. No validator is implemented yet.

| Rule | Severity | Description |
|---|---|---|
| `unique-id` | error | Every `id` is unique across the whole dataset, not merely within its entity type |
| `id-prefix-match` | error | Every `id` matches its descriptor's `idPattern` |
| `unique-slug` | error | Slugs unique within the scope named by `slugScope` |
| `slug-format` | error | Lowercase `a-z`, `0-9`, hyphens; no leading, trailing or repeated hyphens |
| `fk-resolves` | error | Every `idRef` / `idRefArray` resolves to an existing record of the declared target type |
| `poly-ref-paired` | error | Polymorphic type and id supplied together; type is in `allowedTypes` |
| `required-present` | error | Every required field is present and non-empty |
| `enum-valid` | error | Every enum value is a member of the referenced set |
| `page-status-valid` | error | `pageStatus` valid; `basic-profile`, `active-hub`, `archived` and `redirected` each require a resolvable page path |
| `indexation-threshold` | error | `active-hub` requires the indexable-page minimums in DATA-PUBLISHING-POLICY.md; `basic-profile` is noindex by default |
| `source-provenance` | error | Every changing factual record carries ≥1 SourceRecord with publisher, sourceType, accessedAt and authorityLevel |
| `licensing-resolved` | error | No record with unresolved licensing may reach `basic-profile`, `active-hub` or `archived` |
| `verification-valid` | error | `verificationStatus` is a member of the enum |
| `provider-class-valid` | error | Provider `classification` is valid and was set explicitly |
| `placement-resolves` | error | Every placement resolves to a target and exactly one commercial source |
| `prohibited-unused` | error | No placement references a provider classified `prohibited` |
| `disclosure-present` | error | `requiresDisclosure: true` implies a non-empty `disclosureLabel` |
| `no-monetized-optout` | error | No placement targets an entity whose `monetizationEnabled` is `false` |
| `gated-field-sourced` | error | A populated gated field has a SourceRecord at or above `minAuthorityForGated` |
| `no-orphans` | warn | Records reachable from nothing and carrying `pageStatus: database-only` are reported |
| `date-order` | error | Paired date/datetime fields are chronological |
| `entity-constraints` | error | Every rule in an entity descriptor's `constraints` array holds |

---

## 9. Documented deviations

Three places where this contract departs from the uniform pattern, each deliberate:

1. **`NewsletterSignupSource.sourceId`** is the primary key instead of `id`. Kept to match the field name in the approved specification. A validator must special-case it.
2. **`SourceRecord.title`** instead of `name`, and SourceRecord carries no `slug`, `status` or `pageStatus`. It is a citation record, never a page.
3. **`Article.name`** holds the canonical headline; `displayTitle` is a render-time override. Article uses `name` rather than `title` so it stays inside FACTUAL_BASE and needs no special handling.

`Advertiser` also omits `verificationStatus` — it is a contractual record, not a factual claim about the world.

---

## Unresolved modeling decisions

Carried forward for a later phase; none blocks the next step.

1. **Region membership metadata.** `CountryOrTerritory.regionIds` is a flat array, so *when* a country joined a confederation cannot be expressed. If confederation-change history matters, this becomes a join record with dates.
2. **Team identity across relocation and rename.** `nameHistory` exists on Venue but not on Team. A relocated franchise currently overwrites `cityId`, losing the prior city.
3. **Person entity.** Players, coaches and officials are absent. Nothing in the current site needs them, but scorer lines in match reports are person-shaped data with no home.
4. **Event grouping.** Doubleheaders, multi-leg ties and tournament groups have no container. `stage` is a free string, which will not sustain bracket rendering.
5. **Currency and price.** No monetary type is defined. Any future ticket or product pricing needs currency, amount, validity window and source, and should not be added ad hoc.
6. **Provider merge.** The three provider types share `PROVIDER_BASE` and one classification vocabulary. Whether they should become one `Provider` entity with a discriminator is deferred until real records exist.
7. **`data/cities.json`.** Tracked, empty, predates this work. Left untouched. Worth understanding why a prior data layer stalled before committing to this one.
