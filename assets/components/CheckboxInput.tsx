import React from 'react';
import classNames from 'classnames';
import PropTypes from 'prop-types';


function CheckboxInput({name, label, onChange, value, labelClass, readOnly}) {
    if (!name) {
        name = `input-${label}`;
    }

    return (
        <div className='form-check' tabIndex='-1'>
            <input type="checkbox"
                name={name}
                className="form-check-input"
                checked={value}
                id={name}
                onChange={onChange}
                disabled={readOnly}
                tabIndex='0'
            />
            <label className={classNames('form-check-label', labelClass)} htmlFor={name}>{label}</label>
        </div>
    );
}

CheckboxInput.propTypes = {
    name: PropTypes.string,
    label: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    value: PropTypes.bool.isRequired,
    labelClass: PropTypes.string,
    readOnly: PropTypes.bool,
};

export default CheckboxInput;
