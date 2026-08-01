/**
 * SportDGX — Generic entity repository
 * ------------------------------------------------------------------
 * Version: 0.1.0
 *
 * One implementation serves all 18 entity types. Behaviour is driven by
 * the entity descriptor from schema/entities.js, so adding an entity to
 * the schema is enough — no repository subclass is needed.
 *
 * Lookup contract:
 *   getById(id)                -> record | null
 *   getBySlug(slug, scopeKey?) -> record | null
 *   list(options?)             -> record[]
 *   query(filter)              -> record[]
 *   exists(id)                 -> boolean
 *
 * Absence is not an error. Only infrastructure and programming faults
 * throw; see errors.js.
 *
 * Browser- and Node-compatible ES module. Zero dependencies.
 */

import { normaliseFilter, applyFilter } from './query.js';
import { AmbiguousSlugError, SdgxRepositoryError } from './errors.js';

/**
 * Maps a descriptor `slugScope` to the field holding the scope.
 * `per-entityType` needs no scope field: the slug is already unique.
 */
export const SLUG_SCOPE_FIELDS = Object.freeze({
  'per-country':     'countryOrTerritoryId',
  'per-city':        'cityId',
  'per-sport':       'sportId',
  'per-competition': 'competitionId',
  'per-season':      'seasonOrEditionId',
});

/** Emitted once per entityType+operation so an unintended full scan is visible. */
const fallbackNotices = new Set();

function noticeFallback(entityType, operation, adapterName) {
  const key = `${adapterName}:${entityType}:${operation}`;
  if (fallbackNotices.has(key)) return;
  fallbackNotices.add(key);
  if (typeof console !== 'undefined' && console.debug) {
    console.debug(
      `[sdgx] ${adapterName} cannot push down "${operation}" for ${entityType}; ` +
      `falling back to a full load. Fine for small datasets, worth revisiting ` +
      `for large ones.`,
    );
  }
}

/** Reset fallback notices. Test seam; not used in normal operation. */
export function resetFallbackNotices() {
  fallbackNotices.clear();
}

export class Repository {
  /**
   * @param {string} entityType
   * @param {import('./adapter.js').Adapter} adapter
   * @param {object} descriptor entity descriptor from schema/entities.js
   */
  constructor(entityType, adapter, descriptor) {
    if (!entityType) throw new SdgxRepositoryError('entityType is required.');
    if (!adapter) throw new SdgxRepositoryError('adapter is required.', { entityType });
    if (!descriptor) throw new SdgxRepositoryError('descriptor is required.', { entityType });

    this.entityType = entityType;
    this.adapter = adapter;
    this.descriptor = descriptor;

    const fields = descriptor.fields ?? {};
    this.knownFields = new Set(Object.keys(fields));

    /**
     * Primary key field name. Almost always `id`, but the schema documents
     * one deliberate deviation: NewsletterSignupSource uses `sourceId`.
     * Derived rather than assumed, so the deviation needs no special case.
     */
    this.idField =
      Object.keys(fields).find((name) => fields[name]?.type === 'id') ?? 'id';

    this.slugField = fields.slug ? 'slug' : null;
    this.slugScope = descriptor.slugScope ?? null;
    this.slugScopeField = this.slugScope
      ? (SLUG_SCOPE_FIELDS[this.slugScope] ?? null)
      : null;
  }

  /* ---------------------------------------------------------------- *
   * LOOKUP
   * ---------------------------------------------------------------- */

  /**
   * @param {string} id
   * @returns {Promise<object|null>}
   */
  async getById(id) {
    if (id === undefined || id === null || id === '') return null;

    if (this.adapter.supports('getById')) {
      return (await this.adapter.getById(this.entityType, id)) ?? null;
    }
    noticeFallback(this.entityType, 'getById', this.adapter.name);
    const records = await this.adapter.loadAll(this.entityType);
    return records.find((r) => r?.[this.idField] === id) ?? null;
  }

  /**
   * @param {string} id
   * @returns {Promise<object>}
   * @throws {SdgxRepositoryError} when absent
   */
  async getByIdOrThrow(id) {
    const record = await this.getById(id);
    if (!record) {
      throw new SdgxRepositoryError(
        `No ${this.entityType} with ${this.idField} "${id}".`,
        { entityType: this.entityType },
      );
    }
    return record;
  }

  /**
   * Look a record up by slug.
   *
   * Slug uniqueness is scoped (see descriptor.slugScope). When the entity
   * scopes slugs and no scopeKey is given, a slug matching more than one
   * record raises AmbiguousSlugError rather than returning an arbitrary one.
   *
   * @param {string} slug
   * @param {string} [scopeKey] value of the scope field, e.g. a countryId
   * @returns {Promise<object|null>}
   */
  async getBySlug(slug, scopeKey) {
    if (!this.slugField) {
      throw new SdgxRepositoryError(
        `${this.entityType} has no slug field and cannot be looked up by slug.`,
        { entityType: this.entityType },
      );
    }
    if (slug === undefined || slug === null || slug === '') return null;

    let matches;
    if (this.adapter.supports('getBySlug')) {
      matches = (await this.adapter.getBySlug(this.entityType, slug, scopeKey)) ?? [];
    } else {
      noticeFallback(this.entityType, 'getBySlug', this.adapter.name);
      const records = await this.adapter.loadAll(this.entityType);
      matches = records.filter((r) => r?.[this.slugField] === slug);
      if (scopeKey !== undefined && this.slugScopeField) {
        matches = matches.filter((r) => r?.[this.slugScopeField] === scopeKey);
      }
    }

    if (matches.length === 0) return null;
    if (matches.length === 1) return matches[0];

    throw new AmbiguousSlugError(
      this.entityType, slug, this.slugScopeField ?? '(unscoped)', matches.length,
    );
  }

  /**
   * @param {string} slug
   * @param {string} [scopeKey]
   * @returns {Promise<object>}
   * @throws {SdgxRepositoryError} when absent
   */
  async getBySlugOrThrow(slug, scopeKey) {
    const record = await this.getBySlug(slug, scopeKey);
    if (!record) {
      throw new SdgxRepositoryError(
        `No ${this.entityType} with slug "${slug}"` +
        (scopeKey ? ` in scope "${scopeKey}"` : '') + '.',
        { entityType: this.entityType },
      );
    }
    return record;
  }

  /* ---------------------------------------------------------------- *
   * COLLECTIONS
   * ---------------------------------------------------------------- */

  /**
   * All records, optionally ordered and paged.
   * @param {{orderBy?: unknown, limit?: number, offset?: number}} [options]
   * @returns {Promise<object[]>}
   */
  async list(options = {}) {
    const { orderBy, limit, offset } = options;
    return this.query({ orderBy, limit, offset });
  }

  /**
   * Records matching a declarative filter. See query.js for the grammar.
   * Predicate functions are rejected: they cannot be pushed down to a
   * database later.
   *
   * @param {object} [filter]
   * @returns {Promise<object[]>}
   */
  async query(filter = {}) {
    const canonical = normaliseFilter(filter, {
      knownFields: this.knownFields,
      entityType: this.entityType,
    });

    if (this.adapter.supports('query')) {
      return (await this.adapter.query(this.entityType, canonical)) ?? [];
    }
    noticeFallback(this.entityType, 'query', this.adapter.name);
    const records = await this.adapter.loadAll(this.entityType);
    return applyFilter(records, canonical);
  }

  /**
   * @param {string} id
   * @returns {Promise<boolean>}
   */
  async exists(id) {
    if (id === undefined || id === null || id === '') return false;

    if (this.adapter.supports('exists')) {
      return Boolean(await this.adapter.exists(this.entityType, id));
    }
    return (await this.getById(id)) !== null;
  }

  /**
   * @param {object} [filter]
   * @returns {Promise<number>}
   */
  async count(filter = {}) {
    const canonical = normaliseFilter(filter, {
      knownFields: this.knownFields,
      entityType: this.entityType,
    });

    if (this.adapter.supports('count')) {
      return Number(await this.adapter.count(this.entityType, canonical));
    }
    noticeFallback(this.entityType, 'count', this.adapter.name);
    const records = await this.adapter.loadAll(this.entityType);
    return applyFilter(records, canonical).length;
  }
}

export default { Repository, SLUG_SCOPE_FIELDS, resetFallbackNotices };
