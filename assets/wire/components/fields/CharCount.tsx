import React from 'react';
import PropTypes from 'prop-types';
import {characterCount, gettext} from 'utils';

export function CharCount ({item}: any) {
    return <span className="meta-info-item meta-info-item--char-count">{characterCount(item)} {gettext('characters')}</span>;
}

CharCount.propTypes = {
    item: PropTypes.object
};

