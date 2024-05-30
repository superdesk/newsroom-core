import React from 'react';
import classNames from  'classnames';
import {IArticle} from 'interfaces';
import {wireLabel} from 'agenda/utils';

interface IProps {
    item: IArticle;
}

export default function WireLabel({item}: IProps) {
    const classes = classNames('label label--fill label--rounded');

    const subjectList = item.subject || [];
    const wireItemSubjects = subjectList.filter(wireLabel);

    return (
        wireItemSubjects.length > 0 ? (
            <div>
                {wireItemSubjects.map(subject => (
                    <span
                        className={classes + ` label-wire--${subject.code}`}
                        key={subject.name}
                    >
                        {subject.name}
                    </span>
                ))}
            </div>
        ) : null
    );
}
