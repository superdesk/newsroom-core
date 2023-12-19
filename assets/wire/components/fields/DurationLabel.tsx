import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';
import {IArticle} from 'interfaces';

interface IProps {
    item: IArticle,
    filterGroupLabels: {
        [field: string]: string;
    },
}

export function DurationLabel (props: IProps) {
    const {item, filterGroupLabels} = props;

    if (item.extra?.duration == null) {
        return null;
    }

    function zeroPad(number: number):string {
        if (number.toString().length < 2) {
            return `0${number}`;
        } else {
            return number.toString();
        }
    }

    function secondsToHHMMSS(seconds: number) {
        seconds = Number(seconds);

        const h = zeroPad(Math.floor(seconds / 3600));
        const m = zeroPad(Math.floor(seconds % 3600 / 60));
        const s = zeroPad(Math.floor(seconds % 3600 % 60));

        const value = `${h}:${m}:${s}`;
    
        return value;
    }

    const label = filterGroupLabels?.duration ?? gettext('Duration');
    const time = secondsToHHMMSS(item.extra.duration);
    const text = label + ': ' + time;

    return (
        <span>{text}</span>
    );
}
