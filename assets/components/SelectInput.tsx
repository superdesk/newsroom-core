import React from 'react';
import {gettext} from 'utils';

export interface ISelectInputProps {
    name: string;
    label: string;
    onChange(event: React.ChangeEvent<HTMLSelectElement>): void;
    defaultOption?: string;
    value?: string;
    error?: Array<string>;
    options: Array<{
        text: string;
        value: string;
    }>;
    className?: string;
    readOnly?: boolean;
}

const SelectInput: React.FC<ISelectInputProps> = ({
    name,
    label,
    onChange,
    defaultOption,
    value,
    error,
    options,
    className,
    readOnly
}): React.ReactElement => {
    return (
        <div
            className={className ? className : 'form-group'}
            data-test-id={`field-${name}`}
        >
            <label htmlFor={name}>{label}</label>
            <div className="field">
                <select
                    id={name}
                    name={name}
                    value={value || ''}
                    onChange={onChange}
                    className="form-control"
                    disabled={readOnly}>
                    {defaultOption != null &&
                        <option value="">{defaultOption}</option>
                    }
                    {options.map((option: any) => {
                        return <option key={option.value} value={option.value}>{gettext(option.text)}</option>;
                    })}
                </select>
                {error && <div className="alert alert-danger">{error}</div>}
            </div>
        </div>
    );
};

export default SelectInput;
