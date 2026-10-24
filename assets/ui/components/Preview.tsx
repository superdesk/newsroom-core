import React from 'react';
import PropTypes from 'prop-types';

import {gettext, formatDate, formatTime} from 'utils';
import {IconButton} from 'components/IconButton';

export default function Preview(props: any) {
    // The preview does not take focus when it opens, so focus is returned to whatever had it then (usually the list item).
    const returnFocusTo = React.useRef<Element | null>(null);

    React.useEffect(() => {
        returnFocusTo.current = document.activeElement;
    }, []);

    const close = (event: React.SyntheticEvent) => {
        const target = returnFocusTo.current;

        props.onCloseClick(event);

        if (target instanceof HTMLElement && target.isConnected) {
            target.focus();
        }
    };

    return (
        <div
            className='wire-column__preview__items'
            role="dialog"
            aria-label={gettext('Article Preview')}
            onKeyDown={(event) => {
                if (event.key === 'Escape') {
                    event.stopPropagation();
                    close(event);
                }
            }}
        >
            <h3 className="a11y-only">{gettext('Article Preview')}</h3>
            <div className="wire-column__preview__top-bar pt-2 pb-0">
                <div className='wire-column__preview__date'>{gettext('Published on {{ date }} at {{ time }}', {
                    date: formatDate(props.published),
                    time: formatTime(props.published),
                })}</div>
                {props.innerElements}
                <IconButton
                    icon='close-thin'
                    ariaLabel={gettext('Close')}
                    onClick={close}
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
