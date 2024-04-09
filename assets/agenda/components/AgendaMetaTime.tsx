import React from 'react';
import classNames from 'classnames';
import moment from 'moment';

import {IAgendaItem} from 'interfaces';
import {bem} from 'ui/utils';
import {formatAgendaDate, getEndDate, getStartDate, hasCoverages} from '../utils';
import {DATE_FORMAT, formatDate} from 'utils';

import AgendaItemTimeUpdater from './AgendaItemTimeUpdater';
import {MultiDayListLabel} from './MultiDayListLabel';

interface IProps {
    group?: string;
    item: IAgendaItem;
    borderRight?: boolean;
    isRecurring?: boolean;
    isMobilePhone?: boolean;
    onlyDates?: boolean;
}

function format(item: IAgendaItem, onlyDates = true) {
    return (
        <span key="date">
            {formatAgendaDate(item, {onlyDates})}
        </span>
    );
}

function getCalendarClass(item: IAgendaItem) {
    if (item.state === 'rescheduled') {
        return 'icon--orange';
    } else if (item.state === 'cancelled') {
        return 'icon--red';
    } else if (hasCoverages(item)) {
        return 'icon--green';
    }

    return 'icon--default';
}

export default function AgendaMetaTime({item, borderRight, isRecurring, group, isMobilePhone, onlyDates}: IProps) {
    const icon = item.item_type === 'planning' ? 'icon--planning' : 'icon--calendar';
    const groupDate = moment(group, DATE_FORMAT);
    const startDate = moment(formatDate(getStartDate(item)), DATE_FORMAT);
    const endDate = moment(formatDate(getEndDate(item)), DATE_FORMAT);
    const diffDays = groupDate.diff(startDate, 'days') + 1;
    const itemDays = endDate.diff(startDate, 'days') + 1;
    const times = (
        <div key="times" className={classNames(
            bem('wire-articles__item', 'meta-time', {'border-right': borderRight}),
            {'w-100': isMobilePhone},
            {'m-0': onlyDates})}
        >
            {format(item, onlyDates === true)}
            {itemDays <= 1 ? null : (
                <MultiDayListLabel
                    current={diffDays}
                    days={itemDays}
                />
            )}
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
                <i className={`${icon} ${getCalendarClass(item)}`} />
                {isRecurring && <span className="time-icon"><i className="icon-small--repeat" /></span>}
            </span>
        </div>
    );

    return (
        <React.Fragment>
            {isMobilePhone ?
                [times, icons] :
                [icons, times, <AgendaItemTimeUpdater key="timeUpdate" item={item} borderRight={borderRight} />]}
        </React.Fragment>
    );
}
