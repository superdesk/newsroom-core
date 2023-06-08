import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import moment from 'moment';
import {AGENDA_DATE_PICKER_FORMAT_SHORT} from '../utils';

class CalendarButtonWrapper extends React.Component {
    render() {
        return (
            <button className={
                classNames('nh-dropdown-button', {'active': this.props.active})}
            onClick={this.props.onClick}>
                {moment(this.props.value).format(AGENDA_DATE_PICKER_FORMAT_SHORT)}
                <i className={classNames('icon-small--arrow-down')}></i>
            </button>
        );
    }
}

CalendarButtonWrapper.propTypes = {
    onClick: PropTypes.func,
    value: PropTypes.string,
    active: PropTypes.bool,
};

export default CalendarButtonWrapper;
