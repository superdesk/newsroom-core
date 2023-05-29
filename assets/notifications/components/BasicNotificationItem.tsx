import * as React from 'react';
import PropTypes from 'prop-types';

export function BasicNotificationItem({header, body, url, footer}) {
    return (
        <React.Fragment>
            {header == null ? null : (
                <div className="notif__list__info">{header}</div>
            )}
            {body == null ? null : (
                <div className="notif__list__headline">
                    {url != null ? (<a href={url}>{body}</a>) : body}
                </div>
            )}
            {footer == null ? null : (
                <div className='wire-articles__item__meta-info'>
                    {footer}
                </div>
            )}
        </React.Fragment>
    );
}

BasicNotificationItem.propTypes = {
    header: PropTypes.string,
    body: PropTypes.string,
    url: PropTypes.string,
    footer: PropTypes.string,
};
