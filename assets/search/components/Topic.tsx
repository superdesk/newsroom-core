import React from 'react';

import classNames from 'classnames';

import {gettext, formatDate, formatTime} from 'utils';
import ActionButton from 'components/ActionButton';
import {ToolTip} from 'ui/components/ToolTip';
import {ITopic, ITopicNotificationScheduleType, IUser} from 'interfaces';

export interface ITopicAction {
    id: string;
    name: string;
    icon: string;
    action: (topic: ITopic) => void;
    if?: (topic: ITopic) => boolean;
}

interface IProps {
    topic: ITopic;
    actions: Array<ITopicAction>;
    users: Array<IUser>;
    selected: boolean;
    subscriptionType?: ITopicNotificationScheduleType;
}

export function Topic({topic, actions, users, selected, subscriptionType}: IProps) {
    const getActionButtons = (topic: ITopic) => actions.filter((action) => action.if == null || action.if(topic)).map(
        (action) => (
            <ActionButton
                key={action.name}
                testId={`topic-action--${action.name}`}
                item={topic}
                className='icon-button icon-button--primary'
                displayName={false}
                action={action}
            />
        )
    );

    const createdBy = users.find((user) => user._id === topic.original_creator);
    const updatedBy = users.find((user) => user._id === topic.version_creator);
    const createdInfo = topic.is_global && createdBy ?
        gettext('Created by {{author}} on {{date}} at {{ time }}', {
            author: createdBy.first_name + ' ' + createdBy.last_name,
            date: formatDate(topic._created),
            time: formatTime(topic._created),
        }) :
        gettext('Created on {{ date }} at {{ time }}', {
            date: formatDate(topic._created),
            time: formatTime(topic._created),
        });
    const updatedInfo = topic.is_global && updatedBy ?
        gettext('Updated by {{author}} on {{date}} at {{time}}', {
            author: updatedBy.first_name + ' ' + updatedBy.last_name,
            date: formatDate(topic._updated),
            time: formatTime(topic._updated),
        }) :
        gettext('Updated on {{ date }} at {{ time }}', {
            date: formatDate(topic._updated),
            time: formatTime(topic._updated),
        });

    return (
        <div
            key={topic._id}
            data-test-id={`topic-card--${topic.label}`}
            className={classNames(
                'simple-card',
                'simple-card--draggable',
                {'simple-card--selected': selected}
            )}
            draggable={true}
            onDragStart={(event) => {
                event.dataTransfer.setData('topic', topic._id);
                event.dataTransfer.dropEffect = 'move';
            }}
        >
            <div className="simple-card__header simple-card__header-with-icons">
                <ToolTip>
                    <h6
                        className="simple-card__headline"
                        title={topic.label}
                    >
                        {topic.label}
                    </h6>
                </ToolTip>
                <div className='simple-card__icons'>
                    {getActionButtons(topic)}
                </div>
            </div>
            <p className='simple-card__description'>{topic.description || ' '}</p>
            <div className="simple-card__row simple-card__row--space-between">
                <div className="simple-card__column simple-card__column--align-start">
                    <span className="simple-card__date">{createdInfo}</span>
                    <span className="simple-card__date">{updatedInfo}</span>
                </div>
                {subscriptionType != null && (
                    <div className="simple-card__column simple-card__column--align-end">
                        <span className="simple-card__notification-info">
                            <i className="icon--alert"></i>
                            <span className="label--rounded label--alert">
                                {subscriptionType === 'real-time' ? gettext('Real-Time') : gettext('Scheduled')}
                            </span>
                        </span>
                    </div>
                )}
            </div>
        </div>
    );
}

