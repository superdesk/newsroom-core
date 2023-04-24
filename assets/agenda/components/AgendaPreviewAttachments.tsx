import PreviewBox from 'assets/ui/components/PreviewBox';
import {gettext} from 'assets/utils';
import PropTypes from 'prop-types';
import React from 'react';
import {hasAttachments} from '../utils';
import AgendaAttachments from './AgendaAttachments';

export default function AgendaPreviewAttachments({item}: any) {
    if (!hasAttachments(item)) {
        return null;
    }

    return (
        <PreviewBox label={gettext('Attachments')}>
            <AgendaAttachments item={item} />
        </PreviewBox>
    );
}

AgendaPreviewAttachments.propTypes = {
    item: PropTypes.object.isRequired,
};
