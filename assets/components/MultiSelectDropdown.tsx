import React, {Fragment} from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {gettext} from 'utils';
import {Dropdown} from './Dropdown';

function MultiSelectDropdown({values, label, field, options, onChange, showAllButton, multi}) {
    const onChanged = (option: any) => {
        if (multi) {
            if (option === 'all') {
                onChange(field, []);
            } else if (values.includes(option)) {
                onChange(field, values.filter((o) => o !== option));
            } else {
                onChange(field, [...values, option]);
            }
        } else {
            if (option === 'all' || values === option) {
                onChange(field, null);
            } else {
                onChange(field, option);
            }
        }
    };

    const isActive = (multi && !!values.length) || (!multi && values !== null);

    let buttonLabel = label;

    if (!multi && !values) {
        buttonLabel = gettext('All {{label}}', {label});
    }

    if (!multi && values) {
        buttonLabel = values;
    }

    return (
        <Dropdown
            key={field}
            label={buttonLabel}
            icon={'icon-small--arrow-down'}
            isActive={isActive}
        >
            {showAllButton && (
                <Fragment>
                    <button
                        className='dropdown-item'
                        onClick={onChanged.bind(null, 'all')}
                    >
                        <i className={classNames(
                            'me-2',
                            {
                                'icon--': isActive,
                                'icon--check': !isActive,
                            }
                        )}
                        />
                        <span>All {label}</span>
                    </button>
                    <div className='dropdown-divider' />
                </Fragment>
            )}
            {options.map((option) => (
                <Fragment key={option.value}>
                    <button
                        className='dropdown-item'
                        onClick={onChanged.bind(null, option.value)}
                    >
                        <i className={classNames(
                            'me-2',
                            {
                                'icon--': (multi && !values.includes(option.value)) ||
                                    (!multi && values !== option.value),
                                'icon--check': (multi && values.includes(option.value)) ||
                                    (!multi && values === option.value),
                            }
                        )}
                        />
                        <span>{option.label}</span>
                    </button>
                </Fragment>
            ))}
        </Dropdown>
    );
}

MultiSelectDropdown.propTypes = {
    values: PropTypes.oneOfType([
        PropTypes.arrayOf(PropTypes.string),
        PropTypes.string,
        PropTypes.shape({
            label: PropTypes.string,
            value: PropTypes.string,
        }),
    ]),
    options: PropTypes.arrayOf(
        PropTypes.shape({
            value: PropTypes.string,
            label: PropTypes.string,
        })
    ),
    field: PropTypes.string,
    label: PropTypes.string,
    onChange: PropTypes.func,
    showAllButton: PropTypes.bool,
    multi: PropTypes.bool,
};

MultiSelectDropdown.defaultProps = {
    showAllButton: false,
    multi: true,
};

export default MultiSelectDropdown;
