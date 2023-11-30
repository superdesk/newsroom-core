import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment-timezone';
import {get} from 'lodash';
import classNames from 'classnames';

import {bem} from 'ui/utils';
import {formatAgendaDate, isItemTBC} from '../utils';
import {shouldRenderLocation} from'maps/utils';

export default function AgendaTime({item, children}: any) {
    const tbcItem = isItemTBC(item);
    const getClassNames = (modifier: any = 'event') => {
        return bem('wire-column__preview', 'date', modifier);
    };
    const startDateInRemoteTZ = moment.tz(moment(item.dates.start).utc(), item.dates.tz);
    const isRemoteTimezone = get(item, 'dates.tz') &&
        moment.tz(moment.tz.guess()).format('Z') !== startDateInRemoteTZ.format('Z');

    const getDates = (remoteTz: any = false) => {
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
                    all_day: item.dates.all_day,
                    no_end_time: item.dates.no_end_time,
                },
            };

            return (
                <div key='remote-time' className={classNames(
                    getClassNames(),
                    getClassNames('remote'),
                    {'p-0': isItemTBC})}>
                    {formatAgendaDate(new_dates, undefined, {localTimeZone: false})}
                </div>
            );
        }

        return (
            <div key='time' className={getClassNames('event')}>
                {formatAgendaDate(item, undefined, {})}
            </div>
        );
    };

    const margin = !isRemoteTimezone && !shouldRenderLocation(item) && !tbcItem;

    return (
        <React.Fragment>
            <div key='local-time' className={classNames('wire-column__preview__content-header', {'mb-0': !margin, 'mb-2': margin})}>
                {getDates() !== null ? (
                    <div className={classNames(getClassNames(), {'p-0': isRemoteTimezone || tbcItem})}>
                        {getDates()}
                    </div>
                ) : null}
                {children}
            </div>
            {getDates(true)}
        </React.Fragment>
    );
}

AgendaTime.propTypes = {
    item: PropTypes.object.isRequired,
    children: PropTypes.node,
};
