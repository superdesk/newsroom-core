import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {Tooltip} from 'bootstrap';
import {isTouchDevice} from 'utils';


class ActionButton extends React.Component {
    constructor(props: any) {
        super(props);

        this.tooltip = null;
    }

    componentDidMount() {
        if (!isTouchDevice() && this.elem) {
            this.tooltip = new Tooltip(this.elem, {trigger: 'hover'});
        }
    }

    componentWillUnmount() {
        if (this.elem && this.tooltip) {
            this.tooltip.dispose();
        }
    }

    render() {
        const classes = classNames(`icon--${this.props.action.icon}`, {
            'icon--gray-dark': this.props.isVisited || this.props.disabled,
        });
        const {item, group, plan, action, disabled} = this.props;

        return (
            <button
                type='button'
                className={this.props.className}
                disabled={disabled}
                onClick={
                    () => {
                        if (action.multi) {
                            return action.action([item._id]);
                        } else {
                            return action.action(item, group, plan);
                        }
                    }
                }
                ref={(elem) => this.elem = elem}
                title={!this.props.displayName ? this.props.action.tooltip || this.props.action.name : ''}
                aria-label={!this.props.displayName ? this.props.action.tooltip || this.props.action.name : this.props.action.name }>
                <i className={classes}></i>
                {this.props.displayName && this.props.action.name}</button>
        );
    }
}

ActionButton.propTypes = {
    item: PropTypes.object,
    group: PropTypes.string,
    plan: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.object
    ]),
    className: PropTypes.string,
    displayName: PropTypes.bool,
    isVisited: PropTypes.bool,
    action: PropTypes.shape({
        name: PropTypes.string.isRequired,
        icon: PropTypes.string.isRequired,
        action: PropTypes.func.isRequired,
        multi: PropTypes.bool,
        tooltip: PropTypes.string,
    }),
    disabled: PropTypes.bool,
};

export default ActionButton;
