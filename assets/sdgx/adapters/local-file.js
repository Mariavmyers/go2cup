/**
 * SportDGX — Local file adapter
 * ------------------------------------------------------------------
 * Version: 0.1.0
 *
 * Reads entity records from JSON files under /data/, located through a
 * manifest. Declares no capabilities: every operation falls back to
 * loadAll + in-memory work in Repository. That is correct for datasets
 * of this size and keeps the adapter tiny.
 *
 * Manifest format — data/manifest.json:
 *
 *   {
 *     "manifestVersion": "1",
 *     "schemaVersion": "0.1.0",
 *     "datasets": {
 *       "City": { "path": "cities.json", "format": "json-array" }
 *     }
 *   }
 *
 * `path` is resolved relative to the manifest's own directory.
 *
 * No manifest exists yet. Until one does, every call raises
 * ManifestNotFoundError — the correct state, not a bug.
 *
 * KNOWN CONSTRAINTS
 *   - fetch() cannot read file:// URLs in a browser. Opening a page by
 *     double-clicking will fail; serve over HTTP or use the deployed site.
 *     The error message says so rather than surfacing a bare TypeError.
 *   - Base URL is derived from import.meta.url, not hardcoded to /data/,
 *     so the layer works when served from a subpath as well as an apex
 *     domain.
 *
 * Browser- and Node-compatible ES module. Zero dependencies.
 */

import { Adapter } from '../repository/adapter.js';
import {
  ManifestNotFoundError,
  ManifestInvalidError,
  DatasetNotDeclaredError,
  DatasetLoadError,
  DatasetParseError,
} from '../repository/errors.js';

/** This module lives at /assets/sdgx/adapters/, so ../../../data/ is site-root /data/. */
const DEFAULT_DATA_URL = new URL('../../../data/', import.meta.url);

export class LocalFileAdapter extends Adapter {
  /**
   * @param {{baseUrl?: string|URL, manifestFile?: string,
   *          fetchImpl?: typeof fetch, name?: string}} [options]
   */
  constructor(options = {}) {
    super({ name: options.name ?? 'LocalFileAdapter', capabilities: [] });

    this.baseUrl = options.baseUrl ? new URL(String(options.baseUrl), DEFAULT_DATA_URL)
                                   : DEFAULT_DATA_URL;
    this.manifestFile = options.manifestFile ?? 'manifest.json';
    this.manifestUrl = new URL(this.manifestFile, this.baseUrl);

    this._fetch = options.fetchImpl
      ?? (typeof fetch === 'function' ? fetch.bind(globalThis) : null);

    /** In-flight and settled promises, so concurrent callers share one request. */
    this._manifestPromise = null;
    this._datasetPromises = new Map();

    this.assertCapabilityIntegrity();
  }

  /* ---------------------------------------------------------------- *
   * INTERNALS
   * ---------------------------------------------------------------- */

  _assertFetchAvailable(entityType, path) {
    if (this._fetch) return;
    throw new DatasetLoadError(
      entityType, path,
      'no fetch implementation is available in this environment. Pass ' +
      'fetchImpl to the constructor.',
    );
  }

  _fileProtocolHint(url) {
    return String(url).startsWith('file:')
      ? ' (fetch cannot read file:// URLs — serve the site over HTTP)'
      : '';
  }

  /**
   * Fetch and cache the manifest. Concurrent callers share one request:
   * the promise is stored before it is awaited.
   * @returns {Promise<object>}
   */
  loadManifest() {
    if (this._manifestPromise) return this._manifestPromise;

    const url = this.manifestUrl;
    const path = String(url);

    this._manifestPromise = (async () => {
      this._assertFetchAvailable(null, path);

      let response;
      try {
        response = await this._fetch(path, { headers: { accept: 'application/json' } });
      } catch (cause) {
        throw new ManifestInvalidError(
          path,
          `request failed${this._fileProtocolHint(path)}`,
          { cause },
        );
      }

      if (response.status === 404) throw new ManifestNotFoundError(path);
      if (!response.ok) {
        throw new ManifestInvalidError(path, `HTTP ${response.status}`);
      }

      let manifest;
      try {
        manifest = await response.json();
      } catch (cause) {
        throw new ManifestInvalidError(path, 'response is not valid JSON', { cause });
      }

      if (manifest === null || typeof manifest !== 'object' || Array.isArray(manifest)) {
        throw new ManifestInvalidError(path, 'root must be a JSON object');
      }
      if (manifest.datasets === undefined) {
        throw new ManifestInvalidError(path, 'missing required "datasets" key');
      }
      if (manifest.datasets === null || typeof manifest.datasets !== 'object'
          || Array.isArray(manifest.datasets)) {
        throw new ManifestInvalidError(path, '"datasets" must be an object');
      }
      return manifest;
    })();

    // A failed manifest load must not be cached forever; let the next call retry.
    this._manifestPromise.catch(() => { this._manifestPromise = null; });
    return this._manifestPromise;
  }

  /* ---------------------------------------------------------------- *
   * ADAPTER CONTRACT
   * ---------------------------------------------------------------- */

  /**
   * @param {string} entityType
   * @returns {Promise<object[]>}
   */
  loadAll(entityType) {
    const cached = this._datasetPromises.get(entityType);
    if (cached) return cached;

    const promise = (async () => {
      const manifest = await this.loadManifest();
      const manifestPath = String(this.manifestUrl);

      const entry = manifest.datasets[entityType];
      if (!entry) throw new DatasetNotDeclaredError(entityType, manifestPath);
      if (typeof entry.path !== 'string' || !entry.path) {
        throw new ManifestInvalidError(
          manifestPath, `datasets["${entityType}"] has no "path"`, { entityType },
        );
      }

      const url = new URL(entry.path, this.manifestUrl);
      const path = String(url);

      this._assertFetchAvailable(entityType, path);

      let response;
      try {
        response = await this._fetch(path, { headers: { accept: 'application/json' } });
      } catch (cause) {
        throw new DatasetLoadError(
          entityType, path, `request failed${this._fileProtocolHint(path)}`, { cause },
        );
      }
      if (!response.ok) {
        throw new DatasetLoadError(entityType, path, `HTTP ${response.status}`);
      }

      let payload;
      try {
        payload = await response.json();
      } catch (cause) {
        throw new DatasetParseError(entityType, path, 'not valid JSON', { cause });
      }
      if (!Array.isArray(payload)) {
        throw new DatasetParseError(
          entityType, path,
          `expected a JSON array of records, received ${
            payload === null ? 'null' : typeof payload}`,
        );
      }
      return payload;
    })();

    this._datasetPromises.set(entityType, promise);
    promise.catch(() => { this._datasetPromises.delete(entityType); });
    return promise;
  }

  /**
   * Drop cached data so the next call refetches.
   * @param {string} [entityType] omit to clear the manifest and every dataset
   */
  invalidate(entityType) {
    if (entityType === undefined) {
      this._manifestPromise = null;
      this._datasetPromises.clear();
      return;
    }
    this._datasetPromises.delete(entityType);
  }
}

export default { LocalFileAdapter };
