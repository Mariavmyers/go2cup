/**
 * SportDGX — Declarative query filter
 * ------------------------------------------------------------------
 * Version: 0.1.0
 *
 * Filters are DATA, never predicate functions.
 *
 * A closure cannot be translated into SQL, a PostgREST querystring or a
 * CMS query, so accepting one would permanently commit every backend to
 * "load the whole table and filter in memory". This descriptor maps onto
 * all three, and onto an in-memory scan for the local-file adapter.
 *
 *   {
 *     where:   { sportId: 'sport:x',
 *                status:  { op: 'in', value: ['active', 'draft'] } },
 *     orderBy: [{ field: 'name', dir: 'asc' }],
 *     limit:   20,
 *     offset:  0
 *   }
 *
 * A bare value is shorthand for { op: 'eq', value }.
 *
 * Browser- and Node-compatible ES module. Zero dependencies.
 */

import { InvalidFilterError } from './errors.js';

/** Supported comparison operators. Additive: new ones may be appended. */
export const OPERATORS = Object.freeze([
  'eq', 'neq', 'in', 'nin', 'contains', 'gt', 'gte', 'lt', 'lte', 'exists',
]);

/** Operators whose `value` must be an array. */
const ARRAY_VALUE_OPS = Object.freeze(['in', 'nin']);

const SORT_DIRECTIONS = Object.freeze(['asc', 'desc']);

const isPlainObject = (v) =>
  v !== null && typeof v === 'object' && !Array.isArray(v);

/* ------------------------------------------------------------------ *
 * NORMALISATION AND VALIDATION
 * ------------------------------------------------------------------ */

/**
 * Expand shorthand into canonical { op, value } form.
 * @param {unknown} condition
 * @returns {{op: string, value: unknown}}
 */
function normaliseCondition(condition) {
  if (isPlainObject(condition) && typeof condition.op === 'string') {
    return { op: condition.op, value: condition.value };
  }
  return { op: 'eq', value: condition };
}

/**
 * Validate a filter descriptor and return it in canonical form.
 *
 * @param {object} [filter]
 * @param {{knownFields?: Set<string>, entityType?: string}} [context]
 *        knownFields, when supplied, makes an unknown field name an error
 *        rather than a silently empty result.
 * @returns {{where: Record<string, {op: string, value: unknown}>,
 *            orderBy: Array<{field: string, dir: string}>,
 *            limit: number|null, offset: number}}
 * @throws {InvalidFilterError}
 */
export function normaliseFilter(filter = {}, context = {}) {
  const { knownFields = null, entityType = null } = context;
  const details = entityType ? { entityType } : {};

  if (typeof filter === 'function') {
    throw new InvalidFilterError(
      'a predicate function was supplied. Filters must be declarative data so ' +
      'they can be pushed down to a database later. Use ' +
      '{ where: { field: value } } instead.',
      details,
    );
  }
  if (!isPlainObject(filter)) {
    throw new InvalidFilterError('filter must be a plain object.', details);
  }

  for (const key of Object.keys(filter)) {
    if (!['where', 'orderBy', 'limit', 'offset'].includes(key)) {
      throw new InvalidFilterError(
        `unknown filter key "${key}". Supported: where, orderBy, limit, offset.`,
        details,
      );
    }
  }

  /* -- where -- */
  const rawWhere = filter.where ?? {};
  if (!isPlainObject(rawWhere)) {
    throw new InvalidFilterError('where must be a plain object.', details);
  }
  const where = {};
  for (const [field, rawCondition] of Object.entries(rawWhere)) {
    if (knownFields && !knownFields.has(field)) {
      throw new InvalidFilterError(
        `unknown field "${field}"` +
        (entityType ? ` on entity type "${entityType}"` : '') + '.',
        details,
      );
    }
    const condition = normaliseCondition(rawCondition);
    if (!OPERATORS.includes(condition.op)) {
      throw new InvalidFilterError(
        `unsupported operator "${condition.op}" on field "${field}". ` +
        `Supported: ${OPERATORS.join(', ')}.`,
        details,
      );
    }
    if (ARRAY_VALUE_OPS.includes(condition.op) && !Array.isArray(condition.value)) {
      throw new InvalidFilterError(
        `operator "${condition.op}" on field "${field}" requires an array value.`,
        details,
      );
    }
    if (condition.op === 'exists' && typeof condition.value !== 'boolean') {
      throw new InvalidFilterError(
        `operator "exists" on field "${field}" requires a boolean value.`,
        details,
      );
    }
    where[field] = condition;
  }

  /* -- orderBy -- */
  const rawOrderBy = filter.orderBy ?? [];
  const orderByList = Array.isArray(rawOrderBy) ? rawOrderBy : [rawOrderBy];
  const orderBy = orderByList.map((entry) => {
    const spec = typeof entry === 'string' ? { field: entry } : entry;
    if (!isPlainObject(spec) || typeof spec.field !== 'string') {
      throw new InvalidFilterError(
        'each orderBy entry must be a field name or { field, dir }.', details,
      );
    }
    const dir = spec.dir ?? 'asc';
    if (!SORT_DIRECTIONS.includes(dir)) {
      throw new InvalidFilterError(
        `orderBy dir must be "asc" or "desc", received "${dir}".`, details,
      );
    }
    if (knownFields && !knownFields.has(spec.field)) {
      throw new InvalidFilterError(
        `orderBy references unknown field "${spec.field}"` +
        (entityType ? ` on entity type "${entityType}"` : '') + '.',
        details,
      );
    }
    return { field: spec.field, dir };
  });

  /* -- limit / offset -- */
  const limit = filter.limit ?? null;
  if (limit !== null && (!Number.isInteger(limit) || limit < 0)) {
    throw new InvalidFilterError('limit must be a non-negative integer.', details);
  }
  const offset = filter.offset ?? 0;
  if (!Number.isInteger(offset) || offset < 0) {
    throw new InvalidFilterError('offset must be a non-negative integer.', details);
  }

  return { where, orderBy, limit, offset };
}

/* ------------------------------------------------------------------ *
 * IN-MEMORY EVALUATION
 * Used by adapters that cannot push a query down to their backend.
 * ------------------------------------------------------------------ */

/** Chronological/lexical comparison with nulls sorted last. */
export function compareValues(a, b) {
  const aNil = a === null || a === undefined;
  const bNil = b === null || b === undefined;
  if (aNil && bNil) return 0;
  if (aNil) return 1;
  if (bNil) return -1;
  if (typeof a === 'number' && typeof b === 'number') return a - b;
  if (typeof a === 'boolean' && typeof b === 'boolean') {
    return (a ? 1 : 0) - (b ? 1 : 0);
  }
  return String(a).localeCompare(String(b));
}

/**
 * Test one record field against one canonical condition.
 * @returns {boolean}
 */
export function matchCondition(recordValue, condition) {
  const { op, value } = condition;
  switch (op) {
    case 'eq':  return recordValue === value;
    case 'neq': return recordValue !== value;
    case 'in':  return value.includes(recordValue);
    case 'nin': return !value.includes(recordValue);
    case 'contains':
      if (Array.isArray(recordValue)) return recordValue.includes(value);
      if (typeof recordValue === 'string' && typeof value === 'string') {
        return recordValue.includes(value);
      }
      return false;
    case 'gt':  return compareValues(recordValue, value) > 0;
    case 'gte': return compareValues(recordValue, value) >= 0;
    case 'lt':  return compareValues(recordValue, value) < 0;
    case 'lte': return compareValues(recordValue, value) <= 0;
    case 'exists': {
      const present = recordValue !== undefined && recordValue !== null;
      return present === value;
    }
    default:
      // normaliseFilter rejects unknown operators before this point.
      throw new InvalidFilterError(`unsupported operator "${op}".`);
  }
}

/** Test a whole record against a canonical `where` map. Conditions are ANDed. */
export function matchRecord(record, where) {
  for (const [field, condition] of Object.entries(where)) {
    if (!matchCondition(record?.[field], condition)) return false;
  }
  return true;
}

/**
 * Apply a canonical filter to an in-memory array.
 * Does not mutate the input.
 *
 * @param {object[]} records
 * @param {ReturnType<typeof normaliseFilter>} canonicalFilter
 * @returns {object[]}
 */
export function applyFilter(records, canonicalFilter) {
  const { where, orderBy, limit, offset } = canonicalFilter;

  let out = Object.keys(where).length
    ? records.filter((record) => matchRecord(record, where))
    : records.slice();

  if (orderBy.length) {
    out.sort((a, b) => {
      for (const { field, dir } of orderBy) {
        const cmp = compareValues(a?.[field], b?.[field]);
        if (cmp !== 0) return dir === 'desc' ? -cmp : cmp;
      }
      return 0;
    });
  }

  if (offset) out = out.slice(offset);
  if (limit !== null) out = out.slice(0, limit);
  return out;
}

/** Convenience: normalise then apply, in one call. */
export function runQuery(records, filter, context) {
  return applyFilter(records, normaliseFilter(filter, context));
}

export default {
  OPERATORS,
  normaliseFilter,
  compareValues,
  matchCondition,
  matchRecord,
  applyFilter,
  runQuery,
};
