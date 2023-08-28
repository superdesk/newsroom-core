import React from 'react';
import PropTypes from 'prop-types';

export function Source ({item}: any) {
    return <span className="meta-info-item meta-info-item--source">{item.source}</span>;
}

Source.propTypes = {
    item: PropTypes.object
};
