import React from 'react';
import PropTypes from 'prop-types';
import {Tooltip} from 'bootstrap';

import {isTouchDevice} from '../../utils';

class ProfileToggle extends React.Component {
    constructor(props: any) {
        super(props);

        this.tooltip = null;
    }

    componentDidMount() {
        if (!isTouchDevice() && this.elem) {
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
            <div className="header-profile" onClick={(event) => {
                event.preventDefault();
                this.props.onClick();
            }}>
                <figure className="header-profile__avatar">
                    <span className="header-profile__characters"
                        ref={(elem) => this.elem = elem}
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
};

export default ProfileToggle;
