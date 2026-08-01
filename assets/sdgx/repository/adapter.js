/**
 * SportDGX — Adapter contract
 * ------------------------------------------------------------------
 * Version: 0.1.0
 *
 * This is the storage seam. Everything above it (Repository, and one day
 * pages) is written against the five lookup methods; everything below it
 * is backend-specific.
 *
 * An adapter MUST implement:
 *   loadAll(entityType) -> Promise<object[]>
 *
 * An adapter MAY additionally implement any of CAPABILITIES and declare
 * them in `this.capabilities`. Repository delegates to a declared method
 * when present, and otherwise falls back to loadAll + in-memory work.
 *
 * That fallback is the migration path: LocalFileAdapter declares nothing
 * and everything falls back; a SQL adapter declares everything and each
 * operation is pushed down to the backend. Page logic is identical in
 * both cases.
 *
 * Browser- and Node-compatible ES module. Zero dependencies.
 */

import { AdapterCapabilityError } from './errors.js';

/**
 * Operations an adapter may push down to its backend.
 *
 * Signatures, when implemented:
 *   getById(entityType, id)                -> Promise<object|null>
 *   getBySlug(entityType, slug, scope)      -> Promise<object[]>   (all matches)
 *   query(entityType, canonicalFilter)      -> Promise<object[]>
 *   exists(entityType, id)                  -> Promise<boolean>
 *   count(entityType, canonicalFilter)      -> Promise<number>
 *
 * `canonicalFilter` is the output of query.js normaliseFilter — already
 * validated, with shorthand expanded. An adapter translates it; it never
 * has to parse user input.
 */
export const CAPABILITIES = Object.freeze([
  'getById', 'getBySlug', 'query', 'exists', 'count',
]);

/**
 * Base class for storage adapters.
 *
 * Subclasses set `this.capabilities` to a Set drawn from CAPABILITIES and
 * implement the matching methods. Call `assertCapabilityIntegrity()` at the
 * end of the constructor so a typo surfaces at construction rather than at
 * the first query.
 */
export class Adapter {
  /**
   * @param {{name?: string, capabilities?: Iterable<string>}} [options]
   */
  constructor(options = {}) {
    this.name = options.name ?? new.target.name;
    this.capabilities = new Set(options.capabilities ?? []);
  }

  /**
   * Return every record of an entity type.
   * The single required primitive.
   *
   * @param {string} entityType
   * @returns {Promise<object[]>}
   */
  // eslint-disable-next-line no-unused-vars
  async loadAll(entityType) {
    throw new Error(
      `${this.name} does not implement loadAll(entityType). Every adapter must.`,
    );
  }

  /** @param {string} capability @returns {boolean} */
  supports(capability) {
    return this.capabilities.has(capability);
  }

  /**
   * Verify every declared capability has a real method behind it, and that
   * no unknown capability name was declared.
   * @throws {AdapterCapabilityError}
   */
  assertCapabilityIntegrity() {
    for (const capability of this.capabilities) {
      if (!CAPABILITIES.includes(capability)) {
        throw new AdapterCapabilityError(this.name, capability);
      }
      if (typeof this[capability] !== 'function') {
        throw new AdapterCapabilityError(this.name, capability);
      }
    }
    return this;
  }

  /**
   * Optional hook for adapters holding cached state. Repository never calls
   * this; it exists so a caller can force a reload after data changes.
   * @param {string} [entityType] omit to clear everything
   */
  // eslint-disable-next-line no-unused-vars
  invalidate(entityType) { /* no-op by default */ }
}

export default { Adapter, CAPABILITIES };
