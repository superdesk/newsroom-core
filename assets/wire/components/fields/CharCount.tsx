import React from 'react';
import PropTypes from 'prop-types';
import {characterCount, gettext} from 'assets/utils';

export function CharCount ({item}: any) {
    return <span>{characterCount(item)} {gettext('characters')}</span>;
}

CharCount.propTypes = {
    item: PropTypes.object
};

