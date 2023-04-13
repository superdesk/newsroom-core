import React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';
import classNames from 'classnames';
import ActionButton from 'assets/components/ActionButton';
import AuditInformation from 'assets/components/AuditInformation';
import {ToolTip} from 'assets/ui/components/ToolTip';
import {gettext, formatDate, formatTime} from 'assets/utils';

const TopicList = ({topics, selectedTopicId, actions, users}: any) => {
    if (get(topics, 'length', 0) < 0) {
        return null;
    }

    const getActionButtons = (topic: any) => actions.map(
        (action: any) => (
            <ActionButton
                key={action.name}
                item={topic}
                className='icon-button'
                displayName={false}
                action={action}
                disabled={action.when != null && !action.when(topic)}
            />
        )
    );

    return topics.map(
        (topic: any) => (
            <div key={topic._id} className='simple-card-wrap col-12 col-lg-6'>
                <div className={classNames(
                    'simple-card',
                    {'simple-card--selected': selectedTopicId === topic._id}
                )}>
                    <div className="simple-card__header simple-card__header-with-icons">
                        <ToolTip>
                            <h6
                                className="simple-card__headline"
                                title={topic.label || topic.name}
                            >
                                {topic.label || topic.name}
                            </h6>
                        </ToolTip>
                        <div className='simple-card__icons'>
                            {getActionButtons(topic)}
                        </div>
                    </div>
                    <p>{topic.description || ' '}</p>
                    {topic.is_global ? (
                        <span className="simple-card__date">
                            <AuditInformation
                                item={topic}
                                users={users}
                                className="p-0"
                                noPadding={true}
                            />
                        </span>
                    ) : (
                        <span className="simple-card__date">
                            {gettext('Created on {{ date }} at {{ time }}', {
                                date: formatDate(topic._created),
                                time: formatTime(topic._created),
                            })}
                        </span>
                    )}
                </div>
            </div>
        )
    );
};

TopicList.propTypes = {
    topics: PropTypes.arrayOf(PropTypes.object),
    selectedTopicId: PropTypes.string,
    actions: PropTypes.arrayOf(PropTypes.shape({
        name: PropTypes.string,
        icon: PropTypes.string,
        action: PropTypes.func,
    })),
    users: PropTypes.array,
};

export default TopicList;
