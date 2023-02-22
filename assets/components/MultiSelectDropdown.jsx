import React, {Fragment} from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

class MultiSelectDropdown extends React.PureComponent {
    constructor(props) {
        super(props);

        this.dom = {button: null};
    }

    isActive(props) {
        return (props.multi && !!props.values.length) || (!props.multi && props.values !== null);
    }

    componentDidUpdate(prevProps) {
        const isActive = this.isActive(this.props);

        if (isActive !== this.isActive(prevProps) && this.dom.button != null) {
            // Manually add/remove the ``active`` class on the button through the DOM
            // As the dropdown menu doesn't hide if we manage this class name using React
            if (isActive) {
                this.dom.button.classList.add('active');
            } else {
                this.dom.button.classList.remove('active');
            }
        }
    }

    onChanged(option) {
        const {values, field, onChange, multi} = this.props;

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
    }

    render() {
        const {values, label, field, options, showAllButton, multi} = this.props;
        const isActive = this.isActive(this.props);

        return (
            <div className='btn-group' key={field}>
                <button
                    id={field}
                    type='button'
                    ref={(elem) => this.dom.button = elem}
                    className="btn btn-outline-primary btn-sm d-flex align-items-center px-2 ms-2"
                    aria-haspopup='true'
                    aria-expanded='false'
                    data-bs-toggle='dropdown'
                >
                    {multi && (
                        <span className='d-block'>{label}</span>
                    )}

                    {(!multi && !values) && (
                        <span className='d-block'>All {label}</span>
                    )}

                    {(!multi && values) && (
                        <span className='d-block'>{values}</span>
                    )}
                    <i className={classNames('icon-small--arrow-down ms-1', {'icon--white': isActive})}  />
                </button>
                <div className='dropdown-menu' aria-labelledby={field}>
                    {showAllButton && (
                        <Fragment>
                            <button
                                className='dropdown-item'
                                onClick={this.onChanged.bind(this, 'all')}
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
                                onClick={this.onChanged.bind(this, option.value)}
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
                </div>
            </div>
        );
    }
}

MultiSelectDropdown.propTypes = {
    values: PropTypes.oneOf([
        PropTypes.arrayOf(PropTypes.string),
        PropTypes.string,
        PropTypes.shape({
            label: PropTypes.string,
            value: PropTypes.string,
        }),
    ]),
    options: PropTypes.arrayOf(PropTypes.string),
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
