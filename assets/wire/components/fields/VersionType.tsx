import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'assets/utils';

export function VersionType({value}: any) {
    return (
        <span>{gettext('Version type: {{version}}', {version: value})}</span>
    );
}

VersionType.propTypes = {
    value: PropTypes.string,
};
