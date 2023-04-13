import React from 'react';
import PropTypes from 'prop-types';
import PreviewActionButtons from 'assets/components/PreviewActionButtons';
import {isDisplayed} from 'assets/utils';
import types from 'fetch-mock';
import FollowStory from './FollowStory';

export default function WireActionButtons(props: any) {
    const {previewConfig} = props;
    const displayFollowStory = previewConfig == null || isDisplayed('follow_story', previewConfig);

    return (
        <React.Fragment>
            {previewConfig == null && (
                <div style={{flexGrow: 1}} />
            )}
            <div>
                {displayFollowStory && (
                    <FollowStory
                        user={props.user}
                        item={props.item}
                        topics={props.topics}
                        followStory={props.followStory}
                    />
                )}
            </div>
            <PreviewActionButtons item={props.item} user={props.user} actions={props.actions} />
        </React.Fragment>
    );
}

WireActionButtons.propTypes = {
    item: types.item.isRequired,
    user: types.user.isRequired,
    topics: types.topics.isRequired,
    actions: types.actions.isRequired,
    previewConfig: types.previewConfig,
    followStory: PropTypes.func.isRequired,
};
