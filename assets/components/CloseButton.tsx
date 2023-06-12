import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';

function CloseButton({onClick}: any) {
    return (
        <button type="button"
            className="close"
            aria-label={gettext('Close')}
            role="button"
            onClick={onClick}>
            <span aria-hidden="true">&times;</span>
        </button>
    );
}

CloseButton.propTypes = {
    onClick: PropTypes.func.isRequired,
};

export default CloseButton;
