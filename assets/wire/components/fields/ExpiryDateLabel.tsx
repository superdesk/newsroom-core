import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';
import {get} from 'lodash';

export function ExpiryDateLabel ({item, filterGroupLabels}: any) {
    if (item.expiry == null) {
        return null;
    }

    const label = get(filterGroupLabels, 'expiry', gettext('Expiry Date'));
    const value = item.expiry;
    const text = label + ': ' + value;

    return (
        <span>{text}</span>
    );
}

ExpiryDateLabel.propTypes = {
    item: PropTypes.object,
    filterGroupLabels: PropTypes.object,
};
