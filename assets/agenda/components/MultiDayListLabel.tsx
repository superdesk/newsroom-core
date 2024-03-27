import * as React from 'react';

import {gettext} from 'utils';

interface IProps {
    current: number;
    days: number;
}

function getLabelSectionClass(current: number, days: number): string {
    if (current === 1) {
        return 'multiday-label--start';
    } else if (current === days) {
        return 'multiday-label--end';
    }

    return 'multiday-label--mid';
}

function getCurrentOccurrenceNumber(current: number, days: number): number {
    if (current < 1) {
        return 1;
    } else if (current > days) {
        return days;
    }
    return current;
}

export const MultiDayListLabel = React.memo(({current, days}: IProps) => (
    <span className="multiday-label__wrap ms-2">
        <span className={`multiday-label ${getLabelSectionClass(current, days)}`}>
            <span className="multiday-label__label">{gettext('Day:')}</span>
            <span className="multiday-label__value">
                <span>{getCurrentOccurrenceNumber(current, days)}</span>
                <span className="multiday-label__value-divide">/</span>
                <span>{days}</span>
            </span>
        </span>
    </span>
));
