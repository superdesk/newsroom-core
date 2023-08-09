import React from 'react';
import PropTypes from 'prop-types';
import {wordCount, gettext} from 'utils';

export function WordCount ({item}: any) {
    return <span>{wordCount(item)} {gettext('words')}</span>;
}

WordCount.propTypes = {
    item: PropTypes.object
};
