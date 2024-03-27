import React from 'react';
import classNames from  'classnames';
import {IAgendaItem, IListConfig, IPreviewConfig} from 'interfaces';

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

    return (
        config.subject?.topStoryScheme
            ? (
                <div>
                    {item.subject?.filter(subject => subject.scheme === config.subject?.topStoryScheme).map(subject => {
                        return <span className={classes} key={subject.name}>{subject.name}</span>;
                    })}
                </div>
            )
            : null
    );
}
