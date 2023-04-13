import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {formatTime} from 'assets/utils';
import {bem} from '../utils';

export default function MetaTime({date, borderRight, isRecurring, cssClass}: any) {
    const metaTimeClass = classNames('time-label', cssClass);

    return (
        <div className={bem('wire-articles__item', 'meta-time', {'border-right': borderRight})}>
            <span className={metaTimeClass}>{formatTime(date)}</span>
            {isRecurring && <span className='time-icon'><i className="icon-small--repeat"/></span>}
        </div>
    );
}

MetaTime.propTypes = {
    date: PropTypes.string,
    borderRight: PropTypes.bool,
    isRecurring: PropTypes.bool,
    cssClass: PropTypes.string,
};

MetaTime.defaultProps = {
    isRecurring: false,
    hasCoverage: false
};
