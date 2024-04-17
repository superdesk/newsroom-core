import React from 'react';
import classNames from  'classnames';
import {IAgendaItem, IListConfig, IPreviewConfig} from 'interfaces';
import {isTopStory} from 'agenda/utils';

interface IProps {
    item: IAgendaItem;
    config: IListConfig | IPreviewConfig;
    size?: 'normal' | 'big';
}

export default function TopStoryLabel({item, config, size}: IProps) {
    const classes = classNames('label label--fill label--rounded label--top-story', {
        'label--big': size === 'big',
        'mb-2': size === 'big',
    });
    const subjectList = item.subject || [];
    const topStorySubjects = subjectList.filter(isTopStory);

    return (
        topStorySubjects.length > 0 ? (
            <div>
                {topStorySubjects.map(subject => (
                    <span className={classes} key={subject.name}>{subject.name}</span>
                ))}
            </div>
        ) : null
    );
}
