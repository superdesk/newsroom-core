import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment-timezone';
import {get} from 'lodash';
import classNames from 'classnames';

import {bem} from 'ui/utils';
import {SCHEDULE_TYPE, isItemTBC, TO_BE_CONFIRMED_TEXT} from '../utils';
import {formatAgendaDate, getScheduleType} from 'utils';
import {shouldRenderLocation} from'maps/utils';

export default function AgendaTime({item, children}) {
    const tbcItem = isItemTBC(item);
    const getClassNames = (modifier = 'event') => {
        return bem('wire-column__preview', 'date', modifier);
    };
    const startDateInRemoteTZ = moment.tz(moment(item.dates.start).utc(), item.dates.tz);
    const isRemoteTimezone = get(item, 'dates.tz') &&
        moment.tz(moment.tz.guess()).format('Z') !== startDateInRemoteTZ.format('Z');
    const getDates = (remoteTz = false) => {
        let dates;

        if (remoteTz) {
            if (!isRemoteTimezone) {
                return null;
            }

            const new_dates = {
                ...item,
                dates: {
                    start: startDateInRemoteTZ,
                    end: moment.tz(moment(item.dates.end).utc(), item.dates.tz),
                    tz: item.dates.tz,
                }
            };
            dates = formatAgendaDate(new_dates, null, false);
            return (<div key='remote-time' className={classNames(
                getClassNames(),
                getClassNames('remote'),
                {'p-0': isItemTBC})}>
                {dates[0]} {dates[1]}
            </div>);
        } else {
            dates = formatAgendaDate(item, null);
        }

        return [(
            <div key='time' className={getClassNames('event')}>
                {dates[1]} {dates[0]}
            </div>
        )];
    };

    const margin = !isRemoteTimezone && !shouldRenderLocation(item) && !tbcItem;

    let retElement = [(<div key='local-time' className={classNames('wire-column__preview__content-header', {'mb-0': !margin, 'mb-2': margin})}>
        <div className={classNames(getClassNames(), {'p-0': isRemoteTimezone || tbcItem})}>
            {getDates()}
        </div>
        {children}
    </div>),
    getDates(true)];

    if (tbcItem && getScheduleType(item) === SCHEDULE_TYPE.MULTI_DAY) {
        retElement.push((<div key='to-be-confirmed-time' className={classNames(getClassNames(), getClassNames('remote'))}>
            {`${TO_BE_CONFIRMED_TEXT}`}</div>));
    }

    return retElement;
}

AgendaTime.propTypes = {
    item: PropTypes.object.isRequired,
    children: PropTypes.node,
};