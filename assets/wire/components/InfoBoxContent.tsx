import React from 'react';
import PropTypes from 'prop-types';

export default function InfoBoxContent({element}: any) {
    return (
        <div className="info-box__content">
            {element}
        </div>
    );
}

InfoBoxContent.propTypes = {
    element: PropTypes.element,
};