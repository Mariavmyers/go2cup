# SportDGX — Data, Publishing and Rights Policy

**Version:** 0.1.0
**Status:** Policy. Binding on every future dataset, template and page.
**Related:** [ENTITIES.md](ENTITIES.md) · [REPOSITORIES.md](REPOSITORIES.md)

Governs where data may come from, how it must be attributed, when a page may be indexed, and what may be shown. These rules exist to keep SportDGX defensible as it scales from one tournament archive to many sports.

Where this document and any other architecture document disagree, **this one wins on sourcing, licensing, indexation and rights.**

---

## Contents

1. [Current stack](#1-current-stack)
2. [Data sourcing and licensing](#2-data-sourcing-and-licensing)
3. [Static-first rendering](#3-static-first-rendering)
4. [Publishing and indexation](#4-publishing-and-indexation)
5. [Trademarks, logos and official marks](#5-trademarks-logos-and-official-marks)
6. [MVP completion criteria](#6-mvp-completion-criteria)

---

## 1. Current stack

The reality of this repository as of schema version 0.1.0. Any proposal that assumes otherwise is wrong until this section is updated.

| Property | State |
|---|---|
| Site type | Static HTML |
| Hosting | GitHub Pages, apex domain `sportdgx.com` via `CNAME` |
| Jekyll | **Active** — no `.nojekyll` present, so `_`-prefixed paths are excluded from the build |
| Framework | None |
| CMS | None |
| Live database | None |
| Server runtime | None |
| `package.json` | None — Node therefore treats `.js` as CommonJS |
| Build pipeline | None in production |
| Dependencies | None |
| Crawler posture | `robots.txt` allows all, and explicitly names GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended, Applebot-Extended, CCBot, Bytespider, Amazonbot |

Precedent worth noting: `assets/tw.css` was produced by a build run **outside** the repository and the output committed. That pattern — generate offline, commit the artefact — is the sanctioned way to add generation without introducing a production build pipeline.

**No framework migration is proposed in this phase.**

---

## 2. Data sourcing and licensing

### 2.1 Required provenance

Every dataset record whose facts can change must carry provenance through `sourceRecordIds` → `SourceRecord`. Each `SourceRecord` records:

| Requirement | `SourceRecord` field |
|---|---|
| Source name | `publisher` |
| Source URL | `url` (optional — offline sources stay expressible) |
| Source type | `sourceType` |
| Access / verification date | `accessedAt`, plus `verifiedAt` on the entity |
| Authority classification | `authorityLevel` |
| Licensing / terms status | `notes`, until a dedicated field is justified by real records |

Classification uses the existing `authorityLevel` vocabulary — `official` · `primary` · `secondary` · `aggregator` · `community` — which covers the official / authorized / licensed / public-domain / editorial / secondary distinction. Where a source is licensed or public-domain, that status is stated explicitly in `notes` together with the licence name.

`ENTITIES.md` already gates volatile fields: `Venue.capacity`, `Venue.officialName`, `Event.startsAt` and any price may not render as fact without a source at `official` or `primary`.

### 2.2 Permitted sources

Prefer, in order: **official APIs · official publications · licensed feeds · clearly permitted public sources · original editorial work.**

### 2.3 Prohibited

- **Do not scrape** a site whose terms prohibit scraping or automated reuse.
- **Do not treat publicly visible data as licensed.** Visibility is not permission. Commercial republication needs a positive right.
- **Do not depend on undocumented endpoints** in production. They are unstable and their use is rarely authorised.
- **Do not copy** protected ticket inventory, pricing feeds, schedules, images or databases without permission or a valid right of use. Schedules and fixture databases attract database rights in several jurisdictions even where individual facts do not.
- **Do not publish an unresolved licensing question.** Flag it and hold the record at `database-only` or `draft`.

### 2.4 Enforcement

Two schema rules carry this policy — declared in `entities.js` `GLOBAL_RULES`, unimplemented until the validator phase:

- `source-provenance` — every changing factual record carries ≥1 complete `SourceRecord`
- `licensing-resolved` — no record with unresolved licensing may reach `basic-profile`, `active-hub` or `archived`

---

## 3. Static-first rendering

SportDGX is **data-driven, reusable, storage-agnostic and static-first.**

It is **not** dependent on a live database, and must never become so as a condition of rendering public content.

### 3.1 Rules

1. Structured data may live in local files now, and in a CMS or database later. Both are valid.
2. **Public entity pages are generated or authored as crawlable HTML.** The HTML carries the content.
3. JavaScript may enhance filtering, sorting, placement rotation and interaction.
4. **Primary content must never depend on client-side rendering.** A page whose main content only appears after JS execution is a defect.
5. Storage may migrate without page logic changing — that is what the repository abstraction buys.

### 3.2 Why this is non-negotiable here

`robots.txt` deliberately invites GPTBot, ClaudeBot, PerplexityBot and others. Those crawlers do not reliably execute JavaScript. A JS-rendered entity page is invisible to precisely the audience the site has gone out of its way to court — and the AEO position the World Cup archive already holds would be lost.

### 3.3 The sanctioned generation pattern

Run a generator locally against the data layer, commit the emitted HTML. No production build pipeline, no server runtime, no GitHub Pages change. Same shape as `assets/tw.css`.

The runtime repository layer in `assets/sdgx/` is **progressive enhancement**, not the delivery mechanism for primary content.

---

## 4. Publishing and indexation

### 4.1 Page states

The `pageStatus` enum in `entities.js` is the machine-readable form of this table.

| State | Public? | Indexable? | Meaning |
|---|---|---|---|
| `database-only` | **No** | No | Record exists; no public page |
| `draft` | **No** | No | Page exists but is unfinished |
| `basic-profile` | Yes | **No — `noindex` by default** | Thin page below the indexation threshold |
| `active-hub` | Yes | Yes | Meets the threshold in §4.3 |
| `archived` | Yes | Yes | Kept live and indexable, no longer updated |
| `redirected` | Yes | n/a | Resolves but points elsewhere |

### 4.2 Rules

- `database-only` and `draft` records are **not public**.
- Thin or incomplete pages are **not indexed**.
- A page becomes indexable only when it offers substantial unique value.
- **Reusable templates must not emit large volumes of near-duplicate pages.** Template reuse is for structure, never for bulk.
- **No doorway pages** targeting minor keyword variations.
- Every indexable page carries meaningful original or independently compiled content appropriate to its entity.
- A `basic-profile` page uses `noindex` until it clears §4.3. Promotion is deliberate, never automatic on record creation.

### 4.3 Indexation threshold

A page may move to `active-hub` only when it has, where relevant to the entity:

- [ ] Verified entity summary
- [ ] Useful event or venue information
- [ ] Original editorial context — not a restated data dump
- [ ] Source attribution
- [ ] Visible updated date
- [ ] Meaningful internal links
- [ ] Travel, access, ticket or commercial utility
- [ ] **No empty sections and no fake placeholders**

"Where relevant" is a judgement about the entity type, not a licence to skip. A venue page with no access information has not met the bar.

### 4.4 The failure mode this prevents

Programmatic SEO fails when a template plus a dataset emits thousands of pages that each restate a row. That is a doorway-page pattern, it is what search engines penalise, and it would put the existing archive's standing at risk. **The data layer makes pages cheap to produce; this policy is what stops that being the problem.**

---

## 5. Trademarks, logos and official marks

### 5.1 Permitted

- Team, league, competition, tournament and venue **names** used **editorially and accurately** — nominative reference to identify what is being discussed.
- Original photography and original visual assets.
- Neutral text labels in place of marks.
- Country flags via the existing FlagCDN convention, consistent with `CLAUDE.md`.

### 5.2 Prohibited

- **Do not use** official logos, crests, badges, mascots, proprietary artwork, tournament marks or branded graphics without permission, a valid licence, or a clearly documented lawful basis.
- **Do not imitate** official league, team, FIFA, NFL, Olympics or venue branding — including colourways, typography and layout that read as official.
- **Do not imply** endorsement, partnership, accreditation, authorisation or official status.
- **Do not recreate** a logo as an original asset to evade licensing. A redrawn crest is still the mark.

### 5.3 Required

- Where a licensed mark is unavailable, use a neutral text label or an original asset.
- **Record the rights source for every non-original image or logo** — licence name, holder, scope and expiry where applicable.
- Keep the existing independence disclaimer on every page carrying entity content.

### 5.4 Existing precedent

`CLAUDE.md` already requires FlagCDN images and forbids recreating logos, and `SITE_MAP.md` already forbids claiming official status or unconfirmed partnerships. This section generalises those rules from the World Cup archive to every sport, and adds the rights-source record.

---

## 6. MVP completion criteria

The first full validation of this architecture remains **one Kansas City Chiefs vertical slice**.

**Not to be built now.** These are completion criteria only, recorded so the slice is judged against a fixed bar rather than a moving one.

### 6.1 Required records

Reusable records across all ten entity types: `Region`, `CountryOrTerritory`, `AdministrativeRegion`, `City`, `Venue`, `Sport`, `Competition`, `SeasonOrEdition`, `Team`, `Event`.

"Reusable" means each record is shaped so a second team, city or sport can be added without redesigning it. A slice that only works for one team has validated nothing.

### 6.2 Required pages

- [ ] One useful **team** page
- [ ] One useful **venue** page
- [ ] One useful **city** page
- [ ] One useful **event** page
- [ ] One **ticket-intent** page

"Useful" is measured against the §4.3 indexation threshold.

### 6.3 Required qualities

- [ ] Source and verification records for every changing fact
- [ ] Crawlable static content — §3 satisfied, not JS-rendered
- [ ] Valid structured data **only where factually supported** — no schema for unverified fields
- [ ] Mobile usability
- [ ] Accessibility: semantic HTML, keyboard navigation, visible focus states, descriptive labels, accessible forms
- [ ] Affiliate disclosures on every monetised surface
- [ ] Newsletter source tracking wired through `NewsletterSignupSource`

### 6.4 Absolute constraints

- [ ] **No regression to the World Cup archive** — it is complete, live and off-limits except for verified bugs
- [ ] **No invented data** — unknown stays absent, never estimated
- [ ] **No unlicensed logos** — §5 applies fully

### 6.5 Venue naming caution

The Chiefs' home venue carries naming-rights exposure. `Venue.nameHistory` exists precisely for this. The venue's official name must be sourced at `authorityLevel: official` before it renders as fact — no name is asserted from memory.

---

## Open questions

Not blocking, recorded so they are not rediscovered later.

1. **Dedicated licensing fields.** Licensing status currently rides in `SourceRecord.notes`. Once real licensed feeds exist, a structured `licence` / `licenceUrl` / `permittedUse` group is probably warranted — deferred until real records justify the shape.
2. **Rights records for images.** §5.3 requires recording a rights source for non-original imagery, but no entity models an image asset. Whether that becomes a `MediaAsset` entity or an extension of `SourceRecord` is unresolved.
3. **`noindex` mechanics on GitHub Pages.** Per-page `<meta name="robots" content="noindex">` is the only mechanism available without server headers. Sufficient, but it must be emitted by the template rather than added by hand.
4. **Archive vs active-hub for the World Cup pages.** The existing archive would map to `archived`, but those pages predate this model and carry no entity records. Retrofitting is optional and explicitly out of scope.
