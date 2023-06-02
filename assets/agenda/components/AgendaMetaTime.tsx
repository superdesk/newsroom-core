import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import {bem} from 'ui/utils';
import {formatAgendaDate, hasCoverages} from '../utils';

import AgendaItemTimeUpdater from './AgendaItemTimeUpdater';

function format(item, group, onlyDates) {
    return (
        <span key="date">
            {formatAgendaDate(item, group, {onlyDates})}
        </span>
    );
}

function getCalendarClass(item) {
    if (item.state === 'rescheduled') {
        return 'icon--orange';
    }

    if (item.state === 'cancelled') {
        return 'icon--red';
    }

    if (hasCoverages(item)) {
        return 'icon--green';
    } else {
        return 'icon--gray-dark';
    }
}

export default function AgendaMetaTime({item, borderRight, isRecurring, group, isMobilePhone, onlyDates}) {
    const times = (
        <div key="times" className={classNames(
            bem('wire-articles__item', 'meta-time', {'border-right': borderRight}),
            {'w-100': isMobilePhone},
            {'m-0': onlyDates})}>
            {format(item, group, onlyDates)}
        </div>
    );

    if (onlyDates) {
        return times;
    }

    const icons = (
        <div key="icon" className={bem('wire-articles__item', 'icons',{'dashed-border': !isMobilePhone})}>
            <span className={classNames(
                'wire-articles__item__icon',
                {'dashed-border': isMobilePhone}
            )}>
                <i className={`icon--calendar ${getCalendarClass(item)}`} />
                {isRecurring && <span className="time-icon"><i className="icon-small--repeat" /></span>}
            </span>
        </div>
    );

    return isMobilePhone ?
        [times, icons] :
        [icons, times, <AgendaItemTimeUpdater key="timeUpdate" item={item} borderRight={borderRight} />];
}

AgendaMetaTime.propTypes = {
    item: PropTypes.object,
    borderRight: PropTypes.bool,
    isRecurring: PropTypes.bool,
    group: PropTypes.string,
    isMobilePhone: PropTypes.bool,
    onlyDates: PropTypes.bool,
};

AgendaMetaTime.defaultProps = {
    isRecurring: false,
    hasCoverage: false,
    isMobilePhone: false,
    borderRight: false,
};
