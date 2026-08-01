/**
 * SportDGX — Repository registry
 * ------------------------------------------------------------------
 * Version: 0.1.0
 *
 * Binds entity types to repositories over a single adapter. This is the
 * one place a backend swap touches: change the adapter passed here and
 * every caller keeps working, because callers only ever saw the five
 * lookup methods.
 *
 *   const registry = createRegistry({ adapter: new LocalFileAdapter() });
 *   const cities   = registry.get('City');
 *   await cities.getBySlug('example-city', 'country:example-country');
 *
 * Repositories are memoised per entity type. Entity types are validated
 * against schema/entities.js, so a typo fails loudly rather than
 * returning an empty list.
 *
 * Browser- and Node-compatible ES module. Zero dependencies.
 */

import { ENTITIES } from '../schema/entities.js';
import { Repository } from './repository.js';
import { UnknownEntityTypeError, SdgxRepositoryError } from './errors.js';

export class RepositoryRegistry {
  /**
   * @param {{adapter: import('./adapter.js').Adapter, entities?: object}} options
   */
  constructor(options = {}) {
    const { adapter, entities = ENTITIES } = options;
    if (!adapter) throw new SdgxRepositoryError('registry requires an adapter.');
    this.adapter = adapter;
    this.entities = entities;
    this._repositories = new Map();
  }

  /** @returns {string[]} every entity type the schema defines */
  entityTypes() {
    return Object.keys(this.entities);
  }

  /** @param {string} entityType @returns {boolean} */
  has(entityType) {
    return Object.prototype.hasOwnProperty.call(this.entities, entityType);
  }

  /**
   * @param {string} entityType
   * @returns {Repository}
   * @throws {UnknownEntityTypeError}
   */
  get(entityType) {
    if (!this.has(entityType)) {
      throw new UnknownEntityTypeError(entityType, this.entityTypes());
    }
    let repository = this._repositories.get(entityType);
    if (!repository) {
      repository = new Repository(entityType, this.adapter, this.entities[entityType]);
      this._repositories.set(entityType, repository);
    }
    return repository;
  }

  /**
   * Swap the storage backend. The migration seam — one call, no page changes.
   * Memoised repositories are discarded so they rebind to the new adapter.
   *
   * @param {import('./adapter.js').Adapter} adapter
   * @returns {this}
   */
  setAdapter(adapter) {
    if (!adapter) throw new SdgxRepositoryError('setAdapter requires an adapter.');
    this.adapter = adapter;
    this._repositories.clear();
    return this;
  }
}

/**
 * @param {{adapter: import('./adapter.js').Adapter, entities?: object}} options
 * @returns {RepositoryRegistry}
 */
export function createRegistry(options) {
  return new RepositoryRegistry(options);
}

export default { RepositoryRegistry, createRegistry };
