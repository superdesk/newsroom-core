import React from 'react';
import {gettext} from 'utils';

interface IProps {
    title: string;
    photoUrl?: string;
    kind: MoreNewsSearchKind;
    id?: string;
    photoUrlLabel?: string;
    moreNews?: boolean;
}

export enum MoreNewsSearchKind {
    product,
    topic,
}

const MoreNewsInternal = {
    [MoreNewsSearchKind.product]: (props: {id: string}) => (
        <a href={`/wire?product=${props.id}`} role='button' className='nh-button nh-button--tertiary mb-3'>
            {gettext('More news')}
        </a>
    ),
    [MoreNewsSearchKind.topic]:  (props: {id: string}) => (
        <a href={`/wire?topic=${props.id}`} role='button' className='nh-button nh-button--tertiary mb-3'>
            {gettext('More news')}
        </a>
    )
};

function MoreNewsButton(props: IProps): any {
    const {title, photoUrl, photoUrlLabel, moreNews, kind, id} = props;
    const MoreNewsLink = MoreNewsInternal[kind];

    return (
        [
            <div key='heading' className='col-6 col-sm-8'>
                <h3 className='home-section-heading'>{title}</h3>
            </div>,
            <div key='more-news' className='col-6 col-sm-4 d-flex align-items-start justify-content-end'>
                {moreNews && id && <MoreNewsLink id={id} />}
                {photoUrl && (
                    <a href={photoUrl} target='_blank' rel='noopener noreferrer' role='button' className='nh-button nh-button--tertiary mb-3'>
                        {photoUrlLabel}
                    </a>
                )}
            </div>
        ]
    );
}

const component: React.ComponentType<IProps> = MoreNewsButton;

export default component;
