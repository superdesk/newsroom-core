import React from 'react';
import PropTypes from 'prop-types';

import InputWrapper from './InputWrapper';

import {gettext} from 'utils';

function TextInput({
    type,
    name,
    label,
    labelClasses,
    onChange,
    value,
    error,
    required,
    readOnly,
    maxLength,
    placeholder,
    description,
    min,
    autoFocus,
    copyAction,
    ...props
}: any) {
    return (
        <InputWrapper error={error} name={name} testId={`field-${name}`}>
            {label && (
                <label htmlFor={name} className={labelClasses}>{label}</label>
            )}
            {copyAction &&
                <button
                    className='icon-button'
                    onClick={(e: any) => {e.preventDefault();navigator.clipboard.writeText(value);}}
                    title={gettext('Copy')}
                >
                    <i className='icon--copy'></i>
                </button>
            }

            <div className="field">
                <input
                    type={type || 'text'}
                    id={name}
                    name={name}
                    className="form-control"
                    value={value}
                    onChange={onChange}
                    required={required}
                    maxLength={maxLength}
                    disabled={readOnly}
                    placeholder={placeholder}
                    min={min}
                    autoFocus={autoFocus}
                    {...props}
                />
                {error && <div className="alert alert-danger">{error}</div>}
                {description && <small className="form-text">{description}</small>}
            </div>
        </InputWrapper>
    );
}

TextInput.propTypes = {
    type: PropTypes.string,
    label: PropTypes.string,
    labelClasses: PropTypes.string,
    name: PropTypes.string,
    value: PropTypes.string,
    copyAction: PropTypes.bool,
    error: PropTypes.arrayOf(PropTypes.string),
    onChange: PropTypes.func,
    required: PropTypes.bool,
    readOnly: PropTypes.bool,
    maxLength: PropTypes.number,
    placeholder: PropTypes.string,
    description: PropTypes.string,
    min: PropTypes.number,
    autoFocus: PropTypes.bool,
};

TextInput.defaultProps = {autoFocus: false};

const component: React.ComponentType<any> = TextInput;

export default component;
