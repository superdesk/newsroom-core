import React from 'react';
import PropTypes from 'prop-types';
import {Tooltip} from 'bootstrap';

import {gettext, isTouchDevice} from '../../utils';

class ProfileToggle extends React.Component<any, any> {
    static propTypes: any;
    tooltip: any;
    elem: any;
    constructor(props: any) {
        super(props);

        this.tooltip = null;
    }

    componentDidMount() {
        if (!isTouchDevice() && this.elem && !this.tooltip) {
            this.tooltip = new Tooltip(this.elem);
        }
    }

    componentWillUnmount() {
        if (this.elem && this.tooltip) {
            this.tooltip.dispose();
        }
    }

    render() {
        const initials = this.props.user.first_name[0].toLocaleUpperCase() + this.props.user.last_name[0].toLocaleUpperCase();

        return (
            <div
                className="header-profile"
                role="button"
                tabIndex={0}
                aria-expanded={this.props.expanded}
                aria-label={gettext('{{initials}}: user menu for {{name}}', {
                    initials,
                    name: `${this.props.user.first_name} ${this.props.user.last_name}`,
                })}
                onClick={(event: any) => {
                    event.preventDefault();
                    this.props.onClick();
                }}
                onKeyDown={(event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault();
                        this.props.onClick();
                    }
                }}
            >
                <figure className="header-profile__avatar" aria-hidden="true">
                    <span className="header-profile__characters"
                        ref={(elem: any) => this.elem = elem}
                        title={`${this.props.user.first_name} ${this.props.user.last_name}`}
                    >{initials}</span>
                </figure>
            </div>
        );
    }

}

ProfileToggle.propTypes = {
    user: PropTypes.shape({
        first_name: PropTypes.string,
        last_name: PropTypes.string,
    }).isRequired,
    onClick: PropTypes.func.isRequired,
    expanded: PropTypes.bool,
};

export default ProfileToggle;
