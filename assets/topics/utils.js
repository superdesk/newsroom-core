import {canUserManageTopics} from 'users/utils';

export function canUserEditTopic(topic, user) {
    return !(
        topic.is_global &&
            !canUserManageTopics(user) &&
            topic.user !== user._id
    );
}
