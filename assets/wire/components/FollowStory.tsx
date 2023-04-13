import React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';
import {gettext} from 'assets/utils';
import types from 'assets/wire/types';

const isFollowing = (item: any, topics: any) =>
    item && item.slugline && topics && topics.find(
        (topic: any) => topic.query === `slugline:"${item.slugline}"`
    );

export default function FollowStory({item, user, topics, followStory}: any) {
    const canFollowStory = followStory && user && (get(item, 'slugline') || '').trim();
    const disabled = isFollowing(item, topics);

    if (canFollowStory) {
        return (
            <button type="button"
                disabled={disabled}
                className="btn btn-outline-primary btn-responsive"
                onClick={() => followStory(item)}>
                {gettext('Follow story')}
            </button>
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
