import * as React from 'react';
import PropTypes from 'prop-types';

export function TopicItem({topic, newItemsByTopic, onClick, className}) {
    return (
        <button
            className={className}
            onClick={(e: any) => onClick(e, topic)}
        >
            {topic.label}
            {newItemsByTopic && newItemsByTopic[topic._id] && (
                <span className="wire-button__notif">
                    {newItemsByTopic[topic._id].length}
                </span>
            )}
        </button>
    );
}

TopicItem.propTypes = {
    topic: PropTypes.shape({
        _id: PropTypes.string,
        label: PropTypes.string,
    }).isRequired,
    newItemsByTopic: PropTypes.object,
    onClick: PropTypes.func,
    className: PropTypes.string,
};
