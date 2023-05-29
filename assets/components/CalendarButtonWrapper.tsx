import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import moment from 'moment';
import {AGENDA_DATE_PICKER_FORMAT_SHORT} from '../utils';

class CalendarButtonWrapper extends React.Component {
    render() {
        return (
            <button className={
                classNames('btn btn-outline-primary btn-sm me-3 align-items-center px-2 btn-with-icon', {'active': this.props.active})}
            onClick={this.props.onClick}>
                {moment(this.props.value).format(AGENDA_DATE_PICKER_FORMAT_SHORT)}
                <i className={classNames('icon-small--arrow-down ms-1', {'icon--white': this.props.active})}></i>
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
