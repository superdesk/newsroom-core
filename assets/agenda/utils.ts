import {get, isEmpty, keyBy, sortBy} from 'lodash';
import moment from 'moment/moment';

import {IAgendaItem, IPlanningItem, IAgendaListGroup, IAgendaListGroupItem, ICoverage, IUser} from 'interfaces';
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
import {ISubject} from 'interfaces/common';

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

const COVERAGE_INTENDED = 'coverage intended';

export function getCoverageStatusText(coverage: any) {
    if (coverage.workflow_status === WORKFLOW_STATUS.DRAFT || coverage.coverage_status !== COVERAGE_INTENDED) {
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
    'coverage not planned': gettext('Coverage not planned'),
    'coverage not intended': gettext('Coverage not planned'),
    'coverage intended': gettext('Coverage planned'),
    'coverage not decided': gettext('Coverage on merit'),
    'coverage not decided yet': gettext('Coverage on merit'),
    'coverage upon request': gettext('Coverage on request'),
};

const WORKFLOW_STATUS_TEXTS = {
    [WORKFLOW_STATUS.ASSIGNED]: gettext('Coverage planned'),
    [WORKFLOW_STATUS.ACTIVE]: gettext('Coverage in progress'),
    [WORKFLOW_STATUS.COMPLETED]: gettext('Coverage available'),
    [WORKFLOW_STATUS.CANCELLED]: gettext('Coverage cancelled'),
};

export const WORKFLOW_COLORS = {
    [WORKFLOW_STATUS.DRAFT]: 'coverage--draft',
    [WORKFLOW_STATUS.ASSIGNED]: 'coverage--assigned',
    [WORKFLOW_STATUS.ACTIVE]: 'coverage--active',
    [WORKFLOW_STATUS.COMPLETED]: 'coverage--completed',
    [WORKFLOW_STATUS.CANCELLED]: 'coverage--cancelled',
};

export const COVERAGE_STATUS_COLORS = {
    'coverage intended': null,
    'coverage not planned': 'coverage--not-covering',
    'coverage not intended': 'coverage--not-covering',
    'coverage not decided': 'coverage--undecided',
    'coverage not decided yet': 'coverage--undecided',
    'coverage upon request': 'coverage--request',
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
export function hasCoverages(item: IAgendaItem): boolean {
    return item.coverages?.[0]?.coverage_id != null;
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

export function getCoverageAsigneeName(coverage: ICoverage) {
    return coverage.assigned_user_name || null;

}

export function getCoverageDeskName(coverage: ICoverage) {
    return coverage.assigned_desk_name || null;
}
/**
 * Test if an item is watched
 *
 * @param {Object} item
 * @param {String} userId
 * @return {Boolean}
 */
export function isWatched(item: IAgendaItem | ICoverage, userId?: IUser['_id']): boolean {
    return userId != null && item.watches?.includes(userId) === true;
}

/**
 * Test if a coverage is for given date string
 *
 * @param {Object} coverage
 * @param {String} dateString
 * @return {Boolean}
 */
export function isCoverageForExtraDay(coverage: ICoverage, dateString: string) {
    return coverage.scheduled != null && formatDate(moment(coverage.scheduled)) === dateString;
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
    const location = item.location?.[0];
    const locationAddress = location?.address;

    const locationArray: Array<string> = [
        location?.name ?? locationAddress?.title ?? '',
        locationAddress?.line?.[0] ?? '',
        locationAddress?.city ?? locationAddress?.area ?? '',
        locationAddress?.state ?? locationAddress?.locality ?? '',
        locationAddress?.postal_code ?? '',
        locationAddress?.country ?? '',
    ];

    return locationArray.filter((d: string) => d != null && d.trim() != '').map((loc) => loc.trim()).join(', ');
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

export function hasLocationNotes(item: IAgendaItem) {
    return get(item, 'location[0].details[0].length', 0) > 0;
}

export function getLocationDetails(item: IAgendaItem) {
    return item.location && item.location[0] && item.location[0].details && item.location[0].details[0];
}

/**
 * Returns public contacts
 *
 * @param {Object} item
 * @return {String}
 */
export function getPublicContacts(item: IAgendaItem) {
    const contacts = item.event?.event_contact_info ?? [];
    return contacts.filter((c) => c.public).map((c) => ({
        _id: c._id,
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
 */
export function getMomentDate(dateString?: number): moment.Moment {
    if (dateString) {
        return moment(dateString);
    }

    return moment();
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

export const getNextPendingScheduledUpdate = (coverage: any) => {
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

export function getHighlightedName(item: any) {
    if (item.es_highlight.name){
        return item.es_highlight.name[0];
    }
    else if (item.es_highlight.slugline){
        return item.es_highlight.slugline[0];
    }
    else if (item.es_highlight.headline){
        return item.es_highlight.headline[0];
    }
    else{
        return getName(item);
    }
}

/**
 * Get agenda item description
 *
 * @param {Object} item
 * @param {Object} plan
 * @return {String}
 */
export function getDescription(item: IAgendaItem, plan?: IPlanningItem): string {
    return plan?.description_text || item?.definition_short || '';
}

/**
 * Get agenda item highlighted description
 *
 * @param {Object} item
 * @param {Object} plan
 * @return {String}
 */
export function getHighlightedDescription(item: IAgendaItem, plan?: IPlanningItem): string {
    if (item.es_highlight?.description_text?.[0] != null) {
        return item.es_highlight.description_text[0];
    }
    else if (item.es_highlight?.definition_short?.[0] != null) {
        return item.es_highlight.definition_short[0];
    }
    else if (item.es_highlight?.definition_long?.[0] != null) {
        return item.es_highlight.definition_long[0];
    }
    else {
        return getDescription(item, plan);
    }
}


/**
 * Gets the extra days outside the event days
 *
 * @param {Object} item
 * @return {Array} list of dates
 */
export function getExtraDates(item: IAgendaItem): Array<moment.Moment> {
    return getDisplayDates(item).map((displayDate) => moment(displayDate.date));
}

/**
 * Get the display dates, filtering out those that didn't match Planning/Coverage search
 * @param item: Event or Planning item
 * @returns {Array.<{date: moment.Moment}>}
 */
function getDisplayDates(item: IAgendaItem): Array<{date: string}> {
    if (item._hits == null || item._hits.matched_planning_items == null) {
        return item.display_dates ?? [];
    } else if (item.planning_items == null || item.planning_items.length === 0) {
        return [];
    }

    const dates: Array<{date: string}> = [];
    const planningIds = item._hits.matched_planning_items;
    const coverageIds = item._hits.matched_coverages != null ?
        item._hits.matched_coverages :
        (item.coverages ?? []).map((coverage) => coverage.coverage_id);

    item.planning_items.forEach((plan) => {
        if (!planningIds.includes(plan._id)) {
            return;
        }

        const coverages = (plan.coverages ?? []).filter(
            (coverage) => coverage.scheduled != null || coverage.planning?.scheduled != null
        );

        if (!coverages.length) {
            if (plan.planning_date != null) {
                dates.push({date: plan.planning_date});
            }
            return;
        }

        coverages.forEach((coverage: any) => {
            if (!coverageIds.includes(coverage.coverage_id)) {
                return;
            }

            if (coverage.planning?.scheduled != null) {
                // when restricted coverage is enabled
                // there might be no date
                dates.push({date: coverage.planning.scheduled});
            }
        });
    });

    return dates;
}

/**
 * Checks if a date is in extra dates
 */
function containsExtraDate(dateToCheck: moment.Moment, extraDates: Array<moment.Moment>) {
    return extraDates
        .map((ed) => ed.format('YYYY-MM-DD'))
        .includes(dateToCheck.format('YYYY-MM-DD'));
}

// get start date in utc mode if there is no time info
export function getStartDate(item: IAgendaItem): moment.Moment {
    return item.dates.all_day === true ?
        moment.utc(item.dates.start) :
        moment(item.dates.start);
}

// get end date in utc mode if there is no end time info
export function getEndDate(item: IAgendaItem): moment.Moment {
    return item.dates.all_day === true ?
        moment.utc(item.dates.end || item.dates.start) :
        moment(item.dates.end || item.dates.start);
}

// compare days without being affected by timezone
const isBetweenDay = (day: moment.Moment, start: moment.Moment, end: moment.Moment, allDay=false, noEndTime=false) => {
    let testDay = day;
    let startDate = start;
    let endDate = end;

    if (allDay) {
        // we ignore times and only check dates
        startDate = moment(start.format('YYYY-MM-DD'));
        endDate = moment(end.format('YYYY-MM-DD'));
        testDay =  moment(day.format('YYYY-MM-DD'));
    }

    return testDay.isSameOrAfter(startDate, 'day') && testDay.isSameOrBefore(endDate, 'day');
};

/**
 * Groups given agenda items per given grouping
 * @param items: list of agenda items
 * @param activeDate: date that the grouping will start from
 * @param activeGrouping: type of grouping i.e. day, week, month
 */
export function groupItems(
    items: Array<IAgendaItem>,
    minDate: moment.Moment | undefined,
    maxDate: moment.Moment | undefined,
    activeGrouping: string,
    featuredOnly?: boolean
): Array<IAgendaListGroup> {
    if (items.length === 0) {
        return [];
    }

    const groupedItems: {[key: string]: Array<IAgendaItem>} = {};
    const grouper: (dateString: moment.Moment) => string = Groupers[activeGrouping];

    items
        // Filter out items that didn't match any Planning items
        .filter((item) => (
            (item.planning_items?.length ?? 0) === 0 ||
            item._hits?.matched_planning_items == null ||
            item._hits?.matched_planning_items.length > 0 ||
            item._hits?.matched_coverages?.length
        ))
        .forEach((item) => {
            const itemExtraDates = getExtraDates(item);
            const itemStartDate = getStartDate(item);
            let start: moment.Moment;

            if (item._display_from != null) {
                start = moment(item._display_from);
            } else {
                start = moment.min([
                    ...itemExtraDates,
                    itemStartDate,
                ]);

                if (minDate != null) {
                    start = moment.max(minDate, start);
                }
            }

            const itemEndDate = getEndDate(item);

            // If item is an event and was actioned (postponed, rescheduled, cancelled only incase of multi-day event)
            // actioned_date is set. In this case, use that as the cut off date.
            let end = item.event?.actioned_date != null ?
                moment(item.event.actioned_date) :
                null;
            if (end != null || !moment.isMoment(end)) {
                if (item._display_to != null) {
                    end = moment(item._display_to);
                } else {
                    const endDates = [
                        ...itemExtraDates,
                        // If event is all day the end timestamp is the same as
                        // start and depending on the local timezone offset it
                        // might not give enough room for the event to show up,
                        // so add an extra day for it.
                        itemEndDate.clone().add(1, 'd'),
                    ];

                    if (minDate != null) {
                        endDates.push(minDate);
                    }

                    end = moment.max(endDates);
                }
            }

            let key = null;
            end = maxDate != null ?
                moment.min(end, maxDate) :
                moment.min(end, start.clone().add(10, 'd')); // show each event for 10 days max not to destroy the UI

            // use clone otherwise it would modify start and potentially also maxStart, moments are mutable
            for (const day = start.clone(); day.isSameOrBefore(end, 'day'); day.add(1, 'd')) {
                const isBetween = isBetweenDay(day, itemStartDate, itemEndDate, item.dates.all_day, item.dates.no_end_time);
                const addGroupItem = isBetween || containsExtraDate(day, itemExtraDates);

                if (grouper(day) !== key && addGroupItem) {
                    key = grouper(day);
                    if (groupedItems[key] == null) {
                        groupedItems[key] = [];
                    }
                    groupedItems[key].push(item);
                }
            }
        });

    const groupedItemIds: {[group: string]: {day: Array<IAgendaItem['_id']>, hiddenItems: Array<IAgendaItem['_id']>}} = {};

    if (featuredOnly) {
        Object.keys(groupedItems).forEach((dateString) => {
            groupedItemIds[dateString] = {day: groupedItems[dateString].map((i) => i._id), hiddenItems: []};
        });
    } else {
        Object.keys(groupedItems).forEach((dateString) => {
            const itemsWithoutTime: Array<IAgendaItem['_id']> = [];
            const itemsWithTime: Array<IAgendaItem['_id']> = [];
            const hiddenItems: Array<IAgendaItem['_id']> = [];

            groupedItems[dateString].forEach((groupItem) => {
                const scheduleType = getScheduleType(groupItem);
                const itemStartDateGroup: string = grouper(getStartDate(groupItem));

                if (itemStartDateGroup !== dateString && scheduleType === SCHEDULE_TYPE.MULTI_DAY) {
                    hiddenItems.push(groupItem._id);
                } else if (isItemTBC(groupItem)) {
                    itemsWithoutTime.push(groupItem._id);
                } else {
                    itemsWithTime.push(groupItem._id);
                }
            });

            groupedItemIds[dateString] = {
                day: [
                    ...itemsWithoutTime,
                    ...itemsWithTime,
                ],
                hiddenItems: hiddenItems,
            };
        });
    }

    return sortGroups(Object.keys(groupedItemIds).map((dateString) => (
        {
            date: dateString,
            items: groupedItemIds[dateString].day,
            hiddenItems: groupedItemIds[dateString].hiddenItems,
        }
    )));
}

export function sortGroups(groups: Array<IAgendaListGroup>): Array<IAgendaListGroup> {
    const sorted = Array.from(groups);
    sorted.sort((a, b) => {
        const aUnix = moment(a.date, DATE_FORMAT).unix();
        const bUnix = moment(b.date, DATE_FORMAT).unix();

        return aUnix - bUnix;
    });

    return sorted;
}

/**
 * Get Planning Item for the day
 */
export function getPlanningItemsByGroup(item: IAgendaItem, group: string): Array<IPlanningItem> {
    const planningItems = item.planning_items || [];

    if (planningItems.length === 0) {
        return [];
    }

    // Planning item without coverages
    const plansWithoutCoverages = planningItems.filter((planningItem) => (
        formatDate(planningItem.planning_date) === group &&
        (planningItem.coverages?.length ?? 0) === 0
    ));

    const allPlans: {[itemId: string]: IPlanningItem} = keyBy(planningItems, '_id');
    const processed: {[itemId: string]: boolean} = {};

    // get unique plans for that group based on the coverage.
    const plansWithCoverages = (item.coverages || [])
        .filter((coverage) => {
            if (isCoverageForExtraDay(coverage, group) === false) {
                return false;
            }

            if (processed[coverage.planning_id] !== true) {
                processed[coverage.planning_id] = true;
                return true;
            }

            return false;
        })
        .map((coverage) => allPlans[coverage.planning_id]);

    return [...plansWithCoverages, ...plansWithoutCoverages];
}

export function isCoverageOnPreviousDay(coverage: any, group: any) {
    return (
        coverage.scheduled != null &&
        moment(coverage.scheduled).isBefore(moment(group, DATE_FORMAT), 'day')
    );
}


export function getCoveragesForDisplay(item: any, plan: any, group: any) {
    const currentCoverage: Array<ICoverage> = [];
    const previousCoverage: Array<ICoverage> = [];
    // get current and preview coverages
    (get(item, 'coverages') || [])
        .forEach((coverage: any) => {
            if (!get(plan, 'guid') || coverage.planning_id === get(plan, 'guid')) {
                if (isCoverageForExtraDay(coverage, group)) {
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

export function getListItems(
    groups: Array<IAgendaListGroup>,
    itemsById: {[itemId: string]: IAgendaItem},
    hiddenGroupsShown: {[dateString: string]: boolean} = {}
): Array<IAgendaListGroupItem> {
    const listItems: Array<IAgendaListGroupItem> = [];

    groups.forEach((group) => {
        const items = hiddenGroupsShown[group.date] === true ?
            [...group.hiddenItems, ...group.items] :
            group.items;
        items.forEach((itemId) => {
            const plans = getPlanningItemsByGroup(itemsById[itemId], group.date);

            if (plans.length > 0) {
                plans.forEach((plan) => {
                    listItems.push({_id: itemId, group: group.date, plan: plan._id});
                });
            } else {
                listItems.push({_id: itemId, group: group.date, plan: undefined});
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

export function isItemTBC(item: IAgendaItem): boolean {
    return item.event != null ?
        item.event._time_to_be_confirmed === true :
        item.planning_items?.[0]?._time_to_be_confirmed === true;
}


/**
 * Format coverage date ('HH:mm DD/MM')
 *
 * @param {String} dateString
 * @return {String}
 */
export function formatCoverageDate(coverage: ICoverage) {
    return get(coverage, TO_BE_CONFIRMED_FIELD) ?
        `${parseDate(coverage.scheduled).format(COVERAGE_DATE_FORMAT)} ${TO_BE_CONFIRMED_TEXT}` :
        parseDate(coverage.scheduled).format(COVERAGE_DATE_TIME_FORMAT);
}

export const getCoverageTooltip = (coverage: any, beingUpdated?: any) => {
    const slugline = coverage.item_slugline || coverage.slugline;
    const coverageType = getCoverageDisplayName(coverage.coverage_type);
    const coverageScheduled = moment(coverage.scheduled);
    const assignee = getCoverageAsigneeName(coverage);
    const desk = getCoverageDeskName(coverage);
    const assignedDetails = [
        assignee ? gettext('assignee: {{name}}', {name: assignee}) : '',
        desk ? gettext('desk: {{name}}', {name: desk}) : '',
    ].filter((x) => x !== '').join(', ');

    if (coverage.coverage_status !== COVERAGE_INTENDED) {
        return get(DRAFT_STATUS_TEXTS, coverage.coverage_status, '');
    } else if (coverage.workflow_status === WORKFLOW_STATUS.DRAFT) {
        return gettext('{{ type }} coverage {{ slugline }} {{ status_text }} {{assignedDetails}}', {
            type: coverageType,
            slugline: slugline,
            status_text: getCoverageStatusText(coverage),
            assignedDetails,
        });
    } else if (coverage.workflow_status === WORKFLOW_STATUS.ASSIGNED) {
        return gettext('Planned {{ type }} coverage {{ slugline }}, expected {{date}} at {{time}} {{assignedDetails}}', {
            type: coverageType,
            slugline: slugline,
            date: formatDate(coverageScheduled),
            time: formatTime(coverageScheduled),
            assignedDetails,
        });
    } else if (coverage.workflow_status === WORKFLOW_STATUS.ACTIVE) {
        return gettext('{{ type }} coverage {{ slugline }} in progress, expected {{date}} at {{time}} {{assignedDetails}}', {
            type: coverageType,
            slugline: slugline,
            date: formatDate(coverageScheduled),
            time: formatTime(coverageScheduled),
            assignedDetails,
        });
    } else if (coverage.workflow_status === WORKFLOW_STATUS.CANCELLED) {
        return gettext('{{ type }} coverage {{slugline}} cancelled {{assignedDetails}}', {
            type: coverageType,
            slugline: slugline,
            assignedDetails,
        });
    } else if (coverage.workflow_status === WORKFLOW_STATUS.COMPLETED) {
        let deliveryState: any;
        if (get(coverage, 'deliveries.length', 0) > 1) {
            deliveryState = beingUpdated ? gettext('(update to come)') : gettext('(updated)');
        }

        return gettext('{{ type }} coverage {{ slugline }} available {{deliveryState}} {{assignedDetails}}', {
            type: coverageType,
            slugline: slugline,
            deliveryState: deliveryState,
            assignedDetails,
        });
    }

    return gettext('{{ type }} coverage {{assignedDetails}}', {type: coverageType, assignedDetails});
};

function getScheduleType(item: IAgendaItem): string {
    const start = getStartDate(item);
    const end = getEndDate(item);
    const duration = end.diff(start, 'minutes');

    if (item.dates.all_day) {
        return duration === 0 ? SCHEDULE_TYPE.ALL_DAY : SCHEDULE_TYPE.MULTI_DAY;
    }

    if (item.dates.no_end_time && !start.isSame(end, 'day')) {
        return SCHEDULE_TYPE.MULTI_DAY;
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
export function formatAgendaDate(item: IAgendaItem, {localTimeZone = true, onlyDates = false} = {}) {
    function getFormattedTimezone(date: moment.Moment): string {
        const tzStr = date.format('z');
        if (tzStr.indexOf('+0') >= 0) {
            return tzStr.replace('+0', 'GMT+');
        }

        if (tzStr.indexOf('+') >= 0) {
            return tzStr.replace('+', 'GMT+');
        }

        return tzStr;
    }

    const isTBCItem = isItemTBC(item);
    const start = parseDate(item.dates.start, item.dates.all_day);
    const end = parseDate(item.dates.end, item.dates.all_day);

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

export const isTopStory = (subj: ISubject) => subj.scheme === window.newsroom.client_config.agenda_top_story_scheme;
