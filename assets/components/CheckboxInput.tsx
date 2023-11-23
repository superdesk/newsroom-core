import React from 'react';
import classNames from 'classnames';
import PropTypes from 'prop-types';

interface IProps {
    name?: string;
    label: string;
    readOnly?: boolean;
    labelClass?: string;
    value?: boolean;
    onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

function CheckboxInput({name, label, onChange, value, labelClass, readOnly}: IProps) {
    if (!name) {
        name = `input-${label}`;
    }

    return (
        <div className={classNames('form-check', {'form-check--checked': value})} tabIndex={-1} data-test-id={`field-${name}`}>
            <input type="checkbox"
                name={name}
                className="form-check-input"
                checked={value}
                id={name}
                onChange={onChange}
                disabled={readOnly}
                tabIndex={0}
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
