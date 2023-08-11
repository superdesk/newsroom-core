import React from 'react';
import PropTypes from 'prop-types';

function InputWrapper({error, name, label, children, testId}: any) {
    let wrapperClass = 'form-group';

    if (error && error.length > 0) {
        wrapperClass += ' has-error';
    }

    if (!name) {
        name = `input-${label}`;
    }

    return (<div className={wrapperClass} data-test-id={testId}>{children}</div>);
}

InputWrapper.propTypes = {
    error: PropTypes.object,
    name: PropTypes.string,
    children: PropTypes.node,
    label: PropTypes.string,
    testId: PropTypes.string,
};

export default InputWrapper;
