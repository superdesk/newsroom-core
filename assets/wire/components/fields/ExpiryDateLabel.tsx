import React from 'react';
import PropTypes from 'prop-types';
import {gettext, formatDate} from 'utils';

export function ExpiryDateLabel ({item, filterGroupLabels}: any) {
    if (item.expiry == null) {
        return null;
    }

    const label = filterGroupLabels?.expiry ?? gettext('Expiry Date');
    const value = formatDate(item.expiry);
    const text = label + ': ' + value;

    return (
        <span>{text}</span>
    );
}

ExpiryDateLabel.propTypes = {
    item: PropTypes.object,
    filterGroupLabels: PropTypes.object,
};
