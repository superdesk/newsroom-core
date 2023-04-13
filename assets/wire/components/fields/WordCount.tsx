import React from 'react';
import PropTypes from 'prop-types';
import {gettext, wordCount} from 'assets/utils';

export function WordCount ({item}: any) {
    return <span>{wordCount(item)} {gettext('words')}</span>;
}

WordCount.propTypes = {
    item: PropTypes.object
};
