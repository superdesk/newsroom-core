import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';
import {get} from 'lodash';

function getHighlightColorForUrgency(item: any, listConfig: any) {
    return item.urgency > 0 &&
        listConfig &&
        listConfig.highlights &&
        listConfig.highlights.urgency &&
        listConfig.highlights.urgency.length >= item.urgency
        ? listConfig.highlights.urgency[item.urgency - 1]
        : null;
}

export function UrgencyItemBorder({item, listConfig}: any) {
    const urgencyHighlightColor = getHighlightColorForUrgency(item, listConfig);

    if (!urgencyHighlightColor) {
        return null;
    }

    return <span
        className='wire-articles__item-highlight-border'
        style={{
            backgroundColor: urgencyHighlightColor,
        }}
    ></span>;
}

UrgencyItemBorder.propTypes = {
    item: PropTypes.object,
    listConfig: PropTypes.object,
};

const DEFAULT_URGENCY = 4;

export function UrgencyLabel ({item, listConfig, filterGroupLabels, alwaysShow = false}: any) {
    const urgencyHighlightColor = getHighlightColorForUrgency(item, listConfig);
    const label = get(filterGroupLabels, 'urgency', gettext('News Value'));
    const value = item.urgency || DEFAULT_URGENCY;
    const text = label + ': ' + value;

    if (!urgencyHighlightColor && alwaysShow) {
        return (
            <span>{text}</span>
        );
    } else if (!urgencyHighlightColor && !alwaysShow) {
        return null;
    }

    return (
        <span
            className={'label label--rounded'}
            style={{
                color: urgencyHighlightColor,
                // 8.24% is the old '15' hex alpha (21/255), but works for any valid CSS color
                backgroundColor: `color-mix(in srgb, ${urgencyHighlightColor} 8.24%, transparent)`,
            }}
        >{text}</span>
    );
}

UrgencyLabel.propTypes = {
    item: PropTypes.object,
    listConfig: PropTypes.object,
    alwaysShow: PropTypes.bool,
    filterGroupLabels: PropTypes.object,
};
