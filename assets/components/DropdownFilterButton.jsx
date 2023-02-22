import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

class DropdownFilterButton extends React.PureComponent {
    constructor(props) {
        super(props);

        this.dom = {button: null};
    }

    componentDidUpdate(prevProps) {
        if (this.props.isActive !== prevProps.isActive && this.dom.button != null) {
            // Manually add/remove the ``active`` class on the button through the DOM
            // As the dropdown menu doesn't hide if we manage this class name using React
            if (this.props.isActive) {
                this.dom.button.classList.add('active');
            } else {
                this.dom.button.classList.remove('active');
            }
        }
    }

    render() {
        const {id, isActive, autoToggle, onClick, icon, label, textOnly, iconColour} = this.props;

        return (
            <button
                id={id}
                key={id}
                type="button"
                ref={(elem) => this.dom.button = elem}
                className={classNames(
                    'btn btn-sm d-flex align-items-center px-2 ms-2',
                    {
                        'btn-text-only': textOnly,
                        'btn-outline-primary': !textOnly,
                    }
                )}
                data-bs-toggle={autoToggle ? 'dropdown' : undefined}
                aria-haspopup="true"
                aria-expanded="false"
                onClick={onClick}
            >
                {!icon ? null : (
                    <i className={`${icon} d-md-none`} />
                )}
                {textOnly ? label : (
                    <span className="d-none d-md-block">
                        {label}
                    </span>
                )}
                <i className={classNames(
                    'icon-small--arrow-down ms-1',
                    {
                        'icon--white': isActive && !iconColour,
                        [`icon--${iconColour}`]: iconColour
                    }
                )} />
            </button>
        );
    }
}

DropdownFilterButton.propTypes = {
    id: PropTypes.string,
    isActive: PropTypes.bool,
    autoToggle: PropTypes.bool,
    onClick: PropTypes.func,
    icon: PropTypes.string,
    label: PropTypes.oneOfType([
        PropTypes.arrayOf(PropTypes.node),
        PropTypes.node,
        PropTypes.string
    ]),
    textOnly: PropTypes.bool,
    iconColour: PropTypes.string,
};

DropdownFilterButton.defaultProps = {autoToggle: true};

export default DropdownFilterButton;
