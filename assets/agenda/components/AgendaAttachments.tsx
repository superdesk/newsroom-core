import React from 'react';
import PropTypes from 'prop-types';
import {hasAttachments, getAttachments} from '../utils';

import {gettext} from 'utils';
import {bem} from 'ui/utils';

const kB = 1024;
const MB = kB * kB;

function filesize (size) {
    if (size > MB) {
        return (size / MB).toFixed(1) + ' MB';
    } else if (size > kB) {
        return (size / kB).toFixed(1) + ' kB';
    } else {
        return size + ' B';
    }
}

export default function AgendaAttachments({item}: any) {
    if (!hasAttachments(item)) {
        return null;
    }

    return getAttachments(item).map((attachment: any) => (
        <div key={attachment.media} className="coverage-item flex-row">
            <div className={bem('coverage-item', 'column', 'grow')}>
                <div className="coverage-item__row">
                    <span className="d-flex coverage-item--element-grow text-overflow-ellipsis">
                        <i className="icon-small--attachment icon--green me-2"></i>
                        <span className="text-overflow-ellipsis">{attachment.name}</span>
                    </span>
                </div>
                <div className="coverage-item__row">
                    <span className="coverage-item__text-label me-1">{gettext('Size:')}</span>
                    <span className="me-2">{filesize(attachment.length)}</span>
                    <span className="coverage-item__text-label me-1">{gettext('MIME type:')}</span>
                    <span>{attachment.mimetype}</span>
                </div>
            </div>
            <div className="coverage-item__column">
                <a className="icon-button" href={attachment.href + '?filename=' + attachment.name} aria-label={gettext('Download')}>
                    <i className="icon--download icon--gray-dark"></i>
                </a>
            </div>
        </div>
    ));
}

AgendaAttachments.propTypes = {
    item: PropTypes.object.isRequired,
};
