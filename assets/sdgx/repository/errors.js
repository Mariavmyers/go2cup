/**
 * SportDGX — Repository error hierarchy
 * ------------------------------------------------------------------
 * Version: 0.1.0
 *
 * Absence is NOT an error. getById/getBySlug return null and
 * list/query return [] when nothing matches. Everything in this file
 * describes an infrastructure or programming fault.
 *
 * Kept in its own module so adapters can import error types without
 * creating a cycle through repository.js.
 *
 * Browser- and Node-compatible ES module. Zero dependencies.
 */

/** Base class for every fault raised by the repository layer. */
export class SdgxRepositoryError extends Error {
  /**
   * @param {string} message
   * @param {{entityType?: string, path?: string, cause?: unknown}} [details]
   */
  constructor(message, details = {}) {
    super(message);
    this.name = new.target.name;
    this.entityType = details.entityType ?? null;
    this.path = details.path ?? null;
    if (details.cause !== undefined) this.cause = details.cause;
    if (Error.captureStackTrace) Error.captureStackTrace(this, new.target);
  }
}

/**
 * The manifest could not be found. This is the expected state until the
 * first dataset is authored — it is not a bug.
 */
export class ManifestNotFoundError extends SdgxRepositoryError {
  constructor(path, details = {}) {
    super(
      `No dataset manifest at "${path}". This is expected until the first ` +
      `dataset is authored. Create it when data exists; see ` +
      `_architecture/REPOSITORIES.md for the format.`,
      { ...details, path },
    );
  }
}

/** The manifest exists but is not usable. */
export class ManifestInvalidError extends SdgxRepositoryError {
  constructor(path, reason, details = {}) {
    super(`Dataset manifest at "${path}" is invalid: ${reason}`, { ...details, path });
    this.reason = reason;
  }
}

/** The manifest loaded, but declares no dataset for this entity type. */
export class DatasetNotDeclaredError extends SdgxRepositoryError {
  constructor(entityType, path, details = {}) {
    super(
      `Manifest at "${path}" declares no dataset for entity type "${entityType}". ` +
      `Add a datasets["${entityType}"] entry, or use an adapter that does not ` +
      `rely on the manifest.`,
      { ...details, entityType, path },
    );
  }
}

/** The dataset could not be retrieved (network, HTTP status, permissions). */
export class DatasetLoadError extends SdgxRepositoryError {
  constructor(entityType, path, reason, details = {}) {
    super(`Could not load dataset for "${entityType}" from "${path}": ${reason}`,
      { ...details, entityType, path });
    this.reason = reason;
  }
}

/** The dataset was retrieved but is not parseable, or is the wrong shape. */
export class DatasetParseError extends SdgxRepositoryError {
  constructor(entityType, path, reason, details = {}) {
    super(`Dataset for "${entityType}" at "${path}" could not be parsed: ${reason}`,
      { ...details, entityType, path });
    this.reason = reason;
  }
}

/** The entity type is absent from the schema in schema/entities.js. */
export class UnknownEntityTypeError extends SdgxRepositoryError {
  constructor(entityType, known = [], details = {}) {
    super(
      `"${entityType}" is not a known entity type.` +
      (known.length ? ` Known types: ${known.join(', ')}.` : ''),
      { ...details, entityType },
    );
    this.knownEntityTypes = known;
  }
}

/** The query filter descriptor is malformed. */
export class InvalidFilterError extends SdgxRepositoryError {
  constructor(reason, details = {}) {
    super(`Invalid query filter: ${reason}`, details);
    this.reason = reason;
  }
}

/**
 * A scoped slug was looked up without a scope key and matched more than
 * one record. Returning an arbitrary match here would be a silent bug.
 */
export class AmbiguousSlugError extends SdgxRepositoryError {
  constructor(entityType, slug, scopeField, matchCount, details = {}) {
    super(
      `Slug "${slug}" matches ${matchCount} ${entityType} records. This entity ` +
      `scopes slugs by "${scopeField}" — pass a scope key to disambiguate.`,
      { ...details, entityType },
    );
    this.slug = slug;
    this.scopeField = scopeField;
    this.matchCount = matchCount;
  }
}

/** An adapter declared a capability it does not actually implement. */
export class AdapterCapabilityError extends SdgxRepositoryError {
  constructor(adapterName, capability, details = {}) {
    super(
      `Adapter "${adapterName}" declares capability "${capability}" but does ` +
      `not implement a method of that name.`,
      details,
    );
    this.adapterName = adapterName;
    this.capability = capability;
  }
}

export default {
  SdgxRepositoryError,
  ManifestNotFoundError,
  ManifestInvalidError,
  DatasetNotDeclaredError,
  DatasetLoadError,
  DatasetParseError,
  UnknownEntityTypeError,
  InvalidFilterError,
  AmbiguousSlugError,
  AdapterCapabilityError,
};
