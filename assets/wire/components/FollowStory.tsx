import React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';
import {gettext} from 'utils';
import types from 'wire/types';
import {Button} from 'components/Buttons';

const isFollowing = (item: any, topics: any) =>
    item && item.slugline && topics && topics.find(
        (topic: any) => topic.query === `slugline:"${item.slugline}"`
    );

export default function FollowStory({item, user, topics, followStory}: any) {
    const canFollowStory = followStory && user && (get(item, 'slugline') || '').trim();
    const disabled = isFollowing(item, topics);

    if (canFollowStory) {
        return (
            <Button
                value={gettext('Follow story')}
                variant='secondary'
                disabled={disabled}
                onClick={() => followStory(item)}
            />
        );
    }

    return null;
}

FollowStory.propTypes = {
    item: types.item.isRequired,
    user: types.user.isRequired,
    topics: types.topics.isRequired,
    followStory: PropTypes.func.isRequired,
};
