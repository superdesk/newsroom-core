import PropTypes from 'prop-types';
import React from 'react';

export default function AgendaMap({image}: any) {
    return (
        image && <figure className="wire-column__preview__image">
            <span>
                {image}
            </span>
        </figure>
    );
}

AgendaMap.propTypes = {
    image: PropTypes.element,
};
