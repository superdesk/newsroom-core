import React from 'react';
import PropTypes from 'prop-types';

import {gettext, formatDate, formatTime} from 'utils';
import {IconButton} from 'components/IconButton';

export default function Preview(props: any) {
    return (
        <div className='wire-column__preview__items' role={gettext('dialog')} aria-label={gettext('Article Preview')}>
            <h3 className="a11y-only">{gettext('Article Preview')}</h3>
            <div className="wire-column__preview__top-bar pt-2 pb-0">
                <div className='wire-column__preview__date'>{gettext('Published on {{ date }} at {{ time }}', {
                    date: formatDate(props.published),
                    time: formatTime(props.published),
                })}</div>
                {props.innerElements}
                <IconButton
                    icon='close-thin'
                    aria-label={gettext('Close')}
                    onClick={props.onCloseClick}
                />
            </div>
            {props.children}
        </div>
    );
}

Preview.propTypes = {
    children: PropTypes.node,
    published: PropTypes.string,
    onCloseClick: PropTypes.func.isRequired,
    innerElements: PropTypes.node,
};
