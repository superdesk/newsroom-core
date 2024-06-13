import React from 'react';
import classNames from  'classnames';
import {IArticle} from 'interfaces';
import {wireLabel} from 'agenda/utils';
import {gettext} from 'utils';

interface IProps {
    item: IArticle;
}

export default function WireLabel({item}: IProps) {
    const subjectList = item.subject || [];
    const wireItemSubjects = subjectList.filter(wireLabel);

    return (
        wireItemSubjects.length > 0 ? (
            <div>
                {wireItemSubjects.map(subject => {
                    const classes = classNames('label label--fill label--rounded', {
                        [`label-wire--${subject.code}`]: subject.code,
                    });

                    return (
                        <span
                            className={classes}
                            key={subject.code}
                        >
                            {gettext(subject.name)}
                        </span>
                    );
                })}
            </div>
        ) : null
    );
}
