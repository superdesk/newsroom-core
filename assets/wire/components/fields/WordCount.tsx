import React from 'react';
import PropTypes from 'prop-types';
import {wordCount, gettext} from 'utils';

export function WordCount ({item}: any) {
    return <span className="meta-info-item meta-info-item--word-count">{wordCount(item)} {gettext('words')}</span>;
}

WordCount.propTypes = {
    item: PropTypes.object
};
