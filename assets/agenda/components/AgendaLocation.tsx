import React, {Fragment} from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import {hasLocation, getLocationString} from '../utils';

export default function AgendaLocation({item, isMobilePhone, border}: any) {
    if  (!hasLocation(item)) {
        return null;
    }

    return (
        <Fragment>
            <span>
                <i className='icon-small--location icon--gray-dark' />
            </span>

            {isMobilePhone ? (
                <span>{getLocationString(item)}</span>
            ) : (
                <span className={classNames('me-2 align-self-stretch',
                    {'wire-articles__item__icons--dashed-border': border})}>
                    {getLocationString(item)}
                </span>
            )}
        </Fragment>
    );
}

AgendaLocation.propTypes = {
    item: PropTypes.object.isRequired,
    isMobilePhone: PropTypes.bool,
    border: PropTypes.string,
};
