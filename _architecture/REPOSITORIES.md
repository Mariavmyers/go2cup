# SportDGX — Repository Abstraction

**Version:** 0.1.0
**Status:** Interface and local adapter only. No datasets, no fixtures, no validator, no service layer, no renderer.
**Depends on:** [`assets/sdgx/schema/entities.js`](../assets/sdgx/schema/entities.js) · [`ENTITIES.md`](ENTITIES.md)
**Governed by:** [`DATA-PUBLISHING-POLICY.md`](DATA-PUBLISHING-POLICY.md) — sourcing, licensing, static-first, indexation and rights rules override anything here.

The smallest abstraction that lets a page retrieve entities without knowing where they are stored, and lets the storage change later without the page changing.

Nothing in the repository imports this layer yet. It is inert and referenced by zero HTML pages.

---

## Contents

1. [Layers](#1-layers)
2. [Lookup contract](#2-lookup-contract)
3. [Filter grammar](#3-filter-grammar)
4. [Error model](#4-error-model)
5. [Manifest strategy](#5-manifest-strategy)
6. [Adapter contract and extension points](#6-adapter-contract-and-extension-points)
7. [Migration walkthrough](#7-migration-walkthrough)
8. [Constraints and gotchas](#8-constraints-and-gotchas)
9. [Files](#9-files)

---

## 1. Layers

```
schema/entities.js        entity descriptors — drives everything below
        ↓
repository/errors.js      typed faults, importable without cycles
repository/query.js       declarative filter grammar + in-memory evaluator
repository/adapter.js     abstract Adapter + CAPABILITIES  ← the storage seam
        ↓
repository/repository.js  generic Repository: the five lookup methods
repository/registry.js    entityType → Repository binding
        ↓
adapters/local-file.js    LocalFileAdapter (manifest-driven JSON over fetch)
```

One `Repository` implementation serves all 18 entity types. Behaviour comes from the entity descriptor, so adding an entity to the schema is enough — there is no repository subclass to write.

```js
import { createRegistry } from '/assets/sdgx/repository/registry.js';
import { LocalFileAdapter } from '/assets/sdgx/adapters/local-file.js';

const registry = createRegistry({ adapter: new LocalFileAdapter() });
const cities   = registry.get('City');

await cities.getBySlug('example-city', 'country:example-country');
```

---

## 2. Lookup contract

| Method | Returns | Absent |
|---|---|---|
| `getById(id)` | `Promise<object\|null>` | `null` |
| `getBySlug(slug, scopeKey?)` | `Promise<object\|null>` | `null` |
| `list(options?)` | `Promise<object[]>` | `[]` |
| `query(filter)` | `Promise<object[]>` | `[]` |
| `exists(id)` | `Promise<boolean>` | `false` |

Plus `count(filter?)`, `getByIdOrThrow(id)`, `getBySlugOrThrow(slug, scopeKey?)`.

**Absence is not an error.** Only infrastructure and programming faults throw. Folding "not found" into the exception channel forces every call site into a `try/catch` that ends up swallowing real errors alongside benign misses. The `OrThrow` variants exist for call sites where absence genuinely is exceptional.

### Primary key derivation

The key field is read from the descriptor — the field whose type is `id` — rather than assumed to be `id`. This handles the documented deviation in `ENTITIES.md` §9 (`NewsletterSignupSource.sourceId`) with no special case.

### Slug scoping

`ENTITIES.md` scopes slug uniqueness per entity. The repository maps `slugScope` to the field holding the scope:

| `slugScope` | Scope field |
|---|---|
| `per-entityType` | none — the slug is already unique |
| `per-country` | `countryOrTerritoryId` |
| `per-city` | `cityId` |
| `per-sport` | `sportId` |
| `per-competition` | `competitionId` |
| `per-season` | `seasonOrEditionId` |
| `null` | entity has no slug; `getBySlug` throws |

Calling `getBySlug` without a `scopeKey` on a scoped entity is allowed and returns the record **when exactly one matches**. If more than one matches, it raises `AmbiguousSlugError` rather than returning an arbitrary first hit — a silent wrong-record bug is far worse than a loud failure.

---

## 3. Filter grammar

**Filters are data. Predicate functions are rejected.**

This is the load-bearing decision of the whole layer. A closure cannot be translated into SQL, a PostgREST querystring or a CMS query, so accepting one would permanently commit every future backend to *load the whole table and filter in memory* — exactly the lock-in this abstraction exists to prevent. Passing a function raises `InvalidFilterError` with an explanation.

```js
await cities.query({
  where: {
    countryOrTerritoryId: 'country:example-country',   // shorthand for { op: 'eq' }
    status:              { op: 'in', value: ['active', 'draft'] },
    regionIds:           { op: 'contains', value: 'region:example-geographic' },
    lastUpdated:         { op: 'gte', value: '2026-01-01T00:00:00Z' },
  },
  orderBy: [{ field: 'name', dir: 'asc' }],
  limit: 20,
  offset: 0,
});
```

### Operators

| Operator | Meaning |
|---|---|
| `eq` / `neq` | strict equality (default when a bare value is given) |
| `in` / `nin` | membership in an array `value` (array required) |
| `contains` | array field includes `value`; or string field includes substring |
| `gt` `gte` `lt` `lte` | ordered comparison — numbers numerically, others lexically |
| `exists` | field is present and non-null; `value` must be a boolean |

The set is deliberately small and additive. An unsupported operator raises `InvalidFilterError` rather than silently matching nothing.

### Validation

Field names in `where` and `orderBy` are checked against the entity descriptor. A typo raises `InvalidFilterError` instead of returning an empty array that looks like a legitimate "no results".

### Ordering

`orderBy` accepts a field name, an object, or an array of either. Nulls sort last in both directions. Multi-key ordering falls through in the order given.

---

## 4. Error model

```
SdgxRepositoryError                (base — carries entityType and path)
├── ManifestNotFoundError          manifest absent — the expected state today
├── ManifestInvalidError           manifest present but malformed
├── DatasetNotDeclaredError        entityType has no manifest entry
├── DatasetLoadError               network or HTTP failure (wraps cause)
├── DatasetParseError              invalid JSON, or not an array
├── UnknownEntityTypeError         entityType absent from ENTITIES
├── InvalidFilterError             bad operator, unknown field, predicate function
├── AmbiguousSlugError             scoped slug matched more than one record
└── AdapterCapabilityError         adapter declares a capability it lacks
```

Every error names the entity type and, where relevant, the path — so a failure reads as *"Could not load dataset for City from /data/cities.json: HTTP 404"* rather than `TypeError: Failed to fetch`.

`ManifestNotFoundError` says explicitly that a missing manifest is expected until the first dataset is authored. It is a state, not a defect.

---

## 5. Manifest strategy

`data/manifest.json` is the indirection point that lets file layout change without touching code.

```json
{
  "manifestVersion": "1",
  "schemaVersion": "0.1.0",
  "datasets": {
    "City":  { "path": "cities.json",  "format": "json-array" },
    "Venue": { "path": "venues.json",  "format": "json-array" }
  }
}
```

- `path` resolves relative to the **manifest's own directory**, so datasets may be nested or moved without code changes.
- Each dataset file is a JSON array of records. Anything else raises `DatasetParseError`.
- **The manifest does not exist yet.** It belongs with the first dataset, not ahead of it. Until then every call raises `ManifestNotFoundError`, which is the correct runtime state.

### Base URL resolution

Derived from `import.meta.url`, not hardcoded to `/data/`:

```js
new URL('../../../data/', import.meta.url)
```

The module sits at `/assets/sdgx/adapters/`, so three levels up is the site root. This works on the apex domain and equally under a subpath, and is overridable via the `baseUrl` option.

### Caching and in-flight dedupe

The manifest is fetched once; each dataset is fetched once on first access. The cache stores **the pending promise, not the settled value**, so five concurrent `getById` calls trigger one request rather than five. Failed loads are evicted so a later call can retry rather than caching an error forever. `invalidate(entityType?)` clears it.

---

## 6. Adapter contract and extension points

An adapter **must** implement one primitive:

```js
loadAll(entityType) -> Promise<object[]>
```

It **may** additionally implement any of `CAPABILITIES` and declare them in `this.capabilities`:

| Capability | Signature |
|---|---|
| `getById` | `(entityType, id) -> Promise<object\|null>` |
| `getBySlug` | `(entityType, slug, scopeKey) -> Promise<object[]>` — all matches |
| `query` | `(entityType, canonicalFilter) -> Promise<object[]>` |
| `exists` | `(entityType, id) -> Promise<boolean>` |
| `count` | `(entityType, canonicalFilter) -> Promise<number>` |

`Repository` delegates to a declared method when present and otherwise falls back to `loadAll` plus in-memory work. **That fallback is the migration path.**

`canonicalFilter` is the already-validated output of `normaliseFilter` — shorthand expanded, operators checked, fields verified. An adapter translates a known-good structure; it never parses user input.

`assertCapabilityIntegrity()` verifies every declared capability has a real method behind it, so a typo fails at construction rather than at the first query.

`LocalFileAdapter` declares **no** capabilities. Everything falls back, which is correct at this data size. When a fallback happens the repository emits a one-time `console.debug` per entity type and operation, so an unintended full-table scan is visible rather than invisible.

---

## 7. Migration walkthrough

Moving to Postgres, Supabase or a CMS means writing one file and changing one line.

```js
// assets/sdgx/adapters/supabase.js
import { Adapter } from '../repository/adapter.js';

export class SupabaseAdapter extends Adapter {
  constructor(opts) {
    super({ name: 'SupabaseAdapter',
            capabilities: ['getById', 'getBySlug', 'query', 'exists', 'count'] });
    // ...
    this.assertCapabilityIntegrity();
  }

  async getById(entityType, id) { /* pushed down */ }
  async query(entityType, canonicalFilter) { /* descriptor → PostgREST params */ }
  async loadAll(entityType) { /* still required as a fallback */ }
}
```

```js
registry.setAdapter(new SupabaseAdapter({ /* ... */ }));
```

`setAdapter` discards memoised repositories so they rebind. No page logic changes, because pages only ever saw the five methods.

An adapter that implements only `loadAll` still works — it is simply slower. That means a partial migration is viable: ship `loadAll` first, add pushdown capabilities one at a time, and behaviour stays correct throughout.

### A database is optional, not required

Nothing in SportDGX depends on a live database, and nothing may come to depend on one as a condition of rendering public content. The architecture is **data-driven, reusable, storage-agnostic and static-first**.

Local files are a legitimate permanent answer. A CMS or database is a legitimate later answer. The adapter boundary is what makes both true at once — and migrating is a choice, never a prerequisite.

### Static-first is binding

`robots.txt` explicitly invites GPTBot, ClaudeBot, PerplexityBot and others, and those crawlers do not reliably execute JavaScript. **This layer is progressive enhancement, not the delivery mechanism for primary content.**

1. Structured data may live in local files now, and in a CMS or database later.
2. Public entity pages are generated or authored as **crawlable HTML**.
3. JavaScript may enhance filtering, sorting, placement rotation and interaction.
4. **Primary content must never depend on client-side rendering.** A page whose main content appears only after JS execution is a defect.
5. Storage may migrate without page logic changing.

The sanctioned pattern is to run a generator locally against this data layer and commit the emitted HTML — no production build pipeline, no server runtime, exactly as `assets/tw.css` is produced today.

Do not ship a JS-rendered `/events/` index and quietly lose the AEO position the site already holds.

Full rules, including the indexation threshold that governs when a generated page may be indexed at all: [DATA-PUBLISHING-POLICY.md](DATA-PUBLISHING-POLICY.md).

---

## 8. Constraints and gotchas

| Constraint | Detail |
|---|---|
| **`file://` does not work** | `fetch` cannot read `file://` URLs in a browser. Opening a page by double-clicking fails; serve over HTTP or use the deployed site. The error message says so explicitly. |
| **Node cannot `import` these directly** | The repo has no `package.json`, so Node treats `.js` as CommonJS. Future tooling should copy the module tree to a scratch directory with `{"type":"module"}`, or use a `data:` URL for single files. Do **not** add `package.json` to fix this — it changes repo semantics for a tooling-only problem. |
| **Fallback loads whole datasets** | Correct at current size. The one-time `console.debug` makes it visible when it stops being correct. |
| **Filter grammar is small** | Additive by design. A missing operator throws rather than failing silently. |
| **Served publicly** | These modules deploy to sportdgx.com but are imported by zero pages. They are inert. |

---

## 9. Files

| File | Deployed | Purpose |
|---|---|---|
| `_architecture/REPOSITORIES.md` | No | This document |
| `assets/sdgx/repository/errors.js` | Yes | Typed error hierarchy |
| `assets/sdgx/repository/query.js` | Yes | Filter grammar + in-memory evaluator |
| `assets/sdgx/repository/adapter.js` | Yes | Abstract `Adapter` + `CAPABILITIES` |
| `assets/sdgx/repository/repository.js` | Yes | Generic `Repository` |
| `assets/sdgx/repository/registry.js` | Yes | `entityType → Repository` binding |
| `assets/sdgx/adapters/local-file.js` | Yes | Manifest-driven JSON adapter |

**Not created in this phase:** `data/manifest.json`, any dataset, any fixture, any validator, any service layer, any renderer, any production page change.

### Rollback

```
git rm -r --cached assets/sdgx/repository assets/sdgx/adapters _architecture/REPOSITORIES.md
rm -rf assets/sdgx/repository assets/sdgx/adapters _architecture/REPOSITORIES.md
```

Additive only, in new paths, referenced by nothing. The deployed site is byte-identical with or without it.
