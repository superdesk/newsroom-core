import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

export default class ExpiryButtonWrapper extends React.PureComponent<any, any> {
    static propTypes: any;
    render() {
        return (
            <button
                onClick={this.props.onClick}
                className={classNames(
                    'expiry-date__date-input btn nh-dropdown-button',
                    {'active': this.props.active}
                )}
                disabled={this.props.disabled}
            >
                {this.props.value}
                <i className='icon-small--arrow-down' />
            </button>
        );
    }
}

ExpiryButtonWrapper.propTypes = {
    onClick: PropTypes.func,
    value: PropTypes.string,
    disabled: PropTypes.bool,
    active: PropTypes.bool,
};
