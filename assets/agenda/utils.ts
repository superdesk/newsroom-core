import {get, isEmpty, includes, keyBy, sortBy, partition} from 'lodash';
import moment from 'moment/moment';
import {
    formatDate,
    formatMonth,
    formatWeek,
    getConfig,
    gettext,
    DATE_FORMAT,
    COVERAGE_DATE_TIME_FORMAT,
    COVERAGE_DATE_FORMAT,
    parseDate,
    AGENDA_DATE_FORMAT_SHORT,
    formatTime,
    DAY_IN_MINUTES,
} from '../utils';

export const STATUS_KILLED = 'killed';
export const STATUS_CANCELED = 'cancelled';
export const STATUS_POSTPONED = 'postponed';
export const STATUS_RESCHEDULED = 'rescheduled';

const navigationFunctions: any = {
    'day': {
        'next': getNextDay,
        'previous': getPreviousDay,
        'format': (dateString: any) => moment(dateString).format(AGENDA_DATE_FORMAT_SHORT),
    },
    'week': {
        'next': getNextWeek,
        'previous': getPreviousWeek,
        'format': (dateString: any) => `${moment(dateString).format('D MMMM')} -
        ${moment(dateString).add(6, 'days').format('D MMMM')}`,
    },
    'month': {
        'next': getNextMonth,
        'previous': getPreviousMonth,
        'format': (dateString: any) => moment(dateString).format('MMMM, YYYY'),
    }
};

const Groupers: any = {
    'day': formatDate,
    'week': formatWeek,
    'month': formatMonth,
};

export function getCoverageStatusText(coverage: any) {
    if (coverage.workflow_status === WORKFLOW_STATUS.DRAFT) {
        return get(DRAFT_STATUS_TEXTS, coverage.coverage_status, '');
    }

    if (coverage.workflow_status === WORKFLOW_STATUS.COMPLETED && coverage.publish_time) {
        if ((get(coverage, 'deliveries.length', 0) === 2 && coverage.deliveries[0].publish_time) ||
            get(coverage, 'deliveries.length', 0) > 2) {
            return gettext('coverage updated {{ at }}', {at: moment(coverage.publish_time).format(COVERAGE_DATE_TIME_FORMAT)});
        }

        return `${get(WORKFLOW_STATUS_TEXTS, coverage.workflow_status, '')} ${moment(coverage.publish_time).format(COVERAGE_DATE_TIME_FORMAT)}`;
    }

    return get(WORKFLOW_STATUS_TEXTS, coverage.workflow_status, '');
}

const TO_BE_CONFIRMED_FIELD = '_time_to_be_confirmed';
const TO_BE_CONFIRMED_TEXT = gettext('Time to be confirmed');
export const WORKFLOW_STATUS = {
    DRAFT: 'draft',
    ASSIGNED: 'assigned',
    ACTIVE: 'active',
    COMPLETED: 'completed',
    CANCELLED: 'cancelled',
};

const DRAFT_STATUS_TEXTS = {
    'coverage not planned': gettext('coverage not planned'),
    'coverage not intended': gettext('coverage not planned'),
    'coverage intended': gettext('coverage planned'),
    'coverage not decided': gettext('coverage on merit'),
    'coverage not decided yet': gettext('coverage on merit'),
    'coverage upon request': gettext('coverage on request'),
};

const WORKFLOW_STATUS_TEXTS = {
    [WORKFLOW_STATUS.ASSIGNED]: gettext('coverage planned'),
    [WORKFLOW_STATUS.ACTIVE]: gettext('coverage in progress'),
    [WORKFLOW_STATUS.COMPLETED]: gettext('coverage available'),
    [WORKFLOW_STATUS.CANCELLED]: gettext('coverage cancelled'),
};

export const WORKFLOW_COLORS = {
    [WORKFLOW_STATUS.DRAFT]: 'coverage--draft',
    [WORKFLOW_STATUS.ASSIGNED]: 'coverage--assigned',
    [WORKFLOW_STATUS.ACTIVE]: 'coverage--active',
    [WORKFLOW_STATUS.COMPLETED]: 'coverage--completed',
    [WORKFLOW_STATUS.CANCELLED]: 'coverage--cancelled',
};

export const SCHEDULE_TYPE = {
    REGULAR: 'REGULAR',
    ALL_DAY: 'ALL_DAY',
    MULTI_DAY: 'MULTI_DAY',
    NO_DURATION: 'NO_DURATION',
};


/**
 * Early enough date to use in querying all agenda items
 * @type {number}
 */
export const EARLIEST_DATE = moment('20170101').valueOf();

/**
 * Test if an item is canceled or killed
 *
 * @param {Object} item
 * @return {Boolean}
 */
export function isCanceled(item: any) {
    return item && (item.state === STATUS_CANCELED || item.state === STATUS_KILLED);
}

/**
 * Test if an item is postponed
 *
 * @param {Object} item
 * @return {Boolean}
 */
export function isPostponed(item: any) {
    return item && item.state === STATUS_POSTPONED;
}

/**
 * Test if an item is rescheduled
 *
 * @param {Object} item
 * @return {Boolean}
 */
export function isRescheduled(item: any) {
    return item && item.state === STATUS_RESCHEDULED;
}

/**
 * Test if an item has coverages
 *
 * @param {Object} item
 * @return {Boolean}
 */
export function hasCoverages(item: any) {
    return !isEmpty(get(item, 'coverages'));
}

/**
 * Returns icon name of the given coverage type
 *
 * @param coverageType
 * @returns {*}
 */
export function getCoverageIcon(coverageType: any) {
    const coverageTypes = getConfig('coverage_types', {});
    return get(coverageTypes, `${coverageType}.icon`, 'unrecognized');
}

/**
 * Returns display name of the given coverage type
 *
 * @param coverageType
 * @returns {*}
 */
export function getCoverageDisplayName(coverageType: any) {
    const coverageTypes = getConfig('coverage_types', {});
    const locale = (window.locale || 'en').toLowerCase();

    return get(coverageTypes, `${coverageType}.translations.${locale}`) ||
        get(coverageTypes, `${coverageType}.name`, coverageType);
}

/**
 * Test if an item is watched
 *
 * @param {Object} item
 * @param {String} userId
 * @return {Boolean}
 */
export function isWatched(item: any, userId: any) {
    return userId && includes(get(item, 'watches', []), userId);
}

/**
 * Test if a coverage is for given date string
 *
 * @param {Object} coverage
 * @param {String} dateString
 * @return {Boolean}
 */
export function isCoverageForExtraDay(coverage: any) {
    return coverage.scheduled != null;
}

/**
 * Test if an item is recurring
 *
 * @param {Object} item
 * @return {Boolean}
 */
export function isRecurring(item: any) {
    return item && !!item.recurrence_id;
}

/**
 * Returns item Geo location in lat and long
 *
 * @param {Object} item
 * @return {String}
 */
export function getGeoLocation(item: any) {
    return get(item, 'location.location', null);
}

/**
 * Returns item address in string
 *
 * @param {Object} item
 * @return {String}
 */
export function getLocationString(item: any) {
    return [
        get(item, 'location.0.name', get(item, 'location.0.address.title')),
        get(item, 'location.0.address.line.0'),
        get(item, 'location.0.address.city') || get(item, 'location.0.address.area'),
        get(item, 'location.0.address.state') || get(item, 'location.0.address.locality'),
        get(item, 'location.0.address.postal_code'),
        get(item, 'location.0.address.country'),
    ].filter((d: any) => d).join(', ');
}

/**
 * Returns item has location info
 *
 * @param {Object} item
 * @return {Boolean}
 */
export function hasLocation(item: any) {
    return !!getLocationString(item);
}

export function hasLocationNotes(item: any) {
    return get(item, 'location[0].details[0].length', 0) > 0;
}

/**
 * Returns public contacts
 *
 * @param {Object} item
 * @return {String}
 */
export function getPublicContacts(item: any) {
    const contacts = get(item, 'event.event_contact_info', []);
    return contacts.filter((c: any) => c.public).map((c: any) => ({
        name: [c.first_name, c.last_name].filter((x: any) => !!x).join(' '),
        organisation: c.organisation || '',
        email: (c.contact_email || []).join(', '),
        phone: (c.contact_phone || []).filter((m: any) => m.public).map((m: any) => m.number).join(', '),
        mobile: (c.mobile || []).filter((m: any) => m.public).map((m: any) => m.number).join(', '),
    }));
}

/**
 * Returns item calendars
 *
 * @param {Object} item
 * @return {String}
 */
export function getCalendars(item: any) {
    return (get(item, 'calendars') || []).map((cal: any) => cal.name).join(', ');
}

export function getAgendaNames(item: any) {
    return (get(item, 'agendas') || [])
        .map((agenda: any) => agenda.name)
        .join(', ');
}

export function isPlanningItem(item: any) {
    return item.item_type === 'planning' || (
        item.item_type == null &&
        item.event_id == null
    );
}

export function planHasEvent(item: any) {
    return isPlanningItem(item) && item.event_id != null;
}

/**
 * Returns item event link
 *
 * @param {Object} item
 * @return {String}
 */
export function getEventLinks(item: any) {
    return get(item, 'event.links') || [];
}


/**
 * Format date of a date (without time)
 *
 * @param {String} dateString
 * @return {String}
 */
export function formatNavigationDate(dateString: any, grouping: any) {
    return navigationFunctions[grouping].format(dateString);
}


/**
 * Return date formatted for query
 *
 * @param {String} dateString
 * @return {String}
 */
export function getDateInputDate(dateString: any) {
    if (dateString) {
        const parsed = moment(parseInt(dateString));
        return parsed.format('YYYY-MM-DD');
    }

    return '';
}

/**
 * Return moment date
 *
 * @param {String} dateString
 * @return {String}
 */
export function getMomentDate(dateString: any): any {
    if (dateString) {
        return moment(parseInt(dateString));
    }

    return '';
}

/**
 * Gets the next day
 *
 * @param {String} dateString
 * @return {String} number of milliseconds since the Unix Epoch
 */
function getNextDay(dateString: any) {
    return moment(dateString).add(1, 'days').valueOf();
}


/**
 * Gets the previous day
 *
 * @param {String} dateString
 * @return {String} number of milliseconds since the Unix Epoch
 */
function getPreviousDay(dateString: any) {
    return moment(dateString).add(-1, 'days').valueOf();
}

/**
 * Gets the next week
 *
 * @param {String} dateString
 * @return {String} number of milliseconds since the Unix Epoch
 */
function getNextWeek(dateString: any) {
    return moment(dateString).add(7, 'days').isoWeekday(1).valueOf();
}


/**
 * Gets the previous week
 *
 * @param {String} dateString
 * @return {String} number of milliseconds since the Unix Epoch
 */
function getPreviousWeek(dateString: any) {
    return moment(dateString).add(-7, 'days').isoWeekday(1).valueOf();
}

/**
 * Gets the next month
 *
 * @param {String} dateString
 * @return {String} number of milliseconds since the Unix Epoch
 */
function getNextMonth(dateString: any) {
    return moment(dateString).add(1, 'months').startOf('month').valueOf();
}


/**
 * Gets the previous month
 *
 * @param {String} dateString
 * @return {String} number of milliseconds since the Unix Epoch
 */
export function getPreviousMonth(dateString: any) {
    return moment(dateString).add(-1, 'months').startOf('month').valueOf();
}

/**
 * Calls the next function of a given grouping
 *
 * @param {String} dateString
 * @param {String} grouping: day, week or month
 * @return {String} number of milliseconds since the Unix Epoch
 */
export function getNext(dateString: any, grouping: any) {
    return navigationFunctions[grouping].next(dateString);
}

/**
 * Calls the previous function of a given grouping
 *
 * @param {String} dateString
 * @param {String} grouping: day, week or month
 * @return {String} number of milliseconds since the Unix Epoch
 */
export function getPrevious(dateString: any, grouping: any) {
    return navigationFunctions[grouping].previous(dateString);
}

/**
 * Get agenda item attachments
 *
 * @param {Object} item
 * @return {Array}
 */
export function getAttachments(item: any) {
    return get(item, 'event.files', []);
}

/**
 * Get list of internal notes
 *
 * @param {Object} item
 * @return {Array}
 */
export function getInternalNote(item: any, plan: any) {
    return get(plan, 'internal_note') || get(item, 'event.internal_note');
}

/**
 * Get internal notes per coverage
 *
 * @param {Object} item
 * @return {Object}
 */
export function getDataFromCoverages(item: any) {
    const planningItems = get(item, 'planning_items', []);
    let data: any = {
        'internal_note': {},
        'ednote': {},
        'workflow_status_reason': {},
        'scheduled_update_status': {},
    };

    planningItems.forEach((p: any) => {
        (get(p, 'coverages') || []).forEach((c: any) => {
            ['internal_note', 'ednote', 'workflow_status_reason'].forEach((field: any) => {

                // Don't populate if the value is same as the field in upper level planning_item
                // Don't populate workflow_status_reason is planning_item is cancelled to avoid UI duplication
                if (!get(c, `planning.${field}`, '') || c.planning[field] === p[field] ||
                        (field === 'workflow_status_reason' && p['state'] === STATUS_CANCELED)) {
                    return;
                }

                data[field][c.coverage_id] = c.planning[field];
            });

            if (get(c, 'scheduled_updates.length', 0) > 0 && c['workflow_status'] === WORKFLOW_STATUS.COMPLETED) {
                // Get latest appropriate scheduled_update
                const schedUpdate = getNextPendingScheduledUpdate(c);
                if (schedUpdate) {
                    const dateString = `${moment(schedUpdate.planning.scheduled).format(COVERAGE_DATE_TIME_FORMAT)}`;
                    data['scheduled_update_status'][c.coverage_id] = gettext(`Update expected @ ${dateString}`);
                }
            }

        });
    });
    return data;
}

const getNextPendingScheduledUpdate = (coverage: any) => {
    if (coverage.scheduled == null) {
        // Not privileged to see coverage details
        return null;
    } else if (
        get(coverage, 'scheduled_updates.length', 0) === 0 ||
        get(coverage, 'deliveries.length', 0) === 0
    ) {
        // No scheduled_updates or deliveries
        return null;
    } else if (get(coverage, 'deliveries.length', 0) === 1) {
        // Only one delivery: no scheduled_update was published
        return coverage.scheduled_updates[0];
    }

    const lastScheduledDelivery = (coverage.deliveries.reverse()).find((d: any) => d.scheduled_update_id);
    // More deliveries, but no scheduled_update was published
    if (!lastScheduledDelivery) {
        return coverage.scheduled_updates[0];
    }

    const lastPublishedShceduledUpdateIndex = coverage.scheduled_updates.findIndex((s: any) =>
        s.scheduled_update_id === lastScheduledDelivery.scheduled_update_id);

    if (lastPublishedShceduledUpdateIndex === coverage.scheduled_updates.length - 1) {
        // Last scheduled_update was published, nothing pending
        return;
    }

    if (lastPublishedShceduledUpdateIndex < coverage.scheduled_updates.length - 1){
        // There is a pending scheduled_update
        return coverage.scheduled_updates[lastPublishedShceduledUpdateIndex + 1];
    }
};

/**
 * Get list of subjects
 *
 * @param {Object} item
 * @return {Array}
 */
export function getSubjects(item: any) {
    return get(item, 'subject') || [];
}

/**
 * Test if item has any attachments
 *
 * @param {Object} item
 * @return {Boolean}
 */
export function hasAttachments(item: any) {
    return !isEmpty(getAttachments(item));
}

/**
 * Get agenda item name
 *
 * @param {Object} item
 * @return {String}
 */
export function getName(item: any) {
    return item.name || item.slugline || item.headline;
}

/**
 * Get agenda item description
 *
 * @param {Object} item
 * @param {Object} plan
 * @return {String}
 */
export function getDescription(item: any, plan: any) {
    return plan.description_text || item.definition_short;
}


/**
 * Gets the extra days outside the event days
 *
 * @param {Object} item
 * @return {Array} list of dates
 */
export function getExtraDates(item: any) {
    return getDisplayDates(item).map((ed: any) => moment(ed.date));
}

/**
 * Get the display dates, filtering out those that didn't match Planning/Coverage search
 * @param item: Event or Planning item
 * @returns {Array.<{date: moment.Moment}>}
 */
export function getDisplayDates(item: any) {
    const matchedPlanning = get(item, '_hits.matched_planning_items');

    if (matchedPlanning == null) {
        return get(item, 'display_dates') || [];
    }

    const dates: Array<any> = [];
    const planningItems = get(item, 'planning_items') || [];
    const planningIds = item._hits.matched_planning_items;
    const coverageIds = get(item, '_hits.matched_coverages') != null ?
        item._hits.matched_coverages :
        (get(item, 'coverages') || []).map((coverage: any) => coverage.coverage_id);

    planningItems
        .forEach((plan: any) => {
            if (!planningIds.includes(plan._id)) {
                return;
            }

            const coverages = (get(plan, 'coverages') || []).filter((coverage: any) => coverage.scheduled);

            if (!coverages.length) {
                dates.push({date: plan.planning_date});
                return;
            }

            coverages.forEach((coverage: any) => {
                if (!coverageIds.includes(coverage.coverage_id)) {
                    return;
                }

                dates.push({date: coverage.planning.scheduled});
            });
        });

    return dates;
}

/**
 * Checks if a date is in extra dates
 *
 * @param {Object} item
 * @param {Date} date to check (moment)
 * @return {Boolean}
 */
export function containsExtraDate(item: any, dateToCheck: any) {
    return getDisplayDates(item).map((ed: any) => moment(ed.date).format('YYYY-MM-DD')).includes(dateToCheck.format('YYYY-MM-DD'));
}

// get start date in utc mode if there is no time info
const getStartDate = (item: any) => item.dates.all_day ? moment.utc(item.dates.start) : moment(item.dates.start);

// get end date in utc mode if there is no end time info
const getEndDate = (item: any) => item.dates.no_end_time || item.dates.all_day ?
    moment.utc(item.dates.end || item.dates.start) :
    moment(item.dates.end || item.dates.start);

// compare days without being affected by timezone
const isBetweenDay = (day: any, start: any, end: any) => {
    // it will be converted to local time
    // if passed as string which we need
    // for all day events which are in utc mode
    const startDate = start.format('YYYY-MM-DD');
    const endDate = end.format('YYYY-MM-DD');

    return day.isBetween(startDate, endDate, 'day', '[]');
};

/**
 * Groups given agenda items per given grouping
 * @param items: list of agenda items
 * @param activeDate: date that the grouping will start from
 * @param activeGrouping: type of grouping i.e. day, week, month
 */
export function groupItems(items: any, activeDate: any, activeGrouping: any, featuredOnly?: any) {
    const maxStart = moment(activeDate).set({'h': 0, 'm': 0, 's': 0});
    const groupedItems: any = {};
    const grouper = Groupers[activeGrouping];

    items
        // Filter out items that didn't match any Planning items
        .filter((item: any) => (
            get(item, 'planning_items.length', 0) === 0 ||
            get(item, '_hits.matched_planning_items') == null ||
            get(item, '_hits.matched_planning_items.length', 0) > 0)
        )
        .forEach((item: any) => {
            const itemExtraDates = getExtraDates(item);
            const itemStartDate = getStartDate(item);
            const start = item._display_from ? moment(item._display_from) :
                moment.min(maxStart, moment.min(itemExtraDates.concat([itemStartDate])));
            const itemEndDate = getEndDate(item);

            // If item is an event and was actioned (postponed, rescheduled, cancelled only incase of multi-day event)
            // actioned_date is set. In this case, use that as the cut off date.
            let end = get(item, 'event.actioned_date') ? moment(item.event.actioned_date) : null;
            if (!end || !moment.isMoment(end)) {
                end = item._display_to ? moment(item._display_to) :
                    moment.max(
                        itemExtraDates
                            .concat([maxStart])
                            // If event is all day the end timestamp is the same as
                            // start and depending on the local timezone offset it
                            // might not give enough room for the event to show up,
                            // so add an extra day for it.
                            .concat([itemEndDate.clone().add(1, 'd')])
                    );
            }
            let key = null;

            // use clone otherwise it would modify start and potentially also maxStart, moments are mutable
            for (const day = start.clone(); day.isSameOrBefore(end, 'day'); day.add(1, 'd')) {
                const isBetween = isBetweenDay(day, itemStartDate, itemEndDate);
                const containsExtra = containsExtraDate(item, day);
                const addGroupItem = (item.event == null || get(item, '_hits.matched_planning_items') != null) ?
                    containsExtra :
                    isBetween || containsExtra;

                if (grouper(day) !== key && addGroupItem) {
                    key = grouper(day);
                    const groupList = groupedItems[key] || [];
                    groupList.push(item);
                    groupedItems[key] = groupList;
                }
            }
        });

    Object.keys(groupedItems).forEach((k: any) => {
        if (featuredOnly) {
            groupedItems[k] = groupedItems[k].map((i: any) => i._id);
        } else {
            const tbcPartitioned = partition(groupedItems[k], (i) => isItemTBC(i));
            groupedItems[k] = [
                ...tbcPartitioned[0],
                ...tbcPartitioned[1],
            ].map((i: any) => i._id);
        }
    });

    return sortBy(
        Object.keys(groupedItems).map((k: any) => (
            {
                date: k,
                items: groupedItems[k],
                _sortDate: moment(k, DATE_FORMAT)
            })),
        (g: any) => g._sortDate);
}

/**
 * Get Planning Item for the day
 * @param item: Agenda item
 * @param group: Group Date
 */
export function getPlanningItemsByGroup(item: any, group: any) {
    const planningItems = get(item, 'planning_items') || [];

    if (planningItems.length === 0) {
        return [];
    }

    // Planning item without coverages
    const plansWithoutCoverages = planningItems.filter((p: any) =>
        formatDate(p.planning_date) === group && get(p, 'coverages.length', 0) === 0);

    const allPlans = keyBy(planningItems, '_id');
    const processed: any = {};

    // get unique plans for that group based on the coverage.
    const plansWithCoverages = (item.coverages || [])
        .map((coverage: any) => {
            if (isCoverageForExtraDay(coverage)) {
                if (!processed[coverage.planning_id]) {
                    processed[coverage.planning_id] = 1;
                    return allPlans[coverage.planning_id];
                }
                return null;
            }
            return null;
        })
        .filter((p: any) => p);

    return [...plansWithCoverages, ...plansWithoutCoverages];
}

export function isCoverageOnPreviousDay(coverage: any, group: any) {
    return (
        coverage.scheduled != null &&
        moment(coverage.scheduled).isBefore(moment(group, DATE_FORMAT), 'day')
    );
}


export function getCoveragesForDisplay(item: any, plan: any, group: any) {
    const currentCoverage: any = [];
    const previousCoverage: any = [];
    // get current and preview coverages
    (get(item, 'coverages') || [])
        .forEach((coverage: any) => {
            if (!get(plan, 'guid') || coverage.planning_id === get(plan, 'guid')) {
                if (isCoverageForExtraDay(coverage)) {
                    currentCoverage.push(coverage);
                } else if (isCoverageOnPreviousDay(coverage, group)) {
                    previousCoverage.push(coverage);
                } else {
                    currentCoverage.push(coverage);
                }
            }
        });

    return {current: currentCoverage, previous: previousCoverage};
}

export function getListItems(groups: any, itemsById: any) {
    const listItems: any = [];

    groups.forEach((group: any) => {
        group.items.forEach((_id: any) => {
            const plans = getPlanningItemsByGroup(itemsById[_id], group.date);
            if (plans.length > 0) {
                plans.forEach((plan: any) => {
                    listItems.push({_id, group: group.date, plan});
                });
            } else {
                listItems.push({_id, group: group.date, plan: null});
            }
        });
    });
    return listItems;
}

export function isCoverageBeingUpdated(coverage: any) {
    return get(coverage, 'deliveries[0].delivery_state', null) &&
        !['published', 'corrected'].includes(coverage.deliveries[0].delivery_state);
}

export const groupRegions = (filter: any, aggregations: any, props: any) => {
    if (props.locators && Object.keys(props.locators).length > 0) {
        let regions = sortBy(props.locators.filter((l: any) => l.state).map((l: any) => ({...l, 'key': l.name, 'label': l.state})), 'label');
        const others = props.locators.filter((l: any) => !l.state).map((l: any) => ({...l, 'key': l.name, 'label': l.country || l.world_region}));
        const separator: any = {'key': 'divider'};

        if (others.length > 0) {
            if (regions.length > 0) {
                regions.push(separator);
            }
            regions = [...regions, ...sortBy(others, 'label')];
        }

        return regions;
    }

    return aggregations[filter.field].buckets;
};

export const getRegionName = (key: any, locator: any) => locator.label || key;

export const isItemTBC = (item: any) => (
    !get(item, 'event') ? get(item, `planning_items[0].${TO_BE_CONFIRMED_FIELD}`) : get(item, `event.${TO_BE_CONFIRMED_FIELD}`)
);


/**
 * Format coverage date ('HH:mm DD/MM')
 *
 * @param {String} dateString
 * @return {String}
 */
export function formatCoverageDate(coverage: any) {
    return get(coverage, TO_BE_CONFIRMED_FIELD) ?
        `${parseDate(coverage.scheduled).format(COVERAGE_DATE_FORMAT)} ${TO_BE_CONFIRMED_TEXT}` :
        parseDate(coverage.scheduled).format(COVERAGE_DATE_TIME_FORMAT);
}

export const getCoverageTooltip = (coverage: any, beingUpdated?: any) => {
    const slugline = coverage.item_slugline || coverage.slugline;
    const coverageType = getCoverageDisplayName(coverage.coverage_type);
    const coverageScheduled = moment(coverage.scheduled);

    if (coverage.workflow_status === WORKFLOW_STATUS.DRAFT) {
        return gettext('{{ type }} coverage {{ slugline }} {{ status_text }}', {
            type: coverageType,
            slugline: slugline,
            status_text: getCoverageStatusText(coverage)
        });
    } else if (coverage.workflow_status === WORKFLOW_STATUS.ASSIGNED) {
        return gettext('Planned {{ type }} coverage {{ slugline }}, expected {{date}} at {{time}}', {
            type: coverageType,
            slugline: slugline,
            date: formatDate(coverageScheduled),
            time: formatTime(coverageScheduled),
        });
    } else if (coverage.workflow_status === WORKFLOW_STATUS.ACTIVE) {
        return gettext('{{ type }} coverage {{ slugline }} in progress, expected {{date}} at {{time}}', {
            type: coverageType,
            slugline: slugline,
            date: formatDate(coverageScheduled),
            time: formatTime(coverageScheduled),
        });
    } else if (coverage.workflow_status === WORKFLOW_STATUS.CANCELLED) {
        return gettext('{{ type }} coverage {{slugline}} cancelled', {
            type: coverageType,
            slugline: slugline,
        });
    } else if (coverage.workflow_status === WORKFLOW_STATUS.COMPLETED) {
        let deliveryState: any;
        if (get(coverage, 'deliveries.length', 0) > 1) {
            deliveryState = beingUpdated ? gettext('(update to come)') : gettext('(updated)');
        }

        return gettext('{{ type }} coverage {{ slugline }} available {{deliveryState}}', {
            type: coverageType,
            slugline: slugline,
            deliveryState: deliveryState
        });
    }

    return gettext('{{ type }} coverage', {type: coverageType});
};

function getScheduleType(item: any) {
    const start = moment(item.dates.start)
    const end = moment(item.dates.end);
    const duration = end.diff(start, 'minutes');

    if (item.dates.all_day) {
        return duration === 0 ? SCHEDULE_TYPE.ALL_DAY : SCHEDULE_TYPE.MULTI_DAY;
    }

    if (item.dates.no_end_time) {
        return SCHEDULE_TYPE.NO_DURATION;
    }

    if (duration > DAY_IN_MINUTES || !start.isSame(end, 'day')) {
        return SCHEDULE_TYPE.MULTI_DAY;
    }

    if (duration === DAY_IN_MINUTES && start.isSame(end, 'day')) {
        return SCHEDULE_TYPE.ALL_DAY;
    }

    if (duration === 0) {
        return SCHEDULE_TYPE.NO_DURATION;
    }

    return SCHEDULE_TYPE.REGULAR;
}

/**
 * Format agenda item start and end dates
 *
 * @param {String} dateString
 * @param {String} group: date of the selected event group
 * @param {Object} options
 * @return {Array} [time string, date string]
 */
export function formatAgendaDate(item: any, group: any, {localTimeZone = true, onlyDates = false}) {
    const getFormattedTimezone = (date: any) => {
        let tzStr = date.format('z');
        if (tzStr.indexOf('+0') >= 0) {
            return tzStr.replace('+0', 'GMT+');
        }

        if (tzStr.indexOf('+') >= 0) {
            return tzStr.replace('+', 'GMT+');
        }

        return tzStr;
    };

    const isTBCItem = isItemTBC(item);
    let start = parseDate(item.dates.start, item.dates.all_day);
    let end = parseDate(item.dates.end, item.dates.all_day || item.dates.no_end_time);
    let dateGroup = group ? moment(group, DATE_FORMAT) : null;

    let isGroupBetweenEventDates = dateGroup ?
        start.isSameOrBefore(dateGroup, 'day') && end.isSameOrAfter(dateGroup, 'day') : true;

    if (!isGroupBetweenEventDates && hasCoverages(item)) {
        // we rendering for extra days
        const scheduleDates = item.coverages
            .map((coverage: any) => {
                if (isCoverageForExtraDay(coverage)) {
                    return coverage.scheduled;
                }
                return null;
            })
            .filter((d: any) => d)
            .sort((a: any, b: any) => {
                if (a < b) return -1;
                if (a > b) return 1;
                return 0;
            });
        if (scheduleDates.length > 0) {
            start = moment(scheduleDates[0]);
        }
    }

    const scheduleType = getScheduleType(item);
    const startDate = formatDate(start);
    const startTime = formatTime(start);
    const endDate = formatDate(end);
    const endTime = formatTime(end);
    const timezone = localTimeZone ? '' : getFormattedTimezone(start);

    switch (true) {
    case isTBCItem && startDate !== endDate:
        return gettext('{{startDate}} to {{endDate}} (Time to be confirmed)', {
            startDate,
            endDate,
        });

    case isTBCItem:
        return gettext('{{startDate}} (Time to be confirmed)', {
            startDate,
        });

    case startDate !== endDate && (item.dates.all_day || onlyDates || (startTime === '00:00' && endTime === '23:59')):
        return gettext('{{startDate}} to {{endDate}}', {
            startDate,
            endDate,
        });

    case startDate === endDate && (item.dates.all_day || onlyDates || scheduleType === SCHEDULE_TYPE.ALL_DAY):
        return startDate;

    case item.dates.no_end_time && startDate !== endDate:
        return gettext('{{startTime}} {{startDate}} - {{endDate}} {{timezone}}', {
            startTime,
            startDate,
            endDate,
            timezone,
        });

    case item.dates.no_end_time || scheduleType === SCHEDULE_TYPE.NO_DURATION:
        return gettext('{{startTime}} {{startDate}} {{timezone}}', {
            startTime,
            startDate,
            timezone,
        });

    case scheduleType === SCHEDULE_TYPE.REGULAR:
        return gettext('{{startTime}} - {{endTime}} {{startDate}} {{timezone}}', {
            startTime,
            startDate,
            endTime,
            timezone,
        });

    case scheduleType === SCHEDULE_TYPE.MULTI_DAY:
        return gettext('{{startTime}} {{startDate}} to {{endTime}} {{endDate}} {{timezone}}', {
            startTime,
            startDate,
            endTime,
            endDate,
            timezone,
        });

    default:
        console.warn('not sure about the datetime format', item, scheduleType);
        return gettext('{{startTime}} {{startDate}} to {{endTime}} {{endDate}} {{timezone}}', {
            startTime,
            startDate,
            endTime,
            endDate,
            timezone
        });
    }
}
