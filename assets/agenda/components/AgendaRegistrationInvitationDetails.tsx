import * as React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';

import {gettext} from 'utils';
import InfoBox from 'wire/components/InfoBox';
import PreviewTagsBlock from 'wire/components/PreviewTagsBlock';
import {PreviewText} from 'ui/components/PreviewText';


export function AgendaRegistrationInvitationDetails({item}: any) {
    if (!get(item, 'registration_details.length') && !get(item, 'invitation_details.length')) {
        return null;
    }

    return (
        <InfoBox>
            {!get(item, 'registration_details.length') ? null : (
                <PreviewTagsBlock label={gettext('Registration Details')}>
                    <PreviewText text={get(item, 'registration_details')} />
                </PreviewTagsBlock>
            )}
            {!get(item, 'invitation_details.length') ? null : (
                <PreviewTagsBlock label={gettext('Invitation Details')}>
                    <PreviewText text={get(item, 'invitation_details')} />
                </PreviewTagsBlock>
            )}
        </InfoBox>
    );
}

AgendaRegistrationInvitationDetails.propTypes = {
    item: PropTypes.object.isRequired,
};
