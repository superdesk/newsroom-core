import React from 'react';
import PropTypes from 'prop-types';
import classnames from 'classnames';
import {gettext} from 'utils';
import {formatNavigationDate, getNext, getPrevious} from '../utils';


function AgendaDateButtons({selectDate, activeDate, activeGrouping}: any): any {
    return ([<span className='me-3' key='label'>{formatNavigationDate(activeDate, activeGrouping)}</span>,
        <button
            key='today'
            type='button'
            className='btn btn-outline-primary btn-sm me-3'
            onClick={() => selectDate(Date.now(), 'day')}>
            {gettext('Today')}
        </button>,
        <button
            key='left'
            type='button'
            className='icon-button icon-button--small me-2'
            aria-label={gettext('Left')}
            onClick={() => selectDate(getPrevious(activeDate, activeGrouping), activeGrouping)}>
            <i className='icon--arrow-right icon--rotate-180'></i>
        </button>,
        <button
            key='right'
            type='button'
            className='icon-button icon-button--small me-3'
            aria-label={gettext('Right')}
            onClick={() => selectDate(getNext(activeDate, activeGrouping), activeGrouping)}>
            <i className='icon--arrow-right'></i>
        </button>,
        <button
            key='D'
            type='button'
            className={classnames('btn btn-outline-primary btn-sm me-2', {'active': activeGrouping === 'day'})}
            onClick={() => selectDate(activeDate, 'day')}>
            {gettext('D')}
        </button>,
        <button
            key='W'
            type='button'
            className={classnames('btn btn-outline-primary btn-sm me-2', {'active': activeGrouping === 'week'})}
            onClick={() => selectDate(activeDate, 'week')}>
            {gettext('W')}
        </button>,
        <button
            key='M'
            type='button'
            className={classnames('btn btn-outline-primary btn-sm', {'active': activeGrouping === 'month'})}
            onClick={() => selectDate(activeDate, 'month')}>
            {gettext('M')}
        </button>]);
}

AgendaDateButtons.propTypes = {
    selectDate: PropTypes.func,
    activeDate: PropTypes.number,
    activeGrouping: PropTypes.string,
};

const component: React.ComponentType<any> = AgendaDateButtons;

export default component;
