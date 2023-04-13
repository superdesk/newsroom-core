import React from 'react';
import PropTypes from 'prop-types';
import {fullDate} from 'assets/utils';

export function VersionCreated ({item}: any) {
    return (
        <time
            dateTime={fullDate(
                item.versioncreated
            )}
        >
            {fullDate(item.versioncreated)}
        </time>
    );
}

VersionCreated.propTypes = {
    item: PropTypes.object
};
