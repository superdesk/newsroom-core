import {PreviewText} from 'assets/ui/components/PreviewText';
import {gettext} from 'assets/utils';
import InfoBox from 'assets/wire/components/InfoBox';
import PreviewTagsBlock from 'assets/wire/components/PreviewTagsBlock';
import {get} from 'lodash';
import PropTypes from 'prop-types';
import * as React from 'react';

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
