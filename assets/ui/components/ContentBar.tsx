import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';

export default function ContentBar(props: any) {
    return (
        <div className='content-bar navbar justify-content-between'>
            <button className='content-bar__menu' onClick={props.onClose} aria-label={gettext('Close')} role='button'>
                {props.onClose &&
                    <i className='icon--close-thin'></i>
                }
            </button>
            {props.children}
        </div>
    );
}

ContentBar.propTypes = {
    children: PropTypes.node,
    onClose: PropTypes.func,
};