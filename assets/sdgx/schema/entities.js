/**
 * SportDGX — Canonical Entity Schema Descriptors
 * ------------------------------------------------------------------
 * Version:  0.1.0
 * Status:   CONTRACT ONLY. This file describes fields and validation
 *           rules. It contains no runtime framework, no renderer, no
 *           service layer and no repository adapter.
 *
 * This file is the machine-readable twin of _architecture/ENTITIES.md.
 * The two MUST stay in sync. If you change a field here, change it there.
 *
 * Nothing in the repository imports this file yet. It is inert.
 *
 * Design constraints (from the approved architecture phase):
 *   - Stable IDs. Display names are never foreign keys.
 *   - ISO codes only where the entity genuinely has one.
 *   - Commercial configuration lives in CommercialPlacement and provider
 *     records, NOT duplicated across every factual entity. Entities carry
 *     only the few capability flags that cannot be derived.
 *   - Verification is a first-class field, not a convention.
 *
 * Browser- and Node-compatible ES module. Zero dependencies.
 */

/* ------------------------------------------------------------------ *
 * FIELD TYPES
 * Declarative type tokens consumed by a future validator.
 * ------------------------------------------------------------------ */

export const FIELD_TYPES = Object.freeze({
  ID: 'id',                       // this record's primary key
  ID_REF: 'idRef',                // single foreign key
  ID_REF_ARRAY: 'idRefArray',     // many foreign keys, same target type
  POLY_REF_TYPE: 'polyRefType',   // entityType half of a polymorphic ref
  POLY_REF_ID: 'polyRefId',       // entityId half of a polymorphic ref
  SLUG: 'slug',
  STRING: 'string',
  TEXT: 'text',
  STRING_ARRAY: 'stringArray',
  OBJECT_ARRAY: 'objectArray',
  ENUM: 'enum',
  BOOLEAN: 'boolean',
  INTEGER: 'integer',
  DATE: 'date',                   // YYYY-MM-DD
  DATETIME: 'datetime',           // ISO 8601 with offset
  URL: 'url',
  ISO_3166_1_A2: 'iso3166Alpha2',
  ISO_3166_1_A3: 'iso3166Alpha3',
  ISO_3166_2: 'iso3166_2',
  TIMEZONE: 'timezone',           // IANA, e.g. America/Chicago
});

/* ------------------------------------------------------------------ *
 * ENUMS
 * ------------------------------------------------------------------ */

export const ENUMS = Object.freeze({
  /** Lifecycle of the record itself. */
  status: Object.freeze(['active', 'inactive', 'deprecated', 'draft']),

  /** Whether a public page exists for this entity. */
  pageStatus: Object.freeze([
    'none', 'planned', 'draft', 'published', 'archived', 'redirected',
  ]),

  /** How well sourced the record's factual claims are. */
  verificationStatus: Object.freeze([
    'verified', 'partially_verified', 'unverified',
    'historical', 'archived', 'disputed',
  ]),

  /** A Region is a context, not only a sports confederation. */
  regionType: Object.freeze([
    'geographic', 'sports_governance', 'commercial_market',
  ]),

  adminLevel: Object.freeze([
    'state', 'province', 'territory', 'region',
    'department', 'prefecture', 'county', 'other',
  ]),

  competitionType: Object.freeze([
    'league', 'cup', 'tournament', 'friendly', 'exhibition', 'qualifier',
  ]),

  /** Not every team belongs to a city. */
  teamType: Object.freeze([
    'club', 'franchise', 'national', 'territorial', 'representative',
  ]),

  /** State of the fixture. Kept separate from ticketStatus. */
  eventStatus: Object.freeze([
    'scheduled', 'postponed', 'rescheduled', 'live',
    'completed', 'abandoned', 'cancelled',
  ]),

  /** State of ticket availability. Independent of eventStatus. */
  ticketStatus: Object.freeze([
    'not_on_sale', 'on_sale', 'limited', 'sold_out',
    'resale_only', 'not_applicable', 'unknown',
  ]),

  participantRole: Object.freeze(['home', 'away', 'neutral']),

  /**
   * One classification vocabulary shared by all three provider types.
   * Default is `informational`. The existence of a link in the repository
   * is NEVER evidence of approval — classification is always explicit.
   */
  providerClassification: Object.freeze([
    'official', 'authorized', 'affiliate',
    'secondary_marketplace', 'informational', 'prohibited',
  ]),

  ticketProviderCategory: Object.freeze([
    'primary_sale', 'resale', 'hospitality', 'package', 'box_office',
  ]),

  travelProviderCategory: Object.freeze([
    'hotel', 'flight', 'rail', 'transfer', 'parking',
    'car_rental', 'tour', 'esim', 'insurance', 'city_pass',
  ]),

  merchandiseProviderCategory: Object.freeze([
    'kit', 'apparel', 'collectible', 'memorabilia', 'print', 'accessory',
  ]),

  advertiserStatus: Object.freeze(['prospect', 'active', 'paused', 'ended']),

  placementType: Object.freeze([
    'city_sponsor', 'venue_sponsor', 'event_sponsor',
    'featured_local_listing', 'recommended_provider',
    'affiliate_cta', 'merchandise_placement', 'newsletter_placement',
  ]),

  placementStatus: Object.freeze([
    'draft', 'scheduled', 'active', 'paused', 'ended',
  ]),

  articleType: Object.freeze([
    'report', 'guide', 'opinion', 'memoriam', 'archive', 'explainer',
  ]),

  sourceType: Object.freeze([
    'official_site', 'governing_body', 'press_release', 'news_article',
    'wire_service', 'broadcast', 'book', 'dataset', 'direct_communication',
  ]),

  /** How much weight a source carries when gating factual fields. */
  authorityLevel: Object.freeze([
    'official', 'primary', 'secondary', 'aggregator', 'community',
  ]),
});

/* ------------------------------------------------------------------ *
 * SHARED FIELD GROUPS
 * ------------------------------------------------------------------ */

/** Applied to the ten geography/sport entities and to Article. */
const FACTUAL_BASE = Object.freeze({
  id:                 { type: FIELD_TYPES.ID, required: true },
  slug:               { type: FIELD_TYPES.SLUG, required: true },
  name:               { type: FIELD_TYPES.STRING, required: true, maxLength: 200 },
  shortName:          { type: FIELD_TYPES.STRING, required: false, maxLength: 60 },
  description:        { type: FIELD_TYPES.TEXT, required: false },
  status:             { type: FIELD_TYPES.ENUM, required: true, enum: 'status' },
  pageStatus:         { type: FIELD_TYPES.ENUM, required: true, enum: 'pageStatus' },
  officialSourceUrl:  { type: FIELD_TYPES.URL, required: false },
  sourceRecordIds:    { type: FIELD_TYPES.ID_REF_ARRAY, required: false, target: 'SourceRecord' },
  verifiedAt:         { type: FIELD_TYPES.DATETIME, required: false },
  lastUpdated:        { type: FIELD_TYPES.DATETIME, required: true },
  verificationStatus: { type: FIELD_TYPES.ENUM, required: true, enum: 'verificationStatus' },
  notes:              { type: FIELD_TYPES.TEXT, required: false },
});

/** Applied to TicketProvider, TravelProvider, MerchandiseProvider. */
const PROVIDER_BASE = Object.freeze({
  id:                 { type: FIELD_TYPES.ID, required: true },
  slug:               { type: FIELD_TYPES.SLUG, required: true },
  name:               { type: FIELD_TYPES.STRING, required: true, maxLength: 200 },
  shortName:          { type: FIELD_TYPES.STRING, required: false, maxLength: 60 },
  description:        { type: FIELD_TYPES.TEXT, required: false },
  operatorLegalName:  { type: FIELD_TYPES.STRING, required: false },
  classification:     { type: FIELD_TYPES.ENUM, required: true, enum: 'providerClassification', default: 'informational' },
  url:                { type: FIELD_TYPES.URL, required: false },
  affiliateNetwork:   { type: FIELD_TYPES.STRING, required: false },
  affiliateMarker:    { type: FIELD_TYPES.STRING, required: false },
  disclosureRequired: { type: FIELD_TYPES.BOOLEAN, required: true, default: true },
  appliesToEntityTypes: { type: FIELD_TYPES.STRING_ARRAY, required: false },
  geoScopeCountryIds: { type: FIELD_TYPES.ID_REF_ARRAY, required: false, target: 'CountryOrTerritory' },
  policyNote:         { type: FIELD_TYPES.TEXT, required: false },
  status:             { type: FIELD_TYPES.ENUM, required: true, enum: 'status' },
  pageStatus:         { type: FIELD_TYPES.ENUM, required: false, enum: 'pageStatus' },
  sourceRecordIds:    { type: FIELD_TYPES.ID_REF_ARRAY, required: false, target: 'SourceRecord' },
  verifiedAt:         { type: FIELD_TYPES.DATETIME, required: false },
  lastUpdated:        { type: FIELD_TYPES.DATETIME, required: true },
  verificationStatus: { type: FIELD_TYPES.ENUM, required: true, enum: 'verificationStatus' },
  notes:              { type: FIELD_TYPES.TEXT, required: false },
});

/* ------------------------------------------------------------------ *
 * ENTITY DESCRIPTORS
 * ------------------------------------------------------------------ */

export const ENTITIES = Object.freeze({

  /* ---------------------------------------------------------------- *
   * GEOGRAPHY
   * ---------------------------------------------------------------- */

  Region: Object.freeze({
    entityType: 'Region',
    idPrefix: 'region',
    idPattern: '^region:[a-z0-9][a-z0-9-]*$',
    slugScope: 'per-entityType',
    purpose:
      'A named context that groups countries or territories. Not limited to ' +
      'sports confederations: a Region may be geographic, a sports-governance ' +
      'body, or a commercial market. The same country may belong to several.',
    fields: Object.freeze({
      ...FACTUAL_BASE,
      regionType:     { type: FIELD_TYPES.ENUM, required: true, enum: 'regionType' },
      parentRegionId: { type: FIELD_TYPES.ID_REF, required: false, target: 'Region' },
      governingBodyName: { type: FIELD_TYPES.STRING, required: false },
    }),
    relationships: Object.freeze([
      { name: 'parentRegionId', target: 'Region', cardinality: 'many-to-one', required: false },
    ]),
    verification: Object.freeze({
      gatedFields: Object.freeze(['governingBodyName']),
      minAuthorityForGated: 'primary',
    }),
    commercial: Object.freeze({
      placementTargetable: false,
      capabilityFlags: Object.freeze([]),
    }),
    constraints: Object.freeze([
      'parentRegionId, when present, must reference a Region of the same regionType.',
      'A Region may not be its own ancestor.',
    ]),
  }),

  CountryOrTerritory: Object.freeze({
    entityType: 'CountryOrTerritory',
    idPrefix: 'country',
    idPattern: '^country:[a-z0-9][a-z0-9-]*$',
    slugScope: 'per-entityType',
    purpose:
      'A sovereign state or a dependent/disputed territory. Territories are ' +
      'modelled here rather than in a separate entity so that teams and ' +
      'competitions representing them are expressible without special cases.',
    fields: Object.freeze({
      ...FACTUAL_BASE,
      iso3166Alpha2:   { type: FIELD_TYPES.ISO_3166_1_A2, required: false },
      iso3166Alpha3:   { type: FIELD_TYPES.ISO_3166_1_A3, required: false },
      isTerritory:     { type: FIELD_TYPES.BOOLEAN, required: true, default: false },
      sovereigntyNote: { type: FIELD_TYPES.TEXT, required: false },
      regionIds:       { type: FIELD_TYPES.ID_REF_ARRAY, required: false, target: 'Region' },
      flagAssetRef:    { type: FIELD_TYPES.STRING, required: false },
    }),
    relationships: Object.freeze([
      { name: 'regionIds', target: 'Region', cardinality: 'many-to-many', required: false,
        note: 'Membership context is read from the referenced Region.regionType.' },
    ]),
    verification: Object.freeze({
      gatedFields: Object.freeze(['sovereigntyNote']),
      minAuthorityForGated: 'official',
    }),
    commercial: Object.freeze({
      placementTargetable: true,
      capabilityFlags: Object.freeze([]),
    }),
    constraints: Object.freeze([
      'iso3166Alpha2 is optional: some territories and historical entities have none.',
      'isTerritory true requires sovereigntyNote to be present.',
      'regionIds should not contain two Regions of the same regionType unless one is an ancestor of the other.',
    ]),
  }),

  AdministrativeRegion: Object.freeze({
    entityType: 'AdministrativeRegion',
    idPrefix: 'adminregion',
    idPattern: '^adminregion:[a-z0-9][a-z0-9-]*$',
    slugScope: 'per-country',
    purpose:
      'A first-level (or lower) civil subdivision of a country or territory — ' +
      'state, province, department, prefecture. Sits between CountryOrTerritory ' +
      'and City. Optional in the chain: not every City needs one.',
    fields: Object.freeze({
      ...FACTUAL_BASE,
      countryOrTerritoryId: { type: FIELD_TYPES.ID_REF, required: true, target: 'CountryOrTerritory' },
      adminLevel:  { type: FIELD_TYPES.ENUM, required: true, enum: 'adminLevel' },
      iso3166_2:   { type: FIELD_TYPES.ISO_3166_2, required: false },
      parentAdministrativeRegionId: { type: FIELD_TYPES.ID_REF, required: false, target: 'AdministrativeRegion' },
    }),
    relationships: Object.freeze([
      { name: 'countryOrTerritoryId', target: 'CountryOrTerritory', cardinality: 'many-to-one', required: true },
      { name: 'parentAdministrativeRegionId', target: 'AdministrativeRegion', cardinality: 'many-to-one', required: false },
    ]),
    verification: Object.freeze({
      gatedFields: Object.freeze([]),
      minAuthorityForGated: 'secondary',
    }),
    commercial: Object.freeze({
      placementTargetable: false,
      capabilityFlags: Object.freeze([]),
    }),
    constraints: Object.freeze([
      'parentAdministrativeRegionId must belong to the same countryOrTerritoryId.',
      'An AdministrativeRegion may not be its own ancestor.',
    ]),
  }),

  City: Object.freeze({
    entityType: 'City',
    idPrefix: 'city',
    idPattern: '^city:[a-z0-9][a-z0-9-]*$',
    slugScope: 'per-country',
    purpose:
      'A populated place that hosts venues, events and local commerce. The ' +
      'primary geographic unit for fan-travel content and the main target for ' +
      'city-level sponsorship.',
    fields: Object.freeze({
      ...FACTUAL_BASE,
      countryOrTerritoryId: { type: FIELD_TYPES.ID_REF, required: true, target: 'CountryOrTerritory' },
      administrativeRegionId: { type: FIELD_TYPES.ID_REF, required: false, target: 'AdministrativeRegion' },
      timezone:     { type: FIELD_TYPES.TIMEZONE, required: false },
      latitude:     { type: FIELD_TYPES.STRING, required: false },
      longitude:    { type: FIELD_TYPES.STRING, required: false },
      metroName:    { type: FIELD_TYPES.STRING, required: false },
      newsletterTopic: { type: FIELD_TYPES.STRING, required: false },
      monetizationEnabled: { type: FIELD_TYPES.BOOLEAN, required: false, default: true },
    }),
    relationships: Object.freeze([
      { name: 'countryOrTerritoryId', target: 'CountryOrTerritory', cardinality: 'many-to-one', required: true },
      { name: 'administrativeRegionId', target: 'AdministrativeRegion', cardinality: 'many-to-one', required: false },
    ]),
    verification: Object.freeze({
      gatedFields: Object.freeze(['latitude', 'longitude', 'timezone']),
      minAuthorityForGated: 'secondary',
    }),
    commercial: Object.freeze({
      placementTargetable: true,
      capabilityFlags: Object.freeze(['monetizationEnabled', 'newsletterTopic']),
    }),
    constraints: Object.freeze([
      'administrativeRegionId, when present, must belong to countryOrTerritoryId.',
      'latitude and longitude must be supplied together or not at all.',
    ]),
  }),

  Venue: Object.freeze({
    entityType: 'Venue',
    idPrefix: 'venue',
    idPattern: '^venue:[a-z0-9][a-z0-9-]*$',
    slugScope: 'per-city',
    purpose:
      'A physical place where events are staged. Venue names change with ' +
      'naming-rights agreements, so name history is first-class: the current ' +
      'officialName is one entry in a dated series, not a standalone fact.',
    fields: Object.freeze({
      ...FACTUAL_BASE,
      cityId:       { type: FIELD_TYPES.ID_REF, required: true, target: 'City' },
      officialName: { type: FIELD_TYPES.STRING, required: false },
      nameHistory:  {
        type: FIELD_TYPES.OBJECT_ARRAY, required: false,
        itemShape: Object.freeze({
          name:                { type: FIELD_TYPES.STRING, required: true },
          startDate:           { type: FIELD_TYPES.DATE, required: false },
          endDate:             { type: FIELD_TYPES.DATE, required: false },
          isNamingRightsDeal:  { type: FIELD_TYPES.BOOLEAN, required: false },
          namingRightsPartner: { type: FIELD_TYPES.STRING, required: false },
          sourceRecordIds:     { type: FIELD_TYPES.ID_REF_ARRAY, required: false, target: 'SourceRecord' },
        }),
      },
      capacity:       { type: FIELD_TYPES.INTEGER, required: false, min: 0 },
      capacityAsOf:   { type: FIELD_TYPES.DATE, required: false },
      surface:        { type: FIELD_TYPES.STRING, required: false },
      isIndoor:       { type: FIELD_TYPES.BOOLEAN, required: false },
      openedYear:     { type: FIELD_TYPES.INTEGER, required: false },
      latitude:       { type: FIELD_TYPES.STRING, required: false },
      longitude:      { type: FIELD_TYPES.STRING, required: false },
      schemaOrgType:  { type: FIELD_TYPES.STRING, required: false, default: 'StadiumOrArena' },
      monetizationEnabled: { type: FIELD_TYPES.BOOLEAN, required: false, default: true },
    }),
    relationships: Object.freeze([
      { name: 'cityId', target: 'City', cardinality: 'many-to-one', required: true },
    ]),
    verification: Object.freeze({
      gatedFields: Object.freeze(['officialName', 'capacity', 'openedYear', 'surface']),
      minAuthorityForGated: 'official',
      note:
        'capacity and officialName must not render as fact without a source at ' +
        'authorityLevel official or primary. Naming rights and capacity both ' +
        'change; an unsourced value is a liability, not a detail.',
    }),
    commercial: Object.freeze({
      placementTargetable: true,
      capabilityFlags: Object.freeze(['monetizationEnabled']),
    }),
    constraints: Object.freeze([
      'capacity requires capacityAsOf.',
      'At most one nameHistory entry may have no endDate; it must match officialName.',
      'nameHistory entries must not overlap in date range.',
      'namingRightsPartner requires isNamingRightsDeal true.',
    ]),
  }),

  /* ---------------------------------------------------------------- *
   * SPORTS
   * ---------------------------------------------------------------- */

  Sport: Object.freeze({
    entityType: 'Sport',
    idPrefix: 'sport',
    idPattern: '^sport:[a-z0-9][a-z0-9-]*$',
    slugScope: 'per-entityType',
    purpose:
      'A sport discipline. The top of the sporting hierarchy and the axis on ' +
      'which SportDGX expands beyond soccer.',
    fields: Object.freeze({
      ...FACTUAL_BASE,
      governingBodyName: { type: FIELD_TYPES.STRING, required: false },
      newsletterTopic:   { type: FIELD_TYPES.STRING, required: false },
    }),
    relationships: Object.freeze([]),
    verification: Object.freeze({
      gatedFields: Object.freeze(['governingBodyName']),
      minAuthorityForGated: 'primary',
    }),
    commercial: Object.freeze({
      placementTargetable: false,
      capabilityFlags: Object.freeze(['newsletterTopic']),
    }),
    constraints: Object.freeze([]),
  }),

  Competition: Object.freeze({
    entityType: 'Competition',
    idPrefix: 'competition',
    idPattern: '^competition:[a-z0-9][a-z0-9-]*$',
    slugScope: 'per-sport',
    purpose:
      'A recurring or one-off contest within a sport. A Competition may sit ' +
      'under several governance bodies and span several geographies at once, ' +
      'so governance and geographic context are separate many-to-many links.',
    fields: Object.freeze({
      ...FACTUAL_BASE,
      sportId:              { type: FIELD_TYPES.ID_REF, required: true, target: 'Sport' },
      competitionType:      { type: FIELD_TYPES.ENUM, required: true, enum: 'competitionType' },
      organizerName:        { type: FIELD_TYPES.STRING, required: false },
      governanceRegionIds:  { type: FIELD_TYPES.ID_REF_ARRAY, required: false, target: 'Region' },
      geographicRegionIds:  { type: FIELD_TYPES.ID_REF_ARRAY, required: false, target: 'Region' },
      countryOrTerritoryIds:{ type: FIELD_TYPES.ID_REF_ARRAY, required: false, target: 'CountryOrTerritory' },
      gender:               { type: FIELD_TYPES.STRING, required: false },
      tier:                 { type: FIELD_TYPES.INTEGER, required: false, min: 1 },
      newsletterTopic:      { type: FIELD_TYPES.STRING, required: false },
      monetizationEnabled:  { type: FIELD_TYPES.BOOLEAN, required: false, default: true },
    }),
    relationships: Object.freeze([
      { name: 'sportId', target: 'Sport', cardinality: 'many-to-one', required: true },
      { name: 'governanceRegionIds', target: 'Region', cardinality: 'many-to-many', required: false,
        note: 'Referenced Regions must have regionType sports_governance.' },
      { name: 'geographicRegionIds', target: 'Region', cardinality: 'many-to-many', required: false,
        note: 'Referenced Regions must have regionType geographic.' },
      { name: 'countryOrTerritoryIds', target: 'CountryOrTerritory', cardinality: 'many-to-many', required: false },
    ]),
    verification: Object.freeze({
      gatedFields: Object.freeze(['organizerName', 'tier']),
      minAuthorityForGated: 'official',
    }),
    commercial: Object.freeze({
      placementTargetable: true,
      capabilityFlags: Object.freeze(['monetizationEnabled', 'newsletterTopic']),
    }),
    constraints: Object.freeze([
      'governanceRegionIds must reference Regions with regionType sports_governance.',
      'geographicRegionIds must reference Regions with regionType geographic.',
    ]),
  }),

  SeasonOrEdition: Object.freeze({
    entityType: 'SeasonOrEdition',
    idPrefix: 'season',
    idPattern: '^season:[a-z0-9][a-z0-9-]*$',
    slugScope: 'per-competition',
    purpose:
      'One instance of a Competition — a league season ("2025-26") or a ' +
      'tournament edition ("2026"). Carries the hosting geography, which can ' +
      'differ from the Competition-level geography.',
    fields: Object.freeze({
      ...FACTUAL_BASE,
      competitionId:   { type: FIELD_TYPES.ID_REF, required: true, target: 'Competition' },
      label:           { type: FIELD_TYPES.STRING, required: true },
      startDate:       { type: FIELD_TYPES.DATE, required: false },
      endDate:         { type: FIELD_TYPES.DATE, required: false },
      hostCountryOrTerritoryIds: { type: FIELD_TYPES.ID_REF_ARRAY, required: false, target: 'CountryOrTerritory' },
      hostCityIds:     { type: FIELD_TYPES.ID_REF_ARRAY, required: false, target: 'City' },
      isCurrent:       { type: FIELD_TYPES.BOOLEAN, required: false, default: false },
    }),
    relationships: Object.freeze([
      { name: 'competitionId', target: 'Competition', cardinality: 'many-to-one', required: true },
      { name: 'hostCountryOrTerritoryIds', target: 'CountryOrTerritory', cardinality: 'many-to-many', required: false },
      { name: 'hostCityIds', target: 'City', cardinality: 'many-to-many', required: false },
    ]),
    verification: Object.freeze({
      gatedFields: Object.freeze(['startDate', 'endDate']),
      minAuthorityForGated: 'official',
    }),
    commercial: Object.freeze({
      placementTargetable: true,
      capabilityFlags: Object.freeze([]),
    }),
    constraints: Object.freeze([
      'endDate must not precede startDate.',
      'At most one SeasonOrEdition per competitionId may have isCurrent true.',
      'label must be unique within competitionId.',
    ]),
  }),

  Event: Object.freeze({
    entityType: 'Event',
    idPrefix: 'event',
    idPattern: '^event:[a-z0-9][a-z0-9-]*$',
    slugScope: 'per-season',
    purpose:
      'A single scheduled contest. Supports one or more venues (relocations, ' +
      'multi-site events), any number of participants, explicit neutral-site ' +
      'designation, and a ticket status that moves independently of the ' +
      'fixture status.',
    fields: Object.freeze({
      ...FACTUAL_BASE,
      competitionId:  { type: FIELD_TYPES.ID_REF, required: true, target: 'Competition' },
      sportId:        { type: FIELD_TYPES.ID_REF, required: true, target: 'Sport' },
      seasonOrEditionId: { type: FIELD_TYPES.ID_REF, required: true, target: 'SeasonOrEdition' },
      venueIds:       { type: FIELD_TYPES.ID_REF_ARRAY, required: false, target: 'Venue' },
      cityIds:        { type: FIELD_TYPES.ID_REF_ARRAY, required: false, target: 'City' },
      startsAt:       { type: FIELD_TYPES.DATETIME, required: false },
      endsAt:         { type: FIELD_TYPES.DATETIME, required: false },
      startTimeConfirmed: { type: FIELD_TYPES.BOOLEAN, required: false, default: false },
      stage:          { type: FIELD_TYPES.STRING, required: false },
      isNeutralSite:  { type: FIELD_TYPES.BOOLEAN, required: false, default: false },
      eventStatus:    { type: FIELD_TYPES.ENUM, required: true, enum: 'eventStatus' },
      ticketStatus:   { type: FIELD_TYPES.ENUM, required: false, enum: 'ticketStatus', default: 'unknown' },
      participants:   {
        type: FIELD_TYPES.OBJECT_ARRAY, required: false,
        itemShape: Object.freeze({
          teamId:      { type: FIELD_TYPES.ID_REF, required: true, target: 'Team' },
          role:        { type: FIELD_TYPES.ENUM, required: true, enum: 'participantRole' },
          score:       { type: FIELD_TYPES.INTEGER, required: false, min: 0 },
          isWinner:    { type: FIELD_TYPES.BOOLEAN, required: false },
          resultNote:  { type: FIELD_TYPES.STRING, required: false },
        }),
      },
      resultSummary:  { type: FIELD_TYPES.STRING, required: false },
      monetizationEnabled: { type: FIELD_TYPES.BOOLEAN, required: false, default: true },
    }),
    relationships: Object.freeze([
      { name: 'competitionId', target: 'Competition', cardinality: 'many-to-one', required: true },
      { name: 'sportId', target: 'Sport', cardinality: 'many-to-one', required: true },
      { name: 'seasonOrEditionId', target: 'SeasonOrEdition', cardinality: 'many-to-one', required: true },
      { name: 'venueIds', target: 'Venue', cardinality: 'many-to-many', required: false },
      { name: 'cityIds', target: 'City', cardinality: 'many-to-many', required: false },
      { name: 'participants[].teamId', target: 'Team', cardinality: 'many-to-many', required: false },
    ]),
    verification: Object.freeze({
      gatedFields: Object.freeze(['startsAt', 'endsAt', 'participants', 'resultSummary']),
      minAuthorityForGated: 'official',
      note:
        'Kickoff times are the single most volatile field in the model. ' +
        'startTimeConfirmed false means the time may render only as provisional.',
    }),
    commercial: Object.freeze({
      placementTargetable: true,
      capabilityFlags: Object.freeze(['monetizationEnabled']),
    }),
    constraints: Object.freeze([
      'sportId must equal the sportId of the referenced Competition.',
      'seasonOrEditionId must reference a SeasonOrEdition whose competitionId matches this Event.',
      'ticketStatus is independent of eventStatus and must not be inferred from it.',
      'eventStatus completed requires either resultSummary or scores on participants.',
      'isNeutralSite true forbids participantRole home and away on the same Event.',
      'endsAt must not precede startsAt.',
      'A participant teamId may appear at most once per Event.',
    ]),
  }),

  Team: Object.freeze({
    entityType: 'Team',
    idPrefix: 'team',
    idPattern: '^team:[a-z0-9][a-z0-9-]*$',
    slugScope: 'per-sport',
    purpose:
      'A competing side. Not every team belongs to a city: national, ' +
      'territorial and representative sides represent a country or territory ' +
      'instead, and some franchises relocate. Geography is therefore optional ' +
      'and expressed through an explicit "represents" reference.',
    fields: Object.freeze({
      ...FACTUAL_BASE,
      sportId:      { type: FIELD_TYPES.ID_REF, required: true, target: 'Sport' },
      teamType:     { type: FIELD_TYPES.ENUM, required: true, enum: 'teamType' },
      representsEntityType: { type: FIELD_TYPES.POLY_REF_TYPE, required: false,
        allowedTypes: Object.freeze(['CountryOrTerritory', 'AdministrativeRegion', 'City', 'Region']) },
      representsEntityId:   { type: FIELD_TYPES.POLY_REF_ID, required: false },
      cityId:       { type: FIELD_TYPES.ID_REF, required: false, target: 'City' },
      countryOrTerritoryId: { type: FIELD_TYPES.ID_REF, required: false, target: 'CountryOrTerritory' },
      homeVenueIds: { type: FIELD_TYPES.ID_REF_ARRAY, required: false, target: 'Venue' },
      competitionIds: { type: FIELD_TYPES.ID_REF_ARRAY, required: false, target: 'Competition' },
      foundedYear:  { type: FIELD_TYPES.INTEGER, required: false },
      colors:       { type: FIELD_TYPES.STRING_ARRAY, required: false },
      newsletterTopic: { type: FIELD_TYPES.STRING, required: false },
      monetizationEnabled: { type: FIELD_TYPES.BOOLEAN, required: false, default: true },
    }),
    relationships: Object.freeze([
      { name: 'sportId', target: 'Sport', cardinality: 'many-to-one', required: true },
      { name: 'representsEntityType + representsEntityId', target: 'polymorphic', cardinality: 'many-to-one', required: false },
      { name: 'cityId', target: 'City', cardinality: 'many-to-one', required: false },
      { name: 'countryOrTerritoryId', target: 'CountryOrTerritory', cardinality: 'many-to-one', required: false },
      { name: 'homeVenueIds', target: 'Venue', cardinality: 'many-to-many', required: false },
      { name: 'competitionIds', target: 'Competition', cardinality: 'many-to-many', required: false },
    ]),
    verification: Object.freeze({
      gatedFields: Object.freeze(['foundedYear', 'homeVenueIds']),
      minAuthorityForGated: 'primary',
    }),
    commercial: Object.freeze({
      placementTargetable: true,
      capabilityFlags: Object.freeze(['monetizationEnabled', 'newsletterTopic']),
    }),
    constraints: Object.freeze([
      'representsEntityType and representsEntityId must be supplied together or not at all.',
      'teamType national or territorial requires representsEntityType CountryOrTerritory.',
      'teamType club or franchise should carry cityId, but it is not required (relocations, unresolved cases).',
      'referenced competitionIds must have the same sportId as this Team.',
    ]),
  }),

  /* ---------------------------------------------------------------- *
   * COMMERCIAL AND DISTRIBUTION
   * ---------------------------------------------------------------- */

  TicketProvider: Object.freeze({
    entityType: 'TicketProvider',
    idPrefix: 'ticketprovider',
    idPattern: '^ticketprovider:[a-z0-9][a-z0-9-]*$',
    slugScope: 'per-entityType',
    purpose:
      'An organisation through which event tickets are obtained. Kept separate ' +
      'from TravelProvider and MerchandiseProvider because ticketing carries ' +
      'distinct legal and editorial policy, but shares the same classification ' +
      'vocabulary.',
    fields: Object.freeze({
      ...PROVIDER_BASE,
      providerCategories: { type: FIELD_TYPES.STRING_ARRAY, required: false, enum: 'ticketProviderCategory' },
      resaleAllowed:      { type: FIELD_TYPES.BOOLEAN, required: true, default: false },
    }),
    relationships: Object.freeze([
      { name: 'geoScopeCountryIds', target: 'CountryOrTerritory', cardinality: 'many-to-many', required: false },
    ]),
    verification: Object.freeze({
      gatedFields: Object.freeze(['classification']),
      minAuthorityForGated: 'official',
      note:
        'classification must be set deliberately. The presence of a link ' +
        'anywhere in the repository is not evidence of approval.',
    }),
    commercial: Object.freeze({
      placementTargetable: false,
      isPlacementSource: true,
      capabilityFlags: Object.freeze(['disclosureRequired', 'resaleAllowed']),
    }),
    constraints: Object.freeze([
      'classification prohibited forbids use in any CommercialPlacement.',
      'classification secondary_marketplace requires resaleAllowed true and a policyNote.',
      'classification affiliate requires affiliateNetwork and disclosureRequired true.',
    ]),
  }),

  TravelProvider: Object.freeze({
    entityType: 'TravelProvider',
    idPrefix: 'travelprovider',
    idPattern: '^travelprovider:[a-z0-9][a-z0-9-]*$',
    slugScope: 'per-entityType',
    purpose:
      'An organisation supplying travel products around an event or city — ' +
      'accommodation, flights, transfers, parking, passes, connectivity.',
    fields: Object.freeze({
      ...PROVIDER_BASE,
      providerCategories: { type: FIELD_TYPES.STRING_ARRAY, required: true, enum: 'travelProviderCategory' },
    }),
    relationships: Object.freeze([
      { name: 'geoScopeCountryIds', target: 'CountryOrTerritory', cardinality: 'many-to-many', required: false },
    ]),
    verification: Object.freeze({
      gatedFields: Object.freeze(['classification']),
      minAuthorityForGated: 'primary',
    }),
    commercial: Object.freeze({
      placementTargetable: false,
      isPlacementSource: true,
      capabilityFlags: Object.freeze(['disclosureRequired']),
    }),
    constraints: Object.freeze([
      'classification prohibited forbids use in any CommercialPlacement.',
      'classification affiliate requires affiliateNetwork and disclosureRequired true.',
      'providerCategories must contain at least one value.',
    ]),
  }),

  MerchandiseProvider: Object.freeze({
    entityType: 'MerchandiseProvider',
    idPrefix: 'merchprovider',
    idPattern: '^merchprovider:[a-z0-9][a-z0-9-]*$',
    slugScope: 'per-entityType',
    purpose:
      'An organisation supplying goods — kit, apparel, collectibles, prints. ' +
      'Licensing claims are verification-gated: "official merchandise" is a ' +
      'factual assertion, not a marketing phrase.',
    fields: Object.freeze({
      ...PROVIDER_BASE,
      providerCategories: { type: FIELD_TYPES.STRING_ARRAY, required: true, enum: 'merchandiseProviderCategory' },
      licensingNote:      { type: FIELD_TYPES.TEXT, required: false },
      isOfficiallyLicensed: { type: FIELD_TYPES.BOOLEAN, required: false, default: false },
    }),
    relationships: Object.freeze([
      { name: 'geoScopeCountryIds', target: 'CountryOrTerritory', cardinality: 'many-to-many', required: false },
    ]),
    verification: Object.freeze({
      gatedFields: Object.freeze(['classification', 'isOfficiallyLicensed']),
      minAuthorityForGated: 'official',
    }),
    commercial: Object.freeze({
      placementTargetable: false,
      isPlacementSource: true,
      capabilityFlags: Object.freeze(['disclosureRequired', 'isOfficiallyLicensed']),
    }),
    constraints: Object.freeze([
      'classification prohibited forbids use in any CommercialPlacement.',
      'isOfficiallyLicensed true requires licensingNote and a source at authorityLevel official.',
      'providerCategories must contain at least one value.',
    ]),
  }),

  Advertiser: Object.freeze({
    entityType: 'Advertiser',
    idPrefix: 'advertiser',
    idPattern: '^advertiser:[a-z0-9][a-z0-9-]*$',
    slugScope: 'per-entityType',
    purpose:
      'A paying commercial party, as distinct from an affiliate provider. ' +
      'Holds no contact details, contract terms or credentials — those live ' +
      'outside the repository.',
    fields: Object.freeze({
      id:               { type: FIELD_TYPES.ID, required: true },
      slug:             { type: FIELD_TYPES.SLUG, required: true },
      name:             { type: FIELD_TYPES.STRING, required: true },
      legalName:        { type: FIELD_TYPES.STRING, required: false },
      industry:         { type: FIELD_TYPES.STRING, required: false },
      advertiserStatus: { type: FIELD_TYPES.ENUM, required: true, enum: 'advertiserStatus' },
      disclosureLabelDefault: { type: FIELD_TYPES.STRING, required: true },
      externalContactRef: { type: FIELD_TYPES.STRING, required: false },
      status:           { type: FIELD_TYPES.ENUM, required: true, enum: 'status' },
      lastUpdated:      { type: FIELD_TYPES.DATETIME, required: true },
      notes:            { type: FIELD_TYPES.TEXT, required: false },
    }),
    relationships: Object.freeze([]),
    verification: Object.freeze({
      gatedFields: Object.freeze([]),
      minAuthorityForGated: null,
      note: 'Advertiser records are contractual, not factual. They carry no verificationStatus.',
    }),
    commercial: Object.freeze({
      placementTargetable: false,
      isPlacementSource: true,
      capabilityFlags: Object.freeze([]),
    }),
    constraints: Object.freeze([
      'externalContactRef must be an opaque reference, never an email address, phone number or credential.',
      'disclosureLabelDefault must be non-empty.',
    ]),
  }),

  CommercialPlacement: Object.freeze({
    entityType: 'CommercialPlacement',
    idPrefix: 'placement',
    idPattern: '^placement:[a-z0-9][a-z0-9-]*$',
    slugScope: null,
    purpose:
      'The join between a commercial party and a place on the site. All ' +
      'monetisation is expressed here rather than as fields scattered across ' +
      'factual entities, so that inventory can be listed, dated and audited ' +
      'in one place.',
    fields: Object.freeze({
      id:               { type: FIELD_TYPES.ID, required: true },
      placementType:    { type: FIELD_TYPES.ENUM, required: true, enum: 'placementType' },
      // Must stay in lockstep with the entities whose descriptors declare
      // commercial.placementTargetable true. Region, AdministrativeRegion and
      // Sport are navigational and deliberately excluded.
      targetEntityType: { type: FIELD_TYPES.POLY_REF_TYPE, required: false,
        allowedTypes: Object.freeze([
          'CountryOrTerritory', 'City', 'Venue',
          'Competition', 'SeasonOrEdition', 'Event', 'Team', 'Article',
        ]) },
      targetEntityId:   { type: FIELD_TYPES.POLY_REF_ID, required: false },
      pagePath:         { type: FIELD_TYPES.STRING, required: false },
      position:         { type: FIELD_TYPES.STRING, required: true },
      advertiserId:     { type: FIELD_TYPES.ID_REF, required: false, target: 'Advertiser' },
      providerEntityType: { type: FIELD_TYPES.POLY_REF_TYPE, required: false,
        allowedTypes: Object.freeze(['TicketProvider', 'TravelProvider', 'MerchandiseProvider']) },
      providerEntityId: { type: FIELD_TYPES.POLY_REF_ID, required: false },
      status:           { type: FIELD_TYPES.ENUM, required: true, enum: 'placementStatus' },
      startsAt:         { type: FIELD_TYPES.DATETIME, required: false },
      endsAt:           { type: FIELD_TYPES.DATETIME, required: false },
      requiresDisclosure: { type: FIELD_TYPES.BOOLEAN, required: true, default: true },
      disclosureLabel:  { type: FIELD_TYPES.STRING, required: false },
      creativeRef:      { type: FIELD_TYPES.STRING, required: false },
      priority:         { type: FIELD_TYPES.INTEGER, required: false, default: 0 },
      lastUpdated:      { type: FIELD_TYPES.DATETIME, required: true },
      notes:            { type: FIELD_TYPES.TEXT, required: false },
    }),
    relationships: Object.freeze([
      { name: 'targetEntityType + targetEntityId', target: 'polymorphic', cardinality: 'many-to-one', required: false },
      { name: 'advertiserId', target: 'Advertiser', cardinality: 'many-to-one', required: false },
      { name: 'providerEntityType + providerEntityId', target: 'polymorphic', cardinality: 'many-to-one', required: false },
    ]),
    verification: Object.freeze({
      gatedFields: Object.freeze([]),
      minAuthorityForGated: null,
    }),
    commercial: Object.freeze({
      placementTargetable: false,
      isPlacementSource: false,
      capabilityFlags: Object.freeze(['requiresDisclosure']),
    }),
    constraints: Object.freeze([
      'A placement must resolve to a target: either targetEntityType + targetEntityId, or pagePath.',
      'targetEntityType and targetEntityId must be supplied together or not at all.',
      'Exactly one commercial source: advertiserId, or a provider reference — not both, not neither.',
      'providerEntityType and providerEntityId must be supplied together or not at all.',
      'requiresDisclosure true requires a non-empty disclosureLabel.',
      'A provider reference whose classification is prohibited is invalid.',
      'endsAt must not precede startsAt.',
      'status active requires the current time to fall inside startsAt..endsAt when either is set.',
      'targetEntityType must name an entity whose descriptor has commercial.placementTargetable true.',
    ]),
  }),

  Article: Object.freeze({
    entityType: 'Article',
    idPrefix: 'article',
    idPattern: '^article:[a-z0-9][a-z0-9-]*$',
    slugScope: 'per-entityType',
    purpose:
      'An editorial page. Links narrative content to the entities it covers ' +
      'and to the sources behind it. monetizationEnabled is an editorial ' +
      'decision recorded as data, not the incidental absence of placements.',
    fields: Object.freeze({
      ...FACTUAL_BASE,
      articleType:  { type: FIELD_TYPES.ENUM, required: true, enum: 'articleType' },
      pagePath:     { type: FIELD_TYPES.STRING, required: true },
      publishedAt:  { type: FIELD_TYPES.DATETIME, required: false },
      updatedAt:    { type: FIELD_TYPES.DATETIME, required: false },
      authorName:   { type: FIELD_TYPES.STRING, required: false },
      displayTitle: { type: FIELD_TYPES.STRING, required: false },
      entityRefs:   {
        type: FIELD_TYPES.OBJECT_ARRAY, required: false,
        itemShape: Object.freeze({
          entityType: { type: FIELD_TYPES.POLY_REF_TYPE, required: true },
          entityId:   { type: FIELD_TYPES.POLY_REF_ID, required: true },
          relation:   { type: FIELD_TYPES.STRING, required: false },
        }),
      },
      monetizationEnabled: { type: FIELD_TYPES.BOOLEAN, required: true, default: true },
      isOpinion:    { type: FIELD_TYPES.BOOLEAN, required: false, default: false },
    }),
    relationships: Object.freeze([
      { name: 'entityRefs[]', target: 'polymorphic', cardinality: 'many-to-many', required: false },
      { name: 'sourceRecordIds', target: 'SourceRecord', cardinality: 'many-to-many', required: false },
    ]),
    verification: Object.freeze({
      gatedFields: Object.freeze([]),
      minAuthorityForGated: 'secondary',
      note:
        'articleType report should carry at least one sourceRecordId. ' +
        'articleType opinion must set isOpinion true.',
    }),
    commercial: Object.freeze({
      placementTargetable: true,
      capabilityFlags: Object.freeze(['monetizationEnabled']),
    }),
    constraints: Object.freeze([
      'monetizationEnabled false forbids any CommercialPlacement targeting this Article or its pagePath.',
      'articleType opinion requires isOpinion true.',
      'articleType memoriam defaults monetizationEnabled to false.',
      'pagePath must be unique across Articles.',
      'name holds the canonical headline; displayTitle overrides it for rendering only.',
    ]),
  }),

  SourceRecord: Object.freeze({
    entityType: 'SourceRecord',
    idPrefix: 'source',
    idPattern: '^source:[a-z0-9][a-z0-9-]*$',
    slugScope: null,
    purpose:
      'A citation. Every changing fact in the model points at one or more of ' +
      'these, so a claim can always be traced to where it came from and when ' +
      'it was read.',
    fields: Object.freeze({
      id:             { type: FIELD_TYPES.ID, required: true },
      sourceType:     { type: FIELD_TYPES.ENUM, required: true, enum: 'sourceType' },
      publisher:      { type: FIELD_TYPES.STRING, required: true },
      title:          { type: FIELD_TYPES.STRING, required: true },
      url:            { type: FIELD_TYPES.URL, required: false },
      accessedAt:     { type: FIELD_TYPES.DATETIME, required: true },
      publishedAt:    { type: FIELD_TYPES.DATETIME, required: false },
      authorityLevel: { type: FIELD_TYPES.ENUM, required: true, enum: 'authorityLevel' },
      notes:          { type: FIELD_TYPES.TEXT, required: false },
    }),
    relationships: Object.freeze([]),
    verification: Object.freeze({
      gatedFields: Object.freeze([]),
      minAuthorityForGated: null,
      note: 'A SourceRecord is the evidence; it is not itself verification-gated.',
    }),
    commercial: Object.freeze({
      placementTargetable: false,
      capabilityFlags: Object.freeze([]),
    }),
    constraints: Object.freeze([
      'sourceType official_site or governing_body implies authorityLevel official or primary.',
      'accessedAt must not precede publishedAt.',
      'url is optional so that offline sources (books, direct communication) remain expressible.',
    ]),
  }),

  NewsletterSignupSource: Object.freeze({
    entityType: 'NewsletterSignupSource',
    idPrefix: 'nlsource',
    idPattern: '^nlsource:[a-z0-9][a-z0-9-]*$',
    slugScope: null,
    purpose:
      'Describes where a newsletter signup originated, so topic and consent ' +
      'context travel with the signup. Descriptor only — no provider ' +
      'integration and no personal data are modelled here.',
    fields: Object.freeze({
      sourceId:            { type: FIELD_TYPES.ID, required: true },
      pagePath:            { type: FIELD_TYPES.STRING, required: true },
      entityType:          { type: FIELD_TYPES.POLY_REF_TYPE, required: false },
      entityId:            { type: FIELD_TYPES.POLY_REF_ID, required: false },
      campaign:            { type: FIELD_TYPES.STRING, required: false },
      topic:               { type: FIELD_TYPES.STRING, required: false },
      consentTextVersion:  { type: FIELD_TYPES.STRING, required: true },
      status:              { type: FIELD_TYPES.ENUM, required: true, enum: 'status' },
      lastUpdated:         { type: FIELD_TYPES.DATETIME, required: true },
      notes:               { type: FIELD_TYPES.TEXT, required: false },
    }),
    relationships: Object.freeze([
      { name: 'entityType + entityId', target: 'polymorphic', cardinality: 'many-to-one', required: false },
    ]),
    verification: Object.freeze({
      gatedFields: Object.freeze([]),
      minAuthorityForGated: null,
    }),
    commercial: Object.freeze({
      placementTargetable: false,
      capabilityFlags: Object.freeze([]),
    }),
    constraints: Object.freeze([
      'Primary key is sourceId, not id — deliberate deviation, documented in ENTITIES.md.',
      'entityType and entityId must be supplied together or not at all.',
      'consentTextVersion is an opaque version identifier, never the consent text itself.',
      'This entity must never hold an email address or any other personal data.',
    ]),
  }),

});

/* ------------------------------------------------------------------ *
 * GLOBAL VALIDATION RULES
 * Cross-entity rules a future validator enforces. Declarative only.
 * ------------------------------------------------------------------ */

export const GLOBAL_RULES = Object.freeze([
  Object.freeze({ id: 'unique-id',            severity: 'error', description: 'Every id is unique across the whole dataset, not merely within its entity type.' }),
  Object.freeze({ id: 'id-prefix-match',      severity: 'error', description: 'Every id matches its entity descriptor idPattern.' }),
  Object.freeze({ id: 'unique-slug',          severity: 'error', description: 'Slugs are unique within the scope named by slugScope.' }),
  Object.freeze({ id: 'slug-format',          severity: 'error', description: 'Slugs are lowercase a-z, 0-9 and hyphens; no leading, trailing or repeated hyphens.' }),
  Object.freeze({ id: 'fk-resolves',          severity: 'error', description: 'Every idRef and idRefArray value resolves to an existing record of the declared target type.' }),
  Object.freeze({ id: 'poly-ref-paired',      severity: 'error', description: 'Polymorphic type and id fields are supplied together and the type is in allowedTypes.' }),
  Object.freeze({ id: 'required-present',     severity: 'error', description: 'Every field marked required is present and non-empty.' }),
  Object.freeze({ id: 'enum-valid',           severity: 'error', description: 'Every enum value is a member of the referenced ENUMS set.' }),
  Object.freeze({ id: 'page-status-valid',    severity: 'error', description: 'pageStatus is a member of ENUMS.pageStatus; published requires a resolvable page path.' }),
  Object.freeze({ id: 'verification-valid',   severity: 'error', description: 'verificationStatus is a member of ENUMS.verificationStatus.' }),
  Object.freeze({ id: 'provider-class-valid', severity: 'error', description: 'Provider classification is a member of ENUMS.providerClassification and was set explicitly.' }),
  Object.freeze({ id: 'placement-resolves',   severity: 'error', description: 'Every CommercialPlacement resolves to a target and to exactly one commercial source.' }),
  Object.freeze({ id: 'prohibited-unused',    severity: 'error', description: 'No CommercialPlacement references a provider classified prohibited.' }),
  Object.freeze({ id: 'disclosure-present',   severity: 'error', description: 'requiresDisclosure true implies a non-empty disclosureLabel.' }),
  Object.freeze({ id: 'no-monetized-optout',  severity: 'error', description: 'No CommercialPlacement targets an entity whose monetizationEnabled is false.' }),
  Object.freeze({ id: 'gated-field-sourced',  severity: 'error', description: 'A verification-gated field carrying a value has a SourceRecord at or above minAuthorityForGated.' }),
  Object.freeze({ id: 'no-orphans',           severity: 'warn',  description: 'Records reachable from no other record and carrying pageStatus none are reported.' }),
  Object.freeze({ id: 'date-order',           severity: 'error', description: 'Paired date and datetime fields are in chronological order.' }),
  Object.freeze({ id: 'entity-constraints',   severity: 'error', description: 'Every rule listed in an entity descriptor constraints array holds.' }),
]);

export const SCHEMA_VERSION = '0.1.0';

export default Object.freeze({
  SCHEMA_VERSION,
  FIELD_TYPES,
  ENUMS,
  ENTITIES,
  GLOBAL_RULES,
});
