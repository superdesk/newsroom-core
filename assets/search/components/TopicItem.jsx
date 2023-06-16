import * as React from 'react';
import PropTypes from 'prop-types';

export function TopicItem({topic, isActive, onClick, newItems}) {
    return (
        <li className="topic-list__item">
            <a className={`topic-list__item-link ${isActive ? 'topic-list__item-link--active' : ''}`}
                aria-selected={isActive} href=""
                onClick={(event) => onClick(event, topic)}
            >
                <span className="topic-list__item-link_label">{topic.label}</span>
                {newItems > 0 && (
                    <span className="badge rounded-pill bg-info">{newItems}</span>
                )}
            </a>
        </li>
    );
}

TopicItem.propTypes = {
    topic: PropTypes.shape({
        label: PropTypes.string,
    }).isRequired,
    onClick: PropTypes.func,
    newItems: PropTypes.number,
    isActive: PropTypes.bool,
};
